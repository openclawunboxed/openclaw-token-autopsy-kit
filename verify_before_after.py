#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def total_cost(path: Path) -> float:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return sum(float(row.get("cost_usd") or 0) for row in rows)


def main():
    parser = argparse.ArgumentParser(description="verify whether spend dropped after changes")
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    args = parser.parse_args()

    before = total_cost(Path(args.before))
    after = total_cost(Path(args.after))
    delta = after - before
    pct = (delta / before * 100) if before else 0.0

    if delta < 0:
        print(f"success: spend dropped by ${abs(delta):.2f} ({abs(pct):.1f}%)")
    elif delta > 0:
        print(f"warning: spend increased by ${delta:.2f} ({pct:.1f}%)")
    else:
        print("no change detected")


if __name__ == "__main__":
    main()
