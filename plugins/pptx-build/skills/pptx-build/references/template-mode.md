# Template Mode — JS Theme Modules

How to make the generator match a provided/brand look.

## Why a theme module, not a .potx

PptxGenJS builds presentations from scratch; it **cannot open a binary `.pptx`/`.potx`** and inherit its master/theme. So "use our template" is implemented by **transcribing the template's look into a JS theme module** — palette, fonts, grid. This matches how the user's own decks already work (palette + font constants in code), and it keeps the output fully editable and drift-free.

> If a stakeholder genuinely needs the *binary* corporate `.potx` carried through (its master XML, embedded logos, etc.), that is outside PptxGenJS. In that case generate with this skill, then open the result inside the corporate template in PowerPoint, or use a separate OOXML step. The theme-module route below covers the large majority of "make it look like our brand" requests.

## Anatomy of a theme

A theme module exports a plain object (see `themes/minimal-white.js`):

```js
module.exports = {
  name: "minimal-white",
  layout: "LAYOUT_WIDE",          // or "LAYOUT_4x3"
  color: { bg, ink, muted, accent },   // hex strings, no '#'
  font:  { heading, body, number },
  rule: true,                     // master-level accent hairline (NOT a band)
  pageNumbers: true,
  grid: { marginX, top, titleH }, // optional overrides (inches)
};
```

`build_deck.js` reads only these fields, so a theme is the *entire* surface area of "the look." Everything else — slide types, grid math, the no-drift hairline — is shared.

## Matching a brand: the workflow

1. **Copy** `themes/minimal-white.js` to `themes/<brand>.js`.
2. **Transcribe** the brand: set `color.bg` (keep it light for the white-based look), `color.ink`, `color.muted`, `color.accent` (the one signature color), and `font.heading`/`font.body` to the brand fonts. `themes/brand-example.js` is a worked example using an editorial navy palette.
3. **Decide on the hairline.** If the brand has its own strong title treatment, set `rule:false` so nothing competes. Otherwise keep the hairline in the brand accent.
4. **Generate**: `node build_deck.js deck.yaml -o out.pptx --theme themes/<brand>.js`.
5. **Preview**: `./render_preview.sh out.pptx` and confirm the palette/fonts read as the brand and the accent lines up across slides.

## Per-deck overrides without editing the theme

`meta.*` in the spec overrides individual theme values for one deck:

| meta key | overrides |
|---|---|
| `accent`, `bg`, `ink`, `muted` | `theme.color.*` |
| `font_heading`, `font_body`, `font_number` | `theme.font.*` |
| `rule` (bool) | master hairline on/off |
| `page_numbers` (bool) | footer page numbers |
| `aspect` (`"16:9"`/`"4:3"`) | `theme.layout` |

Use this for one-off tweaks (e.g. a single deck in 4:3, or a different accent for one client) without forking the theme module.

## Honoring vs. overriding

- **Do** set the brand accent and fonts.
- **Avoid** moving `bg` off-white unless the brand truly is dark — the whole point of this skill is the clean white-based look.
- **Don't** add extra colors. Emphasis comes from the single accent + weight + size, not a second hue.
