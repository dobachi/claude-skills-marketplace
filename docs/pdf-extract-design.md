# pdf-extract — Design Notes and Evidence Base

Why the `pdf-extract` skill routes the way it does, and the sources behind every rule in it.
Produced with the `grounded-research` skill (Standard depth) on **2026-08-01**.

Method: 5 parallel retrieval subagents returning only verbatim span tuples; a Source Register
built from what they quoted; blind per-claim verification (one subagent per claim, seeing the
claim and the span and nothing else); refutation on the two load-bearing recommendations.
The lead did not search — every claim below traces to a registered span.

**Sources**: 36 registered (T1: 24, T2: 11, T3: 1). **Claims**: 46, all blind-verified.

---

## Bottom line

PDF extraction has no single best method, and the widely-repeated shortcut — "just send the PDF
to a multimodal model" — is refuted by the evidence for anything beyond a handful of pages.
What determines quality is **triage before tool choice**: whether a text layer exists, whether the
layout is multi-column, and whether tables carry meaning. Those three facts pick the path. Every
path then needs the same discipline at the output end, because all of them fail silently: bind
each extracted value to a page and a verbatim span, and check the span mechanically.

## Findings

### 1. The format itself is the root cause

A PDF does not store text. It stores absolutely-positioned glyphs [C-01] and carries no semantic
layer [C-02]. Word boundaries are not stored either — `pdfplumber` reconstructs words by grouping
characters whose horizontal gap falls within a tolerance [C-05]. Reading order is likewise not a
property of the file: PyMuPDF's own documentation lists "text may not appear in any particular
reading order" as a common problem [C-04], and W3C's WCAG technique describes the same failure for
untagged multi-column pages, where a reader traverses "across both columns, interpreting them as
one column" [C-03].

Consequence for the skill: reading order and table structure must be *verified*, never assumed,
whatever tool produced them.

### 2. Triage is cheap and decides everything

The text-layer question is answerable in seconds and forecloses whole branches. `pypdf` states it
is not OCR software and will never extract text from images [C-06]; `pymupdf4llm` returns empty
strings for pages with no selectable text [C-07]. That same behavior is a *detector*: an empty
extraction is a diagnosis, not a failure. Scanned documents may also carry a text layer behind the
page image [C-09], which is why the presence of *some* text does not settle whether OCR quality is
adequate.

This finding is what the bundled `scripts/triage_pdf.py` implements.

### 3. OCR quality is decided before OCR runs

Tesseract's own guidance sets the two preprocessing steps that matter: at least 300 DPI [C-10],
and deskewing, because skew "reduces significantly" line-segmentation quality and "severely
impacts the quality of the OCR" [C-11]. OCRmyPDF exposes both as flags [C-12][C-13]. Preprocessing
is the cheapest available accuracy gain and the most commonly skipped one.

### 4. Layout-aware parsers all document their own limits

Docling covers layout, reading order, tables, code, formulas and image classification [C-14] and
exports Markdown/HTML/JSON [C-32]. MinerU emits reading-order-sorted JSON with tables as HTML and
formulas as LaTeX [C-15][C-33], and states plainly that results "may fall short of expectations"
on complex layouts, scans, and handwriting [C-16]. Marker documents that very complex layouts with
nested tables and forms "may not work" [C-31]. Unstructured's `hi_res` classifies better but runs
slower and needs `detectron2_onnx`, while `ocr_only` is its own recommendation for multi-column
documents lacking extractable text [C-17].

Consequence: a clean-looking output on a hard page is unverified, not successful. Every vendor in
this category says so about their own tool.

### 5. All three LLM vendors send text *and* images

Claude converts each page to an image and supplies the extracted page text alongside it [C-19];
OpenAI "extracts both text and page images and sends both to the model" [C-22]; Gemini uses native
vision over the document. Limits differ and are dated in `references/llm-apis.md`: Claude 600
pages / 32 MB [C-18] at 1,500–3,000 text tokens per page plus image tokens [C-20]; OpenAI 50 MB
per file and combined [C-23]; Gemini 1000 pages / 50MB at 258 tokens per page [C-24].

The two vendors that publish PDF best practices agree on the two rules that cost nothing:
document before prompt, and pages upright [C-21][C-26].

### 6. Schema constraints fix shape, not truth

OpenAI's Structured Outputs guarantees adherence to a supplied JSON Schema [C-27] and Anthropic's
constrains responses to a schema [C-28] — but both exclude keyword sets that matter for extraction.
Numeric and string constraints are unsupported on Anthropic, and on OpenAI fine-tuned models [C-27]
[C-28]. So range-checking must happen in application code, not in the schema.

Separately, key order is not cosmetic: a 2024 study found format restrictions produce "a
significant decline in LLMs' reasoning abilities", with 100% of one model's JSON-mode responses
placing the answer key before the reason key and thereby skipping chain-of-thought [C-47]. That
result predates current native structured-output implementations, so its magnitude is dated — but
ordering evidence keys before answer keys costs nothing and is retained as guidance.

### 7. Grounding must be mechanical, because confidence is not calibrated

Self-reported confidence is not usable as a gate: models "tend to verbalize overly high confidence
rather than signal uncertainty" when wrong, and remain "poorly calibrated to factual accuracy"
[C-34]. Citation *surface* quality is equally unreliable as a proxy — frontier models "maintain
link validity above 94% and relevance above 80%, yet achieve only 39–77% factual accuracy" [C-49] —
and a correct-looking citation may not even be the reason for the answer, with attributed answers
lacking citation faithfulness "up to 57 percent" of the time [C-48].

Anthropic's Citations returns real locators — 1-indexed page ranges for PDFs, 0-indexed character
ranges for plain text [C-29] — which is stronger than a model-written span field. Its limit shapes
the routing: scans without extractable text "are not citable" [C-30], so OCR must come first.

Consequence: the skill's gate is a string containment check in code, not a judgment call.

### 8. Tables are the failure point, and Markdown loses data

Table extraction is hard for a documented structural reason — "the wide variety of formats, styles,
and structures found in presented tables" [C-45] — and it is not solved. The most recent evaluation
finds that even top-scoring models show "misaligned spanning cells, altered values, incorrect
header-cell associations" on manual inspection, "confirming that accurate table extraction from
PDFs remains unsolved" [C-39].

For serialization the evidence is unambiguous: simplified Markdown table syntax cannot represent
complex financial and legal tables, so HTML is the correct target because it expresses rowspan,
colspan, and hierarchical headers [C-43]. Cross-page tables must be merged before serializing, or
repeated headers become phantom rows [C-43a].

### 9. Benchmark numbers do not transfer to your documents

Models near-perfect on one benchmark drop sharply on another: PP-StructureV3 86.7% → 60.3%,
GPT-4o 75% → 52%, PaddleOCR-VL 92.9% → 78.2% [C-44]. And the metric can mislead about the outcome:
"high OCR accuracy does not necessarily translate into strong downstream RAG performance" because
structural and semantic errors break retrieval even at low WER/CER [C-42]. DocVQA's authors chose
ANLS precisely because "no OCR is perfect" [C-46].

Consequence: evaluate on a sample of the target corpus, scored on the real task.

### 10. Documented failure modes worth testing for

Hallucination in VLM parsing [C-37]; multi-column merging on slides and financial reports [C-37];
invented text when a page image is ambiguous, and hallucination on blank pages the model never
trained on [C-50]; repetition loops at low sampling temperature, which olmOCR 2 mitigates with
dynamic temperature scaling from 0.1 up to 0.8 triggered by a missing EOS token [C-41].

---

## Disagreement / unresolved

**Do VLMs beat pipeline parsers?** Sources conflict, and the conflict is real.

| Source | Says | Scope |
|---|---|---|
| OmniDocBench, Dec 2024 [C-36] | VLMs "struggle with high-density documents like newspapers due to limitations in input resolution and token length"; pipeline tools maintain accuracy via layout segmentation | Full-page document parsing |
| Beyond String Matching, Mar 2026 [C-40] | "The top-performing systems are the Gemini 3 models, general-purpose multimodal models rather than dedicated OCR tools"; rule-based tools "lag substantially behind" | Table extraction only |
| NVIDIA [C-51][C-52] | Its OCR pipeline "outperformed the VLM across all visual modalities, with an overall delta of 7.2%", at "32.3x" throughput | Retrieval extraction at volume |

**Conflict type: task scope plus date.** These are not measuring the same thing. VLMs have closed
much of the gap on isolated table extraction since late 2024; pipelines retain the advantage on
dense full-page parsing at volume, where resolution ceilings, throughput, and cost dominate.
**Unresolved and left unresolved in the skill** — `references/routing.md` renders both and gives
per-document selection criteria rather than a winner.

**What would settle it**: a single benchmark scoring both families on the same documents, at the
same page volume, reporting accuracy *and* cost per thousand pages. None of the three sources does.

## Refutation results

Two load-bearing recommendations were sent to refutation subagents.

**"Send the PDF straight to the model as the default."** — **Refuted.** Evidence: NVIDIA's pipeline
beat a VLM by 7.2% with 32.3× throughput [C-51][C-52]; the same write-up documents VLM
hallucination and missed chart legends where "OCR-based methods excel" [C-53][C-54]; cost is
material — "converting a million pages using GPT-4o can cost over $6,200 USD" [C-55]; and
image-only prompting is "prone to models completing unfinished sentences, or to invent larger
texts when the image data was ambiguous" [C-50]. The skill therefore explicitly says *do not
default to Path C*.

**"Schema enforcement plus citation grounding eliminates hallucinated field values."** — **Refuted.**
Constrained decoding can itself degrade reasoning [C-47]; citation faithfulness fails up to 57% of
the time [C-48]; and link validity above 94% coexists with 39–77% factual accuracy [C-49]. The
skill therefore gates on a mechanical span-contains-value check rather than on schema validity or
the presence of a citation.

## What we could not establish

- **ISO 32000 itself was never opened.** The retriever hit 403s and unreadable spec PDFs. The
  format claims [C-01][C-02] rest on `pypdf`'s official documentation and W3C's WCAG technique
  instead — both authoritative for the behavior described, neither the normative spec. A T2 vendor
  page (PDFlib) covering the same ground was **discarded**, since T1 sources said it.
- **No Docling limitations statement was found.** Its docs surfaced capabilities but no
  known-limits section. Recorded as not-found in `references/routing.md` rather than inferred —
  absence of a stated limit is not evidence of none.
- **No head-to-head cost-and-accuracy benchmark** across VLM and pipeline families on identical
  documents. This is why the disagreement above stays unresolved.
- **No Japanese-language or CJK-specific extraction evidence** was retrieved. Every benchmark cited
  is predominantly English or Chinese. CJK vertical text, ruby annotations, and mixed-script
  documents are unaddressed by this research.
- **Two refuter sources were dropped**, not used: arXiv 2607.03325 and 2606.00898. Both exist and
  their titles match, but the returned spans carried editorial brackets and a re-derived table
  number rather than verbatim text, violating the span contract. Their claims are covered by
  cleanly-quoted sources [C-48][C-49].
- **One T3 source discarded**: a LlamaIndex explainer on why PDFs are hard, superseded by T1
  documentation saying the same thing. A second LlamaIndex post is registered [S-36] but carries
  only one non-load-bearing claim.

---

## Source Register

| ID | Source | URL | Tier | Accessed |
|---|---|---|---|---|
| S-01 | pypdf — Extract Text from a PDF | https://pypdf.readthedocs.io/en/stable/user/extract-text.html | T1 | 2026-08-01 |
| S-02 | W3C, WCAG 2.0 Technique PDF3 | https://www.w3.org/TR/WCAG20-TECHS/PDF3.html | T1 | 2026-08-01 |
| S-03 | pdfplumber README | https://github.com/jsvine/pdfplumber | T1 | 2026-08-01 |
| S-04 | PyMuPDF4LLM documentation | https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html | T1 | 2026-08-01 |
| S-05 | PyMuPDF — Text recipes | https://pymupdf.readthedocs.io/en/latest/recipes-text.html | T1 | 2026-08-01 |
| S-06 | pdftotext(1), poppler-utils | https://manpages.debian.org/testing/poppler-utils/pdftotext.1.en.html | T2 | 2026-08-01 |
| S-07 | Tesseract — Improving the quality of the output | https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html | T2 | 2026-08-01 |
| S-08 | OCRmyPDF Cookbook (17.8.1) | https://ocrmypdf.readthedocs.io/en/latest/cookbook.html | T2 | 2026-08-01 |
| S-09 | Docling README | https://github.com/docling-project/docling | T2 | 2026-08-01 |
| S-10 | Docling — Pipeline options | https://docling-project.github.io/docling/reference/pipeline_options/ | T2 | 2026-08-01 |
| S-11 | Marker README (datalab-to) | https://github.com/datalab-to/marker | T2 | 2026-08-01 |
| S-12 | MinerU README (opendatalab) | https://github.com/opendatalab/MinerU | T2 | 2026-08-01 |
| S-13 | Unstructured — Partitioning | https://docs.unstructured.io/open-source/core-functionality/partitioning | T2 | 2026-08-01 |
| S-14 | Anthropic — PDF support | https://platform.claude.com/docs/en/build-with-claude/pdf-support | T1 | 2026-08-01 |
| S-15 | OpenAI — File inputs | https://developers.openai.com/api/docs/guides/file-inputs | T1 | 2026-08-01 |
| S-16 | OpenAI — PDF files | https://developers.openai.com/api/docs/guides/pdf-files | T1 | 2026-08-01 |
| S-17 | Gemini API — Document understanding | https://ai.google.dev/gemini-api/docs/document-processing | T1 | 2026-08-01 |
| S-18 | OpenAI — Structured Outputs | https://developers.openai.com/api/docs/guides/structured-outputs | T1 | 2026-08-01 |
| S-19 | Anthropic — Structured outputs | https://platform.claude.com/docs/en/build-with-claude/structured-outputs | T1 | 2026-08-01 |
| S-20 | Anthropic — Citations | https://platform.claude.com/docs/en/build-with-claude/citations | T1 | 2026-08-01 |
| S-21 | Anthropic blog — Introducing Citations | https://claude.com/blog/introducing-citations-api | T2 | 2026-08-01 |
| S-22 | Gemini API — Grounding with Google Search | https://ai.google.dev/gemini-api/docs/google-search | T1 | 2026-08-01 |
| S-23 | Gemini API — Image understanding | https://ai.google.dev/gemini-api/docs/image-understanding | T1 | 2026-08-01 |
| S-24 | Wired for Overconfidence (arXiv:2604.01457) | https://arxiv.org/abs/2604.01457 | T1 | 2026-08-01 |
| S-25 | OmniDocBench (arXiv:2412.07626v2) | https://arxiv.org/abs/2412.07626 | T1 | 2026-08-01 |
| S-26 | Beyond String Matching (arXiv:2603.18652) | https://arxiv.org/abs/2603.18652 | T1 | 2026-08-01 |
| S-27 | olmOCR 2 (arXiv:2510.19817) | https://arxiv.org/abs/2510.19817 | T1 | 2026-08-01 |
| S-28 | When Good OCR Is Not Enough (arXiv:2605.00911v1) | https://arxiv.org/abs/2605.00911 | T1 | 2026-08-01 |
| S-29 | PubTables-1M (arXiv:2110.00061) | https://arxiv.org/abs/2110.00061 | T1 | 2026-08-01 |
| S-30 | DocVQA (arXiv:2007.00398) | https://arxiv.org/abs/2007.00398 | T1 | 2026-08-01 |
| S-31 | NVIDIA — Approaches to PDF Data Extraction for IR | https://developer.nvidia.com/blog/approaches-to-pdf-data-extraction-for-information-retrieval/ | T2 | 2026-08-01 |
| S-32 | olmOCR (arXiv:2502.18443) | https://arxiv.org/abs/2502.18443 | T1 | 2026-08-01 |
| S-33 | Let Me Speak Freely? (arXiv:2408.02442, EMNLP 2024) | https://arxiv.org/abs/2408.02442 | T1 | 2026-08-01 |
| S-34 | Correctness is not Faithfulness in RAG Attributions (arXiv:2412.18004) | https://arxiv.org/abs/2412.18004 | T1 | 2026-08-01 |
| S-35 | Cited but Not Verified (arXiv:2605.06635) | https://arxiv.org/abs/2605.06635 | T1 | 2026-08-01 |
| S-36 | LlamaIndex — OmniDocBench is Saturated | https://www.llamaindex.ai/blog/omnidocbench-is-saturated-what-s-next-for-ocr-benchmarks | T3 | 2026-08-01 |

All 13 arXiv IDs were independently re-resolved by the lead against `arxiv.org/abs/<id>`, and every
returned `citation_title` matched the title the retriever reported. Vendor numeric spans (Anthropic
page/size/token limits, Gemini page and token limits, Citations behavior, OpenAI schema limits) were
re-grepped by the lead against the live pages.

## Claim Ledger

`Supported` verdicts come from blind per-claim verifiers. Rows marked **narrowed** returned
`Partial` on a broader phrasing and were rewritten down to what the span literally says, per the
skill's protocol — verifiers were not re-run to obtain agreement.

| ID | Claim | Source | Kind | Status |
|---|---|---|---|---|
| C-01 | PDF text is absolutely positioned; every character can be positioned on the page | S-01 | verifiable | Supported (narrowed) |
| C-02 | PDF files don't contain a semantic layer | S-01 | verifiable | Supported |
| C-03 | Untagged PDFs may be read top-to-bottom across both columns, interpreted as one column | S-02 | verifiable | Supported (narrowed) |
| C-04 | A common PDF text-extraction issue is that text may not appear in any particular reading order | S-05 | verifiable | Supported (narrowed) |
| C-05 | pdfplumber groups characters into words by an `x_tolerance` horizontal-gap threshold | S-03 | verifiable | Supported (narrowed) |
| C-06 | pypdf is not OCR software and cannot extract text from images | S-01 | verifiable | Supported |
| C-07 | pymupdf4llm returns empty strings for pages with no selectable text | S-04 | verifiable | Supported (narrowed) |
| C-08 | `pdftotext -layout` preserves physical layout; the default undoes columns/hyphenation and outputs reading order | S-06 | verifiable | Supported |
| C-09 | Some scanned PDFs contain an image plus a background text layer | S-01 | verifiable | Supported (narrowed) |
| C-10 | Tesseract works best on images of at least 300 dpi | S-07 | verifiable | Supported |
| C-11 | Skew significantly reduces Tesseract line-segmentation quality and severely impacts OCR | S-07 | verifiable | Supported |
| C-12 | OCRmyPDF `--deskew` rotates skewed pages back into place | S-08 | verifiable | Supported (narrowed) |
| C-13 | OCRmyPDF `--oversample` resamples to higher resolution before OCR and can improve results | S-08 | verifiable | Supported |
| C-14 | Docling handles layout, reading order, table structure, code, formulas, image classification | S-09 | verifiable | Supported |
| C-15 | MinerU converts tables to HTML and formulas to LaTeX | S-12 | verifiable | Supported |
| C-16 | MinerU parsing may fall short on complex layouts, scanned pages, handwritten content | S-12 | verifiable | Supported (narrowed) |
| C-17 | Unstructured `hi_res` is more accurate but slower and needs detectron2_onnx; `ocr_only` is recommended for multi-column docs lacking extractable text | S-13 | verifiable | Supported |
| C-18 | Claude: max 600 pages/request (100 under 1M context), max request 32 MB | S-14 | verifiable | Supported |
| C-19 | Claude converts each page to an image and supplies extracted page text alongside it | S-14 | verifiable | Supported |
| C-20 | Claude PDFs cost 1,500–3,000 text tokens/page plus image token costs | S-14 | verifiable | Supported |
| C-21 | Anthropic recommends PDFs before text, upright pages, logical page numbers, splitting, prompt caching | S-14 | verifiable | Supported |
| C-22 | OpenAI extracts both text and page images from PDFs and sends both; this increases token usage | S-15 | verifiable | Supported |
| C-23 | OpenAI: each file under 50 MB, 50 MB combined per request | S-15 | verifiable | Supported |
| C-24 | Gemini supports PDFs up to 50MB or 1000 pages, inline or Files API; each page = 258 tokens | S-17 | verifiable | Supported |
| C-26 | Gemini recommends correct page orientation, avoiding blurry pages, prompt after the page | S-17 | verifiable | Supported |
| C-27 | OpenAI Structured Outputs guarantees JSON Schema adherence; composition keywords unsupported; string/number constraints additionally unsupported for fine-tuned models; strict+unsupported schema errors | S-18 | verifiable | Supported |
| C-28 | Anthropic structured outputs constrain to a schema; recursive schemas, numeric and string constraints unsupported | S-19 | verifiable | Supported |
| C-29 | Claude Citations returns 1-indexed page ranges for PDFs, 0-indexed char ranges for plain text, 0-indexed block ranges for custom content | S-20 | verifiable | Supported |
| C-30 | Claude Citations chunks PDF text into sentences; scans without extractable text are not citable | S-20 | verifiable | Supported |
| C-31 | Marker: very complex layouts with nested tables and forms may not work | S-11 | verifiable | Supported (narrowed) |
| C-32 | Docling exports Markdown, HTML, WebVTT, DocLang, DocTags and lossless JSON | S-09 | verifiable | Supported |
| C-33 | MinerU outputs JSON sorted by reading order, in human-readable order for single/multi-column and complex layouts | S-12 | verifiable | Supported |
| C-34 | LLMs verbalize overly high confidence when factually wrong; verbalized confidence is poorly calibrated to accuracy | S-24 | verifiable | Supported |
| C-35 | Gemini returns `box_2d` as [ymin, xmin, ymax, xmax] normalized 0–1000 | S-23 | verifiable | Supported |
| C-36 | VLMs struggle on high-density documents due to input resolution and token length; pipeline tools maintain accuracy via layout segmentation | S-25 | verifiable | Supported |
| C-37 | Some VLMs hallucinate from recognized content; InternVL2/Qwen2-VL merge multi-column text on slides and financial reports | S-25 | verifiable | Supported |
| C-39 | Even top-scoring models show spanning-cell misalignment, altered values, wrong header associations; table extraction remains unsolved | S-26 | verifiable | **Disputed** (see below) |
| C-40 | Top performers are general-purpose multimodal models, not dedicated OCR tools; rule-based tools lag learning-based ones | S-26 | verifiable | **Disputed** (see below) |
| C-41 | Low sampling temperature risks repetition loops; olmOCR 2 uses dynamic temperature scaling 0.1→0.8 on missing EOS | S-27 | verifiable | Supported |
| C-42 | High OCR accuracy does not necessarily translate into strong downstream RAG performance | S-28 | verifiable | Supported |
| C-43 | Markdown table syntax cannot represent complex financial/legal tables; HTML expresses rowspan, colspan, hierarchical headers | S-28 | verifiable | Supported |
| C-43a | Cross-page tables should have continuation text and repeated headers removed and be merged into one table | S-28 | verifiable | Supported |
| C-44 | OmniDocBench-strong models decline on InduOCRBench: 86.7→60.3, 75→52, 92.9→78.2 | S-28 | verifiable | Supported |
| C-45 | Table extraction is challenging for automated systems due to variety of formats, styles, structures | S-29 | verifiable | Supported |
| C-46 | DocVQA chose ANLS because no OCR is perfect, so minor OCR-driven mismatches are not severely penalized | S-30 | verifiable | Supported |
| C-47 | Format restrictions significantly decline LLM reasoning; 100% of one model's JSON-mode responses put answer before reason | S-33 | verifiable | Supported |
| C-48 | Attributed answers often lack citation faithfulness, up to 57 percent of citations | S-34 | verifiable | Supported |
| C-49 | Frontier models keep link validity >94% and relevance >80% yet reach only 39–77% factual accuracy | S-35 | verifiable | Supported |
| C-50 | Page-image-only prompting invites completing unfinished sentences and inventing text when ambiguous; blank pages unseen in training trigger hallucination | S-32, S-27 | verifiable | Supported |
| C-51 | NVIDIA's OCR pipeline outperformed the VLM across all visual modalities by 7.2% overall | S-31 | verifiable | Supported |
| C-52 | That pipeline showed 32.3x higher throughput and lower latency than the larger VLM | S-31 | verifiable | Supported |
| C-53 | VLM-generated descriptions contained fabricated details or unnecessary repeated phrases | S-31 | verifiable | Supported |
| C-54 | Chart annotations and legends were sometimes missed by the VLM, where OCR-based methods excel | S-31 | verifiable | Supported |
| C-55 | Converting a million pages with GPT-4o can cost over $6,200 USD | S-32 | verifiable | Supported |
| C-56 | High benchmark scores mask a long tail of document edge cases where the best models still fail | S-36 | interpretive | Supported |

**C-39 / C-40 are marked `Disputed`** not because their spans fail — both verified `Supported`
against S-26 — but because S-25 and S-31 report the opposite ordering on adjacent tasks. The
disagreement is rendered, attributed, and left unresolved above; it is not averaged.

## Inferences

These are the lead's reading of the evidence, not any source's statement.

| ID | Inference |
|---|---|
| I-01 | Triage belongs *before* tool selection, because the text-layer question forecloses whole branches at near-zero cost. No source prescribes a triage step; it follows from [C-06][C-07][C-09]. |
| I-02 | The VLM-vs-pipeline conflict is task-scoped rather than a factual dispute — table extraction vs full-page parsing at volume. The sources do not say this about each other. |
| I-03 | Hybrid routing (pipeline for transcription, VLM for interpretation over extracted regions) follows from [C-36][C-51][C-54] but is not recommended verbatim by any source. |
| I-04 | A mechanical span-contains-value assertion is the right gate, given that confidence [C-34], citation presence [C-48], and link validity [C-49] all fail as proxies. No source proposes this specific check. |
| I-05 | Column detection by per-band gutter analysis (as implemented in `triage_pdf.py`) is an engineering choice validated empirically on three documents here, not a method drawn from any cited source. |

## Coverage

- **Searched**: PDF format and structure; native extraction libraries (pypdf, pdfplumber, PyMuPDF/pymupdf4llm, poppler); OCR engines and preprocessing (Tesseract, OCRmyPDF); layout-aware parsers (Docling, Marker, MinerU, Unstructured); vendor PDF-input APIs (Anthropic, OpenAI, Google); structured output and citation mechanisms; document-parsing benchmarks (OmniDocBench, DocVQA, PubTables-1M, olmOCR-Bench, InduOCRBench); constrained-decoding and citation-faithfulness literature.
- **Not searched**: commercial document-AI services (AWS Textract, Azure Document Intelligence, Google Document AI, Mathpix as a product); PDF form-field (AcroForm/XFA) extraction; digital signatures and encrypted PDFs; PDF/A and accessibility remediation workflows; CJK-specific extraction.
- **Not found**: a Docling limitations statement; a cross-family cost-and-accuracy benchmark; the ISO 32000 spec text itself.
