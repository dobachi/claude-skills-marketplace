---
name: pdf-extract
description: Extracts information from PDFs by triaging the file first (does a text layer exist? is the layout simple?) and routing to the cheapest path that survives it — native text extraction, OCR plus a layout-aware parser, or a vision model reading page images — then binds every extracted field to a page number and a verbatim span. Use when the user wants text, tables, or structured fields pulled out of a PDF — "PDFから抽出して", "PDFを読み取って", "この請求書/論文/報告書からデータを取って", "PDFを構造化データにして", "スキャンPDFをOCRして", "extract from this PDF", "parse this PDF", "OCR this scan", "get the tables out of this PDF". Also use when a PDF extraction already went wrong (garbled reading order, merged columns, broken tables, invented numbers). Not for summarizing text you have already extracted (`document-summary`), not for pulling out figures and images (`document-figures`), not for web research (`grounded-research`), not for auditing a finished document's claims (`fact-checker`), not for translating extracted text (`faithful-translation`).
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Extracted spans stay in the source language, always verbatim.

# PDF Extraction

Gets information out of PDFs without inventing any. A PDF does not store text — it stores instructions for painting glyphs at coordinates, so **every extraction is a reconstruction**, and every reconstruction can be wrong in ways that read perfectly. This skill picks the reconstruction method by triaging the file, then makes the result checkable: field → page → verbatim span.

**Out of scope**: summarizing already-extracted text (`document-summary`); extracting figures/images/charts as assets (`document-figures`); researching a topic across the web (`grounded-research`); auditing a finished document's factual claims (`fact-checker`, `verify-content`); translating what you extracted (`faithful-translation`); authoring PDFs (`marp-slides`, `pptx-build`).

## Core Principles

1. **Triage before extracting.** Whether a text layer exists decides everything downstream and takes seconds to check. Never pick a tool first and discover the file was a scan afterwards. Run `scripts/triage_pdf.py`.
2. **Reading order is a guess, not a property.** The PDF format lets page content be placed in any order; nothing in an untagged PDF records the order a human would read it. PyMuPDF's own docs list "text may not appear in any particular reading order" as a common problem. Multi-column pages are where this bites — verify order on a sample page before trusting a whole document.
3. **Separate transcription from interpretation.** Use a deterministic tool to get the bytes off the page; use the model to decide what they mean. A model asked to do both at once will smooth over what it could not read.
4. **Tables are the failure point.** They are the hardest element for every method and the one most likely to fail silently. Never serialize a complex table as Markdown — it cannot express merged cells or hierarchical headers. Use HTML.
5. **Schema-valid is not correct.** Constrained output fixes the shape of the answer and nothing about its truth. A perfectly-formed JSON object full of hallucinated values passes every structural check.
6. **Every field carries a page and a span.** An extracted value with no locator cannot be audited, and unauditable extraction is indistinguishable from generation.
7. **Confidence scores are triage, not a gate.** Self-reported confidence stays high when models are wrong. Gate on whether the span supports the field, never on a number the model produced about itself.

## Step 0 — Triage (mandatory)

```bash
python3 scripts/triage_pdf.py <file.pdf>          # per-page text-layer + layout signals
```

| Signal | What it means | Go to |
|---|---|---|
| Most pages yield substantial text | Digitally generated, text layer present | Path A (or C if you need judgment) |
| All pages yield ~0 characters | Image-only scan — no text to extract | Path B (OCR first) |
| Some pages empty, some not | Mixed document (scanned inserts, image pages) | Path B for the empty pages, A for the rest |
| Text present but columns interleave in output | Untagged multi-column layout | Path B (layout-aware parser) |
| Text present but tables collapse to word soup | Table structure is not recoverable from the text layer | Path B, or Path C for the table regions only |

An empty text layer is not an error — it is the diagnosis. `pymupdf4llm` returns empty strings for pages with no selectable text, and `pypdf` states outright that it "is not OCR software and will not be able to detect OCR failures, nor will it ever be able to extract text from images."

## Routing

| Path | Use when | Tools | Cost / speed |
|---|---|---|---|
| **A — Native text** | Text layer present, single-column or simple layout, you want the text | `pdftotext -layout`, `pymupdf4llm`, `pdfplumber` (coordinates), `pypdf` | Free, milliseconds |
| **B — OCR + layout parser** | Scans, multi-column, dense pages, tables, high volume, reproducibility matters | OCRmyPDF + Tesseract; Docling / MinerU / Marker / Unstructured | Free–cheap, GPU helps, seconds/page |
| **C — Vision model direct** | Charts and diagrams must be *understood*, layout is idiosyncratic, few pages, you need judgment not transcription | Claude / Gemini / OpenAI PDF input | Per-page tokens, highest unit cost |

**Do not default to Path C.** It is the most expensive per page and the only path that can invent content. Independent evaluations point both ways depending on the task — see the disagreement note in `references/routing.md` — so choose by document type and volume, not by reflex. Path C is strongest at *understanding* a page; Paths A and B are stronger at *transcribing* one.

Hybrid is normal and usually correct: Path B to get structured text and page images, Path C over the extracted regions to interpret them.

## Path A — Native text extraction

1. `pdftotext -layout` when column geometry matters; plain `pdftotext` outputs in reading order and undoes columns and hyphenation. Pick deliberately — they fail differently.
2. `pymupdf4llm` when you want Markdown for an LLM to consume.
3. `pdfplumber` when you need character/word bounding boxes — it infers words from character coordinates using an `x_tolerance` gap threshold, so tune it before blaming the PDF.
4. Spot-check one dense page and one table page against the rendered PDF. Do not skip this.

## Path B — OCR and layout-aware parsing

**Preprocess before OCR** — it is the highest-leverage step and the most often skipped:

| Fix | Why | How |
|---|---|---|
| Resolution ≥ 300 dpi | Tesseract "works best on images which have a DPI of at least 300 dpi" | `ocrmypdf --oversample 300` |
| Deskew | Skew "reduces significantly" line-segmentation quality and "severely impacts the quality of the OCR" | `ocrmypdf --deskew` |
| Page rotation | Sideways pages OCR to noise | `ocrmypdf --rotate-pages` |

Then parse. Parser selection and their documented limits are in `references/routing.md`. In short: Docling covers layout, reading order, tables, code, formulas and exports Markdown/HTML/JSON; MinerU emits JSON sorted by reading order with tables as HTML and formulas as LaTeX; Marker produces Markdown; Unstructured's `hi_res` classifies elements more accurately but is slower and needs `detectron2_onnx`, while `ocr_only` is its recommendation for multi-column documents lacking extractable text.

Every one of these tools documents that it degrades on complex layouts. Treat a clean-looking output on a hard page as unverified, not as success.

## Path C — Vision model direct

Per-vendor page limits, size limits, and token costs: `references/llm-apis.md` (dated — re-check before relying on a number).

Rules that hold across vendors:

- **Put the document before the prompt.** Anthropic's guidance is "Place PDFs before text in your requests"; Google's is to place the text prompt after the page.
- **Rotate pages upright before sending.** Both Anthropic and Google list this explicitly.
- **Cite by the page number the reader sees** — use the logical page number from the PDF viewer in prompts, not an internal index.
- **Split large PDFs.** Page ceilings are hard limits, and cost is linear in pages.
- **Cache and batch** repeated analysis of the same document rather than re-sending it.
- **Never send only the page image when you have a text layer.** Sending an image alone invites the model to complete unfinished sentences and invent text where the image is ambiguous. Send both, or send text and use the image for layout questions.

## Structured extraction contract

When the deliverable is fields rather than prose, all four apply — see `references/extraction-contract.md` for the schema pattern and worked example.

1. **Constrain the schema.** Both Anthropic and OpenAI support schema-constrained output, with different unsupported-keyword lists — check `references/extraction-contract.md` before writing a schema that will be rejected.
2. **Order schema keys so reasoning precedes the answer.** Key order determines generation order; putting the answer field first forces the model to answer before it reasons.
3. **Require a locator per field**: `{value, page, span, confidence}` where `span` is verbatim source text. A field whose span does not contain the value is a failed extraction regardless of how plausible the value is.
4. **Prefer a native citation mechanism** where one exists — it returns real offsets rather than model-written ones. Note the limit: citation features that work on extracted text cannot cite a scanned page that has no extractable text.

## Verification gate

Run before delivering. A silent extraction failure looks exactly like a success.

1. **Every field → page → span?** Missing locator: re-extract or mark unknown. Never fill from prior knowledge of the document type.
2. **Span actually contains the value?** Check the string, don't eyeball it. Numbers, units, currency, dates, signs.
3. **Totals reconcile?** Line items sum to the stated total; percentages sum plausibly. This catches merged-cell errors nothing else catches.
4. **Table shape preserved?** Row and column counts match the rendered page. Merged cells and hierarchical headers intact.
5. **Reading order sane on a multi-column sample?** Read one extracted page end to end.
6. **Nothing extracted from a blank or unreadable page.** Content attributed to a page that has none is hallucination, full stop.
7. **Empty is a valid answer.** "This field is not in the document" must be reachable, or the model will manufacture it.
8. **Downstream check, not just the extraction metric.** High character-level accuracy does not imply the result works for what you built it for — structural errors survive a good OCR score.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Extracting before triaging | Runs a text extractor on a scan and gets an empty file, or worse, a nearly-empty one | `scripts/triage_pdf.py` first |
| Defaulting to "just send it to the model" | Most expensive path, and the only one that can invent content | Route by triage; hybrid |
| Markdown for complex tables | Cannot express merged cells or hierarchical headers — data is lost at serialization, silently | HTML tables |
| Trusting schema-valid output | Constrained decoding fixes shape, not truth | Locator per field + gate |
| Using the model's confidence as the gate | Stated confidence stays high when the model is wrong | Gate on span↔value |
| One prompt for transcribe + interpret | The model papers over what it could not read | Transcribe, then interpret |
| Accepting clean output on a hard page | Every parser degrades on complex layouts; the output does not say so | Spot-check against the render |
| Page images only, no text layer | Invites completion of unfinished sentences and invented text | Send text + image |
| Ignoring cross-page tables | Repeated headers and "continued" rows become phantom data rows | Merge before serializing |
| Optimizing the OCR score | A good character-accuracy number can coexist with a broken downstream result | Evaluate on the real task |

## References

- `references/routing.md` — path selection detail, per-tool documented capabilities and limits, the VLM-vs-pipeline disagreement and how to resolve it for your document
- `references/llm-apis.md` — vendor PDF input specs (page/size limits, token costs, best practices), with access dates
- `references/extraction-contract.md` — schema patterns, unsupported JSON Schema keywords per vendor, citation mechanisms, worked field-extraction example
- `scripts/triage_pdf.py` — text-layer and layout triage (stdlib + poppler)

Evidence behind the rules in this skill, with sources and verbatim spans: `docs/pdf-extract-design.md` in the repository root.
