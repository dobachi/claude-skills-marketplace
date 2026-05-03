#!/usr/bin/env node
/**
 * retract_check.js - Check DOIs for retraction status via CrossRef (Retraction Watch dataset).
 *
 * Cross-references DOIs against CrossRef's /works/{doi} endpoint, which surfaces
 * retraction status via the `update-to[]` field (Retraction Watch dataset has been
 * CC-licensed and distributed via CrossRef since June 2023).
 *
 * Usage:
 *   node retract_check.js <DOI>
 *   echo "<doi1>\n<doi2>" | node retract_check.js -    (batch via stdin)
 *
 * Output: JSON array (single DOI: object) with per-DOI status:
 *   {doi, status, update_type, update_doi, update_date, source}
 *   status ∈ active | retracted | withdrawn | corrected | expression-of-concern | not-found | error
 *
 * Environment:
 *   LITSEARCH_EMAIL   Email for CrossRef polite pool
 *
 * Examples:
 *   node retract_check.js 10.1234/example
 *   cat dois.txt | node retract_check.js -
 *
 * Exit codes:
 *   0  Success (status determined for all DOIs, regardless of value)
 *   1  Bad usage
 *   2  All lookups failed
 */

const EMAIL = process.env.LITSEARCH_EMAIL || "anonymous@example.com";
const UA = `literature-search-skill/1.0 (mailto:${EMAIL})`;
const CR_BASE = "https://api.crossref.org";

function parseArgs(argv) {
  const rest = argv.slice(2);
  if (rest.length === 0 || rest[0] === "--help" || rest[0] === "-h") { printHelp(); process.exit(rest.length === 0 ? 1 : 0); }
  return { doi: rest[0] };
}

function printHelp() {
  console.error(`Usage:`);
  console.error(`  node retract_check.js <DOI>`);
  console.error(`  cat dois.txt | node retract_check.js -`);
}

async function fetchWithBackoff(url, options = {}, maxRetries = 3) {
  let attempt = 0;
  while (true) {
    const resp = await fetch(url, options);
    if (resp.status === 429 || resp.status >= 500) {
      if (attempt >= maxRetries) throw new Error(`HTTP ${resp.status} after ${maxRetries} retries`);
      await new Promise((r) => setTimeout(r, 2000 * Math.pow(2, attempt)));
      attempt++;
      continue;
    }
    return resp;
  }
}

async function checkDoi(doi) {
  const clean = doi.replace(/^https?:\/\/(dx\.)?doi\.org\//i, "").trim();
  if (!clean) return { doi, status: "error", error: "empty DOI" };
  const url = `${CR_BASE}/works/${encodeURIComponent(clean)}?mailto=${EMAIL}`;
  try {
    const resp = await fetchWithBackoff(url, { headers: { "User-Agent": UA, "Accept": "application/json" } });
    if (resp.status === 404) return { doi: clean, status: "not-found" };
    if (!resp.ok) return { doi: clean, status: "error", error: `HTTP ${resp.status}` };
    const json = await resp.json();
    const msg = json.message || {};
    const updates = msg["update-to"] || [];
    if (updates.length === 0) {
      return { doi: clean, status: "active", source: "CrossRef" };
    }
    // Pick the most severe update type if multiple
    const severity = { "retraction": 5, "withdrawal": 4, "expression_of_concern": 3, "removal": 4, "correction": 1, "addendum": 0 };
    let chosen = updates[0];
    for (const u of updates) {
      if ((severity[u.type] || 0) > (severity[chosen.type] || 0)) chosen = u;
    }
    const statusMap = { "retraction": "retracted", "withdrawal": "withdrawn", "removal": "withdrawn", "expression_of_concern": "expression-of-concern", "correction": "corrected", "addendum": "active" };
    return {
      doi: clean,
      status: statusMap[chosen.type] || "active",
      update_type: chosen.type,
      update_doi: chosen.DOI || null,
      update_date: chosen.updated?.["date-time"] || chosen.updated?.["date-parts"]?.[0]?.join("-") || null,
      source: "CrossRef (Retraction Watch dataset)",
    };
  } catch (e) {
    return { doi: clean, status: "error", error: e.message };
  }
}

async function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => { data += chunk; });
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

async function main() {
  const args = parseArgs(process.argv);

  let dois = [];
  if (args.doi === "-") {
    const stdin = await readStdin();
    dois = stdin.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  } else {
    dois = [args.doi];
  }

  const results = [];
  let okCount = 0;
  for (const doi of dois) {
    const r = await checkDoi(doi);
    results.push(r);
    if (r.status !== "error") okCount++;
    if (r.status === "retracted" || r.status === "withdrawn") {
      console.error(`[FLAG] ${r.doi}: ${r.status} (${r.update_date || "date unknown"})`);
    }
  }

  console.error(`[info] checked ${dois.length} DOI(s); ${okCount} succeeded`);
  const out = dois.length === 1 ? results[0] : results;
  process.stdout.write(JSON.stringify(out, null, 2) + "\n");
  if (okCount === 0) process.exit(2);
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(2);
});
