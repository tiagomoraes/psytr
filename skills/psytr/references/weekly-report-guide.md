# Weekly report guide

The weekly report is sintr's flagship artifact: a plain-language summary of the owner's emotional week, prepared **for the therapist**, written by the agent from the ledger, and **reviewed by the owner before anything is sent**.

The report exists to give the therapist the context they cannot get from a 50-minute session: what actually happened during the week, in the owner's own words.

## Pipeline

1. Collector: `python3 scripts/week_collect.py --ledger <path> --week <this|last|YYYY-Www>` → digest (entries, check-ins, aggregates).
2. Draft: the agent writes `reports/YYYY-Www.md` following this guide.
3. Review: the owner reads and edits. The agent applies requested changes.
4. Approval: only an explicit "manda / approve" from the owner enables sending.
5. Send: through the configured channel (default example: `hermes send --to whatsapp:<number> --file <report>`).
6. Record: update the report's front matter — `status: sent`, `sent_to`, `sent_at` — and nothing more.

If `require_approval: false` in `config.md`, the owner has pre-authorized the send on the configured schedule; record what was sent anyway.

## Required sections

```md
---
week: 2026-W42
range: 2026-10-12 → 2026-10-18
status: draft            # draft | reviewed | sent
generated_at: 2026-10-18T23:00:00Z
sent_to:                 # filled when sent
sent_at:                 # filled when sent
---

# Weekly report — [name] — 2026-W42

(Headings translated to the owner's language in real reports.)

## Summary
3–6 lines. Tone, central events, general state. Owner's language.

## Mood, energy & sleep
Averages and variation from check-ins; days outside the pattern. Facts with numbers.

## Notable situations
3–5 situations, one date line + 1–2 lines each. Owner's vocabulary.

## Recurring themes & patterns
Observations labeled as observations, with dates ("showed up on Oct 12 and Oct 15").
Never a diagnosis, never a closed clinical interpretation.

## What helped
Strategies the owner recorded as helpful (a walk, talking, better sleep…).

## Topics for the session
2–4 topics, as questions or open themes — the owner's own + observed patterns.

---
*Prepared from self-reports (check-ins and structured entries) with the help of a personal assistant. Not a clinical assessment.*
```

## Style rules

- Language: the owner's (`config.md` → language).
- Plain and factual. No clinical jargon unless the owner uses it.
- Every claim dated. Numbers from check-ins, quotes from entries (short ones).
- Observations labeled as observations. **No diagnosis, no advice to the therapist, no speculation about causes.**
- Minimize third-party identifying details (first names or initials; no clinical labels about other people).
- Mark the document as confidential, for the named therapist.
- Quiet week → a short honest report ("quiet week; X check-ins, Y entries; no new themes") rather than padding.

## Review checklist (for the owner)

- Nothing here surprises me.
- Nothing here is something I don't want my therapist to know.
- The facts are right.
- The topics reflect what I want to work on.

## What NOT to include

- Content from entries explicitly marked as not shareable (`share: no`).
- Clinical speculation of any kind.
- Details of third parties beyond what the story needs.
- Anything the owner asked to remove during review.
