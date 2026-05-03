# Integrity Reference

Detection of retracted papers, predatory journals, citation manipulation, and preprint↔published duplication. These checks are baked into the skill's default workflow because Google Scholar — and most other databases — do not surface these issues reliably.

## Why Integrity Checks Matter

Several recurring failure modes contaminate AI-assisted literature search:

- **Retracted papers** appear as ordinary results in Scholar / S2 / OpenAlex. A 2022 study ([PMC9140878](https://pmc.ncbi.nlm.nih.gov/articles/PMC9140878/)) found that retracted papers continue to receive thousands of citations after retraction.
- **Predatory journals** (low or no peer review, often pay-to-publish) distort the literature; their papers should be flagged or filtered.
- **Citation manipulation** — citation cartels, citation mills (paid services that sell citations), self-citation rings — inflate metrics. Documented in [Nature Sci. Reports 2025](https://www.nature.com/articles/s41598-025-88709-7) and [arXiv:2402.04607](https://arxiv.org/abs/2402.04607).
- **Preprint vs published duplication** — same work appears as arXiv preprint AND published version, double-counted in citation totals if not deduplicated.

## Retraction Checking

### Source

The **Retraction Watch Database** (RWD) is the authoritative source. Since June 2023, RWD is distributed under a CC license via CrossRef. CrossRef returns retraction status in `/works/{doi}` responses when present, via the `update-to` field and Crossmark metadata.

### Workflow

1. For every DOI in your result set, call `scripts/retract_check.js <DOI>`.
2. The script queries CrossRef's `/works/{doi}` endpoint and checks for:
   - `update-to[]` entries with `type: "retraction"` or `type: "withdrawal"`
   - Crossmark fields indicating retraction
3. Output: per-DOI status (`active` | `retracted` | `withdrawn` | `corrected` | `expression-of-concern`).
4. Flag retracted/withdrawn papers prominently in any reference list.

### What to do with retracted papers

- **Never cite as authoritative.** Retracted findings are usually retracted because they were wrong (data fabrication, methodology errors, plagiarism).
- **Cite as "retracted"** if discussing the retraction itself, the controversy, or the methodology lessons.
- **Expression of Concern** is not a retraction but indicates the publisher has unresolved questions about validity — note the status without dismissing the paper outright.
- **Corrections** are routine — note the existence of corrections but the paper remains valid (with the correction applied).

### Common gotchas

- Retraction status can be added years after publication; check on your *current* search, not based on cached metadata.
- Some retractions are "stealth" (silent removal); RWD aggregates these where possible.
- Conference papers and preprints may be retracted from the publication venue but remain on arXiv / personal pages.

## Predatory Journal Detection

There is no single authoritative list. Use a layered heuristic.

### Signals (any 2+ → flag for review)

| Signal | How to check |
|---|---|
| **Not in DOAJ** (Directory of Open Access Journals) — for OA venues | DOAJ API: <https://doaj.org/api/> |
| **Very low SJR** (Scimago Journal Rank) or absent from Scimago | OpenAlex `host_venue.type` and external Scimago lookup; SJR < 0.1 is suspicious |
| **Very rapid publication times** (< 2 weeks from submission to publication) | Publisher's own metrics; sometimes published on the journal site |
| **Authors-pay model with no transparent peer review** | Journal's "About" page; check APC vs. peer-review claims |
| **High percentage of authors from low-prestige institutions** with no external citations | OpenAlex authorship data |
| **Listed in known predatory journal indexes** | Beall's-list successors (Stop Predatory Journals, Cabell's Predatory Reports — paywalled) |
| **Hijacked journal name** — a parasitic journal mimicking a legitimate one | Compare ISSN against publisher's official record |
| **Spam invitations** to authors, often inviting submission of manuscripts in unrelated fields | Author reports |

### Practical filter

```python
# Pseudocode
def is_likely_predatory(work):
    venue = work.get("host_venue", {})
    if venue.get("issn_l") in known_predatory_issns:
        return True
    if not venue.get("is_in_doaj") and venue.get("is_oa") and venue.get("apc_usd", 0) > 0:
        # OA, has APC, not in DOAJ — suspicious
        return "likely"
    if venue.get("sjr_score", 1.0) < 0.1:
        return "suspicious"
    return False
```

### Open data sources

- [DOAJ Public Data Dump](https://doaj.org/docs/public-data-dump/) — all DOAJ-indexed journals (positive list)
- [Stop Predatory Journals](https://predatoryjournals.com/) — successor to Beall's list (negative list)
- [Retraction Watch's hijacked journals tracker](https://retractionwatch.com/the-retraction-watch-hijacked-journal-checker/) — for hijacked journals

The skill ships heuristic detection. When in doubt, surface the warning to the user rather than hard-filtering — false positives are common.

## Citation Manipulation

### Patterns to detect

| Pattern | Detection |
|---|---|
| **High self-citation ratio** | (citations from author's own prior papers) / (total citations); > 30% is a flag (varies by field) |
| **Citation cartels** — small group of authors mutually cite each other | Compute co-author overlap in citing-set; if > 30% of citations come from same lab/group, flag |
| **Citation farms / mills** — sudden spike in citations from low-quality venues | Inspect citing-paper venues for predatory cluster; check for time-burst pattern |
| **Coercive citation** — journal editors require citing journal's own papers | Compute fraction of citations from same journal |
| **Citation stacking** — papers citing each other in tight rings | Graph analysis: tight cycles in citation graph |

### When to flag vs. filter

- **Flag in the report** for the user to consider.
- **Don't auto-filter** — high self-citation can be legitimate (focused researcher in a small subfield); citation cartels can be hard to distinguish from genuine intellectual communities.
- **Hard-filter only retracted papers** — those are unambiguous.

### Sanity checks for "suspiciously high" citation counts

When a paper or author has citation counts that seem inflated relative to peers in the same subfield:

1. Compare counts across S2, OpenAlex, Scopus (if accessible) — large divergence may indicate platform-specific manipulation.
2. Check the citing-set: predatory venues over-represented?
3. Check citation timing: a sudden spike often indicates manipulation; organic citation accrues steadily.
4. Cross-reference with [Scite.ai](https://scite.ai/) or Semantic Scholar's "Highly Influential Citations" — these classify citations by purpose (supporting / mentioning / contrasting) and can reveal padding.

## Preprint ↔ Published Deduplication

### Why this matters

The same work often appears as:
- arXiv preprint (with arXiv DOI, e.g., `10.48550/arXiv.1706.03762`)
- Published version (with publisher DOI, e.g., `10.1145/...`)

Without dedup:
- Citation counts are split across the two records (under-count)
- Reference lists may include both (double-cite)
- Author profiles may double-count (h-index inflation)

### Dedup strategy (in `search.js` and `citations.js`)

1. **Primary**: DOI match. arXiv DOI and publisher DOI of the same work are different — but S2 records for the published version usually carry both `externalIds.DOI` and `externalIds.ArXiv`.
2. **Cluster via arXiv ID**: if two records share `externalIds.ArXiv` value, they are versions of the same work.
3. **Cluster via S2 `paperId`**: S2 collapses preprint and published versions under one `paperId` (with both DOIs as external IDs).
4. **OpenAlex `related_works[]`**: sometimes links versions; check for `type: preprint` vs `type: article` pairs with shared DOI prefix.
5. **Title + first author + year fallback**: when no other signal, normalized title + first author surname + year. Flag low-confidence clusters for manual review.

### When to keep both versions

- **Citing the preprint specifically** (e.g., "the original arXiv version showed X; the published version was revised to show Y") — keep both with annotation.
- **For author profiles**: dedupe (count once); attribute citations from both versions to the canonical record.

## Skill-Level Defaults

By default, the skill:

- ✅ Runs retraction check on every result set before final output (adds ~1 API call per DOI; cached)
- ✅ Computes self-citation ratio for author profiles; flags >30%
- ✅ Dedupes preprint↔published via DOI/arXiv ID
- ⚠️ Surfaces predatory-venue heuristic warnings in result tables (does not auto-filter; flags only)
- ⚠️ Does not auto-detect citation cartels (computational cost; available via `--cartel-check` flag in `author.js`)

## When to Skip Integrity Checks

- **Quick search** for personal exploration — fine to skip retraction check
- **Single known paper** lookup — retraction check is cheap, run it anyway
- **Time-pressured** scan — skip predatory heuristics; never skip retraction check

For any output that will be cited or shared, run the full integrity sweep.
