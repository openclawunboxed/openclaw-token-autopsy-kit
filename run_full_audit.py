#!/usr/bin/env python3
"""
run the full token autopsy workflow.

required: --input, --config, --tasks
optional pre-step: --redact-input (runs redact_logs.py before the ledger build)
optional baseline pair: --before, --after (runs anomaly_report and verify_before_after)
optional config diff: --config-before, --config-after (runs config_diff)
optional quality regression: --quality-before, --quality-after (runs quality_regression)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="run the full token autopsy workflow")
    parser.add_argument("--input", required=True, help="raw run records (jsonl, json, or csv)")
    parser.add_argument("--config", required=True, help="active openclaw config")
    parser.add_argument("--tasks", required=True, help="task map csv")
    parser.add_argument("--price-map", required=False)
    parser.add_argument("--redact-input", action="store_true",
                        help="run redact_logs.py on --input first and use the redacted copy for the ledger")
    parser.add_argument("--before", required=False, help="before baseline csv (label, cost_usd)")
    parser.add_argument("--after", required=False, help="after baseline csv (label, cost_usd)")
    parser.add_argument("--config-before", required=False, help="prior openclaw config for config diff")
    parser.add_argument("--config-after", required=False, help="new openclaw config for config diff")
    parser.add_argument("--quality-before", required=False, help="task outcomes csv from before the change")
    parser.add_argument("--quality-after", required=False, help="task outcomes csv from after the change")
    args = parser.parse_args()

    py = sys.executable
    base = Path(__file__).resolve().parent

    # optional pre-step: redact the input before any analysis
    input_for_ledger = args.input
    if args.redact_input:
        redacted_path = str(base / "redacted_input.jsonl")
        run([py, str(base / "redact_logs.py"), "--input", args.input, "--output", redacted_path])
        input_for_ledger = redacted_path

    # core pipeline
    ledger_cmd = [py, str(base / "cost_ledger.py"), "--input", input_for_ledger,
                  "--output", str(base / "spend_ledger.csv")]
    if args.price_map:
        ledger_cmd.extend(["--price-map", args.price_map])
    run(ledger_cmd)

    run([py, str(base / "heartbeat_audit.py"),
         "--config", args.config,
         "--ledger", str(base / "spend_ledger.csv"),
         "--output", str(base / "heartbeat_audit.md")])

    run([py, str(base / "cron_migration.py"),
         "--tasks", args.tasks,
         "--output", str(base / "cron_recommendations.csv")])

    run([py, str(base / "context_weight_scan.py"),
         "--paths", str(base),
         "--output", str(base / "context_scan.csv")])

    run([py, str(base / "generate_client_report.py"),
         "--ledger", str(base / "spend_ledger.csv"),
         "--heartbeat", str(base / "heartbeat_audit.md"),
         "--output", str(base / "client_report.md")])

    # optional baseline comparison
    anomaly_path = None
    if args.before and args.after:
        anomaly_path = str(base / "anomaly_report.md")
        run([py, str(base / "anomaly_report.py"),
             "--before", args.before, "--after", args.after,
             "--output", anomaly_path])
        result = subprocess.run(
            [py, str(base / "verify_before_after.py"), "--before", args.before, "--after", args.after],
            capture_output=True, text=True, check=True,
        )
        (base / "verification_result.txt").write_text(result.stdout.strip() + "\n", encoding="utf-8")
        print(result.stdout.strip())

    # optional config diff
    if args.config_before and args.config_after:
        run([py, str(base / "config_diff.py"),
             "--before", args.config_before, "--after", args.config_after,
             "--output", str(base / "config_diff.md")])

    # optional quality regression
    if args.quality_before and args.quality_after:
        run([py, str(base / "quality_regression.py"),
             "--before", args.quality_before, "--after", args.quality_after,
             "--output", str(base / "quality_regression.md")])

    # final dashboard pulls in whatever optional artifacts exist
    dashboard_cmd = [py, str(base / "build_dashboard.py"),
                     "--ledger", str(base / "spend_ledger.csv"),
                     "--heartbeat", str(base / "heartbeat_audit.md"),
                     "--output", str(base / "dashboard.html")]
    if anomaly_path:
        dashboard_cmd.extend(["--anomaly", anomaly_path])
    run(dashboard_cmd)

    print("\naudit complete. open dashboard.html to view results.")


if __name__ == "__main__":
    main()
