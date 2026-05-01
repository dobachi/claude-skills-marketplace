# Deck Genres, Accessibility, and Pre-Delivery QA

## Deck Genres

Different audiences and formats demand different design conventions. Choose the genre, then design within its rules.

### Investor pitch

- **Length**: 10–15 slides. Kawasaki's 10/20/30 rule — 10 slides, 20 minutes, 30pt minimum.
- **Tone**: story, founder voice, bold visuals.
- **Anchor structure** (Y Combinator / Sequoia template):
  1. Company purpose (one sentence)
  2. Problem
  3. Solution
  4. Why now (timing rationale)
  5. Market size
  6. Product
  7. Traction
  8. Business model
  9. Competition / alternatives
  10. Team
  11. Financials / projections
  12. The ask
- **Design**: image-led, big numbers, sparing text. Custom theme; no default template.

### Sales deck

- **Length**: 10–20 slides.
- **Tone**: customer-problem first.
- **Anchor structure** (Andy Raskin's "Strategic Narrative"):
  1. Name a big, undeniable change in the world
  2. Show winners and losers of that change
  3. Tease the promised land (the future state)
  4. Introduce the product as the path to the promised land
  5. Present evidence (proof points, social proof, ROI)
- **Design**: heavy on social proof (logos, testimonials), ROI calculations, customer outcomes. Avoid product feature dumps until late.

### Internal / business review

- **Length**: 20–60 slides. Information-dense.
- **Tone**: analytical; action titles.
- **Anchor conventions** (McKinsey/BCG):
  - **Action titles** ("so-what" titles) on every slide
  - **Ghost decks** — title-only walkthrough before adding content; verifies the storyline
  - **Source footnotes** on every chart and data claim
  - **Page numbers** + section headers
  - **Horizontal table of contents** at section breaks
  - **Pyramid Principle structure** — answer first, then supporting arguments (Barbara Minto)
- **Design**: dense but disciplined. Single-message-per-slide still applies — multiple charts on one slide are fine if they answer the same question.

### Conference talk

- **Length**: 20–40 slides for a 30-minute talk.
- **Tone**: image-led, low text, evocative.
- **Reference**: Garr Reynolds, *Presentation Zen*.
- **Design**: full-bleed images, large type, ≤6 words per slide, talk track carries content. Rehearse on actual delivery hardware.

### Training / educational

- **Length**: variable.
- **Tone**: higher text density acceptable since slides may be used as standalone reference.
- **Conventions**:
  - Build in deliberate **review/recap slides**.
  - **Consistent iconography** for "exercise," "key concept," "warning."
  - Numbered learning objectives at the start; check at the end.
- **Design**: clear hierarchy, visible progress (e.g., "Module 2 of 5"), exercises clearly marked.

### Status update / async share

- **Length**: short — 5–10 slides.
- **Tone**: information-first; speaker notes carry the talk track.
- **Design**: action titles required (because no speaker is present). Highlight what changed since last update. Source citations on data.

## Accessibility

**Run before every delivery.** PowerPoint's built-in **Accessibility Checker** (Review → Check Accessibility) catches most issues.

### Required practices

| Practice | How |
|---|---|
| **Alt text on every non-decorative image, chart, SmartArt** | Right-click → View Alt Text. Mark decorative images as such. Charts: alt text describes the *takeaway*, not "bar chart." |
| **Reading order** | Selection Pane (Home → Arrange → Selection Pane). Default Z-order from insertion order is rarely correct — verify each slide. |
| **Unique slide titles** | Screen reader users navigate by title. Outline view (View → Outline View) shows them at a glance. |
| **Color contrast** | WCAG 2.1 AA — 4.5:1 for normal text, 3:1 for large. Verify with WebAIM contrast checker. |
| **Color independence** | Never encode meaning in color alone. Add label, pattern, or shape. |
| **Captions / transcripts** for embedded video | Provide synchronized captions; transcript for asynchronous viewers. |
| **Live captions** for live presentation | Slide Show → Subtitle Settings (PowerPoint's built-in). |
| **Speaker notes** populated | Ensures async viewers (and screen reader users replaying the deck) get the context. |
| **Avoid information in headers/footers only** | Screen readers may skip them. |
| **Embed fonts** | Verify rendering on systems without your fonts. |

### Accessibility Checker remediation

When the checker flags issues:

- **Missing alt text** → add it; mark decorative if truly decorative.
- **Hard-to-read color contrast** → verify against WCAG; usually means your accent color on background fails 4.5:1.
- **Tables with no header row** → set the top row as a header (Table Tools → Design → Header Row).
- **Slides with the same title** → make titles unique. Append " (continued)" or numbers if necessary.
- **Reading order check** → verify with Selection Pane; assistive tech reads bottom of pane to top.

## Pre-Delivery QA Checklist

Run before sharing, presenting, or shipping.

### Narrative

- [ ] **Title-only walkthrough** — read every slide's title in sequence. Does the storyline make sense without reading the body?
- [ ] **Single message per slide** — any slide carrying two arguments? Split it.
- [ ] **Spelling, grammar** — run spell check; read titles aloud.
- [ ] **Action titles** present where the genre requires (internal review, status update).

### Data integrity

- [ ] **Numbers reconcile** — totals add up; figures match across slides; percentages are consistent.
- [ ] **Sources cited** on every chart and data claim — 8–10 pt gray footnote.
- [ ] **Date and version** on the title slide.

### Visual hygiene

- [ ] **Consistent fonts, sizes, colors, alignment** across slides — spot-check by clicking through quickly.
- [ ] **Theme colors used** (not hand-applied colors).
- [ ] **No default PowerPoint theme** unless deliberately chosen.
- [ ] **Images** — high resolution, not distorted, license cleared.
- [ ] **Icons** — single family, consistent style, theme color.

### Diagrams

- [ ] **Information test passes** for every diagram (see `diagrams-and-architecture.md`).
- [ ] **Arrow conventions consistent** within each diagram; legend present.
- [ ] **No decorated bullets, SmartArt theater, filler shapes.**
- [ ] **Architecture diagrams** at consistent abstraction level (C4).

### Animation

- [ ] **Every animation justified** — reveal, emphasis, or spatial. Default: no animation.
- [ ] **Transitions** None or Fade only. Morph only when motion *is* the content.

### Accessibility

- [ ] **Accessibility Checker** clean.
- [ ] **Alt text** on every non-decorative image/chart/SmartArt.
- [ ] **Reading order** verified via Selection Pane.
- [ ] **Contrast** ≥AA.
- [ ] **Captions** on video.

### File hygiene

- [ ] **Embedded fonts** if sharing with non-team users.
- [ ] **Linked media** present (or embedded).
- [ ] **File size** ideally <50MB; compress images if larger (File → Compress Pictures).
- [ ] **No broken links**, no `[TBD]`, no `Lorem ipsum`, no leftover `[placeholder]`.
- [ ] **Page numbers** consistent (or deliberately absent on title/section slides).

### Backup

- [ ] **PDF export** as fallback for projector / font / version issues.
- [ ] **Speaker notes** populated for async sharing.
- [ ] **Rehearsal** on actual delivery hardware for live presentation.
- [ ] **Backup deck** on USB / cloud — never rely on a single copy at delivery time.

## Source References

- Nancy Duarte, *slide:ology*; *Resonate* — narrative arc, sparkline, audience analysis.
- Garr Reynolds, *Presentation Zen* — image-led design, restraint, *ma*.
- Edward Tufte, *The Visual Display of Quantitative Information* — data-ink ratio, chartjunk.
- Cole Nussbaumer Knaflic, *Storytelling with Data* — chart selection, gray-the-rest.
- Robin Williams, *The Non-Designer's Design Book* — CRAP principles.
- Barbara Minto, *The Pyramid Principle* — answer-first structure for analytical decks.
- Guy Kawasaki — 10/20/30 rule.
- Andy Raskin — Strategic Narrative for sales decks.
- WCAG 2.1 (W3C) — accessibility standards.
- Microsoft Accessibility documentation — PowerPoint-specific guidance.
- McKinsey/BCG visual conventions — action titles, ghost decks, source footnotes.
- Simon Brown — C4 model for architecture diagrams.
