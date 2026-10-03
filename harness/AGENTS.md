# AGENTS.md

harness-constitution v1.0.0 (kit: github.com/mattgtwk/MKC_Agentic_dev_harness). Every coding agent and every person working in this repository follows this file. Part A is the constitution and is project-agnostic; Part B is this repository. Part B may add detail and may not contradict Part A. `CLAUDE.md` and `GEMINI.md` only import this file.

A rule enters Part A only if it names (a) the value it adds, (b) how it is enforced, and (c) what it displaces. A rule that cannot name an enforcement says "Enforced by: convention" and means it. This file stays under 24 KB (`agents-size`); the always-loaded set (this file, the two adapters, `docs/memory/MEMORY.md`) stays under 32 KB (`context-budget`).

## Part A: Constitution

### 1. Operating model

- **One loop, three skills.** Work moves through `harness-open` (orient), `harness-plan` (decide), implement, `harness-close` (prove, record, promote). The skill is the process; nobody remembers a checklist. Enforced by: the skills' completion checklists; the `--prepush` presence checks in section 6.
- **BMAD above the story.** Anything bigger than a story gets a brief, PRD or architecture through the BMAD skills before stories are cut; story-sized work goes straight to `harness-plan`. The BMAD personas read this file, the architecture map and the memory index at activation; their overrides live in `_bmad/custom/`. Enforced by: `_bmad/custom/*.toml`, checked by `--doctor`.
- **Three libraries, three jobs.** BMAD decides what the work is. `ponytail` decides what gets built: the laziest solution that works, stdlib and platform before a dependency, one line before fifty. `caveman` decides how it is said and how much is read. None is forked; each is installed by its own installer and pinned in `skills-lock.json`. Enforced by: `skills-lock`; `--doctor`.
- **One work item per session.** Context bleed between tasks breeds contradictory assumptions. Enforced by: convention.

### 2. Adapter rule (vendor neutrality)

- **This file is canonical.** Codex, Cursor, Copilot, Antigravity and Claude Code read it natively. `CLAUDE.md` and `GEMINI.md` contain one line, `@./AGENTS.md`, and no rules. Enforced by: `adapter-thin`.
- **Skills live in `.agents/skills/`.** Claude Code reads `.claude/skills/` and the Antigravity IDE reads `.agent/skills/`; both are gitignored junctions to `.agents/skills/`, recreated by `python scripts/harness_lint.py --doctor --relink`. A skill that exists only in a vendor folder is invisible to the other agents. Enforced by: `--doctor`; `.gitignore`.
- **Enforcement is git and CI, never a vendor hook.** Hooks make the loop fast; the pipeline makes it certain. A behaviour that must be guaranteed is a git hook check or a CI job, because those are the only mechanisms every agent shares. Enforced by: `.githooks/`; `.github/workflows/harness-gates.yml`.

### 3. Where things live

| Kind | Home | Kept honest by |
|---|---|---|
| Rule (binds everyone, every time) | this file, Part A | `rule-enforcement`, `agents-size` |
| Repository fact (build, run, layout, gotchas) | this file, Part B, including the `bmad:context` block | `agents-size`, `claims` |
| Invariant about the code's structure | `docs/ARCHITECTURE.md` | `architecture-map`, `claims` |
| Procedure | a skill in `.agents/skills/` | `skills-frontmatter`, `skill-refs` |
| Decision that constrains future work | `docs/adr/NNNN-*.md` and the register | `adr-register` |
| Pointer, preference, why-history | `docs/memory/*.md` | `memory-schema`, `memory-authority`, `memory-index` |
| Session narrative and raw transcript | `docs/sessions/` | `session-log`, `secrets-scan` |
| Approved plan | `docs/plans/PLAN-<topic>-<YYMMDDhhmm>.md` | `harness-close` step 11 |
| Machine-specific value or secret | the environment; never a committed file | `secrets-scan`; `.gitignore` |

- **Kind decides home.** A rule goes to Part A; an invariant to the map; a procedure to a skill; a decision to an ADR; a pointer to memory. No fact lives only in memory, and anything that can go out of date has an owner outside memory. Enforced by: `memory-authority` (every memory page points at its owner); the table above.

### 4. Workflow

- **Investigate first.** Separate what was observed from what is assumed; no product code changes until one mechanism explains the evidence. Enforced by: convention (caveman's investigate-first, adopted as text).
- **Plan before code, three stances in order.** For anything larger than a one-line fix: the product-manager stance (`bmad-agent-pm`: why before what, acceptance criteria before design); then `ponytail` (the simplest thing that works, every new dependency or abstraction justified in one line); then `grill-me`, mandatory before approving anything irreversible, outward-facing or touching more than about ten files. The plan is `docs/plans/PLAN-<topic>-<YYMMDDhhmm>.md` (read the clock; never type a stamp) and gets a Status and departures header when the work closes. Enforced by: `harness-plan`.
- **Declare the surface.** The plan names `Surface:` (the file list) and the first commit body carries it. A defect found in any other file is a BACKLOG line, not a fix, whoever caused it. Enforced by: `surface` and `prepush_check.py` at push.
- **One change, one kind.** Product and tooling (`scripts/`, `.githooks/`, `.github/`) do not ride in the same change without a stated reason. Enforced by: `one-kind` at push; `KIND-OK: <reason>` releases it.
- **Self-review gate.** Before claiming done: trust boundaries; completeness against ground truth; verification honesty (a suite you did not run is not green; an exit code is not a log; mutate the code and watch the test go red); regression risk; output integrity; failure modes fail loudly. Enforced by: `harness-close` step 1; convention for its honesty.
- **Verify and stop.** The smallest proof set that shows acceptance; no enhancements, refactors or extra tests after it passes. Enforced by: convention (caveman's verify-and-stop, adopted as text).
- **Record decisions before proceeding.** The moment a question is answered, write it down: an ADR if durable, the work item if ticket-scoped, memory only as a pointer. Nobody answers the same question twice. Enforced by: `harness-close` step 5; `adr-register`.
- **Read the consumers and the incumbent before changing either.** `git grep -w` every site that reads a value you change, including files already open; read the incumbent on the base branch and say what behaviour is being replaced. Enforced by: the RULE TWO report of `prepush_check.py` at push; convention for acting on it.
- **Review before push.** The whole branch diff gets an adversarial review iterated until nothing new is found; the last commit carries `Review: <outcome>`. Enforced by: `trailers` (presence); convention (honesty).

### 5. Engineering rules

- **Configuration and secrets.** No committed file names a host, a drive, an organisation or a person's folder: named environment variables or placeholders instead. Secrets never appear in prompts, logs, commits, transcripts or memory. Enforced by: `secrets-scan`; `.gitignore` (`.env*`).
- **Native execution, mostly Windows.** Scripts are ASCII; every native call asserts its exit code; paths with spaces are quoted; repositories live under a short root; hooks are LF. Each agent uses its own shell tool and says which. Enforced by: `.gitattributes`; `--doctor` (hook line endings); convention.
- **Definition of tested.** A behaviour is tested when a test names it, asserts it, and has been seen to fail when the behaviour is broken. Coverage does not define tested; the witnessed red does. Enforced by: convention; `Tests:` trailer presence at push.
- **Every bugfix ships a regression test written first.** Red captured before the fix, green after, both named in the commit body. Enforced by: `harness-plan` (names the test); convention.
- **Coverage is a ratchet, never a target.** The floor in `coverage_baseline.json` only rises; new and changed lines are covered. Lowering it needs `--force` and a stated approval. Enforced by: `--ratchet` in CI.
- **A suite you did not run is not green.** Test output is recorded in the session log and summarised in the `Tests:` trailer. Enforced by: `trailers` (presence); convention.
- **Token discipline.** This file, the adapters and the memory index stay under 32 KB; a `SKILL.md` stays under 15 KB with detail in `references/`; a memory page under 800 bytes. `caveman` voice is on by default: answer first, one idea per sentence, nothing dropped that changes meaning; full sentences for security warnings, irreversible actions, ambiguous step order and anything persisted (code, commits, docs, tickets). `caveman-compress` may run on prose files such as `NEXT-STEPS.md` and memory pages, never on this file. Enforced by: `context-budget`, `skills-frontmatter`, `memory-schema`; voice by convention.

### 6. Deterministic governance

`python scripts/harness_lint.py` runs at pre-commit and in CI; `--prepush` adds the commit-range checks at push; `--ratchet` runs in CI; `--doctor` checks the machine. A check that could not run reports WARN, never PASS. Exit 1 on any ERROR.

| Check | Duty |
|---|---|
| `agents-present`, `agents-size`, `rule-enforcement`, `adr-refs` | this file exists with its version line, under 24 KB; every Part A rule names its enforcement; no ADR numbers in Part A |
| `adapter-thin`, `context-budget` | adapters import only; always-loaded set under 32 KB |
| `skill-refs`, `skills-frontmatter`, `skills-lock` | every cited skill exists; valid frontmatter and size; third-party skills pinned |
| `memory-schema`, `memory-authority`, `memory-index` | Fact/Why/Authority, 800 B, Authority resolves, index matches (`--rebuild-index`) |
| `adr-register`, `architecture-map`, `claims` | one register row per ADR; one map with `last_reviewed` (warn after 90 days); every `verify:` claim holds |
| `secrets-scan` | no token-shaped literals in docs or transcripts; no tracked `.env` |
| `surface`, `one-kind`, `trailers`, `session-log` (`--prepush`) | `Surface:` in the first commit; product and tooling not mixed; `Review:` and `Tests:` present; `docs/sessions/` touched when source changed |
| `ratchet` (`--ratchet`) | the coverage floor never falls |
| `doctor` | junctions, hooks, python, node, uv, BMAD overrides, pinned skills |

- **Claims carry their check.** A factual statement about this codebase in this file, the map or a skill carries an HTML comment on the next line beginning `verify:` with one of `exists <path>`, `absent '<regex>' in <dir>`, `present '<regex>' in <dir>` or `count '<regex>' in <dir> between A and B`. Prefer existence and absence to counts; give counts a band. A claim that cannot be checked is rewritten as an observation or deleted. Enforced by: `claims`.

### 7. Skills and memory

- **A skill is created only when the procedure was needed twice, took more than thirty minutes to work out, and is not obvious from the docs.** Below that bar it is a note in an existing skill or a memory pointer. Imported skills enter through the same gate and are pinned. Enforced by: convention; `skills-lock`.
- **Memory is a cache, not an archive.** A page is `**Fact:**`, `**Why:**`, `**Authority:**` under 800 bytes; the Authority is a `path`, a `path#heading` or an `ADR-NNNN` and must resolve. Never restate a rule in memory: memory is read first, so a stale copy beats the truth. Revise in place; a hand-edited page carries `reviewed: true`. Vendor auto-memory is not a store of record: anything durable it holds is promoted into `docs/memory/` at close. Enforced by: `memory-schema`, `memory-authority`, `memory-index`.
- **Promote every lesson to its owner before the work closes.** Each lesson gets a kind and an owner file; the item is ticked only when that file changed. Naming the owner is not promoting to it. Enforced by: `harness-close` step 6.
- **Prune on schedule.** At each retrospective a skill unused for a cycle is fixed or deleted and a drifted claim is a defect. Enforced by: the `bmad-retrospective` override in `_bmad/custom/`; convention.

### 8. Close routine and the conversation record

- **A session ends only when** the self-review gate is written out; tests ran after the last edit and their output is recorded; `docs/ARCHITECTURE.md` matches reality; `NEXT-STEPS.md` is rewritten for the next session; decisions are in ADRs; lessons are promoted; memory pages pass and the index is rebuilt; the session log is written; transcripts are copied; the lint is clean; the plan has its Status header; the commit carries `Surface:`, `Tests:` and `Review:`. Enforced by: `harness-close`; `--prepush`.
- **The conversation record lives in this repository.** Every session leaves `docs/sessions/session_<YYMMDDhhmm>.md` and, where the host exposes it, its raw transcript under `docs/sessions/raw/<host>/` via `python scripts/save_transcript.py`. Nothing of record lives only in a vendor's home folder (Claude, Codex, Gemini, Antigravity). Enforced by: `session-log` at push; `harness-close` step 9.

### 9. Access boundaries

"Ask first" means state the exact command and target, then wait; silence is no.

- **Ask first (destructive):** deleting more than ten files or anything you did not create this session; `git reset --hard`; force-push; history rewrites; anything against a non-local database. Enforced by: convention; the host's permission prompts.
- **Ask first (external):** `git push`, pull-request creation, work-item writes, package installs, new network destinations, posting anywhere. Enforced by: convention; the host's permission prompts.
- **Never:** push to a protected branch; send secrets or personal data anywhere; edit `skills-lock.json` by hand; write into a vendor's skills cache. Enforced by: branch protection (bootstrap step 6); `skills-lock`; convention.

### 10. The working rules, mapped

| Rule | Artefact | Enforced by |
|---|---|---|
| Fix the product; tooling is its own change | `one-kind` | `--prepush` |
| Declare the surface before writing code | `Surface:` in the first commit | `surface`; `prepush_check.py` |
| A review finding outside the surface is a BACKLOG line | the plan's BACKLOG section | convention |
| Never push without a clean adversarial review of the whole diff | `Review:` trailer | `trailers` (presence); convention (honesty) |
| Never self-author a scope override | `SCOPE-OK:` and `KIND-OK:` quote the person who granted it | convention |
| Read consumers and incumbent before changing either | RULE TWO report | `prepush_check.py` |
| A claim is a defect if it is not enforced | "Enforced by:" on every rule | `rule-enforcement` |
| Never type a number a tool generated; point at the artefact | `Tests:` names the command and the output's summary line | convention |

### 11. Changing Part A

- **A change needs** a stated trigger (an incident or an idea), the three questions from the preamble answered (value, enforcement, what it displaces), a version bump of the line at the top, and a review by someone who did not write it; working solo, a `grill-me` pass. Enforced by: `agents-present` (version line); convention.

## Part B: This repository

<!-- Fill from the six bootstrap answers. Keep it short: build, run, test, layout, the handful of repo-specific "never" lines. Path-scoped detail belongs in a skill. Every factual claim about the code carries a verify: line. -->

**Project:** <project name>. **Stack:** <stack>. **Tracker:** <tracker or none>. **Sibling repos:** <none, or paths>.

- Build and run: `<command>`
- Test: `<TEST_COMMAND>`; coverage report at `<coverage report path>`
- Layout: see `docs/ARCHITECTURE.md`

<!-- bmad:context -->
<!-- /bmad:context -->
