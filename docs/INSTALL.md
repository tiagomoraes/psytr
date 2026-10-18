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

1. Open `<ledger>/config.md` and fill: `name`, `language`, `timezone`, therapy fields (therapist name and contact, `session_day` and `session_time`), and keep `require_approval: true` unless you explicitly want automatic sends. The weekly report is prepared `report_lead` (default `1h`) before each session; `report_day`/`report_time` are only for a calendar-week report when there is no fixed session.
2. Try a capture: describe a situation ("Preciso falar de uma situação...") and confirm the structured entry appears in `entries/YYYY-MM.md`.
3. Generate a test report for your next session: ask the agent for the weekly report, or run the collector directly (the installer also places it at `~/.sintr/bin/week_collect.py` for schedulers). Its header names the report file, e.g. `reports/2026-10-19.md`:

```bash
python3 scripts/week_collect.py --ledger ~/sintr            # the next session (or --session 2026-10-19, --week this)
```

4. Review the report draft in `reports/2026-10-19.md`, then render it (the installer places the generator at `~/.sintr/bin/report_pdf.py`):

```bash
python3 scripts/report_pdf.py --ledger ~/sintr --session 2026-10-19 --draft   # preview, marked as a draft
python3 scripts/report_pdf.py --ledger ~/sintr --session 2026-10-19           # final, once status: reviewed
```

   The PDF lands next to the Markdown (`reports/2026-10-19.pdf`, plus the `.html` it was printed from). Rendering needs Google Chrome, Chromium or Edge (found automatically, or set `SINTR_CHROME=/path/to/chrome`), or Playwright (`pip install playwright && playwright install chromium`). Without any of them the script still writes the HTML, which you can print to PDF from a browser. When you're happy with the flow, wire the schedule.

## Scheduling the weekly report

The report is prepared an hour before each session (`report_lead`), so it is fresh when you walk in and covers the 7 days up to that moment. Ask the collector when that is:

```bash
python3 scripts/week_collect.py --ledger ~/sintr --schedule   # or: make report-schedule
```

```text
session:  Mondays at 18:00 (America/Sao_Paulo)
report:   Mondays at 17:00 (America/Sao_Paulo), report_lead 1h before the session
cron, in the ledger's timezone (cronie, systemd timers):
  CRON_TZ=America/Sao_Paulo
  0 17 * * 1
```

Then run the weekly flow at that moment with whatever scheduler your environment has:

- **Hermes**: an agent-driven cron job (so it can write the report) at that time, with a prompt like: "sintr: prepare the report for today's session from the ledger, render the draft PDF and send it to me for review. Do not send anything to the therapist without my approval." Your agent can set this up itself from `config.md`.
- **system cron / launchd**: schedule `scripts/week_collect.py` for the digest at that time, and have your agent pick it up.

If a session moves, ask for the report for that session (`--session 2026-10-22T19:00`). Without a fixed session, schedule a calendar-week report on `report_day`/`report_time` and use `--week`.

Keep approval-before-send on (`require_approval: true`) unless you have deliberately decided otherwise.

## Updating / uninstalling

- Update: `git pull` and re-run the same install command (skill files are replaced; the ledger is never overwritten).
- Uninstall: delete the installed skill folder and, if you want, the ledger. Nothing else was touched.
