---
name: pptx-build
description: >-
  Generate clean, white-based .pptx decks that don't look AI-made, and rebuild decks that
  already exist — built on python-pptx. Three modes, one spec: (1) default — grid-anchored
  layout, no drifting bands, composed archetypes (cards / steps / matrix / split / statement)
  picked from the content's shape; (2) template-fill — write into a corporate .pptx/.potx's own
  layouts and placeholders; (3) refactor — `extract_deck.py` reads an EXISTING deck back into a
  spec. Figures are native and editable (`figure`, `split figure:`, panels figures: diagram /
  flow / staircase / stacked_bar / chips / tiles / timeline) — never a pasted PNG. Five one-pager
  shapes (brief, dashboard, timeline, decision, event report). A `lead:` line makes title,
  supporting sentence and evidence three visible levels; the validator flags buried claims,
  filler slides and deck-level AI tells, and exports the text for ai-tell-reducer. Use for
  "simple white deck", "テンプレに沿ったパワポ", "この資料を作り直して", "1 枚にまとめて",
  "図の文字が編集できない", "AIっぽい資料を直して".
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Clean PowerPoint Generator (python-pptx)

Produces an actual `.pptx` file. Three paths share one spec:

- **Default mode** — a deck that reads as human-designed: white background, quiet typography, one restrained accent, everything snapped to a shared grid. Content is written into the **standard PowerPoint layouts' real placeholders** (title / body / subtitle / picture), never free textboxes floated onto a blank slide — so the deck is master-governed even without a supplied template. The opposite of a default-template AI deck.
- **Template-fill mode** — open a **real** `.pptx`/`.potx` the user provides and write content into **its slide layouts and placeholders**, so the deck inherits the template's master, theme, fonts, and logos. This is what "use our company template" actually means.
- **Refactor mode** — the deck already exists. `extract_deck.py` reads it back into a spec (titles, bullets, tables, charts, images, speaker notes), reports everything it could not represent, and hands you a text file where the argument is cheap to fix. Rebuild through either mode above. See `references/refactor-mode.md`.

**Engine: python-pptx.** Chosen specifically because it can *open* an existing binary template and address its placeholders — the thing PptxGenJS could not do. **Scope = file generation.** For pure design critique, storyboard, or chart-selection advice without producing a file, use the **design-for-agents** skill (this skill's principles are drawn from it). Use **marp-slides** when the user wants Markdown-authored slides.

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
| A diagram is needed | A **native figure**: `type: figure` (full width), `split` with `figure:` (beside its reading), or a figure block in `panels`. Kinds: `diagram` (boxes on a grid + arrows), `flow`, `staircase`, `stacked_bar`, `chips`. Never a rendered PNG/SVG |
| A photograph, a screenshot, someone else's figure | `type: image` with `image_kind: photo \| screenshot \| external` — the only things that belong in a picture |
| Something genuinely unsupported | Extend `build_deck.py` and `references/spec-format.md` — the generator is the artifact, not the deck |

`validate_deck.py` errors on an unknown `type:`, and `audit_pptx.py` (below) fails any deck
whose text ended up in free textboxes. If either fires, fix the generator or the spec.

## Rule one: a drawn diagram is never a picture

A diagram rendered to PNG or SVG and pasted onto a slide is the second failure this skill
exists to prevent. The audience cannot fix a typo in it, the template's fonts do not reach it,
it blurs when projected, and the next revision means redrawing it from scratch. **Every word on
a slide is editable slide text**, including the words inside boxes and on arrows.

So a figure is built from the native vocabulary, and the shape of the content picks the kind:

| The figure shows | Kind | Where it goes |
|---|---|---|
| Things related by arrows, in any arrangement (actors, systems, a one-page overview) | `diagram` — nodes on a `cols` × `rows` grid, edges between ids, optional `groups` | `type: figure`, `split figure:`, or `panels` |
| One left-to-right sequence, optionally with a feedback loop | `flow` | same |
| Ordered levels, maturity, escalation | `staircase` | same |
| Shares of one whole | `stacked_bar` (or `type: chart`) | same |
| A set of equal tags | `chips` | same |
| A real 3–5 stage process with its own text per stage | `type: steps` | its own slide |
| 2×2 with named axes | `type: matrix` | its own slide |

`validate_deck.py` refuses `image_kind: drawing`, and warns on any `image:` that is not a
photograph (`.jpg` / `.heic`) unless the spec declares `image_kind: photo | screenshot |
external`. `document-figures` is for pulling figures *out of* existing documents and for
targets that are not PowerPoint; it is not how a deck gets a diagram. If the content needs a
shape the vocabulary lacks, extend `_diagram` in `build_deck.py` — the generator is the
artifact.

## Rule two: the reader must find the claim in one glance

The flattest failure a generated deck has is a long assertion title at 24 pt over a list of
equal bullets at 18 pt: everything is a sentence, nothing is the point. Three levels, each a
visible step apart, and the claim always at the top:

| Level | What it is | Size (default) | Written as |
|---|---|---|---|
| **Title** | the claim, short enough to read as one unit | 28–34 pt | a short assertion, about 20 characters in Japanese; not the whole argument |
| **`lead:`** | the one sentence that supports the title | 20 pt bold | the sentence you would otherwise have crammed into the title |
| **Body** | the evidence | 18 / 16 pt | bullets, a table, a figure, a composed part |

`lead:` works on every content type: a bullets slide writes it as the first paragraph; a table,
chart, figure, two-column or composed slide gets it as a band across the top of the body region
(the content below is re-placed under it). The title floor is **28 pt** (was 24): a title that
needs a third line at 28 pt is two claims, and `validate_deck.py` says so. It also warns when a
title runs past ~26 characters (the claim is buried in a sentence), and when a short list under a
title fills under a third of the body (filler: add the `lead:`, merge, or give the content its
shape). One-pager text has its own floors — 12 pt for notes, 14 pt for anything read at a glance —
because a one-pager is read on paper, not projected.

## The three guarantees this skill is built around

1. **White-based and quiet (default mode).** `#FFFFFF`/`#FAFAFA` paper, near-black ink (`#1A1A1A`, never pure black), a single accent used only for a hairline and emphasis. No gradients, shadows, WordArt, or clipart.
2. **No drifting bands (default mode).** The classic ugly AI/Office tell is a full-width colored rectangle behind each title that ends up a few pixels off from slide to slide. This skill **never draws per-slide bands.** The accent is a short rule whose coordinates are computed once from the shared grid, so it is identical on every page that carries it and cannot drift — and by default only the pages that mark a turn (`title` / `section` / `statement`) carry it; content titles stand on weight and whitespace alone (`meta.rule: "all"` puts it back under them). See `references/anti-band-design.md`.
3. **Honors a real template (template-fill mode).** Pass `--template corp.pptx`. python-pptx opens it, and each spec slide is mapped to one of the template's **layouts** and written into its **placeholders** (title, body, subtitle, picture). The template's own master/theme/fonts/logos come through untouched. See `references/template-mode.md`. A template that names placeholders for the source line, the section label and the section number, and ships a figure-and-text layout, gets those filled too — then nothing but the composed parts is drawn per slide.

## Three more things the default mode guarantees

These target the failure modes that make generated decks look careless. All are automatic — you don't configure them.

4. **Master-governed placeholders that never overlap.** Default mode builds every slide on a **standard PowerPoint layout** (Title Slide / Section Header / Title and Content / Two Content / Picture with Caption / Blank, plus "Content with Caption" renamed **Statement** for the one-sentence page) and writes titles **and body content** into that layout's real **placeholders** — never free textboxes on a blank page. Each placeholder's geometry is set once on the layout (the "use the slide master" property — edit a layout later in PowerPoint and every slide built on it moves together). Title boxes are **bottom-anchored**, so a long two-line title grows *upward* into the top margin and can never collide with the body. The title size **auto-fits** to the largest value that stays within two lines; body placeholders have autofit turned **off** so the template's shrink-to-fit can never override the readable-size floors (#5).
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
in what order: **design-for-agents**'s `playbooks/pptx-mode-refactor.md`.

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

## One-pagers: five shapes, all native

A one-pager carries the whole argument on one slide, and its shape follows from what the reader
must do with it. Pick from these; never paste a drawn picture (Rule one). Each has a sample in
`assets/samples/onepager-*.yaml` and the reading rules are in `references/one-pagers.md`.

| The reader should… | Shape | Type | Sample |
|---|---|---|---|
| understand what happened and what follows | **brief** — context → findings → implications → next, left to right with arrows, takeaway band | `panels` with `columns:` (2–4) and `arrows: true` | `onepager-brief.yaml` |
| see status at a glance and approve one thing | **dashboard** — a row of number tiles, then status / next columns, takeaway = the ask | `dashboard` (`tiles:` + `columns:`) | `onepager-dashboard.yaml` |
| see when things happen and where we stand | **timeline** — milestones on one line, today marked | `figure` with `kind: timeline` (+ `lead:`) | `onepager-timeline.yaml` |
| choose | **decision memo** — the question, options × criteria, the recommendation with its reason | `decision` | `onepager-decision.yaml` |
| get the debrief of an event | **event report** — facts row (attendance, speakers), highlights / our angle / next steps, takeaway | `panels` with `tiles:` + 3 `columns:` | `onepager-event.yaml` |

## AI tells: the deck-level habits, and the de-AI pass

A deck reads as generated for reasons a single slide never shows: every bullet is `ラベル: 説明`,
every slide has three items, every title is a sentence of the same length, arrows do the work of
verbs. `validate_deck.py` reports these at deck level (label-colon bullets, same item count on four
consecutive slides, rule-of-three reflex, arrows and em-dashes in text, buried claims, filler
slides) — the full list with fixes is `references/deck-ai-tells.md`. For the words themselves:

```bash
python3 validate_deck.py deck.yaml --text /tmp/deck-text.md   # every sentence, as Markdown
```

then run **ai-tell-reducer** on that file and carry its edits back into the spec before building.
The deck text is short; the pass takes a minute and removes the tells a layout cannot.

## Slide types

Text containers: `title`, `section`, `bullets`, `two_col`, `big_number`, `quote`,
`image`, `table`, `chart`, `blank`.

`figure` is a native, editable figure on its own — `diagram` / `flow` / `staircase` /
`stacked_bar` / `chips` / `tiles` / `timeline` at full content width, with `caption` and
`note` in the body placeholder — the counterpart of `image` for anything that was drawn rather
than photographed. `split` takes the same `figure:` in place of `image:`. `dashboard` (tiles
row + columns) and `decision` (options × criteria + recommendation) are the one-pager types;
`panels` takes `columns:` (2–4), `arrows:` and `tiles:`.

`panels` is the dense one-page overview: two to four columns of text blocks and
native, editable figures (bar / staircase / flow / chips / diagram / timeline) with an
optional tiles row above and a takeaway band underneath. Every sentence stays slide text, never baked into a picture. See
`references/spec-format.md`.

**The four large-type pages are four compositions, not one layout with four
names.** `title` = rule / title / subtitle; `section` = large muted number / rule /
title (the number is the figure); `statement` = sentence / rule / gloss on its own
"Statement" layout; `quote` = an indented block beside a vertical bar, no rule.
Content pages carry a running section label (`number  title`, from the first
`section` on) above the title, so the reader always knows where in the argument
they are. The title slide has a presenter block (`presenter` / `affiliation` /
`date`), and `meta.footer` puts a running footer beside the page number — both
are real placeholders (page numbers are `slidenum` fields), never textboxes.
Table and rationale: `references/spec-format.md`.

**Composed archetypes** — `cards`, `steps`, `lead`, `matrix`, `split`, `statement` — are
drawn from the body placeholder's region rather than filled with text. Each one
exists for one shape of content, and picking the type IS the design decision:

| The content is | Type | The condition that earns it |
|---|---|---|
| 2-4 equivalent units | `cards` | They are the same kind of thing (not a ranking, not a list) |
| One unit that outweighs the rest | `lead` | The lead takes 46% of the width — area is the argument |
| A real sequence, 3-5 stages | `steps` | Order or dependency actually exists — the only type that draws arrows |
| Two meaningful axes | `matrix` | Both axes are named and all four quadrants say something |
| A figure and its reading | `split` | 38/62 asymmetry: the figure is the message, the text is the reading; `figure:` native, `image:` only for a photograph |
| A turn in the argument | `statement` | One sentence alone under the rule — the deck's punctuation |

Contrast is deck-level as well as slide-level: `section` and `statement` accept
`invert: true` (a deep, accent-toned page with light text) for the turns, and a
`chart` accepts `series_style: tonal` when its series are the same kind of thing.
All neutrals — part fills, borders, the dark page — are derived in HSL from the
accent, so a deck is one hue at several lightnesses rather than a color plus greys.

The vocabulary is **closed on purpose**. Parts are available because the content
has that structure, never as ornament — the information test applies to a card
exactly as it applies to a box someone drew by hand. `validate_deck.py` enforces
the counts, and every part is named `part/<kind>` in the file so `audit_pptx.py`
can tell a composed graphic from a floated textbox.

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
| a taste in mind but no brand | default mode + `--theme themes/<preset>.json` | one of the shipped presets below |
| a brand palette/fonts but no file | default mode + `--theme` | a JSON theme you transcribe |
| an actual `.pptx`/`.potx` template | `--template` | the template's own master/layouts/placeholders |

### Shipped presets

Same spec, same archetypes, different taste. Every preset sets only tokens —
colors, fonts, grid, and the three shape values — so the composition rules do not
change with the look.

| Preset | Taste | What it changes |
|---|---|---|
| `minimal-white` | Quiet, neutral, the default | White paper, blue accent, 0.06in radius |
| `editorial` | Serif, printed-page | Mincho faces, square corners, wide margins, larger title |
| `warm` | Approachable, human | Cream paper, terracotta accent, rounder corners, heavier line |
| `slate-dark` | Screen-first, technical | Dark ground; every derived tone flips with it |

**A dark preset is a whole-deck decision, not a slide effect.** Set a dark `bg`
and the derivation flips: surfaces and borders become dark tints of the accent,
and `invert: true` produces a *light* page, since the turn has to contrast with
the ground it sits on. Do not mix light and dark decks; `invert` is the only
place a deck changes ground, and only on `section` / `statement`.

Design judgement — which taste suits which audience — belongs to
**design-for-agents**, not here. This skill owns the values, that one owns the
choice.

`meta.*` in the spec overrides individual theme values in default mode (see `spec-format.md`). In template-fill mode the look comes from the template, so `meta` color/font keys are ignored by design.

## Pre-delivery checklist

- [ ] **The deck came out of `build_deck.py`** — no slide was added or patched by hand-written python-pptx.
- [ ] **`validate_deck.py` run, 0 errors** — findings triaged; the printed spine read against `references/narrative-and-logic.md` (one governing thought, MECE sections, close delivers the open).
- [ ] **`audit_pptx.py` run, 0 errors** — every slide is built on a layout and writes into its placeholders; warnings triaged (pinned geometry, empty placeholders, mixed masters).
- [ ] Every title is an **action title** (states the takeaway), not a topic label.
- [ ] One message per slide; no wall of text (split if it won't fit).
- [ ] **No build `warning:` left unaddressed** — each one means a title or body overflows at readable sizes; split or shorten that slide rather than ignoring it.
- [ ] **Titles:** none collide with the body; titles share one baseline across slides (flip the PNGs). Each is a short claim; the supporting sentence is in `lead:`, not in the title; no slide is a short list floating under a long title.
- [ ] **Tells:** `validate_deck.py` reports no deck-level tells (label-colon bullets, same count four slides running, arrows for verbs); the `--text` export went through ai-tell-reducer.
- [ ] **Figures:** every `image` is a photograph, screenshot or external figure (declared `image_kind`); every drawn diagram is a native `figure` / `split figure:` / `panels` figure whose words can be selected in PowerPoint. Each has a `caption` that names it and a `note` that gives the takeaway; the caption is clearly readable, not a tiny footnote.
- [ ] **Default mode:** background white/near-white; ink `#1A1A1A`, not pure black; exactly **one** accent (rule + emphasis only); **no full-width band**; the rule appears only on turn pages unless `meta.rule: "all"`, and lines up across them (flip the PNGs — the accent should never jump); the four large-type pages (`title` / `section` / `statement` / `quote`) do not look like one another.
- [ ] **Template mode:** every intended placeholder is actually filled (read the build log + a PNG); no slide fell back to the wrong layout; the deck still looks like the template, not like us.
- [ ] Data slides carry a `source:` footnote.
- [ ] **Archetypes:** each composed slide passes its condition — cards are equivalent, steps have real order, both matrix axes are named, `split` has a figure worth 62% of the slide.
- [ ] **Rhythm:** no more than about three consecutive slides share the same skeleton; turns are marked (`section` / `statement`), not just implied — `audit_pptx.py` reports runs of identical skeletons.
- [ ] **Contrast:** at least one dark page (`invert`) at a turn; titles ≤ ~22 full-width characters so they keep the large size; no saturated fill covering more than ~10% of a slide (`audit_pptx.py` measures it).
- [ ] **Refactor:** every `LOSS` line from `extract_deck.py` was decided on (redrawn, split, or accepted) — not skimmed.
- [ ] **Refactor:** no claim was changed while cleaning up; contradictions and unsupported numbers were reported back, not quietly fixed.
- [ ] **Refactor:** speaker notes survived (`notes:`), and extracted figures still resolve from the spec's directory.
- [ ] Sub-bullets use a real hanging indent (no glyph flush against text, no tofu boxes).

## Anti-patterns to refuse (carried from design-for-agents)

Apply the **information test** before adding any shape: if deleting it changes no meaning, it's decoration — remove it. Reject decorated bullets (boxes around list items), SmartArt-as-theater, arrows that don't represent real flow, filler hexagons/clouds, and verbatim stock themes. These are the patterns that make a deck read as AI-generated. Full catalog: design-for-agents's `antipatterns/pptx.md`.

## References

- `references/spec-format.md` — every spec field and slide type, including the composed archetypes and `meta.shape`
- `references/one-pagers.md` — the five one-pager shapes: which to pick, reading order, density and size floors
- `references/deck-ai-tells.md` — the habits that mark a deck as generated, how the validator catches them, and the de-AI pass
- `references/refactor-mode.md` — rebuilding a deck that already exists: extract → fix the argument as text → rebuild → audit, what extraction recovers and what it cannot carry
- `references/narrative-and-logic.md` — the cross-slide argument check (Pyramid Principle, SCQA, MECE, action titles, summary consistency) that `validate_deck.py` sets up but can't decide for you
- `references/template-mode.md` — filling a real `.pptx`/`.potx`: inspect → map → fill, and how foreign layouts/placeholders are resolved
- `references/anti-band-design.md` — why bands drift and the computed-grid alternative this generator uses
- `assets/samples/` — argument-shaped example decks (recommendation / review / decision) + `README.md` mapping each to its structure
- `assets/validate_deck.py` — spec linter (structure, logic, table/chart sanity) and narrative-spine printer; run before rendering
- `assets/audit_pptx.py` — artifact auditor: fails a deck whose content is not in layout placeholders; run after rendering
- `assets/extract_deck.py` — reads an existing `.pptx` back into a spec (+ its images) and reports what it could not represent; the entry point for refactoring
- `tests/run_tests.sh` — three-directional check of the extractor and the round-trip comparator (clean → 0, defect-injected → 1, not a deck → 2)
