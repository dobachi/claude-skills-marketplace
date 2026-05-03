#!/usr/bin/env node
/**
 * author.js - Author profile analysis via OpenAlex (primary) + Semantic Scholar (sanity check).
 *
 * Resolves an author by name (or ORCID, or OpenAlex ID), fetches publications,
 * computes h-index (overall and recent N years), and extracts top collaborators
 * with recency-weighted scoring.
 *
 * Usage:
 *   node author.js <name|ORCID|openalex-id> [options]
 *
 * Options:
 *   --recent-years <N>    Window for "recent h-index" and recency weighting (default: 5)
 *   --top-collaborators <N>   Return top N collaborators (default: 10)
 *   --limit <N>           Max works to fetch (default: 500)
 *
 * Output: JSON object {author, openalex_id, works_count, h_index, h_index_recent, top_collaborators, sanity}.
 *
 * Environment:
 *   LITSEARCH_EMAIL   Email for OpenAlex polite pool
 *   S2_API_KEY        Optional Semantic Scholar API key for higher RPS
 *
 * Examples:
 *   node author.js "Yann LeCun"
 *   node author.js "0000-0002-5159-3517" --recent-years 5
 *
 * Exit codes:
 *   0  Success
 *   1  Bad usage
 *   2  Author not found / ambiguous beyond resolution
 *   3  All API calls failed
 */

const EMAIL = process.env.LITSEARCH_EMAIL || "anonymous@example.com";
const S2_KEY = process.env.S2_API_KEY || null;
const UA = `literature-search-skill/1.0 (mailto:${EMAIL})`;
const OA_BASE = "https://api.openalex.org";
const S2_BASE = "https://api.semanticscholar.org/graph/v1";

function parseArgs(argv) {
  const args = { ident: null, recentYears: 5, topCollaborators: 10, limit: 500 };
  const rest = argv.slice(2);
  const positional = [];
  let i = 0;
  while (i < rest.length) {
    const a = rest[i];
    if (a === "--help" || a === "-h") { printHelp(); process.exit(0); }
    else if (a === "--recent-years") args.recentYears = parseInt(rest[++i], 10);
    else if (a === "--top-collaborators") args.topCollaborators = parseInt(rest[++i], 10);
    else if (a === "--limit") args.limit = parseInt(rest[++i], 10);
    else if (a.startsWith("--")) { console.error(`Unknown option: ${a}`); process.exit(1); }
    else positional.push(a);
    i++;
  }
  args.ident = positional.join(" ").trim();
  if (!args.ident) { printHelp(); process.exit(1); }
  return args;
}

function printHelp() {
  console.error(`Usage: node author.js <name|ORCID|openalex-id> [--recent-years N] [--top-collaborators N] [--limit N]`);
}

async function fetchWithBackoff(url, options = {}, maxRetries = 3) {
  let attempt = 0;
  while (true) {
    const resp = await fetch(url, options);
    if (resp.status === 429 || resp.status >= 500) {
      if (attempt >= maxRetries) throw new Error(`HTTP ${resp.status} after ${maxRetries} retries: ${url}`);
      await new Promise((r) => setTimeout(r, 2000 * Math.pow(2, attempt)));
      attempt++;
      continue;
    }
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${url}`);
    return resp;
  }
}

async function resolveAuthorOpenAlex(ident) {
  // ORCID like 0000-0002-5159-3517
  const isOrcid = /^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/.test(ident);
  // OpenAlex ID like A5004478302 or openalex.org/A5004478302
  const oaMatch = ident.match(/A\d+/);
  let url;
  if (oaMatch) {
    url = `${OA_BASE}/authors/${oaMatch[0]}?mailto=${EMAIL}`;
  } else if (isOrcid) {
    url = `${OA_BASE}/authors/orcid:${ident}?mailto=${EMAIL}`;
  } else {
    url = `${OA_BASE}/authors?search=${encodeURIComponent(ident)}&per-page=5&mailto=${EMAIL}`;
  }
  const resp = await fetchWithBackoff(url, { headers: { "User-Agent": UA } });
  const json = await resp.json();
  if (json.results) {
    if (json.results.length === 0) return null;
    if (json.results.length > 1) {
      const top = json.results[0];
      console.error(`[warn] ${json.results.length} candidates for "${ident}"; using top match: ${top.display_name} (${top.id})`);
      console.error(`[warn] disambiguate by passing ORCID or OpenAlex ID directly`);
      return top;
    }
    return json.results[0];
  }
  return json; // single-author response (ID/ORCID lookup)
}

async function fetchAllWorks(authorId, limit) {
  const works = [];
  let cursor = "*";
  while (works.length < limit && cursor) {
    const url = `${OA_BASE}/works?filter=author.id:${authorId}&per-page=200&cursor=${cursor}&mailto=${EMAIL}`;
    const resp = await fetchWithBackoff(url, { headers: { "User-Agent": UA } });
    const json = await resp.json();
    works.push(...(json.results || []));
    cursor = json.meta?.next_cursor || null;
    if (!cursor || (json.results || []).length === 0) break;
  }
  return works.slice(0, limit);
}

function computeHIndex(citationCounts) {
  const sorted = [...citationCounts].sort((a, b) => b - a);
  let h = 0;
  for (let i = 0; i < sorted.length; i++) {
    if (sorted[i] >= i + 1) h = i + 1;
    else break;
  }
  return h;
}

function topCollaborators(works, authorId, recentYears, topN) {
  const now = new Date().getFullYear();
  const counts = new Map(); // key: collaboratorId, value: {name, count, weighted, latest_year, papers}
  for (const w of works) {
    const year = w.publication_year || now;
    const decay = Math.exp(-Math.max(0, now - year) / recentYears);
    for (const auth of w.authorships || []) {
      const a = auth.author;
      if (!a) continue;
      if (a.id === `https://openalex.org/${authorId}` || a.id === authorId) continue;
      const key = a.id || a.display_name;
      if (!counts.has(key)) counts.set(key, { name: a.display_name, openalex_id: a.id, count: 0, weighted: 0, latest_year: 0, papers: [] });
      const c = counts.get(key);
      c.count++;
      c.weighted += decay;
      if (year > c.latest_year) c.latest_year = year;
      c.papers.push({ title: w.title || w.display_name, year });
    }
  }
  const sorted = Array.from(counts.values()).sort((a, b) => b.weighted - a.weighted);
  return sorted.slice(0, topN).map((c) => ({ name: c.name, openalex_id: c.openalex_id, shared_papers: c.count, weighted_score: Number(c.weighted.toFixed(3)), most_recent_collab_year: c.latest_year }));
}

async function s2SanityCheck(name) {
  try {
    const url = `${S2_BASE}/author/search?query=${encodeURIComponent(name)}&fields=name,paperCount,citationCount,hIndex&limit=3`;
    const headers = { "User-Agent": UA };
    if (S2_KEY) headers["x-api-key"] = S2_KEY;
    const resp = await fetchWithBackoff(url, { headers });
    const json = await resp.json();
    if (json.data && json.data.length > 0) return json.data[0];
  } catch (e) {
    console.error(`[warn] S2 sanity-check failed: ${e.message}`);
  }
  return null;
}

async function main() {
  const args = parseArgs(process.argv);
  console.error(`[info] resolving author: ${args.ident}`);

  const author = await resolveAuthorOpenAlex(args.ident);
  if (!author) {
    console.error(`[error] author not found in OpenAlex`);
    process.exit(2);
  }

  const oaId = (author.id || "").replace(/^https?:\/\/openalex\.org\//, "");
  console.error(`[info] resolved: ${author.display_name} (OpenAlex: ${oaId})`);

  const works = await fetchAllWorks(oaId, args.limit);
  console.error(`[info] fetched ${works.length} works`);

  const allCitations = works.map((w) => w.cited_by_count || 0);
  const hIndex = computeHIndex(allCitations);

  const now = new Date().getFullYear();
  const recentWorks = works.filter((w) => (w.publication_year || 0) >= now - args.recentYears + 1);
  const recentCitations = recentWorks.map((w) => w.cited_by_count || 0);
  const hIndexRecent = computeHIndex(recentCitations);

  const collaborators = topCollaborators(works, oaId, args.recentYears, args.topCollaborators);

  const s2 = await s2SanityCheck(author.display_name);
  const sanity = {
    openalex_works: works.length,
    s2_paper_count: s2?.paperCount || null,
    divergence_pct: s2?.paperCount ? Math.abs(works.length - s2.paperCount) / Math.max(works.length, s2.paperCount) : null,
    flag: s2?.paperCount && Math.abs(works.length - s2.paperCount) / Math.max(works.length, s2.paperCount) > 0.3 ? "POSSIBLE_NAME_COLLISION" : "OK",
  };

  const out = {
    author: author.display_name,
    openalex_id: oaId,
    orcid: author.orcid || null,
    affiliations: (author.affiliations || []).map((a) => a.institution?.display_name).filter(Boolean).slice(0, 5),
    works_count: works.length,
    cited_by_count: works.reduce((s, w) => s + (w.cited_by_count || 0), 0),
    h_index: { value: hIndex, source: "OpenAlex (computed)", computed_at: new Date().toISOString().slice(0, 10) },
    h_index_recent: { value: hIndexRecent, window_years: args.recentYears, source: "OpenAlex (computed)", computed_at: new Date().toISOString().slice(0, 10) },
    h_index_published: author.summary_stats ? { value: author.summary_stats.h_index, source: "OpenAlex (published)" } : null,
    i10_index: author.summary_stats?.i10_index ?? null,
    top_collaborators: collaborators,
    sanity,
    note: "h-index values from S2/OpenAlex/Scholar diverge meaningfully. Always tag the source. Scholar's number is typically highest because it indexes grey literature.",
  };

  process.stdout.write(JSON.stringify(out, null, 2) + "\n");
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(3);
});
