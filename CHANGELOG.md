# Changelog

## Unreleased

- The weekly report is prepared an hour before each therapy session (`report_lead`, from `session_day`/`session_time` in `config.md`) instead of on a fixed evening, so it is fresh for the session. It covers the 7 days up to that moment; consecutive reports meet exactly, so the evening after a session is never lost and nothing is counted twice. Reports are named by session date (`reports/YYYY-MM-DD.md`); `--session next|last|YYYY-MM-DD[THH:MM]` in both scripts (the default when a session is configured), `--week` for a calendar week without a fixed session.
- `week_collect.py --schedule` (`make report-schedule`) prints when to prepare the report and a cron line for it, so the agent can set up the job from `config.md`.
- Weekly report redesigned around how the week felt, from research on the DBT diary card, CBT mood checks and thought records, pre-session summaries and Cogni (`skills/sintr/references/report-framework.md`): how the week went, the person's agenda for the session (now on page 1), mood/energy/sleep, moments that stood out, what repeated, what helped.
- `scripts/report_pdf.py`: renders the reviewed report as a PDF in the sintr design system — a continuous, smoothed sentiment chart over the last weeks, day-by-day grid, notebook cards for each moment, the person's words under the verbatim highlighter — via Playwright or a Chrome/Chromium binary, stdlib only. Checks every quote against the ledger. Reads reports from weaker models leniently (section order, field synonyms, tables, emoji, overlong text) and reports every slip. `make report-pdf WEEK=YYYY-Www`.
- The PDF, not the Markdown, is what the therapist receives; the owner previews it (`--draft`) before approving the send.
- The PDF carries no transparency (soft masks, blend modes, opacity): the header light is a pre-rendered image and every color is opaque, so macOS Preview, Acrobat and browsers show the same page. `make report-light` re-renders the light.
- The collector reads `7/10`, `4,5/5`, `6,5` and `7h30` correctly.
- Example: `docs/example-report.pdf`, built from the fictional fixture ledger in `scripts/fixtures/demo-ledger` (`make example-pdf`).

## 0.1.0 — 2026-10-17

- Initial release.
- Skill: supportive capture conversation, CBT thought-record entry framework (Tier 1/Tier 2), daily check-ins, therapy context, insights discipline.
- Ledger templates: config, checkins, entries, therapy, insights, reports.
- Weekly report pipeline: deterministic collector (`scripts/week_collect.py`) + agent-written report + approval-before-send + send recording.
- Privacy & safety references: local-first handling, default-deny sharing, crisis protocol, clinical limits.
- Installers: Hermes, Claude Code (plugin marketplace), generic.
