# cookbook

the audit produces findings. the cookbook tells you what to do with them.

each pattern starts with a signal you can read directly off `spend_ledger.csv` or `heartbeat_audit.md`. each fix is a concrete action you can take in 30 minutes or less. each pattern has been seen in real engagements.

## pattern 1: heartbeat is your highest job_type

**signal**: in `dashboard.html` under "cost by job type," heartbeat is rank 1.

**most likely cause**: heartbeat is running on a premium or mid-tier model. every 30-minute tick costs 5 to 50 cents and you have 48 ticks per day per agent.

**fix**:
1. open your openclaw config
2. find the routing entry for heartbeat (or set one if it's missing)
3. point it at a budget-tier model (`gpt-4.1-mini`, `claude-haiku-4-5`, or a local model if hybrid)
4. re-run the audit on a fresh window 24 to 48 hours later
5. confirm cost dropped without quality regression

**when not to do this**: if heartbeat is doing genuine reasoning work (rare but possible), downgrading the model breaks the workflow. confirm by reading 5 to 10 actual heartbeat outputs first.

**typical savings**: 30 to 60 percent of total spend in stacks where heartbeat dominated.

## pattern 2: the highest-cost row is a single agent/session pair

**signal**: in the top 10 rows on the dashboard, one (agent, session) pair appears 3+ times.

**most likely cause**: that session is dragging full context into routine work. context bloat compounds because every turn pays to re-explain itself.

**fix**:
1. run `context_weight_scan.py` on the working directory for that agent
2. find any file over 5000 estimated tokens
3. ask: does this file need to be in every prompt, or only in some prompts?
4. for files that don't need to be in every prompt, move them out of the bootstrap path
5. re-run the audit

**when not to do this**: if the file is an active memory file the agent writes to, do not move it. trim it instead.

**typical savings**: 15 to 30 percent for the affected agent.

## pattern 3: cron column is at zero

**signal**: cost by job type shows cron as 0 or near 0, but you have recurring scheduled jobs.

**most likely cause**: scheduled jobs are running on heartbeat or main session instead of cron. they're paying for context they don't need.

**fix**:
1. open `cron_recommendations.csv`
2. find rows where `recommendation` is `move_to_cron`
3. start with the simplest one (a daily report or fixed-time reminder)
4. configure it as a cron job in openclaw
5. confirm it creates a task record (cron does, heartbeat doesn't)
6. re-run the audit

**when not to do this**: don't move multiple jobs at once. one at a time, with a baseline between each.

**typical savings**: 10 to 25 percent depending on how many jobs were misclassified.

## pattern 4: tool_heavy is dominant and the model is premium

**signal**: tool_heavy is rank 1 in cost by job type, and the heaviest rows are on a premium model.

**most likely cause**: browser, pdf, or screenshot loops are running each step on the strong reasoning lane. the loops compound because tool-heavy paths often have 5 to 20 hops per task.

**fix**:
1. identify which workflow is producing the tool-heavy rows (agent + session in the ledger)
2. ask: does this workflow need premium reasoning at every hop, or only at decision points?
3. if only at decision points, route the loop body to a budget model and reserve premium for explicit decision steps
4. re-run the audit

**when not to do this**: workflows where every hop has consequential reasoning (financial decisions, content decisions, customer-facing replies) should keep premium routing.

**typical savings**: 25 to 50 percent of tool-heavy spend.

## pattern 5: a workflow shows up in heartbeat audit and cron migration plan

**signal**: same workflow name appears in both `heartbeat_audit.md` (as a flagged row) and `cron_recommendations.csv` (as `move_to_cron`).

**most likely cause**: the workflow needs exact timing but is running on heartbeat with a premium model. you're paying twice: wrong lane and wrong model.

**fix**:
1. move it to cron first (lane fix)
2. point cron at a budget model (model fix)
3. re-run the audit
4. confirm both flags cleared

this is the highest-value fix in the kit. when you find one of these, prioritize it.

**typical savings**: 40 to 70 percent for the affected workflow.

## pattern 6: total cost dropped but one workflow regressed in quality

**signal**: `verify_before_after.py` reports success, but `quality_regression.py` flags one workflow.

**most likely cause**: the budget-tier model can't handle one specific workflow's reasoning load.

**fix**:
1. roll back routing for that workflow only
2. keep the other changes
3. document the workflow in your config notes as "premium required"
4. re-run both verifications

partial rollback is fine and expected. the kit's job is to find every change that holds. not every change will hold.

## pattern 7: cost climbs again 30 days later

**signal**: 30-day re-baseline shows costs creeping back to pre-audit levels.

**most likely cause**: a new agent or workflow was added without going through the routing decision. drift is the normal state for an unaudited stack.

**fix**:
1. run the kit again on a fresh window
2. compare the new spend ledger to the post-audit baseline
3. identify which (agent, session, model, job_type) combinations are new
4. apply the same routing decisions to the new ones

if this is happening in a client engagement, this is the retainer pitch. ongoing monitoring is genuinely needed and the client now knows it.

## pattern 8: nothing in the audit looks expensive but the bill is high

**signal**: the dashboard top 10 totals don't match the provider invoice.

**most likely cause**: either the price map is wrong, or there are runs your logs don't capture, or the provider is billing for something the kit doesn't see (failed retries, cached prompts, image inputs).

**fix**:
1. confirm `example_prices.csv` matches your provider's actual prices for the audit window
2. check whether failed runs are in your logs (some openclaw setups don't log them by default)
3. check the provider invoice for line items the kit doesn't recognize (vision, audio, fine-tuning, embeddings)
4. if the gap is more than 20 percent, flag it in the report and recommend log-completeness work as a separate engagement
