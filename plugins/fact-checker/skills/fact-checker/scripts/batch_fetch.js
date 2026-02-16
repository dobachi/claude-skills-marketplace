#!/usr/bin/env node
/**
 * batch_fetch.js - Fetch multiple URLs in parallel using Puppeteer.
 *
 * Reads a JSON manifest from stdin or a file and fetches each URL,
 * saving PDFs and/or text to the specified output directory.
 *
 * Usage:
 *   node batch_fetch.js <manifest.json> [options]
 *   echo '<json>' | node batch_fetch.js - [options]
 *
 * Manifest format (JSON):
 *   {
 *     "urls": [
 *       { "url": "https://...", "id": "claim-1" },
 *       { "url": "https://...", "id": "ref-2" }
 *     ]
 *   }
 *
 * Options:
 *   --outdir <dir>       Output directory (default: ./fact-check-output)
 *   --concurrency <n>    Max parallel browser pages (default: 4)
 *   --pdf                Save each page as PDF
 *   --text               Extract text from each page
 *   --screenshot         Save full-page screenshot of each page
 *   --timeout <ms>       Navigation timeout per page (default: 30000)
 *   --wait <ms>          Extra wait after load (default: 2000)
 *
 * Output:
 *   Writes a results.json to outdir with per-URL status.
 *
 * Exit codes:
 *   0  All URLs fetched (some may have individual errors)
 *   1  Bad usage / manifest parse error
 */

const puppeteer = require("puppeteer");
const path = require("path");
const fs = require("fs");

function parseArgs(argv) {
  const opts = {
    manifest: null,
    outdir: "./fact-check-output",
    concurrency: 4,
    pdf: false,
    text: false,
    screenshot: false,
    timeout: 30000,
    wait: 2000,
  };
  const rest = argv.slice(2);
  let i = 0;
  while (i < rest.length) {
    const a = rest[i];
    if (a === "--outdir") opts.outdir = rest[++i];
    else if (a === "--concurrency") opts.concurrency = parseInt(rest[++i], 10);
    else if (a === "--pdf") opts.pdf = true;
    else if (a === "--text") opts.text = true;
    else if (a === "--screenshot") opts.screenshot = true;
    else if (a === "--timeout") opts.timeout = parseInt(rest[++i], 10);
    else if (a === "--wait") opts.wait = parseInt(rest[++i], 10);
    else if (!opts.manifest) opts.manifest = a;
    i++;
  }
  if (!opts.pdf && !opts.text && !opts.screenshot) {
    opts.pdf = true;
    opts.text = true;
  }
  return opts;
}

async function readManifest(manifestPath) {
  let raw;
  if (manifestPath === "-") {
    raw = fs.readFileSync(0, "utf-8"); // stdin
  } else {
    raw = fs.readFileSync(manifestPath, "utf-8");
  }
  return JSON.parse(raw);
}

async function fetchOne(page, entry, opts) {
  const result = { id: entry.id, url: entry.url, status: "ok", files: {}, error: null, finalUrl: null };
  const safeId = entry.id.replace(/[^a-zA-Z0-9_-]/g, "_");

  try {
    await page.goto(entry.url, { waitUntil: "networkidle2", timeout: opts.timeout });
    if (opts.wait > 0) await new Promise((r) => setTimeout(r, opts.wait));
    result.finalUrl = page.url();

    if (opts.pdf) {
      const pdfPath = path.join(opts.outdir, `${safeId}.pdf`);
      await page.pdf({
        path: pdfPath,
        format: "A4",
        printBackground: true,
        margin: { top: "1cm", right: "1cm", bottom: "1cm", left: "1cm" },
      });
      result.files.pdf = pdfPath;
    }

    if (opts.screenshot) {
      const ssPath = path.join(opts.outdir, `${safeId}.png`);
      await page.screenshot({ path: ssPath, fullPage: true });
      result.files.screenshot = ssPath;
    }

    if (opts.text) {
      const text = await page.evaluate(() => {
        const clone = document.cloneNode(true);
        clone.querySelectorAll("script, style, noscript").forEach((el) => el.remove());
        return clone.body ? clone.body.innerText : document.documentElement.innerText;
      });
      const txtPath = path.join(opts.outdir, `${safeId}.txt`);
      fs.writeFileSync(txtPath, text, "utf-8");
      result.files.text = txtPath;
    }
  } catch (err) {
    result.status = "error";
    result.error = err.message;
  }
  return result;
}

async function main() {
  const opts = parseArgs(process.argv);
  if (!opts.manifest) {
    console.error("Usage: node batch_fetch.js <manifest.json|-> [options]");
    process.exit(1);
  }

  let manifest;
  try {
    manifest = await readManifest(opts.manifest);
  } catch (err) {
    console.error(`Failed to read manifest: ${err.message}`);
    process.exit(1);
  }

  if (!manifest.urls || !Array.isArray(manifest.urls)) {
    console.error('Manifest must contain a "urls" array.');
    process.exit(1);
  }

  fs.mkdirSync(opts.outdir, { recursive: true });

  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
  });

  const results = [];
  const queue = [...manifest.urls];

  // Process in batches of concurrency
  async function worker() {
    while (queue.length > 0) {
      const entry = queue.shift();
      if (!entry) break;
      const page = await browser.newPage();
      await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      );
      await page.setViewport({ width: 1280, height: 900 });

      console.error(`Fetching [${entry.id}]: ${entry.url}`);
      const result = await fetchOne(page, entry, opts);
      results.push(result);
      console.error(`  -> ${result.status}${result.error ? ": " + result.error : ""}`);

      await page.close();
    }
  }

  // Launch concurrent workers
  const workers = [];
  for (let w = 0; w < opts.concurrency; w++) {
    workers.push(worker());
  }
  await Promise.all(workers);

  await browser.close();

  // Write results manifest
  const resultsPath = path.join(opts.outdir, "results.json");
  fs.writeFileSync(resultsPath, JSON.stringify({ results }, null, 2), "utf-8");
  console.log(`Results written to ${resultsPath}`);

  // Summary
  const ok = results.filter((r) => r.status === "ok").length;
  const fail = results.filter((r) => r.status === "error").length;
  console.log(`Done: ${ok} succeeded, ${fail} failed out of ${results.length} URLs.`);
}

main();
