# glossary

every term used in the kit, defined for an operator who has not read the openclaw docs front to back.

## agent

a configured persona inside openclaw with its own prompt, tools, and working directory. a stack can have one agent or many. cost shows up in the ledger keyed by agent.

## bootstrap files

files that get loaded into the agent's context every turn (system prompt, identity files, memory files, instruction files). these compound prompt costs because every turn pays for them again. the context weight scanner classifies likely bootstrap files by filename keyword.

## context bloat

when bootstrap files or session history grow large enough that routine turns are paying significant token costs just to re-explain the agent to itself. the cure is trimming, not a cheaper model.

## context weight

the estimated token cost of a file or directory if it were loaded into a prompt. the kit estimates at 4 characters per token, which is a usable rough cut.

## cron

an openclaw execution mode for exact-timed, isolated runs. cron executions create task records. they do not inherit the main session context. good fit for daily reports, fixed-time reminders, scheduled scrapes.

## gateway

a single openclaw deployment. you can run one gateway with multiple agents, or multiple gateways for isolation. cost analysis is usually scoped to one gateway at a time.

## heartbeat

an openclaw execution mode for periodic, approximate-timed turns that run inside the agent's main session with full context. good fit for inbox awareness, calendar awareness, notification awareness. bad fit for jobs that need exact timing or that don't benefit from the session context.

## heartbeat interval

how often heartbeat fires. typical values: 15m, 30m, 45m, 60m. shorter intervals multiply cost linearly.

## job_type

the kit's classification of what kind of work each ledger row represents. four values:

- **heartbeat** — periodic awareness work
- **cron** — exact-timed scheduled work
- **tool_heavy** — runs that hit browsers, pdfs, screenshots, or external tools
- **general** — anything else

## lane

a routing slot in the openclaw config that maps a job type to a model. typical lanes: default, heartbeat, tool_heavy, high_judgment. moving work between lanes is the single most leveraged change in most audits.

## ledger

the canonical output of `cost_ledger.py`. one csv row per (agent, session, model, job_type) tuple, summed across the audit window. the ledger is the source of truth for everything else in the kit.

## main session

the persistent conversation an agent runs in. heartbeat turns and most user-facing turns happen here. cron turns do not.

## model tier

the kit's classification of model strength. three values:

- **premium** — strongest reasoning lanes (opus, gpt-5, gemini 2.5 pro, mistral large, etc.)
- **mid** — balanced lanes (sonnet, gpt-4.1, gemini flash, deepseek)
- **budget** — fast cheap lanes (haiku, gpt-4.1-mini, gemini flash lite, qwen 8b, local models)

defined in `model_tier_map.csv`. the heartbeat audit uses tiers to decide what to flag.

## price map

a csv mapping model name to per-1k-token input and output prices. `example_prices.csv` is the kit's starter map. update it for your provider's current pricing before each audit.

## recurring

a flag on ledger rows indicating the run is part of a recurring pattern (cron or heartbeat). recurring rows compound, so a small per-run cost can become a large monthly cost.

## redaction

stripping pii, secrets, and long content from logs before audit. `redact_logs.py` handles email, phone, url, api key, aws key, bearer token, and credit card patterns. consultants run this on every client log file before analysis.

## regression

a quality drop in a workflow after a routing change. `quality_regression.py` detects this by comparing success rate per workflow before and after. a regression that crosses the threshold is a rollback signal.

## rollback

reverting a routing change for one specific workflow because quality dropped. partial rollback is normal and expected. the kit assumes some changes will hold and some won't.

## session

a single conversation thread. one agent can have many sessions running in parallel. cost in the ledger is keyed at session level so you can find the specific session draining budget.

## spike

a sudden, abnormal increase in spend over a short window. `alert_on_spike.py` watches for this by comparing recent rate to a baseline rate.

## tool_heavy

job_type for runs that include browser, pdf, screenshot, or external tool steps. tool-heavy paths often have 5 to 20 hops per task, so cost compounds even when each hop looks small.

## working directory

the file system location an agent reads from for bootstrap files, memory, and reference material. `context_weight_scan.py` walks this directory to estimate prompt bloat.
