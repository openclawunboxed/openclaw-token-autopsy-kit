# quickstart

requires python 3.10 or newer. no third-party packages.

## minimum run

```bash
python run_full_audit.py \
  --input example_logs.jsonl \
  --config example_openclaw.json \
  --tasks example_task_map.csv
```

produces: `spend_ledger.csv`, `heartbeat_audit.md`, `cron_recommendations.csv`, `context_scan.csv`, `client_report.md`, `dashboard.html`.

## full run with baseline comparison

```bash
python run_full_audit.py \
  --input example_logs.jsonl \
  --config example_openclaw.json \
  --tasks example_task_map.csv \
  --price-map example_prices.csv \
  --before example_spend_baseline.csv \
  --after example_spend_delta.csv
```

adds: `anomaly_report.md`, `verification_result.txt`.

## full run with all optional artifacts

```bash
python run_full_audit.py \
  --input client_logs.jsonl \
  --config example_openclaw.json \
  --tasks example_task_map.csv \
  --price-map example_prices.csv \
  --before example_spend_baseline.csv \
  --after example_spend_delta.csv \
  --redact-input \
  --config-before example_openclaw_before.json \
  --config-after example_openclaw_after.json \
  --quality-before example_quality_before.csv \
  --quality-after example_quality_after.csv
```

adds: `redacted_input.jsonl`, `config_diff.md`, `quality_regression.md`.

## run individual scripts

```bash
# build the ledger only
python cost_ledger.py --input example_logs.jsonl --output spend_ledger.csv --price-map example_prices.csv

# tail mode (continuous monitoring)
python tail_audit.py --input live_logs.jsonl --output running_ledger.csv --price-map example_prices.csv

# spike alerts
python alert_on_spike.py --ledger running_ledger.csv --recent-minutes 60 --baseline-hours 6 --threshold 2.0

# redact a log file before audit
python redact_logs.py --input client_logs.jsonl --output redacted.jsonl

# diff two openclaw configs
python config_diff.py --before old_config.json --after new_config.json --output config_diff.md

# quality regression check
python quality_regression.py --before before_outcomes.csv --after after_outcomes.csv --output quality.md

# classify any model (debug)
python model_tier.py claude-sonnet-4-6 gpt-4.1-mini openrouter/opus
```

## run the tests

```bash
python -m unittest discover tests -v
```
