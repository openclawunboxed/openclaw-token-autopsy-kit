#!/usr/bin/env python3
"""
tail mode for the spend ledger.

watches a jsonl log file and appends rows to a running ledger as they arrive.
useful when the audit needs to live alongside the stack instead of running once.

usage:
    python tail_audit.py --input live_logs.jsonl --output running_ledger.csv --price-map example_prices.csv
    python tail_audit.py --input live_logs.jsonl --output running_ledger.csv --window-minutes 60
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sys

# import normalize and price helpers from cost_ledger to stay consistent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cost_ledger import normalize, load_price_map  # noqa: E402


def append_rows(ledger_path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    write_header = not ledger_path.exists() or ledger_path.stat().st_size == 0
    with ledger_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def filter_window(rows: List[Dict[str, Any]], window_minutes: int) -> List[Dict[str, Any]]:
    """if the input has timestamps, only keep rows inside the rolling window."""
    if window_minutes <= 0:
        return rows
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    kept = []
    for row in rows:
        ts = row.get("timestamp") or row.get("ts")
        if not ts:
            kept.append(row)
            continue
        try:
            row_time = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            if row_time.tzinfo is None:
                row_time = row_time.replace(tzinfo=timezone.utc)
            if row_time >= cutoff:
                kept.append(row)
        except (ValueError, TypeError):
            kept.append(row)
    return kept


def tail_file(input_path: Path, ledger_path: Path, price_map: Dict[str, Tuple[float, float]],
              poll_seconds: float, window_minutes: int) -> None:
    print(f"watching {input_path} -> appending normalized rows to {ledger_path}")
    print(f"poll interval: {poll_seconds}s, window: {window_minutes}min (0 means no window)")

    last_size = 0
    if input_path.exists():
        last_size = input_path.stat().st_size

    while True:
        try:
            if not input_path.exists():
                time.sleep(poll_seconds)
                continue

            current_size = input_path.stat().st_size
            if current_size < last_size:
                print(f"file shrank or rotated, resetting cursor")
                last_size = 0

            if current_size > last_size:
                with input_path.open("r", encoding="utf-8") as f:
                    f.seek(last_size)
                    new_text = f.read()
                last_size = current_size

                new_records = []
                for line in new_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        new_records.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"skipping malformed line: {line[:80]}")

                new_records = filter_window(new_records, window_minutes)
                normalized = [normalize(r, price_map) for r in new_records]
                append_rows(ledger_path, normalized)

                if normalized:
                    total_cost = sum(r["cost_usd"] for r in normalized)
                    print(f"appended {len(normalized)} row(s), batch cost ${total_cost:.4f}")

            time.sleep(poll_seconds)
        except KeyboardInterrupt:
            print("\nstopped by user")
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="tail mode for the spend ledger")
    parser.add_argument("--input", required=True, help="jsonl log file to watch")
    parser.add_argument("--output", required=True, help="ledger csv to append to")
    parser.add_argument("--price-map", required=False)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--window-minutes", type=int, default=0,
                        help="if input has timestamps, only count rows inside this rolling window")
    args = parser.parse_args()

    price_map = load_price_map(Path(args.price_map)) if args.price_map else {}
    tail_file(Path(args.input), Path(args.output), price_map, args.poll_seconds, args.window_minutes)


if __name__ == "__main__":
    main()
