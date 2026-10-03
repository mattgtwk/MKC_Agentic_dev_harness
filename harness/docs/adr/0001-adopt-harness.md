# ADR-0001: Adopt the agentic development harness

**Status:** Accepted. **Date:** <YYYY-MM-DD>. **Trigger:** starting <project name> with coding agents from more than one vendor.

## Context

Coding agents follow prose only as long as it is in context and uncontradicted. Three earlier MKC projects each re-derived the same working method by hand and drifted: rulebooks outgrew their caps, skills were visible to one vendor only, gates existed as text, conversations stayed in vendor folders. The kit at github.com/mattgtwk/MKC_Agentic_dev_harness distils what held up.

## Decision

Adopt the kit as copied into this repository: `AGENTS.md` Part A as the constitution with every rule naming its enforcement; `.agents/skills/` as the one skills folder with junctions for Claude Code and Antigravity; BMAD, ponytail, caveman and grill-me installed by `npx skills add` and pinned in `skills-lock.json`; BMAD personas made constitution-aware through `_bmad/custom/` overrides; in-repo memory, ADRs, architecture map, plans and session records; git hooks and CI running `scripts/harness_lint.py` as the guarantee.

## Consequences

- Every change pays the close routine (session log, transcript copy, memory, map, trailers). That is the cost of a record that survives the chat.
- The lint blocks commits and pushes on bookkeeping, not only on code. A green suite is not enough.
- Third-party skills can only be upgraded through `npx skills add` and a lock change, which is slower than editing them in place and is the point.
- Python 3.11+, Node 20+, git, gh and uv become prerequisites on every machine; bootstrap step 0 installs them.

## Alternatives rejected

- One long CLAUDE.md: invisible to the other agents and unenforced.
- Vendor hooks as the guarantee: only one agent runs them.
- Separate CONSTITUTION.md: Codex, Cursor, Copilot and Antigravity read AGENTS.md as plain text and never follow a pointer in line 1.
