# anonymized case study

## operator

small ecommerce team.

one openclaw setup handled:

- shared inbox awareness
- spreadsheet export review
- recurring follow-up nudges
- twice-daily status summaries

## what went wrong

the stack felt cheap for the first few days.

then the bill jumped.

the team blamed the model first.

that was only part of it.

the real leak was structural:

- heartbeat was still on a premium lane
- spreadsheet checks were riding the main session
- a summary job that wanted exact timing was still living on heartbeat
- session files kept growing

## what the audit showed

- 44 percent of estimated spend was tied to heartbeat rows
- the highest-cost rows were routine checks, not real reasoning work
- two recurring jobs should have moved to cron on day one
- context files were heavier than expected for awareness-style runs

## what changed

- heartbeat moved to a cheaper lane
- exact-time jobs moved to cron
- the biggest context files were trimmed
- the team re-ran the audit one day later

## outcome

the post-change baseline dropped by 44 percent in the sample pack.

the bigger win was auditability.

the team could finally answer:

what ran, how often, and why it cost what it cost.
