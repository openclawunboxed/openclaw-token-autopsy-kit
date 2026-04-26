#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def index_rows(rows: List[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    return {row[key]: row for row in rows if key in row}


def main():
    parser = argparse.ArgumentParser(description="compare before and after spend baselines")
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    before = index_rows(load_csv(Path(args.before)), "label")
    after = index_rows(load_csv(Path(args.after)), "label")

    labels = sorted(set(before) | set(after))
    lines = ["# anomaly report", ""]
    for label in labels:
        b = float(before.get(label, {}).get("cost_usd", 0) or 0)
        a = float(after.get(label, {}).get("cost_usd", 0) or 0)
        delta = a - b
        direction = "down" if delta < 0 else "up" if delta > 0 else "flat"
        lines.append(f"- `{label}`: before `${b:.2f}` after `${a:.2f}` delta `${delta:.2f}` direction `{direction}`")
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
