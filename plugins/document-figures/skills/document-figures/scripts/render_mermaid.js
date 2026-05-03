#!/usr/bin/env node
/**
 * render_mermaid.js — Rasterize a Mermaid diagram to PNG or SVG via Puppeteer.
 *
 * Loads assets/mermaid_template.html, injects the Mermaid source, waits for render,
 * and writes the result to a file.
 *
 * Default behavior is to emit Mermaid text only — only call this script when a
 * downstream consumer requires PNG/SVG (e.g., embedding in a .pptx).
 *
 * Usage:
 *   node render_mermaid.js <mmd-file> [--out FILE] [--format png|svg] [--theme default|dark|forest|neutral]
 *   echo "flowchart LR; A-->B" | node render_mermaid.js - [--out FILE] [--format png|svg]
 *
 * Output:
 *   <out> file (PNG or SVG). Default: <input>.png
 *
 * Requirements:
 *   - Node.js 18+
 *   - puppeteer (npm install puppeteer)
 *   - assets/mermaid_template.html (sibling assets/ directory; uses CDN by default)
 *
 * Exit codes:
 *   0  success
 *   1  bad usage
 *   2  runtime failure
 */

const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const rest = argv.slice(2);
  if (rest.length === 0 || rest[0] === "-h" || rest[0] === "--help") {
    printHelp();
    process.exit(rest.length === 0 ? 1 : 0);
  }
  const args = { input: null, out: null, format: "png", theme: "default", timeout: 15000 };
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--out") args.out = rest[++i];
    else if (a === "--format") args.format = rest[++i];
    else if (a === "--theme") args.theme = rest[++i];
    else if (a === "--timeout") args.timeout = parseInt(rest[++i], 10);
    else if (a.startsWith("-") && a !== "-") { console.error(`[error] unknown option: ${a}`); process.exit(1); }
    else if (!args.input) args.input = a;
    else { console.error(`[error] extra arg: ${a}`); process.exit(1); }
  }
  if (!args.input) { console.error("[error] input required (file path or - for stdin)"); process.exit(1); }
  if (!["png", "svg"].includes(args.format)) { console.error("[error] --format must be png or svg"); process.exit(1); }
  return args;
}

function printHelp() {
  console.error(`Usage: node render_mermaid.js <mmd-file|->  [options]
  --out FILE       Output file path (default: <input>.<format>)
  --format FMT     png | svg (default: png)
  --theme NAME     default | dark | forest | neutral (default: default)
  --timeout MS     Render timeout (default: 15000)
  -h, --help       Show this help

Read from stdin: pass - as the input.`);
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

  let source;
  if (args.input === "-") {
    source = await readStdin();
  } else {
    if (!fs.existsSync(args.input)) { console.error(`[error] input not found: ${args.input}`); process.exit(2); }
    source = fs.readFileSync(args.input, "utf8");
  }
  source = source.trim();
  if (!source) { console.error("[error] empty Mermaid source"); process.exit(2); }

  if (!args.out) {
    const baseName = args.input === "-" ? "diagram" : args.input.replace(/\.mmd$/i, "");
    args.out = `${baseName}.${args.format}`;
  }

  let puppeteer;
  try { puppeteer = require("puppeteer"); }
  catch (e) {
    console.error("[error] puppeteer not installed. Run: npm install puppeteer");
    process.exit(2);
  }

  const templatePath = path.join(__dirname, "..", "assets", "mermaid_template.html");
  if (!fs.existsSync(templatePath)) {
    console.error(`[error] template not found: ${templatePath}`);
    process.exit(2);
  }

  const browser = await puppeteer.launch({
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: "new",
  });

  try {
    const page = await browser.newPage();
    const templateUrl = "file://" + path.resolve(templatePath);
    await page.goto(templateUrl, { waitUntil: "networkidle0", timeout: args.timeout });

    // Inject the Mermaid source and theme, then wait for render.
    const rendered = await page.evaluate(async (src, theme, timeoutMs) => {
      // Wait for mermaid global from CDN
      const start = Date.now();
      while (typeof window.mermaid === "undefined") {
        if (Date.now() - start > timeoutMs) throw new Error("mermaid library did not load (CDN unreachable?)");
        await new Promise((r) => setTimeout(r, 100));
      }
      window.mermaid.initialize({ startOnLoad: false, theme });
      const container = document.getElementById("container");
      container.innerHTML = "";
      const id = "diagram-" + Math.random().toString(36).slice(2);
      try {
        const { svg } = await window.mermaid.render(id, src);
        container.innerHTML = svg;
        return { ok: true, svg };
      } catch (e) {
        return { ok: false, error: String(e) };
      }
    }, source, args.theme, args.timeout);

    if (!rendered.ok) {
      console.error(`[error] mermaid render failed: ${rendered.error}`);
      process.exit(2);
    }

    if (args.format === "svg") {
      fs.writeFileSync(args.out, rendered.svg);
    } else {
      // Crop to the diagram's bounding box.
      const elem = await page.$("#container svg");
      if (!elem) { console.error("[error] rendered SVG element not found"); process.exit(2); }
      await elem.screenshot({ path: args.out, omitBackground: true });
    }
  } finally {
    await browser.close().catch(() => {});
  }

  console.error(`[info] rendered: ${args.out}`);
  process.stdout.write(args.out + "\n");
}

main().catch((e) => {
  console.error(`[fatal] ${e.message}`);
  process.exit(2);
});
