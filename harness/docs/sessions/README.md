# Sessions

The conversation record of this repository (`AGENTS.md` Part A, section 8). Nothing of record lives only in a vendor's home folder.

## Session log: `docs/sessions/session_<YYMMDDhhmm>.md`

Written by `harness-close` step 8, in full sentences, from this shape:

```
# Session <YYYY-MM-DD HH:MM> - <headline>

**Type:** <feature|bugfix|refactor|hotfix|maintenance>. **Branch:** <name>. **Work item:** <id or none>.

## Summary of actions
## Decisions, and where each was recorded
## Commands and tests run (command -> summary line)
## Gates (lint, prepush, ratchet: outcome)
## Next steps
```

## Raw transcripts: `docs/sessions/raw/<host>/<YYMMDDhhmm>-<file>`

Copied by `python scripts/save_transcript.py` from the Claude Code, Codex, Gemini CLI and Antigravity folders at `harness-close` step 9. Cursor has no file export; note it in the session log. Transcripts are committed as they are. `secrets-scan` runs over them; a hit blocks the commit until the secret is removed at its source and rotated.
