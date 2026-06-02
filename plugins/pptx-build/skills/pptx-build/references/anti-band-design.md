# Anti-Band Design

Why this generator never draws full-width "bands" behind titles, and what it does instead.

## The problem the user reported

A common Office/AI look is a **colored band** — a full-width filled rectangle placed behind the title (or as a footer strip). It looks fine on one slide and then betrays the deck:

- **Edge drift.** The band is drawn per slide. A 1–2 px difference in left/top/width across slides — from copy-paste, manual nudging, or a slightly different layout — makes the edges fail to line up when you flip through. The eye catches the jump instantly.
- **Z-order and overlap.** Bands sit behind text but in front of the background; on a slide with an image or a long title they collide, and the fix is another manual nudge that drifts again.
- **Reflow fragility.** Change the title length or the slide size (16:9 → 4:3) and a hand-placed band no longer spans cleanly.
- **It signals low effort.** A flat color bar carries no structural information (fails the information test) — it's decoration, and decoration that's slightly misaligned reads as *worse* than none.

## The rule

**Never draw a full-width band per slide.** If a visual accent is wanted, it must come from a source that is identical on every slide by construction. This generator uses both of these:

1. **A Slide Master object.** In PptxGenJS, `pres.defineSlideMaster({ objects: [...] })` registers objects that render at the same coordinates on every slide using that master. The accent hairline (a short ~1 in × ~0.045 in rect) is defined there — so it is byte-for-byte identical on every slide of that family. Drift is impossible because the shape exists once, in the master, not once per slide. `build_deck.js` defines one master per slide family (`TITLE`, `SECTION`, `CONTENT`, `QUOTE`, `PLAIN`); each carries its hairline (and `CONTENT`/`PLAIN` carry the auto page number). Set `rule:false` in the theme to drop the hairline entirely.

2. **A short hairline anchored to the shared grid**, not a full-width fill. Even within the master it is a *short* mark at the left margin, computed from the one `Grid` object. So it never spans edge-to-edge and never depends on title length.

3. **Whitespace and type hierarchy instead of fills.** Most "the title needs to stand out" problems are solved by size/weight/color contrast and margin, not a background fill. A bold 30 pt title on white with generous top margin out-reads a title on a colored band.

## Why a shared grid eliminates drift

`build_deck.js` computes one grid object (`makeGrid`) in inches: left margin, content width, title Y, body top, footer Y, column splits, and the per-family hairline Y. Every renderer and every master reads from that object. So:

- Title text starts at the same `(marginX, top)` on every content slide.
- The hairline sits at the same Y for every slide of a family (it's a master object).
- Columns split the same content width identically.
- Switching `aspect` to `4:3` recomputes `pageW`/`marginX` coherently — nothing is hand-placed, so nothing breaks.

This is the structural reason the output looks designed rather than assembled: alignment is guaranteed, not maintained by hand.

## If a stakeholder insists on a band

Offer the master-level route: add the strip once to the master's `objects` array in the theme (or in PowerPoint's Slide Master view after generation). It will be identical on every slide. Decline to replicate it as a per-slide shape in a renderer — that is the exact thing that drifts.
