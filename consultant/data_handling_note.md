# data handling note

the audit only needs four things from a client. asking for less is a feature, not a limitation.

## what we ask for

1. **run records** — jsonl, json, or csv. one file per gateway, covering 7 to 14 days. the kit normalizes most field shapes, so you do not need a specific schema.
2. **active openclaw config** — the file that controls routing, heartbeat interval, and cron settings.
3. **task map** — one csv listing recurring jobs by name and family. format documented in `example_task_map.csv`.
4. **read access to working directories** — for the context weight scan. read-only is enough.

## what we do not ask for

- access to the model provider account or invoices
- access to the openclaw web ui or admin panel
- access to the underlying servers or containers
- access to client business data outside the agent workflows themselves

## redaction protocol

before any log file leaves the client environment, the consultant runs:

```
python redact_logs.py --input client_logs.jsonl --output redacted_logs.jsonl
```

this strips email addresses, phone numbers, urls, api keys, aws-shaped keys, bearer tokens, and credit card shaped numbers. it also collapses long content fields (prompt, completion, response, message, content, input, output, text) to a length placeholder.

if the client cannot run the redactor on their side, the consultant runs it on a clean machine immediately on receipt and deletes the unredacted copy within one hour.

## storage

- redacted logs live in a project-specific folder for the duration of the engagement
- the openclaw config is stored alongside the redacted logs
- nothing is uploaded to a third party service unless the client explicitly authorizes it in writing
- nothing related to this engagement is fed into a public ai api unless the client signs off

## retention

- redacted logs deleted 30 days after report delivery
- openclaw config deleted at engagement close
- audit deliverables (report, dashboard, ledger csv) retained for 1 year for warranty purposes only

## breach response

if a redacted log is shared with the wrong party, the consultant notifies the client within 24 hours of discovery, identifies which records were exposed, and confirms whether the redactor caught the sensitive fields.

## the one-line policy clients actually read

we look at four files, we redact before we look, we delete in 30 days, and we never feed your data into a third party ai service.
