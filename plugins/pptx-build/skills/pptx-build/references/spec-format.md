# Spec Format

The deck spec is YAML or JSON (detected by file extension). Two top-level keys: `meta` and `slides`. The **same spec drives both modes** — default (`build_deck.py spec -o out.pptx`) and template-fill (`--template corp.pptx`). In template-fill mode the look comes from the template, so `meta` color/font keys are ignored (only `aspect` still has no effect there — the template sets slide size); per-slide `layout:` is honored.

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

## slides

A list. Each item has a `type` and type-specific fields. Default type is `bullets`.

Any slide may also carry `layout:` (a layout name or index). It is used only in template-fill mode, to pin which template layout that slide lands on, overriding the map/heuristic. Ignored in default mode.

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
In default mode the slide is built on the **Picture with Caption** layout: the figure is fitted (uncropped, aspect preserved) into that layout's real **PICTURE-placeholder region**, and the caption goes in its **caption placeholder** below — the image sits in the master's designated region, not free-floated on a blank slide. The caption is a real caption block, not a 10pt footnote: `caption` renders as a **bold ink label** and `note` (alias `description`) as a wrapping muted explanation, both at readable sizes (`caption` / `caption_note` in `meta.size`), so the figure and its explanation never collide. `source` remains a small footnote at the very bottom. If the image path is missing, a placeholder marker is drawn (and a `warning:` printed) so the deck still builds.

Prefer a `caption` that names the figure and a `note` that states the takeaway — a figure without an explanation makes the audience guess.

### blank
```yaml
- type: blank
  title: "optional title only"
```

## Conventions the spec assumes

- **Action titles.** The `title` should be the takeaway, not a topic. "Q3 ARR grew 22%", not "Q3 Results".
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
