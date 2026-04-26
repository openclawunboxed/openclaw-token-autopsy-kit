#!/usr/bin/env python3
"""
spend spike alerter.

reads the running ledger, compares the most recent window of cost against a
baseline window, and emits an alert if the spike crosses a threshold. designed
to run from cron alongside tail_audit.py.

usage:
    # alert if the last 60 minutes spent more than 2x the prior 6 hours of average
    python alert_on_spike.py --ledger running_ledger.csv --recent-minutes 60 --baseline-hours 6 --threshold 2.0 --output alert.md

    # post to a webhook (slack-compatible payload format)
    python alert_on_spike.py --ledger running_ledger.csv --recent-minutes 60 --baseline-hours 6 --threshold 2.0 --webhook https://hooks.example.com/...
"""
from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List


def load_ledger(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except (ValueError, TypeError):
        return None


def window_cost(rows: List[Dict[str, str]], start: datetime, end: datetime, ts_field: str = "timestamp") -> float:
    total = 0.0
    untimestamped_total = 0.0
    has_any_timestamp = False
    for row in rows:
        ts = parse_ts(row.get(ts_field) or row.get("ts") or "")
        if ts is None:
            untimestamped_total += float(row.get("cost_usd") or 0)
            continue
        has_any_timestamp = True
        if start <= ts <= end:
            total += float(row.get("cost_usd") or 0)
    # if there are no timestamps at all, fall back to the full ledger total
    if not has_any_timestamp:
        return untimestamped_total
    return total


def post_webhook(url: str, message: str) -> None:
    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="alert when openclaw spend spikes")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--recent-minutes", type=int, default=60)
    parser.add_argument("--baseline-hours", type=int, default=6)
    parser.add_argument("--threshold", type=float, default=2.0,
                        help="multiplier of recent rate over baseline rate that triggers alert (default 2.0)")
    parser.add_argument("--output", required=False, help="markdown alert path (always written if alert fires)")
    parser.add_argument("--webhook", required=False, help="optional webhook url to post alert text")
    parser.add_argument("--quiet", action="store_true", help="exit silently when no alert fires")
    args = parser.parse_args()

    rows = load_ledger(Path(args.ledger))
    now = datetime.now(timezone.utc)
    recent_start = now - timedelta(minutes=args.recent_minutes)
    baseline_end = recent_start
    baseline_start = baseline_end - timedelta(hours=args.baseline_hours)

    recent_total = window_cost(rows, recent_start, now)
    baseline_total = window_cost(rows, baseline_start, baseline_end)

    recent_rate = recent_total / max(args.recent_minutes / 60.0, 0.0001)
    baseline_rate = baseline_total / max(args.baseline_hours, 0.0001)

    multiplier = (recent_rate / baseline_rate) if baseline_rate > 0 else 0.0

    spike = multiplier >= args.threshold and recent_total > 0

    if not spike:
        if not args.quiet:
            print(
                f"no spike: recent ${recent_total:.4f} ({recent_rate:.4f}/h), "
                f"baseline ${baseline_total:.4f} ({baseline_rate:.4f}/h), x{multiplier:.2f}"
            )
        return

    message = (
        f"openclaw spend spike\n"
        f"recent {args.recent_minutes}m: ${recent_total:.4f} (${recent_rate:.2f}/h)\n"
        f"baseline {args.baseline_hours}h: ${baseline_total:.4f} (${baseline_rate:.2f}/h)\n"
        f"multiplier: x{multiplier:.2f} (threshold x{args.threshold})"
    )
    print(message)

    if args.output:
        Path(args.output).write_text("# spend spike alert\n\n" + message + "\n", encoding="utf-8")
        print(f"wrote {args.output}")

    if args.webhook:
        try:
            post_webhook(args.webhook, message)
            print(f"posted to webhook")
        except Exception as e:
            print(f"webhook post failed: {e}")


if __name__ == "__main__":
    main()
