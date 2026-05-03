# Snowballing Reference

Wohlin's 2014 methodology for systematic literature review via snowballing, as implemented in `scripts/citations.js --snowball`. Includes seed selection, iteration, screening, saturation, and the hybrid PRISMA + snowball approach.

## Why Snowball

Database keyword search (PRISMA-style) misses papers that:
- Use different terminology than your query (especially across decades or research communities)
- Are cited heavily but not indexed in your chosen databases
- Are recent enough that database indexing lags

Snowballing exploits the **citation graph**: relevant papers cite other relevant papers (and are cited by them). It is community-driven rather than vocabulary-driven, achieving complementary recall.

Mourão et al. (2020, *Information and Software Technology*, ["Successful combination of database search and snowballing"](https://www.sciencedirect.com/science/article/pii/S0950584922000659)) show that **hybrid (database + snowballing) yields higher recall than either alone**.

## Wohlin's Methodology (2014)

Source: Claes Wohlin, ["Guidelines for snowballing in systematic literature studies and a replication in software engineering"](https://www.wohlin.eu/ease14.pdf), EASE'14.

### Step 1 — Seed (start) set

Select a small **diverse** set of seed papers. Wohlin emphasizes:

- **Community diversity** — different research groups, different countries
- **Temporal spread** — some old, some recent
- **Venue spread** — different journals/conferences
- **Avoid single-author/single-lab clustering** — would bias the entire snowball

The seed set need not be exhaustive. Aim for ~5–10 papers that, between them, cover the topic from multiple angles.

How to find seeds:
- A focused database search (PRISMA-style preliminary)
- Known landmark papers in the field (textbook references, review articles)
- Papers you already trust

### Step 2 — Per-seed snowball

For each seed, do BOTH:

- **Backward snowball** — read the seed's reference list. Apply screening (title → abstract → full-text). Accepted papers are added to the result set.
- **Forward snowball** — find papers that cite the seed (via Semantic Scholar `/citations` or OpenAlex `cited_by_api_url`). Apply screening. Accepted papers added.

### Step 3 — Iterate

Each newly-accepted paper becomes a seed for the next iteration. Repeat backward + forward on the new seeds.

### Step 4 — Saturation

Stop when **no new relevant papers** are found in a complete iteration. Practical saturation criteria (combine):

- **No new accepted papers** in a full forward + backward pass over the latest accepted set
- **Convergence on cardinal papers** — the same handful of central papers appear repeatedly across snowball directions
- **Accept-rate threshold** — fraction of newly-screened papers that are accepted falls below a chosen threshold (e.g., < 5%; the `--saturation-rate` flag in `citations.js`)

Empirically, **2–4 iterations suffice for narrow topics**; broad topics may need 5+ but rarely converge cleanly.

## Screening Protocol

For every candidate paper from forward or backward chase, apply screening **in this order** (cheapest first):

| Stage | Decision basis | Cost | Reject when |
|---|---|---|---|
| 1. Title | Title + venue | seconds | Off-topic; wrong language; clearly different field |
| 2. Abstract | Abstract + keywords | minutes | Topic-adjacent but not relevant; wrong methodology; insufficient scope |
| 3. Full-text (optional) | Full paper | hours | Doesn't actually answer the question on careful read |

Document **inclusion/exclusion criteria** before starting the snowball. Apply uniformly.

## Saturation Detection

The `citations.js --snowball` script tracks per-iteration metrics:

- `screened_this_iteration` — total candidate papers
- `accepted_this_iteration` — passed screening
- `accept_rate = accepted / screened`
- `new_papers_added` — accepted papers not seen in earlier iterations

Stop conditions (any one):
1. `new_papers_added == 0` (true saturation)
2. `accept_rate < --saturation-rate` (default 0.05)
3. `iteration >= --depth` (hard cap)

Output includes `saturation_reached: true|false` and `saturation_iteration: N`.

## Hybrid PRISMA + Snowball

PRISMA 2020 ([prisma-statement.org](https://www.prisma-statement.org)) and the **PRISMA-S** 2021 search extension require reporting Boolean queries against named databases. The PRISMA flow diagram explicitly accommodates "records identified from citation searching" as a parallel arm to "records identified from databases."

Recommended workflow for systematic reviews:

1. **Database arm** — formal Boolean query in 2+ databases (Semantic Scholar + OpenAlex via this skill; for medical, also PubMed/Embase via dedicated tools).
2. **Snowball arm** — pick 3–5 highly-cited papers from the database results as seeds; snowball to saturation.
3. **Merge** — DOI-dedupe both arms; report counts at each stage in the PRISMA flow diagram.
4. **Report** — query strings, dates run, result counts, screening criteria, exclusion reasons.

The Cochrane Handbook (Ch. 4, "Searching for studies") explicitly recommends supplementing database search with reference checking and forward citation searches.

## Output Graph Schema

`citations.js --snowball` outputs:

```json
{
  "seeds": ["10.48550/arXiv.1706.03762", "..."],
  "config": {
    "depth": 3,
    "direction": "both",
    "saturation_rate": 0.05,
    "screening": "auto"  // or "manual" if user-driven
  },
  "iterations": 3,
  "saturation_reached": true,
  "saturation_iteration": 3,
  "stats": {
    "total_screened": 412,
    "total_accepted": 38,
    "by_iteration": [
      {"i": 0, "screened": 0, "accepted": 5, "accept_rate": null, "new_papers": 5},
      {"i": 1, "screened": 178, "accepted": 21, "accept_rate": 0.118, "new_papers": 21},
      {"i": 2, "screened": 156, "accepted": 9, "accept_rate": 0.058, "new_papers": 9},
      {"i": 3, "screened": 78, "accepted": 3, "accept_rate": 0.038, "new_papers": 3}
    ]
  },
  "nodes": [
    {
      "doi": "10.48550/arXiv.1706.03762",
      "title": "Attention Is All You Need",
      "authors": ["Vaswani", "Shazeer", "..."],
      "year": 2017,
      "venue": "NeurIPS",
      "citations": 95432,
      "depth": 0,
      "accepted": true,
      "added_in_iteration": 0,
      "source": ["S2", "OpenAlex"]
    }
  ],
  "edges": [
    {"from": "10.48550/arXiv.1706.03762", "to": "10.1234/example", "direction": "forward", "iteration": 1}
  ]
}
```

Suitable for direct ingestion into Gephi (via GraphML conversion) or Cytoscape.

## When NOT to Snowball

- **Quick literature scan** — top-N hits from `search.js` is enough; snowball is overkill.
- **Very recent topics** (< 1 year old) — citation graph hasn't formed; rely on database search and arXiv monitoring.
- **Cross-disciplinary scope** — citation graph clusters within disciplines; snowball misses adjacent-field literature; combine with concept-based search (OpenAlex `concepts.id`).

## Auto-Screening vs Manual

`citations.js --snowball` defaults to **manual screening**: it returns all candidate papers from each iteration and waits for the user (or downstream agent) to decide acceptance. With `--auto-accept`, it accepts everything (no screening); with `--auto-relevance <min-score>`, it uses S2's relevance score to filter — but this is a heuristic and degrades the systematic-review quality.

For real systematic reviews, run with the default and have a human (or LLM with explicit criteria) screen each batch.

## References

- Wohlin, C. (2014) ["Guidelines for snowballing in systematic literature studies and a replication in software engineering"](https://www.wohlin.eu/ease14.pdf), EASE'14
- Felizardo et al. (2016) ["Second-generation snowballing"](https://dl.acm.org/doi/10.1145/2915970.2916006)
- Mourão et al. (2020) ["Successful combination of database search and snowballing"](https://www.sciencedirect.com/science/article/pii/S0950584922000659), *Information and Software Technology*
- [PRISMA 2020 statement](https://www.prisma-statement.org/)
- [PRISMA-S search extension](https://prisma-statement.org/Extensions/Searching)
- [Cochrane Handbook, Ch. 4](https://training.cochrane.org/handbook/current/chapter-04)
