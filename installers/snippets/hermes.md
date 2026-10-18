# Hermes usage snippet

Load the skill (or just ask naturally — Hermes picks it up):

```bash
hermes --skills sintr
```

Example prompts (in the owner's language; English examples):

- "I need to talk about something that bothered me today: ..."
- "Mood 3/5, slept 6h30."
- "Generate my weekly report."
- "Send the report to my therapist."   (only after you reviewed it)

Weekly automation: create a Hermes cron job (agent-driven) that runs the report flow an hour before your session (`week_collect.py --schedule` prints when, from `config.md`) and delivers the draft PDF to you for review. Keep sends to third parties behind explicit approval.
