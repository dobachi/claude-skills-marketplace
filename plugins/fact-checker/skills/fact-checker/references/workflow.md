# Fact-Checking Workflow Reference

## Table of Contents

1. [Claim Extraction](#claim-extraction)
2. [Claim Classification](#claim-classification)
3. [Verification Strategies](#verification-strategies)
4. [Evidence Evaluation](#evidence-evaluation)
5. [Verdict Scale](#verdict-scale)
6. [Report Template](#report-template)

---

## Claim Extraction

### What Constitutes a Checkable Claim

Extract statements that are **falsifiable** — statements that can be objectively verified or refuted with evidence. Focus on:

- **Factual assertions**: Statistics, dates, named events, scientific findings
- **Quoted statements**: Claims attributed to a person or organization
- **Citations**: References to papers, articles, reports, laws, or data sources
- **Causal claims**: "X causes Y" or "X led to Y"
- **Comparative claims**: "X is larger/faster/more effective than Y"

### What to Skip

- Opinions or subjective judgments ("This is the best approach")
- Vague or unfalsifiable statements ("Many experts believe...")
- Definitions or tautologies
- Future predictions without a verifiable basis

### Extraction Pattern

For each claim, record:

```
- claim_id: Unique identifier (e.g., "C1", "C2")
- text: The exact text of the claim
- source_context: Surrounding paragraph for context
- type: factual | citation | statistic | quote | causal | comparative
- cited_source: URL or reference string, if any
- priority: high | medium | low (based on importance to document's argument)
```

Prioritize claims that are central to the document's conclusions. Low-priority claims (background context, widely known facts) can be skipped or batch-verified.

---

## Claim Classification

### By Verification Method

| Claim Type | Primary Method | Fallback Method |
|---|---|---|
| Citation with URL | Fetch URL, compare content | Web search for cached/archived version |
| Citation (paper/book) | Search scholarly databases | Web search for summaries/reviews |
| Statistic | Search authoritative data sources | Cross-reference multiple sources |
| Named event/date | Web search, Wikipedia | Multiple news sources |
| Quote attribution | Search for original source | News archives |
| Causal/comparative | Search for supporting studies | Expert consensus sources |

### Priority Assignment

- **High**: Central to the document's argument or conclusion; if wrong, undermines the document
- **Medium**: Supporting evidence; errors would weaken but not invalidate the argument
- **Low**: Background context, tangential facts, widely-known information

---

## Verification Strategies

### Strategy 1: Direct URL Verification

When a claim cites a specific URL:

1. Fetch the URL using `fetch_page.js` (PDF + text)
2. Search the extracted text for the specific claim
3. Compare the claim against the actual source content
4. Note any misquotation, misinterpretation, or context omission

### Strategy 2: Web Search Verification

When no URL is given, or the URL is inaccessible:

1. Formulate 2-3 search queries from the claim's key terms
2. Use WebSearch or web search tools to find corroborating/contradicting sources
3. Prefer authoritative sources: government sites, academic institutions, established news outlets
4. Cross-reference at least 2 independent sources for important claims

### Strategy 3: Scholarly Verification

For academic citations (papers, journal articles):

1. Search by DOI, paper title, or author names
2. Check Google Scholar, PubMed, or relevant databases
3. Verify: correct authors, year, journal, and that the paper says what is claimed
4. Note if the paper has been retracted or corrected

### Strategy 4: Data/Statistic Verification

For numerical claims and statistics:

1. Identify the claimed data source (e.g., "according to WHO...")
2. Fetch the actual data source
3. Verify the exact numbers, time period, and methodology
4. Check for common errors: outdated data, wrong unit, cherry-picked timeframe

---

## Evidence Evaluation

### Source Reliability Tiers

| Tier | Source Type | Examples |
|---|---|---|
| 1 (Highest) | Primary/official sources | Government databases, peer-reviewed papers, official reports |
| 2 | Established institutions | Major news outlets, WHO, World Bank, university research |
| 3 | Secondary sources | Wikipedia, reputable blogs, industry reports |
| 4 (Lowest) | Unverified sources | Social media, anonymous blogs, forums |

### Red Flags

- Source URL returns 404 or has been removed
- Cited paper does not exist or has different authors
- Statistics don't match the cited source's actual data
- Quote is taken out of context or selectively edited
- Claim extrapolates beyond what the source actually says

---

## Verdict Scale

Each claim receives one of these verdicts:

| Verdict | Icon | Meaning |
|---|---|---|
| **Verified** | :white_check_mark: | Claim is accurate and well-supported by the cited source |
| **Mostly Accurate** | :large_blue_circle: | Claim is substantially correct but contains minor inaccuracies |
| **Unverifiable** | :yellow_circle: | Insufficient evidence to confirm or deny; source inaccessible |
| **Misleading** | :orange_circle: | Claim is technically true but missing important context |
| **Inaccurate** | :red_circle: | Claim contradicts the available evidence |
| **Fabricated Source** | :no_entry: | Cited source does not exist or does not contain the claimed information |

---

## Report Template

```markdown
# Fact-Check Report

**Document**: [filename or title]
**Date**: [check date]
**Claims checked**: [N]

## Summary

[Brief overall assessment: X verified, Y issues found, Z unverifiable]

### Verdict Distribution

| Verdict | Count |
|---|---|
| Verified | N |
| Mostly Accurate | N |
| Unverifiable | N |
| Misleading | N |
| Inaccurate | N |
| Fabricated Source | N |

## Detailed Findings

### [C1] [Short description]

- **Claim**: "[exact text from document]"
- **Cited Source**: [URL or reference]
- **Verdict**: [verdict with icon]
- **Evidence**: [What was found]
- **Details**: [Explanation of verification process and findings]

### [C2] [Short description]

...

## Methodology

This report was generated using automated fact-checking:
- Claims were extracted and classified by type and priority
- URLs were fetched using a headless browser (Puppeteer) for content analysis
- Web searches were conducted to cross-reference claims
- Each claim was evaluated against available evidence

## Sources Consulted

- [List of URLs and sources that were actually accessed during verification]
```
