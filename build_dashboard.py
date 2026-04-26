#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def top_rows(rows: List[Dict[str, str]], n: int = 10) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda x: float(x.get("cost_usd") or 0), reverse=True)[:n]


def main() -> None:
    parser = argparse.ArgumentParser(description="build a tiny local html dashboard from the spend ledger")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--heartbeat", required=False)
    parser.add_argument("--anomaly", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    ledger = load_csv(Path(args.ledger))
    total_cost = sum(float(r.get("cost_usd") or 0) for r in ledger)
    total_tokens = sum(int(float(r.get("total_tokens") or 0)) for r in ledger)
    by_job: Dict[str, float] = {}
    for row in ledger:
        job = row.get("job_type") or "unknown"
        by_job[job] = by_job.get(job, 0.0) + float(row.get("cost_usd") or 0)

    job_rows = []
    for job, cost in sorted(by_job.items(), key=lambda kv: kv[1], reverse=True):
        job_rows.append(f"<tr><td>{job}</td><td>${cost:.2f}</td></tr>")

    spend_rows = []
    for row in top_rows(ledger):
        spend_rows.append(
            f"<tr><td>{row.get('agent')}</td><td>{row.get('session')}</td><td>{row.get('model')}</td><td>{row.get('job_type')}</td><td>${float(row.get('cost_usd') or 0):.2f}</td></tr>"
        )

    extra = []
    for label, path in [("heartbeat audit", args.heartbeat), ("anomaly report", args.anomaly)]:
        if path and Path(path).exists():
            text = Path(path).read_text(encoding="utf-8")
            extra.append(f"<h2>{label}</h2><pre>{text}</pre>")

    page = f"""<!doctype html>
<html><head><meta charset=\"utf-8\"><title>token autopsy dashboard</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1100px;margin:40px auto;padding:0 16px;line-height:1.45}}
table{{border-collapse:collapse;width:100%;margin:12px 0 24px}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f5f5f5}}
.cards{{display:flex;gap:16px;flex-wrap:wrap}}
.card{{border:1px solid #ddd;padding:12px 16px;border-radius:10px;min-width:220px}}
pre{{white-space:pre-wrap;background:#fafafa;padding:12px;border:1px solid #eee}}
</style></head>
<body>
<h1>token autopsy dashboard</h1>
<div class=\"cards\">
<div class=\"card\"><strong>total cost</strong><div>${total_cost:.2f}</div></div>
<div class=\"card\"><strong>total tokens</strong><div>{total_tokens}</div></div>
<div class=\"card\"><strong>rows analyzed</strong><div>{len(ledger)}</div></div>
</div>
<h2>cost by job type</h2><table><tr><th>job type</th><th>cost</th></tr>{''.join(job_rows)}</table>
<h2>highest-cost rows</h2><table><tr><th>agent</th><th>session</th><th>model</th><th>job type</th><th>cost</th></tr>{''.join(spend_rows)}</table>
{''.join(extra)}
</body></html>"""
    Path(args.output).write_text(page, encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
