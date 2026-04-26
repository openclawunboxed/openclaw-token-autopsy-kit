# email templates

four templates for the engagement lifecycle. fill in the bracketed fields. all of these are short on purpose. clients open and read short emails.

## template 1: kickoff confirmation

send within 24 hours of sow signature.

subject: kickoff: openclaw token autopsy for {client_name}

hi {first_name},

confirming kickoff for the audit. here's where we are.

what i need from you this week:

1. {file_or_access_item_1}
2. {file_or_access_item_2}
3. {file_or_access_item_3}

what to expect:

- monday and tuesday i build the spend ledger and run the heartbeat audit
- wednesday i run the cron migration plan and the context weight scan
- thursday i write the report
- friday i send the deliverables and we schedule the handoff call

i'll send a short status note on wednesday. if anything comes up before then, just reply to this thread.

{your_name}

## template 2: mid-engagement status

send wednesday of the engagement week.

subject: token autopsy for {client_name}: midpoint update

hi {first_name},

quick update.

what i've found so far:

- {finding_1_one_line}
- {finding_2_one_line}
- {finding_3_one_line}

still pending:

- {pending_item_1}
- {pending_item_2}

i'll have the full report friday. one heads up: {anything_that_might_change_scope_or_timing}.

{your_name}

## template 3: deliverable handoff

send when the report is ready.

subject: token autopsy for {client_name}: report ready

hi {first_name},

deliverables are attached.

- `client_report.md` — the written audit
- `dashboard.html` — open in any browser, no install
- `spend_ledger.csv` — the underlying data
- `cron_recommendations.csv` — the migration plan
- `heartbeat_audit.md` — the heartbeat-specific findings
- `anomaly_report.md` — before/after if applicable

headline: {one_sentence_outcome}

ranked change list:

1. {change_1}
2. {change_2}
3. {change_3}

implementation handoff call is scheduled for {date} at {time}. on the call we'll walk through the changes, talk about which ones to implement first, and i'll answer anything that comes up.

second installment of {amount} is due on report delivery. invoice attached.

{your_name}

## template 4: 30-day check-in

send 30 days after engagement close.

subject: 30 day check-in on the openclaw audit

hi {first_name},

month one. quick check.

three questions:

1. did you implement the changes in the report? if some, which ones?
2. is the bill behaving the way we expected?
3. did anything regress in quality?

if you want a re-baseline run (rerun the audit on a fresh window), i can do that as a flat {retainer_price}. it's optional. either way i'd love to hear how it's going.

{your_name}

## template 5: 90-day retainer pitch

send to clients who implemented the changes and saw real savings.

subject: ongoing monitoring for {client_name}

hi {first_name},

90 days in. you cut {dollar_amount_or_percent} from the bill in the first month and the system has held since. i'm writing because most of the clients who do this audit benefit from light ongoing monitoring afterward, and i wanted to offer it cleanly rather than tack it on by surprise.

what it would look like:

- tail mode runs continuously alongside your stack
- spike alerts if cost crosses a threshold you set
- a monthly one-page summary
- one routing review per quarter

flat fee: {retainer_price}/month. cancel anytime. no setup work needed since the kit is already running.

interested? reply yes and i'll send a one paragraph addendum to the original sow.

{your_name}
