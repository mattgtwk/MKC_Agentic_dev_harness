# Architecture map

last_reviewed: <YYYY-MM-DD>

The one living map of this repository: components, flows, boundaries and invariants. Read it before touching unfamiliar code; update it in the same change that moves structure (`harness-close` step 3). It describes this repository only. Each invariant cites the defect or decision that bought it. Factual claims carry a `verify:` line so the lint fails on the commit that makes them false.

## What this repository is

<two sentences: what it does, for whom>

## Layout

| Path | Holds | Owner doc or skill |
|---|---|---|
| `<path>` | <what lives here> | <doc or skill that explains it> |

## Flows

1. <flow name>: <entry point> -> <step> -> <step> -> <output>. Files: <paths>.

## Boundaries and invariants

- **<Invariant>.** <the statement>. Bought by: <the defect or decision>.
  <!-- add the claim's check here as an HTML comment beginning "verify:", e.g. verify: exists src/main.py -->
  <!-- verify: exists AGENTS.md -->
  <!-- verify: exists docs/adr/README.md -->
  <!-- verify: exists docs/memory/MEMORY.md -->
  <!-- verify: exists docs/sessions/README.md -->
  <!-- verify: exists scripts/harness_lint.py -->
  <!-- verify: exists scripts/save_transcript.py -->
  <!-- verify: exists .githooks/pre-commit -->
  <!-- verify: exists .githooks/pre-push -->
  <!-- verify: exists .github/workflows/harness-gates.yml -->

## Deliberately not built yet

- <thing>: add when <the trigger fires>.
