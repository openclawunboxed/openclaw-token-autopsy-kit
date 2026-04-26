# scope of work template

fill in the bracketed fields. keep it on one page. clients sign one page faster than they sign three.

---

## scope of work

**project**: openclaw token autopsy
**client**: {client_name}
**vendor**: {your_business_name}
**date**: {date}
**engagement window**: {start_date} to {end_date}

## what we will deliver

1. a normalized spend ledger covering {window_in_days} days of {client_name}'s openclaw run records
2. a written audit report identifying the highest-cost rows, the lane and routing problems behind them, and a ranked change list
3. a heartbeat audit and a cron migration plan for the workflows in scope
4. a context weight scan for the openclaw working directories you grant access to
5. a before-and-after baseline if a routing change is implemented during the engagement window
6. a self-contained html dashboard summarizing the findings
7. one 30-minute implementation handoff call

## what is in scope

- {list specific gateways, agents, or workflows}

## what is not in scope

- model fine-tuning
- new workflow design
- managed hosting
- billing disputes with model providers
- changes to any workflow not listed in scope without written approval

## what we need from you

- export of run records (jsonl, json, or csv) for the window above
- a copy of the active openclaw config
- read access to the working directories used by the agents in scope
- a named approver for any routing or config change
- {anything else specific to this engagement}

## privacy and data handling

- raw logs will be redacted with the kit's redactor before any analysis
- raw logs will be deleted from {vendor} systems within 30 days of report delivery
- the audit report will not contain pii or client identifying content unless you specifically request it
- {vendor} will not retain a copy of the openclaw config after the engagement closes

## fee

- total: {price}
- payment terms: 50 percent on signature, 50 percent on report delivery
- payment method: {wire / stripe / ach}

## quality and rollback

if a routing change implemented during the engagement window causes a measurable quality regression in any workflow, we will recommend rollback in writing within 24 hours. rollback support is included.

## out clause

either party may end the engagement with written notice. if {vendor} ends the engagement, no fees are owed. if {client_name} ends the engagement after kickoff, the deposit is retained.

## signatures

{client_name}: ____________________________ date: ___________

{your_name}: ____________________________ date: ___________
