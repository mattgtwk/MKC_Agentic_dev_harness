---
name: interfaces-design-bible
description: Use when building, changing or reviewing a user interface - components, CSS, layout, motion and transitions, colour and tokens, typography, dark mode, accessibility (focus, keyboard, hit areas, forms), or interface copy such as labels, errors and empty states. Applies the interface-craft rulebook in references/bible.md, with exact values and a ranked review.
---

# Interfaces design bible

The rules and numbers live in `references/bible.md`, by Angus Hervey (Oct 2026), compiled from Jakub Krehel's Interfaces magazine, cheat sheet and skills, with each rule credited to its source issue, and published in this kit with permission. This file says how to apply it.

## Before you change a topic, read its section

| You are touching | Read in `references/bible.md` |
|---|---|
| Any value (radius, duration, size, contrast, hit area) | `## Numbers at a glance`, then `### Where his sources disagree` |
| Radius, alignment, shadows, borders, icons, image outlines | `## Surfaces and UI polish` |
| Animation, transitions, hover and press states | `## Motion` |
| Fonts, scale, line length, wrapping, inputs | `## Typography` |
| Palettes, tokens, OKLCH, gradients, dark mode | `## Colour` |
| Grouping, spacing between controls, scrolling, breakpoints | `## Layout` |
| Focus, keyboard, ARIA, reduced motion, forms, zoom | `## Accessibility` |
| Labels, errors, empty states, voice | `## Interface writing` |
| A review of a branch or a component | `## Review process` |

## Two kinds of rule

- **Exact values** (the icon swap recipe, the image outline colour, the shadow-as-border layers, the concentric radius formula): use them as written. Do not round them to something familiar.
- **Starting points** (spacing gaps, type sizes, durations, breakpoints): defaults for a project with no system of its own. Where the project already has tokens, a density or a motion language, keep those.

## The order of fixes

Take the earliest fix that works: delete it; use the platform (the native element); reuse what the project has (an existing token, step or curve); correct the value; only then add something new. A fix made by adding where deleting would have worked is its own defect.

## Reviewing

1. Review in this order, so a missing label is never hidden behind a nicer shadow: accessibility, layout, writing, typography, colour, then UI polish.
2. Cover the empty, loading, error and narrow-width states, not only the default one. For a component, render each stress axis in `### Stress-test each component`: content length and shape, quantity, container width, state, environment (dark mode, zoom, reduced motion).
3. Watch motion slowly: the browser's Animations panel at 10%, or a recording stepped frame by frame.
4. Each finding names a file, a line and a user impact. A density, radius or voice you merely dislike is not a finding.
5. Rank by harm. **High**: blocks a task, misleads, hides content or controls, risks data loss, or repeats across the system. **Medium**: hurts comprehension, efficiency, adaptability or consistency. **Low**: isolated polish. Within a level, a fix to a token or shared component outranks the same symptom in one place. Anything listed in `### Automatic blockers` is High regardless; report as `### Reporting rules` says.

## Companion

Krehel's own review commands (`/better-interface`, `/better-ui`, `/break` and others) install with `npx skills add jakubkrehel/skills`. They are optional; this skill does not require them.
