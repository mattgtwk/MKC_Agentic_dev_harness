# BOOTSTRAP: stand up the agentic development harness in an empty folder

You are a coding agent (Claude Code, Codex, Antigravity, Cursor, Copilot, Gemini CLI or another) working with a person in a new project folder, empty or holding files not yet under git. This file is all you need: it names where the kit lives and how to get every tool, starting from a machine with nothing installed. Follow the steps in order. Each step ends with a check; do not move on until it passes. Ask the person only where a step says to. When a check fails or your host refuses a command, find the symptom in **When a step fails** at the end, tell the person what happened, offer the options listed there, and do what they choose. Never reword a refused command to get it past your host: steps 4 and 6 install third-party code and arm the guards that police you, and a host that refuses them is right to. Everything you create is committed to the project; nothing of record is left in your vendor's home folder.

**The kit:** https://github.com/mattgtwk/MKC_Agentic_dev_harness (public). Its `harness/` folder mirrors the target repository root; `harness/docs/HARNESS.md` explains the result in one page. This file is `BOOTSTRAP.md` at the root of that repository; the raw URL is https://raw.githubusercontent.com/mattgtwk/MKC_Agentic_dev_harness/main/BOOTSTRAP.md.

## 0. Environment: check, then install only what is missing

Work in the shell your IDE gives you (PowerShell on Windows; bash or zsh elsewhere). Find the operating system first: `$env:OS` prints `Windows_NT` on Windows; `uname -s` prints `Darwin` or `Linux`. Then for each row, run the check; if it fails, run the install for that OS, open a new shell so PATH updates, and run the check again. Do not continue with a tool missing. Do not install anything not in this table without asking the person.

**Package manager first.** Windows: `winget --version`; if absent, install "App Installer" from the Microsoft Store, or skip winget and use the direct installers in the last column. macOS: `brew --version`; if absent, `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`. Debian/Ubuntu: `apt-get` is present; run `sudo apt-get update` once.

| Tool | Check | Windows (winget) | macOS (brew) | Debian/Ubuntu (apt) | No package manager |
|---|---|---|---|---|---|
| git | `git --version` | `winget install --id Git.Git -e` | `brew install git` | `sudo apt-get install -y git` | installer from https://git-scm.com/downloads |
| GitHub CLI | `gh --version` | `winget install --id GitHub.cli -e` | `brew install gh` | `(type -p wget >/dev/null \|\| sudo apt-get install -y wget) && sudo mkdir -p -m 755 /etc/apt/keyrings && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \| sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \| sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null && sudo apt-get update && sudo apt-get install -y gh` | MSI, pkg or tarball from https://github.com/cli/cli/releases/latest |
| Node 20+ (gives npm and npx) | `node --version` | `winget install --id OpenJS.NodeJS.LTS -e` | `brew install node` | `sudo apt-get install -y nodejs npm` (if that gives Node below 20, use the installer) | LTS installer from https://nodejs.org |
| uv (installs Python and runs BMAD's scripts) | `uv --version` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | the same one-line installers; they need no package manager |
| Python 3.11+ | `python --version` (Windows: `py -3 --version`) | `uv python install 3.12` then `winget install --id Python.Python.3.12 -e` if a `python` command is still missing | `uv python install 3.12` or `brew install python` | `sudo apt-get install -y python3` | `uv python install 3.12`, or the installer from https://www.python.org/downloads (tick "Add to PATH") |

Then: `gh auth login` (choose GitHub.com, HTTPS, and let the person complete the browser step), and confirm with `gh auth status`. On Windows also run `git config --global core.longpaths true`, and keep the project under a short root such as `D:\src\<name>`. If `python` on Windows opens the Microsoft Store, use `py -3`; the hooks already try `py -3` first.

Check: every row's check command prints a version; `gh auth status` shows a logged-in account.

## 1. Repository and remote

Ask the person: repository name, owner (their account or an organisation), private or public. Tell them before they choose: on a free GitHub plan a private repository cannot make the CI gate binding (step 6) and spends limited Actions minutes; public, or a paid plan, has neither limit.

```
git init -b main
gh repo create <owner>/<name> --private --source . --remote origin
git commit --allow-empty -m "chore: empty root"
git push -u origin main
```

The empty first push exists because the push guard armed in step 6 needs a merge base with `origin/main`.

If the folder already holds files (art, documents, an old codebase), ask the person whether to commit them now as a second commit and push it. Anything committed before step 6 is never judged by the push guard; anything added later is.

Check: `git ls-remote origin main` prints a sha.

## 2. Fetch and copy the kit

Clone the kit beside the project and copy its `harness/` contents, including the dotfiles, into the repository root; then remove the clone.

bash or zsh:
```
git clone --depth 1 https://github.com/mattgtwk/MKC_Agentic_dev_harness ../_harness_kit
cp -a ../_harness_kit/harness/. .
rm -rf ../_harness_kit
```

PowerShell:
```
git clone --depth 1 https://github.com/mattgtwk/MKC_Agentic_dev_harness ..\_harness_kit
Copy-Item -Path ..\_harness_kit\harness\* -Destination . -Recurse -Force
Remove-Item ..\_harness_kit -Recurse -Force
```

(`Copy-Item` with `*` includes dotfiles. If git is somehow unavailable, download https://github.com/mattgtwk/MKC_Agentic_dev_harness/archive/refs/heads/main.zip and copy its `harness/` folder the same way.) Then:

```
python scripts/harness_lint.py --selftest
python scripts/save_transcript.py --selftest
python scripts/prepush_check.py --self-test
```

Check: `ls -a` (or `Get-ChildItem -Force`) shows `.agents`, `.githooks`, `.github`, `.gitignore`, `.gitattributes`, `AGENTS.md`; all three selftests print their OK line. If one fails on this machine, stop and report; do not edit the scripts.

## 3. Write AGENTS.md

Ask the person seven questions: project name; stack; the test command, and that it can write a Cobertura `coverage.xml` (pytest: `--cov --cov-branch --cov-report=xml`; Jest: `--coverage --coverageReporters=cobertura`; .NET: coverlet with the cobertura format); the coverage report path; the work tracker, or none; sibling repositories, or none; what the repository will hold besides source code (images, documents, art, 3D models, data), by file extension, or none. Fill every `<placeholder>` in `AGENTS.md` Part B, `NEXT-STEPS.md`, `docs/ARCHITECTURE.md` (set `last_reviewed` to today), `docs/adr/0001-adopt-harness.md` and `docs/adr/README.md`. Read Part A once in full. Delete any Part A rule the person does not want and cannot name an enforcement for; keep "Enforced by: convention" only where it is true. Do not add rules yet.

Check: `python scripts/harness_lint.py` shows `agents-present`, `agents-size`, `rule-enforcement`, `adr-refs`, `adapter-thin` and `context-budget` as PASS. Other checks may still fail; the next steps fix them.

## 4. Install the four skill sets, pinned

Install for **one** agent only, Codex, whose folder is `.agents/skills/`. Do this even if you are not Codex: every agent reads that folder directly or through the junctions created in step 5, and one folder keeps `skills-lock.json` honest. `-a codex -y` makes the installer non-interactive; if it still asks, answer Codex and yes. If your host refuses them, see **When a step fails**.

```
npx skills add bmad-code-org/BMAD-METHOD -a codex -s '*' -y
npx skills add JuliusBrussee/caveman -a codex -s caveman -s caveman-compress -y
npx skills add DietrichGebert/ponytail -a codex -s ponytail -y
npx skills add mattpocock/skills -a codex -s grill-me -s grilling -y
```

Keep the quotes around `'*'`: an unquoted wildcard is glob-expanded by the shell and the installer silently installs nothing. Then run BMAD's setup non-interactively (it is the `bmad` skill's own script; it asks nothing when the installed modules have no pending questions, and it never touches `_bmad/custom/`):

```
uv run .agents/skills/bmad/scripts/setup.py --project-root . --skill .agents/skills/bmad --root .agents/skills
uv run .agents/skills/bmad/scripts/setup.py --project-root . --skill .agents/skills/bmad --root .agents/skills --status
```

If the status JSON lists `pending_questions`, answer them by invoking the `bmad` skill and asking it to run setup; decline any offer to update skills during bootstrap. Then `python scripts/harness_lint.py --doctor` confirms every key in `_bmad/custom/*.toml` exists in the installed `customize.toml` files. If a name differs, edit the override to the installed name and say so in the session log.

Check: `git status --porcelain` lists only `_bmad/`, `.agents/skills/*` and `skills-lock.json` as new, and BMAD's own resolver shows the constitution in the PM persona:

```
uv run _bmad/scripts/resolve_customization.py --skill .agents/skills/bmad-agent-pm --project-root . --key agent
```

Its `persistent_facts` must list `file:{project-root}/AGENTS.md` and its `principles` must include the four from the override.

## 5. Make the skills visible to every agent

```
python scripts/harness_lint.py --doctor --relink
```

This creates `.claude/skills` (Claude Code) and `.agent/skills` (Antigravity IDE) as gitignored junctions to `.agents/skills/`. On Windows that uses `mklink /J` and needs no elevation. Codex, Cursor, Copilot and Gemini CLI read `.agents/skills/` directly.

Check: `--doctor` prints no ERROR other than `core.hooksPath` (armed next). Type `/caveman` or invoke the `caveman` skill: the reply answers first with no preamble.

## 6. Arm enforcement

Start only once step 5's check passes: the hooks run the lint, and while it fails every commit is refused.

```
git config core.hooksPath .githooks
```

Edit `.github/workflows/harness-gates.yml`: replace `<TEST_COMMAND>`. Edit `scripts/prepush_check.py`: adjust the `SKIP` regex so tests, docs, generated files and every extension from question seven are not counted as production code (for example add `|\.(png|jpe?g|pdf|pptx|stl|3mf)$`); leave `BASE` unless the base branch is not `origin/main`. Then make the gate binding, the one manual step:

```
gh api -X PUT repos/<owner>/<name>/branches/main/protection --input - <<'EOF'
{"required_status_checks":{"strict":true,"contexts":["gates"]},"enforce_admins":true,"required_pull_request_reviews":null,"restrictions":null}
EOF
```

(PowerShell has no heredoc; pipe the JSON instead: `'{...same JSON...}' | gh api -X PUT repos/<owner>/<name>/branches/main/protection --input -`. Never use `-f`: it sends `"true"` as a string and GitHub answers 422 "is not a boolean".)

Check: create `docs/memory/x.md` with a 900-byte body and try to commit: the commit is refused with `memory-schema`. Delete the file. Make a two-commit branch whose second commit touches a production file not in the first: `git push` is refused by RULE ONE. Delete the branch.

## 7. Project context from BMAD

Run the `bmad-project-context` skill with intent **adopt** (the repository already has instructions worth keeping). Give it `AGENTS.md` as the governance document. Accept its fenced `<!-- bmad:context -->` block into Part B; decline its offer to edit `CLAUDE.md` (the adapter already imports AGENTS.md).

Check: `python scripts/harness_lint.py` shows `agents-size` and `context-budget` PASS.

## 8. First records

Write the first `docs/sessions/session_<YYMMDDhhmm>.md` (read the clock; never type a stamp) describing this bootstrap, with its `## Lessons promoted` section (`- none: bootstrap` is acceptable). Run `python scripts/harness_lint.py --rebuild-index`. Fill `NEXT-STEPS.md` with the measured state.

Check: `python scripts/harness_lint.py` reports 0 errors.

## 9. Prove it

Run the loop once on a trivial change, exactly as a real session would:

1. `harness-open`.
2. `harness-plan feature <something small>`; approve.
3. Make the change.
4. `harness-close` (it runs the tests, `--ratchet`, and `save_transcript.py`).
5. Commit with the body `Surface: <files>`, `Tests: <command> -> <summary line>`, `Review: clean after 1 round`.
6. Push on the person's go. After CI is green with a coverage report: `python scripts/harness_lint.py --ratchet --update-baseline` sets the line and branch floors; commit `coverage_baseline.json`.

`main` is protected, so push a branch and open a pull request (`gh pr create`); merge when `gates` is green.

Check: `docs/sessions/raw/<your host>/` holds this session's transcript; CI shows `gates` green on the pull request. A bootstrap that ends without this proof is not done.

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

## When a step fails

Tell the person the symptom and its cause in a sentence, offer the options, and do what they choose. Note the choice in the session log.

| Step | Symptom | Cause | Options to offer |
|---|---|---|---|
| any | Your host refuses a command as untrusted code or tampering (Claude Code auto mode does this for steps 4 and 6) | Installing third-party code and arming the guards that police you need the person's approval | (a) They press Shift+Tab to leave auto mode, and you rerun so each command comes up as a permission prompt. (b) They type it themselves with a `!` prefix in Claude Code. (c) They run it in their own terminal. Never reword the command to get past the host. |
| 0 | `python` opens the Microsoft Store | Windows app alias | Use `py -3`. |
| 2 | Deleting the kit clone is refused | Deleting outside the project | (a) Clone into your scratch or temp folder instead and leave it. (b) The person deletes `../_harness_kit`. |
| 2 | A selftest fails | This machine differs from what the scripts expect | Stop and report the output to the person; do not edit the scripts. |
| 4 | The installer installs nothing | Unquoted `*` was glob-expanded | Quote it: `'*'`. |
| 6 | Every commit is refused after arming | The lint still fails (usually skills missing) | (a) Finish steps 4 and 5 first. (b) `git config --unset core.hooksPath` until they pass, then arm again. |
| 6 | `gh api` answers 422 "is not a boolean" | `-f` sends strings | Use the heredoc, or the PowerShell pipe one-liner. |
| 6 | `gh api` refuses with a plan or upgrade message | Free private repositories cannot enforce branch protection | (a) Make the repository public. (b) Upgrade to GitHub Pro or Team. (c) Leave the gate advisory: CI still runs, but merging is not blocked; record that in `NEXT-STEPS.md`. |
| 6, later | `git push` refused by RULE ONE for an image, document or model file | Its extension is not in `SKIP` | Add the extension to `SKIP` in `scripts/prepush_check.py` and commit that alone, with the person's approval. |
| 9 | No CI run appears within a few minutes (`gh run list` empty) | Actions is not starting jobs: minutes or spending limit on a private repository | (a) The person checks Settings > Billing (`gh auth refresh -h github.com -s user` lets you read it). (b) Make the repository public. Do not change the workflow first. |
