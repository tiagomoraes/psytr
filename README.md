# sintr

**sintr is an agent pack for keeping a private psychological self-tracking ledger on the filesystem.**

It gives AI agents a portable skill, a Markdown-based psychological ledger, templates, and documentation so tools like Hermes, Claude Code, OpenCode, OpenClaw, Claude Cowork, and other personal assistants can help you document how you feel, structure difficult situations the way cognitive-behavioral therapy taught us (thought records), keep therapy context, and produce a weekly report you can hand to your therapist — without running a database, an app, or a service.

## What sintr is

sintr is not a backend. It is a small operating manual for LLM agents:

- a **skill** that teaches an agent to conduct a supportive capture conversation, structure entries with a sound CBT-based schema, log check-ins, keep therapy context, and draft weekly reports;
- a **filesystem layout** of Markdown files that both you and your agent can read and edit;
- **templates** for a fresh personal ledger;
- a **weekly-report pipeline**: a deterministic collector produces a data digest, the agent writes the report, you review it, and it is sent to your therapist through your messaging gateway — only with your approval;
- **language-adaptive**: the pack is written in English as its base; in use, the conversation, entries, and reports follow the owner's own language and words;
- **installer snippets** for common agent environments.

The core idea: the agent is the interface, and plain Markdown files are the product.

```text
You ──chat/voice──> Agent ──read/write──> ~/sintr/*.md ──weekly──> report ──approve──> therapist
```

## What sintr is not

- Not therapy, not a diagnosis, not a crisis service. It is a documentation tool for work done in professional care.
- Not a replacement for your therapist — it feeds sessions better context.
- Not a cloud service: your data lives on your machine, in files you own.

## Ledger layout

```text
sintr/
  README.md
  config.md
  checkins/YYYY-MM.md            # daily mood/energy/sleep check-ins
  entries/YYYY-MM.md             # structured situation entries (CBT thought records)
  therapy/current.md             # goals, themes, tasks from therapy
  therapy/sessions/YYYY-MM.md    # post-session notes
  insights/current.md            # distilled observations (not diagnoses)
  reports/YYYY-Www.md            # weekly reports + status
```

## Repository layout

```text
sintr/
  SKILL.md                  # Portable skill pack for agents
  templates/sintr/         # Starter ledger files
  installers/               # Agent-specific install helper
  docs/                     # Documentation (install, design)
  references/               # Deep dives: entry framework, report guide, privacy & safety
  scripts/                  # week_collect.py (report digest) + tests
  .claude-plugin/           # Claude Code plugin/marketplace manifest
```

## Quick start (Hermes)

```bash
git clone https://github.com/tiagomoraes/sintr.git
cd sintr
make install-hermes          # installs the skill + creates ~/sintr from templates
```

Then talk to your agent:

> Preciso falar de uma situação que me deixou mal hoje: ...

> Humor 4/5, dormi 7h. (check-in)

> Gera meu report semanal pra levar na terapia.

## Weekly report

The report closes the loop between your week and your session:

1. `scripts/week_collect.py` reads the week's entries and check-ins and produces a digest;
2. the agent writes a human-readable report into `reports/YYYY-Www.md`;
3. you review and edit;
4. with your approval it goes out through your gateway (WhatsApp, Telegram, email…) to your therapist.

Approval-before-send is the default. Nothing leaves your ledger without you saying so.

See [`docs/example-report.md`](docs/example-report.md) for a full (fictional) example of the output.

## Privacy

Your ledger is sensitive. Keep it local, keep it private, and read `references/privacy-and-safety.md` before wiring any sharing workflow. sintr never shares content with anyone without your explicit approval.

## License

MIT — see [LICENSE](LICENSE).
