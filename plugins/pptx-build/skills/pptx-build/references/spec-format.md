# Spec Format

The deck spec is YAML or JSON (detected by file extension). Two top-level keys: `meta` and `slides`. The **same spec drives both modes** — default (`build_deck.py spec -o out.pptx`) and template-fill (`--template corp.pptx`). In template-fill mode the look comes from the template, so `meta` color/font keys are ignored (only `aspect` still has no effect there — the template sets slide size); per-slide `layout:` is honored.

## Contents

- [meta (all optional — omit to keep defaults; default mode only)](#meta-all-optional-omit-to-keep-defaults-default-mode-only) — deck-wide colors, fonts, aspect, type scale
- [meta.shape](#metashape--the-three-numbers-every-part-agrees-on) — spacing unit, corner radius, line weight
- [slides](#slides) — every slide type and its fields
- [Composed archetypes](#composed-archetypes) — cards / steps / lead / matrix / split / statement
- [Contrast](#contrast--the-dark-page-and-the-tonal-chart) — the dark page, the tonal chart
- [Conventions the spec assumes](#conventions-the-spec-assumes) — action titles, one message, sources, one accent
- [Minimal JSON equivalent](#minimal-json-equivalent) — the same spec as JSON

## meta (all optional — omit to keep defaults; default mode only)

| Key | Default | Meaning |
|---|---|---|
| `aspect` | `"16:9"` | `"16:9"` or `"4:3"` — recomputes the whole grid coherently |
| `bg` | `FFFFFF` | Slide background hex (no `#` needed). `FAFAFA` for softer paper |
| `ink` | `1A1A1A` | Primary text. Avoid pure `000000` (halation) |
| `muted` | `6B7280` | Secondary text, captions, sources |
| `accent` | `2F5DA8` | The single accent — hairline + emphasis only |
| `rule` | `true` | Draw the short master-level accent hairline under titles. `false` to drop it |
| `font_heading` | `Yu Gothic Medium` | Heading typeface |
| `font_body` | `Yu Gothic` | Body typeface |
| `font_number` | `Yu Gothic Medium` | Typeface for the `big_number` figure |
| `page_numbers` | `true` | Footer page numbers on content slides |
| `size` | — | Map of type-size overrides (see below). Omit to use the readable defaults |

These override the active theme JSON (`--theme`, default `themes/minimal-white.json`) for one deck in default mode. To change the look permanently, edit/copy the theme file. For an actual `.pptx`/`.potx` template, use `--template` instead — see `template-mode.md`.

Colors take a bare hex (`2F5DA8`) or `#2F5DA8`.

### meta.size — readable type scale (optional; default mode only)

Every size the default renderer uses is routed through one type scale, so text can never silently fall back to tiny. Override only what you need:

| Key | Default | Used for |
|---|---|---|
| `title_max` / `title_min` | `30` / `24` | Title auto-fit range — see below |
| `body` / `body_sub` | `18` / `16` | Bullets at level 0 / level 1+ |
| `caption` / `caption_note` | `15` / `14` | Figure caption label / explanation (`image` slide) |
| `big_caption` | `20` | Caption under a `big_number` |
| `subtitle` `section` `quote` `source` `page_number` … | see `SIZE_DEFAULTS` in `build_deck.py` | Other elements |

```yaml
meta:
  size: { body: 20, title_min: 26 }   # bigger floors for a low-density deck
```

**Titles are master-governed and cannot overlap.** Each title is written into a slide-layout **title placeholder** whose geometry is configured once and **bottom-anchored**, so a two-line title grows *upward* into the top margin and never reaches the hairline or body. The renderer auto-fits the title to the **largest** size in `[title_min, title_max]` that keeps it to two lines — it never shrinks below `title_min`. If a title needs more than two lines even at the floor, the build prints a `warning:` to shorten or split it (it is **not** crammed into illegible type). The same warning fires when bullet content won't fit the body at readable sizes — split the slide instead.

### meta.shape — the three numbers every part agrees on

Composed parts (cards, steps, quadrants) are drawn, not typed, so they need a
geometry vocabulary. There are exactly three values, and everything derives from
them — every gap, padding and offset in a part is an integer multiple of `unit`.

| Key | Default | Meaning |
|---|---|---|
| `unit` | `0.0833` | The spacing scale's base, in inches (8 px at 96 dpi) |
| `radius` | `0.06` | The **only** corner radius. `0` gives square corners |
| `line` | `0.75` | The **only** line weight, in points |

```yaml
meta:
  shape: { radius: 0, line: 1 }     # a squarer, slightly firmer deck
```

Four colors come with them, and by default all four are **derived from the
accent** rather than being neutral greys: `surface` (a part's ground),
`surface_hi` (a highlighted part's ground), `border` (its edge), and `invert_bg`
(the dark page). A pure grey beside a colored accent reads as a second color; the
same grey carried a few percent toward the accent reads as one hue at several
weights. Pin any of them to a literal hex in the theme JSON to opt out; `"auto"`
(the default) asks for the derived value.

The derivation works in **HSL**, not by mixing with white: white-mixing drops
saturation as it raises lightness, and the pale steps come out muddy — visibly so
behind thin Japanese strokes.

**The ground decides the direction.** A `bg` darker than mid-grey puts the deck in
dark mode: surfaces and borders become dark tints of the accent, and an `invert:`
page becomes *light* — the turn has to stand away from the ground it sits on.
Nothing else in the spec changes, so the same deck builds in either mode.

## slides

A list. Each item has a `type` and type-specific fields. Default type is `bullets`.

Any slide may also carry `layout:` (a layout name or index). It is used only in template-fill mode, to pin which template layout that slide lands on, overriding the map/heuristic. Ignored in default mode.

Any slide may also carry `notes:` — a string written into the slide's real **speaker-notes** page, in both modes. Extraction recovers it (`extract_deck.py`), so notes survive a refactor round trip; what the presenter says is half the argument and a rebuild that drops it loses that half.

```yaml
- type: bullets
  title: "解約率は3四半期連続で低下、ただし新規獲得が鈍化"
  bullets: ["…"]
  notes: "ここで欠品の実害を口頭で補足する"
```

### title
```yaml
- type: title
  title: "Deck title"
  subtitle: "optional kicker"        # optional
```

### section (divider)
```yaml
- type: section
  number: "01"                       # optional, shown in accent
  title: "Section name"
```

### bullets
```yaml
- type: bullets
  title: "Action title — state the conclusion"
  bullets:
    - "Top-level point"              # string => level 0 (en-dash marker)
    - text: "Sub-point"              # dict => set level
      level: 1                       #   level 1 => indented round bullet, muted
  source: "出典: …"                  # optional footnote
```
Levels: `0` = ink en-dash; `1`+ = muted, indented round bullet with a real hanging indent. Keep to two levels.

### two_col
```yaml
- type: two_col
  title: "Action title"
  left:
    heading: "Column heading"        # optional, accent-colored
    bullets: ["…", {text: "…", level: 1}]
  right:
    heading: "Column heading"
    bullets: ["…"]
  source: "…"                        # optional
```
Both columns split the same grid content width — edges align by construction.

### big_number
```yaml
- type: big_number
  title: "Action title"
  number: "94%"                      # large accent figure
  caption: "what the number is"      # optional
  source: "…"                        # optional
```

### quote
```yaml
- type: quote
  quote: "The quotation text."
  attribution: "Name"                # optional
```

### image
```yaml
- type: image
  title: "Action title"              # optional; omit for full-area image
  image: "/path/to/figure.png"       # fit to remaining area, height-capped, centered
  caption: "図1: what the figure shows"   # optional — a BOLD, readable label (not a footnote)
  note: "One or two sentences explaining what the reader should take away."  # optional
  source: "出典: …"                  # optional footnote (smaller, muted)
```
Relative `image:` paths resolve against the **spec file's directory** first (falling back to the working directory), so a spec and its `deck_media/` folder — what `extract_deck.py` produces — can be moved together and built from anywhere.

In default mode the slide is built on the **Picture with Caption** layout: the figure is fitted (uncropped, aspect preserved) into that layout's real **PICTURE-placeholder region**, and the caption goes in its **caption placeholder** below — the image sits in the master's designated region, not free-floated on a blank slide. The caption is a real caption block, not a 10pt footnote: `caption` renders as a **bold ink label** and `note` (alias `description`) as a wrapping muted explanation, both at readable sizes (`caption` / `caption_note` in `meta.size`), so the figure and its explanation never collide. `source` remains a small footnote at the very bottom. If the image path is missing, a placeholder marker is drawn (and a `warning:` printed) so the deck still builds.

Prefer a `caption` that names the figure and a `note` that states the takeaway — a figure without an explanation makes the audience guess.

### table
```yaml
- type: table
  title: "Action title — what the table proves"
  columns: ["方式", "初期費用", "年間運用", "備考"]   # optional header row
  rows:
    - ["方式A", "1.2億円", "2,400万円", "既存資産を流用"]
    - ["方式B", "0.9億円", "1,800万円", "推奨"]
  widths: [1, 1, 1, 2]              # optional relative column widths
  source: "出典: 社内試算 2026-07"
```
`rows` may also be a list of dicts keyed by the `columns` names. The table is inserted at the
**body placeholder's** region and adopts its placeholder marker, so it stays master-governed.
Default mode draws it plain — no banded template style, transparent cells, bold header with an
accent hairline under it, light hairlines between rows; template-fill mode uses the template's
own table style. Readability ceilings the linter enforces: **6 columns, ~8 rows**. Beyond that,
split the table or move the detail to an appendix — a slide is not a spreadsheet.

### chart
```yaml
- type: chart
  title: "Action title — the conclusion the chart supports"
  chart: column          # column | bar | line | area | pie | doughnut
  categories: ["1年目", "2年目", "3年目"]
  series:
    - name: "方式B"
      values: [1800, 1800, 1800]
    - name: "方式C"
      values: [1200, 1200, 1200]
  legend: true           # optional; default = only when there is >1 series
  gridlines: false       # optional; default off (value axis)
  data_labels: false     # optional
  source: "出典: 社内試算 2026-07"
```
Also inserted at the body placeholder's region with its placeholder marker. Default mode gives
one accent-led palette, no chart-area border and **no chart title** — the slide title carries
the message, so a chart title would repeat it. Template-fill mode leaves colors to the
template's theme. `series` may also be given as a mapping `{name: [values]}`. Pie/doughnut take
exactly one series and stay readable to about 6 slices; past that use `bar`.

## Composed archetypes

Five types below are **compositions**, not text containers: the renderer draws
them from the body placeholder's region. Each one exists for one shape of
content, and the item count is part of that claim — `validate_deck.py` enforces
the ranges, because a count outside them means the content is not that shape.

The composition is what carries the meaning, so pick the type from the content:
equivalent units → `cards`; a real sequence → `steps`; two meaningful axes →
`matrix`; a figure and its reading → `split`; a turn in the argument →
`statement`.

### cards
```yaml
- type: cards
  title: "Action title"
  cards:                              # 2-4 EQUIVALENT units
    - {label: "承認の直列化", text: "5部署を順に回すため平均42日"}
    - {label: "仕様の後出し", text: "着手後の変更が6割で発生"}
  emphasis: 1                         # optional, 1-based: tint one card
  source: "出典: …"
```
Equivalence is the condition. Items that are not the same kind of thing are a
list — use `bullets`. The row is centered in the region and every card is the
same height, so the eye compares them instead of ranking them.

### steps
```yaml
- type: steps
  title: "Action title"
  steps:                              # 3-5 stages, in order
    - {label: "起案", text: "現場が申請"}
    - {label: "一次審査", text: "部門長"}
    - {label: "決裁", text: "役員"}
```
The **only** archetype that draws arrows, because here the arrow encodes the
order the content actually has. Stages are numbered (01, 02, …) for the same
reason. If the items have no order, they are `cards`.

### lead
```yaml
- type: lead
  title: "Action title"
  lead: {label: "並列承認への切替", text: "規程改正だけで来月から着手できる"}
  rest:                               # 2-3 supporting items
    - {label: "帳票の統合", text: "来期に検討。効果は限定的"}
    - {label: "制度改正", text: "半年かかる。並行して準備"}
```
The one archetype whose parts are deliberately **unequal**: the lead takes 46% of
the width and the full height, the rest stack beside it. `cards` says "compare
these"; `lead` says "this one, and the others are context". Area is the argument,
so use it only when one item really does outweigh the others.

### matrix
```yaml
- type: matrix
  title: "Action title"
  x_axis: ["着手が遅い", "着手が早い"]   # [low, high]
  y_axis: ["効果が小さい", "効果が大きい"]
  quadrants:                          # exactly 4: TL, TR, BL, BR
    - {label: "制度改正", text: "効果は大きいが半年かかる"}
    - {label: "並列承認", text: "規程変更だけで来月から"}
    - {label: "帳票統合", text: "効果は限定的で工数も大きい"}
    - {label: "テンプレ整備", text: "すぐ効くが効果は小さい"}
  emphasis: 2
```
Both axes have to mean something and all four quadrants have to say something.
A matrix with an empty quadrant is four boxes wearing a matrix.

### split
```yaml
- type: split
  title: "Action title"
  image: "figures/funnel.png"
  heading: "読み取れること"            # optional, accent-colored
  bullets: ["…", "…"]                 # <= 4 — the figure is the message
  flip: true                          # optional: figure on the LEFT
  ratio: 0.32                         # optional: the TEXT column's share (0.25-0.50)
  source: "出典: …"
```
The asymmetric composition — 38% reading, 62% figure, either way round (`flip`).
`ratio` moves that split when the figure needs it: a wide figure wants more of
the slide (`0.30`), a tall one less (`0.45`). A very wide figure (about 2:1 or
wider) is usually a full-width `image` slide instead — in a side-by-side it ends
up small no matter how the columns are set. Symmetry claims the two
halves are equal; a figure and its explanation are not. The text stays in the
layout's body placeholder (re-placed into the narrow column), so the slide is
still master-governed.

### statement
```yaml
- type: statement
  text: "調達に3か月かかる限り、どの改善案も間に合わない"
  sub: "第2四半期 事業レビュー"        # optional
```
One sentence, alone, under the rule — the deck's punctuation at a turn or a
verdict. Keep it to about 46 display-width characters so it lands in one breath.
It is not "a slide with little on it": emptiness here is the emphasis.

## Contrast — the dark page and the tonal chart

### invert (section / statement only)
```yaml
- type: section
  number: "02"
  title: "打ち手"
  invert: true            # deep accent-toned page, light text, lighter rule
```
A deck of white slides has no contrast at the **deck** level — every page weighs
the same. One inverted page at a turn in the argument fixes that, and it is not
the drifting band this skill refuses to draw: it is the whole page, so there is
no edge to misalign. Allowed on `section` and `statement` only, because those are
the types that mark a turn. Every color on it is the same hue at a different
lightness.

Use it two or three times in a deck. Inverted pages that repeat stop being
punctuation and become a second template.

### series_style (chart)
```yaml
- type: chart
  chart: column
  series_style: tonal     # focus (default) | tonal
```
| Style | Palette | Right when |
|---|---|---|
| `focus` | accent + greys that recede | One series carries the message and the rest are context |
| `tonal` | one hue at four lightnesses | The series are the same kind of thing and the comparison is between them |

`tonal` steps are at least 0.13 apart in lightness so they survive projection and
greyscale, but a tonal chart still needs its series **labelled at the mark**
(annotation or data labels) rather than by a legend alone — color-blind readers
and photocopiers both flatten a single hue.

### blank
```yaml
- type: blank
  title: "optional title only"
```

## Conventions the spec assumes

- **Action titles.** The `title` should be the takeaway, not a topic. "Q3 ARR grew 22%", not "Q3 Results".
- **Titles fit one line.** Keep a title to roughly 22 full-width characters. The renderer auto-fits down when a title wraps, so a long title silently costs you the size jump between title and body — the length limit is what makes a large title possible.
- **One message per slide.** Split rather than overfill. If bullets need <18 pt to fit, there are too many.
- **Sources on data.** Any slide showing a number gets a `source:`.
- **One accent.** Don't add more colors via `meta`; emphasis comes from the single accent + weight + size.

## Minimal JSON equivalent

```json
{
  "meta": {"accent": "2F5DA8"},
  "slides": [
    {"type": "title", "title": "…", "subtitle": "…"},
    {"type": "bullets", "title": "…", "bullets": ["…", {"text": "…", "level": 1}]}
  ]
}
```
