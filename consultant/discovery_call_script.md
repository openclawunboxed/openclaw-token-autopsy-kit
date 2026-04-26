# discovery call script

20 to 30 minutes. one purpose: decide whether you're going to send a quote and what tier it should be.

## before the call

read their questionnaire answers. mark any answer that needs follow-up. have the pricing tiers in front of you so you can quote on the call if it's clearly a fit.

## minute 0 to 2: framing

"thanks for the time. quick agenda: i want to understand your stack and your bill, you'll get to ask anything you want about how the audit works, and at the end we'll either set up the audit or i'll be honest if it's not a fit yet. sound good?"

then ask: "before i go through my questions, what's the one thing you're hoping to get out of this call?"

their answer tells you what to anchor the close to.

## minute 2 to 10: the diagnostic

go in this order. do not skip steps even if they sound similar.

1. "walk me through what your openclaw stack actually does day to day."
2. "what triggered you to look at the bill in the first place?"
3. "what's the spend trend over the last 60 days? flat, climbing, spiky?"
4. "which workflows are on heartbeat right now?"
5. "which workflows are on cron?"
6. "do you know the answer to that, or are you guessing?" (the honest answer matters more than the answer)
7. "what's your highest-cost model in the stack? what is it doing for you?"
8. "is there any workflow you'd consider mission-critical, where a quality drop would break a customer commitment?"

if at any point the answer is "i don't know," that's a good thing. it means the audit will produce real information.

## minute 10 to 18: scope and constraints

1. "how many gateways are we looking at?"
2. "can you pull jsonl or csv run records for me, or do i need to help set that up?"
3. "is there pii in the logs we'd need to handle carefully?"
4. "who has to approve a routing change once we identify one?"
5. "are there any workflows i'm not allowed to touch during the audit window?"
6. "what does success look like for you 30 days after the audit?"

## minute 18 to 25: explain the audit in their language

mirror their answers. if they care about a specific workflow, frame the audit around that workflow. if they care about predictable spend, frame it around the before/after baseline.

never over-explain the kit. the kit is your work. they care about the outcome.

key sentences to keep handy:

- "the deliverable is a written report plus a small html dashboard you keep, not a slide deck."
- "we run a baseline first so the change is provable, not opinion."
- "we touch one workflow at a time so a regression is contained."
- "you keep the configs and the report. there is no lock-in."

## minute 25 to 30: close

if it's a fit, quote the tier on the call. do not say "i'll send a quote later" unless you genuinely need to scope. delays kill close rates.

quoting language:

- "based on what you described, this is the operator audit tier. {price}. one week to deliver. half up front, half on report delivery."
- "i'll send a one page sow today. if you sign and send the deposit, we kick off monday."

if it's not a fit, say so:

- "i don't think the audit makes sense for you yet. you need {specific_thing} first. if you want, i can point you to a free way to do that, then we can talk in 30 days."

a clean no preserves the relationship and your time. an unclear yes costs both.

## after the call

within 24 hours:

- send the sow if you quoted
- send the free resource if you declined
- log the call in your tracker with the price quoted and the next action

within 7 days:

- one follow up if no response on the sow
- after that, treat it as a deferred lead and move on
