#!/usr/bin/env python3
"""
quality regression detector.

cost cuts are only useful if the stack still does the work. this script reads
two task-outcome csvs (before and after a routing change) and reports whether
success rate stayed flat, dropped, or improved per workflow family.

input csv format:
    workflow,task_id,outcome
    daily_report,2026-04-22,success
    daily_report,2026-04-23,failure
    inbox_watch,t-1001,success

outcome values accepted: success, failure, fail, ok, error, partial
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


SUCCESS_VALUES = {"success", "ok", "passed", "pass", "true", "1"}
FAILURE_VALUES = {"failure", "fail", "error", "false", "0"}
PARTIAL_VALUES = {"partial", "degraded", "warning"}


def classify(outcome: str) -> str:
    o = outcome.strip().lower()
    if o in SUCCESS_VALUES:
        return "success"
    if o in FAILURE_VALUES:
        return "failure"
    if o in PARTIAL_VALUES:
        return "partial"
    return "unknown"


def load(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    buckets: Dict[str, Dict[str, int]] = defaultdict(lambda: {"success": 0, "failure": 0, "partial": 0, "unknown": 0})
    for row in rows:
        workflow = (row.get("workflow") or "unknown").strip()
        outcome_class = classify(row.get("outcome") or "")
        buckets[workflow][outcome_class] += 1
    return buckets


def rate(counts: Dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return counts["success"] / total


def main() -> None:
    parser = argparse.ArgumentParser(description="detect quality regression after a routing change")
    parser.add_argument("--before", required=True, help="task outcomes csv from before the change")
    parser.add_argument("--after", required=True, help="task outcomes csv from after the change")
    parser.add_argument("--output", required=True, help="markdown report path")
    parser.add_argument("--regression-threshold", type=float, default=0.05,
                        help="success rate drop that counts as regression (default 0.05 = 5 percent)")
    args = parser.parse_args()

    before = summarize(load(Path(args.before)))
    after = summarize(load(Path(args.after)))

    workflows = sorted(set(before) | set(after))

    lines = ["# quality regression report", ""]
    regressions = []
    improvements = []

    for w in workflows:
        b_counts = before.get(w, {"success": 0, "failure": 0, "partial": 0, "unknown": 0})
        a_counts = after.get(w, {"success": 0, "failure": 0, "partial": 0, "unknown": 0})
        b_rate = rate(b_counts)
        a_rate = rate(a_counts)
        delta = a_rate - b_rate

        if delta <= -args.regression_threshold:
            verdict = "regression"
            regressions.append(w)
        elif delta >= args.regression_threshold:
            verdict = "improvement"
            improvements.append(w)
        else:
            verdict = "stable"

        lines.append(
            f"- `{w}`: before {b_rate:.0%} ({sum(b_counts.values())} runs), "
            f"after {a_rate:.0%} ({sum(a_counts.values())} runs), "
            f"delta `{delta:+.0%}` -> `{verdict}`"
        )

    lines.append("")
    lines.append("## verdict")
    lines.append("")
    if regressions:
        lines.append(f"- **rollback candidates**: {', '.join(f'`{r}`' for r in regressions)}")
    if improvements:
        lines.append(f"- **improvements**: {', '.join(f'`{i}`' for i in improvements)}")
    if not regressions and not improvements:
        lines.append("- no workflow crossed the regression or improvement threshold. routing change appears safe.")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")
    if regressions:
        print(f"WARNING: {len(regressions)} workflow(s) regressed: {regressions}")


if __name__ == "__main__":
    main()
