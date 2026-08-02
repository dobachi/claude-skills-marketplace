# Structured Extraction Contract

How to get fields out of a PDF in a form you can audit. Verified against vendor docs 2026-08-01.

## The field shape

Every extracted field carries its own evidence:

```json
{
  "invoice_total": {
    "reasoning": "Found in the summary block at the bottom of page 3, labelled 合計.",
    "value": "1234567",
    "currency": "JPY",
    "page": 3,
    "span": "合計　¥1,234,567",
    "found": true
  }
}
```

Four properties make this auditable:

- **`span` is verbatim source text**, in the source language, long enough to stand alone. A span that only proves the topic appeared on the page does not support the value.
- **`page` is the logical page number** a reader sees, not a zero-based array index.
- **`found` is explicit.** The model must be able to say no. Without a reachable "not present" answer, missing fields get manufactured.
- **`reasoning` precedes `value`** in key order — see below.

## Key ordering is not cosmetic

Structured output is generated in schema key order, so a schema that puts `value` first forces the model to commit to an answer before it reasons. This was measured: in "Let Me Speak Freely?" (arXiv:2408.02442, EMNLP 2024), "100% of GPT 3.5 Turbo JSON-mode responses placed the 'answer' key before the 'reason' key, resulting in zero-shot direct answering instead of zero-shot chain-of-thought reasoning." The same paper reports "a significant decline in LLMs' reasoning abilities under format restrictions" and that "stricter format constraints generally lead to greater performance degradation in reasoning tasks."

That study is from 2024 and predates current native structured-output implementations, so treat the magnitude as dated. The mitigation costs nothing and still applies: **put reasoning/evidence keys before answer keys.**

## Schema support differs by vendor

Write the schema against the stricter target if you may switch vendors.

**OpenAI Structured Outputs** — "a feature that ensures the model will always generate responses that adhere to your supplied JSON Schema." Supported types: "String, Number, Boolean, Integer, Object, Array, Enum, anyOf".

- Not yet supported: `allOf`, `not`, `dependentRequired`, `dependentSchemas`, `if`, `then`, `else`.
- Additionally unsupported **for fine-tuned models**: `minLength`, `maxLength`, `pattern`, `format`, `minimum`, `maximum`, `multipleOf`, `patternProperties`, `minItems`, `maxItems`.
- "If you turn on Structured Outputs by supplying `strict: true` and call the API with an unsupported JSON Schema, you will receive an error."

**Anthropic structured outputs** — "constrain Claude's responses to follow a specific schema, ensuring valid, parseable output for downstream processing." Not supported: "Recursive schemas, Complex types within enums, External `$ref`…, Numerical constraints (such as minimum, maximum, multipleOf), String constraints (minLength, maxLength), Array constraints beyond minItems of 0 or 1, additionalProperties set to anything other than false".

**Practical consequence**: numeric and string constraints are unavailable on Anthropic and unavailable on OpenAI fine-tuned models. Do not rely on the schema to range-check a value — validate it in your own code after parsing.

## Prefer a native citation mechanism

A model-written `span` field can itself be wrong. A native citation API returns real offsets computed from the document.

Anthropic Citations returns "the exact passages that support each claim", with "the page number range (1-indexed)" for PDFs. Its limit matters for this skill's routing: "PDF text is extracted and chunked into sentences. As image citations are not yet supported, PDFs that are scans of documents and do not contain extractable text are not citable." **OCR the scan first, then supply the text**, if you want real citations on a scanned document.

## Why the gate cannot be a confidence score

Three independent findings, all pointing the same way:

- Self-reported confidence is not calibrated: "Large language models are often not just wrong, but confidently wrong: when they produce factually incorrect answers, they tend to verbalize overly high confidence rather than signal uncertainty", and "their verbalized confidence remains poorly calibrated to factual accuracy" (arXiv:2604.01457).
- Well-formed citations coexist with wrong content: "even the strongest frontier models maintain link validity above 94% and relevance above 80%, yet achieve only 39–77% factual accuracy" (arXiv:2605.06635).
- A correct-looking citation may not be the reason for the answer: "current attributed answers often lack citation faithfulness (up to 57 percent of the citations)" (arXiv:2412.18004).

So the gate is mechanical, not judgmental: **does the span string actually contain the value?** Check it in code.

```python
for name, f in fields.items():
    if not f["found"]:
        continue
    assert f["span"] in page_text[f["page"]], f"{name}: span not on page {f['page']}"
    assert normalize(f["value"]) in normalize(f["span"]), f"{name}: value not in its own span"
```

That check catches the failure that reads best: a plausible value with a plausible-looking citation attached to it.

## Tables

Serialize as **HTML**, never as Markdown, whenever cells merge or headers nest. The reasoning is stated directly in arXiv:2605.00911: "We reject simplified Markdown table syntax due to its inability to represent complex financial and legal tables. Instead, we standardize on HTML format. This allows us to precisely describe complex table structures, including cell merging (rowspan, colspan), text alignment, and hierarchical header relationships."

Merge cross-page tables before serializing. Same source: "For tables spanning multiple pages, if the original document contains 'Table continued' or similar indicators, we remove the redundant continuation text and header repetition, merging the data into a single, coherent HTML table object." Skipping this turns repeated headers into phantom data rows.

After serializing, reconcile: row count, column count, and any total that the table itself states. Merged-cell errors are the most common table failure and arithmetic is the cheapest detector.

## Extraction checklist

- [ ] Schema written against the stricter vendor's supported keyword set
- [ ] Reasoning/evidence keys ordered before answer keys
- [ ] Every field has `page`, `span`, and an explicit `found`
- [ ] "Not present" is reachable and used
- [ ] Span-contains-value asserted in code, not by inspection
- [ ] Numeric ranges validated after parsing, not via schema constraints
- [ ] Tables in HTML; cross-page tables merged; totals reconcile
- [ ] Blank/unreadable pages produce empty output, asserted
- [ ] Native citations used where the document has extractable text
