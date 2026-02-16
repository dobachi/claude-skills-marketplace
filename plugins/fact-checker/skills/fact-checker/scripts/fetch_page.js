#!/usr/bin/env node
/**
 * fetch_page.js - Fetch a web page using Puppeteer and save as PDF / extract text.
 *
 * Usage:
 *   node fetch_page.js <url> [options]
 *
 * Options:
 *   --pdf  <path>    Save page as PDF to the given path
 *   --text <path>    Extract visible text and save to the given path
 *   --screenshot <path>  Save a full-page screenshot (PNG)
 *   --timeout <ms>   Navigation timeout in milliseconds (default: 30000)
 *   --wait <ms>      Extra wait after load event (default: 2000)
 *
 * Examples:
 *   node fetch_page.js https://example.com --pdf out.pdf --text out.txt
 *   node fetch_page.js https://example.com --screenshot shot.png --timeout 60000
 *
 * Exit codes:
 *   0  Success
 *   1  Missing arguments / bad usage
 *   2  Navigation or network error
 *   3  File write error
 */

const puppeteer = require("puppeteer");
const path = require("path");
const fs = require("fs");

function parseArgs(argv) {
  const args = { url: null, pdf: null, text: null, screenshot: null, timeout: 30000, wait: 2000 };
  const rest = argv.slice(2);
  let i = 0;
  while (i < rest.length) {
    const a = rest[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      if (["pdf", "text", "screenshot"].includes(key)) {
        args[key] = rest[++i];
      } else if (["timeout", "wait"].includes(key)) {
        args[key] = parseInt(rest[++i], 10);
      }
    } else if (!args.url) {
      args.url = a;
    }
    i++;
  }
  return args;
}

async function fetchPage(args) {
  if (!args.url) {
    console.error("Usage: node fetch_page.js <url> [--pdf path] [--text path] [--screenshot path]");
    process.exit(1);
  }

  if (!args.pdf && !args.text && !args.screenshot) {
    // Default: output text to stdout
    args.text = "-";
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: "new",
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
      ],
    });

    const page = await browser.newPage();

    // Set a realistic user-agent to reduce bot detection
    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    );

    // Set viewport
    await page.setViewport({ width: 1280, height: 900 });

    // Navigate
    await page.goto(args.url, {
      waitUntil: "networkidle2",
      timeout: args.timeout,
    });

    // Extra wait for JS-rendered content
    if (args.wait > 0) {
      await new Promise((r) => setTimeout(r, args.wait));
    }

    // --- PDF ---
    if (args.pdf) {
      const pdfDir = path.dirname(path.resolve(args.pdf));
      fs.mkdirSync(pdfDir, { recursive: true });
      await page.pdf({
        path: args.pdf,
        format: "A4",
        printBackground: true,
        margin: { top: "1cm", right: "1cm", bottom: "1cm", left: "1cm" },
      });
      console.log(`PDF saved: ${args.pdf}`);
    }

    // --- Screenshot ---
    if (args.screenshot) {
      const ssDir = path.dirname(path.resolve(args.screenshot));
      fs.mkdirSync(ssDir, { recursive: true });
      await page.screenshot({ path: args.screenshot, fullPage: true });
      console.log(`Screenshot saved: ${args.screenshot}`);
    }

    // --- Text extraction ---
    if (args.text) {
      const text = await page.evaluate(() => {
        // Remove script/style elements
        const clone = document.cloneNode(true);
        clone.querySelectorAll("script, style, noscript").forEach((el) => el.remove());
        return clone.body ? clone.body.innerText : document.documentElement.innerText;
      });

      if (args.text === "-") {
        process.stdout.write(text);
      } else {
        const txtDir = path.dirname(path.resolve(args.text));
        fs.mkdirSync(txtDir, { recursive: true });
        fs.writeFileSync(args.text, text, "utf-8");
        console.log(`Text saved: ${args.text}`);
      }
    }

    // Print final URL (useful for redirect detection)
    console.error(`Final URL: ${page.url()}`);
  } catch (err) {
    console.error(`Error fetching ${args.url}: ${err.message}`);
    process.exit(2);
  } finally {
    if (browser) await browser.close();
  }
}

const args = parseArgs(process.argv);
fetchPage(args);
