# client delivery example

## audit summary

we analyzed one gateway and one primary workflow class.

the largest spend driver was routine awareness work running on a premium lane with full main-session context.

two exact-time jobs also belonged on cron, not heartbeat.

## what we changed

- pinned a cheaper model to recurring checks
- moved daily report and timed reminder jobs to cron
- trimmed oversized context files used in routine runs
- kept the higher-cost lane only for judgment-heavy work

## before and after

- before estimated weekly spend: `$93.90`
- after estimated weekly spend: `$52.60`
- estimated reduction: `44.0%`
