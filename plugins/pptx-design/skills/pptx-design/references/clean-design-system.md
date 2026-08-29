# Clean Design System

The default look this skill recommends, as decided values rather than ranges.
`visual-design.md` explains the underlying theory and the cases for departing
from it; this file is what you apply when nobody asked for something else.

It is the same system `pptx-build` renders, token for token — the right-hand
column of each table is the key that sets it. Advice that cannot be produced is
not advice, so if you change a value here, change it there.

## Contents

- [What "clean" means](#what-clean-means) — subtractive, not sparse
- [Tokens](#tokens) — color, type, grid
- [The five rules](#the-five-rules)
- [Density budget](#density-budget) — how much fits before a slide splits
- [Layout archetypes](#layout-archetypes) — what earns each one
- [Emphasis without adding color](#emphasis-without-adding-color)
- [Brand and dark variants](#brand-and-dark-variants)
- [Cleanliness check](#cleanliness-check)
- [What clean is not](#what-clean-is-not)

## What "clean" means

Clean is **subtractive**. A slide is clean when nothing on it can be removed
without losing meaning — not when it has little on it. The two failures look
opposite and are the same mistake: a slide crowded with boxes that encode
nothing, and a slide holding three words that prove nothing.

The operative question for every element: **what would the audience not know if
this were deleted?** No answer means delete it. That is the information test
(`diagrams-and-architecture.md`) applied to ornament as well as diagrams.

A deck also reads as clean only if it is clean *across* slides. Titles on one
baseline, one rule position, one margin — repetition is what makes a deck look
designed rather than assembled. This is why the system is a slide master, not a
set of per-slide choices.

## Tokens

### Color — four slots, no fifth

| Slot | Value | Used for | `pptx-build` |
|---|---|---|---|
| Paper | `#FFFFFF` (or `#FAFAFA`) | Background, every slide | `meta.bg` |
| Ink | `#1A1A1A` | Titles, body — never pure `#000000` | `meta.ink` |
| Muted | `#6B7280` | Sub-bullets, captions, sources, page numbers | `meta.muted` |
| Accent | one brand color (default `#2F5DA8`) | The title hairline and the single emphasis per slide | `meta.accent` |

Semantic colors (red = decline, green = growth) are a fifth slot that exists
**only inside charts and tables**, never in body text or ornament. Body text has
exactly three colors: ink, muted, accent.

### Type — one scale, with floors

| Element | pt | `meta.size` key |
|---|---|---|
| Deck title (title slide) | 40 | `title_slide` |
| Section divider | 34 | `section` |
| Slide title | 30, auto-fitting down to **24** | `title_max` / `title_min` |
| Body, level 0 | 18 | `body` |
| Body, level 1 | 16 | `body_sub` |
| Figure caption / its note | 15 / 14 | `caption` / `caption_note` |
| Table text | 15 | `table` |
| Source, page number | 11 | `source` / `page_number` |
| Big number | 88 | `big_number` |
| Quote | 28 | `quote` |

18 pt body is a **floor, not a target**. Text is never shrunk to make content
fit: content is cut or split until it fits at the floor. Two typefaces at most —
one family with weight variation is cleaner still.

### Grid — 16:9, in inches

| Measure | Value | Why |
|---|---|---|
| Side margin | 0.92 | Content width 11.49 on a 13.33 × 7.5 slide |
| Title top | 0.62 | Title block is bottom-anchored, so a two-line title grows upward |
| Title height | 1.04 | One baseline across every slide |
| Gap under title | 0.22 | Where the accent hairline sits (length 1.05, weight 0.045) |
| Footer line | 7.04 | Source and page number below it; nothing else |

Everything on a slide aligns to the left margin or to a column edge derived from
it. Two columns split the content width with a 0.5 gutter, so their edges line
up by construction rather than by eye.

## The five rules

1. **White paper, ink text.** No colored backgrounds, no full-width bands behind
   titles. A band that must be redrawn per slide will drift, and drift is the
   most recognizable tell of a generated deck.
2. **One accent, used twice at most per slide.** The hairline is one of them.
3. **One type scale.** Sizes come from the table above; no slide invents its own.
4. **One grid.** If an element does not sit on a margin or a column edge, move it.
5. **No ornament.** No gradients, shadows, bevels, WordArt, clipart, rounded
   decorative frames, hexagons, or connectors that represent nothing.

## Density budget

Exceeding a budget is a signal to split the slide, not to shrink the type.

| Slide kind | Budget |
|---|---|
| Bullets | ≤ 6 top-level bullets; ≤ 2 levels; ~1 line each, 2 at the very most |
| Two columns | ≤ 4 bullets per column; both columns on the same subject |
| Table | ≤ 6 columns × ~8 rows; beyond that it is an appendix, not a slide |
| Chart | ≤ 4 series; pie ≤ 6 slices (past that, a bar chart) |
| Figure | 1 per slide, with a caption naming it and a note stating the takeaway |
| Any slide | 1 message. Two arguments = two slides. Slides are free |

Whitespace target: roughly a quarter of the slide stays empty. If nothing is
empty, something on it is not carrying its weight.

## Layout archetypes

Pick the archetype from what the slide has to prove — not from what the content
happens to look like.

| The slide proves | Archetype | Earned when |
|---|---|---|
| A claim, by argument | Title + bullets | The points are parallel and independent |
| A contrast | Two columns | Both sides are the same kind of thing (before/after, kept/cut) |
| A single fact | Big number + caption | One figure is the message; a chart would add nothing |
| A trend or comparison | Chart | The shape of the data is the argument |
| A precise set of values | Table | The reader needs to look values up, not see a shape |
| A mechanism or flow | Figure + caption + note | Structure exists to encode (else it is a list in costume) |
| A framing or a turn | Quote, or section divider | The deck changes subject or needs a beat |

## Emphasis without adding color

Emphasis is a ladder. Climb it in order and stop at the first rung that works —
reaching for color first is what makes decks loud.

1. **Position** — put it first, or alone.
2. **Isolation** — whitespace around it.
3. **Size** — one step up the scale, not two.
4. **Weight** — bold, on a few words rather than a sentence.
5. **Accent color** — last, and once per slide.

Never: underline (reads as a link), italics for emphasis in Japanese, ALL CAPS
for長い phrases, or two rungs at once on the same element.

## Brand and dark variants

A brand palette does not change the system; it fills the same slots. Transcribe
the brand's primary into **accent**, keep paper and ink neutral, and check the
contrast (4.5:1 for body, 3:1 for ≥18 pt) before adopting it — many brand blues
fail on white at body size and are fine as a hairline only.

Dark decks swap paper and ink (`#111315` paper, `#F2F2F2` ink, muted around
`#9AA1AC`) and nothing else. Choose one and hold it for the whole deck; a deck
that switches backgrounds mid-way reads as two decks.

When the organization has a real `.pptx` template, do not apply this system on
top of it — fill the template instead (`pptx-build --template`), and let its
master carry the look. Mixing the two produces a deck that matches neither.

## Cleanliness check

Run down this list against a rendered deck (or its PNG previews):

- [ ] Every slide's title sits on the same baseline — flip the slides and watch it
- [ ] The accent hairline never jumps position between slides
- [ ] Exactly one accent color appears, and at most twice per slide
- [ ] No slide has a colored band, gradient, shadow, or decorative shape
- [ ] Body text is at 18 pt or the deck's declared floor — nothing was shrunk to fit
- [ ] Every slide passes the density budget above
- [ ] Left edges of titles, body, and footnotes align to one margin
- [ ] Each data slide carries a source line at 11 pt, muted
- [ ] Nothing on any slide could be deleted without the audience losing something

## What clean is not

- **Not sparse.** Three words on a white slide is not clean, it is empty. Clean
  is dense in meaning and quiet in ornament.
- **Not white-only.** Charts and tables use as many colors as the data needs.
- **Not "minimal template".** A stock minimal theme applied verbatim reads as a
  stock theme. The look comes from the grid and the restraint, not the theme file.
- **Not a reason to cut evidence.** Sources, units, and caveats stay. Delete
  decoration, never the proof.
