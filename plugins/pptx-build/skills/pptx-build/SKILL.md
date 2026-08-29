---
name: pptx-build
description: >-
  Generate clean, white-based .pptx decks that don't look AI-made, and rebuild decks that
  already exist — built on python-pptx. Three modes, one spec: (1) default — grid-anchored
  layout with no drifting decorative bands; (2) template-fill — open a real corporate
  .pptx/.potx and write into ITS layouts and placeholders, inheriting its master, theme,
  fonts, and logos; (3) refactor — `extract_deck.py` reads an EXISTING deck (inherited,
  AI-made, hand-floated) back into a spec and reports what it cannot carry, so the argument
  is fixed as text and re-rendered into real placeholders. Use when an actual PowerPoint file
  must be produced or fixed, not just designed — "simple white deck", "テンプレに沿ったパワポ",
  "会社のテンプレートで作って", "この資料を作り直して/整えて". Covers bullets/two-column/
  big-number/quote/image plus table and chart, so a deck never falls back to hand-written
  python-pptx. Ships `validate_deck.py` (spec lint + narrative spine) and `audit_pptx.py`
  (fails a deck whose content is not in layout placeholders).
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Clean PowerPoint Generator (python-pptx)

Produces an actual `.pptx` file. Three paths share one spec:

- **Default mode** — a deck that reads as human-designed: white background, quiet typography, one restrained accent, everything snapped to a shared grid. Content is written into the **standard PowerPoint layouts' real placeholders** (title / body / subtitle / picture), never free textboxes floated onto a blank slide — so the deck is master-governed even without a supplied template. The opposite of a default-template AI deck.
- **Template-fill mode** — open a **real** `.pptx`/`.potx` the user provides and write content into **its slide layouts and placeholders**, so the deck inherits the template's master, theme, fonts, and logos. This is what "use our company template" actually means.
- **Refactor mode** — the deck already exists. `extract_deck.py` reads it back into a spec (titles, bullets, tables, charts, images, speaker notes), reports everything it could not represent, and hands you a text file where the argument is cheap to fix. Rebuild through either mode above. See `references/refactor-mode.md`.

**Engine: python-pptx.** Chosen specifically because it can *open* an existing binary template and address its placeholders — the thing PptxGenJS could not do. **Scope = file generation.** For pure design critique, storyboard, or chart-selection advice without producing a file, use the **pptx-design** skill (this skill's principles are drawn from it). Use **marp-slides** when the user wants Markdown-authored slides.

## Rule zero: never hand-write python-pptx for a deck

Generate every deck through `build_deck.py` with a spec. Do not write an ad-hoc script, do
not "just add one slide" with `python-pptx` afterwards, and do not "just fix" an existing
deck by patching its shapes with `python-pptx` — extract it and rebuild (`extract_deck.py`). Hand-written generation reaches
for `slide_layouts[6]` ("Blank") + `add_textbox()`, and the result is the failure this skill
exists to prevent: **nothing lands in a placeholder, so the slide master governs nothing** —
titles drift, the template's fonts and logos are ignored, and a rebrand means editing every
slide by hand.

When the spec seems not to cover what you need:

| Situation | Do this — not a hand-rolled script |
|---|---|
| A table is needed | `type: table` (rows/columns land in the body placeholder's region) |
| A chart is needed | `type: chart` (column / bar / line / area / pie / doughnut) |
| A diagram is needed | Draw it with `document-figures`, place it as `type: image` |
| Something genuinely unsupported | Extend `build_deck.py` and `references/spec-format.md` — the generator is the artifact, not the deck |

`validate_deck.py` errors on an unknown `type:`, and `audit_pptx.py` (below) fails any deck
whose text ended up in free textboxes. If either fires, fix the generator or the spec.

## The three guarantees this skill is built around

1. **White-based and quiet (default mode).** `#FFFFFF`/`#FAFAFA` paper, near-black ink (`#1A1A1A`, never pure black), a single accent used only for a hairline and emphasis. No gradients, shadows, WordArt, or clipart.
2. **No drifting bands (default mode).** The classic ugly AI/Office tell is a full-width colored rectangle behind each title that ends up a few pixels off from slide to slide. This skill **never draws per-slide bands.** The accent is a short hairline whose coordinates are computed once from the shared grid, so it is identical on every slide of a family and cannot drift. See `references/anti-band-design.md`.
3. **Honors a real template (template-fill mode).** Pass `--template corp.pptx`. python-pptx opens it, and each spec slide is mapped to one of the template's **layouts** and written into its **placeholders** (title, body, subtitle, picture). The template's own master/theme/fonts/logos come through untouched. See `references/template-mode.md`.

## Three more things the default mode guarantees

These target the failure modes that make generated decks look careless. All are automatic — you don't configure them.

4. **Master-governed placeholders that never overlap.** Default mode builds every slide on a **standard PowerPoint layout** (Title Slide / Section Header / Title and Content / Two Content / Picture with Caption / Blank) and writes titles **and body content** into that layout's real **placeholders** — never free textboxes on a blank page. Each placeholder's geometry is set once on the layout (the "use the slide master" property — edit a layout later in PowerPoint and every slide built on it moves together). Title boxes are **bottom-anchored**, so a long two-line title grows *upward* into the top margin and can never collide with the hairline or the body. The title size **auto-fits** to the largest value that stays within two lines; body placeholders have autofit turned **off** so the template's shrink-to-fit can never override the readable-size floors (#5).
5. **Text stays readable — it is never shrunk to fit.** Every size flows through one type scale with floors (`title_min` 24pt, `body`/`body_sub` 18/16pt). When a title or body genuinely won't fit at those sizes, the build prints a `warning:` telling you to **split or shorten** that slide — it does not silently shrink text to an unreadable size. One message per slide; split rather than cram. Tune floors with `meta.size` (see `references/spec-format.md`).
6. **Figures get a real caption, not a footnote.** An `image` slide's `caption` is a **bold, readable label** and its `note` (alias `description`) is a wrapping explanation at a readable size; the image height is reduced automatically to reserve room for them, so figure and explanation never collide. Give every figure a `caption` that names it and a `note` that states the takeaway.

## How to use it

Everything lives in `assets/`. Run the commands from there.

### 0. Install deps (once)

```bash
cd assets && pip install -r requirements.txt   # python-pptx + PyYAML
```

### 0b. Refactoring an existing deck? Extract it first

```bash
python3 extract_deck.py old.pptx -o deck.yaml   # + deck_media/ for its images
```

This recovers titles, bullets (with levels), two-column headings, tables,
charts, figures, sources and speaker notes into a spec, and prints a report of
what it could **not** carry (SmartArt, grouped drawings, decoration, animations).
Exit `1` means there are `LOSS` lines to decide on; `2` means the file is not a
`.pptx`. Then continue from step 1b below — the spec is content, not a finished
deck: rewrite topic titles into action titles and split multi-message slides
before rebuilding. Full procedure: `references/refactor-mode.md`. What to fix and
in what order: **pptx-design**'s `references/refactor-playbook.md`.

Never patch an existing deck's shapes with hand-written python-pptx. If the deck
is already master-governed (`audit_pptx.py old.pptx` reports no errors) and only
a few slides need edits, patch it **in PowerPoint** instead of rebuilding.

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

### 3. Audit the produced file (mechanical, do not skip)

```bash
python3 audit_pptx.py out.pptx      # nonzero exit on ERROR
```

`validate_deck.py` lints the *spec*; this lints the *artifact*. It reports, per slide, the
layout used and whether content sits in placeholders, and it **errors** when a slide's text
is in free textboxes instead — the signature of a hand-rolled deck or a template-fill that
landed on the wrong layout. It also warns on placeholders that pin their own geometry
(they stop following the layout), empty placeholders, and mixed slide masters.

### 4. Preview and QA

```bash
./render_preview.sh out.pptx        # -> preview/slide-*.png via LibreOffice
```

Read the PNGs back and run the checklist below. LibreOffice may substitute fonts, but it faithfully shows alignment, placeholder fills, and the no-drift property.

## Slide types

`title`, `section`, `bullets`, `two_col`, `big_number`, `quote`, `image`, `table`, `chart`, `blank`.

`table` and `chart` exist so that a deck needing one never has to leave the generator. Both
are inserted at the **body placeholder's** region and adopt its placeholder marker — the same
thing PowerPoint does when you insert a table into a content placeholder — so they stay
master-governed instead of becoming free objects. In default mode the table is drawn plain
(no banded template style): header row bold with an accent hairline under it, body rows
separated by a light hairline, transparent cells. Charts get one accent-led series palette,
no chart-area border, no chart title (the slide title carries the message), and a legend only
when there is more than one series. In template-fill mode both inherit the template's own
table style and theme colors.

In default mode each type maps to a standard PowerPoint layout and writes that layout's placeholders — titles share one bottom-anchored baseline, body/columns go in the layout's body placeholder(s), and `image` fits the figure into a real PICTURE-placeholder region with its `caption` + `note` in the caption placeholder. In template-fill mode each maps to the *supplied* template's layout and placeholders instead. Detail in `references/spec-format.md`.

Any slide may also carry `notes:` — the speaker notes, written into the real
notes slide in both modes. They survive an extract → rebuild round trip, because
what the presenter says is half the argument.

## Themes vs. templates — pick the right one

| The user has… | Use | What carries the look |
|---|---|---|
| no template, wants a clean deck | default mode | `themes/minimal-white.json` |
| a brand palette/fonts but no file | default mode + `--theme` | a JSON theme you transcribe |
| an actual `.pptx`/`.potx` template | `--template` | the template's own master/layouts/placeholders |

`meta.*` in the spec overrides individual theme values in default mode (see `spec-format.md`). In template-fill mode the look comes from the template, so `meta` color/font keys are ignored by design.

## Pre-delivery checklist

- [ ] **The deck came out of `build_deck.py`** — no slide was added or patched by hand-written python-pptx.
- [ ] **`validate_deck.py` run, 0 errors** — findings triaged; the printed spine read against `references/narrative-and-logic.md` (one governing thought, MECE sections, close delivers the open).
- [ ] **`audit_pptx.py` run, 0 errors** — every slide is built on a layout and writes into its placeholders; warnings triaged (pinned geometry, empty placeholders, mixed masters).
- [ ] Every title is an **action title** (states the takeaway), not a topic label.
- [ ] One message per slide; no wall of text (split if it won't fit).
- [ ] **No build `warning:` left unaddressed** — each one means a title or body overflows at readable sizes; split or shorten that slide rather than ignoring it.
- [ ] **Titles:** none collide with the hairline or body (a two-line title should sit above the hairline with clear space); titles share one baseline across slides (flip the PNGs).
- [ ] **Figures:** every `image` has a `caption` that names it and a `note` that gives the takeaway; the caption is clearly readable, not a tiny footnote.
- [ ] **Default mode:** background white/near-white; ink `#1A1A1A`, not pure black; exactly **one** accent (hairline + emphasis only); **no full-width band**; hairline lines up across all slides (flip the PNGs — the accent should never jump).
- [ ] **Template mode:** every intended placeholder is actually filled (read the build log + a PNG); no slide fell back to the wrong layout; the deck still looks like the template, not like us.
- [ ] Data slides carry a `source:` footnote.
- [ ] **Refactor:** every `LOSS` line from `extract_deck.py` was decided on (redrawn, split, or accepted) — not skimmed.
- [ ] **Refactor:** no claim was changed while cleaning up; contradictions and unsupported numbers were reported back, not quietly fixed.
- [ ] **Refactor:** speaker notes survived (`notes:`), and extracted figures still resolve from the spec's directory.
- [ ] Sub-bullets use a real hanging indent (no glyph flush against text, no tofu boxes).

## Anti-patterns to refuse (carried from pptx-design)

Apply the **information test** before adding any shape: if deleting it changes no meaning, it's decoration — remove it. Reject decorated bullets (boxes around list items), SmartArt-as-theater, arrows that don't represent real flow, filler hexagons/clouds, and verbatim stock themes. These are the patterns that make a deck read as AI-generated. Full catalog: pptx-design's `references/diagrams-and-architecture.md`.

## References

- `references/refactor-mode.md` — rebuilding a deck that already exists: extract → fix the argument as text → rebuild → audit, what extraction recovers and what it cannot carry
- `references/narrative-and-logic.md` — the cross-slide argument check (Pyramid Principle, SCQA, MECE, action titles, summary consistency) that `validate_deck.py` sets up but can't decide for you
- `references/template-mode.md` — filling a real `.pptx`/`.potx`: inspect → map → fill, and how foreign layouts/placeholders are resolved
- `references/anti-band-design.md` — why bands drift and the computed-grid alternative this generator uses
- `references/spec-format.md` — every spec field and slide type, with examples
- `assets/samples/` — argument-shaped example decks (recommendation / review / decision) + `README.md` mapping each to its structure
- `assets/validate_deck.py` — spec linter (structure, logic, table/chart sanity) and narrative-spine printer; run before rendering
- `assets/audit_pptx.py` — artifact auditor: fails a deck whose content is not in layout placeholders; run after rendering
- `assets/extract_deck.py` — reads an existing `.pptx` back into a spec (+ its images) and reports what it could not represent; the entry point for refactoring
- `tests/run_tests.sh` — three-directional check of the extractor and the round-trip comparator (clean → 0, defect-injected → 1, not a deck → 2)
