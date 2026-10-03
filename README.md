# MKC Agentic dev harness

A bootstrap kit for the way MKC works with coding agents, distilled from three projects and written so that Claude Code, Codex, Antigravity, Cursor, Copilot and Gemini CLI all follow the same rules from the same files.

- **To bootstrap a new project:** open the empty folder in your agent and hand it `BOOTSTRAP.md`. It installs what is missing, copies `harness/`, installs and pins BMAD, ponytail, caveman and grill-me, wires the gates, and proves the loop once.
- **What you get:** one `AGENTS.md` (constitution plus repo facts) with every rule naming its enforcement; skills in `.agents/skills/` visible to every agent; in-repo memory, ADRs, architecture map, plans and session records including raw transcripts; BMAD personas that read the constitution at activation; git hooks and CI running one stdlib lint. The one-page explanation is `harness/docs/HARNESS.md`.
- **To upgrade a bootstrapped project:** re-copy `harness/` over it, keep your Part B and records, bump the version line in `AGENTS.md`, run `python scripts/harness_lint.py --doctor --relink` and the lint.

Sources: the MOHR harness discussion set (September 2026), gems_to_bundles, AI Foundation, and the public BMAD, ponytail and caveman repositories. Caveman's own benchmark caveats are quoted where its numbers are.
