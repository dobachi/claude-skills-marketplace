# Visual Design Reference

Typography, color, layout, hierarchy, imagery, and icons for `.pptx` decks.

## Typography

### Font choice

- **Sans-serif for projection and screen.** Calibri, Helvetica, Arial, Roboto, Inter, Source Sans render cleanly at low resolution and from a distance.
- **Serifs (Georgia, Merriweather)** are acceptable for print handouts or deliberate editorial tone, never for body text on a projected slide.
- **Avoid decorative or condensed faces** for body text. Reserve them for branded title treatments at most.
- **Embed fonts** when the file may be opened on machines without your fonts installed (File → Options → Save → Embed fonts in the file).

### Font pairing

- **No more than two typefaces.** One sans for headings + a complementary sans (or serif) for body. Often cleaner: a single family with weight variation (Light / Regular / Medium / Bold).
- **Pair safe combinations**: Inter + Source Serif, Roboto + Roboto Slab, Helvetica + Georgia. When in doubt, use one family.

### Sizing

| Element | Projector / live | Laptop / async | Print handout |
|---|---|---|---|
| Slide title | 36–44 pt | 28–36 pt | 24–32 pt |
| Subtitle / kicker | 24–28 pt | 18–22 pt | 14–16 pt |
| Body | 24 pt min | 18 pt min | 12–14 pt |
| Caption | 14–16 pt | 12–14 pt | 10–11 pt |
| Footnote / source | 12 pt | 10 pt | 9 pt |

If you need <18 pt body to fit, the slide has too much content. Split it. (Duarte, Reynolds)

### Hierarchy

Establish three to four levels (title, subtitle, body, caption) and use them consistently across the deck. Differentiate via **scale, weight, color** — not multiple typefaces.

### Spacing

- **Line height** 1.15–1.4× font size. Tight leading (1.0×) suffocates text; >1.5× looks sloppy.
- **Line length** ~50–75 characters per line. Wider lines lose the eye between rows.
- **Paragraph spacing** ≥0.5× line height — separate ideas visually.

## Color

### Palette construction

- **60-30-10 rule** (interior design heuristic widely adopted in slide design): 60% dominant neutral (often the background), 30% secondary, 10% accent for emphasis.
- **Tools**: Coolors, Adobe Color, Material Design palette generator, Open Color, Tailwind Colors. Brand guidelines override.
- **Limit to ~5 colors total**: 1 background, 1 primary text, 1 secondary text/muted, 1 accent, 1 semantic warning.

### Semantic color use

- Red = warning, decline, negative.
- Green = positive, growth, success.
- Yellow / orange = caution, in-progress.
- Neutral grays = non-emphasized data, supporting context.

Apply consistently across the deck. Reusing the same color for unrelated meanings confuses the audience.

### Contrast (WCAG 2.1)

| Requirement | Normal text | Large text (≥18pt or 14pt bold) |
|---|---|---|
| AA (minimum) | 4.5:1 | 3:1 |
| AAA (enhanced) | 7:1 | 4.5:1 |

- Verify with WebAIM Contrast Checker, or PowerPoint's Accessibility Checker (Review → Check Accessibility).
- Light gray text on white — a common "elegant" choice — usually fails AA.

### Color blindness

- ~8% of men have red-green color blindness. **Never encode meaning in color alone.**
- Add shape, position, label, pattern, or icon as a redundant cue.
- Test with a deuteranopia simulator (Color Oracle, Sim Daltonism).
- Avoid red/green-only differentiators on charts.

### Background choice

- **Light backgrounds** suit well-lit rooms and printed handouts.
- **Dark backgrounds** favor dim auditoriums and reduce eye fatigue on screens.
- Be **consistent within a deck**. Mixing freely looks chaotic.
- Pure black (`#000`) on pure white (`#FFF`) creates harsh halation; prefer `#1A1A1A` on `#FAFAFA`.

## Layout & Composition

### Grid

- Use a consistent underlying grid (12-column or rule-of-thirds 3×3) so elements snap to predictable positions across slides.
- PowerPoint: View → Guides + Grid; Smart Guides; align tools (Format → Align → Distribute).
- Inconsistent positioning across slides reads as amateurish even when individual slides look fine.

### Alignment

- Every element should align with another element on the slide (CRAP: **A**lignment).
- **Default to left-alignment** for text in Western reading; centered text reads as ceremonial.
- Numbers right-align (decimal align in tables).

### Proximity

- Group related items physically close; separate unrelated items with whitespace.
- Reduce visual gaps within a group; increase gaps between groups.

### White space

- Leave ~20–30% of the slide empty. Whitespace is a design element (Reynolds, drawing on Japanese *ma*), not waste.
- Crowded slides signal "I didn't have time to edit."

### Focal point

- The viewer's eye should know within one second where to look first.
- Place the visual anchor at one of the four intersections of a 3×3 grid (rule of thirds), not dead center.
- Achieved via size, contrast, position, or isolation.

### Single-message principle

- One message per slide. If a slide carries two arguments, split it.
- Pair with **action titles**: replace topic titles ("Q3 Revenue") with takeaway titles ("Q3 revenue grew 18%, driven by enterprise renewals").

## CRAP Principles (Robin Williams)

| Principle | Definition | How it shows up on slides |
|---|---|---|
| **C**ontrast | Different things should look meaningfully different | Title vs body weight; emphasis color; size jump |
| **R**epetition | Recurring visual motifs unify a deck | Same Slide Master layouts; consistent colors/icons; same chart style |
| **A**lignment | Every element ties to a grid line | Left edges line up; nothing floats |
| **P**roximity | Group related, separate unrelated | Caption sits *with* its image; sections breathe |

These four rules prevent ~80% of common slide design errors.

## Imagery

### Quality

- Minimum **150 DPI** at display size; **300 DPI** for printed handouts.
- Pixelation destroys credibility instantly.
- Hold **Shift while resizing** to constrain proportions — never stretch images non-uniformly.

### Purpose

- An image must **advance the argument**, not decorate. (Reynolds)
- If the image could be removed without loss, remove it.

### Full-bleed vs. framed

- **Full-bleed** (image covers the entire slide) creates emotional impact. Use for openers, section breaks, evocative moments. Add a semi-transparent scrim if text overlays.
- **Framed** (image with margin) suits comparative or analytical contexts.
- Pick one convention per section and apply consistently.

### Royalty-free sources

| Source | License notes |
|---|---|
| Unsplash, Pexels, Pixabay | Free, including commercial — verify each image's license |
| Getty, Shutterstock, Adobe Stock | Paid, commercial license included |
| Wikimedia Commons | Per-image license — check before use |
| AI-generated | Verify the model's license terms; current best practice is to credit |

Always verify license terms — "free for personal use" often excludes commercial decks.

## Icons

- **One icon family throughout.** Material Symbols, Phosphor, Heroicons, Font Awesome, Lucide. Mixing outline and filled, or different stroke weights, looks unprofessional.
- **Avoid clipart** — Microsoft's default emoji-style icons signal low effort unless used intentionally as a visual joke.
- **Size icons consistently** within a slide and across the deck.
- **Apply theme color**, not multicolor decoration.

## Slide Master Setup (the highest-leverage 30 minutes)

In View → Slide Master:

1. **Theme fonts**: Heading font + Body font.
2. **Theme colors**: 6–10 colors (background, text, accent, semantic). Use Design → Colors → Customize Colors.
3. **Layouts**: title, section divider, content (single-column), two-column, full-bleed image, data (chart-anchored), thank-you.
4. **Title placement**: same coordinates on every layout (title bar continuity).
5. **Footer**: page number + section name (or empty on title/section slides).
6. **Logo**: title and closing slides only.

Changes propagate to all slides — fix once, not 80 times.

## What Not to Do

- Hand-applying colors instead of theme colors (rebrand becomes a manual sweep).
- Using PowerPoint's stock themes (Ion, Facet, Wisp) verbatim — instantly recognizable as low effort.
- WordArt, drop shadows, gradient fills, beveled edges by default.
- Mixing left-alignment, center-alignment, and right-alignment within a single slide.
- Putting body text in 14pt to fit "just one more bullet."
