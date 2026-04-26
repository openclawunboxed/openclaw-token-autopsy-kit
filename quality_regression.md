# quality regression report

- `calendar_check`: before 100% (4 runs), after 100% (4 runs), delta `+0%` -> `stable`
- `daily_report`: before 80% (5 runs), after 100% (5 runs), delta `+20%` -> `improvement`
- `followup_reminder`: before 100% (3 runs), after 100% (3 runs), delta `+0%` -> `stable`
- `inbox_watch`: before 100% (5 runs), after 100% (5 runs), delta `+0%` -> `stable`
- `vendor_price_scrape`: before 67% (3 runs), after 0% (4 runs), delta `-67%` -> `regression`

## verdict

- **rollback candidates**: `vendor_price_scrape`
- **improvements**: `daily_report`