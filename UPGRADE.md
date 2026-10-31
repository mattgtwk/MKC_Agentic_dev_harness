# UPGRADE.md: bring a bootstrapped harness up to date

You are an agent in a repository that was bootstrapped from this kit (github.com/mattgtwk/MKC_Agentic_dev_harness). Each version is a git tag, so a kit file as it was at a version is at `https://raw.githubusercontent.com/mattgtwk/MKC_Agentic_dev_harness/v<X.Y.Z>/<path>`, and the newest at `.../main/<path>`. Kit paths under `harness/` land at the repository root, so kit `harness/scripts/harness_lint.py` is your `scripts/harness_lint.py`.

## Procedure

1. Read line 3 of `AGENTS.md`: `harness-constitution vX.Y.Z`. That is your version. A `-local.N` suffix marks a project's own Part A change: your kit version is the part before it. A project may also have bumped it without a suffix, before v1.3.0 asked for one, so confirm the version: at least one file your version's own entry re-copies should match the kit's at that tag and not at the tag before it (v1.0.0 needs no check). If it is not one of the versions below, or no such file matches, ask the person which kit version it came from. No version line means the repository was not bootstrapped from this kit: stop and ask the person.
2. Take every entry below that is newer than your version, oldest first. Tell the person what each one changes and skip one marked *optional* unless its condition holds.
3. Apply each entry's steps. **Re-copy** means: compare your file with the kit's file at your version. If they are the same, replace yours with the kit's newest. If they differ, the project changed it: merge by hand, keeping the project's change. Re-copy each file once per run, even when several entries name it. If the file at your version's tag does not fetch, stop and ask the person; never compare against `main` instead, which would read a project's change as the kit's.
4. Last, Part A of `AGENTS.md` (everything above `## Part B: This repository`). Compare your Part A with the kit's at your version (kit `harness/AGENTS.md`, not the kit's root `AGENTS.md`) and show the person every difference: bootstrap lets a project delete Part A rules, and Part A section 11 lets it amend them. Then replace the span with the kit's newest Part A, carrying over each local change the person keeps. That also sets the version line; if any local change was kept, add `-local.1` to it.
5. Never touch Part B, `docs/memory/` pages, ADRs, sessions or plans, except where an entry says so. A memory page marked `reviewed: true` is changed only with the person's agreement.
6. Opt-in kit skills (`skills/` in the kit) are not versioned with the constitution. If the person wants skills current, run `npx skills update`; it updates every pinned skill, BMAD included, and rewrites `skills-lock.json`, so run it before step 7.
7. Run each entry's Check, then `python scripts/harness_lint.py --doctor --relink` and `python scripts/harness_lint.py` (0 errors).
8. In the session log, list each entry as applied or skipped, with the reason. Branch, commit and push as for any change; it is a tooling change if a script was re-copied.

## v1.3.0 (2026-10-24)

- **Rule.** A project's own Part A change bumps the version line with a `-local.N` suffix (`v1.3.0-local.1`), so this file can tell it from a kit version. Enforced by convention; `agents-present` accepts the suffix. Part A section 11 changes, which step 4 carries in.
- **Procedure.** A promoted lesson names its evidence, and a lesson whose cause was not isolated is recorded as `- none: confounded: <lesson>`. Why: the push gate checked that a lesson reached its owner, not that it was true. Enforced by convention; the gate does not read the evidence line. Re-copy `.agents/skills/harness-close/SKILL.md` and `docs/sessions/README.md`.
- **Doc.** A memory `description:` names the situation an agent needs the page in. Re-copy `docs/memory/README.md`.
- **Doc.** A code knowledge graph (graphify) is an upgrade path with a trigger; the in-loop hook vs git/CI trade-off is stated; upgrades point here. Re-copy `docs/HARNESS.md`.
- **Optional, projects with a user interface.** The kit's design rulebook: `npx skills add mattgtwk/MKC_Agentic_dev_harness -a codex -s interfaces-design-bible -y`.
- **Optional, projects with client-facing deliverables.** The executive-panel review: `npx skills add mattgtwk/MKC_Agentic_dev_harness -a codex -s open-executive -y`. A project that already carries a hand-copied `open-executive` folder, absent from `skills-lock.json`, asks the person: keep it as it is (unpinned), or move its project-specific rules (jurisdiction, file paths, review order) into Part B, delete the folder and install this one.
- Check: step 6 of the harness-close skill mentions `confounded`; `skills-lock.json` lists each optional skill installed.

## v1.2.0 (2026-10-07)

- **Rule.** A memory page's `description:` is 150 characters or fewer, because it is the `MEMORY.md` index line. Re-copy `scripts/harness_lint.py` and `docs/memory/README.md`. This entry edits records: shorten any longer description, then `python scripts/harness_lint.py --rebuild-index`. The lint has no exemption for `reviewed: true` pages, so agree the shorter wording of each one with the person.
- Check: the lint reports `memory-schema` PASS.

## v1.1.0 (2026-10-04)

- **Rule.** Coverage at close: `--ratchet` keeps line and branch floors and holds the executable lines a change adds to `diff_min_pct`; `harness-close` step 2 runs it.
- **Rule.** The push check `promotions`: every pushed session log has `## Lessons promoted`, and each named owner file is in the change.
- Re-copy `scripts/harness_lint.py`, `.agents/skills/harness-close/SKILL.md`, `docs/sessions/README.md` and `docs/HARNESS.md`. Add `"branch_pct": null` and `"diff_min_pct": 90` to `coverage_baseline.json` if they are missing, keeping your own values.
- Check: `python scripts/harness_lint.py --selftest` prints SELFTEST-OK with `HARNESS_BASE` unset or `origin/main` (any other value can fail), and `--ratchet` runs.

## v1.0.0 (2026-10-03)

The first release.
