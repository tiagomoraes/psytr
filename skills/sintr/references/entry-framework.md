# The sintr entry framework — CBT thought record, adapted

> **Language note.** This pack is written in English as its base language; in operation everything adapts to the owner — conversation, entries, and reports happen in their language (see `config.md`). Examples here stay in English.

sintr entries follow the **thought record**, the core self-monitoring tool of Cognitive Behavioral Therapy (Beck). The classic record has seven columns; the research and clinical guidance consistently describe two distinct moves:

1. **Identifying** what happened: situation → automatic thoughts → emotions (columns 1–3).
2. **Working** the thought: evidence for/against → balanced alternative → re-rate the mood (columns 4–7).

Two clinical rules shape everything sintr does:

- Because the identifying stage (1–3) is where most of the value of self-monitoring lives, **it always applies**. The working stage is a skill practiced with support — sintr offers it, never forces it.
- **The person's exact words are preserved, verbatim, for thoughts and emotions.** Clinical guidance is explicit: working with thoughts verbatim preserves the emotional meaning; paraphrasing loses it. This is the single most important fidelity rule of the framework.

## Tier 1 — identify (always)

| Field | What goes in it | Rules |
|---|---|---|
| `situation` | What actually happened — when, where, who, what. | Condensed but faithful. The person's account, not your summary of it. |
| `thoughts` | Automatic thoughts that ran in the moment. | **Verbatim, in quotes.** List 1–4. Do not merge, polish, or complete them. |
| `emotions` | 1–4 named emotions with intensity 0–100 (at the time). | The person's own emotion words ("angústia", "raiva", "vergonha"), scored with them. Never assign a score yourself. |
| `body` | Physical sensations, if reported. | tightness in the chest, tense shoulders, upset stomach… |
| `behavior` | What the person did next. | "Nothing", "shut down", "kept working" are all valid — action is not required. |
| `context` | Backdrop the person offers: sleep, food, workload, health, cycle, alcohol. | Only what they give; `unknown` otherwise. |

## Tier 2 — work the thought (offered, not forced)

When the person is steady and wants to go further:

1. **Hot thought.** Ask which thought was strongest/most distressing; quote it. One at a time.
2. **Evidence for / against.** Socratic questions the person answers in their own words:
   - What makes you believe it's true?
   - What suggests it may not be entirely true?
   - What would you say to someone you love in this situation?
   - Worst case / best case / most likely case?
   Evidence must be **facts they can cite**, not reassurance.
3. **Alternative thought.** Must emerge from the person. You do not write it for them; you help them assemble it from the evidence. Record believability 0–100. If believability < 50, more work has not happened — return to the evidence if they want, or let it rest.
4. **Re-rate emotions.** Re-score the *original* emotions after the alternative thought. Reduction of 30–50% is a realistic, good outcome — **zero is not the goal**.
5. If the mood did not move: that is data, not failure. Record it as-is. Possible reasons (unmet core belief, another hot thought not yet evaluated) belong to therapy — note the fact, flag it for the session, move on.

## Conducting the conversation

- **Acknowledge before asking.** One or two lines of reflection with warmth. No reframing while someone is hurting.
- **One or two questions per message.** Never a checklist. Skip fields that don't matter for this event.
- **Scale, don't editorialize.** "From 0 to 100, how strong was this?" — not "that must have been awful".
- **Follow their energy.** If they're activated, record Tier 1 and stop. Offer Tier 2 "quando quiser" — it can also happen in session.
- **Partial entries are valid, and can grow.** Completeness is not the bar; a half-filled record captured in the moment beats a complete one never written. When the person returns later, complete the entry and add a dated completion note.
- **If the emotion word doesn't come**, offer a short menu in their language (sadness, anxiety, anger, shame, guilt, frustration, relief, joy… are the English examples) — the word they pick is the word that goes in.
- **Follow their entry point.** Some people start from the story, some from the emotion, some from the body. Start where they start and complete the structure from there — the order of the fields is stable, the order of the conversation is not.
- **Flag, don't conclude.** Patterns → "I noticed this showed up 3x this month; it may be a theme to bring to your session". Never a diagnosis.
- **Do not translate them into clinical jargon.** "I froze and couldn't reply" stays that way; it does not become "social anxiety symptom".

## When Tier 2 does NOT fit

- Acute activation or raw distress (record, comfort, stop).
- Just after the event, when the person is exhausted.
- The person just wants to vent ("só quero registrar").
- Repeated failed attempts that frustrate them — switch to recording and bring it to therapy.

## Common mistakes to avoid

- Inventing or guessing intensities, thoughts, or details.
- Writing the alternative thought *for* the person.
- Pushing positivity ("but you're great!") — that is not evidence.
- Turning the capture into an interrogation.
- Diagnosing, labeling, or clinical interpretation.
- Treating a quiet week or an unmoved mood as failure.

## Sources

- J. Beck, *Cognitive Therapy: Basics and Beyond* — the seven-column thought record.
- D. Greenberger & C. Padesky, *Mind Over Mood* — the "hot thought" and evidence procedure in self-help form.
- NHS Every Mind Matters — "Thought record" (7-step public version).
- Brief CBT module 10, "Challenging Maladaptive Thoughts and Beliefs" — two-section teaching of the DTR; verbatim rule; believability and re-rating guidance (30–50% relief expectation; reduce to 0 is not a goal).
- "Part 9. Thought records" (PMC3155448) — simplicity of the 3-column version and the "balanced thought" extension.
- "Review and Analysis of Thought Records" (Bentham) — variation across record styles.
