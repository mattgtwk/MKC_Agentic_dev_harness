---
name: harness-open
description: Use at the start of every session in this repository, before any other work. Reads the memory index, the architecture map and NEXT-STEPS.md, runs the lint, and prints where you are and what the next session was told. Invoke for "harness-open", "open the session", "orient", "where were we". Never blocks; it reports.
---

# Open the session

Orient in under a minute. Read, do not act, until the banner is printed.

## Flow

1. Read `docs/memory/MEMORY.md`. Open any page whose index line is relevant to the work you expect.
2. Read `docs/ARCHITECTURE.md` (the map; note its `last_reviewed` date).
3. Read `NEXT-STEPS.md`. Run its **Step 0** list before trusting any number in it; the previous session wrote it for you.
4. Run `git status --short` and `git branch --show-current`.
5. Run `python scripts/harness_lint.py`. Note the `context-budget` figure and any WARN.
6. Confirm the voice: `caveman` is on by default; full sentences for anything persisted.

## Print the banner

```
[harness] <repo> on <branch>; <n> uncommitted file(s)
constitution: <version line from AGENTS.md>
map: last_reviewed <date>
next-steps: <the one-line "what is true now">
lint: <errors> error(s), <warnings> warning(s); context <bytes> of 32768
loop: harness-plan <type> <topic> -> implement -> harness-close
```

## Then

Pick up the first open thread in `NEXT-STEPS.md`, or ask what the work item is. For anything larger than a one-line fix, run `harness-plan`.

## Completion checklist

- [ ] Memory index, map and NEXT-STEPS read; Step 0 run
- [ ] Lint run; its output quoted, not summarised from memory
- [ ] Banner printed
