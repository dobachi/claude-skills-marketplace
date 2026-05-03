---
name: literature-search
description: Literature search, citation chasing, snowballing, author analysis, BibTeX export, and retraction screening using free official APIs (Semantic Scholar + OpenAlex + CrossRef). Honest Google Scholar alternative
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Literature Search Expert

Performs literature search, citation analysis, and snowballing using **free official APIs only** — Semantic Scholar (~225M papers), OpenAlex (~271M works), and CrossRef (canonical BibTeX, retraction status). A complete Google Scholar alternative for ~90% of workflows: no scraping, no paid services, no legal risk surface.

**Out of scope** (deliberate):
- **Google Scholar direct access.** No SerpAPI (active litigation, DMCA §1201 risk as of 2026), no Puppeteer scraping (ToS violation, CAPTCHA cascades). For genuinely Scholar-only data (grey literature, "All versions" cluster, Scholar's own h-index), use [Publish or Perish](https://harzing.com/resources/publish-or-perish) — Anne-Wil Harzing's free desktop app — see `references/backends.md`.
- **Full-text PDF retrieval and ingestion.** Out of scope; chain with `fact-checker` (Puppeteer) or external tools.
- **Document reading / summarization.** Hand off to `document-summary`.
- **Writing methodology.** Hand off to `academic-researcher`.

## Core Principles

1. **API-first**: default to free official sources. No scraping, no paid wrappers.
2. **DOI is the dedup key.** Cluster preprint↔published via shared DOI suffix or arXiv ID; fall back to (normalized title, first author, year).
3. **Integrity is baked in.** Retraction status checked by default via CrossRef Retraction Watch dataset. Predatory venue heuristics applied.
4. **Snowballing for systematic recall.** Wohlin (2014) methodology when the user needs comprehensive literature, not just top-N hits.
5. **Provenance preserved.** Every result tagged with the source backend (S2 / OpenAlex / CrossRef) and timestamp; h-index always reports its source.
6. **Multi-backend by default.** Single-source recall is an anti-pattern for systematic work.

## Backend Decision Matrix

| Goal | Primary | Supplement | Notes |
|---|---|---|---|
| Topic search | Semantic Scholar + OpenAlex (merge on DOI) | — | Use both for recall; S2 for ranking, OpenAlex for coverage |
| Forward citation chase ("who cites X?") | Semantic Scholar `/paper/{id}/citations` | OpenAlex `cited_by_api_url` | S2's API is cleanest |
| Backward citation chase ("what does X cite?") | CrossRef references (publisher-deposited) | Semantic Scholar `/references` | CrossRef when refs deposited (~60% of works) |
| Author profile + h-index | OpenAlex `summary_stats.h_index` | S2 `/author/{id}` | Always tag the source — values diverge by backend |
| "More like this" | Semantic Scholar `/recommendations` | — | Uses SPECTER2 embeddings |
| Open-access PDF discovery | OpenAlex `open_access.oa_url` | S2 `openAccessPdf` | OpenAlex shares lineage with Unpaywall |
| Canonical BibTeX | CrossRef content negotiation (`Accept: application/x-bibtex`) | — | More reliable than constructing from S2/OpenAlex metadata |
| Retraction status | CrossRef Retraction Watch dataset | — | S2/OpenAlex do not surface retractions reliably |

Detail: `references/backends.md`.

## Workflows

### Workflow A — Topic literature search

1. **Query design** — concept-OR-blocks joined by AND; include synonyms/acronyms; validate against 3–5 known seed papers.
2. **Multi-backend fetch** — `scripts/search.js "<topic>" --limit N` calls S2 + OpenAlex, merges on DOI.
3. **Filter** — year window, min citations, venue list (passed as flags or post-filtered).
4. **Integrity sweep** — `scripts/retract_check.js` over the result DOIs; flag retractions.
5. **BibTeX export** — `scripts/bibtex.js` over the kept DOIs.

### Workflow B — Citation chase / snowballing

1. **Resolve seed** — `scripts/citations.js <DOI|arxiv-id> --depth 1 --direction both` returns forward + backward.
2. **Snowball** — `scripts/citations.js <DOI> --snowball --depth 3` iterates Wohlin-style: each newly-accepted paper becomes the next iteration's seed; stops when new-accepted-rate falls below `--saturation-rate` (default 0.05) or `--depth` cap is reached.
3. **Output** — JSON graph (nodes = papers, edges = citations with direction) suitable for analysis or external visualization (Gephi, Cytoscape).

Methodology detail: `references/snowballing.md`.

### Workflow C — Author profile

1. **Disambiguate** — `scripts/author.js "<name>"` resolves to OpenAlex Author ID (uses ORCID when available); flags name collisions.
2. **Compile** — fetch all works; compute h-index overall and recent N years (default 5); aggregate top collaborators (recency-weighted).
3. **Sanity check** — compare publication counts across S2 and OpenAlex; large divergence (>30%) signals merged-profile or name-collision issues.

## Script Invocation

All scripts: Node.js 18+ (built-in `fetch`); **no npm dependencies**.

```bash
# Topic search
node <skill-path>/scripts/search.js "transformer attention" --limit 50 --year-from 2017

# Citation chase
node <skill-path>/scripts/citations.js 10.48550/arXiv.1706.03762 --depth 1 --direction both

# Snowballing
node <skill-path>/scripts/citations.js 10.48550/arXiv.1706.03762 --snowball --depth 3

# Author profile
node <skill-path>/scripts/author.js "Yann LeCun" --recent-years 5

# BibTeX (single or batch via stdin)
node <skill-path>/scripts/bibtex.js 10.48550/arXiv.1706.03762
echo -e "10.48550/arXiv.1706.03762\n10.1145/3458817.3476160" | node <skill-path>/scripts/bibtex.js -

# Retraction check
node <skill-path>/scripts/retract_check.js 10.1234/example
```

Always replace `<skill-path>` with the actual path to this skill's directory when running scripts.

### Polite-pool email

Set `LITSEARCH_EMAIL=you@example.com` to identify yourself in OpenAlex's polite pool and CrossRef's polite pool — they grant higher rate limits and prioritize your traffic.

### Optional Semantic Scholar API key

Set `S2_API_KEY=…` for higher RPS on Semantic Scholar. Free key request: <https://www.semanticscholar.org/product/api>. Without a key, scripts fall back to the shared unauthenticated pool (slower, may rate-limit during peak).

## Quality Rubric (5 axes)

| Dimension | Strong | Adequate | Weak |
|---|---|---|---|
| **Recall** | 2+ backends used; snowball iteration to saturation | 2 backends, no snowball | Single backend |
| **Precision** | Year/venue/citation filters tuned; predatory venues filtered | Some filtering | Raw API output dumped |
| **Integrity** | Retractions flagged; predatory venue heuristic applied; preprint↔published deduped | Retractions only | No integrity checks |
| **Provenance** | Backend + timestamp + h-index source on every record | Backend tagged | No provenance |
| **Reproducibility** | Query + filters + backend versions logged | Query logged | One-off result |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| **Predatory journal blindness** — accepting any indexed venue | Predatory venues distort literature; pollute references | Cross-check against DOAJ; use OpenAlex `host_venue` SJR/CiteScore as a heuristic; see `references/integrity.md` |
| **Retracted papers cited as authoritative** | Scholar/S2/OpenAlex don't reliably flag retractions | Always run `retract_check.js` before final cite list |
| **Preprint vs published double-counting** | Same work counted twice; citation counts inflated | DOI-based dedup; cluster preprint↔published via shared DOI suffix |
| **Citation manipulation indicators ignored** | Self-citation cartels and citation mills inflate metrics | Compute self-citation ratio (>30% is a flag); check author overlap in citing-set |
| **Single-source recall** | Each backend has coverage gaps; recall suffers | Always 2+ backends for systematic work; merge on DOI |
| **h-index reported without source** | S2 vs OpenAlex vs Scholar h-indices diverge meaningfully | Always tag: `h_index: 42 (OpenAlex, 2026-05-03)` |
| **"All versions" assumption** | Scholar's preprint+published cluster is not 1:1 in S2/OpenAlex | Document the dedup key used; flag unclustered duplicates |
| **Stop at top-10 results for systematic review** | Insufficient recall | Use snowballing with saturation criterion |

## Deliverable Formats

### Search results table

```markdown
| Rank | Title | Authors | Year | Venue | Citations | OA PDF | Source | Retracted? |
|---|---|---|---|---|---|---|---|---|
| 1 | Attention Is All You Need | Vaswani et al. | 2017 | NeurIPS | 95,432 | [PDF](…) | S2+OpenAlex | No |
| … | … | … | … | … | … | … | … | … |
```

### Snowball graph

```json
{
  "seeds": ["10.48550/arXiv.1706.03762"],
  "iterations": 3,
  "saturation_reached": true,
  "saturation_iteration": 3,
  "nodes": [{"doi": "...", "title": "...", "depth": 0, "accepted": true, "...": "..."}],
  "edges": [{"from": "...", "to": "...", "direction": "forward|backward"}],
  "stats": {"total_screened": 412, "total_accepted": 38, "by_iteration": [...]}
}
```

### Author report

```markdown
## Author: Yann LeCun

- **OpenAlex ID**: A5004478302
- **Works (OpenAlex)**: 412  | **(S2)**: 398
- **h-index (OpenAlex, 2026-05-03)**: 142
- **h-index, last 5 years**: 87
- **Top collaborators** (recency-weighted):
  | Rank | Name | Shared papers | Most recent |
  |---|---|---|---|
  | 1 | … | … | … |
```

### BibTeX bundle

Plain `.bib` file via CrossRef content negotiation; one entry per DOI.

### Retraction report

```markdown
| DOI | Status | Retraction date | Retraction reason | Source |
|---|---|---|---|---|
| 10.1234/example | Retracted | 2024-08-15 | Data fabrication | Retraction Watch |
```

## Iteration Modes

| Mode | When to use |
|---|---|
| **Quick search** | Top-N hits on a topic; no snowball |
| **Systematic search** | Topic + snowball to saturation; multi-backend; integrity sweep |
| **Citation chase** | Forward + backward from a known seed |
| **Author analysis** | Profile + h-index + collaborators |
| **Integrity audit** | Run retraction + predatory checks over an existing reference list |
| **Cross-source compare** | Same query in S2 vs OpenAlex; surface coverage gaps |

## References (consult when relevant)

- `references/backends.md` — Per-backend endpoints, rate limits, authentication, field mapping, dedup keys, coverage gaps; Publish-or-Perish as the Scholar fallback
- `references/snowballing.md` — Wohlin 2014 methodology, seed selection, forward/backward iteration, saturation, hybrid PRISMA+snowball
- `references/integrity.md` — Retraction checking, predatory venue heuristics, citation manipulation flags, preprint dedup
