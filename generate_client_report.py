#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Dict


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def top_rows(rows: List[Dict[str, str]], n: int = 5) -> List[Dict[str, str]]:
    sorted_rows = sorted(rows, key=lambda x: float(x.get("cost_usd") or 0), reverse=True)
    return sorted_rows[:n]


def main():
    parser = argparse.ArgumentParser(description="generate a client-facing markdown cost audit report")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--heartbeat", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    ledger = load_csv(Path(args.ledger))
    total_cost = sum(float(r.get("cost_usd") or 0) for r in ledger)
    total_tokens = sum(int(float(r.get("total_tokens") or 0)) for r in ledger)
    top = top_rows(ledger)

    lines = [
        "# token autopsy client report",
        "",
        "## summary",
        "",
        f"- total estimated cost: `${total_cost:.2f}`",
        f"- total estimated tokens: `{total_tokens}`",
        f"- rows analyzed: `{len(ledger)}`",
        "",
        "## highest-cost rows",
        "",
    ]
    for row in top:
        lines.append(
            f"- agent `{row.get('agent')}` session `{row.get('session')}` model `{row.get('model')}` "
            f"job `{row.get('job_type')}` cost `${float(row.get('cost_usd') or 0):.2f}`"
        )
    lines.extend([
        "",
        "## recommended next moves",
        "",
        "- move precise recurring work to cron",
        "- pin cheaper models on routine checks",
        "- reduce prompt and file baggage in recurring lanes",
        "- re-run the baseline after every routing change",
        "",
        "## operator note",
        "",
        "this report is an estimate based on available records. use provider invoices as the final billing source.",
    ])

    if args.heartbeat and Path(args.heartbeat).exists():
        lines.extend([
            "",
            "## heartbeat audit excerpt",
            "",
            Path(args.heartbeat).read_text(encoding="utf-8"),
        ])

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
