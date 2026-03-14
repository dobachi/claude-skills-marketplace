---
name: verify-content
description: Integrated skill for fact-checking and reference verification. Identifies claims, verifies with external sources, and organizes references. Use for document reviews, article proofreading, report verification, and academic paper checks.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Content Verification Skill

Provides an integrated workflow to ensure the reliability of written content.

## Workflow Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Step 1     │    │  Step 2     │    │  Step 3     │
│  Identify   │ →  │  Verify     │ →  │  Reference  │
│  (scan)     │    │  (verify)   │    │  (reference)│
└─────────────┘    └─────────────┘    └─────────────┘
```

## Quick Start

### Run the full flow

```
User: Verify the content of this document
```

### Run a specific step only

```
User: Identify sections that need verification in this article
User: Fact-check this numerical data
User: Organize the reference list
```

## Step 1: Identify (scan)

Analyze the entire text and identify sections that require verification.

### Check Perspectives

| Category | Examples |
|----------|----------|
| Factual statements | Historical facts, scientific facts, regulations/laws |
| Quantitative claims | Numbers, statistics, dates, rankings |
| Definitive expressions | "always", "the only", "the largest" |
| Citations/references | Quotes from people, citations from literature |
| Comparisons/evaluations | "better than", "generally" |

### Output Format

```markdown
## Sections to Verify

### Priority: High
| # | Section | Type | Verification Needed |
|---|---------|------|---------------------|
| 1 | "..." | Numerical | Confirm source |
```

## Step 2: Verify

Fact-check identified sections against external sources.

### Verification Process

1. **Identify sources**: Collect candidates via web search
2. **Retrieve actual content**: Verify with WebFetch or curl
3. **Evaluate**: Check consistency, accuracy, context, and recency

### Important: Do not blindly trust AI search results

```bash
# If WebFetch is blocked
curl -s -L "https://example.com/page" | head -200

# Check past versions on Wayback Machine
curl -s "https://archive.org/wayback/available?url=example.com/page"
```

### Evaluation Criteria

| Verdict | Condition |
|---------|-----------|
| Accurate | Confirmed by reliable source, content matches |
| Needs Correction | Mostly accurate but details need fixing |
| Incorrect | Contradicts facts, could cause serious misunderstanding |
| Unverifiable | No reliable source found |

## Step 3: Reference Organization

After verification is complete, organize references according to project specifications.

### Tasks

1. **Check project specifications**: Citation style, placement location
2. **Register to reference list**: Add confirmed sources
3. **Add cross-references in text**: Footnotes/inline/numbered references

### Reference Format Examples

```markdown
<!-- Footnote format -->
The population of Japan is approximately 120 million[^1].
[^1]: Statistics Bureau of Japan, "Population Estimates", 2024

<!-- Inline format -->
The population of Japan is approximately 120 million (Statistics Bureau of Japan, 2024).
```

## Verifying Existing References/Citations

If the text already has references, also check the following:

### Checklist

- [ ] Links are live (no 404 errors)
- [ ] Cited content matches the reference source
- [ ] Citations are used in appropriate context
- [ ] Referenced information is up to date

### Handling Broken Links

```bash
# Check status code
curl -s -o /dev/null -w "%{http_code}" "https://example.com/page"

# Get alternative URL from Wayback Machine
curl -s "https://archive.org/wayback/available?url=example.com/page"
```

## Usage Examples

```
User: Verify the content of README.md and organize the references
```

```
User: Check if the citations in this paper are correct
```

```
User: Verify the items identified in Issue #45
```

## Output Report Format

```markdown
# Content Verification Report

## Target Files
- path/to/document.md

## Verification Summary
| Total | Accurate | Needs Correction | Incorrect | Unverifiable |
|-------|----------|-------------------|-----------|--------------|
| 10    | 7        | 2                 | 0         | 1            |

## Detailed Results
[Verification results for each item...]

## Reference Organization Status
- [ ] Reference list updated
- [ ] Cross-references added in text
- [ ] Link verification complete
```
