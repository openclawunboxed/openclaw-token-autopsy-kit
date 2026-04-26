# openclaw config diff

## routing changes

- routing for `heartbeat`: `claude-sonnet-4-5` -> `gpt-4.1-mini`
  - this is the lane that runs every interval. moving from premium to budget here is the single biggest cost lever in most stacks.
- routing for `tool_heavy`: `claude-sonnet-4-5` -> `gpt-4.1-mini`
  - browser, screenshot, and pdf paths run here. premium models on this lane multiply fast.

## heartbeat changes

- top-level heartbeat interval: `30m` -> `60m`
  - longer interval reduces heartbeat row count linearly. shorter interval will increase spend.

## cron changes

- cron enabled: `False` -> `True`
  - cron lets exact-time work create task records and skip main-session context.
- cron max concurrent runs: `1` -> `2`
  - too high can spike spend during overlaps. too low can starve scheduled work.
- cron session retention: `(unset)` -> `24h`
