# Translating the sintr home page

`i18n/en.json` holds every English string on the home page, keyed. A translation is
`i18n/<code>.json`:

```json
{ "locale": "pt-BR", "strings": { "hero.title": "…", "…": "…" } }
```

It must have exactly the same keys as `en.json`. After writing it, run
`python3 i18n/build.py --check <code>` and fix every `error:` line until it prints `ok`.

## What the page is

sintr is a private **mood diary** that a person keeps by talking to their AI assistant. It
records hard moments in their own words, and before each therapy session it puts the week on
one page, which goes to the therapist only if the person says yes. The reader is someone in
therapy who is **not technical**. The page's voice is calm, warm, short and plain: no hype,
no exclamation marks, no clinical jargon, nothing childish. It never claims to be therapy.

## Hard rules

1. **Markup stays identical.** Keep every HTML tag and attribute exactly as in English, in the
   same order: `<span class="hl">`, `<q class="said">`, `<span class="when">`, `<a class="link" href="…">`,
   `<b>`, `<mark>`, `<span class="line__how">`, `<span class="paper__dot" aria-hidden="true"></span>`
   and so on. Translate only the text between tags.
2. **Never translate these:** `sintr` (always lowercase), Claude Code, Claude Cowork, Hermes,
   OpenCode, OpenClaw, CVV, Centro de Valorização da Vida, Samaritans, SNS 24, phone numbers
   (188, 988, 116 123, 808 24 24 24), "Demo Person", "2026-W42".
3. **The setup message (`start.message`)** is read by the AI assistant. Translate its prose,
   but keep every technical token character for character: the URL, `docs/INSTALL.md`,
   `./installers/install.sh`, `hermes`, `claude-code`, `generic`, `~/sintr`, `~/sintr/config.md`,
   `require_approval: true`.
4. `&nbsp;` keeps short words together at line ends. Keep them where they still make sense in
   your language, drop them where they don't, and never add them in CJK text.
5. Quotation marks: write them the way your language does (« » in French, „ " in German,
   「」 in Japanese). Exception: inside `<q class="said">…</q>`, don't add quotes at all. The
   page draws them itself.
6. Keep each string about as long as the English. The page was cut to be short on purpose.
7. Dates and times follow your language's habits ("Tuesday, 7:40 pm" becomes "Terça, 19h40",
   "Dienstag, 19:40", "火曜日 19:40"…). Day names stay in the same order as the story:
   Tuesday, Thursday, Sunday, Monday.
8. The `report.doc_*` keys are a translated example of a weekly report. The person's original
   is in Portuguese. Translate the English version into your language as a natural, plain
   document. Keep the quoted thoughts inside `<mark>` faithful.
9. Output must be valid JSON in UTF-8. Escape `"` inside values as `\"`. Use real characters
   (é, ü, 日), not escapes.

## Voice and glossary

| | Address | mood diary | AI assistant | therapist | therapy session |
|---|---|---|---|---|---|
| pt-BR | você | diário de humor | assistente de IA | terapeuta | sessão de terapia |
| es | tú | diario de estado de ánimo | asistente de IA | terapeuta | sesión de terapia |
| fr | vous | journal d'humeur | assistant IA | thérapeute | séance de thérapie |
| de | du | Stimmungstagebuch | KI-Assistent | Therapeut:in (or neutral phrasing) | Therapiesitzung |
| it | tu | diario dell'umore | assistente IA | terapeuta | seduta di terapia |
| ja | です・ます (polite, gentle) | 気分日記 | AIアシスタント | セラピスト | セラピーのセッション |
| zh-Hans | 你 | 情绪日记 | AI 助手 | 心理治疗师 | 治疗会谈 |

Other terms:
- "your own words": the person's exact words, not paraphrased. It is the heart of the product.
- "check-in": a quick one-line note of mood and sleep. Use a natural word (pt-BR: registro rápido
  or check-in; es: registro rápido; de: kurzer Eintrag…).
- "Under the hood": the link to the technical page, which is in English. Use a natural phrase
  ("Por dentro", "Cómo funciona por dentro", "Sous le capot", "Unter der Haube", "Dietro le
  quinte", "技術的な仕組み", "技术细节").
- "Get started": a short, friendly button label.
- Crisis lines (`lines.*`): translate "Free, 24 hours", "Call or text, 24 hours" and "Health line
  with psychological support". "988 crisis line" becomes the natural phrase for "crisis line
  988". `lines.lN_call` is a screen-reader label ("Call CVV, 188").
