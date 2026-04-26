# changelog

## v2 (current)

### new scripts

- `tail_audit.py` — continuous mode that watches a log file and updates the ledger live. closes the "one-shot only" gap.
- `quality_regression.py` — detects task success rate drops per workflow after a routing change. flags rollback candidates.
- `redact_logs.py` — strips pii, urls, api keys, bearer tokens, aws keys, and credit card patterns from logs before audit. consultants run this on every client log file.
- `config_diff.py` — diffs two openclaw configs and explains routing, heartbeat, and cron changes in plain language.
- `alert_on_spike.py` — webhook or markdown alert when spend crosses a threshold over a recent window. designed to run from cron alongside tail mode.
- `model_tier.py` — classifies any model as premium, mid, budget, or unknown. replaces the brittle substring matching that used to live inside heartbeat_audit.py.

### new reference data

- `model_tier_map.csv` — 38 model patterns mapped to tiers across anthropic, openai, google, deepseek, qwen, mistral, llama, openrouter, and local hosts.

### new lane templates

- `lane_template_browser_heavy.json` — for stacks dominated by browser, pdf, or scraping work.
- `lane_template_cron_heavy.json` — for stacks dominated by scheduled batch jobs.

### new example data

- `example_quality_before.csv` and `example_quality_after.csv` — sample task outcomes for the quality regression demo. the after file includes one workflow regression so the script has something real to flag.
- `example_openclaw_before.json` and `example_openclaw_after.json` — sample configs for the config diff demo.

### new tests

- `tests/test_cost_ledger.py` — 27 tests covering job type inference, price resolution, normalization, aggregation, and record loading.
- `tests/test_model_tier.py` — 11 tests covering tier classification across providers.
- run with `python -m unittest discover tests -v`.

### new operator guides

- `cookbook/cookbook.md` — 8 patterns: signal, cause, fix, savings range. covers heartbeat domination, agent/session bloat, missing cron usage, premium models on tool-heavy lanes, double misclassification, partial regression, drift over 30 days, and unexplained invoice gaps.
- `cookbook/glossary.md` — every term in the kit defined for an operator who has not read the openclaw docs front to back.
- `cookbook/troubleshooting.md` — common issues running the kit and what to do about each.

### new consultant playbook

- `consultant/discovery_questionnaire.md` — 25 question intake form for prospects.
- `consultant/outreach_scripts.md` — three cold email variants plus two linkedin dm templates.
- `consultant/discovery_call_script.md` — minute-by-minute agenda for the first call.
- `consultant/sow_template.md` — one-page scope of work.
- `consultant/data_handling_note.md` — redaction protocol and retention policy.
- `consultant/email_templates.md` — five lifecycle templates (kickoff, midpoint, handoff, 30-day check-in, retainer pitch).
- `consultant/objection_handling.md` — eight common pushbacks with responses.
- `consultant/red_flags.md` — ten signals that an engagement will go badly.
- `consultant/portfolio_case_study_template.md` — fill-in-the-blank for consultants to build their own anonymized case studies.

### service install templates

- `service_templates/` — systemd, launchd, cron, and docker compose entries for running tail_audit.py and alert_on_spike.py in production.

### updates to existing files

- `heartbeat_audit.py` now uses the model tier classifier and prints a warning when config parse fails.
- `run_full_audit.py` now accepts five new optional flags: `--redact-input`, `--config-before`, `--config-after`, `--quality-before`, `--quality-after`. existing usage is unchanged.
- `README.md` rewritten to list all 70+ files with descriptions and grouped by purpose.
- `QUICKSTART.md` rewritten with all new flags and individual script commands.
- `requirements.txt` notes the python 3.10+ requirement.

### bug fixes

- corrected `$93.80` to `$93.90` in `client_delivery_example.md`. the actual baseline file sums to `$93.90` (42 + 8 + 31.50 + 12.40). verification was already correct at `$41.30 / 44.0%`.
- replaced `claude-sonnet-4-7` with `claude-sonnet-4-5` across all sample data. there is no sonnet 4.7 in the anthropic lineup. all derived sample outputs were regenerated.

## v1 (original release)

initial release. core pipeline (cost_ledger, heartbeat_audit, cron_migration, context_weight_scan, anomaly_report, verify_before_after, generate_client_report, build_dashboard, run_full_audit), three lane templates, environment notes for mac mini, vps, wsl2, and docker, the case study, and the service offer template.
