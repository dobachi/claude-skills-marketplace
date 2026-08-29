---
name: pptx-design
description: >-
  Expert guidance for PowerPoint (.pptx) decks, for BOTH new decks and ones that already
  exist — a decided simple/clean design system (four color slots, one type scale, one grid,
  a density budget) plus typography, color, data visualization, structural diagrams, deck
  genres, accessibility, and slide-master setup. Covers refactoring an inherited, AI-generated,
  or hurried deck: diagnose, triage, patch vs. rebuild, preserving the author's argument.
  Use for "シンプルできれいな資料にしたい",
  "この資料をレビューして", "既存のパワポを直したい/作り直したい", "clean up this deck",
  "design a deck", "参考文献を教えて", "what should I read on slide design" — it carries a
  routed further-reading list. ADVICE ONLY: it plans and critiques but never produces a file.
  The moment an actual .pptx must be written or rebuilt ("パワポを作って", "スライドにして",
  "build the deck"), hand off to **pptx-build**, which extracts an existing deck into a spec
  and writes into real layout placeholders — never hand-write python-pptx, which floats
  textboxes onto blank slides and ignores the slide master.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# PowerPoint Design Expert

Helps users plan, design, critique, and finalize professional `.pptx` decks. Scope is design and information architecture — not programmatic file manipulation.

## Producing an actual file — hand off, never hand-roll

This skill does not generate `.pptx` files, and **you must not write ad-hoc python-pptx code
to make one.** Hand-written generation reaches for `slide_layouts[6]` ("Blank") plus
`add_textbox()`, which is exactly the deck this skill argues against: nothing is in a
placeholder, the slide master governs nothing, and re-branding means editing every slide.

| The user wants | Use |
|---|---|
| A real `.pptx` file (from scratch or into their corporate template) | **`pptx-build`** — one YAML spec, writes into layout placeholders; `--template corp.pptx` fills their master |
| An **existing** `.pptx` fixed, cleaned up, or rebuilt | **`pptx-build`**'s `extract_deck.py` — recovers the content into a spec you edit, then rebuild. Diagnose first with Mode D below |
| A table or chart on a slide | `pptx-build`'s `table` / `chart` slide types — not a hand-built shape |
| Markdown-authored slides | `marp-slides` |
| A diagram worth drawing | `document-figures`, then place the result as an `image` slide |
| Design advice, storyboard, critique, master/layout planning | this skill |

If `pptx-build`'s spec cannot express something, extend the spec or render it as an image —
do not drop out of the generator. After any deck is produced, `pptx-build`'s
`audit_pptx.py` verifies that every slide is built on a layout and writes into placeholders.

## Core Principles

1. **Audience first.** Define what the audience must know, feel, and do *before* opening PowerPoint. Map prior knowledge, incentives, and time budget. (Duarte; Reynolds)
2. **One message per slide.** If a slide carries two arguments, split it. Slides are free.
3. **Action titles ("so-what" titles).** Replace topic titles ("Q3 Revenue") with takeaway titles ("Q3 revenue grew 18%, driven by enterprise renewals"). The title states the conclusion; the body proves it. (McKinsey/BCG convention)
4. **Visual hierarchy via CRAP.** Contrast, Repetition, Alignment, Proximity. (Robin Williams)
5. **Restraint, as decided values.** High data-ink ratio (Tufte), minimum animation, no chartjunk, no decorative shapes. "Clean" here is not a mood — it is four color slots, one type scale, one grid, and a density budget: `references/clean-design-system.md`. Apply it unless the user has a template or a brand system that says otherwise.
6. **Clean is subtractive.** A slide is clean when nothing on it can be deleted without losing meaning — not when it holds little. Three words on a white slide is empty, not clean.
7. **Diagrams must encode structure, not decorate text.** Apply the **information test**: if removing the boxes/arrows changes no meaning, it isn't a diagram — it's bullets in costume. See `references/diagrams-and-architecture.md`.
8. **Accessibility by default.** WCAG AA contrast, alt text, unique slide titles, logical reading order — every deck.

## Two entry points

| The deck… | Start at |
|---|---|
| does not exist yet | the **Workflow** below (brief → storyboard → master → draft) |
| already exists (inherited, AI-made, hurried, or someone else's) | **Mode D — refactor**, and `references/refactor-playbook.md`. Diagnose before restyling: content first, form last |

## Workflow (new deck)

| Step | Action | Why |
|---|---|---|
| 1. Brief | Capture goal, audience, format (live/async/handout), duration, brand constraints | Design choices flow from these |
| 2. Storyboard on paper | Sketch the narrative arc and one-line title for each slide before opening PowerPoint | The software's defaults push bullet-list thinking |
| 3. Set up Slide Master | Theme fonts, theme colors, layouts (title, section, content, two-col, full-bleed image, data) | Fixes propagate; rebrand is one edit |
| 4. Draft | Build action titles first; then content. Per slide: apply the information test before adding any shape | Title-first guarantees narrative coherence |
| 5. Critique | Title-only walkthrough, single-message check, anti-pattern sweep | Catches structural issues cheaply |
| 6. QA | Accessibility Checker, contrast verification, source citations, page numbers, PDF backup | Pre-delivery hygiene |

## Quick Reference

### Font sizes (minimum)

| Element | Projector / live | Laptop / async | Print handout |
|---|---|---|---|
| Slide title | 36–44 pt | 28–36 pt | 24–32 pt |
| Body | 24 pt | 18 pt | 12–14 pt |
| Footnote / source | 12 pt | 10 pt | 9 pt |

If you need <18pt body to fit, the slide has too much content — split it.

### Color & contrast

- **60-30-10 rule** — 60% dominant neutral, 30% secondary, 10% accent for emphasis.
- **WCAG 2.1 AA** — 4.5:1 contrast for normal text; 3:1 for large text (≥18pt or 14pt bold). AAA: 7:1 / 4.5:1.
- **Color independence** — never encode meaning in color alone (8% of men have red-green color blindness). Add shape, label, or position.
- **Pure black on pure white** halates — prefer `#1A1A1A` on `#FAFAFA`.

### Chart selection cheat sheet

| Question | Recommended chart | Avoid |
|---|---|---|
| Compare across categories | Horizontal bar (long labels) / vertical bar | Pie with >3 slices |
| Change over time | Line | 3D anything |
| Part-to-whole | Stacked bar (or single number if 2 parts) | Exploded pie |
| Distribution | Histogram, box plot | — |
| Correlation | Scatter | — |
| One number | **Big number, no chart** | Single-bar chart |

Detailed guidance: `references/data-visualization.md`.

### Deck genre defaults

| Genre | Length | Tone | Anchor structure |
|---|---|---|---|
| Investor pitch | 10–15 slides | Story, founder voice | Kawasaki 10/20/30; YC/Sequoia template |
| Sales | 10–20 slides | Customer-problem first | Andy Raskin Strategic Narrative |
| Internal / business review | 20–60 slides | Information-dense | Action titles, ghost deck, source footnotes |
| Conference talk | 20–40 slides | Image-led, low text | Reynolds *Presentation Zen* |
| Training | Variable | Higher text density OK | Recap slides, consistent iconography |

Detail: `references/genres-and-qa.md`.

## Anti-Patterns

Reject these by default. If a draft contains any of them, name it and propose the fix.

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Wall of text | Audience reads faster than speaker; speaker becomes redundant | Send an email; or split + extract action title |
| Default templates (Ion/Facet/Wisp) | Instantly read as low-effort | Build a minimal custom Slide Master |
| 3D charts, exploded pies | Distort perception (Tufte chartjunk) | Flat 2D, gray non-emphasized series, accent the one that matters |
| Gratuitous animation / transitions | Cognitive cost without comprehension gain | None or Fade only; Morph only when motion *is* the content |
| Low-res or distorted images | Destroys credibility | ≥150 DPI; Shift-drag to constrain proportions |
| Logo soup | Repetition without information | Logo on title + closing only |
| Color-only encoding | Fails for color-blind viewers | Add label, pattern, or position |
| Unsourced data | Audience cannot verify | "Source:" footnote, 8–10 pt gray |
| **Decorated bullets** (boxes/shapes around list items) | Adds visual noise without structural meaning — common in AI-generated decks | Apply information test → either delete shapes (it's a list) or actually encode relationships |
| **SmartArt as theater** (default SmartArt to dress up bullets) | Implies a process/hierarchy that doesn't exist | Use SmartArt only for genuinely sequential or hierarchical content; otherwise plain text |
| **Arrows that don't represent flow** | Decorative connectors with no data-flow / dependency / temporal meaning | Remove, or pick one meaning (data flow / dependency / time) and apply consistently |
| **Hexagons / pentagons / clouds as filler** | Shape carries no semantic load | Use rectangles unless the shape encodes meaning |
| **Center-and-spokes** with mismatched spokes | Implies a relationship that isn't there | Restructure as a list, table, or proper diagram |

Detail: `references/diagrams-and-architecture.md`.

## The Information Test (use every time before adding shapes)

Before drawing boxes/arrows on a slide, answer out loud:

1. **What structural information does this visual encode?** Relationship, flow direction, hierarchy, containment, parallelism, temporal order, or grouping?
2. **If I deleted the shapes and arrows and left only the text, what would I lose?**

If the answer to (2) is "nothing meaningful," the visual is decoration. Choose one of:

- **Delete the shapes.** Present as a list or sentence.
- **Replace with a chart** if data is involved.
- **Actually encode the structure.** Redraw with meaningful arrows, hierarchy, grouping, or boundaries — see diagram type catalog in `references/diagrams-and-architecture.md`.

## Deliverable Modes

The user typically wants one of these — clarify if ambiguous.

### A. Storyboard / outline (before drafting)

```markdown
# Deck: <title>

**Audience**: …  **Duration**: …  **Format**: live | async | handout
**Single take-home**: <one sentence>

| # | Action title | Visual | Notes |
|---|---|---|---|
| 1 | <takeaway> | full-bleed image | opener |
| 2 | <takeaway> | 2x2 matrix | …  |
| … | … | … | … |
```

### B. Slide-by-slide design recommendations

Per slide: action title, layout (which Slide Master), visual element with the information test applied, color tokens (hex), font sizes, source citation, alt text, animation justification (or "none").

### C. Design review of an existing deck (read-only)

Critique organized by topic area, anti-pattern by anti-pattern, with concrete
fixes. Stop here when the user wants findings; go on to **D** when they want the
deck actually changed.

```markdown
## Slide 5 — "Q3 Performance"
- ❌ Topic title — change to action title (e.g., "Q3 ARR grew 22%, …")
- ❌ 3D pie chart with 6 slices — replace with horizontal bar; gray 5 series, accent the one in focus
- ❌ Decorated bullet (rounded rectangles around 4 list items, no structural meaning) — delete shapes; present as plain list with consistent indentation
- ⚠️ Body text 14pt — raise to 18pt; cut content if needed
- ✅ Source citation present
```

### D. Refactor an existing deck

Design review (C) says what is wrong. A refactor changes it — while preserving
the argument. Full procedure: `references/refactor-playbook.md`.

1. **Diagnose in five passes, in order**: titles only → one-message-per-slide →
   evidence and sources → structure vs. decoration (information test) → form.
   Write findings down between passes; a mixed pass becomes restyling.
2. **Triage.** Fix the argument before the form: governing thought → action
   titles → split/merge → evidence → decoration → chart choice → density →
   ornament → accessibility. Work on form in a deck that does not argue is wasted.
3. **Decide patch vs. rebuild.**

   | Situation | Do |
   |---|---|
   | A few slides; master and layouts are sound | Patch in PowerPoint |
   | Corporate template, only the content is bad | Patch, or refill the same template |
   | Content is free textboxes on blank slides | Rebuild — patching preserves the disease |
   | The argument is being restructured, or >⅓ of slides change | Rebuild |

4. **Rebuild through the generator, never by hand.** `pptx-build`:
   `extract_deck.py old.pptx -o deck.yaml` recovers the content (and reports what
   it could not carry), you fix the argument in the YAML, then
   `validate_deck.py` → `build_deck.py` → `audit_pptx.py`.
5. **Report three things**: what changed structurally and why, what could not be
   carried over, and what you deliberately left for the author to settle
   (contradictions, unsupported claims). Never change a claim silently.

**Scope boundary:** refactoring preserves what the deck argues. Rewriting the
argument, cutting a slide, or reconciling two contradictory numbers are the
author's calls — surface them, don't take them.

## Quality Criteria

| Dimension | Strong | Adequate | Weak |
|---|---|---|---|
| Narrative | Title-only walkthrough tells the full story | Storyline emerges with body content | Disconnected slides |
| Single message | Every slide passes the test | A few dense slides | Multi-argument slides throughout |
| Information density | Right for the format (live/async) | Slightly over or under | Wall of text or empty filler |
| Visual hierarchy | Eye lands at focal point in <1s | Hierarchy present but soft | Eye wanders |
| Diagrams | All pass the information test | One or two decorative | Decorated bullets / SmartArt theater |
| Cleanliness | Four color slots, one type scale, one grid, density budget met | Minor drift | Bands, extra colors, shrunken type |
| Accessibility | AA contrast, alt text, reading order verified | Mostly compliant | Issues unaddressed |

## Iteration Modes

| Mode | When to use |
|---|---|
| **Storyboard** | Before any slides exist — define narrative arc and titles |
| **Refactor** | A deck already exists — diagnose, triage, patch or rebuild (Mode D) |
| **Clean up** | The argument is fine, the form is loud — apply `clean-design-system.md` and delete what fails the information test |
| **Tighten** | Cut filler, raise data-ink ratio, sharpen action titles |
| **Visualize** | Replace text-heavy slides with charts or proper diagrams (apply information test) |
| **Accessibility pass** | Pre-delivery — Accessibility Checker, contrast, alt text |
| **Genre-fit** | Reshape for a different audience (e.g., internal review → investor pitch) |

## References (consult when relevant)

- `references/clean-design-system.md` — **the default look as decided values**: four color slots, one type scale, one grid, density budget, emphasis ladder, cleanliness check
- `references/refactor-playbook.md` — fixing a deck that already exists: five-pass diagnosis, triage order, patch-vs-rebuild, what a refactor may not change
- `references/visual-design.md` — typography, color, layout, hierarchy, imagery, icons
- `references/data-visualization.md` — chart selection, Tufte data-ink, tables, anti-patterns
- `references/diagrams-and-architecture.md` — information test, diagram types, architecture conventions, AI-deck anti-patterns
- `references/genres-and-qa.md` — deck genres, accessibility, pre-delivery checklist
- `references/further-reading.md` — **which outside source to consult, and when**: a routing table from the open question (chart choice, contrast rule, pitch sequence, grid, diagram semantics, the evidence for "don't read your slides") to one source, plus fetchable standards, books, Japanese-language sources, and sample decks

Sourcing discipline: cite a work only after actually consulting it. The URLs in
`further-reading.md` can be fetched and quoted; the books cannot — recommend those to the
author, and never attribute a specific number, rule, or quotation to one you have not read.
The principles this skill runs on stand on their own without a citation.
