---
name: fact-checker
description: Automated fact-checking for AI-generated documents. Extracts verifiable claims and citations from text or files (Markdown, PDF, DOCX), verifies each claim via web search and headless-browser source retrieval (Puppeteer), runs verification tasks in parallel, and generates a comprehensive Markdown fact-check report. Use when a user wants to verify the accuracy of AI-generated content, check cited references, validate statistics or quotes, or audit a research report for factual correctness. Triggers on requests like "fact-check this document", "verify these claims", "check if the references are real", or "audit this report for accuracy".
---

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

## Phase 1: Ingest Document

Determine input type and extract text:

**Markdown / plain text in conversation** -> Use directly.
**File path provided** -> Read the file. For PDFs, use the Read tool (supports PDF). For DOCX, use python-docx or similar extraction.

## Phase 2: Extract Claims

Scan the document for verifiable claims. See [references/workflow.md](references/workflow.md) for detailed extraction criteria, claim types, and priority assignment.

For each claim, record: claim ID, exact text, type (factual / citation / statistic / quote / causal / comparative), cited source (if any), and priority (high / medium / low).

Focus on high-priority claims first. Skip subjective opinions and unfalsifiable statements.

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
