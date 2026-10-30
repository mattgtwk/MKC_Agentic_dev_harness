# Interfaces Design Bible

Oct 6, 2026 · @Angus Hervey

## How to use this bible

This is a working rulebook for interface craft, compiled from Jakub Krehel's [Interfaces magazine](https://interfaces.dev/magazine) (18 issues, May to September 2026), his [cheat sheet](https://interfaces.dev/cheat-sheet) and his public [skills repository](https://github.com/jakubkrehel/skills). Issue 17 is a guest piece by Jakub Antalik, and the transition values taken from it are credited to him.

Every rule is summarised in my words with the source issue named, so you can open the original for its interactive demo. The magazine is paid content, so this document carries the rules and the numbers and leaves the prose and demos where they live.

Krehel sorts his own rules into two kinds, and the distinction matters when you apply them:

- **Exact values.** The icon swap recipe, the image outline colour, the shadow-as-border layers and the concentric radius formula are written as fixed values. His skills say to use them as written and not round them to something familiar.
- **Starting points.** Spacing gaps, type sizes, durations and breakpoints are defaults for a project with no system of its own. Where a project already has tokens, a density or a motion language, keep those.

### Where his sources disagree

The magazine, cheat sheet and skills were written months apart, and a few values differ. The last column is my recommendation.

| Detail | Magazine | Cheat sheet | Skills repo | Use |
| --- | --- | --- | --- | --- |
| Button press scale | 0.97, 200ms ease-out (issue 12) | 0.95 to 0.98, 200ms ease-out | 0.96, 150ms ease-out, never below 0.95 | 0.96 or 0.97, pick one per product |
| Image outline opacity | 10% (issue 9) | 8% | 10% | 10% |
| Desktop hit area | No smaller than 32px (issue 16) | 40px where possible | 40px where density permits | 40px target, 32px working floor, 24px hard floor |
| Staged entrance | 8px rise, 8px blur, 800ms (issue 9) | Not specified | 12px rise, 4px blur, 400ms ease-out | Either, held constant across the product |
| Dark-mode ring on hover | White at 12% (issue 9) | Not specified | White at 13% | Either |

## Philosophy

Nine beliefs sit under every rule in this document. When two rules conflict, these decide.

1. **Quality is a pile of small decisions.** No single detail makes a product feel good. Matching radii, balanced headings, steady numbers and a hundred similar choices add up to the difference people feel but can't name (issues 1, 9 and 13).
2. **Removing is harder than adding, and worth more.** AI made adding nearly free, so the scarce skill is knowing what to leave out. His worked example is a context menu opened 200 times a day with a 300ms entrance, which costs about a minute a day and more than six hours a year (issue 13).
3. **Animate only what earns it.** The more often an interaction happens, the less motion it should carry. Frequent actions respond instantly, and expressive motion is saved for rare moments.
4. **Most of the job is invisible.** Accessibility, performance, responsiveness, hit areas, reduced motion and locale formatting take up most of a design engineer's day and never appear in a social post (issue 18).
5. **Use the thing you built.** He says he might never have noticed that a code input lacked auto-focus had he not signed in through his own dialog (issue 12).
6. **Slow it down to judge it.** Flaws that hide at full speed are obvious at one-eighth speed, and fixing them improves the full-speed result (issue 11).
7. **Use the platform first.** Native elements, the browser's own focus ring and headless primitives beat custom rebuilds (issue 16).
8. **Agents speed up execution, and the judgment stays yours.** He uses AI to try ideas in minutes and throws most away. He does not use it to decide what is good (issues 6 and 13).
9. **Report evidence, leave taste alone.** In review, a finding needs a file, a line and a user impact. A density, radius or voice you merely dislike is not a finding (skills repo).

### The order of fixes

When several fixes would work, his review skill takes the earliest one on this list.

1. Delete it. A separator that spacing could replace, an animation on a frequent interaction, a colour ramp nothing imports.
2. Use the platform. The native element or control in place of a custom one.
3. Reuse what the project has. An existing token, spacing step or motion curve.
4. Correct the value. The wrong easing, radius, gap or contrast pair.
5. Add something new. A token, a wrapper, a media query or an ARIA attribute.

A fix made by adding where deleting would have worked counts as its own defect.

## Numbers at a glance

Every value the later sections rely on, in one place. "Skills" means the public skills repository, and issue 17 values are Jakub Antalik's.

### Surfaces

| Rule | Value | Source |
| --- | --- | --- |
| Nested radius | Outer radius = inner radius + padding | Issue 9 |
| When to stop nesting radii | Past 24px of padding, choose each radius on its own | Skills |
| Button with trailing icon | Icon-side padding = text-side padding minus 2px | Skills |
| Play triangle | Shift 2px toward its point | Skills |
| Shadow as border, light | 1px ring black 6%, then 0 1px 2px -1px black 6%, then 0 2px 4px black 4% | Issue 9 |
| Shadow as border, light hover | Same three layers at 8%, 8% and 6% | Issue 9 |
| Shadow as border, dark | One 1px ring, white 8%, hover 12 to 13% | Issue 9, skills |
| Image outline | 1px, offset -1px, pure black or pure white at 10% | Issue 9, skills |
| Icon stroke on a 24px grid | 1.5px beside regular text, 2px beside medium or semibold, 2.5px beside bold | Skills |
| Inline icon size | 1em to 1.25em | Skills |

### Motion

| Rule | Value | Source |
| --- | --- | --- |
| Duration, tooltips and small elements | 150ms | Issue 17 |
| Duration, dropdowns, menus, tabs | 250ms | Issue 17 |
| Duration, modals, drawers, panels | 350 to 450ms | Issue 17 |
| Exit against entrance | Shorter, for example 250ms open and 150ms close | Issue 17 |
| Entrance scale, tooltip or dropdown | From 0.96 or 0.97 to 1 | Issue 17 |
| Entrance scale, modal or panel | From 0.98 or 0.99 to 1 | Issue 17 |
| Exit scale | To about 0.99 | Issue 17 |
| Travel, text swap | 4px | Issue 17 |
| Travel, page transition | About 8px | Issue 17 |
| Travel, most UI elements | 8 to 32px | Issue 17 |
| Travel, sheets and panels | Up to 70% of their own width or height | Issue 17 |
| Default spring | Bounce 0, duration 0.3s | Issue 12 |
| Tab indicator spring | Bounce 0, duration 0.4s | Issue 12 |
| Drawer spring | Bounce 0, duration 0.45s | Issue 9 |
| Icon swap | Scale 0.25 to 1, opacity 0 to 1, blur 4px to 0, spring 0.3s with bounce 0 | Cheat sheet, skills |
| Icon swap without a motion library | 300ms on cubic-bezier(0.2, 0, 0, 1) | Skills |
| Button press | Scale 0.96 or 0.97, 150 to 200ms ease-out | Issue 12, skills |
| Staged entrance stagger | About 100ms between groups, 80ms between words of a title | Issue 9 |
| Frequent interactions | Instant, or 150ms at most on opacity and colour | Skills |
| Dialog content crossfade | Opacity plus scale 0.95 | Issue 12 |
| Subtle exit | 12px travel, 4px blur, 150ms ease-out | Skills |
| Looping loader | 1.25s, linear, infinite | Issue 12 |
| Swipe row | Elastic 0.05, momentum off, commit threshold at half the snap distance | Issue 7 |

### Typography

| Rule | Value | Source |
| --- | --- | --- |
| Long-form body | 16px | Issue 15 |
| UI text, inputs, menus | 14px | Issue 15 |
| Captions | 13px | Issue 15 |
| Floor | 12px | Issue 15 |
| Input text on mobile | 16px, or iOS Safari zooms the page | Issue 15 |
| Line height, headings | About 1.1 | Issue 15 |
| Line height, body | 1.5 to 1.6 | Issue 15 |
| Line height, anything wrapping to 3+ lines | At least 1.4 | Skills |
| Line length | 60 to 75 characters, roughly 560 to 680px at 16px | Issue 15 |
| Letter spacing, display headings | About -0.02em | Skills |
| Letter spacing, small uppercase labels | About +0.05em | Skills |
| Weight below 18px | 400 or heavier | Skills |
| Weights under 300 | Display only, 28px and up | Skills |
| Fonts per project | Three at most | Issue 14 |
| Inter fallback matching | font-size-adjust: 0.545 | Issue 14 |

### Colour and contrast

| Rule | Value | Source |
| --- | --- | --- |
| Ramps in a system | 1 neutral, 1 accent, 0 to 4 status | Skills |
| Same colour test | Hues within 15 degrees read as one colour | Skills |
| WCAG AA, regular text | 4.5:1 | Issue 15 |
| WCAG AA, large text (24px, or 18.5px bold) | 3:1 | Issue 15, skills |
| APCA, body text | Lc 75 minimum, Lc 90 preferred | Skills |
| APCA, labels and headlines | Lc 60 minimum, Lc 75 preferred | Skills |
| APCA, UI components | Lc 30 | Skills |
| Dark text or light text | Switch at about 73% perceived background lightness | Skills |
| Increased-contrast variant | Widen the lightness gap by 15 points or more | Skills |

### Layout and accessibility

| Rule | Value | Source |
| --- | --- | --- |
| Gap between groups | At least twice the gap within a group, such as 8px and 16px | Cheat sheet |
| Between bordered controls | 12px | Skills |
| Around borderless controls | 24px | Skills |
| Indent step | 16px | Skills |
| Peek of the next scrolling item | 16 to 32px | Skills |
| Mobile side margin | 16px | Skills |
| Hit area | 24px hard floor, 40px desktop, 44px touch | Issue 16, cheat sheet |
| Focus ring | 2px solid, 2px offset | Issue 16 |
| Zoom and reflow | Works at 200% zoom and at 320px wide | Skills |
| Timed toast | 5 seconds minimum, paused on hover or focus | Skills |
| Sticky-header anchor offset | scroll-margin-top, such as 80px | Skills |

## Surfaces and UI polish

Mismatched radii on nested elements are, by his account, the most common reason an interface feels off. Sources: [issue 9](https://interfaces.dev/magazine/issues/details-that-make-interfaces-feel-better), the cheat sheet and the `better-ui` skill.

### Concentric radius

When one rounded element sits inside another, the outer radius equals the inner radius plus the padding between them. A 12px inner card with 8px of padding needs a 20px outer radius. The rule applies while the two layers share a visible, even inset. Past about 24px of padding they read as separate surfaces and each takes its own radius. Browsers already apply the same maths to a focus ring with an offset.

### Optical alignment

Align by eye when geometry looks wrong.

- A button with text and a trailing icon takes about 2px less padding on the icon side.
- A play triangle sits about 2px toward its point, because its visual centre is not its geometric centre.
- Stars, arrows and carets carry uneven weight. Fix the SVG itself where you can, so no component needs a margin hack.

### Shadows for depth, borders for structure

Where a border exists only to lift a card, button or container off the page, he replaces it with three stacked transparent shadows. The first is a 1px ring, the second adds lift and the third adds ambient depth. Transparent shadows adapt to any background, including images, where a solid border colour was designed for one background only.

```css
.surface {
  box-shadow:
    0 0 0 1px rgb(0 0 0 / 0.06),
    0 1px 2px -1px rgb(0 0 0 / 0.06),
    0 2px 4px 0 rgb(0 0 0 / 0.04);
  transition: box-shadow 150ms ease-out;
}
.surface:hover {
  box-shadow:
    0 0 0 1px rgb(0 0 0 / 0.08),
    0 1px 2px -1px rgb(0 0 0 / 0.08),
    0 2px 4px 0 rgb(0 0 0 / 0.06);
}
/* Dark mode: depth layers are invisible, so keep one ring */
.dark .surface { box-shadow: 0 0 0 1px rgb(255 255 255 / 0.08); }
```

Keep real borders where they carry structure or state: dividers between rows, table cell boundaries, form input outlines, hairlines in dense UI, and selected or focus states.

### Image outlines

Every image gets a 1px outline drawn 1px inside its edge, pure black at 10% in light mode and pure white at 10% in dark. The colour is fixed. A near-black from the palette or a tinted neutral picks up the surface beneath and looks like dirt on the image edge. An outline is used over a border because it never changes layout.

```css
img { outline: 1px solid rgb(0 0 0 / 0.1); outline-offset: -1px; }
.dark img { outline-color: rgb(255 255 255 / 0.1); }
```

### Icons

- **Match stroke to text weight.** A hairline icon beside semibold text looks broken. Use 1.5px beside regular text, 2px beside medium or semibold, 2.5px beside bold.
- **One icon library per surface,** with one stroke convention.
- **One SVG, recoloured per state.** Draw icons with `currentColor` and let CSS drive hover, selected and disabled. Strip hardcoded fills on import.
- **Outline by default, filled when active.** The pair is a state signal, so filled icons everywhere leave the active tab with no signal.
- **Design at render size.** Test every icon at 16px and use the set's native grid sizes (16, 20, 24) so it stays sharp.
- **Flip for right-to-left only when direction is the meaning.** Back arrows and chevrons flip. Logos, checkmarks, clocks and media playback controls do not.

### Small details that carry weight

- **Disable text selection on controls.** Nobody copies a button label, and Cmd+A should select only content the reader would want. Keep content selectable everywhere else (issues 12 and 15).
- **Give decorative layers `pointer-events: none`.** A glow or gradient laid over a button swallows its clicks.
- **Put hover styles inside `@media (hover: hover)`.** On touch screens a hover state sticks after a tap and looks like a selection.
- **Format dates, times and prices by locale.** Hardcoded formats are one of the invisible defects he lists in issue 18.

## Motion

Decide whether to animate before deciding how. Sources: issues [4](https://interfaces.dev/magazine/issues/how-i-use-shared-layout-animations), [5](https://interfaces.dev/magazine/issues/will-change-in-css), [7](https://interfaces.dev/magazine/issues/drag-gestures-on-the-web), [8](https://interfaces.dev/magazine/issues/using-gestures-in-motion), [9](https://interfaces.dev/magazine/issues/details-that-make-interfaces-feel-better), [11](https://interfaces.dev/magazine/issues/review-your-animations), [12](https://interfaces.dev/magazine/issues/building-an-animated-sign-in-dialog), [13](https://interfaces.dev/magazine/issues/less-is-more) and [17](https://interfaces.dev/magazine/issues/4-principles-of-transition), plus the `better-ui` skill.

### Whether to animate

Motion has a cost paid on every trigger, so frequency sets the budget.

| Interaction | Treatment |
| --- | --- |
| Row hover, keystroke, tab switch in a work tool | Instant, or a colour or opacity change of 150ms or less |
| Context menu or other menu opened many times a day | No entrance animation, a short exit only |
| Icon that changes with state (copy to check, play to pause) | The icon swap recipe below |
| First load of a view, success state, empty state | Staged entrance, split and staggered |
| Static navigation icons, always-visible icons, decoration | No animation |
| Anything on page load | No animation unless it is a deliberate entrance |

Two rules hold everywhere. Every state change an animation shows must also leave a static cue behind, such as a colour, an icon or a label. And when a shorter, smaller animation says the same thing, use the shorter one.

### The four principles of a transition

These come from Jakub Antalik's guest issue and apply to desktop and web apps. Mobile can run longer and travel farther.

1. **Duration follows size.** Small things move fast and large things take longer: 150ms for tooltips, 250ms for dropdowns and tabs, 350 to 450ms for modals and panels. Entrances run longer than exits, because a new element needs reading and a leaving one does not.
2. **Easing defaults to ease-out.** It responds at once and settles slowly. Use linear for loaders and continuous motion, and a subtle spring for morphs, sheets and anything that should feel physical. A colour change on hover gains nothing from a spring.
3. **Scale runs opposite to size.** A tooltip can grow from 0.96, and a modal should start no lower than 0.98 because so much of the screen changes. Exits shrink only to about 0.99. Set `transform-origin` to the trigger's position so the element grows from where it was opened.
4. **Movement explains origin.** Travel shows where something came from. Keep it between 4px and 32px for most elements, about 8px for a page transition, and up to 70% of its own size for a sheet or side panel.

Bounce stays at 0 or very close to it. High bounce across an interface gets tiring fast.

### Make interactions interruptible

CSS transitions retarget when state changes mid-flight, so a drawer reversed halfway reverses smoothly. Keyframe animations run a fixed timeline and restart. Use transitions for anything a person can toggle, and keep keyframes for sequences that run once, such as an entrance or a loader.

### Entrances and exits

- **Split and stagger entrances.** Animating one big container wastes the effect. Break a hero into title, description and buttons, and delay each group by about 100ms. A title can split further into words 80ms apart. Each piece combines opacity, a small rise and a blur.
- **Make exits smaller than entrances.** The reader's attention has moved on. A drawer that slides fully in can leave by moving 70% of its width while fading and blurring 4px. A list item can leave with 12px of travel in 150ms.
- **Sometimes remove instantly.** When the exit adds no information, the interaction repeats often or reduced motion is on, skip it.

### Recipes

**Icon swap.** The outgoing icon goes to scale 0.25, opacity 0 and 4px blur while the incoming one does the reverse, both at once, on a 0.3s spring with no bounce. The skill is strict that these values are not approximated. Without a motion library, keep both icons mounted, position one absolutely over the other and cross-fade over 300ms on `cubic-bezier(0.2, 0, 0, 1)`.

**Button press.** Scale to 0.96 or 0.97 on `:active` with a 150 to 200ms ease-out transition on scale only. Offer a way to switch it off for buttons where the motion distracts.

**Sliding tab indicator.** Render an absolutely positioned background inside only the active tab and give it a shared `layoutId` in Motion. The library animates between the two positions. Put the label in its own span above the indicator.

**Shared layout rules.** Elements animate between states when they share a `layoutId` that is unique within the group. Pass changing values such as border radius through `animate` so they interpolate. Keep `layoutId` elements outside `AnimatePresence` unless you want them to fade during the move.

**Animating height.** CSS and Motion cannot animate to `auto`. Measure the content with a `ResizeObserver` hook, attach the ref to an inner wrapper and animate the outer element to the measured height. Give the first state a fixed height, because the measurement reads 0 until the content mounts.

**Swapping content inside a container.** Wrap it in `AnimatePresence` with `mode="popLayout"` and `initial={false}`, key the child by step and animate opacity with scale 0.95. `sync` runs both at once, `wait` finishes the exit first and `popLayout` lifts the leaving element out of the layout.

**Swipe row.** Drag on one axis with constraints at the snap points, elastic at 0.05 and momentum off, so the row stops where the hand stops. On release, snap open if travel passed half the snap distance and closed otherwise. Reveal actions one at a time as the drag passes pixel thresholds.

**Rotating border loader.** Spin an oversized conic gradient behind a clipped, padded container at 1.25s linear.

### Housekeeping

- **Name the properties you transition.** Never `transition: all`. It animates properties you didn't intend and blocks browser optimisation.
- **No animation on first render.** Set `initial={false}` on `AnimatePresence` for toggles, tabs and icon swaps. Leave it off where a page entrance depends on `initial`.
- **Kill transitions during a theme switch.** Every colour, border and shadow transition fires at once and the page smears. Inject a rule that sets `transition: none` on everything, force a reflow, and remove it on the next frame. The `next-themes` option `disableTransitionOnChange` does this.
- **Use `will-change` only as a fix.** Add `will-change: transform` when an element shifts by a pixel or stutters on the first frame, most often in Safari. It helps only for transform, opacity and filter, and every promoted layer costs memory.
- **Set shared defaults once.** Wrap the app in `MotionConfig` with a default transition and `reducedMotion="user"`, and load Motion through `LazyMotion` with the `m` components to keep the bundle small.
- **Keep focus animations subtle.** Large motion on keyboard focus disorients.
- **Prefer springs for dragged and physical things.** Sliders, sheets and drags feel more natural on a spring. For transform, clip-path and filter, Motion and CSS perform about the same.

## Typography

His position is that good typography is mostly restraint: a small scale, comfortable spacing and enough contrast. Sources: issues [14](https://interfaces.dev/magazine/issues/typography-manual-for-the-web) and [15](https://interfaces.dev/magazine/issues/working-with-type), and the `better-typography` skill.

### Choosing and pairing

- Use three fonts at most. Marketing pages can be more expressive than apps.
- Keep sizes and weights few as well. Both define hierarchy, and both stop working when overused.
- Pair for contrast. A serif headline over a sans body looks deliberate, and two similar sans-serifs look like a mistake.
- Serif suits long reading, sans-serif is the interface default, and monospace suits code and tables.
- Where a family ships Display and Text cuts, use the cut that matches the size.
- Two fonts at the same `font-size` can look different sizes because their x-heights differ.

### Loading

- Serve `.woff2`. Add `.woff` only for very old browsers, and keep `.ttf` and `.otf` off the web.
- Self-host. A font CDN adds a request before the font is available. In Next.js, `next/font` downloads at build time and serves from your own domain, including for Google Fonts.
- Subset to the character ranges you use.
- Set `font-display: swap` with a system fallback that looks similar. If the fallback's x-height differs, `font-size-adjust` scales it to match (0.545 for Inter).
- Choose a variable font when you use several weights, optical sizes or custom axes. For one or two weights, static files can be smaller.
- Load every weight and style the design uses. A browser fakes missing bold and italic, and the result distorts the face.
- Prefer CSS properties over raw tags: `font-weight` over `"wght"`, `font-variant-numeric: tabular-nums` over `"tnum"`. Properties keep working when a fallback renders. Keep `font-variation-settings` and `font-feature-settings` for custom axes and stylistic sets.

### Scale, spacing and rhythm

Use a type scale and stray from it as little as possible. On a team, name sizes by role (`text-body-sm`), because `text-sm` says the size and not the use. The skill offers this starting scale for a product interface.

| Role | Size | Line height | Weight |
| --- | --- | --- | --- |
| Display | 36px | 1.1 | 600 |
| Title | 24px | 1.2 | 600 |
| Heading | 18px | 1.3 | 600 |
| Body | 16px | 1.5 | 400 |
| Caption | 13px | 1.4 | 400 |

- Emphasis inside a role is one weight step up, from 400 to 500, with the size unchanged.
- Heading sizes descend with level. A child heading never looks bigger than its parent.
- Pick the heading element from the document structure, then size it in CSS.
- Use unitless line heights so they scale with the font size.
- Tighten letter spacing on large headings, loosen it on small uppercase labels and leave body text alone.
- `text-box: trim-both cap alphabetic` removes the built-in space above and below letters, which fixes text sitting low in buttons and badges. Chromium and Safari support it, so treat it as an enhancement.
- Set `-webkit-font-smoothing: antialiased` and `-moz-osx-font-smoothing: grayscale` once on the root. macOS otherwise renders text heavier than designed.

### Lines and wrapping

| Situation | Declaration |
| --- | --- |
| Headings | `text-wrap: balance` |
| Descriptions and short paragraphs | `text-wrap: pretty` |
| Long-form articles | Neither, with the line capped at 60 to 75 characters |
| Long URLs, IDs and keys | `overflow-wrap: break-word` |
| Labels and badges | `white-space: nowrap` |
| One line that must fit | `text-overflow: ellipsis` with `overflow: hidden` and `white-space: nowrap` |
| Several lines that must fit | `line-clamp` |
| Numbers that change or align | `font-variant-numeric: tabular-nums`, skipped in a monospace font |

Truncation hides content, so the full value must be reachable in a tooltip or an expanded view. Avoid justified text in interfaces.

### Copy, punctuation and direction

- Write copy in natural case and apply uppercase with `text-transform`, so a redesign never means retyping.
- Use curly quotes in prose and straight quotes in code, an en dash for ranges and the single ellipsis character.
- A non-breaking space keeps a value and its unit together. A soft hyphen marks where a long word may break.
- Set `lang`, and `dir` where direction changes. Use logical properties such as `margin-inline-start` and `text-align: start` so layouts mirror correctly.

### Underlines and selection

- Take underline position and thickness from the font with `from-font`, and set `text-decoration-skip-ink: auto` so the line clears descenders.
- A dotted underline signals a term with extra information.
- Only the colour of a real underline animates well. For any other effect, build the underline as its own element.
- Style `::selection` in brand colours and check the selected text still has contrast. Mobile systems override it.

### Inputs

iOS Safari zooms the page when a focused input has text under 16px. He uses two fixes. The first sizes inputs at 16px on mobile and the design size above the small breakpoint. The second caps zoom in the viewport meta tag, which costs pinch zoom in other browsers, so he limits it to short-lived screens such as sign-in. The skill adds a third: keep 16px and shrink the input with a transform, compensating its width and line height.

Caret styling stops at `caret-color`. A custom caret is rarely worth building.

### Size and contrast floors

Body text starts at 16px, UI text at 14px, captions at 13px, and almost nothing goes below 12px. Regular text needs 4.5:1 against its background and large text needs 3:1.

## Colour

A colour system is a few ramps, named by role and measured against the backgrounds they render on. Sources: issues [2](https://interfaces.dev/magazine/issues/what-are-oklch-colors) and [3](https://interfaces.dev/magazine/issues/understanding-gradients), the cheat sheet and the `better-colors` skill.

### Why OKLCH

`oklch(L C H)` describes a colour by lightness (0 to 1), chroma (intensity, roughly 0 to 0.4) and hue (0 to 360 degrees). It is built to match how people perceive colour, which gives three practical gains.

- **Even brightness across hues.** Hold lightness and chroma and change only hue, and the colours look equally bright. The same move in HSL gives colours of visibly different brightness.
- **Shades without drift.** Change lightness alone and the hue stays put. HSL shades of blue drift toward purple when light and go muddy when dark.
- **Wider gamut.** It can express Display-P3 colours that sRGB cannot. Greys are identical in both.

It can also describe colours no screen can show, which the browser clips to something that may look different. Keep chroma inside what the target gamut allows. For old browsers, declare a hex value first and override it inside `@supports (color: oklch(0 0 0))`. For P3, declare the sRGB value first and override inside `@media (color-gamut: p3)`.

For a new system he recommends OKLCH. In an existing project, keep whatever notation it already uses. One consistent hex system beats hex with stray OKLCH values in it.

### Build ramps for roles

Most products need one neutral ramp, one accent ramp and only the status ramps they render. Each step exists because a role needs it.

| Role | Tailwind step | Radix step |
| --- | --- | --- |
| Page background | 50 | 1 |
| Subtle background | 50 | 2 |
| Component background | 100 | 3 |
| Component hover | 200 | 4 |
| Component active or selected | 200 | 5 |
| Subtle border | 200 | 6 |
| Border, separator | 300 | 7 |
| Strong border, focus ring | 400 | 8 |
| Solid fill | 500 | 9 |
| Solid fill hover | 600 | 10 |
| Low-contrast text | 700 | 11 |
| High-contrast text | 900 | 12 |

Radix defines steps by role, so step 9 is the solid fill in light and dark. Tailwind defines them by lightness, so the mapping inverts in dark mode. He prefers the Radix model for a new system.

A well-formed ramp has these properties:

- Steps are evenly spaced in perceived lightness.
- Hue stays constant from end to end.
- Vividness peaks in the middle and falls away at both ends.
- Steps sit closer together at the light end, where backgrounds need finer distinctions.
- Neither end reaches pure black or pure white.

Generate ramps with a colour library (`culori`, `colorjs.io`, `chroma.js`) and never by eye. Place the brand colour on the solid-fill step. If it fails contrast behind white text, leave it where it lands and use a darker step for fills. Across several hues, match lightness exactly and match vividness as a proportion of each hue's own maximum, because yellow and cyan peak far lower than red and blue.

A pure grey neutral is a good default. Tinting it slightly toward the accent is a style choice. Whichever you choose, hold it across the whole ramp.

### Name tokens by job

- **Two tiers.** Primitives name a value (`--blue-500`) and never appear in a component. Semantic tokens name a job (`--color-text-secondary`), point at a primitive and are the only thing components use. That seam is what makes dark mode and theming possible.
- **One grammar.** `--color-{role}-{variant}-{state}`, as in `--color-accent-solid-hover`.
- **One word per concept.** `text`, `bg`, `border`, `accent`. Never mix in `fg`, `fill` or `stroke`.
- **Reserve `accent` for the brand.** Then `primary` only ever means the most prominent of its group, and `--color-primary` never collides with `--color-text-primary`.
- **Never name by appearance or first use.** `--color-blue-button` lies when the brand changes, and `--color-sidebar-gray` stops making sense on its second use.
- **Never borrow a token for its value.** A separator token used as text colour breaks the day borders get lighter. If a role has no token, add one.

A complete system has tokens for surfaces (page, surface, raised, sunken, overlay), text (primary, secondary, disabled, inverse, on-accent), borders (subtle, default, strong, focus ring, separator), accent (subtle background, border, solid, solid hover, text) and each status it ships.

### Use colour for one meaning

- A colour carries one meaning across the product. If the accent means interactive, accent-coloured static text invites clicks that go nowhere.
- One filled primary action per view, with the colour on the background. Peers stay neutral.
- Status hues must differ from the accent. A red brand needs its danger colour moved toward crimson.
- Colour is never the only signal. Pair it with an icon, a label or a shape.
- Colour meaning varies by culture. Chinese financial interfaces show gains in red and losses in green, so make such colours per-locale tokens.

### Gradients

Linear gradients blend along a line, radial ones spread from a point and conic ones sweep around a centre. Two stops at the same position make a hard edge. A colour hint between two stops moves the midpoint of the blend without adding a colour. Layered gradients with `background-blend-mode` build richer effects, and gradients animate cheaply as long as the browser isn't recalculating them.

The interpolation space is a look you choose.

| Space | Result | Use when |
| --- | --- | --- |
| `in oklab` | Even brightness, no surprise hues | Default |
| `in oklch` | Travels around the hue wheel and stays vivid, sometimes through hues you never chose | A two-hue gradient goes grey in the middle |
| sRGB (no keyword) | Midpoint darkens and mutes | You want the classic look |

Tailwind 4 uses oklab by default. Keep text off gradients where possible, and where it must sit on one, measure contrast at the worst point.

### Contrast

- Measure the text against the surface directly behind it, which is often a card and not the page.
- Fix a failing pair by changing lightness. Hue and saturation barely move the number.
- A background near the middle of the lightness range caps what any text colour can reach, so body text needs a background near one extreme.
- Check every pair again in dark mode. Contrast does not survive mirroring.
- For translucent surfaces and text over images, test the lightest and darkest content that can sit behind.
- In review, report a failing pair with its measured value and leave the colours alone until asked. They are a design decision.

### Dark mode

Build a separate dark palette. Reversing the light one is only the first step. After the swap, lower the accent's vividness a step or two, widen the gaps between dark steps and remeasure every pair.

Pick one switching mechanism and use it everywhere: `prefers-color-scheme` when there is no toggle, a `.dark` class when users can override the system, or `light-dark()` with `color-scheme`. Mixing a media query with a class leaves the interface half-themed when someone overrides their system setting.

## Layout

Position, spacing and alignment set the hierarchy before anyone reads a word. The magazine has no layout issue yet, so this section comes from the cheat sheet and the `better-layout` skill. Its numbers are starting points for a project with no density system.

### Grouping

- **Group with space first.** Use space, then a background shape, then a separator line, in that order of preference. Lines are for dense data such as tables and long settings lists.
- **The 2x rule.** The gap between groups is at least twice the gap inside one. With 8px between a label and its field, leave 16px or more between fields.
- **Controls must look like controls.** Give every interactive element a background, border, underline or a consistent zone. A link styled like the sentence around it is invisible, and a static badge shaped like a button collects dead clicks.

### Alignment and order

- **Pick a few alignment edges and put everything on them.** An icon 2px off the text edge reads as noise even when nobody can say why.
- **Indent by one step.** Use a single spacing step per level of nesting, 16px by default.
- **Numbers align to the trailing edge, text to the leading edge.**
- **Order by importance.** The most important thing sits top and leading. In a row, identity leads, and metadata and actions trail.
- **One primary action per view.** Move secondary actions into a menu once there are more than two or three.
- **Use logical properties.** `margin-inline-start`, `padding-inline-end`, `inset-inline-start` and `text-align: start` mirror for right-to-left without extra work.

### Spacing between controls

Leave 12px between adjacent bordered or filled controls and 24px around borderless text and icon buttons. Borderless controls need more room because the space is the only thing marking where one target ends. Compact tools can go tighter if hit areas never overlap.

### Edges and scrolling

- **Inset buttons from the viewport edge.** Start with a 16px side margin on mobile and a visible radius. A button glued to three edges looks like system chrome.
- **Content bleeds, controls float.** Backgrounds and media run to the viewport edge. Text and controls stay inside the margins and the safe areas (`env(safe-area-inset-*)`).
- **Hint at hidden content.** Let the next item in a scroller peek 16 to 32px, or label a disclosure with what it hides, such as "Show 12 more results". Content with no cue may as well not exist.
- **Offset anchored headings.** `scroll-margin-top` stops a sticky header covering the heading a link jumps to.

### Adapting

- **Break where the content breaks.** A breakpoint belongs where the layout stops fitting. 768px is a preset and may have nothing to do with your content.
- **Collapse late.** Keep the expanded layout as long as it fits.
- **Prefer container queries for components.** A card should respond to its column.
- **Plan for longer strings.** No fixed widths sized to English labels and no fixed heights on text. Buttons size from their label with padding. Test with a long-string locale.
- **Never park a primary action where it can be clipped.** Keep it in a sticky footer or other stable chrome. When a modal's content scrolls, its action row stays put.

## Accessibility

He treats accessibility as craft equal to animation and visual design, and as friction removed for everyone. Sources: [issue 16](https://interfaces.dev/magazine/issues/accessibility-as-craft), the cheat sheet and the `better-accessibility` skill.

A review is two walks. First with the keyboard alone, where every flow must complete. Then with a screen reader, where every control announces a name, a role and its state.

### Native elements first

- `<button>` for actions and `<a href>` for navigation. A `div` with a click handler has no focus, no keyboard support and no role.
- A real link gives you open-in-new-tab, the right-click menu and the address preview for free.
- Wrap inputs in a real `<form>`. That gives Enter to submit, browser validation and something password managers recognise.
- For complex widgets such as dialogs and selects, use a headless library (Base UI or Radix) before building your own.
- Don't add ARIA where a native element exists. Wrong ARIA is worse than none, because screen readers trust it.

### Focus

- Style `:focus-visible`, which appears for keyboard use and stays hidden on mouse clicks.
- Never remove the outline without a replacement. The browser's default ring is a fine choice.
- A custom ring is 2px solid with a 2px offset, in a colour checked against every background it crosses.
- Use only `tabindex="0"` and `tabindex="-1"`. Positive values create a second tab order nobody can maintain.
- Tabs, menus, toolbars and radio groups take one Tab stop, with arrow keys moving inside them.
- A modal makes the background `inert`, moves focus inside on open and returns it to the trigger on close. Native `<dialog>` with `showModal()` does this for you.
- For a destructive confirmation, put initial focus on the least destructive button.
- Make "Skip to content" the first Tab stop.

### Keyboard

- Every pointer action needs a keyboard path. Escape closes the most recent overlay, Enter submits and arrow keys move within a widget.
- In a multi-step dialog, Escape goes back a step and closes only from the first step (issue 12).
- Auto-focus the field the person will type in next, and focus the main button on steps with no input.
- Prefer key sequences such as G then I over single-letter shortcuts, which speech-input software can trigger by accident. Avoid combinations the browser owns, such as Cmd+T.
- Never bind a destructive action to a single easy key.
- A Cmd+K search reachable from anywhere counts as accessibility in his sense of the word.
- Use a hotkey library (`react-hotkeys-hook` or TanStack Hotkeys) once shortcuts span the app. They handle form fields, key repeat and composition.

### Hit areas

The visible element can stay small while the clickable area grows. Extend it with a pseudo-element on the button or label.

```css
.icon-button { position: relative; }
.icon-button::after { content: ""; position: absolute; inset: -8px; }
```

- 24px is the WCAG 2.2 floor. Aim for 44px on touch and 40px on desktop.
- Expanded areas must never overlap. Shrink the extension until they don't.
- Close the dead gaps between list items by adding 1px of hit area above and below each item when the visual gap is 2px.
- A checkbox and its label share one target.
- Add `touch-action: manipulation` to interactive elements to remove the double-tap delay on mobile.

### Reduced motion

Make motion opt-in. Wrap CSS animation in `@media (prefers-reduced-motion: no-preference)`, or Tailwind's `motion-safe:`, so a forgotten guard fails still. For Motion, one `MotionConfig reducedMotion="user"` at the root disables transform and layout animation and keeps opacity and colour.

| Under reduced motion | Treatment |
| --- | --- |
| Parallax, autoplaying video, looping decoration, large movement | Remove |
| Slides, scales and zooms | Replace with an opacity crossfade |
| Smooth scrolling | Jump instantly |
| Carousels | Start paused |
| Spinners, progress, hover colour, focus rings, button press | Keep |

Anything that moves on its own for more than five seconds needs a visible pause control. A toast carrying an action or an error stays until dismissed.

### Names and announcements

- An icon-only button needs an `aria-label` that names the action ("Copy link"), never the picture ("Chain icon").
- Visible text and the accessible name must match, because voice-control users say what they see.
- Decorative icons take `aria-hidden="true"`. Never put it on something focusable.
- Alt text states what the image communicates. Decorative images take `alt=""`. A missing `alt` is worse than an empty one.
- When something changes without focus moving, announce it through a live region. Use `role="status"` for routine updates such as "Link copied" and `role="alert"` for urgent errors only.
- Hide announcement text with an `sr-only` class, never `display: none`, which hides it from screen readers too.

### Forms

- Every input has a visible `<label>`. A placeholder is an example of the format and never the label.
- Set `type`, `inputmode` and `autocomplete` so the right keyboard and autofill appear. One-time codes take `inputmode="numeric"` and `autocomplete="one-time-code"`.
- Never block paste.
- Keep the submit button enabled until the request starts, then disable it and show a spinner beside the original label.
- Validate on submit. Mark failing fields `aria-invalid`, link each error with `aria-describedby` and move focus to the first invalid field.
- Show an error with an icon and a message as well as a red border. About 1 in 12 men and 1 in 200 women have a colour vision deficiency.
- Accept free text and validate afterwards. Trim values first, since autofill adds trailing spaces.

### Zoom

The page must work at 200% zoom and reflow at 320px wide with no horizontal scroll. Use `min-height` on anything that holds text, and prefer `rem` for font sizes and breakpoints in new code.

## Interface writing

His writing rules favour short, plain copy that uses the same word for the same thing every time. An error that keeps firing is a design fault to fix before it is a message to reword. Sources: the cheat sheet and the `better-writing` skill.

| Element | Rule | Weak | Strong |
| --- | --- | --- | --- |
| Button | Start with a verb that names the action | OK! | Save draft |
| Confirmation | Repeat the consequence, so the dialog can be answered without reading the body | Yes / No | Delete project / Cancel |
| Multi-step flow | One word for "next" on every step | Continue, Next, Proceed | Continue, Continue, Continue |
| Link | Describe the destination | Click here | Read the billing docs |
| Toggle | Describe what happens when it is on | Disable read receipts | Send read receipts |
| Error | Say how to fix it, next to the field | Invalid name | Use only letters for your name |
| System failure | Plain, no blame, with a next step | Oops! Something went wrong. | Unable to save. Check your connection and try again. |
| Empty state | Say what belongs here and offer one action | No results. | No projects yet, a line on what projects are for, and a Create a project button |
| Reader | Address them directly | The user will receive an email. | You'll receive an email. |
| Placeholder | Show the expected format, never act as the label | Email | name@example.com |

### Voice and consistency

- **Read the nearby copy before writing.** A product has one voice, and a local edit doesn't get to invent another.
- **Keep terms fixed.** If the menu says "Archive", the toast doesn't say "Move to storage".
- **Tone follows the stakes.** Success and onboarding can be warm. Settings stay neutral. Errors and destructive confirmations are calm and plain, and data loss is serious and explicit.
- **One capitalisation policy per element type.** Sentence case is the safer default.
- **Plain words.** No idioms or jokes that won't translate. Use "tap" on touch, "click" with a pointer and "select" when both apply.
- **No sentences assembled from fragments around a variable.** Word order changes by language, so use a full templated string with proper plurals.
- **Suffix every "Learn more"** once two appear on a page: "Learn more about exports".
- **Link straight to a setting** in place of describing the path to it.
- **Show format hints before the mistake,** phrased positively. When the same error keeps firing, redesign the interaction.
- **A search empty state names the query and offers a way out,** such as clearing filters.

## Working with AI agents

He uses agents to shorten the gap between an idea and seeing it on screen, and keeps the deciding for himself. Sources: issues [6](https://interfaces.dev/magazine/issues/using-ai-as-a-design-engineer) and [13](https://interfaces.dev/magazine/issues/less-is-more).

### His setup

- **Rules first.** A new project starts with short rule files for the things he already has opinions on: animation performance, the design system, utility conventions, accessibility. Rules save repeating himself in every prompt.
- **Understand any rule you copy.** Borrowed rules you can't explain are a liability.
- **Assume the agent knows nothing.** Each conversation starts with no context, and prompts written that way get better results.
- **Commands for repeat jobs.** A cleanup command strips agent habits from a diff: needless comments, defensive checks out of character for the file, type casts used to dodge errors. His team also runs a review command against its own written codebase standards.
- **Plan mode for bigger features,** and one task per prompt in sequence over a pile of follow-ups.
- **Design-file access for scaffolding.** With good rules, an agent reading the Figma file builds the skeleton of a complex screen quickly. He then tunes, polishes and animates by hand.
- **Current docs on tap.** A documentation server (context7) covers libraries that changed after the model was trained.
- **A second reviewer.** Another agent reviews each pull request.
- **Less code as a goal.** He points agents at duplication and tedious migrations. One icon-package migration removed about 5,000 lines with no change in function.

### His principles

1. Don't hand over your thinking.
2. Be critical. An agent's output is not automatically the right answer.
3. Ask whether each addition makes the result better.
4. An agent extends you, so it is only as good at something as you are.
5. Give it as much context as you can, and be opinionated about how you want things done.
6. Be able to explain, at least broadly, what the agent's code does.
7. When you don't understand something, have the agent teach you.

### His skills

The rules in this bible also exist as installable agent skills, which is the fastest way to apply them to a codebase.

| Skill | What it does |
| --- | --- |
| `/better-interface` | Runs every skill below as one ranked review |
| `/better-ui` | Radius, alignment, shadows, icons, motion polish |
| `/better-typography` | Scale, spacing, wrapping, truncation, font features |
| `/better-colors` | Palettes, tokens, OKLCH conversion, contrast |
| `/better-accessibility` | Focus, keyboard, ARIA, hit areas, forms |
| `/better-layout` | Grouping, alignment, reading order, adaptivity |
| `/better-writing` | Button labels, errors, empty states, consistency |
| `/interface-review` | Reviews a branch or pull request and classifies each finding |
| `/explain-interface` | Works out how an effect on someone else's site was built |
| `/break` | Renders one component in every state and stress case |
| `/variant` | Builds several variants of a component to compare |

Install the collection with `npx skills add jakubkrehel/skills`. Jakub Antalik's transition skill installs with `npx skills add Jakubantalik/transitions.dev`.

## Review process

His review habit has three parts: watch it slowly, test it against hostile content, and rank what you find by harm to the user. Sources: issues [10](https://interfaces.dev/magazine/issues/sharing-your-work-online) and [11](https://interfaces.dev/magazine/issues/review-your-animations), and the `better-interface` and `break` skills.

### Watch it slowly

Record the interaction, play it at one-eighth speed and step through it frame by frame. He does this for most animations he builds and treats it as the first round of QA. Speed hides flaws, and the fixes show at full speed too. The browser's Animations panel at 10% does the same job without a recording. The same method teaches you how someone else's animation works.

His bar before sharing anything publicly is whether he would post it. If not, he keeps working on it.

### Stress-test each component

The `break` skill renders one component under each condition below. Skip an axis when it can't apply, such as quantity on a component that never repeats.

| Axis | Cases to render | Catches |
| --- | --- | --- |
| Content length | Empty, one word, typical, several sentences, one unbreakable string | Collapsed boxes, overflow, containers that assumed one line |
| Content shape | Emoji, right-to-left text, mixed direction, tall scripts and diacritics, numbers in columns | Broken centring, clipped letters, wobbling figures |
| Quantity | Zero, one, a realistic count, ten times that | Missing empty states, layouts built for plurals, missing pagination |
| Container | 320px wide, squeezed by a sibling, very wide | Clipping, refusal to shrink, unbounded line length |
| State | Loading, error, disabled | Layout shift, colour-only errors, lost contrast |
| Environment | Dark mode, browser zoom, reduced motion | Theme gaps, zoom breakage, ignored motion settings |

### Review in this order

Foundations come before polish, so a missing label is never hidden behind a nicer shadow: accessibility, layout, writing, typography, colour, then UI polish. Cover the empty, loading, error and narrow-width states as well as the default one.

### Rank by harm

| Severity | Meaning |
| --- | --- |
| High | Blocks a task, misleads, hides content or controls, risks data loss, or repeats across the system |
| Medium | Hurts comprehension, efficiency, adaptability or consistency |
| Low | Isolated polish |

Within a level, a fix to a token or shared component outranks the same symptom in one place.

### Automatic blockers

These are always high severity, however minor the screen.

- A control with no accessible name.
- A keyboard-reachable control with no visible focus indicator.
- Something reachable by pointer and not by keyboard.
- Motion or autoplay that ignores the reduced-motion setting.
- Content or a control clipped or unreachable at 320px or 200% zoom.
- Body or control text that fails its contrast requirement.
- State or meaning carried by colour alone.
- A destructive action with no confirmation, undo or distinct styling.
- Truncated content with no way to see the full value.
- Content hidden past a scroll edge or behind a disclosure with no visible cue.
- An error that gives no way to recover.
- A semantic colour used against its meaning, such as the danger colour on a harmless action.
- A state change shown by motion alone.

### Reporting rules

- Every finding cites a file and line and shows the current code.
- One root cause is one finding, with every location listed under it.
- A check you couldn't run is reported as not verified. It is never written up as a finding.
- Report 15 findings at most, and never pad to reach the number.
- Read the project's own conventions first and write every fix in its existing stack.
- A review changes nothing unless asked to.

## How interfaces.dev itself is built

The site follows its own rules, and its measured values make a useful reference set. I read these from the live page in Chrome on 6 October 2026, in the light theme. They are the browser's computed values, so they describe the build and may differ in notation from his source tokens.

### Type

| Element | Observed |
| --- | --- |
| Typeface | Inter Variable, self-hosted, with font features `cv01` and `ss03` on by default |
| Smoothing | Antialiased on the body |
| Article title | 24px on a 32px line, weight 550, letter spacing -0.3px, balanced wrapping, 20px below |
| Section heading | 16px on a 26px line, weight 550, balanced wrapping, 80px above and 20px below |
| Paragraph | 16px on a 26px line, weight 400, in a softer grey than headings |
| List item | 16px on a 26px line, pretty wrapping |
| Code block | 13px on a 21px line, monospace |
| Inline code | 14px, white background, 6px radius |
| Navigation link | 14px, weight 500, mid grey |
| Reading column | 668px wide |
| Other faces | Berkeley Mono for code. Open Runde, Heldane, Libre Baskerville and PP Mondwest are also loaded, for demos and issue artwork |

The hierarchy runs on weight and spacing more than size. Section headings are the same 16px as body text, set apart by weight 550 and 80px of space above.

### Colour and surfaces

| Token | Light | Dark |
| --- | --- | --- |
| Page background | #fcfcfc | #101010 |
| Heading text (grey 1200) | About 12% lightness | About 94% lightness |
| Paragraph text | About 28% lightness | About 87% lightness |
| Surface shadow | 1px ring black 6%, 0 1px 2px -1px black 6%, 0 2px 4px black 4% | 1px ring white 8% |
| Surface shadow, hover | Same layers at 8%, 8%, 6% | 1px ring white 13% |
| Surface shadow, pressed | Same layers at 12%, 10%, 8% | 1px ring white 20% |
| Image and media outline | Black 10% | White 10% |
| Text selection | Light grey (grey 500) | Not measured |

The palette is a 12-step neutral grey with no hue, numbered 100 to 1200. In light mode the first nine steps run from about 99% lightness to 59%, packed tightly at the light end as his ramp rules describe. Steps 1000 to 1200 sit at about 55%, 42% and 12%.

### Controls and motion

| Element | Observed |
| --- | --- |
| Header button | 36px tall, fully rounded, 14px text at weight 500, 12px side padding, white fill with the surface shadow |
| Button transition | Scale, colour, background colour and box shadow, each 200ms ease-out, named one by one |
| Radius scale | Tailwind's defaults, from 2px to 32px |
| Default transition | 150ms |
| Keyboard | G then I, B, T or S jumps between sections. Cmd+K opens search |
| Inputs | 14px text, by his own account in issue 15 |

### Stack and page patterns

Several issues point to the stack behind the site: Next.js with `next/font` and the React Compiler, Tailwind, Motion loaded through `LazyMotion`, Base UI primitives and Central Icons.

Three page patterns are worth borrowing for any teaching material:

- **Paired comparisons.** Nearly every rule is shown as two live examples labelled "Not recommended" and "Recommended", often with a toggle that reveals the padding, margin or hit area.
- **Controls on the demo.** Sliders for width, radius and speed let the reader find the breaking point themselves.
- **Reading aids in the margin.** A contents rail, a word count and a reading time sit beside every issue, with a mark-as-read control at the end.

## Sources and further reading

I read all 18 issues, the cheat sheet, the skills, bookmarks and tools pages, and 32 files from the skills repository on 6 October 2026. The issue pages need a subscriber login.

### The 18 issues

| No. | Issue | Published | Covers |
| --- | --- | --- | --- |
| 18 | [The invisible side of design engineering](https://interfaces.dev/magazine/issues/the-invisible-side-of-design-engineering) | Sep 2026 | Performance, hit areas, reduced motion, locales |
| 17 | [4 principles of transition](https://interfaces.dev/magazine/issues/4-principles-of-transition) (guest: Jakub Antalik) | Sep 2026 | Duration, easing, scale, movement |
| 16 | [Accessibility as craft](https://interfaces.dev/magazine/issues/accessibility-as-craft) | Aug 2026 | Native elements, focus, shortcuts, hit areas, live regions |
| 15 | [Working with type](https://interfaces.dev/magazine/issues/working-with-type) | Jul 2026 | Spacing, wrapping, punctuation, underlines, inputs, 13 type rules |
| 14 | [Typography manual for the web](https://interfaces.dev/magazine/issues/typography-manual-for-the-web) | Jul 2026 | Choosing, loading, variable fonts, OpenType |
| 13 | [Less is more, more or less](https://interfaces.dev/magazine/issues/less-is-more) | Jun 2026 | Restraint, when not to animate, agent principles |
| 12 | [Building an animated sign-in dialog](https://interfaces.dev/magazine/issues/building-an-animated-sign-in-dialog) | Jun 2026 | Height animation, content swaps, tabs, small details |
| 11 | [Reviewing your animations](https://interfaces.dev/magazine/issues/review-your-animations) | May 2026 | Slow-motion review |
| 10 | [Sharing your work online](https://interfaces.dev/magazine/issues/sharing-your-work-online) | May 2026 | Career story, posting habit, quality bar |
| 9 | [Details that make interfaces feel better](https://interfaces.dev/magazine/issues/details-that-make-interfaces-feel-better) | May 2026 | Eleven polish details with values |
| 8 | [Using gestures in Motion](https://interfaces.dev/magazine/issues/using-gestures-in-motion) | May 2026 | Hover, tap, drag, pan, focus, in-view |
| 7 | [Drag gestures on the web](https://interfaces.dev/magazine/issues/drag-gestures-on-the-web) | May 2026 | Swipe-to-reveal row |
| 6 | [Using AI as a design engineer](https://interfaces.dev/magazine/issues/using-ai-as-a-design-engineer) | May 2026 | Rules, commands, tools, workflow |
| 5 | [will-change in CSS](https://interfaces.dev/magazine/issues/will-change-in-css) | May 2026 | Rendering pipeline, compositor layers |
| 4 | [How I use shared layout animations](https://interfaces.dev/magazine/issues/how-i-use-shared-layout-animations) | May 2026 | layoutId patterns |
| 3 | [Understanding gradients](https://interfaces.dev/magazine/issues/understanding-gradients) | May 2026 | Gradient types, colour spaces, hints, layering |
| 2 | [What are OKLCH colors?](https://interfaces.dev/magazine/issues/what-are-oklch-colors) | May 2026 | Colour models, gamut, fallbacks |
| 1 | [Introduction](https://interfaces.dev/magazine/issues/introduction) | May 2026 | What the magazine is |

### His reference pages and code

- [Interface cheat sheet](https://interfaces.dev/cheat-sheet): about 60 one-line rules across UI, animation, typography, colour, accessibility, layout and writing.
- [Skills page](https://interfaces.dev/magazine/skills) and the [skills repository](https://github.com/jakubkrehel/skills), which holds the detailed rule files this bible draws on.
- [make-interfaces-feel-better](https://github.com/jakubkrehel/make-interfaces-feel-better), his earlier single skill.
- [oklch.fyi](https://oklch.fyi/), his palette generator, converter and contrast checker.
- [transitions.dev](https://transitions.dev), Jakub Antalik's library of more than 30 transitions.

### His bookmarks

| Kind | Links |
| --- | --- |
| Practical | [Bézier curves](https://blog.richardekwonye.com/bezier-curves), [Designing with Code](https://justinjay.wang/designing-with-code/), [Web Interface Guidelines](https://vercel.com/design/guidelines), [Design Engineer Principles](https://vercel.com/design/engineer), [Web Animation Performance Tier List](https://motion.dev/magazine/web-animation-performance-tier-list), [Not a Number](https://www.nan.fyi/), [React Handbook](https://devouringdetails.com/resources/react-handbook), [UI Skills](https://www.ui-skills.com/) |
| Thinking | [Intelligent vs. Smart](https://collabfund.com/blog/intelligent-vs-smart/), [Productivity](https://blog.samaltman.com/productivity), [Startup = Growth](https://paulgraham.com/growth.html), [How To Do Great Work](https://paulgraham.com/greatwork.html), [When Good Is No Longer Good Enough](https://vanschneider.com/blog/when-good-is-no-longer-good-enough/), [Make Something Wonderful](https://book.stevejobsarchive.com/), [Make Something Heavy](https://www.workingtheorys.com/p/make-something-heavy), [Family Values](https://benji.org/family-values) |
| Inspiration | [Vintage Apple](https://vintageapple.org/), [Spotted in Prod](https://www.spottedinprod.com/), [Grilli Type](https://www.grillitype.com/), [US Graphics](https://usgraphics.com/products) |

### Tools he names for interface work

[Motion](https://motion.dev/) for animation, [easing.dev](https://easing.dev/) for curves, [Figma](https://www.figma.com/) and [Paper](https://paper.design/) for design, [CleanShot X](https://cleanshot.com/) for screen recording, [Cursor](https://cursor.com/) and [Claude Code](https://claude.com/claude-code) for agents, and [Ghostty](https://ghostty.org/) as terminal. Base UI and Radix are his headless component libraries, and Central Icons is his icon set.
