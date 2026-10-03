---
name: harness-close
description: Use at the end of every session that changed anything, and whenever asked to "update docs", "close", "close out", "wrap up" or "harness-close". Proves the work (self-review gate, tests, verify and stop), records it (session log, raw transcript, ADRs, architecture map, NEXT-STEPS, memory), promotes every lesson to its owner file, runs the lint, and prepares the commit with its Surface, Tests and Review trailers. Push only on the user's go.
---

# Close the session

Twelve steps, in order. Skipping one means the branch stays open. "Update docs" means this whole routine, not editing a document.

## NEVER

- Never claim a suite is green that you did not run after the last edit. Paste its summary line.
- Never tick a promotion because you named the owner. Tick it when the owner file changed.
- Never restate a rule in memory. Point at the owner.
- Never push without the user's go. Prepare the commit; stop.

## Flow

1. **Self-review gate**, six lines written into the session: trust boundaries; completeness against ground truth; verification honesty (mutate the code and watch the relevant test go red, then revert); regression risk (the full affected suite); output integrity (the artefact produced is the artefact claimed); failure modes (does it fail loudly).
2. **Verify and stop.** Run the smallest proof set that shows acceptance: the affected tests, then the full suite with coverage if anything shared changed. Record the command and its summary line. Then `python scripts/harness_lint.py --ratchet`: the line and branch floors must hold and the lines this change added must meet `diff_min_pct`; an ERROR here means more tests, not a lower floor. No enhancements after pass.
3. **Architecture map.** `docs/ARCHITECTURE.md` matches reality: every component, flow or invariant this work added or moved is on it. If you surveyed it, bump `last_reviewed`.
4. **NEXT-STEPS.md** rewritten for a reader who knows nothing: what is true now (measured, with the date), Step 0 re-verification commands, open threads, traps in the order they will bite, and a paste-ready kickoff text.
5. **Decisions.** Every decision taken this session is an ADR (next number, register row, Consequences name the cost) or a line in the work item. None lives only in chat.
6. **Wave-close promotion.** List every lesson. Classify each: rule (Part A, with trigger and displacement), repo fact (Part B), invariant (map), procedure (a skill, if it passes the twice/thirty-minutes/not-obvious gate; otherwise a note in an existing skill), decision (ADR), pointer (memory page). Change the owner file. Write the list into the session log under `## Lessons promoted`, one line each as `- <kind> -> <owner path>`, or `- none: <reason>` when nothing outlives the session. The push gate refuses a named owner file that is not in the change.
7. **Memory.** Promote anything durable from the host's auto-memory into `docs/memory/` as Fact/Why/Authority pages under 800 bytes; revise existing pages in place; then `python scripts/harness_lint.py --rebuild-index`.
8. **Session log.** Write `docs/sessions/session_<YYMMDDhhmm>.md` (read the clock) in full sentences: summary of actions, decisions, commands and tests run with their summary lines, gates and their outcomes, `## Lessons promoted` (from step 6), next steps.
9. **Transcript.** `python scripts/save_transcript.py`. Confirm the copied files appear under `docs/sessions/raw/<host>/`.
10. **Lint.** `python scripts/harness_lint.py` reports 0 errors. Fix, do not suppress.
11. **Plan file.** The plan from `harness-plan` gets its header: `Status: done <date>` plus departures from the plan as written.
12. **Commit.** Stage everything that belongs to this change. The message body carries `Surface: <files>`, `Tests: <command> -> <summary line>`, `Review: <outcome and rounds>`. Run `python scripts/harness_lint.py --prepush` and `python scripts/prepush_check.py` by hand to see what the push hook will say. Then stop: push only on the user's go.

## Completion checklist

- [ ] Gate written; tests run after the last edit and quoted
- [ ] Map, NEXT-STEPS, ADRs, memory, session log, transcript all updated in the same change
- [ ] Every lesson's owner file changed
- [ ] Lint 0 errors; prepush checks clean
- [ ] Commit prepared with Surface, Tests, Review; awaiting the go
