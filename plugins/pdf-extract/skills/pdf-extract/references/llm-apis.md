# Vendor PDF Input Specs

**All figures verified 2026-08-01 against the official documentation linked below.** These change without notice — re-check before relying on a number, and update the access date when you do.

## Limits and costs

| | Anthropic Claude | OpenAI | Google Gemini |
|---|---|---|---|
| Max pages / request | 600 (100 when the request's context window is under 1M tokens) | not stated as a page count | 1000 |
| Max size | 32 MB request (varies by platform) | 50 MB per file, 50 MB combined per request | 50 MB |
| Text tokens | 1,500–3,000 per page, depending on content density | not published per page | — |
| Page tokens | image tokens additionally, per the vision cost calculation | text + page images both in context, "which can increase token usage" | 258 tokens per document page |
| Format | "Standard PDF (no passwords/encryption)" | base64, Files API `file_id`, or external URL | inline data or Files API |

Sources: [Anthropic PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support) · [OpenAI file inputs](https://developers.openai.com/api/docs/guides/file-inputs) · [OpenAI PDF files](https://developers.openai.com/api/docs/guides/pdf-files) · [Gemini document understanding](https://ai.google.dev/gemini-api/docs/document-processing)

## How each vendor actually reads the PDF

All three send **both** text and page images. This matters: you are paying for both, and the model can cross-check them.

- **Anthropic** — "The system converts each page of the document into an image. The text from each page is extracted and provided alongside each page's image." "Documents are provided as a combination of text and images for analysis. This allows users to ask for insights on visual elements of a PDF, such as charts, diagrams, and other non-textual content." Because it runs on the vision path, it inherits the same limitations as other vision tasks.
- **OpenAI** — "the API extracts both text and page images and sends both to the model." Note the contrast the docs draw: "For non-PDF files, the API doesn't extract embedded images or charts into the model context." Page-image detail is tunable — set `detail` to `auto` (default), `low`, or `high` — but "Chat Completions file inputs don't support `detail`", so that control requires the Responses API.
- **Gemini** — "Gemini models can process documents in PDF format, using native vision to understand entire document contexts." The 50MB/1000-page limit "applies to both inline data and Files API uploads." Multiple documents are allowed in one request "as long as the combined size of the documents and the text prompt stays within the model's context window."

## Documented best practices

**Anthropic** lists these verbatim:

- Place PDFs before text in your requests
- Use standard fonts
- Ensure text is clear and legible
- Rotate pages to proper upright orientation
- Use logical page numbers (from PDF viewer) in prompts
- Split large PDFs into chunks when needed
- Enable prompt caching for repeated analysis

Also documented: cache PDFs with prompt caching "to improve performance on repeated queries", and use the Message Batches API "to process many PDFs in one request".

**Google** lists: "Rotate pages to the correct orientation before uploading, Avoid blurry pages, and If using a single page, place the text prompt after the page."

**OpenAI** on scale: "For large document retrieval, use File Search for retrieval over large files instead of passing them directly as `input_file`."

The two vendor guidances agree on the two rules that matter most and cost nothing to follow: **document before prompt**, and **pages upright**.

## Cost sanity check

Direct VLM extraction is priced per page and adds up fast at volume. The olmOCR paper puts one reference point on it: "converting a million pages using GPT-4o can cost over $6,200 USD" (arXiv:2502.18443). Run the arithmetic for your page count before committing to Path C for a corpus.

## Citations

**Anthropic Citations** ([docs](https://platform.claude.com/docs/en/build-with-claude/citations)) is the only mechanism among the three that returns source locations natively for PDFs rather than model-written ones:

- "Ground Claude's responses in your source documents. Citations return the exact passages that support each claim, so you can verify answers and surface sources to your users."
- Location format varies by document type: "For PDFs: Citations include the page number range (1-indexed). For plain text documents: Citations include the character index range (0-indexed). For custom content documents: Citations include the content block index range (0-indexed)."
- **Hard limit for scans**: "PDF text is extracted and chunked into sentences. As image citations are not yet supported, PDFs that are scans of documents and do not contain extractable text are not citable." So a scan must go through OCR first, then be supplied as text, before it can be cited.

**Google** returns citation metadata for search grounding — "Each `url_citation` annotation links a text segment (defined by `start_index` and `end_index`) to a source URL" — and, for visual extraction, bounding boxes: "Each item has a bounding box (`box_2d`) in the format [ymin, xmin, ymax, xmax] with normalized coordinates between 0 and 1000."

Anthropic's vendor claim on effectiveness, to weigh as a vendor claim: "Our internal evaluations show that Claude's built-in citation capabilities outperform most custom implementations, increasing recall accuracy by up to 15%."
