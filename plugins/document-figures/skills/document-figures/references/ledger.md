# Figure Ledger — Schema and Cross-Linking

The Figure Ledger is the integrity record for figures, mirroring the **Claim Ledger** pattern from `document-summary`. It is mandatory for any deliverable that includes figures.

## Schema

### Markdown form (human-readable, ships in `FIGURES.md`)

```markdown
| ID    | Origin       | Source reference                    | Caption / Description                       | Linked claim |
|-------|--------------|-------------------------------------|---------------------------------------------|--------------|
| F-01  | Extracted    | source.pdf, p.7, fig.2              | Bar chart of revenue by segment, 2018-2024  | C-03         |
| F-02  | Extracted    | source.pptx, slide 12, img.1        | System architecture diagram                 | C-05         |
| F-03  | Created      | encodes Mermaid flowchart           | Decision flow synthesizing C-08..C-10       | C-08, C-10   |
| F-04  | Reconstructed| source.docx, fig.1 (caption written; original had alt-text only) | Sales pipeline by stage    | C-11         |
```

### JSON form (machine-readable, ships in `manifest.json`)

```json
{
  "source": "/abs/path/source.pdf",
  "source_format": "pdf",
  "extracted_at": "2026-05-03T12:00:00Z",
  "figures": [
    {
      "id": "F-01",
      "origin": "Extracted",
      "file": "figures/F-01.png",
      "source_reference": "source.pdf, p.7, fig.2",
      "source_page": 7,
      "bbox": [120, 340, 480, 620],
      "caption": "Bar chart of revenue by segment, 2018-2024",
      "caption_confidence": "recovered",
      "alt_text": null,
      "linked_claim": ["C-03"],
      "sha256": "abc123…"
    },
    {
      "id": "F-03",
      "origin": "Created",
      "file": "mermaid/F-03.mmd",
      "rendered_file": "figures/F-03.png",
      "source_reference": "encodes Mermaid flowchart",
      "caption": "Decision flow synthesizing C-08..C-10",
      "caption_confidence": "authored",
      "linked_claim": ["C-08", "C-10"],
      "rationale": "C-08 establishes the cache-hit path, C-10 establishes the cache-miss path; the flowchart combines them to make the branching legible at a glance",
      "diagram_type": "flowchart"
    }
  ]
}
```

## Field Definitions

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | `F-NN` numeric, zero-padded for ≥10 figures (`F-01`, `F-02`, … `F-15`) |
| `origin` | enum | yes | `Extracted` \| `Created` \| `Reconstructed` |
| `file` | string | yes | Path to the figure file (PNG/JPG/SVG for extracted; `.mmd` for created) |
| `rendered_file` | string | no | For Created figures with rasterization, the PNG/SVG path |
| `source_reference` | string | yes | Provenance string in the per-format grammar (see below) |
| `source_page` / `source_slide` | number | conditional | Numeric page or slide for Extracted figures from PDF/PPTX |
| `bbox` | `[x1, y1, x2, y2]` | no | PDF only; image bounding box on the page |
| `caption` | string | yes (or null with explicit reason) | Human-readable caption |
| `caption_confidence` | enum | yes | `recovered` (from source verbatim) \| `reconstructed` (you wrote it from neighboring text) \| `authored` (Created origin) \| `none` (no caption available) |
| `alt_text` | string \| null | yes | Alt text from the source; `null` if absent |
| `linked_claim` | string[] | yes (may be empty) | Claim Ledger IDs (`C-NN`) the figure supports |
| `rationale` | string | conditional | For Created figures, why this diagram and not text/list |
| `diagram_type` | string | conditional | For Created figures, the Mermaid type (`flowchart`, `sequenceDiagram`, etc.) |
| `sha256` | string | yes (Extracted) | Content hash for dedup |

## Origin Field Conventions

- **Extracted** — figure came from the source document. `source_reference` cites the source file + location; `caption_confidence` is `recovered` (caption was in the source) or `none` (no caption available; consider adding a caption and switching origin to `Reconstructed`).
- **Reconstructed** — figure came from the source document, but you wrote a caption because the source had only alt-text or no caption text. `caption_confidence` is `reconstructed`. The `caption` field should explain provenance: `"<text>" [reconstructed from §3 surrounding paragraph]`.
- **Created** — new diagram authored by the skill (Mermaid or SVG). `source_reference` is descriptive (`encodes Mermaid flowchart`); `caption_confidence` is `authored`; `rationale` is required.

## Source Reference Grammar (per format)

| Source | Grammar | Example |
|---|---|---|
| PDF | `<filename>, p.<N>, fig.<M>` (or `img.<M>` if no figure number) | `paper.pdf, p.7, fig.2` |
| DOCX | `<filename>, fig.<N>` (or `img.<N>`) | `report.docx, fig.4` |
| PPTX | `<filename>, slide <N>, img.<M>` | `deck.pptx, slide 12, img.1` |
| HTML | `<URL>, fig.<N>` | `https://example.com/article, fig.3` |
| Created | `encodes <type> diagram` | `encodes Mermaid sequenceDiagram` |
| Reconstructed | original grammar + `(caption [reconstructed])` | `report.docx, fig.4 (caption [reconstructed])` |

Always use the source filename or full URL. Bare numeric IDs without filename are not provenance.

## Cross-Linking with Claim Ledger

The Claim Ledger (from `document-summary`) and the Figure Ledger reference each other.

### From Claim Ledger → Figure Ledger

When a claim's evidence is a figure, add an `evidence` field (or extend the existing source-reference column):

```markdown
| ID    | Claim                                    | Source span         | ... | Evidence |
|-------|------------------------------------------|---------------------|-----|----------|
| C-03  | Revenue grew 18% YoY in segment A         | §4.2, p.18         | ... | F-01     |
```

### From Figure Ledger → Claim Ledger

`linked_claim` is an array of `C-NN` IDs:

```markdown
| ID    | ... | Linked claim |
|-------|-----|--------------|
| F-01  | ... | C-03         |
| F-03  | ... | C-08, C-10   |
```

### Cross-link audit

Before delivery, verify:
1. Every `evidence: F-NN` in the Claim Ledger resolves to a row in the Figure Ledger.
2. Every `linked_claim: C-NN` in the Figure Ledger resolves to a row in the Claim Ledger.
3. Bidirectional consistency — if `C-03` cites `F-01`, then `F-01` should list `C-03` in `linked_claim`.

This audit is the analogue of `document-summary`'s self-verification pass.

## ID Conventions

- `F-NN` — figures (this ledger)
- `C-NN` — claims (from `document-summary`)
- `I-NN` — inferences (from `document-summary`)
- Numeric, zero-padded when ≥10 entries (`F-01` through `F-15`)
- IDs are stable within a deliverable; do not renumber when adding figures (append `F-16`, etc.)
- Across multiple sources or chained deliverables, prefix the source: `src1:F-01`, `src2:F-01`

## Edge Cases

### Figure-of-a-figure (screenshot of someone else's chart)

Source contains an image that is itself a screenshot of a third-party figure. The Figure Ledger entry is for *the source's image*, not the original chart. In `caption`, note the secondary provenance:

```
caption: "Industry growth chart [reproduced from Acme Industries 2024 Annual Report, Fig. 3]"
caption_confidence: recovered
```

If you have access to the *primary* source, consider chaining: extract from there too as a separate figure (`F-02`) with its own provenance.

### Multi-panel figures

A single visual figure may contain multiple panels (a, b, c, d), and `pdfimages` extracts each as a separate file. Group them:

```json
{
  "id": "F-05",
  "origin": "Extracted",
  "file": "figures/F-05a.png",
  "panels": [
    {"label": "a", "file": "figures/F-05a.png", "bbox": [...]},
    {"label": "b", "file": "figures/F-05b.png", "bbox": [...]}
  ],
  "source_reference": "paper.pdf, p.7, fig.2 (4-panel figure)",
  ...
}
```

### Partial extraction (one panel of many)

If only one panel is relevant to a claim, extract just that one but note in `caption`:

```
caption: "Panel (b) of Figure 2: response curve for treatment B [other panels not extracted]"
```

### Redacted / proprietary figures

If a figure exists in the source but cannot be reproduced (license, redaction), record the slot:

```json
{
  "id": "F-06",
  "origin": "Extracted",
  "file": null,
  "source_reference": "report.pdf, p.12, fig.4",
  "caption": "[figure not reproduced — proprietary; see source]",
  "caption_confidence": "recovered",
  "linked_claim": ["C-15"]
}
```

This preserves the citation chain even when the asset cannot ship.

### Same figure across multiple sources

Use SHA-256 to detect duplicate extractions. If the same image appears in two source documents, decide:
1. **Per-source** — keep both `F-01` (source A) and `F-02` (source B); cross-reference in `caption`.
2. **Canonical** — one entry; list multiple `source_reference`s as `["src_a.pdf, p.5", "src_b.pdf, p.12"]`.

Default to per-source for traceability; switch to canonical when the figure is genuinely shared (e.g., a published chart cited by both sources).

## Illustrative-Only Figures

A figure with empty `linked_claim` and no caption in the source is decoration. Default policy: drop. If retained (e.g., user explicitly wants it for visual texture), tag clearly:

```json
{
  "id": "F-07",
  "origin": "Extracted",
  "linked_claim": [],
  "caption": "[illustrative, no claim linkage]",
  ...
}
```

Most deliverables — especially summaries — should reject illustrative-only figures.
