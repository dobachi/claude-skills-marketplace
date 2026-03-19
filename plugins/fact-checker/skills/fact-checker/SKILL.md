---
name: fact-checker
description: Automated fact-checking for AI-generated documents. Extracts verifiable claims and citations from text or files (Markdown, PDF, DOCX), verifies each claim via web search and headless-browser source retrieval (Puppeteer), runs verification tasks in parallel, and generates a comprehensive Markdown fact-check report. Use when a user wants to verify the accuracy of AI-generated content, check cited references, validate statistics or quotes, or audit a research report for factual correctness. Triggers on requests like "fact-check this document", "verify these claims", "check if the references are real", or "audit this report for accuracy".
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Fact Checker

Automated, parallel fact-checking for AI-generated documents. Extract claims, verify them against real sources (via web search and headless browser), and produce a structured Markdown report.

## Workflow Overview

```
1. Ingest document   (read text/file, normalize to plain text)
2. Extract claims    (identify checkable assertions and citations)
3. Verify claims     (parallel: web search + headless browser fetch)
4. Evaluate evidence (score each claim)
5. Generate report   (Markdown fact-check report)
```

## Verification Modes

### Standard Mode (Default)

The 5-phase workflow below. Use this when the user asks for a general fact-check or claim verification.

### Structured Checklist Mode

Activated when:
- The user provides a specific checklist of items to verify
- The user requests "comprehensive verification", "thorough audit", or "structured fact-check"
- The user mentions specific verification dimensions (e.g., "check link validity", "verify all numbers")

In this mode, apply the 7 verification dimensions defined in [references/workflow.md](references/workflow.md):

| Dimension | Code | What it checks |
|-----------|------|---------------|
| Link Validity | D-LINK | HTTP status of all cited URLs |
| Source Content Matching | D-CONTENT | Field-by-field comparison of claims vs. source |
| Citation Granularity | D-GRANULARITY | Whether citations point to specific sections |
| Numeric Accuracy | D-NUMERIC | Exact match of numbers, dates, amounts |
| Fact/Speculation Distinction | D-FACTSPEC | Whether speculation is mixed with facts |
| Source Reliability | D-RELIABILITY | Tier (1-4) and ABC classification of sources |
| Cross-Section Consistency | D-CONSISTENCY | Contradictions between document sections |

The standard 5-phase workflow still applies, but each phase is augmented with dimension-specific steps as described below.

## Phase 1: Ingest Document

Determine input type and extract text:

**Markdown / plain text in conversation** -> Use directly.
**File path provided** -> Read the file. For PDFs, use the Read tool (supports PDF). For DOCX, use python-docx or similar extraction.

## Phase 2: Extract Claims

Scan the document for verifiable claims. See [references/workflow.md](references/workflow.md) for detailed extraction criteria, claim types, and priority assignment.

For each claim, record: claim ID, exact text, type (factual / citation / statistic / quote / causal / comparative), cited source (if any), and priority (high / medium / low).

Focus on high-priority claims first. Skip subjective opinions and unfalsifiable statements.

### Structured Checklist Mode: Additional Extraction

When in Structured Checklist Mode, also extract:
- **All URLs and references** — a complete list for D-LINK batch checking
- **All numeric data with source mapping** — every number, date, percentage, and amount paired with its cited source (for D-NUMERIC)
- **Section membership** — which section each claim belongs to (for D-CONSISTENCY cross-referencing)

## Phase 3: Verify Claims (Parallel Execution)

Run verification for all claims concurrently using the Task tool with background agents. This allows the user to step away while verification proceeds.

### For each claim, choose the best strategy:

**Claim cites a URL:**
1. Fetch the URL with the Puppeteer script to get PDF + text:
   ```bash
   node <skill-path>/scripts/fetch_page.js <url> --pdf <outdir>/<id>.pdf --text <outdir>/<id>.txt
   ```
2. Read the extracted text and check whether the source actually supports the claim.
3. If the URL is inaccessible (404, paywall, bot-blocked), fall back to web search.

**Claim cites a paper/book (no URL):**
1. Web search for the paper title + authors.
2. Attempt to locate and fetch the source.
3. Verify the claim matches what the source actually says.

**Claim is a statistic or factual assertion (no citation):**
1. Formulate 2-3 search queries from the claim's key terms.
2. Use WebSearch to find corroborating or contradicting evidence.
3. Prefer authoritative sources (Tier 1-2 per workflow.md).

### Batch fetching multiple URLs

When many URLs need fetching, create a manifest JSON and use batch_fetch.js:

```bash
# Create manifest
cat > /tmp/fc-manifest.json << 'MANIFEST'
{
  "urls": [
    { "url": "https://example.com/article1", "id": "C1" },
    { "url": "https://example.com/article2", "id": "C2" }
  ]
}
MANIFEST

# Fetch all in parallel
node <skill-path>/scripts/batch_fetch.js /tmp/fc-manifest.json --outdir /tmp/fact-check-output --concurrency 4
```

The script produces `results.json` in the output directory with per-URL status, plus `.pdf` and `.txt` files for each successfully fetched page.

### Parallel agent pattern

Launch one background Task agent per claim (or per batch of related claims):

```
For each claim or batch:
  -> Task agent (background): verify claim using web search + fetch_page.js
  -> Collect result when done
```

Aggregate all results before proceeding to report generation.

### Structured Checklist Mode: Dimension-Specific Verification

When in Structured Checklist Mode, perform these additional verification steps after the standard claim verification:

**D-LINK — Link Validity Check**:
1. Create a manifest of all URLs from the document
2. Run `batch_fetch.js` to check all URLs in parallel
3. Read `results.json` and build an HTTP status table from the `httpStatus` field
4. Flag any non-200 responses (404 = broken, 403 = restricted, 0 = unreachable)

**D-CONTENT — Source Content Matching**:
1. For each claim with a citation, identify the specific items being asserted
2. Fetch the source and locate the relevant passage
3. Compare field-by-field: author names, findings, conclusions, data points
4. Record match/mismatch for each field

**D-GRANULARITY — Citation Granularity**:
1. For each URL, check if it includes anchors, section paths, or specific page references
2. Classify as Specific / Page-level / Top-level
3. Flag top-level citations that should point to more specific content

**D-NUMERIC — Numeric Accuracy**:
1. Extract every number, date, percentage, and monetary amount from claims
2. Locate the corresponding value in the cited source
3. Check for exact match — flag rounding, unit errors, or outdated figures

**D-FACTSPEC — Fact vs. Speculation Distinction**:
1. Analyze the rhetorical structure of each claim (LLM text analysis, no external fetch needed)
2. Look for hedging language ("likely", "suggests", "probably", "may") mixed with factual assertions
3. Classify each claim as Fact / Speculation / Mixed
4. Flag cases where speculation is presented as established fact

**D-RELIABILITY — Source Reliability Classification**:
1. For each unique source, determine the organization type
2. Assign Tier (1-4) and ABC classification per workflow.md's Source Reliability Tiers table
3. Flag claims relying solely on Tier 4 / unclassified sources

**D-CONSISTENCY — Cross-Section Consistency**:
1. Group claims by section
2. Identify overlapping topics across sections (same entities, same data points)
3. Compare cross-referenced values for consistency
4. Flag any contradictions (different numbers, conflicting conclusions)

## Phase 4: Evaluate Evidence

For each claim, assign a verdict based on the evidence found. See [references/workflow.md](references/workflow.md) for the full verdict scale:

- :white_check_mark: **Verified** — Accurate and well-supported
- :large_blue_circle: **Mostly Accurate** — Substantially correct, minor issues
- :yellow_circle: **Unverifiable** — Insufficient evidence
- :orange_circle: **Misleading** — Technically true but missing context
- :red_circle: **Inaccurate** — Contradicts evidence
- :no_entry: **Fabricated Source** — Cited source doesn't exist or doesn't say what is claimed

## Phase 5: Generate Report

Produce a Markdown report following the template in [references/workflow.md](references/workflow.md). The report includes:

1. **Summary** with verdict distribution table
2. **Detailed findings** for each claim (claim text, source, verdict, evidence, explanation)
3. **Methodology** section
4. **Sources consulted** (all URLs actually accessed)

Save the report to the working directory as `fact-check-report.md`.

### Structured Checklist Mode: Additional Report Sections

When in Structured Checklist Mode, append these sections after the standard report content:

1. **Link Validity Summary (D-LINK)** — Table of all URLs with HTTP status, final URL, and assessment
2. **Source Content Matching (D-CONTENT)** — Table of field-by-field comparisons between claims and their sources
3. **Citation Granularity (D-GRANULARITY)** — Table classifying each citation as Specific / Page-level / Top-level
4. **Numeric Accuracy (D-NUMERIC)** — Table of all numeric values with claimed vs. source comparison
5. **Fact/Speculation Distinction (D-FACTSPEC)** — Table classifying each claim as Fact / Speculation / Mixed
6. **Source Reliability (D-RELIABILITY)** — Table of all sources with Tier (1-4) and ABC classifications
7. **Cross-Section Consistency (D-CONSISTENCY)** — Table of detected cross-section contradictions
8. **Verification Completeness Checklist** — Checklist confirming all 7 dimensions were checked

See [references/workflow.md](references/workflow.md) for the detailed output format of each dimension table.

## Scripts Reference

| Script | Purpose | Key Options |
|---|---|---|
| `scripts/fetch_page.js` | Fetch single URL via Puppeteer | `--pdf`, `--text`, `--screenshot`, `--timeout`, `--wait` |
| `scripts/batch_fetch.js` | Fetch multiple URLs in parallel | `--outdir`, `--concurrency`, `--pdf`, `--text`, `--screenshot` |

Both scripts use headless Chromium with a realistic user-agent to handle sites that block simple HTTP requests.

**Prerequisites**: Node.js and Puppeteer must be installed. Install with:
```bash
npm install puppeteer
```

## Important Notes

- Always replace `<skill-path>` with the actual path to this skill's directory when running scripts.
- Fetched PDFs and text are saved to a temporary output directory. Clean up after report generation if desired.
- For large documents with many claims, prioritize high-priority claims and offer the user a choice on how many to verify.
- When a source is behind a paywall or login wall, note it as "Unverifiable (access restricted)" rather than marking it inaccurate.
