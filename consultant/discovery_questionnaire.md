# discovery questionnaire

send this to a prospect before the discovery call. you want answers in writing because most of the audit pricing decision is in the answers, and most of the prospects you should walk away from will reveal themselves here.

## stack basics

1. how many openclaw gateways do you run?
2. how many distinct agents are configured across those gateways?
3. how is openclaw deployed (mac mini, vps, docker, wsl2, other)?
4. which providers are wired in (anthropic, openai, openrouter, local, other)?
5. roughly how long has the stack been running in its current shape?

## the bill

6. what was your spend last month across all model providers?
7. what did you expect it to be?
8. when did the gap first show up (give a week or a date if possible)?
9. did anything change around that time (new agent, new workflow, new heartbeat interval, new model)?
10. do you have an itemized invoice or do you only see the total?

## what the stack does

11. list the recurring jobs (anything that runs on a schedule or on heartbeat). one line each.
12. for each recurring job, mark whether it needs exact timing or whether approximate is fine.
13. list the tool-heavy workflows (browser, pdf, screenshot, scraping). one line each.
14. which workflow do you trust the least to be cost-disciplined?

## access and data

15. can you export run records (jsonl, json, or csv) for a 7 to 14 day window?
16. is there pii or client-confidential text in those records? (yes/no/unsure)
17. who is allowed to see the raw logs?
18. who is allowed to see the audit findings?

## constraints

19. are there workflows we are not allowed to touch during the audit window?
20. are there workflows that must keep running while we audit?
21. is there a quality bar a regression in any workflow would breach? (e.g. inbox triage cannot drop below 95% correct routing)
22. do you have a rollback plan for routing or config changes?

## decision

23. who approves a routing change in your org?
24. what is the budget range you have already allocated for this audit?
25. what does success look like 30 days from now?

## red flag check (for your own use, not for them)

after they answer, score it before quoting:

- vague answers to questions 6 through 10 → discovery call to ground the numbers, do not quote yet
- "no" or "unsure" to question 15 → audit is impossible without records, walk away or do a paid discovery
- yes to question 16 plus no to question 17 → you need a data handling note and probably an nda
- no answer to question 23 → the project will stall on approval, charge a deposit
- question 24 well below your starter price → either a smaller scoped offer or a polite decline
