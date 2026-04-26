#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

RULES = {
    "exact_time": "move_to_cron",
    "background_report": "move_to_cron",
    "reminder": "move_to_cron",
    "calendar_awareness": "keep_on_heartbeat",
    "inbox_awareness": "keep_on_heartbeat",
    "destructive_action": "manual_review",
}


def classify(row):
    job_family = (row.get("job_family") or "").strip()
    needs_precise_timing = (row.get("needs_precise_timing") or "").lower() in {"yes", "true", "1"}
    uses_full_context = (row.get("uses_full_context") or "").lower() in {"yes", "true", "1"}

    if job_family in RULES:
        return RULES[job_family]
    if needs_precise_timing:
        return "move_to_cron"
    if uses_full_context:
        return "keep_on_heartbeat"
    return "manual_review"


def main():
    parser = argparse.ArgumentParser(description="suggest which recurring jobs should move to cron")
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with Path(args.tasks).open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    out_rows = []
    for row in rows:
        recommendation = classify(row)
        reason = {
            "move_to_cron": "precise or isolated work should not ride on full main-session context",
            "keep_on_heartbeat": "awareness-style work benefits from approximate checks with context",
            "manual_review": "the job shape is mixed or high-stakes",
        }[recommendation]
        row["recommendation"] = recommendation
        row["reason"] = reason
        out_rows.append(row)

    with Path(args.output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
