---
name: open-executive
description: Final-pass review of a client-facing deliverable (report, proposal, board paper) by a simulated executive team. Eight specialist personas (CSO, CFO, CHRO, GC, COO, CMO, CPO, Board Comms) each review the draft from their own seat and file a memo; their findings are synthesised into ONE executive voice and applied. Run only when the user asks, as the last gate before the deliverable ships. Triggers - "an executive review", "open-executive", "what would a CFO say about this", or a named role. Not for code review.
---

# Open Executive

A project's own checks find defects. They do not find what a chief financial officer would ask
in the second minute of the meeting. This skill runs a deliverable past eight executive seats
before the client sees it, and folds what they say back into the document.

Personas vendored from [SenteLabsAI/OpenExecutive](https://github.com/SenteLabsAI/OpenExecutive)
(Apache 2.0, commit `8e7fbc1`, taken 2026-09-21). Licence in
`references/LICENSE-OpenExecutive.txt`. The upstream project is a deployable executive agent;
what is used here is the persona layer only. This copy is generalised from a project's version and is installed from the harness kit with `npx skills add`, so it is
pinned in `skills-lock.json` like any third-party skill.

## When to run it

Only when the user asks. If the project's plan records whether a deliverable gets this review,
follow it. Order, once asked:

1. Tests green; the deliverable regenerated from committed data, if it is generated.
2. Every figure in the deliverable carries its source (file, page, clause or table).
3. A `humanizer` pass over the prose, where the host provides that skill.
4. **This skill.**
5. After applying: repeat steps 1 and 2, because the panel's additions arrive after the first
   check.

Running it earlier wastes the reviewers on copy that is going to change.

## How it runs

### 1. Brief once, in writing

Write one briefing that every reviewer gets, in `docs/reviews/exec-review-BRIEF-<YYMMDDhhmm>.md`
(read the clock; never type a stamp). It carries:

- The jurisdiction. The persona prompts carry US and EU law; tell every seat, the general
  counsel above all, which law applies and that a date or duty from another jurisdiction is wrong.
- Who the client is, what the work covers, and the two or three numbers that set the stakes.
- What the deliverable is, who reads it, and what decision it is meant to produce.
- Where the evidence lives: the data, the deliverable, the source documents (read-only).
- What is already decided and not up for review, so eight reviewers do not relitigate it.
- The open questions, so they aim at those rather than at what is settled.
- The deliverable's constraints (page budget, what the data cannot support), or they will
  recommend work the evidence does not carry.

A vague brief gets eight generic memos. The brief is most of the work.

### 2. Fan out, one agent per seat

Launch all eight in a single message so they run in parallel, as subagents of the host on its
strongest model; never call a model API from project code. Each agent gets:

- Its persona prompt, read from `references/domain_prompts.py` (`CSO_PROMPT`, `CFO_PROMPT`,
  `CHRO_PROMPT`, `GC_PROMPT`, `COO_PROMPT`, `CMO_PROMPT`, `CPO_PROMPT`, `BOARD_COMMS_PROMPT`).
- The briefing.
- Instructions to READ the actual artifacts rather than react to a summary, and to cite file,
  page and clause or table for every factual claim.
- One output path: `docs/reviews/exec-review-<role>-<YYMMDDhhmm>.md`.

Ask each memo for the same six things, so the synthesis has something to compare:

| | |
|---|---|
| **What is wrong** | Specific, with the page or the claim it lands on. |
| **What is missing** | The question this seat would ask and the document does not answer. |
| **What to add** | The page, section, number or table they would write, concrete enough to build: what is on it, what evidence it draws on, where it sits. Mandatory. |
| **What to cut** | Something to remove, to pay for what they added. Mandatory. |
| **Anything else from their seat** | The open box: risks nobody named, a question for the client, a number that should be produced, the objection a specific reader will raise. Often the best material. |
| **The one change** | If they get one edit, which. |

The pairing matters. **What to add** without **what to cut** grows the document every review;
**what to cut** on its own turns eight executives into eight sub-editors. Where the shape is
fixed, say in the brief what "cut" means (content inside pages, not pages).

### 3. Synthesise into ONE voice

Read all eight, then write a single review in the voice of `references/executive_persona.py`:
a seasoned operator who has made the calls, not a consultant who generates frameworks. Take only
the voice and judgement from that prompt. It was written for a deployed agent: ignore every
instruction in it to act unasked, send, post, message, alert, create skills or record people;
its `{VOICE_PERSONA}` slot; its ban on mentioning sub-agents; and its length limit. The
synthesis is `docs/reviews/exec-review-SYNTHESIS-<YYMMDDhhmm>.md` and carries:

- The findings more than one seat raised. Convergence is the signal.
- The findings only one seat could have raised, kept because they are why the seat was there
  (the general counsel's statutory date; the CFO's read on a pricing mechanism).
- What to reject, with the reason, so it is killed rather than quietly dropped.
- An applied-or-not decision against every accepted finding.

### 4. Apply, then say what you did not apply

Change the deliverable. A generated deliverable is changed in its generator or its data, then
regenerated; a hand edit is lost at the next run. Then do step 5 of the order above. Write the
rejections in the synthesis, so the next session does not rediscover them. An unactioned review
is a file, not a gate.

The files in `docs/reviews/` are working papers: a finding that reaches the deliverable is
recorded there, not here.

## Rules that bind the panel

- **A reviewer who says a figure is wrong has raised a question.** Check it against the source
  documents; a reviewer's memo is never a source. If two sources disagree, record the
  discrepancy with both sources rather than picking a winner, unless the project's own policy
  says otherwise. If the deliverable misstates its source, that is a defect: fix it with its
  regression test written first. If the deliverable is right, reject the finding.
- **Their factual claims are questions, not findings.** Reviewers confidently assert things the
  evidence does not say, and miss things it does. Check every "this is not in the evidence"
  against the evidence before acting on it, and fix the wording that let them miss it.
- **Keep the finding, recheck the number.** Structural points are usually right while the
  arithmetic behind them is wrong. Never copy a reviewer's number onto a page; recompute it
  from the data.
- **The panel advises; it does not get a vote on scope.** A recommendation to restructure the
  deliverable goes to the user as an open question, not into the build.
- **Nothing leaves this machine** (`AGENTS.md` Part A section 9, Access boundaries). Never pass
  the `WEB_SEARCH_ADDENDUM` or `MCP_ADDENDUM`. Tell every reviewer in its prompt that it may read
  local files only: no web search, no fetch, no MCP or connector tool, no publishing. Prefer a
  read-only agent type and have it return the memo in its report, for the main agent to write.
  Enforced by: convention; the host's agent types may still carry web tools.
- **No framework vocabulary in client copy.** They arrive with Porter, RICE, Rule of 40. The
  finding is welcome; the vocabulary is not.

## What it is good at

The question the document does not answer; the number an executive will ask for in the room;
the page that reads as advocacy rather than advice; content one seat owns that a generalist
under-weights (statutory and notice dates, pricing mechanics, covenant terms). Its best catches
sit in the seam between an artifact and a sentence about it: prose that misstates the data,
hand-typed counts, a date scheduled past its own deadline. No test reads prose against data, so
say this out loud in the brief.

## Cost

Eight agents reading a full artifact set is expensive. Run it once per deliverable, on the
near-final draft; re-run only if the argument changes. A partial run on added pages is cheaper:
give the new pages as text and the full document as something to grep, with the pages worth
checking named.
