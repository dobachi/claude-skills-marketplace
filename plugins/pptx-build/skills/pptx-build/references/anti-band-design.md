# Anti-Band Design

Why this generator never draws full-width "bands" behind titles, and what it does instead. This applies to **default mode** (build-from-scratch); in template-fill mode the template owns all chrome.

## The problem the user reported

A common Office/AI look is a **colored band** — a full-width filled rectangle placed behind the title (or as a footer strip). It looks fine on one slide and then betrays the deck:

- **Edge drift.** The band is drawn per slide. A 1–2 px difference in left/top/width across slides — from copy-paste, manual nudging, or a slightly different layout — makes the edges fail to line up when you flip through. The eye catches the jump instantly.
- **Z-order and overlap.** Bands sit behind text but in front of the background; on a slide with an image or a long title they collide, and the fix is another manual nudge that drifts again.
- **Reflow fragility.** Change the title length or the slide size (16:9 → 4:3) and a hand-placed band no longer spans cleanly.
- **It signals low effort.** A flat color bar carries no structural information (fails the information test) — it's decoration, and decoration that's slightly misaligned reads as *worse* than none.

## The rule

**Never draw a full-width band per slide.** If a visual accent is wanted, it must come from a source that is identical on every slide by construction. This generator uses all three of these:

1. **Coordinates computed once from a shared grid, never hand-placed.** `build_deck.py` builds one `grid` dict (`make_grid`) in inches and every renderer reads from it. The accent hairline (a short ~1 in × ~0.045 in rect) is drawn at `(grid.marginX, grid.ruleY[family])` — the same inputs produce the same EMU coordinates on every slide of a family, so the mark is pixel-identical and cannot drift. Drift only happens when a shape is nudged by hand; nothing here is. Set `rule:false` in the theme to drop the hairline entirely.

2. **A short hairline anchored to the left margin**, not a full-width fill. It is a *short* mark computed from the one grid, so it never spans edge-to-edge and never depends on title length. (If you want the even stronger "exists once" guarantee, the hairline can be promoted onto a python-pptx slide layout so it is inherited rather than re-emitted — but identical computed coordinates already give zero drift.)

3. **Whitespace and type hierarchy instead of fills.** Most "the title needs to stand out" problems are solved by size/weight/color contrast and margin, not a background fill. A bold 30 pt title on white with generous top margin out-reads a title on a colored band.

## Why a shared grid eliminates drift

`build_deck.py` computes one grid dict (`make_grid`) in inches: left margin, content width, title Y, body top, footer Y, column splits, and the per-family hairline Y. Every renderer reads from that dict. So:

- Title text starts at the same `(marginX, top)` on every content slide.
- The hairline sits at the same Y for every slide of a family (same computed coordinates).
- Columns split the same content width identically.
- Switching `aspect` to `4:3` recomputes `pageW`/`marginX` coherently — nothing is hand-placed, so nothing breaks.

This is the structural reason the output looks designed rather than assembled: alignment is guaranteed, not maintained by hand.

## If a stakeholder insists on a band

Offer the master-level route: add the strip once in PowerPoint's Slide Master view after generation (or, better, ship it on a real template and use template-fill mode). It will be identical on every slide. Decline to replicate it as a hand-nudged per-slide shape — that is the exact thing that drifts.
