# Installing psytr in an AI agent

psytr does not run as a service. Installation means two things:

1. install the psytr behavior instructions into your agent; and
2. create a psytr ledger the agent can read and write.

## Hermes Agent

```bash
git clone https://github.com/tiagomoraes/psytr.git
cd psytr
make install-hermes                              # or: ./installers/install.sh hermes [ledger-path]
```

What this does:

- copies `skills/psytr/` into `${HERMES_HOME:-~/.hermes}/skills/psytr`;
- creates the ledger (default `~/psytr`) from `templates/psytr/`, skipping files that already exist;
- sets `700` on the ledger directory and `600` on its files;
- writes `~/.psytr/config` with the ledger path and `~/.psytr/psytr.md` (a canonical copy of the instructions).

Verify: ask your agent to load the `psytr` skill, then send a test check-in:

> Humor 4/5, dormi 7h.

Expected: one short confirmation and a new `## checkin-...` block at the end of `~/psytr/checkins/YYYY-MM.md`.

## Claude Code

Easiest, from inside Claude Code (this repo is a self-hosted plugin marketplace):

```text
/plugin marketplace add tiagomoraes/psytr
/plugin install psytr@psytr
```

Or copy the skill manually:

```bash
./installers/install.sh claude-code ~/psytr
```

## Any other agent (OpenCode, OpenClaw, Cowork, custom)

```bash
./installers/install.sh generic ~/psytr
```

This copies the skill into `~/.psytr/skill/` and creates the ledger. Then:

- for skill-aware agents: point the agent at `~/.psytr/skill/` (or copy it into the agent's skills directory — the folder is a standard `SKILL.md` pack);
- for instruction-file agents (AGENTS.md / CLAUDE.md / custom system prompt): include `~/.psytr/psytr.md` or the skill's `SKILL.md`;
- for GUI agents (Cowork): zip `~/.psytr/skill/` and upload it as a skill.

## First-run checklist

1. Open `<ledger>/config.md` and fill: `name`, `language`, `timezone`, therapy fields (therapist name/contact, session day), `report_day`/`report_time`, and keep `require_approval: true` unless you explicitly want automatic sends.
2. Try a capture: describe a situation ("Preciso falar de uma situação...") and confirm the structured entry appears in `entries/YYYY-MM.md`.
3. Generate a test report for the current week: ask the agent for the weekly report, or run the collector directly (the installer also places it at `~/.psytr/bin/week_collect.py` for schedulers):

```bash
python3 scripts/week_collect.py --ledger ~/psytr --week this
```

4. Review the report draft in `reports/YYYY-Www.md`. When you're happy with the flow, wire the schedule.

## Scheduling the weekly report

Run the weekly flow with whatever scheduler your environment has:

- **Hermes**: a cron job (agent-driven, so it can write the report), scheduled before your session — e.g. Sundays 20:00 local, prompt: "psytr: generate this week's report from the ledger, save it to reports/, and send me a summary for review. Do not send anything to the therapist without my approval."
- **system cron / launchd**: schedule `scripts/week_collect.py` for the digest, and have your agent pick it up on your next interaction.

Keep approval-before-send on (`require_approval: true`) unless you have deliberately decided otherwise.

## Updating / uninstalling

- Update: `git pull` and re-run the same install command (skill files are replaced; the ledger is never overwritten).
- Uninstall: delete the installed skill folder and, if you want, the ledger. Nothing else was touched.
