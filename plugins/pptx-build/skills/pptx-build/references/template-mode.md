# Template-Fill Mode — using a real `.pptx`/`.potx`

How to make the generator write into a template the user actually hands you, so the
output inherits that template's master, theme, fonts, logos, and **placeholders**.

## Contents

- [Why this is a real engine feature now](#why-this-is-a-real-engine-feature-now) — what python-pptx makes possible
- [The workflow: inspect → (map) → fill](#the-workflow-inspect-map-fill) — the three commands, in order
- [How resolution works (precedence)](#how-resolution-works-precedence) — which layout and placeholder a slide lands on
- [Annotation placeholders](#annotation-placeholders-source-section-label-section-number) — source line, section label, section number as real placeholders
- [Figures land in the picture placeholder](#figures-land-in-the-picture-placeholder) — `split`, and `fit: contain`
- [Dark turn pages, tables, headings](#dark-turn-pages-tables-headings) — `invert`, default table style, `nest_under_heading`
- [What carries the look](#what-carries-the-look) — master, theme, fonts, logos
- [Nothing is dropped silently](#nothing-is-dropped-silently) — the warnings that tell you content did not land
- [When the binary master itself must be carried — this is it](#when-the-binary-master-itself-must-be-carried-this-is-it) — the case only this mode covers

## Why this is a real engine feature now

python-pptx can **open an existing presentation** and add slides from its layouts:

```python
prs = Presentation("corp.pptx")          # the real template, master + theme + logos
slide = prs.slides.add_slide(prs.slide_layouts[1])   # a layout from the template
slide.placeholders[0].text = "..."       # write the title placeholder it defines
```

That is the whole fix. The earlier PptxGenJS engine built from scratch and could not
touch a binary template's placeholders, so "use our template" silently degraded to
"transcribe the colors." Now the template's layouts and placeholders are first-class.

## The workflow: inspect → (map) → fill

Foreign templates have arbitrary layout names and placeholder indices. Don't guess —
**inspect first.**

### 1. Inspect

```bash
python3 inspect_template.py corp.pptx
```

Prints every layout (with its index) and every placeholder on it: `idx`, semantic
`type` (TITLE / CENTER_TITLE / SUBTITLE / BODY / OBJECT / PICTURE …), name, position,
and size. This is the ground truth for "which placeholder is the title."

### 2. Map (optional but recommended for odd templates)

```bash
python3 inspect_template.py corp.pptx --map > map.json
```

Emits a starter map: for each slide `type`, the layout index and the placeholder
`idx` for each role. Open it, fix any wrong guess, delete roles you don't want filled.

```json
{
  "title":      {"layout": 0, "title": 0, "subtitle": 1},
  "section":    {"layout": 2, "title": 0},
  "bullets":    {"layout": 1, "title": 0, "body": 1},
  "two_col":    {"layout": 3, "title": 0, "left": 1, "right": 2},
  "big_number": {"layout": 1, "title": 0, "body": 1},
  "image":      {"layout": 8, "title": 0, "image": 1, "caption": 2},
  "statement":  {"layout": 5, "title": 0},
  "blank":      {"layout": 6}
}
```

- `layout` is an **index** (int) or a **name** (string, case-insensitive substring match).
- Role values (`title`, `subtitle`, `body`, `left`, `right`, `image`, `caption`,
  `source`) are placeholder **idx** values from the inspect output.

### 3. Fill

```bash
python3 build_deck.py deck.yaml -o out.pptx --template corp.pptx           # auto-detect
python3 build_deck.py deck.yaml -o out.pptx --template corp.pptx --map map.json
```

The build log prints which layout each slide landed on:

```
title       -> layout 'Title Slide'
bullets     -> layout 'Title and Content'
two_col     -> layout 'Two Content'
```

Read that log. If a slide picked the wrong layout, pin it (below) and rerun.

## How resolution works (precedence)

For each spec slide, the layout is chosen by: **per-slide `layout:` in the spec → the
map → a name/type heuristic.** Placeholders are chosen by: **explicit idx in the map →
placeholder type on the chosen layout** (title = TITLE/CENTER_TITLE; body = the
BODY/OBJECT placeholders in reading order; subtitle = SUBTITLE; picture = PICTURE).

The auto-heuristic (no map) matches common layout names in English and Japanese
— "Title Slide"/"タイトル スライド", "Section Header"/"セクション"/"中扉", "Title and
Content"/"タイトルとコンテンツ", "Two Content"/"Comparison"/"2 つのコンテンツ"/"比較",
"Picture with Caption"/"図"/"画像", "Blank"/"白紙" — and falls back to a content
layout. A `statement` looks for the template's one-message page ("Title Only"/
"タイトルのみ"/"メッセージ"/"キーメッセージ"), then the section divider, then content.
The word table is `LAYOUT_WORDS` in `build_deck.py`; `inspect_template.py --map` reads
the same table. Reach for a map only when names are non-standard or a guess is wrong.

`meta.footer` and `meta.page_numbers: true` also work here: each built slide gets its
own instance of the layout's FOOTER / SLIDE_NUMBER placeholder (geometry and style stay
the template's). Layouts without those placeholders are skipped silently. The title
slide's `presenter` / `affiliation` / `date` go into the title layout's second body
placeholder when it has one, else as lines under the subtitle.

### Pinning one slide without a whole map

```yaml
- type: bullets
  layout: "Title and Content"   # name or index, overrides the heuristic/map for this slide
  title: "…"
  bullets: ["…"]
```

## Annotation placeholders: source, section label, section number

The small print of a slide is content too, and a textbox per slide is exactly what a
master exists to avoid. A template can offer a placeholder for each; the build finds it
by the **name the placeholder has on the layout** (case-insensitive substring), fills it,
and removes it from slides that have nothing to put there.

| Role | Layout placeholder name contains | Filled with |
|---|---|---|
| `source` | `source`, `出典` | the slide's `source:` — on **every** slide type, tables and two-column slides included |
| `eyebrow` | `eyebrow`, `section label`, `章名`, `セクション名` | the running section label (`01  Title`) on content pages after the first `section` |
| `number` | `section number`, `章番号`, `セクション番号` | a `section` slide's `number:` |

These placeholders are BODY-typed, but they are never taken for the content slot. The
`--map` roles `source` / `eyebrow` / `number` (placeholder idx) override the name match.

A `source:` the chosen layout has no place for is **reported**, like any other dropped
content — it used to vanish without a word:

```
  warning: slide 9: layout 'Title and Content' has no source placeholder — the source line
           was NOT written. Name a placeholder 'Source' on the layout or map the `source` role.
```

## Figures land in the picture placeholder

- **`split`**: when the template has a figure-and-text layout — a layout named
  `図と説明` / `figure and text` / `picture and text` holding a PICTURE placeholder and a
  body — the figure goes into the PICTURE placeholder and the heading + bullets into the
  body as plain levels (heading at level 0, bullets at level 1). The proportions and the
  type are the layout's; `ratio:` is ignored. Pin a variant per slide with `layout:` (a
  wide figure wants a layout with the picture above the text). Without such a layout the
  split is drawn into the body region as before.
- The figure is fitted **whole** into the placeholder's box and centred. `insert_picture`
  crops to fill, which is right for a photograph and wrong for a diagram. An `image` slide
  keeps the crop by default; `fit: contain` on the slide fits it whole.

## Dark turn pages, tables, headings

- **`invert: true`** on a `section` / `statement` picks the template's dark variant: a
  layout whose name carries the type's word **and** one of `invert` / `dark` / `濃色` /
  `反転`. The dark page is then a layout — background, colors and all. A dark variant is
  never chosen unless asked for.
- **Tables** take the template's **default table style** (`<a:tblStyleLst def="…">`)
  instead of the Office style python-pptx stamps on every new table, and honor `widths:`.
- **`meta.nest_under_heading: true`** puts a `two_col` column's bullets one level below
  its heading, so the template can style heading (level 0) and bullets (level 1) apart.
- The content layout is chosen **by name first**; "the first layout with a body" is only
  the fallback. (Taken first, it lands on a title slide that merely has a presenter block.)

## What carries the look

In template-fill mode the **template owns the look** — colors, fonts, the master's
logos and chrome, the bullet styling of each BODY placeholder. So:

- We write **plain text / bullet levels** into placeholders and let the template style
  them. We do **not** override fonts or colors, and `meta.*` color/font keys are ignored.
- `two_col` needs two BODY/OBJECT placeholders (e.g. the "Two Content" layout). If the
  chosen layout has only one, the right column is appended into it rather than dropped.
- `image` uses a PICTURE placeholder when the layout has one (`insert_picture`); else
  the image is added at the placeholder's box, or top-left as a fallback.
- `quote`/`big_number` reuse the title+body of a content layout (the quote/number go in
  the body) unless you map them to a dedicated layout.
- `table`/`chart` are inserted **at the body placeholder's own region** and take over its
  placeholder marker (the same shape PowerPoint produces when you insert a table into a
  content placeholder), so they remain master-governed. Their look is the template's: the
  table keeps the template's table style and theme fonts, the chart its theme colors. The
  plain-table styling and the accent palette of default mode are deliberately not applied.

## Nothing is dropped silently

Template-fill can only write into placeholders the chosen layout actually has. Whenever the
spec supplies content for a role the layout lacks, the build now prints a `warning:` naming
the slide, the layout, and the missing role — and the run ends with a count of them:

```
  warning: slide 4: layout 'Title Only' has no body placeholder — that content was NOT
           written. Pin a layout with `layout:` or map the role in --map.
  1 template warning(s) above — content may be missing from the deck.
```

Fix it by pinning a different layout on that slide (`layout: "Two Content"`) or by mapping
the role to a placeholder idx in `--map`. Then confirm with `audit_pptx.py`, which reads the
produced file and fails it if a slide's content ended up outside placeholders.

## When the binary master itself must be carried — this is it

This *is* the path that carries the binary corporate master/theme/logos through. The
only thing it does not do is invent layouts the template lacks; if the template has no
"Two Content" layout, map `two_col` to whatever two-region layout it does have, or fall
back to default mode for those slides.
