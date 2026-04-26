# security hardening

short checklist for hardening an openclaw deployment before you run an audit on it. some of this matters more for client-facing or vps deployments than for a local mac mini.

## gateway exposure

- bind the gateway to localhost (127.0.0.1) unless you have a deliberate reason for public exposure
- if the gateway must be reachable, put it behind a reverse proxy with auth (caddy, nginx, traefik)
- never expose the gateway port directly to the public internet without auth in front of it
- block the gateway port at the firewall layer, not just at the openclaw config layer

## auth

- if openclaw supports an auth token or admin password, set one (do not use defaults)
- rotate the auth token quarterly or whenever a contractor with access leaves
- store the token in a secrets manager or in `.env` (never in source control)
- if the gateway is multi-tenant, each tenant gets a distinct auth token

## logs

- run `redact_logs.py` on any log file before sharing with a third party (auditor, consultant, vendor)
- set log rotation so you do not silently fill disk
- audit who has read access to the logs directory
- if your logs include client-confidential data, the logs directory should be encrypted at rest

## api keys for model providers

- store provider api keys in a secrets manager or `.env`, never in the openclaw config file directly if you can avoid it
- set per-key spend limits on the provider side as a hard ceiling
- rotate keys after every consultant engagement that ends
- monitor key usage on the provider dashboard for unexpected geographic origin

## browser-attached agents

- never attach an openclaw agent to your real signed-in personal browser for client work
- use a dedicated browser profile for each client or workflow
- close the agent's browser process when not in use, even on a local mac mini
- audit which sites the agent can reach (an agent with full browser access can read anything you can read)

## file system

- the agent's working directory should not contain unrelated personal or client files
- read access to the working directory should be restricted to the user account running openclaw
- bootstrap files (memory, identity, instructions) should not contain pii or secrets, even your own

## destructive actions

- any agent capable of destructive actions (delete, send email, transfer money, write to a database) should require manual confirmation by default
- if you turn off confirmation, do it on a per-action basis with explicit logging
- the cron migration planner classifies destructive actions as `manual_review` for this reason

## sharing audit deliverables

- the audit report should not contain raw log content from the client
- the dashboard html should be reviewed before sending (it embeds the heartbeat audit and anomaly report verbatim)
- if you used `redact_logs.py`, double-check the redacted file before letting it leave the client environment
- do not paste raw client logs into a public ai api unless the client signed off in writing

## post-engagement cleanup

- delete client run records 30 days after report delivery
- delete the client's openclaw config at engagement close
- empty your local terminal scrollback if you ran logs through `cat` or `head` during the audit
- audit your shell history file if you typed any client identifiers on the command line

## general posture

- assume any log file contains pii until proven otherwise
- assume any string longer than 100 characters in a log might contain a secret
- err toward over-redacting and under-storing
- when in doubt, ask the client what they consider sensitive before you start
