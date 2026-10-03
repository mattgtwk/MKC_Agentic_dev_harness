# How this harness works

One page. The rules are in `AGENTS.md` Part A; this explains the shape so a newcomer can hold it in their head.

## The loop

`harness-open` reads the memory index, the architecture map and `NEXT-STEPS.md`, runs the lint, and prints where you are. `harness-plan` produces a plan in a fixed shape (acceptance criteria, Surface, design, test plan, map and ADR decisions) through three stances in order: the BMAD product-manager persona asks why before what, `ponytail` asks whether each piece needs to exist, `grill-me` interrogates anything irreversible. You implement. `harness-close` proves it (self-review gate, tests, verify and stop), records it (session log, transcript, ADRs, map, NEXT-STEPS) and promotes every lesson to its owner file. Work bigger than a story goes through the BMAD skills first (brief, PRD, architecture, tickets).

## Where things live

| Kind | Home | Kept honest by |
|---|---|---|
| Rule | `AGENTS.md` Part A | `rule-enforcement` |
| Repo fact | `AGENTS.md` Part B | `claims` |
| Invariant | `docs/ARCHITECTURE.md` | `architecture-map`, `claims` |
| Procedure | `.agents/skills/<name>/SKILL.md` | `skills-frontmatter` |
| Decision | `docs/adr/` + register | `adr-register` |
| Pointer | `docs/memory/` | `memory-*` |
| Session record | `docs/sessions/` | `session-log` |
| Approved plan | `docs/plans/` | `harness-close` |

## Enforcement, in layers

1. **Git hooks** (`.githooks/`, armed by `git config core.hooksPath .githooks`): pre-commit runs the lint in under a second; pre-push adds the commit-range checks and the declared-surface guard. Both are shell plus stdlib Python, so every agent and every human gets the same gate.
2. **CI** (`.github/workflows/harness-gates.yml`): the same lint, the test suite, and the coverage ratchet, on every push and pull request. Branch protection on `main` makes it binding; that is the one manual step in bootstrap.
3. **Skills**: the open/plan/close procedures. They make the loop fast and legible; they are not the guarantee.
4. **Vendor hooks**: none shipped. If you add a Claude Stop hook that runs the lint, it is a convenience over the same script.

A check that could not run reports WARN, never PASS.

## The three libraries

| Library | Job | How it is bound to the harness |
|---|---|---|
| BMAD | what the work is: personas, brief, PRD, architecture, stories, build, review, retro | overrides in `_bmad/custom/*.toml` make the PM, architect and dev personas read `AGENTS.md`, the map and the memory index at activation, and make build/review/architecture/retro workflows ask for `harness-close` on completion; `--doctor` verifies every override key against the installed `customize.toml`; `bmad-project-context` writes repo facts into Part B between fences |
| ponytail | what gets built: the laziest solution that works | the second planning stance; a rule in Part A section 4 |
| caveman | how it is said and how much is read | voice on by default (rule in Part A section 5); `caveman-compress` for prose files; the proxy is optional per machine |

None is forked. Each is installed by `npx skills add` into `.agents/skills/` and pinned in `skills-lock.json`.

## Token budget

The always-loaded set (`AGENTS.md`, the two adapters, `docs/memory/MEMORY.md`) is capped at 32 KB by `context-budget`; `AGENTS.md` alone at 24 KB (Codex's project document cap is 32 KiB). Skills load on demand and are capped at 15 KB each; memory pages at 800 bytes. That budget is the primary token control.

Caveman's own `docs/HONEST-NUMBERS.md` reports: the plain caveman voice saves about 3% of output tokens at the median against an "answer concisely" control and ultracave about 35%; the skill saves 0% of input tokens; `caveman-compress` cut memory files by about 46% in its fixtures; the local proxy plus skill cut input tokens by 33.2% over 54 runs. Treat the voice as a cheap extra, the compress as optional for prose, and the proxy as a per-machine choice.

## The conversation record

Every session ends with `docs/sessions/session_<YYMMDDhhmm>.md` and a run of `python scripts/save_transcript.py`, which copies this project's raw transcripts out of the vendor folders (Claude, Codex, Gemini CLI, Antigravity) into `docs/sessions/raw/<host>/`. Cursor has no file export. Nothing of record lives only in a vendor's home folder. `secrets-scan` runs over the copies.

## Agent compatibility, honestly

| Agent | Reads `AGENTS.md` | Sees `.agents/skills/` | Note |
|---|---|---|---|
| Codex | natively | natively | plain text, no imports; 32 KiB cap |
| Claude Code | natively (recent) or via `CLAUDE.md` import | via the `.claude/skills` junction | does not read `.agents/skills/` itself |
| Gemini CLI | via `GEMINI.md` import | natively | |
| Cursor | natively | natively (and `.claude/skills`, so a skill may list twice on one machine) | |
| Copilot | natively | natively | |
| Antigravity | natively (IDE 1.20.3 and later) | IDE via the `.agent/skills` junction; CLI natively | its conversation store is not configurable; `save_transcript.py` copies from it |

Proven by run in bootstrap where the tool is installed; by citation otherwise.

## Deliberately not built (upgrade paths)

Constitution vendoring with a hash header across repos; TestDoc metadata and a test catalog; test-run receipts; an evidence ledger linking regression tests to historical bugs; a cross-repo impact tool; telemetry; reviewer, security and mutation-prover subagents; a persona review panel for documents; an append-only action log for outward writes; two-layer dated memory; BMAD Builder custom agents; the caveman proxy and cavecrew presets; Claude hook adapters; a pattern-card catalog (`docs/PATTERNS.md`, create it at the first card). Each has a known source in the MKC repositories; add one when a measured need appears, not before.

## Upgrading a bootstrapped project

Re-copy `harness/` from the kit over the repo, keep your Part B and your records, bump the version line, run `python scripts/harness_lint.py --doctor --relink` and the lint. `npx skills experimental_install` restores the pinned skills on a fresh clone; `npx skills update` upgrades them and rewrites `skills-lock.json`, after which `--doctor` re-checks every override key.
