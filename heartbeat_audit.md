# heartbeat audit

- detected heartbeat interval: `30m`
- recurring expensive heartbeat rows found: `1`

## highest-cost heartbeat rows

- agent `ops` session `main` model `claude-sonnet-4-5` (tier: `mid`) cost `$0.081` tokens `17490`

## recommendation

move exact schedule work to cron, pin a budget-tier model on heartbeat, and trim the main-session context.