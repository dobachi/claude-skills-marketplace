# Template-Fill Mode — using a real `.pptx`/`.potx`

How to make the generator write into a template the user actually hands you, so the
output inherits that template's master, theme, fonts, logos, and **placeholders**.

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

The auto-heuristic (no map) matches common layout names — "Title Slide", "Section
Header", "Title and Content", "Two Content"/"Comparison", "Picture with Caption",
"Blank" — and falls back to a content layout. It handles the standard PowerPoint
layout set well; reach for a map only when names are non-standard or a guess is wrong.

### Pinning one slide without a whole map

```yaml
- type: bullets
  layout: "Title and Content"   # name or index, overrides the heuristic/map for this slide
  title: "…"
  bullets: ["…"]
```

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

## When the binary master itself must be carried — this is it

This *is* the path that carries the binary corporate master/theme/logos through. The
only thing it does not do is invent layouts the template lacks; if the template has no
"Two Content" layout, map `two_col` to whatever two-region layout it does have, or fall
back to default mode for those slides.
