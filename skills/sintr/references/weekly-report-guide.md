# Weekly report guide

The weekly report is sintr's flagship artifact: a short, warm account of **how the owner's week felt**, prepared **for their therapist**, written by the agent from the ledger, reviewed by the owner, and sent as a **PDF** only with their approval.

It gives the therapist what a 50-minute session cannot reconstruct from memory: what happened during the week, how it felt at the time, and what the person wants to work on — in the person's own words. It is not a data export and not a clinical note. Why it is shaped this way (DBT diary card, CBT mood check and thought records, pre-session summaries, Cogni), with sources: `report-framework.md`.

## When, and which days

**An hour before the session.** The report is prepared `report_lead` (default `1h`) before each therapy session (`session_day`, `session_time` in `config.md`), so it is as fresh as it can be when the person walks in: the days just before a session are the ones memory blurs least and recall distorts most (`report-framework.md`). It covers **the 7 days that end at that moment** — the morning of the session day included — so each report starts exactly where the previous one ended: what the person wrote after last week's session is in, nothing is counted twice.

- `python3 scripts/week_collect.py --ledger <path> --schedule` prints the weekly moment and a cron line; the agent creates the job once (Hermes cron, crontab, launchd). If the session day or time is not in `config.md`, ask the person and write it there.
- A rescheduled session: `--session YYYY-MM-DDTHH:MM`, and the same `session:` in the front matter.
- Without a fixed session, a calendar week (`--week`, Monday to Sunday, `reports/YYYY-Www.md`) on `report_day`/`report_time`.
- The person reviews and approves before the session. No approval in time means nothing is sent; the PDF stays in the ledger and can be shown in the session.

## Pipeline

1. **Collect.** `python3 scripts/week_collect.py --ledger <path>` (the next session by default; or `--session <next|last|YYYY-MM-DD>`, `--week <this|last|YYYY-Www>`) → digest (entries, check-ins, aggregates). Its header names the report file, e.g. `reports/2026-10-19.md`, and the `session:` and `range:` lines for its front matter.
2. **Draft.** Write that file (`status: draft`) following this guide.
3. **Preview.** `python3 scripts/report_pdf.py --ledger <path> --session 2026-10-19 --draft` → `reports/2026-10-19.draft.pdf`, marked as a draft. Use the same date in every command for this report. Resolve every `warning:` it prints before showing it.
4. **Review.** The owner reads the preview; apply their edits to the Markdown and re-render. Content approved → `status: reviewed`.
5. **Render.** The same command without `--draft` → `reports/2026-10-19.pdf` (+ `.html`). Or `make report-pdf SESSION=2026-10-19`.
6. **Approve and send.** Only an explicit "manda / send it" from the owner enables sending, and **the PDF is what is sent** (default example: `hermes send --to whatsapp:<number> --file reports/2026-10-19.pdf`). The Markdown stays in the ledger as the auditable source.
7. **Record.** Update the front matter — `status: sent`, `sent_to`, `sent_at` — and nothing more.

If `require_approval: false` in `config.md`, the owner has pre-authorized the send on the configured schedule; still render the PDF from a reviewed report and record what was sent.

## What the agent writes, what the script adds

| | Written by the agent (Markdown, reviewed by the owner) | Added by `report_pdf.py` (computed from the ledger) |
|---|---|---|
| Header | — | the period's dates as title; the session it is for; check-in coverage ("6 of 7 days · none on Wed"); moments recorded; confidential, for the therapist |
| 1. How the week went | 3–6 warm lines | — |
| 2. For the session | 2–4 topics | the open checkboxes; the *suggested by sintr* label |
| 3. Mood, energy and sleep | 2–4 lines reading the numbers; the day's check-in notes, verbatim | averages with their number of days and the week before; the sentiment chart (last 4 weeks, smoothed, dotted across days without a check-in); the day-by-day grid |
| 4. Moments that stood out | one line on how they were chosen; 3–5 moments | the date and time from the linked entry when `when` is empty; the person's strongest-thought mark |
| 5. What repeated · 6. What helped | dated lists | — |
| Foot of page 1 | — | how it was prepared and reviewed; not a diagnosis, not a clinical assessment; what the highlights mean; not a crisis channel |

The PDF prints only words that are in the reviewed Markdown — the one exception is the opt-in appendix (below), which the owner sees in the preview. Dates and numbers are computed from the ledger and never typed.

Page 1 is a letter (the summary, the agenda, how to read it); page 2 the numbers; then the moments, what repeated and what helped. About four pages, five minutes of reading.

## The file

```md
---
session: 2026-10-19T18:00                     # the session it is for (week: YYYY-Www for a calendar week)
range: 2026-10-12 17:00 → 2026-10-19 17:00    # as the collector prints it
status: draft            # draft → reviewed → sent
generated_at: 2026-10-19T20:05:00Z
sent_to:                 # filled when sent
sent_at:                 # filled when sent
---

# Relatório para a sessão de 19/10 — Demo Person

## Como foi a semana <!-- week -->
## Para conversar na sessão <!-- session -->
## Humor, energia e sono <!-- mood -->
## Momentos que marcaram <!-- moments -->
## O que se repetiu <!-- patterns -->
## O que ajudou <!-- helped -->
```

Headings are written in the owner's language; the comment after each one (`week`, `session`, `mood`, `moments`, `patterns`, `helped`) tells the PDF which section is which and is invisible when the Markdown is rendered. Other HTML comments are notes for the agent and are not printed. Optional front matter: `appendix: true` (see below). Full example (fictional, Portuguese): `docs/example-report.md`, printed as `docs/example-report.pdf`.

## The six sections

### 1. How the week went — `week`
3–6 lines, plain and warm, like a short note to someone who knows the person. The tone of the week, its turning points, and how it ended. Name the hard moments **and the best one** — people remember their weeks worse than they recorded them. Use weekday names ("on Tuesday"); no numbers, no jargon, no causes, no adjectives the person did not use for themselves.

> Foi uma semana puxada no trabalho. Os dois momentos mais difíceis vieram cedo: o planejamento de terça, quando chegaram três demandas de uma vez, e a conversa de feedback de quinta. […] Na sexta veio o melhor momento: uma caminhada sem celular no almoço, a primeira em semanas.

### 2. For the session — `session`
2–4 topics, printed on page 1 as an open checklist the therapist can tick. **The person's own topics first**, in their words — from `therapy/current.md` ("Things I want to bring up") or what they said during review. Then, if the person kept them, topics the agent proposes (a recurring theme, a link to the last session's homework); end each of those with `(sugestão do sintr)` / `(suggested by sintr)` and the PDF labels it. Topics, not instructions to the therapist. No topics → say so ("Nada específico esta semana.").

```md
- O feedback do gestor.
- A pausa no meio do dia, tarefa da última sessão: aconteceu na sexta. Como mantê-la nas semanas de pressão? (sugestão do sintr)
```

### 3. Mood, energy and sleep — `mood`
2–4 lines that **read** the numbers; the script prints the numbers themselves. Say where the week went up and down, which nights were short, and which days have no check-in. Never estimate a missing day, never claim one measure caused another.

Then, optionally, the check-in notes worth keeping, **verbatim**, one per line, starting with the day — the diary card's daily notes. The PDF sets them under the grid as "In the day's own words":

```md
- ter 13/10 — "acordei cansado"
- qui 15/10 — "fui dormir 1h terminando a entrega"
```

### 4. Moments that stood out — `moments`
Open with one line saying how the moments were chosen ("Quatro dos cinco momentos registrados: os dois mais intensos, o melhor da semana e o domingo à tarde, que se repetiu."). Then 3–5 moments, chosen by weight — intensity, what the person flagged, links to the therapy themes — and **including a good moment** when there was one. Each is an H3 with the entry ID it comes from, then fields — keys in English, values in the owner's language:

```md
### Feedback sobre o ritmo de entrega <!-- entry-2026-10-15-001 -->
- when: quinta, 15 de outubro, à tarde
- tags: trabalho
- happened: Conversa individual com o gestor sobre o ritmo das entregas do mês.
- context: Tinha ido dormir à 1h terminando a entrega (5h30 de sono).
- thoughts: "ele acha que eu sou lento" ; "eu sempre decepciono"
- felt: ansiedade 70 ; vergonha 55
- body: rosto quente, estômago embrulhado
- did: Pediu desculpas várias vezes durante a conversa e ficou calado o resto da tarde.
- evidence_for: Atrasou a entrega de setembro.
- evidence_against: O gestor disse que a qualidade está boa e pediu só mais previsibilidade.
- alternative: "ele pediu previsibilidade, não disse que eu decepciono" (believability: 55)
- felt_after: ansiedade 45 ; vergonha 30
```

| Key | In the PDF (pt / en) | Content |
|---|---|---|
| `when` | card head | Day and part of the day. Empty → the entry's date and time. |
| `tags` | card head | Life area(s), from the entry. |
| `felt` | chips under the title | `emotion intensity ; …` exactly as recorded (0–100), the person's emotion words. Leads the card, for scanning. |
| `happened` | O que aconteceu / What happened | One or two sentences, faithful to the entry's `situation`; third parties by first name or role. |
| `context` | Contexto / Context | Optional: sleep, workload, health — only what the entry records. |
| `thoughts` | O que passou pela cabeça / What went through their mind | The entry's thoughts, **verbatim, in quotes**, separated by ` ; `. Never paraphrased, completed, or translated. The PDF marks the strongest one only if the person marked it (`hot_thought`). |
| `body` | No corpo / In the body | Optional: sensations, if recorded. |
| `did` | O que fez / What they did | What the person did next ("nothing" is valid). |
| `evidence_for` · `evidence_against` | O que sustentava o pensamento · O que não sustentava | Only if the entry has Tier 2. |
| `alternative` | Outro jeito de ver / Another way to see it | Only with Tier 2: the person's own alternative thought, quoted, with `(believability: N)`. |
| `felt_after` | Depois / Afterwards | Only with Tier 2: the re-rated emotions; the PDF shows `70 → 45`. |

Never fill a field the entry does not have. If `happened`, `thoughts`, `felt` or `did` is missing, leave it out and the PDF prints "não registrado / not recorded".

### 5. What repeated — `patterns`
Observations, each **starting with its dates**, then ` — `, then the observation; the PDF sets the dates in their own column.

```md
- 11 e 18/10 — No fim da tarde de domingo, ansiedade e o mesmo pensamento: "amanhã começa tudo de novo".
```

Two or more dated occurrences make a pattern; one does not. Describe what co-occurred, never why: no causal verbs, no labels ("avoidance", "catastrophizing", "burnout"), no "a pattern of…". Do not compute relations between measures ("sleep predicts mood") — the grid shows both numbers on the same days. Earlier weeks may be cited when the ledger shows them.

### 6. What helped — `helped`
What made things lighter, **as the person recorded it**: a walk, a conversation, sleep, a skill from therapy, an alternative thought. Quote their words; when the help was working a thought, give the re-rate numbers. Say "helped" only where the person said so or the numbers moved — never call something "effective". Mark homework from the last session when it applies. If nothing helped this week, say so plainly.

## The appendix (opt-in)

`appendix: true` in the front matter adds "Todos os registros da semana / Every entry this week" after the report: every shareable entry of the week, in full, in the card format. Off by default — the report is a summary; offer the appendix when the therapist asked for more detail. The owner sees it in the preview before anything is sent.

## What the script forgives, and what it reports

The PDF must look right whoever wrote the Markdown, so `report_pdf.py` reads it leniently and says what it changed (`warning: normalized: …`):

- sections are recognized by their marker or their heading (H1 or H2), merged if repeated, and put back in the template's order; text before the first heading opens the summary; an empty heading is not printed;
- moment fields are read under common other names (`situation`, `emotions`, `behavior`, `Situação`, `Pensamentos`…), in any case, bold or not; emotions written `ansiedade 85, vergonha 55`, `85/100` or `85%` are read as `ansiedade 85 ; vergonha 55`;
- a fenced report, tables, images, links, block quotes, inline code, emoji and template placeholders (`{…}`, the template's own moment) are taken out, never printed half-rendered; long words break inside the page;
- `status: revisado / aprovado / enviado` is read as `reviewed` / `sent`; any other unknown status is treated as a draft;
- a summary and agenda too long for page 1 no longer squeeze the letter layout: page 1 flows like the rest.

What it cannot fix it reports, and the agent fixes before showing the preview: quotes not found in the ledger, intensities that differ from the entry, thoughts without quotes, observations without dates, words that state a cause ("porque", "causou", "because"…) or a clinical label ("burnout", "depressão", "catastrofização"…), more than 6 topics or moments, a summary over ~140 words. `--strict` turns any warning into exit code 5.

## Style rules

- **Language:** the owner's (`config.md` → `language`), their register, their vocabulary. No clinical jargon unless the owner uses it.
- **Voice:** about the person, warm and plain; their actions in the third person or impersonal ("aceitou as três na hora"), their words in first person inside quotes.
- **Quotes are testimony.** Double quotes are reserved for the person's exact words, copied from the ledger (entries, check-in notes, therapy notes). The PDF highlights them in peach and checks every one against the ledger; a quote it cannot find is a `warning:` to fix before sending. Never put the agent's words in quotes.
- **Numbers are not typed.** Check-in figures, averages and the grid come from the script. Emotion intensities in moments are copied, not rounded or re-estimated; the script compares them with the entry.
- **Every claim dated.** Observations labeled as observations. **No diagnosis, no advice to the therapist, no speculation about causes.**
- **Short beats complete.** 3–5 moments, not all of them; a few observations, not every co-occurrence.
- **Third parties:** first names or roles; no clinical labels about other people.
- **Quiet week:** a short honest report ("semana quieta: 4 check-ins, nenhum registro; nada novo para trazer") rather than padding. The PDF handles a week without check-ins.
- **Entries marked `share: no`** are never quoted, summarized, counted, or printed; the script warns if a quote comes from one.
- **Safety content.** If the week's entries mention self-harm or suicide, do not leave it out or soften it: it goes first among the moments, verbatim and dated. The weekly report is not a crisis channel — the crisis protocol (`privacy-and-safety.md`) applies at the moment of capture, and the PDF says it is not monitored in real time.

## Review checklist (for the owner)

- Nothing here surprises me.
- Nothing here is something I don't want my therapist to know.
- The facts are right, and the quotes are mine.
- The topics for the session are the ones I want, in the order I want.

## What NOT to include

- Content from entries marked not shareable (`share: no`).
- Clinical speculation or labels of any kind.
- Raw tables of check-ins (the PDF has the grid) or every entry of the week outside the opt-in appendix.
- Details of third parties beyond what the story needs.
- Anything the owner asked to remove during review.
