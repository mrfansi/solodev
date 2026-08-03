---
name: ui
description: Audit user interface presentation — visual hierarchy, typography, spacing, colour and contrast, component states, responsiveness, and consistency. Use when the user asks for a UI audit, visual review, design review, accessibility contrast check, or says an interface looks off, cluttered, or inconsistent. Also invoked by the loop skill when a run touches a visual surface. Covers web, mobile, and terminal interfaces.
---

# ui

`/solodev:ui [screen or component]`

You audit **presentation**: what the eye lands on first, whether it is readable,
whether it is consistent. Whether the user can finish their task belongs to the `ux`
skill — hand flow findings there rather than absorbing them.

## 1. Look at it

Render it and look. Screenshot the web or mobile surface; `tmux capture-pane` the
terminal one. Auditing from a stylesheet tells you what was intended, not what
shipped.

Capture every state that exists, because the broken one is almost never the default:

**default · hover · focus · active · disabled · loading · empty · error · overflow**

The empty state and the overflow state are where most interfaces fall apart, and both
are the ones nobody screenshots for the design review.

## 2. Dimensions

### Visual hierarchy
Squint at it. What do you see first? If that is not the most important thing on the
screen, the hierarchy is inverted. Rank the top three elements by visual weight and
compare against their actual importance.

### Typography
- Sizes come from a scale, not from ad-hoc numbers; count how many distinct sizes are
  in play — more than five in one view is usually accident, not intent
- Line length 45–75 characters for body text
- Line height ~1.5 for body, tighter for headings
- Weight carries hierarchy before size does

### Spacing and rhythm
- Space comes from one scale (4/8pt or a terminal's cell grid)
- **Proximity encodes relationship**: related things sit closer than unrelated ones.
  When a label sits equidistant between two fields, it belongs to neither.
- Alignment: everything shares an edge with something else; stray indents read as bugs

### Colour and contrast
Measure, do not eyeball:

| Content | WCAG AA minimum |
|---|---|
| Body text | 4.5:1 |
| Large text (≥18.66px bold, ≥24px regular) | 3:1 |
| UI components, focus rings, chart strokes | 3:1 |

- Colour is never the **only** carrier of meaning — pair it with a shape, icon, or
  word, or it disappears for colour-blind users and on bad monitors
- One palette with fixed semantics: success, warning, danger, focus
- Both themes if the product has them; a dark theme that was never opened is broken

### Component states
Every interactive element needs a visible focus state — keyboard users navigate by
it. Disabled must be distinguishable from enabled by more than opacity alone.

### Responsiveness
Test the tightest case first: smallest viewport, narrowest terminal, longest string,
largest font scale. Nothing may clip, overlap, or force horizontal scrolling of the
page body.

### Consistency
The same concept looks the same everywhere. Divergence here is the clearest signal of
copy-paste rather than a shared component.

## 3. Severity

| Level | Meaning |
|---|---|
| **Blocker** | Unreadable, invisible focus state, contrast below AA, or content clipped and unreachable |
| **Major** | Inverted hierarchy, broken alignment, or one state visually indistinguishable from another |
| **Minor** | Off-scale spacing, an extra font size, small inconsistency |
| **Polish** | Refinement with no functional cost |

## 4. Output

```markdown
## UI audit: <screen>

**Captured states:** <which ones> · **Viewports:** <sizes tested>

**First glance:** <what the eye lands on> — <correct or inverted, and why>

### Blockers
1. **<element>** — <what is wrong>
   **Measured:** <contrast 3.1:1, needs 4.5:1 / clipped at 80 cols / no focus ring>
   **Fix:** <exact value — hex, px, spacing token, not "increase contrast">

### Major
...

### Consistency notes
- <where the same concept renders differently, with both locations named>
```

Every fix carries a **concrete value**. "Add more spacing" is not actionable;
"16px instead of 6px, matching the other form rows" is.

## For terminal interfaces

The same dimensions, in cells rather than pixels:
- hierarchy → borders, bold, and colour, since size is fixed
- spacing → column widths and padding cells, aligned to one grid
- contrast → still measurable; do not assume the user's theme resembles yours
- responsiveness → 80×24 first, then wider
- states → selection must be obvious without colour alone, since some terminals
  render it poorly or not at all

## When the loop skill invokes this

Runs in Phase 5 alongside `ux`, only when the slice touched a visual surface.
Blockers **fail the rubric** and are fixed in the same run; major findings map to
rubric items 2, 3, and 8; minor and polish go to the backlog.
