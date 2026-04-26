#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_INPUT_PRICE = 0.0
DEFAULT_OUTPUT_PRICE = 0.0


def load_records(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        records = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("runs", "records", "events", "items"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    raise ValueError(f"unsupported file type: {path.suffix}")


def load_price_map(path: Path | None) -> Dict[str, Tuple[float, float]]:
    if path is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    price_map: Dict[str, Tuple[float, float]] = {}
    for row in rows:
        model = (row.get("model") or "").strip().lower()
        if not model:
            continue
        in_price = float(row.get("input_price_per_1k") or 0)
        out_price = float(row.get("output_price_per_1k") or 0)
        price_map[model] = (in_price, out_price)
    return price_map


def infer_job_type(record: Dict[str, Any]) -> str:
    text = " ".join(str(v).lower() for v in record.values())
    if "heartbeat" in text:
        return "heartbeat"
    if "cron" in text or "scheduled" in text:
        return "cron"
    if any(word in text for word in ["browser", "screenshot", "pdf", "web"]):
        return "tool_heavy"
    return "general"


def resolve_prices(record: Dict[str, Any], price_map: Dict[str, Tuple[float, float]], model: str) -> Tuple[float, float]:
    explicit_in = record.get("input_price_per_1k")
    explicit_out = record.get("output_price_per_1k")
    if explicit_in not in (None, "") or explicit_out not in (None, ""):
        return float(explicit_in or 0), float(explicit_out or 0)

    model_key = model.strip().lower()
    if model_key in price_map:
        return price_map[model_key]

    for key, prices in price_map.items():
        if key.endswith("*") and model_key.startswith(key[:-1]):
            return prices

    if "default" in price_map:
        return price_map["default"]

    return DEFAULT_INPUT_PRICE, DEFAULT_OUTPUT_PRICE


def normalize(record: Dict[str, Any], price_map: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
    model = record.get("model") or record.get("provider_model") or "unknown"
    agent = record.get("agent") or record.get("agent_id") or "default"
    session = record.get("session") or record.get("session_id") or "unknown"
    job_type = record.get("job_type") or record.get("type") or infer_job_type(record)
    input_tokens = int(float(record.get("input_tokens") or record.get("prompt_tokens") or 0))
    output_tokens = int(float(record.get("output_tokens") or record.get("completion_tokens") or 0))
    input_price, output_price = resolve_prices(record, price_map, model)
    explicit_cost = record.get("cost_usd")
    if explicit_cost is None or explicit_cost == "":
        cost_usd = ((input_tokens / 1000.0) * input_price) + ((output_tokens / 1000.0) * output_price)
    else:
        cost_usd = float(explicit_cost)
    recurring = bool(record.get("recurring") or job_type in {"heartbeat", "cron"})
    return {
        "agent": agent,
        "session": session,
        "model": model,
        "job_type": job_type,
        "runs": 1,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost_usd, 6),
        "recurring": recurring,
        "source": record.get("source") or "",
    }


def aggregate(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[tuple, Dict[str, Any]] = {}
    for row in rows:
        key = (row["agent"], row["session"], row["model"], row["job_type"])
        if key not in buckets:
            buckets[key] = dict(row)
        else:
            bucket = buckets[key]
            bucket["runs"] += 1
            bucket["input_tokens"] += row["input_tokens"]
            bucket["output_tokens"] += row["output_tokens"]
            bucket["total_tokens"] += row["total_tokens"]
            bucket["cost_usd"] += row["cost_usd"]
    results = list(buckets.values())
    for r in results:
        r["cost_usd"] = round(r["cost_usd"], 6)
    results.sort(key=lambda x: x["cost_usd"], reverse=True)
    return results


def write_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="build a spend ledger from json, jsonl, or csv records")
    parser.add_argument("--input", required=True, help="path to input file")
    parser.add_argument("--output", required=True, help="path to output csv")
    parser.add_argument("--price-map", required=False, help="optional csv with model,input_price_per_1k,output_price_per_1k")
    args = parser.parse_args()

    records = load_records(Path(args.input))
    price_map = load_price_map(Path(args.price_map)) if args.price_map else {}
    normalized = [normalize(r, price_map) for r in records]
    ledger = aggregate(normalized)
    write_csv(ledger, Path(args.output))

    total_cost = round(sum(r["cost_usd"] for r in ledger), 4)
    total_tokens = sum(r["total_tokens"] for r in ledger)
    print(json.dumps({"rows": len(ledger), "total_cost_usd": total_cost, "total_tokens": total_tokens}, indent=2))


if __name__ == "__main__":
    main()
