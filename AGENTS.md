# AGENTS.md (the kit itself)

This repository is a bootstrap kit, not a bootstrapped project. `harness/` is the template that gets copied into a new repository; `BOOTSTRAP.md` is the recipe an agent follows there. Read `harness/docs/HARNESS.md` for the one-page explanation.

- To use the kit on a new project: open the empty folder in your agent and follow `BOOTSTRAP.md`. Do not run it here.
- To change the kit: edit under `harness/`, then run `python harness/scripts/harness_lint.py --selftest`, `python harness/scripts/save_transcript.py --selftest` and `python harness/scripts/prepush_check.py --self-test`; all three must print their OK line. Bump the version line in `harness/AGENTS.md` for any rule change and note it in `harness/docs/HARNESS.md` if the shape changes.
- Records of the kit's own work live in `docs/plans/` and `docs/sessions/`.
