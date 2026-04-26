# token autopsy kit (v2)

a stdlib-only audit pipeline for finding hidden token spend in openclaw stacks. designed for two buyers:

- **operators** running their own stack who want to know which lane to fix first
- **consultants** packaging openclaw cost audits as a paid service

requires python 3.10 or newer. no third-party packages. 79 files. 38 passing tests.

## what this kit answers

1. which agent or workflow is spending the most
2. which jobs are paying for full context when they should not
3. which recurring checks belong on cron instead of heartbeat
4. which model lanes are stronger than the work needs
5. whether the fix worked after you changed the stack

## quickstart

```bash
python run_full_audit.py \
  --input example_logs.jsonl \
  --config example_openclaw.json \
  --tasks example_task_map.csv \
  --price-map example_prices.csv \
  --before example_spend_baseline.csv \
  --after example_spend_delta.csv
```

open `dashboard.html` in any browser.

see `QUICKSTART.md` for the full set of flags and individual script commands.

## the 30 minute path

if this is your first run, follow `beginner_first_30_minutes.md`. it walks through the sample audit step by step and tells you what each output means.

## file map

### core pipeline (run in this order)

| file | purpose |
| --- | --- |
| `cost_ledger.py` | normalize raw logs (jsonl/json/csv) into a spend ledger |
| `heartbeat_audit.py` | flag premium and mid-tier models on heartbeat rows |
| `cron_migration.py` | classify recurring jobs as move_to_cron, keep_on_heartbeat, or manual_review |
| `context_weight_scan.py` | estimate prompt bloat from working directory files |
| `generate_client_report.py` | produce the markdown audit report |
| `anomaly_report.py` | per-label before/after delta report |
| `verify_before_after.py` | one-line success/warning/no change verdict |
| `build_dashboard.py` | self-contained html dashboard |
| `run_full_audit.py` | orchestrator that runs the full pipeline |

### scripts added in v2

| file | purpose |
| --- | --- |
| `tail_audit.py` | continuous mode that watches a log file and updates the ledger live |
| `quality_regression.py` | detect quality drops in workflows after a routing change |
| `redact_logs.py` | strip pii and secrets from logs before audit |
| `config_diff.py` | plain-language diff of two openclaw configs |
| `alert_on_spike.py` | webhook or markdown alert when spend crosses a threshold |
| `model_tier.py` | classify models as premium, mid, or budget |

### reference data

| file | purpose |
| --- | --- |
| `model_tier_map.csv` | canonical model name to tier mapping (38 entries) |
| `example_prices.csv` | starter price map for the kit's example data |
| `example_logs.jsonl` | sample run records for testing the pipeline |
| `example_openclaw.json` | sample openclaw config |
| `example_task_map.csv` | sample task map for the cron migration planner |
| `example_spend_baseline.csv` | sample before-baseline for anomaly comparison |
| `example_spend_delta.csv` | sample after-baseline for anomaly comparison |
| `example_quality_before.csv` | sample task outcomes (before) for quality regression demo |
| `example_quality_after.csv` | sample task outcomes (after) with one regression to find |
| `example_openclaw_before.json` | sample prior config for config_diff demo |
| `example_openclaw_after.json` | sample new config for config_diff demo |

### lane templates

| file | use when |
| --- | --- |
| `lane_template_budget.json` | low-cost stacks where most work fits a budget model |
| `lane_template_hybrid.json` | stacks running a local model alongside cloud providers |
| `lane_template_multiagent.json` | stacks with multiple distinct agents |
| `lane_template_browser_heavy.json` | stacks dominated by browser, pdf, or scraping work |
| `lane_template_cron_heavy.json` | stacks dominated by scheduled batch jobs |

### environment notes

| file | covers |
| --- | --- |
| `env_mac_mini.md` | always-on local operator box |
| `env_vps.md` | remote gateway, client-facing deployments |
| `env_wsl2.md` | windows users running the linux path |
| `env_docker.md` | reproducible isolated deployments |

### operator guides

| file | purpose |
| --- | --- |
| `beginner_first_30_minutes.md` | the on-ramp for a first-time user |
| `pre_change_checklist.md` | hygiene before changing any routing |
| `post_change_checklist.md` | what to verify after the change |
| `case_study_anonymized.md` | the anchor narrative behind the kit |
| `client_delivery_example.md` | what a client-facing audit looks like |
| `sample_report.md` | one-paragraph result summary template |

### cookbook

| file | purpose |
| --- | --- |
| `cookbook/cookbook.md` | 8 patterns: signal, cause, fix, savings range |
| `cookbook/glossary.md` | every term in the kit defined |
| `cookbook/troubleshooting.md` | common issues and what to do about each |

### consultant playbook

| file | purpose |
| --- | --- |
| `consultant/discovery_questionnaire.md` | intake form for prospects |
| `consultant/outreach_scripts.md` | cold email and linkedin templates |
| `consultant/discovery_call_script.md` | first-call agenda and questions |
| `consultant/sow_template.md` | one-page scope of work |
| `consultant/data_handling_note.md` | redaction protocol and retention policy |
| `consultant/email_templates.md` | five lifecycle email templates |
| `consultant/objection_handling.md` | eight common pushbacks with responses |
| `consultant/red_flags.md` | when to walk away from a prospect |
| `consultant/portfolio_case_study_template.md` | build your own anonymized case studies |
| `service_offer_template.md` | the offer description |
| `pricing_and_scope_examples.md` | three pricing tiers with fit notes |

### service install templates

| file | platform |
| --- | --- |
| `service_templates/README.md` | install steps for each platform |
| `service_templates/tail_audit.systemd.service` | linux (vps, docker host, wsl2) |
| `service_templates/tail_audit.launchd.plist` | macos (mac mini) |
| `service_templates/alert_on_spike.crontab` | any unix |
| `service_templates/docker-compose.yml` | docker |

### tests

| file | covers |
| --- | --- |
| `tests/test_cost_ledger.py` | 27 tests for the ledger normalization and aggregation |
| `tests/test_model_tier.py` | 11 tests for the model tier classifier |

### project files

| file | purpose |
| --- | --- |
| `README.md` | this file |
| `QUICKSTART.md` | minimum-effort run instructions |
| `CHANGELOG.md` | v1 to v2 changes |
| `LICENSE` | usage terms |
| `SECURITY.md` | hardening checklist for openclaw deployments |
| `.gitignore` | for subscribers who put the kit in their own git repo |
| `requirements.txt` | python version requirement (stdlib only) |
| `sample_audit_excerpt.md` | one-page redacted sample for outreach |

### sample outputs

generated by running the pipeline once on the example inputs. delete and regenerate any time.

| file | source |
| --- | --- |
| `spend_ledger.csv` | from cost_ledger.py |
| `heartbeat_audit.md` | from heartbeat_audit.py |
| `cron_recommendations.csv` | from cron_migration.py |
| `context_scan.csv` | from context_weight_scan.py |
| `client_report.md` | from generate_client_report.py |
| `anomaly_report.md` | from anomaly_report.py |
| `verification_result.txt` | from verify_before_after.py |
| `dashboard.html` | from build_dashboard.py |

## installation

```bash
# clone or unzip the kit, then
cd token-autopsy-kit
python --version  # confirm 3.10 or newer
python -m unittest discover tests -v  # confirm tests pass
python run_full_audit.py --input example_logs.jsonl --config example_openclaw.json --tasks example_task_map.csv
```

## who this is for

**a stack operator** uses the core pipeline plus the cookbook and glossary. start with `beginner_first_30_minutes.md`.

**a consultant** uses the core pipeline plus everything under `consultant/`. start with `service_offer_template.md`, then `pricing_and_scope_examples.md`, then run the kit on the sample data so you know what the deliverable looks like before quoting.

## what this is not

this is not a replacement for provider invoices. all costs reported by the kit are estimates derived from your run records and your price map. use provider invoices as the source of truth for billing, and use the kit for diagnosing where the spend is going inside the stack.

## license

free to use and modify for your own audits and client engagements. do not redistribute the paid version of the kit publicly.
