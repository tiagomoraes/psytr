# sintr.tiagomoraes.cloud: design notes

How the public site was designed, which references shaped it, and the rules that keep it
consistent. Product truth lives in `PRODUCT.md` and `docs/DESIGN.md`; this file covers only
the website.

## The idea

**The page is the white wall of a quiet consulting room, and window light crosses it while
the week between two sessions goes by.**

- The ground is white, as the brief asks. The only color on the page is **light**: a tall
  two-by-three window projected at an angle onto the wall, with leaf shadows moving across it.
  That is where the sky, sage, lavender and peach gradients live. They never fill buttons,
  text or cards.
- Scrolling follows one fictional week: Tuesday 7:40 pm (a capture), Thursday 8:50 am (a
  check-in), Sunday 8 pm (the report), Monday 6 pm (the session), then night for the privacy
  section. The light changes with each time of day: morning sky, dusk peach, evening lavender,
  golden hour, and a dim, cool moonlight at night.
- Every artifact shown is a **real sintr file format** (entry, check-in, report, therapy,
  insights), as selectable text labeled with its path. The page demonstrates the product
  instead of describing it.

The category usually ships one of two pages: a wellness app (pastel blobs, a phone mockup, a
row of three feature cards) or a developer tool (a dark terminal page). This site avoids both.

## References

Researched on Awwwards before any design work. The site borrows ideas from these, not their
looks.

| # | Reference | Recognition | What sintr took from it |
|---|---|---|---|
| 1 | **Daylight**, [daylightcomputer.com](https://daylightcomputer.com/) ([Awwwards](https://www.awwwards.com/sites/daylight)) | Site of the Day, Jun 18 2024 (basement studio) | Calm technology told through **dappled sunlight and leaf shadow**. The product rests in real light instead of floating on a gradient. This became the window light and leaf shadows that fall across the ledger files. Not taken: orange commerce CTAs, video, pop-overs. |
| 2 | **Poor Charlie's Almanack**, Stripe Press, [stripe.press/poor-charlies-almanack](https://www.stripe.press/poor-charlies-almanack) ([Awwwards](https://www.awwwards.com/sites/poor-charlies-almanack)) | Site of the Day, Jan 4 2024 | **Typography alone carries the hierarchy**: a light, high-contrast serif at display size, two tones, no icons, and reading treated as the experience. Hence the two-tone statements ("Your therapist sees fifty minutes of your week. / The other 10,030 happen without them."), no icon tiles anywhere, and the weekly report set as a real document in a text serif. |
| 3 | **Twofold Therapy**, [twofoldny.com](https://twofoldny.com/) ([Awwwards](https://www.awwwards.com/sites/twofold-therapy)) | Honorable Mention, Aug 2 2026 | Restraint for a **therapy** subject: warm neutrals, slow parallax, and the room and the chair as the subject. The consulting room became this site's governing idea. Not taken: photography, double exposure, the all-caps grotesk. |
| 4 | **Q Psychology**, [qpsychology.com.au](https://qpsychology.com.au/) ([Awwwards](https://www.awwwards.com/sites/q-psychology)) | Honorable Mention, Jan 23 2025 | A **very large light serif headline** reads as calm authority in mental-health care, and sage/green can carry trust without clinical blue. Sage appears here only in the leaf shadows. Not taken: the dark green ground and the full-bleed office photo. |
| 5 | **Sleep Well Creative**, [sleep-well-creatives.com](https://sleep-well-creatives.com/) ([Awwwards](https://www.awwwards.com/sites/sleep-well-creative)) | Site of the Day, Jan 28 2026 (8.03/10) | A single page told as **one arc of time** (a night), with illustration instead of stock imagery. Here the arc is one week, and the light marks the time of day. Not taken: the "Enter site" gate and the WebGL dependency. sintr's content has to render with JavaScript off. |
| 6 | **This Is Sleep**, [thisissleep.co.uk](https://thisissleep.co.uk/pages/your-sleep-solution) ([Awwwards](https://www.awwwards.com/sites/this-is-sleep)) | Site of the Day, Mar 23 2019 | Reviewed through its Awwwards listing. It keeps a strict **black, white and one calm accent** palette with type-led fullscreen sections. It is also a warning: the jury scored its accessibility **4.80/10**. sintr treats WCAG AA, no-JS rendering and reduced motion as requirements. |

Also considered and dropped: Haptic (HM 2020, a minimal journaling app; the site is now
offline), Yin Mindfulness Immersion (HM 2020; the domain no longer resolves), and Roveia Health
(nominee 2026; a clinical-white SaaS page with blue gradients, which is the generic look
`PRODUCT.md` warns against).

## Reconciling the brief with PRODUCT.md

The brief asks for soft gradients. `PRODUCT.md` lists "gradients, glassmorphism, purple-blue"
among its anti-references. The two are reconciled this way:

- A gradient appears only where something physical would make one: **light through a
  window**. It is never a UI fill, never on text, and never a decorative halo.
- No glass, no blur used as decoration, and no purple-to-blue pairs. Lavender appears only as
  evening light, mixed with peach.
- The one exception is the install prompt card, which carries a faint morning wash (a linear
  gradient from sky to peach). It marks the single place that asks the visitor to act.

## System

**Type** (self-hosted, SIL OFL; see `fonts/OFL.txt`)
- Display: *Source Serif 4*, weight 300, optical sizing on. Precise and calm at 92px, which suits a notebook a professional would recognize.
- Body: *Hanken Grotesk*, weight 400/500. A quiet grotesk.
- Files: *Fragment Mono*, used **only** for real file contents and paths, never to signal "technical".
- Hierarchy comes from size and line breaks. No eyebrows or kickers. Times of day are part of the heading sentence ("*Tuesday, 7:40 pm.* Something happened at work.").

**Color**
- Paper `#ffffff`, ink `#16171a`, secondary `#474a51`, tertiary `#6b6e75` (≥ 4.5:1 on white), large-text gray `#82858c`.
- Hairlines `#e8e6e1`. Wash for chat and code blocks `#f5f4f1`.
- Buttons and the active state of every control are black. The verbatim highlighter (peach `#fbe0cd`) marks a person's own words: quoted thoughts in the files, and "your own words" in the headline.
- Light palettes per time of day live in `styles.css` (`html[data-time=…]`). They are registered `@property` colors, so the light cross-fades instead of jumping.

**Motion**
- One authored moment: the light. It is fixed to the viewport, multiplied onto the page, and moves and recolors over about 3s when the section's time of day changes. Leaves sway on 13s and 17s cycles, and the light breathes slowly.
- Reveals are short fade-ups (blur 5px to 0, expo-out). The capture entry writes itself line by line, then the quoted thought gets highlighted. Artifacts drift slightly slower than text on desktop.
- Content is visible by default. Motion is opt-in (`html.motion` is set only when JavaScript runs, `IntersectionObserver` exists, and `prefers-reduced-motion` is not `reduce`). With reduced motion or no JavaScript, the light stays static at the top of the page and everything is readable.

**Interaction without JavaScript**
- The report language toggle (PT original / EN) and the agent install tabs are native radio groups styled with CSS. They work with JavaScript off and with arrow keys.
- Copy buttons appear only when JavaScript runs. Without it, the hero CTA is a plain link to the visible prompt.

## Content sources

- Entry, check-in, therapy and insights formats come from `skills/sintr/SKILL.md` and `templates/sintr/`.
- The weekly report is abridged from `docs/example-report.md` (fictional demo data, Portuguese). The English version is a translation made for this page and is labeled as one.
- Install commands come only from `docs/INSTALL.md` and the `Makefile`. There is no `curl | bash`.
- The crisis lines come from `skills/sintr/references/privacy-and-safety.md`.
- One claim is new to this page and should be reviewed by the owner: the caveat that sintr adds no servers, but the agent's model provider still sees the conversation.

## Revision 2: two pages, two audiences

The owner approved the look but found the language too technical. The site is now split by
reader, with the same visual world on both pages:

- **`/` (home)** is for someone in therapy who isn't technical. It starts from the person and
  not the tool: the week fades before the session, and here is how you keep it. It shows what
  living with sintr feels like (talk to your assistant like a friend, one line a day is enough,
  a summary on Sunday, walk into Monday with the week), then privacy in plain words, then
  three steps to get started.
- **`/tech/` (Under the hood)** is for builders and the curious. It covers the model, the
  ledger, the raw entry and check-in formats, the real collector digest, the report front
  matter lifecycle, installation per agent, Make targets, privacy architecture, scheduling
  and the repository.

**Language rules on the home.** These words don't appear on the home: skill, agent pack,
ledger, Markdown, file-native, field keys, installer, repo, plugin marketplace, cron. Raw
code doesn't appear either. Technical evidence becomes something you can read as a person:

- The `entry-*.md` mock becomes a **notebook card**: ruled hairlines tinted like school paper,
  a peach margin rule, human labels (What happened · What went through your mind · How you
  felt · In your body · What you did) in the sans, and the person's words in the serif. The
  quoted thought keeps the peach highlighter. It still "writes itself" line by line.
- The check-in becomes three readable values (Mood 2 of 5 · Anxiety 4 of 5 · Sleep 5½ hours).
  The therapy file becomes homework with drawn checkboxes. The insights file becomes "Something
  that keeps coming up", written as an observation with dates.
- The `ls -l` permissions block becomes a "Your sintr folder" card that lists what it holds,
  with a small lock and "Only you can open it".
- The report keeps its PT/EN toggle and loses the YAML front matter (which moved to `/tech/`).
  A small "Draft, waiting for you" status sits above it.
- The setup message for the assistant is the only technical text left on the home. The card
  says plainly that it's a message for your assistant, not for you. The full text sits in a
  closed "Read the message before you copy it" disclosure, so it can be read before pasting
  without putting paths in the home's default reading. The copy buttons work whether the
  disclosure is open or closed.

**`/tech/` layout.** It is a reading page: a contents list that stays in view (with the current
section marked by script, as an enhancement only), a 9-column text column, specification
tables with a hairline above each, and the original file cards in Fragment Mono. The window
light stays in the header and fades out, so it never sits behind long reading. Nothing in the
visual system changed: same tokens, faces, buttons, hairlines and motion grammar.

**Accuracy.** The digest excerpt on `/tech/` is real output of `scripts/week_collect.py` run on
a fictional demo ledger. Only the scratch ledger path was replaced with `~/sintr`, and sections
in between are marked with an ellipsis. Install paths come from `installers/install.sh`, and
targets from the `Makefile`.

## Revision 3: a lean home, positioned as a mood diary

The owner liked the narrative but found the home long and repetitive. He also asked to
position sintr as a **mood diary**, which is a simpler way to understand it. The cut is
editorial, not visual: the world, the tokens and the motion are unchanged.

- **Each idea appears once.**
  - The hero says what sintr is: "a private mood diary you keep by talking to your AI
    assistant", and that the week is waiting on one page before each session.
  - The next section says why: therapy gets fifty minutes a week, and your week happens in the
    rest of it.
  - The two scenes show how it works. "Fresh", "one page" and "your own words" each appear
    exactly once.
  - Approval appears only in the report section; privacy no longer repeats it.
- **Two scenes instead of four.**
  - Tuesday is the conversation. The check-in is now a one-line exchange inside it.
  - Sunday is the report, still with its PT/EN toggle, now abridged: summary, two situations,
    one observation, two topics.
  - Monday is a single closing line with its own day stamp: "Monday, 6 pm. The hour starts
    with Tuesday, not with today."
- **One mock per idea.** The notebook card appears only in the hero, where it also writes
  itself on load. The capture scene shows the conversation, not the card again.
- **Cut:**
  - the flow diagram, which restated the narrative;
  - the "One week, kept" intro;
  - the session cards;
  - the folder card and three of the six privacy promises;
  - the second copy button and its lead;
  - the acted-out chat bubbles in steps 2 and 3, and the "then just talk to it" examples;
  - the gradient wash on the setup message (it now sits on the plain wash), so on the home the
    window light is the only color again.
- **Privacy** is three points in a row plus a one-sentence caveat that links to `/tech/`.
  **Getting started** keeps the three steps and the copyable message, now in a single "Read
  the setup message before you copy it" disclosure under the steps.
- **A shorter page gets a slightly tighter rhythm.** `--section` is `clamp(88px, 10vw, 148px)`
  on the home, compared with 104–208px before. `/tech/` keeps its own rhythm.
- **Measured** (reduced motion, so nothing animates during measurement):

  | | Before | After | Change |
  |---|---|---|---|
  | Words in `<main>` | 1,970 | 825 | −58% |
  | Page height at 1440 | 10,220 px (11.4 screens) | 6,448 px (7.2 screens) | −37% |
  | Page height at 390 | 15,529 px (18.4 screens) | 8,180 px (9.7 screens) | −47% |
  | Sections | 9 | 7 | |
  | Mock pieces (cards, bubbles, papers) | 21 | 9 | |

## After launch: cache and the support lines

- **Stale stylesheet.** The CDN caches `styles.css` and `main.js` for four hours
  (`max-age=14400`) but not the HTML. After a deploy, some visitors got the new page with the
  old stylesheet, which caused overlapping text and unstyled sections. The home now links
  `styles.css?v=dev` and `main.js?v=dev`. `make site-deploy` stamps each file's content hash
  into those URLs in the published copy, so a changed file always gets a new URL. `/tech/`
  still links them without a version; it can opt in by adding `?v=dev` the same way.
- **Support lines, not a card.** The crisis box was a bordered panel with label and value pairs
  ("CVV 188"), which read like credit card fields. It is now a ruled list of phone lines. Each
  line has the country, the service's full name (CVV, Centro de Valorização da Vida; 988
  crisis line; Samaritans; SNS 24), how it works ("Free, 24 hours"), and an outlined call
  button with a phone icon. The note about calling the local emergency number and about the
  assistant stopping to help sits under the list.

## Languages

The home exists in English (`/`), Brazilian Portuguese (`/pt-br/`), Spanish (`/es/`), French
(`/fr/`), German (`/de/`), Italian (`/it/`), Japanese (`/ja/`) and Simplified Chinese (`/zh/`).
`/tech/` stays in English.

- **Static pages, one per language.** They are generated, so every language renders without
  JS, has its own `<html lang>`, canonical URL, `hreflang` alternates and `og:locale`, and can be
  indexed.
- **Detection.** On a first visit to `/`, a small script in `<head>` reads
  `navigator.languages`. That is the same preference list the browser sends as
  `Accept-Language`. If the first supported entry isn't English, the script redirects before
  anything paints. Traditional Chinese isn't served Simplified. Server-side negotiation would
  need a CDN or server rule, which is infrastructure the site doesn't own.
- **Choice wins.** Picking a language in the menu (header) or the list (footer) is stored in
  `localStorage` (`sintr-lang`). `/?lang=en` also pins English. Pages under a language path never
  redirect.
- **The report** keeps the Portuguese original. Every other language offers the original next to
  a translation into that language. `/pt-br/` shows the original only.
- **Typography.** Latin text stays in the self-hosted faces. Japanese and Chinese fall back to the
  reader's system fonts (Hiragino, Yu, PingFang, Noto CJK), without tightened tracking or synthetic
  italics. Each language gets its own quotation marks around the person's words („…", « … », 「…」).

**How it's built** (`i18n/`):
- English is the source: elements in `site/index.html` carry `data-i18n="key"`, or
  `data-i18n-attr` for attributes.
- `python3 i18n/build.py` (`make site-i18n`) does three things:
  - extracts `i18n/en.json`;
  - validates each `i18n/<code>.json`: same keys, identical markup, kept tokens (commands,
    names, phone numbers), and stale entries;
  - writes `site/<lang>/index.html` and the generated regions (`hreflang` tags, detection, menus).
- Translations were made by Haiku subagents following `i18n/TRANSLATING.md`.
- **To change English copy:** edit `site/index.html` and run the build. It flags the translations
  that became stale. Retranslate those keys, run `--stamp <code>`, and build again.
- **To add a language:** add it to `i18n/locales.json` and write `i18n/<code>.json` following
  `TRANSLATING.md`.

## The report as a PDF

The weekly report became a short PDF (`scripts/report_pdf.py`, structure and sources in
`skills/sintr/references/report-framework.md`), so the Sunday scene follows it:

- **The paper** is abridged from the new example (`docs/example-report.md`, printed as
  `docs/example-report.pdf`) in the PDF's order: how the week went, for the session, two moments
  (the hardest and the best one) and one dated observation. Its title is the PDF's: the dates of
  the week, then "Demo Person's week, in their own words".
- **The copy** says what the person receives: a short PDF with how the week went, what to talk
  about, a chart of mood and sleep, and the moments in their own words. The lifecycle names the
  PDF: the draft is read as a PDF, and the same PDF is what is sent.
- **The source line** links the full four-page example PDF on GitHub.
- **`/tech/`** gains a Preview step (the draft PDF and the verbatim check) and a "What the
  therapist receives" list; the send step names the PDF; the print layout leaves the roadmap.
- **Languages.** The new strings were translated for every locale and stamped; the removed
  `report.doc_summary*`, `doc_situation*` and `doc_topic*` keys are gone from all files.

## The report an hour before the session

The weekly report is now prepared an hour before each session (`report_lead`) instead of on
Sunday evening, so it is fresh when the session starts. The Sunday scene became **Monday, 5 pm**
("The week comes together"), an hour before the Monday 6 pm payoff, and its light moved from
`evening` to the `golden` palette that was kept for this. The copy opens with "An hour before your
session". `/tech/` explains the period (the 7 days up to the report, consecutive reports meeting
exactly), `--schedule`, and the new file names (`reports/YYYY-MM-DD.md`, by session date).

## Privacy of the site itself

The page loads nothing from third parties: no analytics, no cookies, no font CDN. The fonts,
favicon and social image are served from the same origin. That should stay true for any
future edit.

## Files

```text
site/
  index.html        the home (English source): what it is and why, two scenes, the report, privacy, three steps
  <lang>/index.html the same home in pt-BR, es, fr, de, it, ja, zh (generated by i18n/build.py)
  tech/index.html   Under the hood: formats, pipeline, install, privacy architecture, repo
  styles.css        tokens, layout, light, motion
  main.js           copy, time-of-day observer, reveals, parallax, contents highlight (progressive enhancement)
  favicon.svg       the window glyph
  og.png            1200×630 social image, rendered from the live page in headless Chrome
  fonts/            self-hosted woff2 (Latin subset) + OFL.txt
  robots.txt
  DESIGN-NOTES.md   this file (excluded by `make site-deploy`)
```

Preview with `make preview-site` (http://127.0.0.1:8089). Publish with `make site-deploy`,
which copies `site/` to `/home/hermes/artifacts/sintr/`.
