# AGENTS.md (the kit itself)

This repository is a bootstrap kit, not a bootstrapped project. `harness/` is the template that gets copied into a new repository; `BOOTSTRAP.md` is the recipe an agent follows there. Read `harness/docs/HARNESS.md` for the one-page explanation.

- To use the kit on a new project, or to upgrade one it bootstrapped: open the folder in your agent and follow `BOOTSTRAP.md`; it sends a bootstrapped repository to `UPGRADE.md`. Do not run it here.
- To change the kit: edit under `harness/`, then run `python harness/scripts/harness_lint.py --selftest`, `python harness/scripts/save_transcript.py --selftest` and `python harness/scripts/prepush_check.py --self-test`; all three must print their OK line. Bump the version line in `harness/AGENTS.md` for any rule change, add its entry at the top of `UPGRADE.md` (what to re-copy or edit, and a check), tag the release commit on `main` `vX.Y.Z` (UPGRADE.md reads kit files at the project's tag), and note it in `harness/docs/HARNESS.md` if the shape changes. Nothing checks the entry or the tag; both are convention.
- `skills/` holds opt-in skills that bootstrapped projects install with `npx skills add mattgtwk/MKC_Agentic_dev_harness -a codex -s <name> -y`; they are not copied with `harness/`. No selftest covers them: keep each `SKILL.md` under 15 KB with `name` equal to its folder, by hand.
- Records of the kit's own work live in `docs/plans/` and `docs/sessions/`.
