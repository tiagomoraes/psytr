---
version: 1
slug: "site-tech-index-html"
primary_target: "site/tech/index.html"
related_targets: ["site/index.html"]
---

Scope: `site/tech/index.html`, served at /tech/ ("Under the hood"). Mode: Read. Sibling of the home page (`site/index.html`, Persuade), inside the same established world.

Audience: technical readers: developers, contributors, and people who want to understand before they install. Their question: how does sintr work inside, how do I install it on my agent, and what exactly happens to the data? Source material: SKILL.md, references/, docs/INSTALL.md, docs/DESIGN.md, installers/install.sh, the Makefile, and real output from scripts/week_collect.py on a fictional demo ledger. Wayfinding: a contents list that stays in view (stacked on mobile), with sections for the model, the ledger, entries and check-ins, the weekly pipeline, install, privacy architecture, scheduling, and the repository. Nav and footer link back to the home.

## Direction contract

THESIS: The same white consulting-room wall, now read in good light: a calm reading page where the raw files are the illustrations. It refuses the dark docs-site default and any developer-portal chrome.

OWN-WORLD: Identical tokens and faces to the home. The window light stays in the header and fades out, never sitting behind long text. The file cards set in Fragment Mono are the only illustrations. Specification tables are a serif term column beside a sans description, with a single ink hairline on top and pale hairlines between rows. The pipeline steps are numbered in light serif.

STORY: The reader gets the model in one paragraph and a flow line, then the ledger layout and its conventions, then exact entry and check-in formats with Tier 2, then the collector command, a real digest excerpt and the front matter before and after sending. After that: install per agent with copyable commands, the Make targets, the precise privacy boundary (including the model provider caveat), scheduling, and how to contribute.

FIRST VIEWPORT: The same nav (wordmark links home; Home, Privacy, GitHub, and a black Install pill). The serif headline "Under the hood." at about 5rem; a one-paragraph lede; a facts line (Backend: None · Storage: plain Markdown on your disk · Collector: Python, stdlib only · License: MIT); a link back to the home for newcomers; the contents list and the first section starting just below the fold.

FORM: The established world, extended to a long-document reading layout. No concept roll, because the world is settled and the owner's brief specifies the content. The signature is the contents list marking the current section, plus real artifacts throughout.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
