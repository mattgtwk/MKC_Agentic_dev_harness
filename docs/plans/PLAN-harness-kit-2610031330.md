# Plan: agent-agnostic harness bootstrap kit

**Status 2026-10-03: DONE.** Departures from the plan as written: `coverage_ratchet.py` folded into `harness_lint.py --ratchet` as planned; a `--quiet` mode was added for the hooks; BOOTSTRAP gained an environment step 0 that installs missing tools by instruction (user request mid-build); `on_complete` overrides are strings, matching BMAD's installed `customize.toml`; the fresh-clone section uses `npx skills experimental_install` because the skills CLI has no `check` command; the kit itself was renamed and published as github.com/mattgtwk/MKC_Agentic_dev_harness (user request mid-build).

**2026-10-04, v1.1.0:** branch floor and diff coverage added to `--ratchet`; `promotions` push check added; BOOTSTRAP step 0 made self-starting (package manager or direct installers; uv installs Python) and step 2 fetches `harness/` from the named kit repo. All three were gaps the user asked about after delivery.

## Context

Three MKC projects (MOHR monorepo, gems_to_bundles, AI Foundation) carry the same development harness around different products: a constitution, BMAD, ponytail, in-repo memory, skills, enforced testing, open/plan/close routines, ADRs and an architecture map. The most considered write-up is `D:\MOHR_MKC_MonoRepo_July26\deliverables\MohR harness discussion 260904` (docs 00-10 plus the `mohr-harness/` scaffold). Each new project re-derives the setup by hand and drifts. Measured drift across the three repos: constitution over its own token cap (MOHR live, 24.5 KB against a 4k-token cap); the `.claude/skills` junction never created (MOHR live); constitution citing skills that do not exist (MOHR live, AI Foundation); gates that exist only as prose (AI Foundation and gems_to_bundles have no git hooks or CI); lowercase `claude.md` canonical with `agents.md` a pointer (AI Foundation); BMAD personas never told about the constitution although BMAD's `customize.toml` hooks for it exist unused (all three); transcripts left in vendor folders, with MOHR's archiver reading only Antigravity's brain folder so Claude sessions stopped being archived on 31 Aug.

Goal: one reusable kit, dropped into an empty folder, that any coding agent (Claude Code, Codex, Antigravity, Cursor, Copilot, Gemini CLI) can follow to stand up the whole harness, project-agnostic, with the harness itself documented; BMAD's PM/architect/dev personas and workflows made constitution-aware during bootstrap; caveman's token discipline built in; every conversation saved inside the project.

User decisions this session: **`BOOTSTRAP.md` prompt plus a `harness/` folder of real template files**; location **`D:\MKC\agentic_harness_bootstrap\`**; BMAD central with its PM/workflow instructions modified by override; caveman adopted alongside BMAD and ponytail; all agent conversations saved within the project.

**One design change from the first draft, flagged for the user:** the constitution is Part A of `AGENTS.md`, not a separate `CONSTITUTION.md`. Codex, Cursor, Copilot and Antigravity read `AGENTS.md` as plain text with no import syntax, so a separate file referenced from line 1 would never be loaded by four of the six agents. MOHR split the two only to vendor-and-hash across three repos, which this kit does not do. The "key aspects of constitution" guidance is unchanged; it now describes Part A.

## Design principles (kept from the sources, corrected by the adversarial review)

1. **Guaranteed behaviour lives outside the model.** Git hooks and CI are the enforcement layer because only git and CI are common to every agent. No vendor hooks ship in the kit. "Hooks make it fast; the pipeline makes it certain." (MOHR 03)
2. **One instruction file, `AGENTS.md`, ≤24 KB** (Codex's `project_doc_max_bytes` default is 32 KiB). Read natively by Codex, Cursor, Copilot, Antigravity (≥1.20.3) and Claude Code (≥2.1.277, unless a `CLAUDE.md` is present). `CLAUDE.md` and `GEMINI.md` are one-line `@./AGENTS.md` adapters (Claude for older versions; Gemini does not read AGENTS.md by default). Adapters contain zero rules; lint compares them to the template bytes.
3. **One skills folder, `.agents/skills/`** (agentskills.io; read by Codex, Cursor, Copilot, Gemini CLI). Claude Code reads only `.claude/skills/`; the Antigravity IDE reads `.agent/skills/`. Both are **gitignored junctions** recreated idempotently by `harness_lint.py --doctor --relink` (Git for Windows would otherwise commit every skill twice). Every third-party skill set (BMAD, ponytail, caveman, grill-me) is installed by `npx skills add` into this folder and pinned by the committed `skills-lock.json`.
4. **Every rule names its enforcement**, and "Enforced by: convention" is allowed but must be written. A rule paragraph without "Enforced by:" fails lint. (MOHR 01; gems_to_bundles; user global rule 7.)
5. **Kind decides home.** Rule → `AGENTS.md` Part A; repo fact → Part B; invariant → `docs/ARCHITECTURE.md`; procedure → a skill; decision → `docs/adr/`; pointer → `docs/memory/`; session narrative → `docs/sessions/`; approved plan → `docs/plans/`. No fact lives only in memory.
6. **Memory is a cache.** Fact / Why / Authority, ≤800 B unless `reviewed: true`, Authority grammar `path` | `path#heading` | `ADR-NNNN`, index generated. No vendor auto-memory junction: Claude writes `MEMORY.md` in its own format and would fight the lint; harness-close promotes durable items by hand, which is the only agent-agnostic path.
7. **Ponytail on the kit.** Three scripts: `harness_lint.py` (ours: lint, ratchet, doctor, index), `save_transcript.py` (ours), `prepush_check.py` (vendored verbatim from mkc_agentic_workflow_langchain). Each has a `--selftest` that fails on a known-bad fixture and passes a known-good one. Not built, named as upgrade paths in `docs/HARNESS.md`: constitution vendoring with sha256, TestDoc catalog and test receipts, evidence ledger, cross-repo impact tool, telemetry, reviewer/mutation-prover subagents, persona review panel, action log for outward writes, two-layer dated memory, BMAD Builder agents, caveman proxy and cavecrew, Claude hook adapters, `docs/PATTERNS.md` (create at the first card).
8. **Modify BMAD by override, never by fork.** Committed `_bmad/custom/<skill>.toml` files use `persistent_facts` (`file:{project-root}/…`), `principles`, `activation_steps_prepend` and `[workflow] on_complete` so the PM, Architect and Dev agents read AGENTS.md, the map and the memory index at activation, and the build / code-review / architecture / retrospective workflows **ask** for the harness close routine on completion (prose to prose; the git hook remains the guarantee). `--doctor` loads every override with `tomllib` and asserts each key exists in the installed `customize.toml`. BMAD Builder is the upgrade path for a bespoke agent.
9. **Declared surface, one kind, review before push, tests stated.** Pre-push checks over the pushed range: `prepush_check.py` (strays outside the first commit); `Surface:` present in the first commit body when production files changed; tooling paths (`scripts/ .githooks/ .github/`) and product paths not mixed without `KIND-OK:`; a `Review:` trailer and a `Tests: <cmd> -> <summary>` trailer in the range when source changed (presence is checkable; honesty is a convention and is labelled so). (User global rules 1–8.)
10. **Three libraries, three jobs.** BMAD decides *what the work is*; ponytail decides *what gets built*; caveman decides *how it is said and how much is read*. Ponytail's docs name the pairing. None is forked.
11. **Token limiting is mechanical.** `context-budget`: AGENTS.md + CLAUDE.md + GEMINI.md + `docs/memory/MEMORY.md` ≤32 KB (WARN 24 KB). SKILL.md ≤15 KB, detail in `references/`. Memory ≤800 B. Caveman's voice is the extra on top; its own `HONEST-NUMBERS.md` puts the plain voice at ~3% median output saving (ultracave ~35%) and skill-side input saving at 0%; input savings come from `/caveman-compress` on prose (~46% on memory fixtures) and the local proxy (33.2% fewer input tokens, 54 runs). The kit installs the caveman skill as standard and offers compress and proxy as optional steps with those numbers stated.
12. **The conversation record lives in the repo.** Each session leaves `docs/sessions/session_<YYMMDDhhmm>.md` and, where the host exposes it, the raw transcript under `docs/sessions/raw/<host>/`. Nothing of record lives only in `~/.claude`, `~/.codex`, `~/.gemini` or an Antigravity brain folder; vendor memory features are not a store of record. Enforced by `save_transcript.py` in harness-close and the `session-log` and `secrets-scan` checks.

## Verified external facts the kit depends on

| Fact | Source |
|---|---|
| SKILL.md: `name` (≤64, kebab, equals dir), `description` (≤1024); optional `license`, `compatibility`, `metadata`, `allowed-tools`; body <500 lines | agentskills.io/specification |
| `npx skills add <owner/repo> [--skill x] [-a <agent>] [-g]` installs into the chosen agent's folder (symlink to canonical; copy on Windows without Developer Mode); writes `skills-lock.json` with per-skill `computedHash`; no `@ref` pin syntax | github.com/vercel-labs/skills; mintlify.wiki/vercel-labs/skills/advanced/lock-files |
| Codex reads `AGENTS.md` (repo root, nested, `~/.codex/AGENTS.md`), plain text, `project_doc_max_bytes` 32 KiB; scans `.agents/skills` and `~/.agents/skills`; sessions `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | learn.chatgpt.com/docs/agent-configuration/agents-md, /docs/build-skills; codex.danielvaughan.com |
| Claude Code ≥2.1.277 reads `AGENTS.md` natively unless `CLAUDE.md` exists (which may `@`-import it); skills from `.claude/skills/` only; transcripts `~/.claude/projects/<slug>/<uuid>.jsonl` | code.claude.com/docs/en/memory, /skills |
| Gemini CLI: `GEMINI.md` with `@./file.md` imports; `context.fileName` may add AGENTS.md; skills `.gemini/skills/`, `.agents/skills/`; chats `~/.gemini/tmp/<hash>/chats/` | geminicli.com docs |
| Cursor reads AGENTS.md; skills `.agents/skills/`, `.cursor/skills/`, compat `.claude/skills/` (a skill may appear twice with the junction; note in HARNESS.md) | cursor.com/docs/context/rules, /skills |
| Copilot reads AGENTS.md; skills `.github/skills`, `.claude/skills`, `.agents/skills` | docs.github.com about-agent-skills |
| Antigravity reads AGENTS.md (≥1.20.3); IDE skills `.agent/skills/` per BMAD's reference, `.agents/skills/` per the skills CLI (doctor checks both); conversations `~/.gemini/antigravity-cli/brain/`, `~/.gemini/antigravity/conversations/`, `~/.gemini/antigravity-ide/brain/` | BMAD skills-and-agents; ponytail agent-portability.md; discuss.ai.google.dev |
| BMAD: `npx skills add bmad-code-org/BMAD-METHOD`, then `bmad setup` (asks to run `npx skills update` when newer exists), `bmad status`; prereqs Node, npm, git, `uv`; creates `_bmad/` (`config.toml` installer-owned, `config.user.toml` gitignored), `_bmad/custom/`, `_bmad-output/` | docs.bmad-method.org/start/install-bmad |
| BMAD overrides: `_bmad/custom/<skill>.user.toml` > `<skill>.toml` > skill's `customize.toml`; `[agent]` `icon role identity communication_style` scalar, `persistent_facts principles` append (`file:{project-root}/…`, `skill:`), `activation_steps_prepend/append`, `[[agent.menu]]` by `code`; `[workflow]` adds `on_complete`; `name`/`title` read-only; base items cannot be deleted; `bmad-customize` writes and verifies | docs.bmad-method.org/customize/customize-bmad |
| `bmad-project-context` writes only into `AGENTS.md` between `<!-- bmad:context -->` fences; intents setup (no instructions worth keeping) / **adopt** (keep and improve existing) / refresh / record / audit; proposes a one-line `@AGENTS.md` for CLAUDE.md; refuses repo overviews and stack lists | docs.bmad-method.org/existing-codebases/set-and-maintain-project-context |
| BMAD agents `bmad-agent-pm` (John), `-architect` (Winston), `-dev` (Amelia), `-analyst`; workflows `bmad-prd`, `bmad-architecture`, `bmad-ticket`, `bmad-build`, `bmad-code-review`, `bmad-retrospective`, `bmad-customize`, `bmad-project-context` | docs.bmad-method.org/reference/skills-and-agents |
| Ponytail (MIT, DietrichGebert; SKILL.md 5 KB; ships `.agents/`): installable by `npx skills add DietrichGebert/ponytail`; pairs with caveman | installed plugin 4.7.0 README, docs/agent-portability.md |
| grill-me / grilling: `npx skills add mattpocock/skills --skill grill-me --skill grilling` | mkc_agentic_workflow_langchain vendoring note; mattpocock/skills |
| Caveman (Apache-2.0 ≥3.0; v3.1.0): `npx skills add JuliusBrussee/caveman` (`--skill caveman` for the voice only; `--with-init` for always-on rule files); voice rules: answer first, one idea per sentence ≤20 words, never drop negations, code/commands/paths verbatim, full sentences for security, irreversible actions, ambiguous order and anything persisted; other skills `caveman-compress` (prose only, keeps structure/code/paths, backups out of tree), `caveman-commit`, `caveman-review`, `caveman-stats`, `cavecrew`, `investigate-first`, `verify-and-stop`, `lean-build`; proxy `npm i -g @caveman-ai/cli`, `caveman setup --install`, `caveman start` (127.0.0.1:8787; never logs auth headers) | github.com/JuliusBrussee/caveman README, INSTALL.md, docs/HONEST-NUMBERS.md, docs/technical/*, skills/*/SKILL.md |

BMAD v6 and caveman v3 move quickly; `skills-lock.json` is the pin, `--doctor` recomputes the hashes, and the agent declines `bmad setup`'s update prompt during bootstrap.

## Deliverable layout

`D:\MKC\agentic_harness_bootstrap\`

```
BOOTSTRAP.md                 the recipe (≈2 pages; numbered steps; each ends with a check; proof; fresh-clone section)
README.md                    ten lines: what this is, run BOOTSTRAP.md, how to upgrade a bootstrapped project (re-copy harness/, rerun --doctor)
harness/                     mirrors the target repo root; copy verbatim, then fill <placeholders>
  AGENTS.md                  Part A: Constitution (version line; sections below). Part B: This repo (six answers; bmad:context fence). ≤24 KB
  CLAUDE.md                  @./AGENTS.md  (+ one comment line; must equal template bytes)
  GEMINI.md                  @./AGENTS.md  (same)
  NEXT-STEPS.md              What is true now (measured <date>) · Step 0: re-verify before acting · Open threads · Traps in order · Kickoff text
  .gitignore                 .env*, .claude/skills/, .agent/skills/, _bmad/config.user.toml, _bmad/custom/*.user.toml, _bmad-output/**/*.user.*, .harness/, coverage output, *.original.md
  .gitattributes             .githooks/* text eol=lf; *.py text eol=lf
  docs/HARNESS.md            one page: the loop; kind→home→kept-honest-by; enforcement layers; the three libraries; token budget with caveman's numbers; conversation record; junction note; upgrade paths not built
  docs/ARCHITECTURE.md       `last_reviewed:`; layout; flows; boundaries & invariants (each cites the defect that bought it); "Deliberately not built yet"; two example verify: lines
  docs/adr/README.md         register (ID | Title | Status | Date); 4 sections; Consequences names the cost; Part A cites no ADR numbers
  docs/adr/0000-template.md
  docs/adr/0001-adopt-harness.md
  docs/memory/README.md      schema; Authority grammar; reviewed: true; write-back rule; promotion from vendor auto-memory by hand
  docs/memory/MEMORY.md      generated
  docs/memory/project-where-the-rules-live.md   seed page (Authority: AGENTS.md#where-things-live)
  docs/sessions/README.md    session log template (Summary · Decisions · Commands and tests run · Gates · Next); raw/<host>/ layout; secrets rule
  docs/plans/.gitkeep        naming rule lives in AGENTS.md Part A §4 (PLAN-<topic>-<YYMMDDhhmm>.md; read the clock; Status + departures header after execution)
  .agents/skills/harness-open/SKILL.md
  .agents/skills/harness-plan/SKILL.md
  .agents/skills/harness-close/SKILL.md
  _bmad/custom/config.toml, bmad-agent-pm.toml, bmad-agent-architect.toml, bmad-agent-dev.toml, bmad-build.toml, bmad-code-review.toml, bmad-architecture.toml, bmad-retrospective.toml
  .githooks/pre-commit       exec "$(python3 -c 1 2>/dev/null && echo python3 || echo py -3)" scripts/harness_lint.py
  .githooks/pre-push         harness_lint.py --prepush && prepush_check.py --git-hook   (seconds; no test suite)
  scripts/harness_lint.py    ours; see "Lint"
  scripts/save_transcript.py ours; see below
  scripts/prepush_check.py   vendored verbatim; two tunables named at the top: SKIP regex, BASE ref
  .github/workflows/harness-gates.yml   on: [push, pull_request]: harness_lint.py; <TEST_COMMAND>; harness_lint.py --ratchet (compares to origin/main's baseline too)
  coverage_baseline.json     {"line_pct": null}  (null = WARN until set)
```

Removed from the first draft after review: `CONSTITUTION.md` (merged), `docs/PATTERNS.md`, `docs/plans/README.md`, kit `CHANGELOG.md`, `adapters/claude/settings.json`, vendored ponytail/grill-me copies, `coverage_ratchet.py` (now `--ratchet`), the Claude auto-memory junction.

## AGENTS.md Part A (constitution): sections and the guidance BOOTSTRAP gives

Preamble: `harness-constitution v1.0.0`; "a rule is added only if it names the value it adds, how it is enforced, and what it displaces"; the 24 KB cap; Part B may add detail and may not contradict Part A.
1. **Operating model**: the loop `harness-open → harness-plan → implement → harness-close`; BMAD for anything bigger than a story; one work item per session.
2. **Adapter rule**: this file is canonical; CLAUDE.md/GEMINI.md are one-line imports; `.agents/skills/` canonical with gitignored junctions. Enforced by `adapter-thin`, `doctor`.
3. **Where things live**: kind → home → kept honest by.
4. **Workflow**: plan (investigate first; three stances PM / ponytail / grill-me; declared Surface), implement, document, test, self-review gate (six axes incl. mutate-to-RED), verify and stop, decision promotion, close. Plan files `docs/plans/PLAN-<topic>-<YYMMDDhhmm>.md`. Enforced by the skills and `--prepush` presence checks; the gate itself is a convention and says so.
5. **Engineering rules**: config & secrets (Enforced by `secrets-scan`, `.gitignore`); native Windows execution (ASCII, assert exit codes, quote paths, per-agent shell note; convention); testing bar (definition of tested; red-first regression; ratchet never a target; "a suite not run is not green"; Enforced by `--ratchet` in CI and the `Tests:` trailer; the rest convention); **token discipline** (budgets as in principle 11; caveman voice on by default; full sentences for anything persisted; `/caveman-compress` only on prose files, never on AGENTS.md; Enforced by `context-budget`, `skills-frontmatter`, `memory-schema`; voice by convention).
6. **Deterministic governance**: the lint table; "a check that did not run is WARN, never PASS".
7. **Skills & memory**: crystallization gate; kind decides home; never restate a rule in memory; wave-close promotion; pruning at retrospective.
8. **Close routine and the conversation record**: as in principle 12.
9. **Access boundaries**: ask-first / never lists; vendor memory is not a store of record.
10. **The user's working rules, mapped**: one table, rule → artefact → enforcement-or-convention, covering declared Surface, one PR one kind, review before push, SCOPE-OK never self-authored, read consumers and incumbent first, a claim is a defect if not enforced, never type a tool-generated number, fix the product not the tooling.
11. **Changing Part A**: trigger recorded, three questions answered, version bumped, reviewed by someone who did not write it (solo: after grill-me).

Part B placeholders from six questions: project name, stack, test command, coverage report path, work tracker (or none), sibling repos (or none).

## BMAD overrides (`_bmad/custom/*.toml`, committed)

Common: `persistent_facts = ["file:{project-root}/AGENTS.md", "file:{project-root}/docs/ARCHITECTURE.md", "file:{project-root}/docs/memory/MEMORY.md"]`; `activation_steps_prepend = ["Read the three persistent facts before greeting. Open any memory page whose index line is relevant. Caveman voice; full sentences for anything persisted."]`.
- PM principles: why before what; acceptance criteria before design; simplest thing that works, each abstraction justified in one line; decisions recorded before proceeding; a story names its Surface and test plan.
- Architect principles: structural change updates `docs/ARCHITECTURE.md` in the same change and gets an ADR whose Consequences name the cost; prefer existence/absence `verify:` lines to counts.
- Dev principles: bugfix is red-first; a test is done when watched going RED; investigate first; never fix outside the Surface, write a BACKLOG line; verify and stop; ask for harness-close before "done".
- `bmad-build`, `bmad-code-review` `[workflow] on_complete`: "Ask to run the harness-close skill; the story is not done until it passes." Code review adds filing-by-kind.
- `bmad-architecture` `on_complete`: one ADR per decision with a register row; bump `last_reviewed`.
- `bmad-retrospective` `on_complete`: wave-close promotion; walk the skills list: unused → delete, drifted → defect.

## Lint (`scripts/harness_lint.py`; stdlib; `--json`; exit 1 on ERROR; modes: default, `--prepush`, `--ratchet`, `--doctor [--relink]`, `--rebuild-index`, `--selftest`)

| Check | Rule | Severity |
|---|---|---|
| `agents-present` | `AGENTS.md` exists with the version line and a Part A heading | ERROR |
| `agents-size` | ≤24 KB | ERROR |
| `rule-enforcement` | every rule paragraph in Part A contains "Enforced by:" | ERROR |
| `adr-refs` | no `ADR-\d{4}` in Part A | ERROR |
| `adapter-thin` | CLAUDE.md and GEMINI.md byte-equal the template (or ≤5 lines containing `@./AGENTS.md`) | ERROR |
| `context-budget` | AGENTS.md + CLAUDE.md + GEMINI.md + MEMORY.md ≤32 KB (WARN 24 KB) | ERROR / WARN |
| `skill-refs` | every backticked `harness-*`, `bmad-*`, `caveman*`, `grill-me`, `ponytail*` in AGENTS.md / HARNESS.md resolves to `.agents/skills/<name>/` | ERROR |
| `skills-frontmatter` | `name` == dir, kebab ≤64; `description` ≤1024; body ≤15 KB | ERROR |
| `skills-lock` | `skills-lock.json` present; recomputed hashes match (`--doctor`) | ERROR |
| `memory-schema` | frontmatter name/description/type; **Fact/Why/Authority**; ≤800 B unless `reviewed: true` | ERROR |
| `memory-authority` | `path` exists / `path#heading` exists / `ADR-NNNN` in register | ERROR |
| `memory-index` | one MEMORY.md line per page; `--rebuild-index` regenerates | ERROR |
| `adr-register` | one row per `docs/adr/NNNN-*.md`; sequential | ERROR |
| `architecture-map` | exactly one; `last_reviewed` ≤90 d | WARN only (harness-close instructs the bump) |
| `claims` | every `<!-- verify: exists\|absent\|count … -->` holds | ERROR |
| `secrets-scan` | token-shaped literals absent from `*.md`; `.env*` untracked | ERROR |
| `surface` (`--prepush`) | production files changed in range ⇒ first commit body has `Surface:` | ERROR |
| `one-kind` (`--prepush`) | tooling paths and product paths both changed ⇒ `KIND-OK:` in range | ERROR |
| `trailers` (`--prepush`) | source changed ⇒ `Review:` and `Tests:` trailers somewhere in the range | ERROR (presence; honesty is a convention) |
| `session-log` (`--prepush`) | source changed in range ⇒ range also touches `docs/sessions/` | ERROR |
| `ratchet` (`--ratchet`) | coverage.xml line-rate ≥ baseline and ≥ `origin/main:coverage_baseline.json`; `--update-baseline`; null baseline = WARN | ERROR / WARN |
| `doctor` | junctions `.claude/skills`, `.agent/skills` → `.agents/skills` (`--relink` creates); `core.hooksPath` set; hooks LF; python resolves from `sh`; `_bmad/` present; every `_bmad/custom/*.toml` key exists in the installed `customize.toml` (tomllib); caveman, ponytail, grill-me dirs present; node, uv on PATH | ERROR |

`--selftest`: temp repo; every check PASSes on the good fixture and FAILs on one deliberate break each.

## `scripts/save_transcript.py`

Host table: Claude `~/.claude/projects/<slug>/*.jsonl` (slug = cwd with `:\/` → `-`); Codex `~/.codex/sessions/**/rollout-*.jsonl`; Gemini `~/.gemini/tmp/*/chats/*`; Antigravity `~/.gemini/antigravity-cli/brain/**`, `~/.gemini/antigravity/conversations/**`, `~/.gemini/antigravity-ide/brain/**`. Copies files modified after `.harness/last_transcript_sync` whose text contains the repo root (or whose folder slug matches) to `docs/sessions/raw/<host>/<YYMMDDhhmm>-<basename>`; updates the marker; prints copied and skipped-with-reason; Cursor prints "no file export; attach manually"; never deletes a source; `--selftest` with a fake home.

## BOOTSTRAP.md, step by step (each step ends with a check)

0. **Preconditions.** git, Node ≥20, Python ≥3.11, `uv`. `git init -b main`; create the remote and push an empty first commit (`prepush_check.py` needs a merge-base). Short root path on Windows.
1. **Copy the kit.** `harness/*` → repo root. Check: `--selftest` on both scripts green.
2. **Write AGENTS.md.** Six answers fill Part B; Part A placeholders filled; delete any rule you cannot name an enforcement for. Check: `agents-*`, `adapter-thin`, `context-budget` green.
3. **Install skills, pinned.** `npx skills add bmad-code-org/BMAD-METHOD`, `… JuliusBrussee/caveman --skill caveman`, `… DietrichGebert/ponytail`, `… mattpocock/skills --skill grill-me --skill grilling`, each selecting **only** the agent whose path is `.agents/skills/` (Codex). `bmad setup` (decline the update prompt), `bmad status`. Check: `git status --porcelain` shows only `_bmad/`, `.agents/skills/*`, `skills-lock.json`; `--doctor` override-key check green; PM activation reads AGENTS.md.
4. **Project context.** `bmad-project-context` with intent **adopt**, AGENTS.md as the governance input; accept the fenced block; decline its CLAUDE.md edit. Check: `agents-size` green.
5. **Make skills visible to every agent.** `harness_lint.py --doctor --relink` creates the two junctions. Check: `--doctor` green; `/caveman` answers first without preamble.
6. **Arm enforcement.** `git config core.hooksPath .githooks`; `<TEST_COMMAND>` in `harness-gates.yml`; `SKIP` and `BASE` in `prepush_check.py`; branch protection on `main` requiring the gates workflow (the one manual step; `gh api` line given). Check: a 900-byte memory page is refused at commit; a stray file outside the first commit is refused at push.
7. **First records.** ADR-0001; ARCHITECTURE.md first survey; NEXT-STEPS.md; one memory page; `--rebuild-index`; first session log.
8. **Prove it.** `harness-open`; trivial change via `harness-plan` → implement → `harness-close` (runs `save_transcript.py`); `--ratchet --update-baseline` after the first green CI run; commit with `Surface:`, `Tests:`, `Review:` trailers; push. Check: `docs/sessions/raw/<host>/` holds this session's transcript; CI green. Not done without this proof.
9. **Optional, token side.** `/caveman-compress` on NEXT-STEPS.md and memory pages only, lint green after; the caveman proxy per machine, with the honest numbers quoted.
10. **Fresh clone.** `--doctor --relink`, `git config core.hooksPath .githooks`, `npx skills add` from `skills-lock.json` if the folder is empty.

## The three routines

- **harness-open**: read MEMORY.md, ARCHITECTURE.md, NEXT-STEPS.md (run Step 0); `git status`; `harness_lint.py` (prints the context-budget figure); print constitution version and the loop. Never blocks.
- **harness-plan `<feature|bugfix|refactor|hotfix> <topic>`**: investigate first; stances in order (PM via `bmad-agent-pm` beyond a one-liner; ponytail; grill-me mandatory when irreversible, outward-facing or >10 files); fixed shape: acceptance criteria · Surface · design (each abstraction justified in one line) · test plan · architecture delta y/n · ADR y/n · open questions with recommended answers; writes `docs/plans/PLAN-…`; stops for approval. Surface goes into the first commit body.
- **harness-close**: (1) self-review gate, six lines; (2) verify and stop: smallest proof set, output recorded, no enhancements after pass; (3) ARCHITECTURE.md matches reality, `last_reviewed` bumped if surveyed; (4) NEXT-STEPS.md rewritten; (5) decisions → ADR + register row; (6) wave-close promotion, ticked only when the owner file changed; (7) memory pages (promote anything durable from vendor auto-memory by hand), `--rebuild-index`; (8) session log in full sentences; (9) `save_transcript.py`; (10) `harness_lint.py` 0 errors; (11) plan file Status + departures; (12) commit with `Surface:`, `Tests:`, `Review:` in the body; push only on the user's go. The user's "update docs" ritual is this routine.

## Verification of the kit (execution phase)

1. `harness_lint.py --selftest`, `save_transcript.py --selftest` green, each check seen red once; `prepush_check.py --self-test` green unchanged.
2. Dry-run bootstrap into `D:\tmp\…\bootstrap_proof` following BOOTSTRAP.md literally against a throwaway GitHub remote: `--doctor` green; bad memory page refused at commit; stray file refused at push; missing `Surface:` refused at push; PM activation prints the AGENTS.md fact; `bmad-project-context` block lands inside 24 KB; this session's transcript appears under `docs/sessions/raw/claude/`; CI green on push.
3. Skill visibility, proven by run where the tool is installed here (Claude Code via junction; Codex or Gemini CLI if present) and by citation otherwise (Cursor, Copilot, Antigravity); stated as such in HARNESS.md.
4. Budgets: BOOTSTRAP.md ≈2 pages; AGENTS.md template ≤24 KB; always-loaded total ≤32 KB; each SKILL.md ≤15 KB.

## Review findings not adopted, with reason

- Dropping `docs/plans/` entirely: the user's own practice copies approved plans into the repo as the document of record (AI Foundation `plan-doc-naming`); kept, README removed.
- Dropping `.harness/`: still needed for the transcript sync marker; gitignored.
- Running tests in pre-push: rejected per MOHR 03 §3; tests run in CI and in harness-close.
