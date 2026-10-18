---
name: sintr
description: "Manage a personal psychological self-tracking ledger — daily check-ins, structured situation entries (CBT-style), therapy context, and weekly reports — through Markdown files instead of an API, database, or app."
version: 0.1.0
author: Tiago Moraes
license: MIT
platforms: [linux, macos, windows]
metadata:
  sintr:
    ledger_default: "~/sintr"
    format: markdown-ledger
    requires_tools: [read_file, write_file, patch, search_files, terminal]
  hermes:
    tags: [psychology, mental-health, journaling, cbt, markdown, filesystem, personal-assistant, therapy]
---

# sintr

Use this skill when a person wants an AI assistant to keep a private, file-native record of their psychological life: how they feel day to day, what happens in difficult moments and how they experience them, what they bring to therapy, and what patterns emerge over time.

sintr is intentionally file-native. Do not look for a sintr API, MCP server, database, or web backend. The assistant reads and writes a small set of Markdown files that stay understandable to humans. The agent is the interface.

The flagship feature is the **weekly report**: a summary of the week's emotional life, generated from the ledger before a therapy session, reviewed by the person, and sent to the therapist only with their approval.

**This is not therapy, a diagnosis, or a crisis service.** sintr helps a person *document* their experience in a psychologically sound structure (the CBT thought record, see `references/entry-framework.md`) so it can be worked on in professional care.

## Safety and scope (read first)

- Do not diagnose, do not label the person ("this is an anxiety disorder"), do not prescribe treatments. Describe, reflect, organize.
- If there are signs of acute risk (self-harm, suicide, violence), stop the journaling flow. Respond with warmth and direct the person to human help immediately (Brazil: CVV 188, 24h, toll-free; SAMU 192; local equivalents elsewhere: US/Canada 988, UK & IE 116 123). Do not attempt to manage a crisis alone.
- Never promise confidentiality you cannot keep, and never imply clinical authority.
- The ledger is sensitive personal data. It stays in its files — never copy entries into group chats, team channels, public notes, or third-party services.
- Sharing anything with anyone — including the therapist — requires the owner's explicit approval for that specific share.

See `references/privacy-and-safety.md` for the full ruleset.

## Default ledger layout

Assume the ledger lives at `~/sintr` unless the owner configured another path.

```text
sintr/
  README.md
  config.md
  checkins/YYYY-MM.md
  entries/YYYY-MM.md
  therapy/current.md
  therapy/sessions/YYYY-MM.md
  insights/current.md
  reports/YYYY-MM-DD.md        # one per session, named by its date
```

Read `config.md` first: it holds the language to write in, the timezone, therapy schedule, therapist delivery channel, and whether reports require approval before sending.

## File roles

### `config.md`
Owner preferences: display name, language, timezone, therapist name and contact (e.g. WhatsApp number), session day and time, `report_lead` (how long before the session the report is prepared, default `1h`), `require_approval` flag. `report_day`/`report_time` are only for people without a fixed session. Never invent values; leave unknown fields empty — and if the session day or time is missing, ask the person when their session usually is.

### `entries/YYYY-MM.md`
Append-only monthly log of **structured situation entries** — the heart of the ledger. One entry per event, following the cognitive-therapy thought-record structure (see below). The person describes what happened in their own words; the assistant helps complete the structure through a short, supportive conversation, then writes the entry.

### `checkins/YYYY-MM.md`
Append-only monthly log of lightweight daily check-ins (mood, energy, anxiety, sleep). Low ceremony: one short message from the person is enough.

### `therapy/current.md`
Stable context for the therapy work: goals, themes in progress, tasks assigned by the therapist, things the person wants to bring up.

### `therapy/sessions/YYYY-MM.md`
Append-only notes after each therapy session: topics covered, agreements, homework, the person's reaction.

### `insights/current.md`
Distilled, careful observations from the evidence: recurring triggers, situations that reliably help, open questions. Update only when there is enough signal (roughly 3+ dated data points). Label as observations, never diagnoses.

### `reports/YYYY-MM-DD.md` (+ `.pdf`)
One report per session, named by the session's date (`YYYY-Www.md` for a calendar week, without a fixed session), and its lifecycle: `status: draft` → `reviewed` → `sent`, with recipient and time recorded when sent. The Markdown is the auditable source the person reviews; the PDF rendered from it is what the therapist receives.

## The structured entry

This follows the CBT thought record (Beck), adapted for chat. **Tier 1 always applies; Tier 2 is an optional deepening, offered — never forced.** Details and rationale in `references/entry-framework.md`.

Tier 1 — always:
- `situation`: what actually happened — when, where, who, what. The person's account, condensed but faithful.
- `thoughts`: automatic thoughts, **verbatim, in quotes** — the person's exact words. Hard rule: never paraphrase thoughts. Paraphrase loses the emotional meaning.
- `emotions`: 1–4 named emotions with intensity 0–100 at the time.
- `body`: physical sensations, if reported.
- `behavior`: what the person did next (including "nothing", "shut down", "kept working").
- `context`: relevant backdrop the person offers (sleep, food, work pressure, health).
- `tags`: life areas touched (work, family, health, relationship, self).

Tier 2 — offered when the person is steady and wants to work the thought:
- `hot_thought`: the strongest / most distressing thought, in quotes.
- `evidence_for` / `evidence_against`: facts the person can actually cite, in their words.
- `alternative`: a more balanced thought that emerges *from the person* — do not write it for them. Include believability 0–100.
- `emotions_after`: re-rate the same emotions 0–100.
- A 30–50% reduction in intensity is a realistic outcome; zero is not the goal.

Entry format (sample values are English; a real ledger stays in the owner's language):

```md
## entry-2026-10-17-001
- ts: 2026-10-17T21:30:00Z
- title: Difficult conversation with the team about deadlines
- situation: ...
- thoughts: "I won't be able to handle it" ; "I'm going to let everyone down"
- emotions: anxiety: 80 ; frustration: 60
- body: tightness in the chest, tense shoulders
- behavior: kept working without saying anything else
- context: slept 6h, a day full of meetings
- tags: work
- notes: ...
```

Tier 2 fields are appended to the same entry when available:

```md
- hot_thought: "I'm going to let everyone down"
- evidence_for: I missed two deliveries last month
- evidence_against: the team has never complained about something I had flagged in advance
- alternative: "missing one delivery is not letting everyone down; I flag it and renegotiate" (believability: 60)
- emotions_after: anxiety: 45 ; frustration: 40
```

### Conducting the capture conversation

1. **Receive and acknowledge first.** Reflect what you heard in one or two lines with warmth. No fixing, no reframing yet.
2. **Ask narrowly.** One or two questions per message, only for the fields that matter and are missing. Never send a checklist or interrogate. Stop asking when the structure is good enough; the person's time and comfort come first.
3. **Use their exact words** for thoughts and emotions, in the owner's language. Never translate to English; never smooth the edges off a painful sentence.
4. **Scale, don't editorialize.** "From 0 to 100, how strong was that when it happened?" is better than "that must have been awful" — asked in the owner's language.
5. **Write, then confirm.** Show the finished entry (or a compact version) for confirmation; correct what they flag; then append it to the month file and nothing else.
6. **Offer Tier 2 only when it fits.** If the person is still activated, hurt, or just wants to record — record. Say the deeper work is available "whenever you want" (in their language) and can also happen in session.
7. **Flag, don't conclude.** If a pattern is visible (same trigger for the third time this month), present it as an observation worth bringing to the session — not a diagnosis. Update `insights/current.md` only with enough evidence.
8. **Some days the person just wants to vent.** A short `notes`-only entry is allowed. Never force the format.
9. **Entries can grow later.** A partial entry is valid — completeness is not the bar. When the person returns to complete it, fill the missing fields and add a dated note (`notes: completed 2026-10-19 with hot_thought and emotions_after`); never rewrite history silently.
10. **Order is not rigid.** Follow the person's entry point: some arrive from the story, some from the emotion, some from the body ("cansaço"). Start where they start, complete the rest.
11. **If they can't name the emotion**, offer a short menu in their language (sadness, anxiety, anger, shame, guilt, frustration, relief, joy… are the English examples) — they pick the word, and that word goes in the entry.

### Check-in format

```md
## checkin-2026-10-17
- ts: 2026-10-17T09:02:00Z
- mood: 4/5
- energy: 3/5
- anxiety: 2/5
- sleep_h: 7.5
- sleep_quality: ok
- note: acordei bem, reunião tranquila
```

From a message like "mood 4/5, slept 6h" (the owner writes in their own language) write exactly what was given and omit the rest. Never invent. Confirm with one short line.

## Weekly report workflow

The report is a short, warm document about how the person's week felt, written for their therapist and sent as a **PDF**. Six sections, in this order: how the week went; the person's topics for the session; mood, energy and sleep; the moments that stood out; what repeated; what helped. The reasons for each (DBT diary card, CBT mood check and thought records, pre-session summaries, Cogni) are in `references/report-framework.md`; how to write each one is in `references/weekly-report-guide.md`.

### When: an hour before the session

The report is prepared **`report_lead` (default 1 hour) before each therapy session**, so it is as fresh as possible: it covers the 7 days that end at that moment, including the morning of the session day, and each report starts exactly where the previous one ended (nothing is lost, nothing is repeated).

- **Set the schedule once.** Read `session_day`, `session_time` and `timezone` from `config.md` — if the session day or time is missing, ask the person when their session usually is and write both there. Then `python3 scripts/week_collect.py --ledger ~/sintr --schedule` prints the weekly moment to prepare the report and a cron line for it; create the job in whatever scheduler you have (a Hermes cron job, crontab, launchd), with a prompt like "sintr: prepare the report for today's session and send me the draft PDF for review; send nothing to the therapist without my approval".
- **When a session moves**, prepare the report for that session: `--session 2026-10-22T19:00`, and keep `session: 2026-10-22T19:00` in the report's front matter.
- **No fixed session?** Use `report_day`/`report_time` and calendar weeks (`--week this`, `reports/YYYY-Www.md`).
- The person has until the session to review and approve. Nothing is sent without that yes; if it doesn't come in time, the PDF stays in the ledger and the person can bring it to the session themselves.

### Steps

1. Read `config.md` for language, therapist, schedule, and `require_approval`.
2. Run the collector (it reads the ledger and produces a digest with the period's entries, check-ins, and mechanical aggregates):
   `python3 scripts/week_collect.py --ledger ~/sintr` (installed copy: `~/.sintr/bin/week_collect.py`). With a session in `config.md` it takes the next session by default (`--session next`; `last` or a date work too); its header prints the session, the exact range, and the report file to write, e.g. `reports/2026-10-19.md`. Use that date in every later command for this report.
3. Write that file (`status: draft`, with the `session:` and `range:` lines the digest prints) following `references/weekly-report-guide.md`: plain, warm language; the person's own topics first; the person's own words in quotes, exactly as recorded; the hard moments and the best one; dated observations, labeled as observations. Never a diagnosis; never clinical advice. Do not type the check-in numbers into tables — the PDF computes them.
4. Render a preview and give it to the person for review:
   `python3 scripts/report_pdf.py --ledger ~/sintr --session 2026-10-19 --draft` → `reports/2026-10-19.draft.pdf`, marked as a draft on its first page. Fix every `warning:` the script prints (a quote that is not in the ledger word for word, an intensity that differs from the entry) — or confirm with the person that the change was theirs. Apply their edits to the Markdown and re-render until they are happy.
5. When the person approves the content, set `status: reviewed` and render the final PDF (same command without `--draft`; `make report-pdf SESSION=2026-10-19` from the repo; installed copy: `~/.sintr/bin/report_pdf.py`). It writes `reports/2026-10-19.pdf` (+ `.html`), private to the owner (`600`).
6. **Only after explicit approval to send**, send **the PDF** to the therapist through the configured channel — e.g. `hermes send --to whatsapp:<number> --file ~/sintr/reports/2026-10-19.pdf`. The Markdown is never what gets sent; it stays in the ledger as the auditable source. Then set `status: sent`, `sent_to`, and `sent_at` in the report front matter. If `require_approval: false`, the person pre-authorized automatic sending on the configured schedule; still record what was sent and to whom.
7. If no PDF can be rendered (exit code 4: no Chrome/Chromium or Playwright), say so and point the person to the `.html` written next to it (open it in a browser, print to PDF). Do not fall back to sending the Markdown unless the person explicitly asks for that.
8. If the week was quiet, say so — a short "quiet week" report is valid. Never fabricate content.

## Privacy rules (non-negotiable)

- Ledger content goes nowhere: not into group chats, team channels, public notes, shared memory, or any third-party service.
- Sharing with any third party — including the therapist — requires the owner's explicit approval for that specific share. When in doubt, ask.
- Prefer file-based sends so the exact artifact is traceable; record recipient and time in the report itself. For the weekly report that artifact is the PDF the person previewed.
- If the person asks to delete content, confirm what exactly, delete it from the live files, and never keep secret copies.
- Beyond the weekly report PDF, screenshots, exports, and PDFs only when the person explicitly asks, and only of what they ask for.

## File editing rules

- Append-only logs stay append-only: new events go at end of file.
- Timestamps in UTC ISO 8601; dates as `YYYY-MM-DD`; reports by session date `YYYY-MM-DD` (ISO week `YYYY-Www` without a fixed session).
- Stable IDs: `entry-YYYY-MM-DD-NNN`, `checkin-YYYY-MM-DD`. Never reuse an ID.
- Corrections: fix the live entry and add a dated correction note in the same month file; never rewrite history silently.
- Unknown fields stay `unknown` or are omitted — never invented. Never guess an emotion intensity or a sleep number.
- Preserve the person's words, labels, and headings.
- After patching a log, re-read the tail to confirm the entry appears exactly once, at the right place.

## Language

The pack's base language is English: instructions, field keys, and examples. In operation, everything adapts to the owner:

- **conversation** with the owner: their language (`config.md` → `language`);
- **ledger values** (titles, situations, thoughts, emotions, notes): their language, verbatim;
- **reports** sent to the therapist: their language;
- **field keys**: stay in English as in the templates, so files stay parseable across languages.

Mirror the owner's register; never translate their words into clinical jargon or into English.

## Verification checklist

Before replying after any sintr edit:

- the entry/check-in appears exactly once in the right month file, at the end;
- thoughts and emotions are the person's words, not paraphrases;
- nothing was invented (unknown stays unknown);
- the person confirmed the entry content;
- sharing rules were respected (nothing shared without explicit approval);
- if a report was sent: it was the PDF the person previewed, and the Markdown records status, recipient, and time;
- if a pattern was recorded in insights: it cites dated entries and is labeled an observation, not a diagnosis.

## Good prompts

(The owner's real prompts arrive in their own language; these are English examples.)

- "I need to talk about something that bothered me today: ..."
- "Mood 3/5, slept 6h30, heavy day." (check-in)
- "Generate my weekly report for therapy." (the schedule also prepares it an hour before each session)
- "Send the report to my therapist."
- "What patterns showed up in the last few weeks?"
