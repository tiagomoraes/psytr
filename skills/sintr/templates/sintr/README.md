# sintr ledger

This folder is a private psychological ledger. It belongs to one person and is maintained by their AI assistant.

**Sensitive personal data.** Keep it local. Directory `700`, files `600`. See the skill's `references/privacy-and-safety.md` for the full rules.

- `config.md` — owner preferences (language, timezone, therapy schedule, delivery channel, approval flag).
- `checkins/YYYY-MM.md` — lightweight daily check-ins (mood, energy, anxiety, sleep). Append-only.
- `entries/YYYY-MM.md` — structured situation entries (CBT thought records). Append-only, new entries at end of file.
- `therapy/current.md` — goals, themes in progress, tasks from the therapist.
- `therapy/sessions/YYYY-MM.md` — post-session notes. Append-only.
- `insights/current.md` — distilled observations (never diagnoses).
- `reports/YYYY-MM-DD.md` — one report per session (named by its date; `YYYY-Www.md` for a calendar week) and its status (`draft` → `reviewed` → `sent`); the `.pdf` rendered from each one is what the therapist receives.

Agents: read `config.md` and the relevant current file first; append events to the monthly logs at end-of-file; never share anything from this folder with anyone without the owner's explicit approval; never invent values (leave unknown fields empty).
