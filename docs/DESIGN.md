# Design

## What sintr is

An agent pack for AI-first management of a person's psychological history: a portable skill + a Markdown ledger + a report pipeline. No database, no service, no app. The agent is the interface; the files are the product.

## Principles

1. **File-native.** One folder, plain Markdown, readable and editable by humans. Any agent with file tools can operate it.
2. **CBT-grounded structure.** Entries follow the thought record (Beck): situation → automatic thoughts → emotions → body → behavior, with the optional working stage (evidence, alternative, re-rate). See `skills/sintr/references/entry-framework.md`.
3. **Fidelity over completeness.** The person's exact words for thoughts and emotions; partial entries are valid and can grow; `unknown` beats invented.
4. **Local-first privacy.** Sensitive data stays in the ledger with strict permissions. Nothing is shared with anyone — including the therapist — without explicit approval.
5. **Deterministic where possible.** The collector and the PDF generator are stdlib Python scripts; the LLM writes prose on top of facts, not facts from thin air. The report's numbers and chart are computed from check-ins, and every quote in it is checked against the ledger.
6. **The report is the product surface.** The loop "week → digest → report → session" is what users actually experience. Everything else supports it.
7. **English base, owner's language in operation.** The pack (instructions, field keys, docs) is written in English so it travels; the conversation, ledger values, and reports adapt to the owner's language and words.

## Data model

```text
sintr/
  config.md                    # preferences; language, timezone, therapist, approval flag
  checkins/YYYY-MM.md          # append-only quick check-ins (mood/energy/anxiety/sleep)
  entries/YYYY-MM.md           # append-only structured entries (thought records)
  therapy/current.md           # goals, themes, tasks (updated in place)
  therapy/sessions/YYYY-MM.md  # append-only post-session notes
  insights/current.md          # distilled observations (3+ data points rule)
  reports/YYYY-Www.md          # weekly reports with lifecycle status (+ .pdf, the sent artifact)
```

Decisions and rationale:

- **Monthly append-only logs** keep diffs small, make history auditable, and avoid rewriting facts. Live state that answers "what is true now?" lives in `therapy/current.md` and `insights/current.md`.
- **Stable field keys in English, values in the owner's language.** Keys make files machine-parseable across users and locales; values (thoughts, emotions, situations) stay in the person's own language and voice.
- **ISO timestamps in UTC; ISO weeks for reports.** Unambiguous across timezones; weeks align with how therapy sessions are usually discussed.
- **Intensity 0–100 for emotions.** Wide enough for nuance, coarse enough to compare across weeks; matches standard thought-record practice.
- **Tier 1 / Tier 2 split.** Tier 1 is always captureable; Tier 2 (cognitive restructuring) is a skill that benefits from support and practice — offered, never forced, and allowed to wait for the session.

## Flows

1. **Capture** — person tells a situation → short supportive conversation → structured entry → confirmation → append.
2. **Check-in** — one message → parse what's given → append; never invent missing numbers.
3. **Weekly report** — collector digest → agent writes the report Markdown → PDF preview → owner review → `reviewed` → final PDF → explicit approval → the PDF is sent via gateway → record `sent_to`/`sent_at`. Structure and sources: `skills/sintr/references/report-framework.md`.
4. **Therapy** — post-session notes + tasks feed `therapy/current.md`; the report references open tasks.

## Privacy model

- Ledger perms `700/600`; local-first by default; no cloud sync in the standard setup; git only as private repo and only if the owner wants.
- Default-deny sharing: approval gates on every external share; approval recorded in the report front matter.
- Crisis protocol and clinical limits documented in `skills/sintr/references/privacy-and-safety.md`.
- The agent never copies ledger content into shared channels, group chats, or third-party services.

## Non-goals

- Not therapy, diagnosis, or a crisis service.
- Not a clinical instrument: no psychometrics, no scoring batteries, no treatment planning.
- Not a multi-user SaaS: one person per ledger by design. (Multiple people = multiple ledgers.)
- No compliance claims (LGPD/HIPAA/GDPR); the architecture simply minimizes exposure: data never leaves the owner's machine except through approved shares.

## Roadmap ideas

- Encrypted-at-rest option (age/gpg wrapper) for the ledger.
- Wearable/sleep import into check-ins.
- Multi-week trend view in `insights/`.
- Local web view (read-only) for browsing entries.
