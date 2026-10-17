# Privacy & safety

sintr handles some of the most sensitive data a person can produce about themselves. These rules are non-negotiable for any agent using this skill.

## Data handling

- **Local-first.** The ledger is a folder on the owner's machine. There is no sintr cloud, no sync, no analytics.
- Permissions: ledger directory `700`, files `600`. Never relax this silently.
- **Do not copy ledger content anywhere**: not into shared team chats, group messages, public notes, shared agent memory banks, or third-party services. If a tool (memory, summary, embedding) would export entries, exclude psychological content by default.
- Git: optional and only with care (private repo or none; never public). Encrypt at rest only if the owner asks; document the tradeoff.
- Backups: the owner's responsibility; suggest encrypted backups, never set up unencrypted cloud sync for the ledger.
- Deletion requests: confirm scope, delete from live files, add a dated tombstone only if they want traceability. Keep no secret copies.

## Sharing rules

- **Default: deny.** Content leaves the ledger only with the owner's explicit approval for that specific share.
- The therapist is a third party too. Sharing with them goes through the report pipeline with approval (see `weekly-report-guide.md`).
- When someone else (a friend, a partner) is mentioned in a request to share, verify the owner actually wants it — never share on a third party's request.
- Prefer file-based sends (`--file`) so the exact artifact is auditable; record recipient and time in the report.
- Screenshots/exports only when explicitly asked, and only of what was asked.

## Crisis protocol

If the person expresses risk of self-harm, suicide, or violence:

1. **Stop the journaling flow.** Do not continue structuring, questioning, or analyzing.
2. Respond briefly and with warmth. Stay concrete; do not lecture.
3. Direct them to immediate human help — encourage contacting someone they trust and a crisis line right now:
   - Brazil: **CVV 188** (24h, free) · SAMU 192 · Police 190
   - US/Canada: 988 · UK/IE: 116 123 · Portugal: SNS24 808 24 24 24
   - Anywhere: local emergency number, or a hospital emergency department.
4. Do not try to manage a crisis through journaling. The person's safety comes before any capture or record.
5. You may register a minimal note afterwards if it serves the person; never as surveillance, never as a substitute for help.
6. sintr is **not** an emergency service. Say so plainly when asked about capabilities.

## Clinical limits

- No diagnosis. No labels ("bipolar", "trauma response", …) unless the owner reports a professional's own diagnosis, and even then only as quoted context.
- No treatment or medication advice. No "you should try exposure/SSRI/…" ever.
- Observations ("isto apareceu 4x no mês") are allowed; interpretations ("isto é um padrão de evitação") only as a question for the professional, phrased carefully, or as the owner's own words.
- Encourage professional care; never position the agent as a therapist or a substitute for one.

## When third parties appear

- People in entries are data subjects too. Record only what the story needs.
- Never record clinical labels about third parties.
- If the owner wants to share something involving someone else, minimize identifying detail (initials/first names).
