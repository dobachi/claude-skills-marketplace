# Routing Detail

Path selection, per-tool documented behavior, and what to do when the evidence points both ways.

## Why triage decides everything

A PDF stores glyph-painting instructions, not text. `pypdf`'s documentation states it directly: "The text within a PDF document is absolutely positioned, meaning that every single character could be positioned on the page," and "PDF files don't contain a semantic layer." There is no stored notion of a word, a paragraph, a column, or a table — every one of those is inferred by whatever tool you point at the file.

That inference is only possible when a text layer exists. Two facts follow:

- **No text layer → no amount of library tuning helps.** `pypdf`: "pypdf is not OCR software and will not be able to detect OCR failures, nor will it ever be able to extract text from images." `pymupdf4llm`: "Pages with no selectable text will return empty strings."
- **Text layer present ≠ correct order.** Tagged PDF carries a logical structure tree, but most PDFs in the wild are untagged. W3C's WCAG technique PDF3 notes that when "the document is not properly tagged, a screen reader may read the document from top to bottom, across both columns, interpreting them as one column" — the same failure a text extractor produces. PyMuPDF's docs list it as a known issue: "One of the common issues with PDF text extraction is, that text may not appear in any particular reading order."

## Path A — native text tools

| Tool | Documented behavior | Use it for |
|---|---|---|
| `pdftotext` (poppler) | `-layout` "Maintain (as best as possible) the original physical layout of the text." Default "is to 'undo' physical layout (columns, hyphenation, etc.) and output the text in reading order." | Fast bulk text; `-layout` when column geometry carries meaning |
| `pymupdf4llm` | "turns PDFs into clean, structured data with minimal setup"; returns empty strings for pages with no selectable text | Markdown for LLM consumption |
| PyMuPDF `get_text()` | Plain text "as it is coded in the document. No effort is made to prettify in any way." | Raw text when you will post-process yourself |
| `pdfplumber` | "Plumb a PDF for detailed information about each text character, rectangle, and line." Words are inferred: characters group into a word when "the difference between the x1 of one character and the x0 of the next is less than or equal to x_tolerance" | Coordinates, bounding boxes, positional logic |
| `pypdf` | Pure-Python text extraction; not OCR | Simple text-layer documents, no native deps |

`pdftotext` with and without `-layout` produce genuinely different failure modes. Layout mode preserves visual columns and can leave ragged whitespace mid-sentence; default mode reflows and can interleave columns. Try both on a sample page.

## Path B — OCR and layout-aware parsers

### Preprocessing (before OCR, not after)

Tesseract's own quality guide is explicit on all three:

- Resolution: "Tesseract works best on images which have a DPI of at least 300 dpi, so it may be beneficial to resize images."
- Skew: "The quality of Tesseract's line segmentation reduces significantly if a page is too skewed, which severely impacts the quality of the OCR. To address this rotate the page image so that the text lines are horizontal."
- Binarization: "Tesseract does this internally (Otsu algorithm), but the result can be suboptimal, particularly if the page background is of uneven darkness."

OCRmyPDF wraps these: `--deskew` "will correct pages that were scanned at a skewed angle by rotating them back into place"; `--oversample DPI` can "resample images to higher resolution before attempting OCR; this can improve results as well"; `--rotate-pages-threshold` tunes how aggressively pages are auto-rotated.

### Parser comparison

| Parser | Documented output | Documented limits |
|---|---|---|
| **Docling** | "Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more." Exports "Markdown, HTML, WebVTT, DocLang, DocTags and lossless JSON." Pluggable OCR: `EASYOCR, OCRMAC, RAPIDOCR, TESSERACT, TESSERACT_CLI`, plus `force_full_page_ocr` | No explicit limitations section found in the docs consulted — absence of a stated limit is not evidence of none |
| **MinerU** | "JSON sorted by reading order"; "Output text in human-readable order, suitable for single-column, multi-column, and complex layouts"; tables → HTML; formulas → LaTeX | "In scenarios such as complex layouts, scanned pages, and handwritten content, the parsing results may fall short of expectations" |
| **Marker** | Markdown with "image links…, formatted tables, embedded LaTeX equations (fenced with $$), Code is fenced with triple backticks, Superscripts for footnotes"; "Garbled or scanned pages are OCR'd by the VLM" | "Very complex layouts, with nested tables and forms, may not work" — mitigated by `--use_llm` and `--force_ocr` |
| **Unstructured** | `hi_res` "Employs a document layout analysis model (detectron2_onnx) to identify the structural organization of content"; `ocr_only` runs Tesseract then processes the text | `hi_res` "provides superior accuracy for element classification but requires detectron2_onnx installation and processes more slowly"; `ocr_only` is "Recommended for multi-column documents lacking extractable text or when layout detection struggles with element ordering" |

Prefer the parser whose native output format matches what you need. MinerU's reading-order-sorted JSON and HTML tables are the closest fit for structured field extraction; Marker and `pymupdf4llm` are the closest fit for "give an LLM readable Markdown."

## The VLM-vs-pipeline disagreement

Two credible bodies of evidence point in opposite directions. **Do not average them** — they measure different tasks.

| Source | Finding | Scope |
|---|---|---|
| OmniDocBench (arXiv:2412.07626, Dec 2024) | "VLMs, however, struggle with high-density documents like newspapers due to limitations in input resolution and token length. In contrast, pipeline tools leverage layout-based segmentation to process components individually, maintaining accuracy in complex layouts." | Full-page document parsing |
| "Beyond String Matching" (arXiv:2603.18652, Mar 2026) | "The top-performing systems are the Gemini 3 models, general-purpose multimodal models rather than dedicated OCR tools." "Rule-based tools (PyMuPDF4LLM, GROBID) require no GPU but lag substantially behind all learning-based approaches." | Table extraction specifically |
| NVIDIA, "Approaches to PDF Data Extraction for Information Retrieval" | "The baseline NeMo Retriever pipeline outperformed the VLM across all visual modalities, with an overall delta of 7.2%." "…significantly higher throughput, 32.3x, and lower latency compared to the much larger VLM model." | Retrieval-oriented extraction at volume |

**Conflict type: task scope plus date.** Frontier VLMs have closed much of the gap on *isolated table extraction* since late 2024, while pipelines retain the advantage on *dense full-page parsing at volume* — where resolution ceilings, token limits, throughput, and cost all favor segmentation. The same 2026 paper that puts VLMs on top also concludes "accurate table extraction from PDFs remains unsolved," so neither side is a solved problem.

Resolve it per document, not once:

- Few pages, idiosyncratic layout, judgment needed → VLM.
- Many pages, uniform layout, throughput or cost matters → pipeline.
- Dense pages (newspapers, financial statements, multi-column journals) → pipeline for segmentation, VLM per region.
- Anything you must reproduce byte-for-byte later → pipeline; sampling-based VLM output varies.

## Known failure modes to check for

Each is documented in the sources behind this skill; each is invisible in the output unless you look.

| Failure | Where it shows up | Detection |
|---|---|---|
| Multi-column merged into one | Untagged PDFs; some VLMs "in specific PDF types (such as slides or financial reports), tend to merge multi-column text" | Read one extracted page end to end |
| Reading order scrambled | Any untagged PDF; notes and sidebars especially | Compare to the render |
| Hallucinated content | "Some vision language models generate hallucinated information based on the content they can recognize" | Span must exist in source |
| Invented text on blank/ambiguous pages | Models never trained on blank pages "would hallucinate in such cases"; page-image-only prompting is "prone to models completing unfinished sentences, or to invent larger texts when the image data was ambiguous" | Assert blank pages produce empty output |
| Repetition loops | Low sampling temperature raises the risk; olmOCR 2 mitigates with dynamic temperature scaling from 0.1 up to 0.8, triggered by failure to emit an EOS token | Check for long repeated n-grams |
| Merged/spanning cell errors | Complex tables; "handling multi-dimensional cell merging remains a key differentiator" | Row/column counts + totals reconcile |
| Cross-page table fragmentation | Tables with repeated headers and "Table continued" markers | Merge continuations into one table before serializing |
| Missed chart legends and annotations | "Critical text annotations, detailed legends, or specific data within charts or infographics were sometimes missed by the VLM, whereas OCR-based methods excel at capturing this text" | Cross-check figures with an OCR pass |

## Benchmark scores are not your document

Two cautions before trusting any published number:

- Benchmark scores do not transfer. Models "achieving near perfect scores on OmniDocBench decline sharply on InduOCRBench. PP-StructureV3 drops from 86.7% to 60.3% (26.4 points), GPT 4o from 75% to 52%, and PaddleOCR-VL from 92.9% to 78.2%."
- The metric you optimize may not be the outcome you want: "high OCR accuracy does not necessarily translate into strong downstream RAG performance: structural and semantic errors can cause substantial retrieval failures even when WER/CER remains low."

Evaluate on a sample of your own documents, scored on the task you actually need.
