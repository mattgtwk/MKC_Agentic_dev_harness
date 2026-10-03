# BOOTSTRAP: stand up the agentic development harness in an empty folder

You are a coding agent (Claude Code, Codex, Antigravity, Cursor, Copilot, Gemini CLI or another) working with a person in a new, empty project folder. Follow these steps in order. Each step ends with a check; do not move on until the check passes. Ask the person only where a step says to. Everything you create is committed to the project; nothing of record is left in your vendor's home folder.

The kit is this repository: `harness/` mirrors the target repository root. `docs/HARNESS.md` inside it explains the result in one page; read it first if you have not.

## 0. Environment: check, then install only what is missing

For each tool, run the check. If it fails, run the install command for the operating system, open a new shell so PATH updates, and run the check again. Do not continue with a tool missing. Do not install anything not in this table without asking.

| Tool | Check | Windows (winget) | macOS (Homebrew) | Debian/Ubuntu |
|---|---|---|---|---|
| git | `git --version` | `winget install --id Git.Git -e` | `brew install git` | `sudo apt-get install -y git` |
| GitHub CLI | `gh --version` then `gh auth status` | `winget install --id GitHub.cli -e` | `brew install gh` | follow cli.github.com/manual/installation |
| Node 20+ (gives npm and npx) | `node --version` | `winget install --id OpenJS.NodeJS.LTS -e` | `brew install node` | `sudo apt-get install -y nodejs npm` |
| Python 3.11+ | `python --version` (Windows: `py -3 --version`) | `winget install --id Python.Python.3.12 -e` | `brew install python` | `sudo apt-get install -y python3` |
| uv (BMAD's script runner) | `uv --version` | `winget install --id astral-sh.uv -e` | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

Then: `gh auth login` if `gh auth status` is not logged in (the person completes the browser step). On Windows: `git config --global core.longpaths true`, and keep the project under a short root such as `D:\src\<name>`. Homebrew missing on macOS: install it from brew.sh first. winget missing on Windows: install "App Installer" from the Microsoft Store.

Check: every row's check command prints a version; `gh auth status` shows a logged-in account.

## 1. Repository and remote

```
git init -b main
gh repo create <owner>/<name> --private --source . --remote origin   # ask the person: name, owner, private or public
git commit --allow-empty -m "chore: empty root"
git push -u origin main
```

The empty first push exists because the push guard installed in step 6 needs a merge base with `origin/main`.

Check: `git ls-remote origin main` prints a sha.

## 2. Copy the kit

Copy everything under this kit's `harness/` folder into the repository root, including dotfiles (`.agents/`, `.githooks/`, `.github/`, `.gitignore`, `.gitattributes`). Then:

```
python scripts/harness_lint.py --selftest
python scripts/save_transcript.py --selftest
python scripts/prepush_check.py --self-test
```

Check: all three print their OK line. If one fails on this machine, stop and report; do not edit the scripts.

## 3. Write AGENTS.md

Ask the person six questions: project name; stack; the test command (and that it can write a Cobertura `coverage.xml`); the coverage report path; the work tracker, or none; sibling repositories, or none. Fill every `<placeholder>` in `AGENTS.md` Part B, `NEXT-STEPS.md`, `docs/ARCHITECTURE.md` (set `last_reviewed` to today), `docs/adr/0001-adopt-harness.md` and `docs/adr/README.md`. Read Part A once in full. Delete any Part A rule the person does not want and cannot name an enforcement for; keep "Enforced by: convention" only where it is true. Do not add rules yet.

Check: `python scripts/harness_lint.py` shows `agents-present`, `agents-size`, `rule-enforcement`, `adr-refs`, `adapter-thin` and `context-budget` as PASS. Other checks may still fail; they are fixed by the next steps.

## 4. Install the four skill sets, pinned

Install for **one** agent only, Codex, whose folder is `.agents/skills/`. Do this even if you are not Codex: every agent reads that folder directly or through the junctions created in step 5, and one folder keeps `skills-lock.json` honest. `-a codex -y` makes the installer non-interactive; if it still asks, answer Codex and yes.

```
npx skills add bmad-code-org/BMAD-METHOD -a codex -s '*' -y
npx skills add JuliusBrussee/caveman -a codex -s caveman -s caveman-compress -y
npx skills add DietrichGebert/ponytail -a codex -s ponytail -y
npx skills add mattpocock/skills -a codex -s grill-me -s grilling -y
```

Then invoke the `bmad` skill and ask it to run setup (it runs its own scripts with `uv run`; answer its configuration questions; if it offers to update skills to a newer version, decline during bootstrap), then ask it for status. Open `.agents/skills/bmad-agent-pm/customize.toml` and confirm the field names used by `_bmad/custom/*.toml` exist there (`persistent_facts`, `principles`, `activation_steps_prepend`; for workflows `on_complete`, a string). `python scripts/harness_lint.py --doctor` checks the same thing. If a name differs, edit the override to the installed name and say so in the session log.

Check: `git status --porcelain` lists only `_bmad/`, `_bmad-output/`, `.agents/skills/*` and `skills-lock.json` as new. Activate the PM persona (type `bmad-agent-pm`); it reads AGENTS.md, the map and the memory index before greeting.

## 5. Make the skills visible to every agent

```
python scripts/harness_lint.py --doctor --relink
```

This creates `.claude/skills` (Claude Code) and `.agent/skills` (Antigravity IDE) as gitignored junctions to `.agents/skills/`. On Windows that uses `mklink /J` and needs no elevation. Codex, Cursor, Copilot and Gemini CLI read `.agents/skills/` directly.

Check: `--doctor` prints no ERROR except a missing `_bmad/custom` key, which step 4 resolved. Type `/caveman` (or invoke the `caveman` skill): the reply answers first with no preamble.

## 6. Arm enforcement

```
git config core.hooksPath .githooks
```

Edit `.github/workflows/harness-gates.yml`: replace `<TEST_COMMAND>`. Edit `scripts/prepush_check.py`: adjust the `SKIP` regex so tests, docs and generated files in this layout are not counted as production code; leave `BASE` unless the base branch is not `origin/main`. Then make the gate binding, the one manual step:

```
gh api -X PUT repos/<owner>/<name>/branches/main/protection -f required_status_checks[strict]=true -f required_status_checks[contexts][]=gates -f enforce_admins=true -f required_pull_request_reviews= -f restrictions=
```

(If the API shape rejects a field, set branch protection in the repository settings UI: require the `gates` status check on `main`.)

Check: create `docs/memory/x.md` with a 900-byte body and try to commit: the commit is refused with `memory-schema`. Delete the file. Make a two-commit branch whose second commit touches a production file not in the first: `git push` is refused by RULE ONE. Reset the branch.

## 7. Project context from BMAD

Run the `bmad-project-context` skill with intent **adopt** (the repository already has instructions worth keeping). Give it `AGENTS.md` as the governance document. Accept its fenced `<!-- bmad:context -->` block into Part B; decline its offer to edit `CLAUDE.md` (the adapter already imports AGENTS.md).

Check: `python scripts/harness_lint.py` shows `agents-size` and `context-budget` PASS.

## 8. First records

Write the first `docs/sessions/session_<YYMMDDhhmm>.md` (read the clock; never type a stamp) describing this bootstrap. Run `python scripts/harness_lint.py --rebuild-index`. Fill `NEXT-STEPS.md` with the measured state.

Check: `python scripts/harness_lint.py` reports 0 errors.

## 9. Prove it

Run the loop once on a trivial change, exactly as a real session would:

1. `harness-open`.
2. `harness-plan feature <something small>`; approve.
3. Make the change.
4. `harness-close` (it runs `save_transcript.py`).
5. Commit with the body `Surface: <files>`, `Tests: <command> -> <summary line>`, `Review: clean after 1 round`.
6. `git push` on the person's go. After CI is green with a coverage report: `python scripts/harness_lint.py --ratchet --update-baseline` and commit `coverage_baseline.json`.

Check: `docs/sessions/raw/<your host>/` holds this session's transcript; CI shows `gates` green on the push. A bootstrap that ends without this proof is not done.

## 10. Optional, token side (say which you did in the session log)

- `caveman-compress` on `NEXT-STEPS.md` and memory pages only, never on `AGENTS.md`; run the lint after.
- The caveman proxy, per machine, for input-side compression of logs, JSON and diffs: `npm install -g @caveman-ai/cli`, `caveman setup --install`, `caveman start`. Its own numbers: 33.2% fewer input tokens over 54 runs; the voice alone about 3% of output.
- A Claude Code `SessionStart` hook that prints `cat docs/memory/MEMORY.md NEXT-STEPS.md` is a convenience; the gates above are the guarantee.

## Fresh clone of a bootstrapped repository

```
python scripts/harness_lint.py --doctor --relink
git config core.hooksPath .githooks
npx skills experimental_install     # restores .agents/skills from skills-lock.json
```

## What you must not do

Do not create a `CONSTITUTION.md`, a long `CLAUDE.md`, or rules in any vendor file: four of the six agents never read them. Do not junction your vendor's auto-memory folder into `docs/memory/`; promote by hand at close. Do not edit `skills-lock.json` or anything under `.agents/skills/` that was installed. Do not skip the proof.
