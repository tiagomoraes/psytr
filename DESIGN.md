---
name: sintr website
description: The visual system of the public sintr site (sintr.tiagomoraes.cloud). A white consulting-room wall that window light crosses as the week between sessions goes by.
colors:
  ink: "#16171a"
  ink-pressed: "#000000"
  ink-confirm: "#23302a"
  verbatim-peach: "#fbe0cd"
  light-morning-sky: "#d4e6f4"
  light-morning-linen: "#f1e8df"
  light-morning-peach: "#f8dcc8"
  leaf-shadow-sage: "#a9b9a3"
  paper: "#ffffff"
  ink-2: "#474a51"
  ink-3: "#6b6e75"
  ink-soft: "#82858c"
  rule: "#e8e6e1"
  rule-strong: "#d4d2cc"
  wash: "#f5f4f1"
typography:
  display:
    fontFamily: "Source Serif 4, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "clamp(2.75rem, 1.35rem + 4.7vw, 5.75rem)"
    fontWeight: 300
    lineHeight: 1.02
    letterSpacing: "-0.028em"
  headline-statement:
    fontFamily: "Source Serif 4, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "clamp(2.25rem, 1.2rem + 3.6vw, 4.5rem)"
    fontWeight: 300
    lineHeight: 1.06
    letterSpacing: "-0.024em"
  headline:
    fontFamily: "Source Serif 4, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "clamp(2.125rem, 1.3rem + 2.7vw, 3.75rem)"
    fontWeight: 300
    lineHeight: 1.06
    letterSpacing: "-0.022em"
  title:
    fontFamily: "Source Serif 4, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "clamp(1.875rem, 1.2rem + 2.1vw, 3.125rem)"
    fontWeight: 300
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  title-small:
    fontFamily: "Source Serif 4, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "1.375rem"
    fontWeight: 400
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  lede:
    fontFamily: "Hanken Grotesk, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.125rem, 1rem + 0.4vw, 1.3125rem)"
    fontWeight: 400
    lineHeight: 1.55
  body:
    fontFamily: "Hanken Grotesk, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.65
  document:
    fontFamily: "Source Serif 4, Iowan Old Style, Charter, Georgia, serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.62
  label:
    fontFamily: "Hanken Grotesk, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "0.005em"
  file-body:
    fontFamily: "Fragment Mono, ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.8
  file-path:
    fontFamily: "Fragment Mono, ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  pill: "999px"
  bubble: "20px"
  panel: "18px"
  file: "14px"
  command: "12px"
  paper: "6px"
  inline: "6px"
spacing:
  gutter: "clamp(20px, 5vw, 72px)"
  section: "clamp(104px, 13vw, 208px)"
  column-gap: "24px"
  container: "1360px"
components:
  button-ink:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 26px 0 22px"
    height: "52px"
  button-ink-hover:
    backgroundColor: "{colors.ink-pressed}"
  button-ink-confirmed:
    backgroundColor: "{colors.ink-confirm}"
  button-ink-small:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "0 18px"
    height: "40px"
  button-copy-icon:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    size: "36px"
  file-card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.file-body}"
    rounded: "{rounded.file}"
    padding: "16px 18px 18px"
  file-card-path:
    textColor: "{colors.ink-3}"
    typography: "{typography.file-path}"
    padding: "12px 18px 11px"
  paper-document:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.document}"
    rounded: "{rounded.paper}"
    padding: "clamp(24px, 4vw, 56px) clamp(22px, 4.4vw, 64px) clamp(28px, 4vw, 52px)"
  chat-bubble-you:
    backgroundColor: "{colors.wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.bubble}"
    padding: "13px 18px"
  chat-bubble-agent:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.bubble}"
    padding: "13px 18px"
  segmented-toggle:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "4px"
  segmented-option:
    textColor: "{colors.ink-2}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  segmented-option-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  tab:
    textColor: "{colors.ink-3}"
    padding: "10px 0 14px"
  tab-selected:
    textColor: "{colors.ink}"
  command-block:
    backgroundColor: "{colors.wash}"
    textColor: "{colors.ink}"
    typography: "{typography.file-body}"
    rounded: "{rounded.command}"
    padding: "18px 60px 18px 20px"
  inline-code:
    backgroundColor: "{colors.wash}"
    rounded: "{rounded.inline}"
    padding: "0.08em 0.38em"
  help-panel:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.panel}"
    padding: "24px 26px"
---

# Design System: sintr website

This file records the visual system of the public **sintr** website (`site/`). It covers the site only. The product's data model (ledger files, frontmatter fields, statuses) is a different document: see `docs/DESIGN.md`. Product truth lives in `PRODUCT.md`; the rationale and references for the site are in `site/DESIGN-NOTES.md`. Tokens are normative in the frontmatter above and are mirrored as custom properties in `site/styles.css` `:root`.

## Overview

**Creative North Star: "The Consulting-Room Wall"**

The page is the white wall of a quiet consulting room, and window light crosses it while the week between two sessions goes by. The ground is plaster white, everything structural is graphite ink and hairline, and the only color in the world is light: a tall, obliquely projected window of soft gradient with blurred sage leaf shadows, multiplied onto the page. As the reader moves through the week, the light changes time of day (morning, noon, dusk, early morning, evening, golden hour, night, late morning, dawn) and cross-fades rather than jumps.

Hierarchy is carried by type size and line breaks alone. A light, optically sized serif speaks at display size in two tones; a quiet grotesk does the reading; a mono appears only where a real file is being shown. The product is demonstrated, not illustrated: every artifact on the page is a real sintr file format, set as selectable text in a white paper card labelled by its path, resting in the light.

Density is low and the pace is slow. Sections are separated by large vertical rests and single hairlines, not by fills or boxes. Motion is opt-in and unhurried: the light moves over about three seconds, leaves sway on 13 and 17 second cycles, and content settles in with a short blur-to-sharp fade. With JavaScript off or reduced motion requested, the light rests at the top of the page and everything reads. The wellness-app default (pastel blob hero, phone mockup, feature-card trio) and the dev-tool default (dark terminal page) are both rejected.

**Key Characteristics:**
- White ground, graphite ink, black pill controls; light is the only color.
- Light serif display (weight 300) carrying hierarchy by size and two tones, never by labels.
- Real files as artifacts: white cards, hairline edge, path as caption, mono body.
- Hairline-ruled structure on a 12-column grid with generous section rests.
- A time-of-day light that moves with the reader, and that disappears into a static wash when motion is unwelcome.

## Colors

A near-monochrome paper-and-graphite palette; the only chroma is window light and a single peach highlighter for a person's own words.

### Primary
- **Graphite Ink** (`ink`): text, every primary button, the selected state of every control, focus rings, the gate markers in the flow diagrams, and the background of the brand glyph. Black is the action color; there is no colored CTA.
- **Pressed Black** (`ink-pressed`): the hover fill of ink buttons; a one-step deepening, not a new hue.
- **Confirmed Ink** (`ink-confirm`): the brief "Copied" state of a copy action, a green-tinted near-black that confirms without introducing a success color. The bordered icon variant confirms with a deep green glyph (#2f5a3f) on a pale sage edge (#b9cdb9).

### Secondary
- **Verbatim Peach** (`verbatim-peach`): the highlighter. It underlays a person's own quoted words (the `thoughts` line in an entry, "your own words." in the headline) as a low band from 10% to 36% of the line height in headings and 0% to 46% inside files, and it is the text-selection color. It marks testimony, never emphasis in general.

### Tertiary
- **Window Light** (`light-morning-sky`, `light-morning-linen`, `light-morning-peach`, `leaf-shadow-sage`): the three gradient stops of the projected window and the leaf-shadow fill, shown here at their morning (default) values. Each time of day swaps all four as registered `@property` colors so the light cross-fades over 2.8s. The palettes per time are recorded in `.impeccable/design.json` (`extensions.lightPalettes`); the hues stay within sky, linen, peach, lavender and sage at very high lightness, and night drops to a cool grey-blue at lower opacity.

### Neutral
- **Plaster White** (`paper`): the page ground and every card, paper and agent bubble. Cards are the same white as the wall; they separate by hairline and shadow, not by tone.
- **Ink Two** (`ink-2`): lede, prose, agent chat text, secondary links and nav. The reading gray.
- **Ink Three** (`ink-3`): tertiary text that still has to pass 4.5:1 on white: file paths and keys, meta lines, captions, field definitions, inactive tabs.
- **Soft Ink** (`ink-soft`): large text and marks only: the second tone of two-tone statements, step numerals, list dashes, flow arrowheads. Below 4.5:1, so never for small text.
- **Hairline** (`rule`): every card edge, section divider, row rule and tab baseline.
- **Strong Hairline** (`rule-strong`): flow edges, the stations spine, link underlines at rest, hover borders.
- **Wash** (`wash`): the one tinted surface: your own chat bubbles, command blocks, inline code, and option hover.

### Named Rules
**The Light Is the Only Color Rule.** Chroma lives in the window light and nowhere else. Gradients never fill text, buttons or cards; the light is a projection on the wall, multiplied onto whatever it falls across.

**The Morning Wash Exception.** Exactly one surface carries a faint light gradient as a fill: the install prompt card that asks the visitor to act (162deg, #e9f2f8 to #f3f2ee to #f9ebe1). One per page, and only on the single call to act.

**The Verbatim Rule.** Peach highlights a person's own words. If the words are not a quotation of the person, they do not get the highlighter.

## Typography

**Display Font:** Source Serif 4 (with Iowan Old Style, Charter, Georgia), self-hosted variable 200 to 600, roman and italic, optical sizing on
**Body Font:** Hanken Grotesk (with ui-sans-serif, system-ui), self-hosted variable 300 to 700
**Label/Mono Font:** Fragment Mono (with ui-monospace, SF Mono, Menlo), 400 only

**Character:** A calm, precise notebook serif at light weight carries every heading and the report itself, against a quiet grotesk that never competes. The mono is a material, not a mood: it means "this is the actual file".

### Hierarchy
- **Display** (300, clamp 2.75rem to 5.75rem, 1.02, -0.028em, balanced): the hero headline only.
- **Headline Statement** (300, clamp 2.25rem to 4.5rem, 1.06, -0.024em, max 15.5em): two-tone statements, each clause on its own line, the second in Soft Ink.
- **Headline** (300, clamp 2.125rem to 3.75rem, 1.06, -0.022em): section heads; an XL variant reaches 5rem.
- **Title** (300, clamp 1.875rem to 3.125rem, 1.1, -0.02em, max 13em): the day headings. The time of day opens the sentence as an italic Ink Three line inside the heading ("*Tuesday, 7:40 pm.* Something happened at work.").
- **Title Small** (400, 1.375rem, 1.25): sub-heads over the install routes and the lifecycle; also the definition terms in the privacy promises.
- **Lede** (400, clamp 1.125rem to 1.3125rem, 1.55, max 34em, Ink Two): the hero paragraph.
- **Body** (400, 1.0625rem, 1.65; 1rem under 720px): prose at max 36em in Ink Two; quiet prose steps to 1rem in Ink Three.
- **Document** (serif 400, 1.0625rem, 1.62): the body of the report paper; its section heads switch to the grotesk at 600, 0.9375rem.
- **Label** (500, 0.9375rem to 1rem, line-height 1): buttons, nav, tabs, segmented options. Sentence case, never uppercase.
- **File Body / File Path** (mono, 0.8125rem / 1.8 and 0.75rem / 1.4): contents and path captions of real files only.

### Named Rules
**The Size Is the Hierarchy Rule.** Rank is expressed by size, weight 300 serif, and line breaks. No eyebrows, kickers, uppercase labels or icon tiles introduce a heading; context belongs inside the heading sentence.

**The Mono Means File Rule.** Fragment Mono appears only for real file contents, paths, and shell commands. It never decorates a heading or signals "technical".

## Layout

A centered container (1360px max) with a fluid gutter (clamp 20px to 72px) holds a 12-column grid with a 24px column gap. Compositions are asymmetric splits on that grid: copy in columns 1 to 5 or 1 to 7, artifacts in 7 to 12 or 8 to 12, with alternate days flipped so the artifact leads. Day copy is sticky (top 12vh) beside its artifact on desktop; the report lifecycle column is sticky at 14vh. Section rests are large (clamp 104px to 208px); sections are divided by one full-width hairline. The hero fills the first viewport minus the 88px header and leaves the upper-right wall empty for the light.

Responsive behavior: at 1100px the hero copy widens to 8 columns and the horizontal flow diagram may wrap. At 900px every split collapses to a single column, sticky positioning is released, artifacts drop below their copy with a 44px to 64px rest, and the horizontal flow turns into a vertical spine with 44px-tall edges. At 720px body steps to 1rem, the header shrinks to 72px and keeps only the GitHub mark and the Install pill, the light becomes one fixed oversized pane (150vw) that no longer travels, multi-column lists stack, and chat bubbles widen to 92%. Below 380px button padding tightens. Parallax drift runs only above 900px.

### Named Rules
**The Held Wall Rule.** The first viewport keeps one wall region empty so the light has somewhere to land. Do not fill the upper right of the hero.

## Elevation & Depth

Hybrid and low. Surfaces are white on white and separate primarily by a 1px hairline; two soft, long, ink-tinted shadows lift the artifacts that rest in the light. Depth also comes from the light itself, which sits above the page in multiply blend so cards visibly take the light, and from slow parallax that lets artifacts drift a little slower than the words.

### Shadow Vocabulary
- **Card** (`box-shadow: 0 1px 2px rgba(22,23,26,.04), 0 18px 40px -22px rgba(22,23,26,.22)`): default file cards.
- **Lift** (`box-shadow: 0 2px 4px rgba(22,23,26,.05), 0 26px 50px -24px rgba(22,23,26,.28)`): the hero file and the report paper, the two artifacts the page asks you to read.
- **Ink Button** (`box-shadow: 0 1px 1px rgba(22,23,26,.2), 0 10px 26px -10px transparent`, hover `0 16px 30px -12px rgba(232,168,130,.55)`): a contact shadow at rest; on hover a warm glow rises under the pill as it lifts 1px.
- **Paper Ring** (`box-shadow: 0 0 0 4px` or `5px` in paper white): knocks gate dots out of the line they sit on.

### Named Rules
**The Hairline First Rule.** A new surface gets a 1px hairline before it gets a shadow. Shadows are reserved for real artifacts resting in the light; the file listing in the privacy section deliberately drops its shadow.

## Shapes

Soft rectangles and full pills. Controls are pills (999px) without exception: buttons, copy buttons, the segmented toggle and its options, the skip link. Containers soften by role: chat bubbles 20px with one 6px tail corner on the speaker's side, the install card 20px, the help panel 18px, file cards 14px, command blocks 12px, inline code and focus rings 6px. The report paper is nearly square (6px, 4px on mobile) because it is a sheet of paper, not a card. Lines are 1px throughout; markers are 7px to 13px circles and 7px chevrons built from borders. The one recurring silhouette is the skewed window grid, in the light and in the brand glyph.

## Components

### Buttons
Black, quiet, confident; the only filled controls on the page.
- **Shape:** full pill (999px).
- **Primary (ink):** Graphite Ink fill, white label at 500, 52px tall, padding 0 26px 0 22px, optional 18px line icon leading with a 10px gap. The small variant is 40px tall with 18px padding, used in the header.
- **Hover / Focus:** fill deepens to Pressed Black, the pill lifts 1px, and a warm glow rises beneath it (transform 0.6s, shadow 0.8s, both on the expo-out ease); active returns to rest. Focus is a 2px ink outline offset 3px.
- **Copy:** an ink pill (40px, 0.9375rem) that appears only when JavaScript runs; on success it turns Confirmed Ink and its label reads the confirmation for 2.6s. The icon variant is a 36px white circle with a hairline edge and Ink Two glyph, pinned top-right inside command blocks; hover darkens glyph and edge only.
- **Text link:** ink text with a 1px Strong Hairline underline offset 0.28em that darkens to ink on hover.

### Segmented Toggle
- **Style:** a hairline-bordered white pill with 4px inset holding pill options (8px 16px, 500, Ink Two) and an optional leading label in Ink Three that hides under 720px.
- **State:** hover fills the option with Wash; the selected option is an ink pill with white text. Built on native radio inputs so it works without JavaScript and with arrow keys; focus draws a 2px ink outline on the visible option.

### Tabs
- **Style:** text labels at 500 in Ink Three on a single hairline baseline, 26px apart, no boxes.
- **State:** hover and selected turn the label ink; the selected tab grows a 2px ink underline from the left (scaleX, 0.6s). Panels fade up 6px over 0.7s. Native radios, no JavaScript required.

### Cards / Containers
- **File card (signature):** white, 1px hairline, 14px radius, Card shadow, clipped. A caption bar carries the real path in mono Ink Three (with an optional plain-sans note on the right) above a hairline; the body is mono at 0.8125rem / 1.8 with keys in Ink Three, numbers tabular, and quoted thoughts under the peach highlighter.
- **Report paper (signature):** a sheet, not a card: 6px radius, Lift shadow, generous fluid padding, serif body, mono path and frontmatter at the top, grotesk section heads, short dash list markers in Soft Ink, and an italic foot over a hairline.
- **Install card:** the one tinted container, 20px radius, the morning wash gradient, no border, no shadow.
- **Help panel:** hairline outline only, 18px radius, 24px 26px padding.
- **Command block:** Wash fill, hairline, 12px radius, mono at 0.8438rem / 1.85, room on the right for the copy icon; shell prompts are Ink Three and unselectable.

### Chat Bubbles
- **You:** Wash fill, ink text, aligned right, 20px radius with a 6px bottom-right tail.
- **Agent:** white with a hairline, Ink Two text, aligned left, 6px bottom-left tail.
- Max width 82% (92% under 720px), 13px 18px padding, 0.9688rem / 1.5, 12px between messages.

### Navigation
- **Style:** an 88px bar (72px under 720px) with the serif wordmark and window glyph on the left; text links at 500 in Ink Two turn ink on hover; the small ink Install pill closes the row. Under 720px only the GitHub mark (22px) and the pill remain.

### Lists and Diagrams
- **Definition rows:** serif terms against Ink Three definitions on a fixed term column, separated by hairlines; the privacy list opens on a full ink rule.
- **Flow and stations:** states named in serif, edges as 1px Strong Hairline lines with border-built arrowheads; the one irreversible gate is marked in ink with a filled dot knocked out by a paper ring.
- **Numbered steps:** large light-serif numerals in Soft Ink above (or beside, on mobile) a 500 step title.

### Motion
- **Easing:** expo-out `cubic-bezier(.16, 1, .3, 1)` for interface and reveals; a slow in-out `cubic-bezier(.45, .05, .2, 1)` for the light.
- **Reveal:** fade up 16px from blur 5px over 1.3s to 1.4s, siblings staggered by 0.09s (capped at six).
- **Writing entry:** file lines appear one by one (150ms apart after 200ms), then the highlighter sweeps in.
- **Light:** recolors over 2.8s and moves over 3.4s when the section's time of day changes; breathes on an 11s cycle; leaves sway on 13s and 17s.
- All motion is opt-in behind `html.motion`; reduced motion removes animation and transition entirely.

## Do's and Don'ts

### Do:
- **Do** keep every filled control Graphite Ink on white, as a full pill; selected states are ink too.
- **Do** show real file formats as selectable text in a white, hairline-edged card captioned with the file's path.
- **Do** carry hierarchy with light serif size steps and line breaks, putting context (like the time of day) inside the heading sentence.
- **Do** keep small text at Ink Three (#6b6e75) or darker; reserve Soft Ink for large type and marks.
- **Do** separate sections with large rests and a single hairline rather than fills.
- **Do** make motion opt-in and keep every interaction (toggles, tabs) working with JavaScript off.
- **Do** self-host every font and asset; the site loads nothing from third parties.

### Don't:
- **Don't** fill text, buttons or cards with gradient; chroma belongs to the window light (including the small window in the brand glyph), plus the single morning-wash install card.
- **Don't** add eyebrows, kickers, uppercase labels, or icon tiles above headings.
- **Don't** use the mono face outside real file contents, paths and commands.
- **Don't** use the peach highlighter on anything but a person's own quoted words.
- **Don't** build the page from pastel blobs, a phone mockup, or a row of three feature cards, and don't turn it into a dark terminal page.
- **Don't** use glassmorphism or backdrop blur on surfaces; blur belongs only to the light's soft edges, the leaf shadows, and the reveal transition. No purple-to-blue pairs; lavender appears only as evening light mixed with peach.
