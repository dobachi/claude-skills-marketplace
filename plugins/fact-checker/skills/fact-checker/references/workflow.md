# Fact-Checking Workflow Reference

## Table of Contents

1. [Claim Extraction](#claim-extraction)
2. [Claim Classification](#claim-classification)
3. [Verification Strategies](#verification-strategies)
4. [Evidence Evaluation](#evidence-evaluation)
5. [Verdict Scale](#verdict-scale)
6. [Verification Dimensions](#verification-dimensions)
7. [Report Template](#report-template)

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

| Tier | ABC | Source Type | Examples |
|---|---|---|---|
| 1 (Highest) | A | Primary/official sources | Government databases, peer-reviewed papers, official reports, legislation, standards documents |
| 2 | B | Established institutions | Major news outlets, WHO, World Bank, university research, industry official publications |
| 3 | C | Secondary sources | Wikipedia, reputable blogs, industry reports, media articles |
| 4 (Lowest) | — | Unverified sources | Social media, anonymous blogs, forums |

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

## Verification Dimensions

These seven dimensions provide a systematic framework for comprehensive fact-checking. They are used in **Structured Checklist Mode** (see SKILL.md) when the user requests thorough verification or provides a specific checklist.

### D-LINK: Link Validity

**Purpose**: Verify that all cited URLs are accessible and return valid content.

**Procedure**:
1. Collect all URLs referenced in the document
2. Use `batch_fetch.js` to check all URLs — the `httpStatus` field in `results.json` provides the HTTP status code
3. For single URLs, `fetch_page.js` outputs `HTTP Status: <code>` to stderr and writes `.meta.json`
4. Classify results:
   - 200: OK
   - 301/302: Redirect (check `finalUrl` for destination)
   - 403: Forbidden (access restricted)
   - 404: Not Found (broken link)
   - 0: Connection failure

**Output format**:

| URL | HTTP Status | Final URL | Assessment |
|-----|-------------|-----------|------------|
| ... | 200 | ... | OK |

### D-CONTENT: Source Content Matching

**Purpose**: Verify that each claim accurately reflects the content of its cited source.

**Procedure**:
1. For each claim with a citation, fetch the source content
2. Identify the specific fields/items being claimed (e.g., author name, finding, conclusion)
3. Compare each field against the actual source content
4. Flag misquotations, misinterpretations, or context omissions

**Output format**:

| Claim ID | Claimed Item | Source Says | Match? |
|----------|-------------|-------------|--------|
| C1 | "Author found X" | Author found Y | No — misinterpretation |

### D-GRANULARITY: Citation Granularity

**Purpose**: Check whether citations point to specific, relevant sections rather than generic top-level pages.

**Procedure**:
1. For each citation URL, check if it points to a specific page/section/anchor
2. Classify granularity:
   - **Specific**: URL points to exact section, paragraph, or data point (e.g., `page.html#section-3`)
   - **Page-level**: URL points to a relevant page but not a specific section
   - **Top-level**: URL points to a site homepage or generic landing page
3. Flag top-level citations as needing improvement

**Output format**:

| Claim ID | URL | Granularity | Note |
|----------|-----|-------------|------|
| C1 | .../report#findings | Specific | OK |
| C2 | .../homepage | Top-level | Should cite specific report page |

### D-NUMERIC: Numeric and Date Accuracy

**Purpose**: Verify exact accuracy of all numbers, dates, percentages, and monetary amounts.

**Procedure**:
1. Extract all numeric data points from claims (amounts, percentages, dates, quantities)
2. Locate the corresponding values in the cited source
3. Check for exact match — partial matches or approximations must be flagged
4. Common errors to check: wrong unit, outdated figure, rounding discrepancy, wrong time period

**Output format**:

| Claim ID | Claimed Value | Source Value | Match? | Note |
|----------|--------------|-------------|--------|------|
| C1 | "$4.2 billion" | "$4.2 billion (2023)" | Yes | Year confirmed |
| C2 | "35%" | "34.7%" | Partial | Rounded up |

### D-FACTSPEC: Fact vs. Speculation Distinction

**Purpose**: Identify whether factual claims contain unstated speculation, opinion, or hedging that should be made explicit.

**Procedure**:
1. For each claim, analyze the rhetorical structure
2. Check for speculative language mixed with factual assertions (e.g., "X is likely...", "This suggests...", "probably")
3. Verify that factual statements are presented as facts and speculative statements are clearly marked as such
4. Flag cases where speculation is presented as established fact

**Output format**:

| Claim ID | Classification | Indicators | Issue |
|----------|---------------|------------|-------|
| C1 | Fact | Direct assertion with citation | None |
| C2 | Mixed | "likely" + uncited assertion | Speculation presented as fact |

### D-RELIABILITY: Source Reliability Level

**Purpose**: Classify each cited source by reliability tier and ABC level.

**Procedure**:
1. For each unique source, determine the source type (government, academic, media, blog, etc.)
2. Assign a Tier (1-4) and ABC classification per the Source Reliability Tiers table
3. Flag claims that rely solely on Tier 4 / unclassified sources

**Output format**:

| Source | Type | Tier | ABC | Note |
|--------|------|------|-----|------|
| WHO report | International organization | 2 | B | Authoritative |
| Personal blog | Anonymous | 4 | — | Needs corroboration |

### D-CONSISTENCY: Cross-Section Consistency

**Purpose**: Detect contradictions or inconsistencies between different sections of the same document.

**Procedure**:
1. Map each claim to the section it belongs to
2. Identify claims that reference the same entities, facts, or data across sections
3. Compare these cross-references for consistency (same numbers, same conclusions, no contradictions)
4. Flag any discrepancies

**Output format**:

| Section A | Section B | Topic | Discrepancy |
|-----------|-----------|-------|-------------|
| Introduction | Results | Market size | "$4.2B" vs "$4.5B" |

---

### Structured Checklist Mode: Report Extension

When using Structured Checklist Mode, append the following sections to the standard report:

#### Link Validity Summary (D-LINK)

Table of all URLs with HTTP status and assessment.

#### Source Content Matching (D-CONTENT)

Table of field-by-field comparisons between claims and sources.

#### Citation Granularity (D-GRANULARITY)

Table classifying each citation's specificity level.

#### Numeric Accuracy (D-NUMERIC)

Table of all numeric values with source comparison.

#### Fact/Speculation Distinction (D-FACTSPEC)

Table classifying each claim as fact, speculation, or mixed.

#### Source Reliability (D-RELIABILITY)

Table of all sources with Tier and ABC classifications.

#### Cross-Section Consistency (D-CONSISTENCY)

Table of any detected cross-section contradictions.

#### Verification Completeness Checklist

```
- [ ] D-LINK: All URLs checked for accessibility
- [ ] D-CONTENT: All cited claims compared against source content
- [ ] D-GRANULARITY: Citation specificity reviewed
- [ ] D-NUMERIC: All numeric values verified against sources
- [ ] D-FACTSPEC: Fact vs. speculation analysis completed
- [ ] D-RELIABILITY: All sources classified by reliability tier
- [ ] D-CONSISTENCY: Cross-section consistency verified
```

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
