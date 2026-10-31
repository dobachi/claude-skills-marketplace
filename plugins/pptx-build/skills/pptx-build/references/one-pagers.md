# One-pagers

One slide that carries the whole argument, read on paper or on a screen at arm's length rather
than projected. Five shapes ship, all drawn from native parts (no picture of a diagram, ever).

## Contents

- Pick the shape from what the reader must do
- The reading order is the layout
- Density and size floors
- What every one-pager needs
- Anti-patterns

## Pick the shape from what the reader must do

| The reader should… | Shape | Spec | Why this shape |
|---|---|---|---|
| understand what happened and what follows | **brief** | `panels` + `columns` (3–4) + `arrows: true` + `takeaway` | causality reads left to right; the arrow says "therefore" so the text does not have to |
| see status and approve one thing | **dashboard** | `dashboard` (`tiles` + `columns` + `takeaway`) | numbers first, because the reader checks the numbers before reading a word |
| see when things happen and where we stand | **timeline** | `figure` `kind: timeline` + `lead` | a sequence with dates has one honest shape |
| choose between options | **decision memo** | `decision` | the question, a comparison on named criteria, and a recommendation the reader can accept or reject |
| get the debrief of an event | **event report** | `panels` + `tiles` (facts) + 3 `columns` (highlights / our angle / next) + `arrows` | the facts row answers "what was it" in a glance; the columns separate what was seen from what we make of it |

When two shapes fit, choose the one whose takeaway is a single sentence the reader will act on.
If no sentence is the takeaway, the page is a reference table, not a one-pager: use `table`.

## The reading order is the layout

A one-pager is read top-left to bottom-right, and the layout should agree with the argument:

1. **Title**: the claim, short. On a one-pager it is the only large text, so it must be the point.
2. **`lead:`**: the one sentence that supports the claim. Set it; the reader who stops here leaves
   with the message.
3. **Facts or numbers** (`tiles`): what happened, before what it means.
4. **Columns**, left to right: context → findings → implications → next. `arrows: true` makes the
   order explicit. Each column has a `label` so a reader can enter anywhere.
5. **Takeaway band**: the sentence the reader takes away, or the ask. Last, because it is what
   remains on the retina.

Put interpretation in its own column (「当社の切り口」「示唆（考察）」) so that what was observed
and what we make of it never share a bullet.

## Density and size floors

A one-pager is read, so the floors are lower than for a projected slide but not by much:

| Element | Floor | Default |
|---|---|---|
| Title | 28 pt | auto-fit 28–34 |
| Lead | — | 20 pt bold |
| Column body (`panel_body`) | 12 pt | 14 pt |
| Notes (`panel_note`) | 12 pt | 12 pt |
| Figure labels (`panel_fig_label`) | 12 pt | 14 pt |
| Tile number | — | 32 pt |

The builder warns when a column needs more height than it has. The fix is to cut, not to shrink:
a one-pager that needs 10 pt text is a two-pager. Three columns of 3–4 short lines each plus one
figure is the comfortable load for 16:9.

Numbers inside a sentence are emphasized the Japanese way — `29%から **15%** に低下` — the
number large inside the line, not a big number with a small caption floating above.

## What every one-pager needs

- a `source:` line (date, place, counts and where they came from)
- the confidentiality / ownership line if the organization uses one (`meta.footer` or the template's own)
- a takeaway or an ask; a page that only informs is a handout, and that is fine, but say so
- every figure native: `flow`, `diagram`, `timeline`, `tiles`, `chips`, `staircase`, `stacked_bar`

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| The whole page as one PNG | nothing can be edited, fonts do not match, it blurs | native `panels` / `dashboard` / `decision` |
| Title that is the full argument | 40 characters at 24 pt reads like a bullet | short claim + `lead:` |
| Findings and interpretation in one list | the reader cannot tell what was seen from what we think | separate column, labelled 考察 |
| Four columns of six lines each | 10 pt text; nobody reads it | cut to the takeaway; move detail to the Word version |
| Numbers only in sentences on a dashboard | the reader scans for numbers and finds prose | `tiles` first |
| A decision memo without a recommendation | asks the reader to do the analysis | `recommend` with a one-sentence reason |
