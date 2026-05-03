#!/usr/bin/env node
/**
 * citations.js - Citation chasing and Wohlin-style snowballing via Semantic Scholar.
 *
 * Usage:
 *   node citations.js <DOI|arXiv-ID> [options]
 *
 * Options:
 *   --depth <N>           Max iteration depth (default: 1; for --snowball, max iterations)
 *   --direction <forward|backward|both>   Citation direction (default: both)
 *   --snowball            Iterate Wohlin-style: each accepted paper becomes the next iteration's seed
 *   --saturation-rate <F> Stop when accept-rate falls below F (default: 0.05)
 *   --auto-accept         Accept all candidates without screening (snowball without filter)
 *   --limit <N>           Max papers per direction per iteration (default: 100)
 *
 * Output: JSON graph (nodes + edges) to stdout. See references/snowballing.md for schema.
 *
 * Environment:
 *   LITSEARCH_EMAIL   Email for polite pool
 *   S2_API_KEY        Optional Semantic Scholar API key for higher RPS
 *
 * Examples:
 *   node citations.js 10.48550/arXiv.1706.03762 --depth 1 --direction both
 *   node citations.js 10.48550/arXiv.1706.03762 --snowball --depth 3
 *
 * Exit codes:
 *   0  Success
 *   1  Bad usage
 *   2  Seed paper not found
 *   3  All API calls failed
 */

const EMAIL = process.env.LITSEARCH_EMAIL || "anonymous@example.com";
const S2_KEY = process.env.S2_API_KEY || null;
const UA = `literature-search-skill/1.0 (mailto:${EMAIL})`;
const S2_BASE = "https://api.semanticscholar.org/graph/v1";

function parseArgs(argv) {
  const args = {
    seed: null,
    depth: 1,
    direction: "both",
    snowball: false,
    saturationRate: 0.05,
    autoAccept: false,
    limit: 100,
  };
  const rest = argv.slice(2);
  const positional = [];
  let i = 0;
  while (i < rest.length) {
    const a = rest[i];
    if (a === "--help" || a === "-h") { printHelp(); process.exit(0); }
    else if (a === "--depth") args.depth = parseInt(rest[++i], 10);
    else if (a === "--direction") args.direction = rest[++i];
    else if (a === "--snowball") args.snowball = true;
    else if (a === "--saturation-rate") args.saturationRate = parseFloat(rest[++i]);
    else if (a === "--auto-accept") args.autoAccept = true;
    else if (a === "--limit") args.limit = parseInt(rest[++i], 10);
    else if (a.startsWith("--")) { console.error(`Unknown option: ${a}`); process.exit(1); }
    else positional.push(a);
    i++;
  }
  args.seed = positional[0] || null;
  if (!args.seed) { printHelp(); process.exit(1); }
  if (!["forward", "backward", "both"].includes(args.direction)) {
    console.error(`--direction must be forward|backward|both`);
    process.exit(1);
  }
  return args;
}

function printHelp() {
  console.error(`Usage: node citations.js <DOI|arXiv-ID> [--depth N] [--direction forward|backward|both] [--snowball] [--saturation-rate 0.05] [--auto-accept] [--limit N]`);
}

function s2Headers() {
  const h = { "User-Agent": UA };
  if (S2_KEY) h["x-api-key"] = S2_KEY;
  return h;
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

function resolveSeedId(seed) {
  // S2 accepts: paperId, DOI, arXiv ID, etc. Use prefixed forms for clarity.
  const s = seed.trim();
  if (/^10\./.test(s)) return `DOI:${s}`;
  if (/^arxiv:/i.test(s)) return s;
  if (/^\d{4}\.\d{4,5}/.test(s)) return `arXiv:${s}`;
  if (/^[a-f0-9]{40}$/i.test(s)) return s; // S2 paperId hash
  return s;
}

async function fetchPaper(id) {
  const fields = "paperId,title,authors,year,venue,externalIds,citationCount,influentialCitationCount,openAccessPdf,abstract,tldr";
  const url = `${S2_BASE}/paper/${encodeURIComponent(id)}?fields=${fields}`;
  const resp = await fetchWithBackoff(url, { headers: s2Headers() });
  return await resp.json();
}

async function fetchCitations(id, limit) {
  const fields = "paperId,title,authors,year,venue,externalIds,citationCount,influentialCitationCount,openAccessPdf";
  const url = `${S2_BASE}/paper/${encodeURIComponent(id)}/citations?fields=${fields}&limit=${Math.min(limit, 1000)}`;
  const resp = await fetchWithBackoff(url, { headers: s2Headers() });
  const json = await resp.json();
  return (json.data || []).map((d) => d.citingPaper).filter(Boolean);
}

async function fetchReferences(id, limit) {
  const fields = "paperId,title,authors,year,venue,externalIds,citationCount,influentialCitationCount,openAccessPdf";
  const url = `${S2_BASE}/paper/${encodeURIComponent(id)}/references?fields=${fields}&limit=${Math.min(limit, 1000)}`;
  const resp = await fetchWithBackoff(url, { headers: s2Headers() });
  const json = await resp.json();
  return (json.data || []).map((d) => d.citedPaper).filter(Boolean);
}

function normalize(p) {
  if (!p) return null;
  const doi = p.externalIds?.DOI ? p.externalIds.DOI.toLowerCase() : null;
  const arxiv = p.externalIds?.ArXiv || null;
  return {
    s2_paper_id: p.paperId,
    doi,
    arxiv,
    title: p.title || null,
    authors: (p.authors || []).map((a) => a.name).filter(Boolean),
    year: p.year || null,
    venue: p.venue || null,
    citations: p.citationCount ?? null,
    influential_citations: p.influentialCitationCount ?? null,
    oa_url: p.openAccessPdf?.url || null,
  };
}

function nodeKey(p) {
  if (p.doi) return `doi:${p.doi}`;
  if (p.arxiv) return `arxiv:${p.arxiv}`;
  if (p.s2_paper_id) return `s2:${p.s2_paper_id}`;
  return `title:${(p.title || "").toLowerCase().replace(/\W+/g, "")}`;
}

async function main() {
  const args = parseArgs(process.argv);
  console.error(`[info] seed=${args.seed} direction=${args.direction} depth=${args.depth} snowball=${args.snowball}`);

  const seedId = resolveSeedId(args.seed);
  let seedPaper;
  try {
    seedPaper = await fetchPaper(seedId);
  } catch (e) {
    console.error(`[error] cannot resolve seed: ${e.message}`);
    process.exit(2);
  }

  const seedNorm = normalize(seedPaper);
  if (!seedNorm) {
    console.error(`[error] seed paper not found`);
    process.exit(2);
  }

  const nodes = new Map();
  const edges = [];
  const stats = { total_screened: 0, total_accepted: 1, by_iteration: [] };

  const seedNode = { ...seedNorm, depth: 0, accepted: true, added_in_iteration: 0, source: ["S2"] };
  nodes.set(nodeKey(seedNorm), seedNode);
  stats.by_iteration.push({ i: 0, screened: 0, accepted: 1, accept_rate: null, new_papers: 1 });

  let currentSeeds = [{ id: seedNorm.s2_paper_id || seedId, paper: seedNorm }];
  let saturationReached = false;
  let saturationIteration = null;

  for (let iter = 1; iter <= args.depth; iter++) {
    let screened = 0;
    let accepted = 0;
    let newPapers = 0;
    const nextSeeds = [];

    console.error(`[info] iteration ${iter} of ${args.depth} — ${currentSeeds.length} seeds`);

    for (const { id, paper } of currentSeeds) {
      let candidates = [];
      try {
        if (args.direction === "forward" || args.direction === "both") {
          const fwd = await fetchCitations(id, args.limit);
          for (const c of fwd) {
            const n = normalize(c);
            if (n) candidates.push({ direction: "forward", paper: n, parent: id });
          }
        }
        if (args.direction === "backward" || args.direction === "both") {
          const bwd = await fetchReferences(id, args.limit);
          for (const r of bwd) {
            const n = normalize(r);
            if (n) candidates.push({ direction: "backward", paper: n, parent: id });
          }
        }
      } catch (e) {
        console.error(`[warn] iteration ${iter} seed ${id}: ${e.message}`);
      }

      for (const c of candidates) {
        screened++;
        const k = nodeKey(c.paper);
        const existing = nodes.get(k);
        const isNew = !existing;

        // Decision: accept?
        // Snowball mode: accept if --auto-accept; else only seeds added are accepted by external screening
        // Non-snowball: every reachable paper is added to the graph (no further iteration)
        const acceptIntoSeeds = args.snowball && args.autoAccept;

        if (isNew) {
          newPapers++;
          accepted++;
          nodes.set(k, { ...c.paper, depth: iter, accepted: true, added_in_iteration: iter, source: ["S2"], from_direction: c.direction });
        } else {
          // Re-encountered; not new
        }

        // Add edge (avoid dup)
        const fromKey = c.direction === "forward" ? k : nodeKey(paper);
        const toKey = c.direction === "forward" ? nodeKey(paper) : k;
        edges.push({ from: fromKey, to: toKey, direction: c.direction, iteration: iter });

        if (isNew && acceptIntoSeeds) {
          nextSeeds.push({ id: c.paper.s2_paper_id || (c.paper.doi ? `DOI:${c.paper.doi}` : null), paper: c.paper });
        }
      }
    }

    const acceptRate = screened > 0 ? newPapers / screened : 0;
    stats.total_screened += screened;
    stats.total_accepted += newPapers;
    stats.by_iteration.push({ i: iter, screened, accepted: newPapers, accept_rate: acceptRate, new_papers: newPapers });

    console.error(`[info] iteration ${iter}: screened=${screened} new=${newPapers} accept_rate=${acceptRate.toFixed(3)}`);

    if (!args.snowball) break; // single hop; done
    if (newPapers === 0) {
      saturationReached = true;
      saturationIteration = iter;
      break;
    }
    if (acceptRate < args.saturationRate) {
      saturationReached = true;
      saturationIteration = iter;
      break;
    }
    currentSeeds = nextSeeds.filter((s) => s.id);
    if (currentSeeds.length === 0) break;
  }

  const out = {
    seed: args.seed,
    config: { depth: args.depth, direction: args.direction, snowball: args.snowball, saturation_rate: args.saturationRate, auto_accept: args.autoAccept, limit: args.limit },
    iterations: stats.by_iteration.length - 1,
    saturation_reached: saturationReached,
    saturation_iteration: saturationIteration,
    stats,
    nodes: Array.from(nodes.values()),
    edges,
  };
  process.stdout.write(JSON.stringify(out, null, 2) + "\n");
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(3);
});
