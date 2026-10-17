# Generic agent usage snippet

sintr works with any agent that can read and write files.

1. Create the ledger: copy `templates/sintr/` to a private folder (e.g. `~/sintr`), or run `./installers/install.sh generic`.
2. Teach the agent: add the skill's `SKILL.md` to the agent's instructions (system prompt, AGENTS.md, custom instructions), or install `skills/sintr/` where the agent discovers skills.
3. Fill `config.md` (language, timezone, therapist info, `require_approval`).

The contract is simple: read `config.md` and the relevant current files first; append events to the monthly logs at end-of-file; never share anything outside the ledger without explicit approval.
