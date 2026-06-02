---
name: pptx-build
description: Generate clean, white-based .pptx decks that don't look AI-made — built on PptxGenJS (Node). Grid-anchored layout with no drifting decorative bands (accent lives on the Slide Master, so it can't shift slide to slide), and a swappable JS theme module to match a provided/brand template. Use when the user wants to actually produce a PowerPoint file (not just design advice), asks for a "simple white deck," "テンプレに沿ったパワポ," or a deck that doesn't look AI-generated.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Clean PowerPoint Generator (PptxGenJS)

Produces an actual `.pptx` file that reads as human-designed: white background, quiet typography, one restrained accent, everything snapped to a shared grid. The opposite of a default-template AI deck.

**Engine: PptxGenJS (Node).** Chosen to match the user's existing slide-generation workflow. **Scope = file generation.** For pure design critique, storyboard, or chart-selection advice without producing a file, use the **pptx-design** skill (this skill's principles are drawn from it). Use **marp-slides** when the user wants Markdown-authored slides.

## The three guarantees this skill is built around

1. **White-based and quiet.** `#FFFFFF`/`#FAFAFA` paper, near-black ink (`#1A1A1A`, never pure black), a single accent used only for a hairline and emphasis. No gradients, shadows, WordArt, or clipart.
2. **No drifting bands.** The classic ugly AI/Office tell is a full-width colored rectangle drawn behind each title that ends up a few pixels off from slide to slide. This skill **never draws per-slide bands.** The accent is a short hairline placed on the **Slide Master**, so it is pixel-identical on every slide and cannot drift. See `references/anti-band-design.md`.
3. **Honors a provided template.** PptxGenJS cannot open a binary `.pptx`/`.potx`, so a "template" here is a **JS theme module** (palette + fonts + grid). Copy `themes/minimal-white.js`, transcribe the brand's colors/fonts, pass it with `--theme`. See `references/template-mode.md`.

## How to use it

Everything lives in `assets/`. Run the commands from there.

### 0. Install deps (once)

```bash
cd assets && npm install      # pptxgenjs + js-yaml
```
(If `pptxgenjs` already resolves from a parent `node_modules`, you can skip this.)

### 1. Write a spec

Author a small YAML (or JSON) spec describing slides. Start from `assets/deck.example.yaml`. Full field reference: `references/spec-format.md`.

- Use **action titles** — state the conclusion ("解約率は3四半期連続で低下、ただし新規獲得が鈍化"), not a topic label ("解約率").
- One message per slide. If a slide carries two arguments, split it.
- Set `meta.accent` to the brand color; leave the rest of `meta` unless asked.

### 2. Generate

```bash
# Default white-minimal theme:
node build_deck.js deck.yaml -o out.pptx

# Brand/provided look — a JS theme module:
node build_deck.js deck.yaml -o out.pptx --theme themes/brand-example.js
```

### 3. Preview and QA

```bash
./render_preview.sh out.pptx        # -> preview/slide-*.png via LibreOffice
```

Read the PNGs back and run the checklist below. LibreOffice may substitute fonts, but it faithfully shows alignment and confirms the no-drifting-band property.

## Slide types

`title`, `section`, `bullets`, `two_col`, `big_number`, `quote`, `image`, `blank`. Each is grid-anchored; titles share one Y coordinate and the accent hairline (a master object) sits at the same place across the whole deck. Detail in `references/spec-format.md`.

## Themes (the "template" mechanism)

A theme module exports `{ color, font, grid, layout, rule, pageNumbers }`. `build_deck.js` turns `rule:true` into a **master-level** hairline — never a per-slide shape. To match a brand: copy `themes/minimal-white.js`, swap the palette and fonts, pass `--theme`. The grid, slide types, and no-drift guarantee stay identical; only the look changes. `meta.*` in the spec can override individual theme values without editing the module.

## Pre-delivery checklist

- [ ] Every title is an **action title** (states the takeaway), not a topic label.
- [ ] One message per slide; no wall of text (body ≥18 pt — split if it won't fit).
- [ ] Background is white/near-white; ink is `#1A1A1A`, not pure black.
- [ ] Exactly **one** accent color; used only for the hairline + emphasis.
- [ ] **No full-width band** behind any title. Hairlines line up across all slides (flip through the PNGs — the accent mark should never jump).
- [ ] Data slides carry a `source:` footnote.
- [ ] Sub-bullets use a real hanging indent (no glyph flush against text, no tofu boxes).

## Anti-patterns to refuse (carried from pptx-design)

Apply the **information test** before adding any shape: if deleting it changes no meaning, it's decoration — remove it. Reject decorated bullets (boxes around list items), SmartArt-as-theater, arrows that don't represent real flow, filler hexagons/clouds, and verbatim stock themes. These are the patterns that make a deck read as AI-generated. Full catalog: pptx-design's `references/diagrams-and-architecture.md`.

## References

- `references/anti-band-design.md` — why bands drift and the master/grid alternatives this generator uses
- `references/template-mode.md` — matching a provided/brand template via a JS theme module
- `references/spec-format.md` — every spec field and slide type, with examples
