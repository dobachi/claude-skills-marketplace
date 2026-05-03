---
name: document-figures
description: Extracts figures from existing documents (PDF, Word, PowerPoint, web) with provenance and creates new structural diagrams (Mermaid-first), producing a Figure Ledger that chains into document-summary
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Output language can differ from source language.

# Document Figures Expert

Handles figures for document summarization workflows. Two operations: **extract** figures from existing documents (PDF / Word / PowerPoint / web) with provenance preserved, and **create** new structural diagrams (Mermaid-first) when the source has no figure or its figure is unsuitable. Both feed downstream summaries via a **Figure Ledger** that mirrors `document-summary`'s Claim Ledger discipline.

**Out of scope**: full-text extraction (use Read or `document-summary`); chart authoring from raw data (chain `data-analyst`); PowerPoint design principles (use `pptx-design`); slide deck authoring (use `marp-slides` or `pptx-design`); OCR or image-to-text (out for v1); image upscaling / enhancement (out for v1); caption translation (chain `faithful-translation`).

## Core Principles

1. **Provenance first.** Every figure has a stable ID (`F-NN`) and a verifiable origin. Extracted figures cite source file + page/slide + caption when recoverable. Created figures cite design rationale + the Claim Ledger ID(s) they support.
2. **The information test governs creation.** *If I deleted the shapes and arrows and left only the text, what would I lose? If "nothing meaningful," it is not a diagram — it is bullets in costume.* Reject decorated bullets, default-SmartArt theater, and decorative arrows. See `references/creation.md` and `pptx-design/references/diagrams-and-architecture.md`.
3. **Format-appropriate strategy.** Embedded-asset extraction for speed (raw images out of the container); page/slide rendering when layout matters; Puppeteer for web. No one-size-fits-all.
4. **Mermaid by default for creation.** Text-based, deterministic, reviewable, copy-paste-ready, integrates with `marp-slides` and most Markdown renderers. Rasterize only when a downstream consumer requires PNG/SVG.
5. **Caption ↔ figure are linked.** A figure without a caption is incomplete. Recover the source caption when possible; if writing a caption because the source had none, mark it `[reconstructed]` or `[inferred from §X]` — never present a written caption as if it were the source's own.
6. **Selective by default.** Extract figures relevant to the summary's claims. Bulk extraction (Workflow C) is opt-in for archival / triage, not for summary integration.
7. **No invented data.** If a chart's underlying numbers are not in the source, do not regenerate it from imagined values. Either extract the original image or describe the chart in text.

## Operation Matrix

| Source format | Extract embedded | Render page/slide | Caption recovery | Tooling |
|---|---|---|---|---|
| PDF | yes (`pdfimages`) | yes (`pdftocairo`) | partial — text-near-bbox heuristic via `pdftotext -bbox-layout` | poppler-utils |
| DOCX | yes (`unzip word/media/`) | n/a | yes — alt-text (`wp:docPr/@descr`) + Caption-styled paragraph siblings | unzip + xmllint |
| PPTX | yes (`unzip ppt/media/`) | yes (LibreOffice headless, optional) | yes — per-slide title + alt-text | unzip + xmllint |
| HTML / web | yes — `<img>` + `<figure>` DOM walk | yes — Puppeteer full-page PNG | yes — `alt` + `<figcaption>` | Puppeteer |

## Diagram-Type Selection (for the *create* path)

| When the source / claim describes… | Recommended diagram |
|---|---|
| Sequential process or decision flow | `flowchart` (TD or LR) |
| Time-ordered events | `timeline` or `gantt` |
| Actor interactions | `sequenceDiagram` |
| State machine | `stateDiagram-v2` |
| Entities + relationships | `erDiagram` |
| Hierarchy / breakdown | `mindmap` or block diagram |
| 2×2 positioning | `quadrantChart` |
| Categorical share | `pie` |
| XY data | `xychart-beta` |
| Flow volumes / Sankey | `sankey-beta` |
| Comparison matrix / table | **Markdown table — not Mermaid** |

Detail and worked examples: `references/creation.md`.

## Workflows

### Workflow A — Extract for an existing summary

Input: source document(s) + a Claim Ledger from `document-summary`. For each claim of class "evidence-by-figure," locate the source figure, extract it with provenance, and emit a Figure Ledger that cross-links to the Claim Ledger IDs.

| Step | Action | Output |
|---|---|---|
| 1 | Read the Claim Ledger; flag claims whose evidence is a figure (chart, diagram, screenshot) | List of claim → source-figure pointers |
| 2 | Run the format-appropriate extractor (`extract_pdf.sh` / `extract_office.sh` / `extract_web.js`) | `figures/*.png` + `manifest.json` |
| 3 | Pick the relevant figure(s); discard noise (icons, decorations) | Filtered subset |
| 4 | Recover or write captions; mark reconstructed captions explicitly | Figure metadata complete |
| 5 | Emit the Figure Ledger with `linked_claim` cross-references | `FIGURES.md` + updated `manifest.json` |

### Workflow B — Create figures for a summary

Input: a Claim Ledger. Identify structural / sequential / comparative claims that benefit from a diagram, propose Mermaid for each, apply the information test, and emit a Figure Ledger (origin: created).

| Step | Action | Output |
|---|---|---|
| 1 | Read the Claim Ledger; identify candidate diagram opportunities | List of `(claim group, suggested diagram type)` |
| 2 | For each candidate, draft Mermaid source | `mermaid/F-NN.mmd` |
| 3 | **Information test pass** — for each draft, ask: would the text alone convey the same information? If yes, delete the draft. | Filtered diagram set |
| 4 | Optional: rasterize via `render_mermaid.js` for downstream consumers that need PNG/SVG | `figures/F-NN.png` |
| 5 | Emit the Figure Ledger with `linked_claim` references | `FIGURES.md` |

### Workflow C — Bulk inventory

Input: source document(s). Output: every embedded figure with metadata. Used for archival / triage, not summary integration. Run the appropriate extractor with no filtering; emit `manifest.json` with provenance.

## Script Invocation

All scripts live under `<skill-path>/scripts/`. Run from any working directory; pass absolute paths or paths relative to CWD.

```bash
# PDF — extract embedded images and/or render pages
bash <skill-path>/scripts/extract_pdf.sh path/to/source.pdf --out figures/

# DOCX or PPTX — auto-detected by extension
bash <skill-path>/scripts/extract_office.sh path/to/source.pptx --out figures/

# Web — DOM walk + optional full-page screenshot
node <skill-path>/scripts/extract_web.js https://example.com/article --out figures/ --include-screenshot

# Mermaid — rasterize source to PNG/SVG (optional; emit text-only by default)
node <skill-path>/scripts/render_mermaid.js mermaid/F-03.mmd --out figures/F-03.png
```

Each script accepts `--help`. Stderr carries diagnostics; stdout carries the manifest path or rendered output.

## Figure Ledger (mandatory artifact)

The Figure Ledger is the integrity record. Required for every deliverable.

```markdown
| ID    | Origin       | Source reference            | Caption / Description                | Linked claim |
|-------|--------------|-----------------------------|--------------------------------------|--------------|
| F-01  | Extracted    | source.pdf, p.7, fig.2      | Bar chart of revenue by segment      | C-03         |
| F-02  | Extracted    | source.pptx, slide 12       | Architecture diagram                 | C-05         |
| F-03  | Created      | encodes Mermaid flowchart   | Decision flow synthesizing C-08..10  | C-08, C-10   |
| F-04  | Reconstructed| source.docx, fig.1 (caption written; original had alt-text only) | …    | C-11         |
```

Conventions:
- **Origin**: `Extracted` (file from source) / `Created` (new diagram) / `Reconstructed` (extracted figure with a caption you wrote because the source had none).
- **Source reference grammar** per format (PDF: `file, p.N, fig.M`; PPTX: `file, slide N`; DOCX: `file, fig.N`; HTML: `URL, fig.N`).
- **Linked claim**: comma-separated Claim Ledger IDs (`C-NN`) the figure supports. May be empty for purely illustrative figures, but flag those — most deliverables should reject illustrative-only figures.

Schema detail and edge cases: `references/ledger.md`.

## Quality Rubric (5 axes)

| Dimension | Strong | Adequate | Weak |
|---|---|---|---|
| **Provenance** | Every figure has source ref + caption + linked claim | Minor caption gaps | Origin unknown; no manifest |
| **Information density** | Every diagram passes the information test | One borderline diagram | Decorated bullets present |
| **Caption fidelity** | Source captions verbatim; reconstructed ones flagged | Mostly faithful | Captions invented as if source's |
| **Format fit** | Right tool per format; layout preserved when needed | Good enough | Wrong extraction mode (raw when render needed, etc.) |
| **Reproducibility** | Manifest + Mermaid source committed; rerun deterministic | Manifest present | Output not reproducible |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| **Bulk extract without provenance** | Source attribution lost; downstream cannot cite | Always emit `manifest.json` with per-figure origin |
| **Decorated bullets dressed as a flowchart** | Mermaid nodes that just list items; arrows decorative | Information test before emitting any diagram |
| **Caption invented to match the figure** | Hallucinated source content | Mark `[reconstructed]` or `[inferred from §X]`; never as the source's own |
| **Decorative arrows** | Arrows whose meaning shifts (sometimes flow, sometimes dependency, sometimes time) | One arrow semantic per diagram + a legend |
| **Mismatched abstraction levels** | "Cloud" alongside a function name alongside a buzzword | Pick one level; stay there |
| **Re-rendering when the source figure is fine** | Wasted effort + drift from source | Prefer extracted; create only when extracted is unsuitable or absent |
| **Chartjunk** | Gradients, 3D, drop shadows on Mermaid output | Tufte data-ink ratio; see `pptx-design/references/data-visualization.md` |
| **Invented chart data** | Recreating a chart from imagined numbers | If data is not in the source, extract the original image or describe in text |
| **Illustrative-only figures** | Decoration with no claim linkage | Drop or attach to a real claim before shipping |

## Deliverable Formats

| Artifact | Purpose |
|---|---|
| `figures/` | Extracted PNG/JPG/SVG (and optionally rasterized Mermaid) |
| `mermaid/` | `.mmd` source for created diagrams (text, reviewable, version-controllable) |
| `manifest.json` | Machine-readable Figure Ledger (per-figure: id, origin, source_reference, caption, linked_claim, sha256) |
| `FIGURES.md` | Human-readable Figure Ledger; thumbnails + rationale; ready to chain into `document-summary` |

## Iteration Modes

| Mode | When to use |
|---|---|
| **Extract-only** | Source figures are sufficient; no creation needed |
| **Create-only** | Source has no figures; build diagrams from the Claim Ledger |
| **Hybrid** | Mix of extracted and created (most common for summaries) |
| **Re-render** | Update Mermaid source; rerun `render_mermaid.js` to refresh PNG |
| **Cross-link audit** | Walk every Figure Ledger row; verify each `linked_claim` resolves in the Claim Ledger |

## Prerequisites

- **Node.js 18+**
- **Puppeteer** (`npm install puppeteer`) — also required by `fact-checker`
- **poppler-utils** — `pdfimages`, `pdftocairo`, `pdftotext` (`apt install poppler-utils` / `brew install poppler`)
- **xmllint** — `apt install libxml2-utils` / `brew install libxml2`
- **(optional) LibreOffice** — for slide-to-PNG rendering of PPTX

## References (consult when relevant)

- `references/extraction.md` — per-format extraction recipes (PDF / DOCX / PPTX / HTML); caption recovery heuristics; `srcset` and relationship-id resolution
- `references/creation.md` — Mermaid syntax cookbook per diagram type; the information test with worked pass/fail examples; chartjunk avoidance; SVG-direct fallbacks
- `references/ledger.md` — Figure Ledger schema; cross-linking with `document-summary`'s Claim Ledger; ID conventions; edge cases (figure-of-a-figure, multi-panel partial extraction, redacted figures)
