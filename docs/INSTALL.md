# Installing sintr in an AI agent

sintr does not run as a service. Installation means two things:

1. install the sintr behavior instructions into your agent; and
2. create a sintr ledger the agent can read and write.

## Hermes Agent

```bash
git clone https://github.com/tiagomoraes/sintr.git
cd sintr
make install-hermes                              # or: ./installers/install.sh hermes [ledger-path]
```

What this does:

- copies `skills/sintr/` into `${HERMES_HOME:-~/.hermes}/skills/sintr`;
- creates the ledger (default `~/sintr`) from `templates/sintr/`, skipping files that already exist;
- sets `700` on the ledger directory and `600` on its files;
- writes `~/.sintr/config` with the ledger path and `~/.sintr/sintr.md` (a canonical copy of the instructions).

Verify: ask your agent to load the `sintr` skill, then send a test check-in:

> Humor 4/5, dormi 7h.

Expected: one short confirmation and a new `## checkin-...` block at the end of `~/sintr/checkins/YYYY-MM.md`.

## Claude Code

Easiest, from inside Claude Code (this repo is a self-hosted plugin marketplace):

```text
/plugin marketplace add tiagomoraes/sintr
/plugin install sintr@sintr
```

Or copy the skill manually:

```bash
./installers/install.sh claude-code ~/sintr
```

## Any other agent (OpenCode, OpenClaw, Cowork, custom)

```bash
./installers/install.sh generic ~/sintr
```

This copies the skill into `~/.sintr/skill/` and creates the ledger. Then:

- for skill-aware agents: point the agent at `~/.sintr/skill/` (or copy it into the agent's skills directory — the folder is a standard `SKILL.md` pack);
- for instruction-file agents (AGENTS.md / CLAUDE.md / custom system prompt): include `~/.sintr/sintr.md` or the skill's `SKILL.md`;
- for GUI agents (Cowork): zip `~/.sintr/skill/` and upload it as a skill.

## First-run checklist

1. Open `<ledger>/config.md` and fill: `name`, `language`, `timezone`, therapy fields (therapist name/contact, session day), `report_day`/`report_time`, and keep `require_approval: true` unless you explicitly want automatic sends.
2. Try a capture: describe a situation ("Preciso falar de uma situação...") and confirm the structured entry appears in `entries/YYYY-MM.md`.
3. Generate a test report for the current week: ask the agent for the weekly report, or run the collector directly (the installer also places it at `~/.sintr/bin/week_collect.py` for schedulers):

```bash
python3 scripts/week_collect.py --ledger ~/sintr --week this
```

4. Review the report draft in `reports/YYYY-Www.md`. When you're happy with the flow, wire the schedule.

## Scheduling the weekly report

Run the weekly flow with whatever scheduler your environment has:

- **Hermes**: a cron job (agent-driven, so it can write the report), scheduled before your session — e.g. Sundays 20:00 local, prompt: "sintr: generate this week's report from the ledger, save it to reports/, and send me a summary for review. Do not send anything to the therapist without my approval."
- **system cron / launchd**: schedule `scripts/week_collect.py` for the digest, and have your agent pick it up on your next interaction.

Keep approval-before-send on (`require_approval: true`) unless you have deliberately decided otherwise.

## Updating / uninstalling

- Update: `git pull` and re-run the same install command (skill files are replaced; the ledger is never overwritten).
- Uninstall: delete the installed skill folder and, if you want, the ledger. Nothing else was touched.
