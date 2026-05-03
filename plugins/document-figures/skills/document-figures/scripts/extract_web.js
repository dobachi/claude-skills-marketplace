#!/usr/bin/env node
/**
 * extract_web.js — Extract figures from a web page via Puppeteer.
 *
 * Walks the DOM for <img> and <figure>, captures alt-text and <figcaption>,
 * resolves srcset to the largest variant, downloads each image, and emits
 * manifest.json with provenance. Optional --include-screenshot adds a
 * full-page PNG.
 *
 * Usage:
 *   node extract_web.js <url> [--out DIR] [--include-screenshot] [--min-px 200]
 *                              [--timeout 30000] [--wait-until networkidle2|load|domcontentloaded]
 *
 * Output:
 *   <out>/figures/<filename>      downloaded images
 *   <out>/screenshot.png          (optional) full-page screenshot
 *   <out>/manifest.json           per-figure metadata
 *
 * Requirements:
 *   - Node.js 18+ (built-in fetch)
 *   - puppeteer (npm install puppeteer)
 *
 * Environment:
 *   LITSEARCH_EMAIL    Email for polite User-Agent (shared with literature-search)
 *
 * Exit codes:
 *   0  success
 *   1  bad usage
 *   2  runtime failure
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const EMAIL = process.env.LITSEARCH_EMAIL || "anonymous@example.com";
const UA = `document-figures-skill/1.0 (mailto:${EMAIL})`;

function parseArgs(argv) {
  const rest = argv.slice(2);
  if (rest.length === 0 || rest[0] === "-h" || rest[0] === "--help") {
    printHelp();
    process.exit(rest.length === 0 ? 1 : 0);
  }
  const args = { url: null, out: "./out_web", screenshot: false, minPx: 200, timeout: 30000, waitUntil: "networkidle2" };
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--out") args.out = rest[++i];
    else if (a === "--include-screenshot") args.screenshot = true;
    else if (a === "--min-px") args.minPx = parseInt(rest[++i], 10);
    else if (a === "--timeout") args.timeout = parseInt(rest[++i], 10);
    else if (a === "--wait-until") args.waitUntil = rest[++i];
    else if (a.startsWith("-")) { console.error(`[error] unknown option: ${a}`); process.exit(1); }
    else if (!args.url) args.url = a;
    else { console.error(`[error] extra arg: ${a}`); process.exit(1); }
  }
  if (!args.url) { console.error("[error] URL required"); process.exit(1); }
  return args;
}

function printHelp() {
  console.error(`Usage: node extract_web.js <url> [options]
  --out DIR              Output directory (default: ./out_web)
  --include-screenshot   Also save full-page PNG
  --min-px N             Drop images smaller than NxN (default: 200)
  --timeout MS           Page load timeout (default: 30000)
  --wait-until EVENT     networkidle2 | load | domcontentloaded (default: networkidle2)
  -h, --help             Show this help`);
}

function sha256File(filePath) {
  const buf = fs.readFileSync(filePath);
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function safeBasename(url, fallbackIdx) {
  try {
    const u = new URL(url);
    const last = u.pathname.split("/").filter(Boolean).pop() || `image-${fallbackIdx}`;
    // Strip query strings; ensure extension
    const clean = last.split("?")[0].split("#")[0];
    if (/\.[a-zA-Z0-9]{1,5}$/.test(clean)) return clean;
    return `${clean}-${fallbackIdx}.bin`;
  } catch {
    return `image-${fallbackIdx}.bin`;
  }
}

async function downloadImage(url, dest) {
  const resp = await fetch(url, { headers: { "User-Agent": UA, "Accept": "image/*,*/*;q=0.8" }, redirect: "follow" });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const ab = await resp.arrayBuffer();
  fs.writeFileSync(dest, Buffer.from(ab));
}

async function main() {
  const args = parseArgs(process.argv);

  let puppeteer;
  try { puppeteer = require("puppeteer"); }
  catch (e) {
    console.error("[error] puppeteer not installed. Run: npm install puppeteer");
    process.exit(2);
  }

  fs.mkdirSync(path.join(args.out, "figures"), { recursive: true });

  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: "new",
  });

  let figures = [];
  let pageErr = null;
  try {
    const page = await browser.newPage();
    await page.setUserAgent(UA);
    await page.goto(args.url, { waitUntil: args.waitUntil, timeout: args.timeout });

    // Encourage lazy-loaded images to materialize
    await page.evaluate(async () => {
      await new Promise((resolve) => {
        let total = 0;
        const step = 400;
        const timer = setInterval(() => {
          window.scrollBy(0, step);
          total += step;
          if (total >= document.body.scrollHeight) { clearInterval(timer); resolve(); }
        }, 100);
      });
    });

    figures = await page.evaluate(() => {
      const out = [];
      const imgs = Array.from(document.querySelectorAll("img"));
      imgs.forEach((img, i) => {
        const fig = img.closest("figure");
        const cap = fig?.querySelector("figcaption")?.textContent?.trim() || null;
        const src = img.currentSrc || img.src;
        out.push({
          index: i,
          src: src ? new URL(src, document.baseURI).href : null,
          alt: img.alt || null,
          caption: cap,
          width: img.naturalWidth || 0,
          height: img.naturalHeight || 0,
        });
      });
      return out;
    });

    if (args.screenshot) {
      const shotPath = path.join(args.out, "screenshot.png");
      await page.screenshot({ path: shotPath, fullPage: true });
      console.error(`[info] screenshot: ${shotPath}`);
    }
  } catch (e) {
    pageErr = e;
  } finally {
    await browser.close().catch(() => {});
  }

  if (pageErr) {
    console.error(`[error] page load failed: ${pageErr.message}`);
    process.exit(2);
  }

  // Filter, download, build manifest
  const out = [];
  let okCount = 0;
  for (let i = 0; i < figures.length; i++) {
    const f = figures[i];
    if (!f.src) continue;
    if (args.minPx > 0 && (f.width < args.minPx || f.height < args.minPx)) continue;
    const id = `F-${String(out.length + 1).padStart(2, "0")}`;
    const fname = `${id}-${safeBasename(f.src, i)}`;
    const dest = path.join(args.out, "figures", fname);
    let sha = "";
    try {
      await downloadImage(f.src, dest);
      sha = sha256File(dest);
      okCount++;
    } catch (e) {
      console.error(`[warn] download failed for ${f.src}: ${e.message}`);
      continue;
    }
    let confidence = "none";
    let caption = null;
    if (f.caption) { caption = f.caption; confidence = "recovered"; }
    else if (f.alt) { caption = f.alt; confidence = "recovered"; }

    out.push({
      id,
      origin: "Extracted",
      file: `figures/${fname}`,
      source_reference: `${args.url}, fig.${out.length + 1}`,
      source_url: args.url,
      image_url: f.src,
      caption,
      caption_confidence: confidence,
      alt_text: f.alt,
      linked_claim: [],
      sha256: sha,
      width: f.width,
      height: f.height,
    });
  }

  const manifest = {
    source: args.url,
    source_format: "html",
    extracted_at: new Date().toISOString(),
    figures: out,
  };
  const manifestPath = path.join(args.out, "manifest.json");
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + "\n");

  console.error(`[info] downloaded ${okCount} of ${figures.length} candidate image(s)`);
  console.error(`[info] manifest: ${manifestPath}`);
  process.stdout.write(manifestPath + "\n");
  if (out.length === 0 && !args.screenshot) process.exit(2);
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(2);
});
