#!/usr/bin/env node
/**
 * bibtex.js - Fetch canonical BibTeX via CrossRef content negotiation.
 *
 * Usage:
 *   node bibtex.js <DOI>           # Single DOI
 *   echo "<doi1>\n<doi2>" | node bibtex.js -    # Batch via stdin (one DOI per line)
 *
 * Output: BibTeX entries to stdout (concatenated for batch input).
 *         Errors per-DOI written to stderr; entry omitted from stdout.
 *
 * Environment:
 *   LITSEARCH_EMAIL   Email for CrossRef polite pool
 *
 * Examples:
 *   node bibtex.js 10.48550/arXiv.1706.03762
 *   cat dois.txt | node bibtex.js -
 *
 * Exit codes:
 *   0  Success (at least one entry returned)
 *   1  Bad usage
 *   2  All DOIs failed
 */

const EMAIL = process.env.LITSEARCH_EMAIL || "anonymous@example.com";
const UA = `literature-search-skill/1.0 (mailto:${EMAIL})`;

function parseArgs(argv) {
  const rest = argv.slice(2);
  if (rest.length === 0 || rest[0] === "--help" || rest[0] === "-h") { printHelp(); process.exit(rest.length === 0 ? 1 : 0); }
  return { doi: rest[0] };
}

function printHelp() {
  console.error(`Usage:`);
  console.error(`  node bibtex.js <DOI>`);
  console.error(`  cat dois.txt | node bibtex.js -    (batch via stdin, one DOI per line)`);
}

async function fetchBibtex(doi) {
  // Strip URL prefix if present
  const clean = doi.replace(/^https?:\/\/(dx\.)?doi\.org\//i, "").trim();
  if (!clean) throw new Error("empty DOI");
  const url = `https://doi.org/${encodeURI(clean)}`;
  const resp = await fetch(url, {
    headers: { "Accept": "application/x-bibtex; charset=utf-8", "User-Agent": UA },
    redirect: "follow",
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const text = await resp.text();
  if (!text.trim().startsWith("@")) throw new Error("response not BibTeX");
  return text.trim();
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

  let successCount = 0;
  for (const doi of dois) {
    try {
      const bib = await fetchBibtex(doi);
      process.stdout.write(bib + "\n\n");
      successCount++;
    } catch (e) {
      console.error(`[error] ${doi}: ${e.message}`);
    }
  }
  console.error(`[info] ${successCount} of ${dois.length} BibTeX entries retrieved`);
  if (successCount === 0) process.exit(2);
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(2);
});
