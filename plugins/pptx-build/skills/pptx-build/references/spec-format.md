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

These override the active theme JSON (`--theme`, default `themes/minimal-white.json`) for one deck in default mode. To change the look permanently, edit/copy the theme file. For an actual `.pptx`/`.potx` template, use `--template` instead — see `template-mode.md`.

Colors take a bare hex (`2F5DA8`) or `#2F5DA8`.

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
  image: "/path/to/figure.png"       # fit to content width, height-capped, centered
  caption: "Source / caption"        # optional
```
If the path is missing, a placeholder marker is drawn so the deck still builds.

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
