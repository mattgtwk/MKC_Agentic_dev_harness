# NEXT-STEPS

Rewritten at every `harness-close`. Assume the next session knows nothing that is not written here. Read this after `docs/memory/MEMORY.md` and `docs/ARCHITECTURE.md`. Plans in `docs/plans/` are dated snapshots of intent; this file is the current state. If they disagree, this file is right.

## What is true now (measured <YYYY-MM-DD>)

- <one line per fact, each with the command or file that proves it>

## Step 0: re-verify before acting on anything above

1. `python scripts/harness_lint.py`
2. `git status --short && git log --oneline -3`
3. <the command that re-measures the most important number above>

## Open threads

- <thread>: <state>; <what the next session needs to know>

## Traps, in the order they will bite

1. <trap, and the way around it>

## Kickoff text (paste into the next session)

> Read NEXT-STEPS.md in full, then AGENTS.md, then docs/memory/MEMORY.md, then docs/ARCHITECTURE.md. Run harness-open. Then: <the one thing to do first>.
