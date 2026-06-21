---
name: pptx-build
description: Generate clean, white-based .pptx decks that don't look AI-made — built on python-pptx. Two modes from ONE spec: (1) default — grid-anchored from-scratch layout with no drifting decorative bands (accent computed once from the grid, identical on every slide); (2) template-fill — open a real corporate .pptx/.potx and write into ITS layouts and placeholders (title/body/subtitle), inheriting the template's master, theme, fonts, and logos. Use when the user wants to actually produce a PowerPoint file (not just design advice), asks for a "simple white deck," "テンプレに沿ったパワポ," "会社のテンプレートで作って," or a deck that doesn't look AI-generated. Also ships `validate_deck.py` (lints structure/logic and prints the title-only narrative spine for a cross-slide story check) and argument-shaped starter decks in `assets/samples/` (recommendation / progress-review / decision).
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Clean PowerPoint Generator (python-pptx)

Produces an actual `.pptx` file. Two rendering paths share one spec:

- **Default mode** — a deck that reads as human-designed: white background, quiet typography, one restrained accent, everything snapped to a shared grid. The opposite of a default-template AI deck.
- **Template-fill mode** — open a **real** `.pptx`/`.potx` the user provides and write content into **its slide layouts and placeholders**, so the deck inherits the template's master, theme, fonts, and logos. This is what "use our company template" actually means.

**Engine: python-pptx.** Chosen specifically because it can *open* an existing binary template and address its placeholders — the thing PptxGenJS could not do. **Scope = file generation.** For pure design critique, storyboard, or chart-selection advice without producing a file, use the **pptx-design** skill (this skill's principles are drawn from it). Use **marp-slides** when the user wants Markdown-authored slides.

## The three guarantees this skill is built around

1. **White-based and quiet (default mode).** `#FFFFFF`/`#FAFAFA` paper, near-black ink (`#1A1A1A`, never pure black), a single accent used only for a hairline and emphasis. No gradients, shadows, WordArt, or clipart.
2. **No drifting bands (default mode).** The classic ugly AI/Office tell is a full-width colored rectangle behind each title that ends up a few pixels off from slide to slide. This skill **never draws per-slide bands.** The accent is a short hairline whose coordinates are computed once from the shared grid, so it is identical on every slide of a family and cannot drift. See `references/anti-band-design.md`.
3. **Honors a real template (template-fill mode).** Pass `--template corp.pptx`. python-pptx opens it, and each spec slide is mapped to one of the template's **layouts** and written into its **placeholders** (title, body, subtitle, picture). The template's own master/theme/fonts/logos come through untouched. See `references/template-mode.md`.

## Three more things the default mode guarantees

These target the failure modes that make generated decks look careless. All are automatic — you don't configure them.

4. **Master-governed titles that never overlap.** Default-mode titles are written into a real slide-**layout title placeholder** whose geometry is set once (the "use the slide master" property — edit that layout later in PowerPoint and every title moves together). The box is **bottom-anchored**, so a long two-line title grows *upward* into the top margin and can never collide with the hairline or the body. The title size **auto-fits** to the largest value that stays within two lines.
5. **Text stays readable — it is never shrunk to fit.** Every size flows through one type scale with floors (`title_min` 24pt, `body`/`body_sub` 18/16pt). When a title or body genuinely won't fit at those sizes, the build prints a `warning:` telling you to **split or shorten** that slide — it does not silently shrink text to an unreadable size. One message per slide; split rather than cram. Tune floors with `meta.size` (see `references/spec-format.md`).
6. **Figures get a real caption, not a footnote.** An `image` slide's `caption` is a **bold, readable label** and its `note` (alias `description`) is a wrapping explanation at a readable size; the image height is reduced automatically to reserve room for them, so figure and explanation never collide. Give every figure a `caption` that names it and a `note` that states the takeaway.

## How to use it

Everything lives in `assets/`. Run the commands from there.

### 0. Install deps (once)

```bash
cd assets && pip install -r requirements.txt   # python-pptx + PyYAML
```

### 1. Write a spec

Author a small YAML (or JSON) spec describing slides. Start from `assets/deck.example.yaml`. Full field reference: `references/spec-format.md`.

- Use **action titles** — state the conclusion ("解約率は3四半期連続で低下、ただし新規獲得が鈍化"), not a topic label ("解約率").
- One message per slide. If a slide carries two arguments, split it.
- The **same spec** drives both modes — you don't rewrite it to switch.
- **Start from a sample if the argument shape is known.** `assets/samples/` has argument-shaped specs — `recommendation-scqa` ("we should do X"), `progress-review` ("on track except Y"), `analysis-decision` ("choose B") — each a clean SCQA + Pyramid-Principle skeleton you adapt rather than inventing structure from scratch. See `assets/samples/README.md`.

### 1b. Validate the structure and narrative (before you render)

```bash
python3 validate_deck.py deck.yaml          # lint + print the title-only "spine"
```

This does two things a renderer can't: it **lints** the spec (action titles present, one-message density, sources on data, section structure, duplicate titles, overflow — each a finding with a severity, nonzero exit on ERROR) and it prints the **narrative spine** — every title in order, grouped by section. Read that spine end-to-end against `references/narrative-and-logic.md`: one governing thought? MECE sections? does the close deliver the open? Fix the argument here, where edits are cheap, before generating the file.

### 2a. Generate — default white-minimal look

```bash
python3 build_deck.py deck.yaml -o out.pptx
python3 build_deck.py deck.yaml -o out.pptx --theme themes/brand-example.json   # transcribed brand palette
```

Set `meta.accent` to the brand color; leave the rest of `meta` unless asked.

### 2b. Generate — fill the user's real template

```bash
# 1. INSPECT the template first — this is the step that prevents "the title placeholder
#    isn't being filled": it prints each layout's index and each placeholder's idx/type.
python3 inspect_template.py corp.pptx

# 2. (Optional) write a starter role->placeholder map, edit any wrong guess, and pass it.
python3 inspect_template.py corp.pptx --map > map.json

# 3. Build into the template. Without --map, layouts/placeholders are auto-detected.
python3 build_deck.py deck.yaml -o out.pptx --template corp.pptx
python3 build_deck.py deck.yaml -o out.pptx --template corp.pptx --map map.json
```

The command prints which layout each slide landed on. If a slide picked the wrong layout, pin it in `map.json` (or per-slide via `layout:` in the spec) and rerun. See `references/template-mode.md`.

### 3. Preview and QA

```bash
./render_preview.sh out.pptx        # -> preview/slide-*.png via LibreOffice
```

Read the PNGs back and run the checklist below. LibreOffice may substitute fonts, but it faithfully shows alignment, placeholder fills, and the no-drift property.

## Slide types

`title`, `section`, `bullets`, `two_col`, `big_number`, `quote`, `image`, `blank`. In default mode titles share one bottom-anchored placeholder baseline and the body is grid-anchored; `image` carries an optional `caption` + `note` caption block. In template-fill mode each maps to a template layout and writes the template's placeholders. Detail in `references/spec-format.md`.

## Themes vs. templates — pick the right one

| The user has… | Use | What carries the look |
|---|---|---|
| no template, wants a clean deck | default mode | `themes/minimal-white.json` |
| a brand palette/fonts but no file | default mode + `--theme` | a JSON theme you transcribe |
| an actual `.pptx`/`.potx` template | `--template` | the template's own master/layouts/placeholders |

`meta.*` in the spec overrides individual theme values in default mode (see `spec-format.md`). In template-fill mode the look comes from the template, so `meta` color/font keys are ignored by design.

## Pre-delivery checklist

- [ ] **`validate_deck.py` run, 0 errors** — findings triaged; the printed spine read against `references/narrative-and-logic.md` (one governing thought, MECE sections, close delivers the open).
- [ ] Every title is an **action title** (states the takeaway), not a topic label.
- [ ] One message per slide; no wall of text (split if it won't fit).
- [ ] **No build `warning:` left unaddressed** — each one means a title or body overflows at readable sizes; split or shorten that slide rather than ignoring it.
- [ ] **Titles:** none collide with the hairline or body (a two-line title should sit above the hairline with clear space); titles share one baseline across slides (flip the PNGs).
- [ ] **Figures:** every `image` has a `caption` that names it and a `note` that gives the takeaway; the caption is clearly readable, not a tiny footnote.
- [ ] **Default mode:** background white/near-white; ink `#1A1A1A`, not pure black; exactly **one** accent (hairline + emphasis only); **no full-width band**; hairline lines up across all slides (flip the PNGs — the accent should never jump).
- [ ] **Template mode:** every intended placeholder is actually filled (read the build log + a PNG); no slide fell back to the wrong layout; the deck still looks like the template, not like us.
- [ ] Data slides carry a `source:` footnote.
- [ ] Sub-bullets use a real hanging indent (no glyph flush against text, no tofu boxes).

## Anti-patterns to refuse (carried from pptx-design)

Apply the **information test** before adding any shape: if deleting it changes no meaning, it's decoration — remove it. Reject decorated bullets (boxes around list items), SmartArt-as-theater, arrows that don't represent real flow, filler hexagons/clouds, and verbatim stock themes. These are the patterns that make a deck read as AI-generated. Full catalog: pptx-design's `references/diagrams-and-architecture.md`.

## References

- `references/narrative-and-logic.md` — the cross-slide argument check (Pyramid Principle, SCQA, MECE, action titles, summary consistency) that `validate_deck.py` sets up but can't decide for you
- `references/template-mode.md` — filling a real `.pptx`/`.potx`: inspect → map → fill, and how foreign layouts/placeholders are resolved
- `references/anti-band-design.md` — why bands drift and the computed-grid alternative this generator uses
- `references/spec-format.md` — every spec field and slide type, with examples
- `assets/samples/` — argument-shaped example decks (recommendation / review / decision) + `README.md` mapping each to its structure
- `assets/validate_deck.py` — structure/logic linter and narrative-spine printer (run before rendering)
