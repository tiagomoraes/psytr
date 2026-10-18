# Changelog

## Unreleased

- Weekly report redesigned around how the week felt, from research on the DBT diary card, CBT mood checks and thought records, pre-session summaries and Cogni (`skills/sintr/references/report-framework.md`): how the week went, the person's agenda for the session (now on page 1), mood/energy/sleep, moments that stood out, what repeated, what helped.
- `scripts/report_pdf.py`: renders the reviewed report as a PDF in the sintr design system — sentiment chart over the last weeks, day-by-day grid, notebook cards for each moment, the person's words under the verbatim highlighter — via Playwright or a Chrome/Chromium binary, stdlib only. Checks every quote against the ledger. `make report-pdf WEEK=YYYY-Www`.
- The PDF, not the Markdown, is what the therapist receives; the owner previews it (`--draft`) before approving the send.
- Example: `docs/example-report.pdf`, built from the fictional fixture ledger in `scripts/fixtures/demo-ledger` (`make example-pdf`).

## 0.1.0 — 2026-10-17

- Initial release.
- Skill: supportive capture conversation, CBT thought-record entry framework (Tier 1/Tier 2), daily check-ins, therapy context, insights discipline.
- Ledger templates: config, checkins, entries, therapy, insights, reports.
- Weekly report pipeline: deterministic collector (`scripts/week_collect.py`) + agent-written report + approval-before-send + send recording.
- Privacy & safety references: local-first handling, default-deny sharing, crisis protocol, clinical limits.
- Installers: Hermes, Claude Code (plugin marketplace), generic.
