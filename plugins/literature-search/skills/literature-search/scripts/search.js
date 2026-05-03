#!/usr/bin/env node
/**
 * search.js - Multi-backend literature search using Semantic Scholar + OpenAlex.
 *
 * Usage:
 *   node search.js <query> [options]
 *
 * Options:
 *   --limit <N>           Max results per backend (default: 30; merged result may be smaller after dedup)
 *   --year-from <YYYY>    Earliest publication year
 *   --year-to <YYYY>      Latest publication year
 *   --min-citations <N>   Minimum citation count
 *   --backend <s2|openalex|both>   Which backend(s) to query (default: both)
 *
 * Output: JSON array of deduplicated, ranked results to stdout.
 *         Each record: {doi, title, authors, year, venue, citations, oa_url, sources, ...}.
 *
 * Environment:
 *   LITSEARCH_EMAIL   Email for OpenAlex / CrossRef polite pool
 *   S2_API_KEY        Optional Semantic Scholar API key for higher RPS
 *
 * Examples:
 *   node search.js "transformer attention" --limit 50 --year-from 2017
 *   node search.js "RAG retrieval augmented generation" --min-citations 100
 *
 * Exit codes:
 *   0  Success
 *   1  Bad usage
 *   2  All backends failed
 */

const EMAIL = process.env.LITSEARCH_EMAIL || "anonymous@example.com";
const S2_KEY = process.env.S2_API_KEY || null;
const UA = `literature-search-skill/1.0 (mailto:${EMAIL})`;

function parseArgs(argv) {
  const args = {
    query: null,
    limit: 30,
    yearFrom: null,
    yearTo: null,
    minCitations: null,
    backend: "both",
  };
  const rest = argv.slice(2);
  const positional = [];
  let i = 0;
  while (i < rest.length) {
    const a = rest[i];
    if (a === "--help" || a === "-h") {
      printHelp();
      process.exit(0);
    } else if (a === "--limit") {
      args.limit = parseInt(rest[++i], 10);
    } else if (a === "--year-from") {
      args.yearFrom = parseInt(rest[++i], 10);
    } else if (a === "--year-to") {
      args.yearTo = parseInt(rest[++i], 10);
    } else if (a === "--min-citations") {
      args.minCitations = parseInt(rest[++i], 10);
    } else if (a === "--backend") {
      args.backend = rest[++i];
    } else if (a.startsWith("--")) {
      console.error(`Unknown option: ${a}`);
      process.exit(1);
    } else {
      positional.push(a);
    }
    i++;
  }
  args.query = positional.join(" ").trim();
  if (!args.query) {
    printHelp();
    process.exit(1);
  }
  return args;
}

function printHelp() {
  console.error(`Usage: node search.js <query> [--limit N] [--year-from YYYY] [--year-to YYYY] [--min-citations N] [--backend s2|openalex|both]`);
}

async function fetchWithBackoff(url, options = {}, maxRetries = 3) {
  let attempt = 0;
  while (true) {
    const resp = await fetch(url, options);
    if (resp.status === 429 || resp.status >= 500) {
      if (attempt >= maxRetries) {
        throw new Error(`HTTP ${resp.status} after ${maxRetries} retries: ${url}`);
      }
      const delay = 2000 * Math.pow(2, attempt);
      await new Promise((r) => setTimeout(r, delay));
      attempt++;
      continue;
    }
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${url}`);
    }
    return resp;
  }
}

async function searchSemanticScholar(query, args) {
  const fields = "title,abstract,year,authors,venue,externalIds,citationCount,influentialCitationCount,openAccessPdf,tldr";
  const params = new URLSearchParams({ query, fields, limit: String(Math.min(args.limit, 100)) });
  if (args.yearFrom || args.yearTo) {
    const from = args.yearFrom || "*";
    const to = args.yearTo || "*";
    params.set("year", `${from}-${to}`);
  }
  if (args.minCitations !== null) {
    params.set("minCitationCount", String(args.minCitations));
  }
  const url = `https://api.semanticscholar.org/graph/v1/paper/search/bulk?${params}`;
  const headers = { "User-Agent": UA };
  if (S2_KEY) headers["x-api-key"] = S2_KEY;
  try {
    const resp = await fetchWithBackoff(url, { headers });
    const json = await resp.json();
    return (json.data || []).map((p) => normalizeS2(p));
  } catch (e) {
    console.error(`[s2] error: ${e.message}`);
    return [];
  }
}

function normalizeS2(p) {
  const doi = p.externalIds?.DOI ? p.externalIds.DOI.toLowerCase() : null;
  const arxiv = p.externalIds?.ArXiv || null;
  return {
    doi,
    arxiv,
    title: p.title || null,
    authors: (p.authors || []).map((a) => a.name).filter(Boolean),
    year: p.year || null,
    venue: p.venue || p.publicationVenue?.name || null,
    citations: p.citationCount ?? null,
    influential_citations: p.influentialCitationCount ?? null,
    abstract: p.abstract || null,
    tldr: p.tldr?.text || null,
    oa_url: p.openAccessPdf?.url || null,
    sources: ["S2"],
    s2_paper_id: p.paperId || null,
  };
}

async function searchOpenAlex(query, args) {
  const params = new URLSearchParams({
    search: query,
    "per-page": String(Math.min(args.limit, 200)),
    mailto: EMAIL,
  });
  const filters = [];
  if (args.yearFrom) filters.push(`from_publication_date:${args.yearFrom}-01-01`);
  if (args.yearTo) filters.push(`to_publication_date:${args.yearTo}-12-31`);
  if (args.minCitations !== null) filters.push(`cited_by_count:>${args.minCitations - 1}`);
  if (filters.length) params.set("filter", filters.join(","));
  const url = `https://api.openalex.org/works?${params}`;
  try {
    const resp = await fetchWithBackoff(url, { headers: { "User-Agent": UA } });
    const json = await resp.json();
    return (json.results || []).map((w) => normalizeOpenAlex(w));
  } catch (e) {
    console.error(`[openalex] error: ${e.message}`);
    return [];
  }
}

function normalizeOpenAlex(w) {
  const doi = w.doi ? w.doi.replace(/^https?:\/\/doi\.org\//i, "").toLowerCase() : null;
  const arxivId = w.ids?.arxiv || null;
  // Reconstruct abstract from inverted index
  let abstract = null;
  if (w.abstract_inverted_index) {
    const positions = {};
    for (const [word, idxs] of Object.entries(w.abstract_inverted_index)) {
      for (const idx of idxs) positions[idx] = word;
    }
    const sorted = Object.keys(positions).map(Number).sort((a, b) => a - b);
    abstract = sorted.map((i) => positions[i]).join(" ");
  }
  return {
    doi,
    arxiv: arxivId ? arxivId.replace(/^https?:\/\/arxiv\.org\/abs\//i, "") : null,
    title: w.title || w.display_name || null,
    authors: (w.authorships || []).map((a) => a.author?.display_name).filter(Boolean),
    year: w.publication_year || null,
    venue: w.host_venue?.display_name || w.primary_location?.source?.display_name || null,
    citations: w.cited_by_count ?? null,
    abstract,
    oa_url: w.open_access?.oa_url || null,
    is_oa: w.open_access?.is_oa || false,
    sources: ["OpenAlex"],
    openalex_id: w.id || null,
    type: w.type || null,
  };
}

function dedup(records) {
  const byKey = new Map();
  for (const r of records) {
    let key = r.doi;
    if (!key && r.arxiv) key = `arxiv:${r.arxiv}`;
    if (!key) {
      const norm = (r.title || "").toLowerCase().replace(/[^a-z0-9]+/g, "").slice(0, 80);
      const author = (r.authors[0] || "").toLowerCase().split(/\s+/).pop() || "";
      key = `t:${norm}|${author}|${r.year || ""}`;
    }
    if (byKey.has(key)) {
      const existing = byKey.get(key);
      existing.sources = Array.from(new Set([...existing.sources, ...r.sources]));
      // Prefer non-null fields from the merged record
      for (const f of ["doi", "arxiv", "title", "authors", "year", "venue", "abstract", "oa_url", "tldr", "influential_citations"]) {
        if (existing[f] == null && r[f] != null) existing[f] = r[f];
      }
      // Keep the maximum citation count
      if ((r.citations ?? 0) > (existing.citations ?? 0)) existing.citations = r.citations;
    } else {
      byKey.set(key, { ...r });
    }
  }
  return Array.from(byKey.values());
}

function rank(records) {
  // Simple rank: citations × log relevance proxy. Without query relevance scores, just sort by citations.
  return records.sort((a, b) => (b.citations ?? 0) - (a.citations ?? 0));
}

async function main() {
  const args = parseArgs(process.argv);
  console.error(`[info] query="${args.query}" backends=${args.backend} limit=${args.limit}`);
  const tasks = [];
  if (args.backend === "s2" || args.backend === "both") tasks.push(searchSemanticScholar(args.query, args));
  if (args.backend === "openalex" || args.backend === "both") tasks.push(searchOpenAlex(args.query, args));
  const results = (await Promise.all(tasks)).flat();
  if (results.length === 0) {
    console.error("[error] all backends returned 0 results");
    process.exit(2);
  }
  const deduped = dedup(results);
  const ranked = rank(deduped).slice(0, args.limit);
  console.error(`[info] s2+openalex returned ${results.length} raw, ${deduped.length} after dedup, returning top ${ranked.length}`);
  process.stdout.write(JSON.stringify({
    query: args.query,
    timestamp: new Date().toISOString(),
    config: { limit: args.limit, year_from: args.yearFrom, year_to: args.yearTo, min_citations: args.minCitations, backend: args.backend },
    stats: { raw: results.length, deduped: deduped.length, returned: ranked.length },
    results: ranked,
  }, null, 2) + "\n");
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(2);
});
