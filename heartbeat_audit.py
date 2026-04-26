#!/usr/bin/env python3
"""
heartbeat audit.

reads the openclaw config and the spend ledger. flags ledger rows where
job_type is heartbeat and the model is classified premium or mid by the tier
map. prints a parse error if the config does not load cleanly.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model_tier import classify_model  # noqa: E402


def parse_json5_like(text: str, path: Path) -> Dict:
    cleaned = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"WARNING: could not parse {path}: {e}", file=sys.stderr)
        return {}


def load_config(path: Path) -> Dict:
    return parse_json5_like(path.read_text(encoding="utf-8"), path)


def load_ledger(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def find_heartbeat_interval(config: Dict) -> str:
    heartbeat = config.get("heartbeat") or {}
    every = heartbeat.get("every")
    if every:
        return str(every)
    agents_default = (config.get("agents") or {}).get("defaults") or {}
    every = (agents_default.get("heartbeat") or {}).get("every")
    return str(every) if every else "default_or_unknown"


def flag_expensive_rows(ledger: List[Dict[str, str]]) -> List[Dict[str, str]]:
    flagged = []
    for row in ledger:
        if (row.get("job_type") or "").lower() != "heartbeat":
            continue
        cost = float(row.get("cost_usd") or 0)
        if cost <= 0:
            continue
        tier = classify_model(row.get("model") or "")
        if tier in {"premium", "mid"}:
            row = dict(row)
            row["_tier"] = tier
            flagged.append(row)
    flagged.sort(key=lambda x: float(x.get("cost_usd") or 0), reverse=True)
    return flagged


def write_report(path: Path, interval: str, flagged: List[Dict[str, str]]) -> None:
    lines = [
        "# heartbeat audit",
        "",
        f"- detected heartbeat interval: `{interval}`",
        f"- recurring expensive heartbeat rows found: `{len(flagged)}`",
        "",
    ]
    if flagged:
        lines.append("## highest-cost heartbeat rows")
        lines.append("")
        for row in flagged[:10]:
            lines.append(
                f"- agent `{row.get('agent')}` session `{row.get('session')}` "
                f"model `{row.get('model')}` (tier: `{row.get('_tier')}`) "
                f"cost `${row.get('cost_usd')}` tokens `{row.get('total_tokens')}`"
            )
        lines.append("")
        lines.append("## recommendation")
        lines.append("")
        lines.append(
            "move exact schedule work to cron, pin a budget-tier model on heartbeat, "
            "and trim the main-session context."
        )
    else:
        lines.append("## recommendation")
        lines.append("")
        lines.append(
            "no premium or mid-tier models detected on heartbeat rows in the ledger. "
            "manual review still recommended for context weight and recurring patterns."
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="audit heartbeat settings against a spend ledger")
    parser.add_argument("--config", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--output", default="heartbeat_audit.md")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    ledger = load_ledger(Path(args.ledger))
    interval = find_heartbeat_interval(config)
    flagged = flag_expensive_rows(ledger)
    write_report(Path(args.output), interval, flagged)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
