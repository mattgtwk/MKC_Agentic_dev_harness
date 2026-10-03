---
name: harness-plan
description: Use before any change larger than a one-line fix. Takes a type (feature, bugfix, refactor, hotfix) and a topic, applies the three stances in order (BMAD product manager, ponytail, grill-me), and writes a plan in a fixed shape with acceptance criteria, declared Surface, design, test plan and map/ADR decisions to docs/plans/. Invoke for "harness-plan feature <topic>", "plan this", "plan the bugfix". Stops for approval; never implements.
---

# Plan the work

Arguments: `<feature|bugfix|refactor|hotfix> <topic>`. The plan is the contract; the first commit will carry its Surface.

## NEVER

- Never write product code in this skill. Planning stops at approval.
- Never skip the test plan. Unit always; e2e named or "n/a: <reason>"; a bugfix names the regression test that goes red first.
- Never leave an abstraction, dependency or layer unjustified. One line each, or it is not built.
- Never type a timestamp. Read the clock: `date +%y%m%d%H%M` (or `Get-Date -Format yyMMddHHmm`).

## Flow

1. **Investigate first.** Read the relevant code and `docs/ARCHITECTURE.md`. Write down what you observed and what you are assuming, separately. For a bugfix: no fix is planned until one mechanism explains every observed symptom.
2. **PM stance** (load `bmad-agent-pm` for anything beyond a small story). Why does this change exist? What user-visible outcome changes, and how will it be seen to work? Write the acceptance criteria before any design.
3. **Ponytail stance** (`ponytail`). Does each part need to exist? Stdlib or platform before a dependency; an existing component before a new one; the shortest working diff. Each remaining abstraction gets its one-line justification.
4. **Grill-me stance** (`grill-me`). Mandatory when the change is irreversible, outward-facing (push, deploy, external write), touches more than about ten files, or changes a contract another component consumes. One question at a time, each with a recommended answer. Update the plan with what it found.
5. **Decide the records.** Does structure move? Then the map changes in the same change. Is a decision durable? Then an ADR, numbered next in the register.
6. **Write the plan** to `docs/plans/PLAN-<topic>-<YYMMDDhhmm>.md` in this shape:

```
# Plan (<type>): <topic>
Status: proposed <date>

Acceptance criteria: <what changes for the user and how it is verified>
Surface: <file list; nothing else may change without a BACKLOG line>
Design: <the smallest solution; each new dependency or abstraction justified in one line>
Test plan: unit <subjects>; e2e <journey or "n/a: reason">; bugfix regression test: <name, and what makes it red first>
Architecture map delta: yes/no. ADR: yes/no (<why>)
Cross-repo impact: <none, or what lands in the sibling and in what order>
Open questions: <each with a recommended answer>
BACKLOG: <defects seen outside the Surface; written down, not fixed>
```

7. **Stop.** Present the plan and wait for approval, correction, or a grilling. Then implement, and close with `harness-close`.

## When implementing (after approval)

- The first commit body carries `Surface: <the list>`.
- Bugfix: write the regression test first, run it, capture the red line, then fix, then capture the green line. Both lines go in the commit body and the session log.
- Anything found outside the Surface is a BACKLOG line in the plan file, not a change.

## Completion checklist

- [ ] Observed and assumed stated separately
- [ ] Acceptance criteria written before the design
- [ ] Every abstraction justified in one line, or removed
- [ ] Surface and test plan complete; map and ADR decisions explicit
- [ ] Plan file written with a read-the-clock stamp; approval requested
