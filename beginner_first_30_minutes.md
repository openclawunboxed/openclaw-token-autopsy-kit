# first 30 minutes

this is the fastest safe path for a total beginner.

## goal

find out whether your openclaw spend is being driven by:

- heartbeat
- long session baggage
- the wrong model in the wrong lane
- recurring jobs that should move to cron

## step 1

run the full audit on the sample files first.

```bash
python run_full_audit.py --input example_logs.jsonl --config example_openclaw.json --tasks example_task_map.csv --price-map example_prices.csv --before example_spend_baseline.csv --after example_spend_delta.csv
```

if it worked, you should see these files update:

- spend_ledger.csv
- heartbeat_audit.md
- cron_recommendations.csv
- context_scan.csv
- client_report.md
- dashboard.html

## step 2

replace the sample files with your own logs and config.

start with only one agent or one workflow.

you are not trying to audit your whole stack yet.

you are trying to find the first leak.

## step 3

open `heartbeat_audit.md`.

look for:

- premium model on heartbeat
- heartbeat interval that is too frequent
- work marked for cron instead of heartbeat

## step 4

open `spend_ledger.csv`.

sort by `cost_usd` from highest to lowest.

if the top rows are all heartbeat, summary, or routine awareness work, you found the wrong lane.

## step 5

open `cron_recommendations.csv`.

move one exact-time recurring job to cron.

good first candidates:

- daily report
- reminder
- weekly review
- fixed-time follow-up

## step 6

re-run the audit after the change.

compare the before and after files.

if cost dropped and the task became easier to audit, keep the change.
