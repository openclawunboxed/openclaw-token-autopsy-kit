# troubleshooting

things that go wrong when you run the kit, and what to do about each.

## the audit ran but the dashboard is empty

most likely cause: the input file was loaded but no records had usable token fields.

check:
1. `python -c "import json; [print(json.loads(l)) for l in open('your_logs.jsonl').readlines()[:3]]"` to inspect the first 3 records
2. confirm at least one of these field pairs exists per record: `input_tokens`/`output_tokens`, or `prompt_tokens`/`completion_tokens`, or `cost_usd` directly
3. if your logs use different field names, you'll need to add them to `cost_ledger.py`'s `normalize()` function

## the audit ran but every cost is $0

most likely cause: no price map matched your model names.

check:
1. open `spend_ledger.csv` and look at the model column
2. open `example_prices.csv` and confirm those exact model names are in the price map
3. add your model with current per-1k pricing, save, re-run

if your records have explicit `cost_usd` fields, those should override the price map. if costs are still zero, check for typos in the field name (`cost_usd` vs `cost` vs `usd`).

## heartbeat audit reports zero rows but i know heartbeat is expensive

most likely cause: your records don't have job_type set, and `infer_job_type` didn't pick up the heartbeat signal.

check:
1. open `spend_ledger.csv` and look at the job_type column
2. if heartbeat is showing as "general" or something else, your records don't include the word "heartbeat" anywhere in their fields
3. fix: add a `job_type: "heartbeat"` field to your heartbeat records at the source, or modify `infer_job_type` to match your stack's vocabulary

## cron migration recommends move_to_cron for everything

most likely cause: your task map has `needs_precise_timing: yes` for every row.

check:
1. open `example_task_map.csv` and look at the structure
2. for each task in your map, ask honestly: does this need to fire at a specific clock time, or is approximate timing fine?
3. fix the task map and re-run

## context weight scan flags everything as "general"

expected behavior. the classifier uses filename keywords (memory, agent, soul, user). if your file names don't match, everything falls through to general. this isn't a bug. the risk score (high/medium/low) is the more useful column anyway.

## the run_full_audit script fails on the anomaly step

most likely cause: you didn't pass `--before` and `--after` arguments, or the files don't exist.

check:
1. anomaly and verification are optional. run without them on the first pass.
2. if you want them, you need two ledger summary csvs in the format of `example_spend_baseline.csv`: two columns, label and cost_usd.

## tail mode is using too much cpu

most likely cause: poll interval too aggressive.

fix: pass `--poll-seconds 5` or higher. default is 2 seconds. for production monitoring, 30 to 60 seconds is plenty.

## tail mode misses records

most likely cause: file rotation or truncation.

check:
1. tail_audit.py detects shrink and resets the cursor, but if the file is replaced atomically it might miss the swap
2. if your stack rotates logs hourly, point tail mode at the latest active file or use a wrapper script that re-points after rotation

## redactor is collapsing useful content

most likely cause: a real content field is in `LONG_TEXT_FIELDS` and getting collapsed.

fix: open `redact_logs.py`, edit the `LONG_TEXT_FIELDS` set, remove the field name. or pass a higher `--collapse-text-over` value.

## the dashboard html shows total cost different from the report

most likely cause: you re-ran the ledger after generating the report but before generating the dashboard, or vice versa.

fix: re-run `run_full_audit.py` end to end. all artifacts will be consistent.

## tests fail when i run them

check:
1. `python --version` should be 3.10 or higher (the type hints use modern syntax)
2. you must run from the repo root: `cd /path/to/repo && python -m unittest discover tests -v`
3. if `cost_ledger.py` was edited and the test still references old behavior, the test is stale and needs an update, not the code

## webhook alerts fail silently

most likely cause: the webhook url is wrong or the receiving service has changed its expected payload format.

check:
1. test the webhook with curl: `curl -X POST -H 'Content-Type: application/json' -d '{"text":"test"}' YOUR_URL`
2. if curl works but the script doesn't, check `alert_on_spike.py`'s payload format against the receiving service's docs
3. for slack incoming webhooks, the `{"text": "..."}` shape is correct
