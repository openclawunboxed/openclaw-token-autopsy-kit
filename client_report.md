# token autopsy client report

## summary

- total estimated cost: `$0.63`
- total estimated tokens: `67870`
- rows analyzed: `4`

## highest-cost rows

- agent `sales` session `followup` model `openrouter/opus` job `tool_heavy` cost `$0.55`
- agent `ops` session `main` model `claude-sonnet-4-5` job `heartbeat` cost `$0.08`
- agent `research` session `daily` model `gpt-4.1-mini` job `general` cost `$0.01`
- agent `ops` session `main` model `gpt-4.1-mini` job `cron` cost `$0.00`

## recommended next moves

- move precise recurring work to cron
- pin cheaper models on routine checks
- reduce prompt and file baggage in recurring lanes
- re-run the baseline after every routing change

## operator note

this report is an estimate based on available records. use provider invoices as the final billing source.

## heartbeat audit excerpt

# heartbeat audit

- detected heartbeat interval: `30m`
- recurring expensive heartbeat rows found: `1`

## highest-cost heartbeat rows

- agent `ops` session `main` model `claude-sonnet-4-5` (tier: `mid`) cost `$0.081` tokens `17490`

## recommendation

move exact schedule work to cron, pin a budget-tier model on heartbeat, and trim the main-session context.