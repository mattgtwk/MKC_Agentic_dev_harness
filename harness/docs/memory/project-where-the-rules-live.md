---
name: project-where-the-rules-live
description: "Kind decides home: rules in AGENTS.md Part A, invariants in the map, procedures in skills, decisions in ADRs; memory holds pointers only"
metadata:
  type: project
---

**Fact:** A rule lives in `AGENTS.md` Part A; an invariant in `docs/ARCHITECTURE.md`; a procedure in a skill under `.agents/skills/`; a decision in `docs/adr/`; a pointer here. Memory holds nothing that can rot.

**Why:** Memory is read first, so a stale copy of a rule beats the truth. One home per fact means one place to fix.

**Authority:** AGENTS.md#Where things live
