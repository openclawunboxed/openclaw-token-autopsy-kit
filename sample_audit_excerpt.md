# token autopsy: sample audit excerpt

this is a one-page excerpt from a real audit. client identifiers, agent names, and session names have been redacted. the numbers, structure, and recommendations are unchanged from the original deliverable.

---

## engagement context

**client**: mid-size {industry} operator
**stack**: one openclaw gateway, three agents, mixed cron and heartbeat usage
**audit window**: 14 days of run records
**total records analyzed**: 4,217
**estimated audit-window spend**: `$184.20`

## headline finding

heartbeat is responsible for `$78.40` of the `$184.20` audit-window spend (42.6 percent). of that, `$71.30` is concentrated in a single (agent, session) pair running a mid-tier model on every 30-minute tick.

the workflow is awareness-style (inbox triage and calendar scanning). it does not need a mid-tier model and it does not need full main-session context.

## ranked change list

| rank | change | est. weekly impact | risk |
|---|---|---|---|
| 1 | route heartbeat for `[redacted_agent_a]` to budget tier | `-$26.50/week` | low |
| 2 | move `[redacted_workflow_1]` (daily report) from heartbeat to cron | `-$8.10/week` | low |
| 3 | move `[redacted_workflow_2]` (timed reminder) from heartbeat to cron | `-$3.40/week` | low |
| 4 | trim the `[redacted_agent_a]` working directory (4 files over 5k tokens each) | `-$5.20/week` | low |
| 5 | downgrade tool_heavy lane for `[redacted_agent_b]` from premium to mid-tier | `-$11.30/week` | medium |
| 6 | downgrade tool_heavy lane for `[redacted_agent_b]` further to budget | not recommended without testing | high |

estimated cumulative weekly reduction if changes 1-5 are implemented: `$54.50/week` (about 41 percent of audit-window spend).

## what we recommend leaving alone

- the high_judgment lane for `[redacted_agent_c]`. this lane is doing reasoning work that justifies premium routing. moving it would save `$3-4/week` and likely cause measurable quality drop.
- the cron settings as currently configured. cron concurrency and session retention are appropriate for the workload.
- the bootstrap files for `[redacted_agent_c]`. context weight is high but the files are actively used in every meaningful turn.

## verification plan

1. implement change 1 first. re-baseline 48 hours later. confirm `[redacted_agent_a]` quality has not regressed on inbox triage accuracy.
2. if change 1 holds, implement changes 2 and 3 together. cron migration creates task records, so verification is deterministic.
3. implement change 4 in isolation. context trim is reversible.
4. implement change 5 last and re-baseline 1 week later. tool_heavy changes have the highest regression risk because the work is consequential per hop.

## quality regression note

we recommend running `quality_regression.py` against task outcome logs from the 7 days before and the 7 days after each change. flag for rollback any workflow whose success rate drops more than 5 percentage points.

## operator note

this report is an estimate based on the run records provided over the 14 day window. provider invoices remain the source of truth for billing. estimates assume the price map matched the prices in effect during the audit window.

---

(full report continues for 6 more pages with per-workflow detail, the heartbeat audit output, the cron migration recommendations table, and the context weight scan ranking.)

---

*this excerpt is a sanitized version of an audit deliverable. if you want to see the full format on your own stack, the audit takes one week and the deliverable is yours to keep.*
