# Backends Reference

Per-API details for Semantic Scholar, OpenAlex, and CrossRef. Includes endpoints, rate limits, authentication, field mapping, dedup strategy, coverage gaps, and the Publish-or-Perish fallback for Scholar-only data.

## Semantic Scholar (Allen Institute for AI)

**Coverage**: ~225M papers, ~100M authors, ~2.8B citations. Strong on CS, AI, biomedicine; weaker on humanities, social sciences, non-English.

**Base URL**: `https://api.semanticscholar.org/graph/v1`

**Endpoints used**:

| Endpoint | Purpose |
|---|---|
| `/paper/search/bulk` | Topic search; supports up to 1000 results/page; `query`, `fields`, `year`, `venue`, `minCitationCount` filters |
| `/paper/{paperId}` | Single paper metadata; `paperId` can be S2 ID, DOI, arXiv ID, MAG ID, ACL ID, PMID, PMCID, CorpusId |
| `/paper/{paperId}/citations` | Forward citation chase; paginated |
| `/paper/{paperId}/references` | Backward citation chase; paginated |
| `/recommendations/v1/papers/forpaper/{paperId}` | "More like this" via SPECTER2 embeddings |
| `/author/{authorId}` | Author profile; includes `hIndex`, `paperCount`, `citationCount` |
| `/author/search` | Author disambiguation |

**Rate limits**:
- Unauthenticated: shared pool; ~5,000 req / 5 min globally; expect throttling under load.
- With free API key (request at <https://www.semanticscholar.org/product/api>): default 1 RPS, raisable to ~100 RPS on request.

**Authentication**: HTTP header `x-api-key: <YOUR_KEY>`. Set `S2_API_KEY` env var; scripts pick it up automatically.

**Useful fields**:
- `title`, `abstract`, `year`, `authors[]{name, authorId}`, `venue`, `publicationVenue`
- `externalIds{DOI, ArXiv, PMID, ...}` — critical for dedup
- `citationCount`, `influentialCitationCount` (the "highly influential" classifier)
- `tldr{text}` — auto-generated summary (when available)
- `openAccessPdf{url}` — when available
- `embedding` — SPECTER2 vector (768-d)

**Pagination**: `/paper/search/bulk` returns `token` for continuation; loop until empty.

**Errors**: 429 → exponential backoff (base 2s, max 3 retries). 5xx → retry once; otherwise surface.

## OpenAlex (OurResearch)

**Coverage**: ~271M works (Nov 2025), broadest open scholarly graph. Includes works, authors, sources (venues), institutions, concepts (topics), funders. CC0 metadata.

**Base URL**: `https://api.openalex.org`

**Endpoints used**:

| Endpoint | Purpose |
|---|---|
| `/works?search=<q>` | Topic search; rich filtering on `from_publication_date`, `cited_by_count`, `host_venue.id`, `concepts.id` |
| `/works/{id}` | Single work; `id` can be OpenAlex ID, DOI, PMID, MAG ID, etc. |
| `/works?filter=cited_by:{id}` | Forward citation chase |
| `/authors?search=<name>` | Author search |
| `/authors/{id}` | Author profile; includes `summary_stats.h_index`, `summary_stats.i10_index`, `summary_stats.2yr_mean_citedness` |
| `/works?filter=author.id:{id}&per-page=200` | All works by an author |

**Rate limits**:
- Public pool: 10 RPS, 100,000 req/day
- Polite pool (recommended): same limits but prioritized; identify with `mailto=<your email>` query param OR set `LITSEARCH_EMAIL` env var
- Free API keys are rolling out (Feb 2026 cutover); the `mailto=` pattern remains supported

**Authentication**: query param `?mailto=you@example.com` (polite pool) or `?api_key=…` (when API keys are issued). Scripts use `LITSEARCH_EMAIL` automatically.

**Useful fields**:
- `id` (OpenAlex Work ID), `doi`, `title`, `display_name`
- `publication_year`, `type` (article / preprint / dataset / ...)
- `cited_by_count`, `referenced_works[]`, `cited_by_api_url`
- `authorships[]{author{id, display_name, orcid}, institutions[]}`
- `host_venue{id, display_name, issn_l, type, is_oa}` — venue with OA status
- `open_access{is_oa, oa_url, oa_status}` — `oa_url` is the best free PDF link
- `concepts[]{id, display_name, score}` — auto-tagged topics (Wikipedia-derived)
- `referenced_works[]` — backward citation IDs (when known)

**Coverage gaps**:
- ~40% of records lack abstracts (per OurResearch's own metrics)
- ~60% of records have missing/partial institutional affiliations
- Citation counts thinner than Scholar's (Scholar indexes preprint servers and personal sites OpenAlex misses)

**Pagination**: `?per-page=200&cursor=*` then page through `meta.next_cursor`.

## CrossRef

**Coverage**: ~165M DOI-bearing research outputs. Authoritative publisher-deposited metadata.

**Base URL**: `https://api.crossref.org`

**Endpoints used**:

| Endpoint | Purpose |
|---|---|
| `/works/{doi}` | Full metadata for one DOI |
| Content negotiation on `https://doi.org/{doi}` with `Accept: application/x-bibtex` | Canonical BibTeX |
| `/works?query=<topic>` | Topic search (less rich than S2/OpenAlex; supplemental only) |
| `/works/{doi}` (returns `is-referenced-by-count`, `reference[]`) | Backward citations when publisher deposited refs (~60%) |

**Rate limits**:
- Public pool: anonymous; rate-limited dynamically (respect `X-Rate-Limit-*` headers)
- Polite pool: identify with `mailto=` query param OR `User-Agent: yourapp/1.0 (mailto:you@example.com)`
- Plus pool: paid; not used by this skill

**Authentication**: User-Agent + `mailto=` for polite pool. Scripts use `LITSEARCH_EMAIL` automatically.

**BibTeX content negotiation**:
```bash
curl -LH "Accept: application/x-bibtex" "https://doi.org/10.48550/arXiv.1706.03762"
```

Returns canonical BibTeX from the publisher's metadata. **Far more reliable** than constructing BibTeX from S2/OpenAlex fields; the `bibtex.js` script wraps this.

**Retraction Watch dataset**:
- Publicly available since 2023 under CC license, distributed via CrossRef
- Per-DOI lookup: CrossRef returns retraction status in `/works/{doi}` response when present
- The `retract_check.js` script wraps this lookup

## Field Mapping (cross-API)

| Concept | Semantic Scholar | OpenAlex | CrossRef |
|---|---|---|---|
| Paper ID | `paperId`, `corpusId` | `id` (e.g., `https://openalex.org/W2741809807`) | DOI |
| DOI | `externalIds.DOI` | `doi` | (the key) |
| arXiv ID | `externalIds.ArXiv` | `ids.arxiv` | (in `subtitle` or via DOI prefix) |
| Title | `title` | `title` / `display_name` | `title[]` |
| Year | `year` | `publication_year` | `published.date-parts[0][0]` |
| Authors | `authors[]{name, authorId}` | `authorships[]{author{...}}` | `author[]` |
| Venue | `venue`, `publicationVenue` | `host_venue.display_name` | `container-title[]` |
| Citations count | `citationCount` | `cited_by_count` | `is-referenced-by-count` |
| Abstract | `abstract` | `abstract_inverted_index` (rebuild) | `abstract` (rare) |
| OA PDF | `openAccessPdf.url` | `open_access.oa_url` | (no) |
| References | `references[]` | `referenced_works[]` | `reference[]` |
| Author h-index | (compute or `/author/{id}.hIndex`) | `summary_stats.h_index` | (no) |

## Dedup Strategy

**Primary key**: DOI (case-normalized).

**Fallback when DOI missing**:
1. arXiv ID → derived DOI (`10.48550/arXiv.<id>`)
2. PMID → CrossRef lookup → DOI
3. Composite key: lowercased + alphanumeric-only first 80 chars of title + first author surname + year

**Preprint↔published reconciliation**:
- arXiv preprint and the published version often share a DOI suffix or the published DOI cites the arXiv ID; check `externalIds.ArXiv` on the published S2 record
- OpenAlex `related_works[]` sometimes links them
- When uncertain, prefer the DOI-bearing version with the higher `cited_by_count`

**Cluster confidence**:
- High: DOI match
- Medium: arXiv ID match across versions
- Low: title+author+year match — flag for manual review

## Coverage and Quality Notes

- **Scholar wins on**: grey literature (theses, working papers, personal sites), pre-DOI historical content, "All versions" cluster traversal
- **S2 wins on**: TLDR auto-summaries, "Highly Influential Citations" classifier, SPECTER2 embeddings for similarity
- **OpenAlex wins on**: broadest coverage, h-index as a first-class field, OA PDF discovery, concept taxonomy, free-tier rate limits
- **CrossRef wins on**: canonical publisher metadata, BibTeX, retraction status, funder linkage
- **None of these reliably surface**: predatory venues (need DOAJ + venue checks), citation manipulation (need self-citation analysis)

## Publish or Perish — the Scholar fallback

If a user genuinely needs Scholar-only data (h-index that matches Scholar's published value, "All versions" cluster, grey literature recall), the responsible path is:

**[Publish or Perish](https://harzing.com/resources/publish-or-perish)** by Anne-Wil Harzing — free desktop app, queries Scholar + 8 other sources, runs locally on the user's machine.

- Liability stays with the user (they execute the queries on their own IP)
- POP handles Scholar's rate-limiting and surfaces CAPTCHAs to the user
- Exports BibTeX, RIS, EndNote
- Computes h-index, g-index, hI-norm consistent with Scholar conventions

**The skill does not invoke Publish or Perish.** When the user asks for Scholar-canonical data, instruct them to install POP and run the query themselves; the skill helps construct the query string and process the exported file once they have it.
