#!/usr/bin/env node
// Drive the --comments page in headless Chrome (puppeteer), both storage paths:
//
//   local  : no window.claude. Pick a status and type a comment on p.2, reload, and both are
//            still there (localStorage); j typed in the comment box does not move the page;
//            the filter shows only commented slides; Export gives the expected Markdown.
//   db     : a fake window.claude whose use("db") resolves a recording store, as an Artifact
//            published with capabilities {db:{}} would. A document already in "reviews" shows
//            up on its slide; a new comment is written to reviews/<spec id> with page and slide.
//
// usage: web_preview_browser.cjs OUT_DIR      (OUT_DIR/index.html built from fixtures/review-deck.yaml)
// exit:  0 all good / 1 a check failed / 2 cannot run (no puppeteer or no Chrome)
'use strict';
const fs = require('fs');
const http = require('http');
const path = require('path');
const { execSync } = require('child_process');

function loadPuppeteer() {
  const tries = ['puppeteer', 'puppeteer-core'];
  let root = '';
  try { root = execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch (e) { /* no npm */ }
  if (process.env.PUPPETEER_PATH) tries.unshift(process.env.PUPPETEER_PATH);
  if (root) tries.push(path.join(root, 'puppeteer'), path.join(root, '@mermaid-js/mermaid-cli/node_modules/puppeteer'));
  for (const t of tries) { try { return require(t); } catch (e) { /* next */ } }
  return null;
}

const out = process.argv[2];
if (!out || !fs.existsSync(path.join(out, 'index.html'))) { console.error('usage: web_preview_browser.cjs OUT_DIR'); process.exit(2); }
const puppeteer = loadPuppeteer();
if (!puppeteer) { console.error('SKIP puppeteer not found'); process.exit(2); }
const chrome = ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find(p => fs.existsSync(p));

const bad = [];
const check = (ok, what) => { if (!ok) bad.push(what); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

const server = http.createServer((req, res) => {
  const p = path.join(out, decodeURIComponent(req.url.split('?')[0].split('#')[0]).replace(/^\/+/, '') || 'index.html');
  fs.readFile(p.endsWith(path.sep) ? path.join(p, 'index.html') : p, (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'content-type': p.endsWith('.html') ? 'text/html; charset=utf-8' : 'image/jpeg' });
    res.end(data);
  });
});

// A stand-in for the Artifact runtime: use("db") resolves a store that records writes and
// delivers one existing document through onSnapshot.
function fakeClaude() {
  const writes = [];
  window.__writes = writes;
  const existing = { id: 'p3', data: () => ({ status: '質問', comment: '既にある指摘', updated: '2026-11-20T01:00:00Z', page: 3, slide: '' }) };
  const db = {
    collection(c) {
      return {
        doc(id) { return { set(body) { writes.push({ c, id, body }); return Promise.resolve(); } }; },
        onSnapshot(next) { setTimeout(() => next({ docs: [existing], metadata: { fromCache: false } }), 50); return () => {}; },
      };
    },
  };
  window.claude = { use: name => Promise.resolve(name === 'db' ? db : null) };
}

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/index.html`;
  let browser;
  try {
    browser = await puppeteer.launch({ headless: true, executablePath: chrome, args: ['--no-sandbox'] });
  } catch (e) { console.error('cannot start Chrome: ' + e.message); server.close(); process.exit(2); }
  try {
    // ---------------- local fallback ----------------
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(url, { waitUntil: 'load' });
    const noteText = await page.$eval('#rvnote', e => e.textContent);
    check(/このブラウザの中だけ/.test(noteText), `local notice missing (got "${noteText}")`);
    const bar = '#s2 .rb';
    await page.click(`${bar} button[data-s="要修正"]`);
    await page.click(`${bar} textarea`);
    const y0 = await page.evaluate(() => scrollY);
    await page.keyboard.type('矢印の向きが逆');
    await page.keyboard.down('Shift'); await page.keyboard.press('Enter'); await page.keyboard.up('Shift');
    await page.keyboard.type('jk 2 行目');
    const y1 = await page.evaluate(() => scrollY);
    check(y0 === y1, `typing j/k in the comment box scrolled the page (${y0} -> ${y1})`);
    check(!/#p/.test(await page.evaluate(() => location.hash)), 'typing j changed the #pN hash');
    await page.click('#s3 .rb button[data-s="OK"]');   // blur the textarea (saves) and mark p.3 OK
    await sleep(900);
    await page.reload({ waitUntil: 'load' });
    const after = await page.evaluate(() => ({
      text: document.querySelector('#s2 .rb textarea').value,
      fix: document.querySelector('#s2 .rb button[data-s="要修正"]').getAttribute('aria-pressed'),
      ok3: document.querySelector('#s3 .rb button[data-s="OK"]').getAttribute('aria-pressed'),
      count: document.querySelector('#rvcount').textContent,
      keys: Object.keys(localStorage).sort(),
    }));
    check(after.text === '矢印の向きが逆\njk 2 行目', `comment did not survive a reload (got ${JSON.stringify(after.text)})`);
    check(after.fix === 'true', 'status 要修正 did not survive a reload');
    check(after.ok3 === 'true', 'status OK on p.3 did not survive a reload');
    check(after.count === '2 / 6 枚に記入', `counter wrong: ${after.count}`);
    check(after.keys.includes('pptx-preview-review:レビュー用の小さなデッキ|intro'), `localStorage key not by title + spec id: ${after.keys}`);
    // keys still work outside the box
    await page.evaluate(() => document.activeElement && document.activeElement.blur());
    await page.keyboard.press('j');
    await sleep(100);
    check(/^#p\d+$/.test(await page.evaluate(() => location.hash)), 'j outside the comment box does not page any more');
    // filter
    await page.select('#rvf', 'has');
    const shown = await page.$$eval('main figure', fs => fs.filter(f => !f.hidden).map(f => f.id));
    check(JSON.stringify(shown) === '["s2","s3"]', `filter "commented" shows ${shown}`);
    await page.select('#rvf', 's:要修正');
    const fix = await page.$$eval('main figure', fs => fs.filter(f => !f.hidden).map(f => f.id));
    check(JSON.stringify(fix) === '["s2"]', `filter by status shows ${fix}`);
    await page.select('#rvf', 'all');
    // export
    await page.click('#rvx');
    await sleep(200);
    const md = await page.$eval('#rvdt', e => e.value);
    const open = await page.$eval('#rvd', e => e.open);
    check(open, 'export dialog did not open');
    for (const want of ['# レビュー用の小さなデッキ — レビューコメント', '<!-- review-labels: OK,要修正,質問 -->',
      '## p.2 背景と問い\n\np2 [intro] 要修正: 矢印の向きが逆\n  jk 2 行目\n', '## p.3 id の無い枚\n\np3 OK\n']) {
      check(md.includes(want), `export lacks ${JSON.stringify(want)}\n--- got ---\n${md}`);
    }
    check(!md.includes('p1 ') && !md.includes('p4 '), 'export lists slides without comments');
    check(errors.length === 0, `page errors: ${errors.join('; ')}`);
    await page.close();

    // ---------------- Artifact db ----------------
    const p2 = await browser.newPage();
    const errs2 = [];
    p2.on('pageerror', e => errs2.push(e.message));
    await p2.evaluateOnNewDocument(fakeClaude);
    await p2.goto(url, { waitUntil: 'load' });
    await sleep(300);
    const s3 = await p2.evaluate(() => ({
      text: document.querySelector('#s3 .rb textarea').value,
      q: document.querySelector('#s3 .rb button[data-s="質問"]').getAttribute('aria-pressed'),
      note: document.querySelector('#rvnote').textContent,
    }));
    check(s3.text === '既にある指摘' && s3.q === 'true', `db document p3 not shown on slide 3: ${JSON.stringify(s3)}`);
    check(/全員に見えます/.test(s3.note), `db notice missing (got "${s3.note}")`);
    await p2.click('#s2 .rb button[data-s="OK"]');
    await p2.click('#s2 .rb textarea');
    await p2.keyboard.type('良い');
    await p2.click('#s1 .rb button[data-s="質問"]');
    await sleep(300);
    const writes = await p2.evaluate(() => window.__writes);
    const last = writes.filter(w => w.id === 'intro').pop();
    check(writes.every(w => w.c === 'reviews'), `writes outside collection "reviews": ${JSON.stringify(writes)}`);
    check(last && last.body.status === 'OK' && last.body.comment === '良い' && last.body.page === 2 && last.body.slide === 'intro',
      `doc reviews/intro not written as expected: ${JSON.stringify(writes)}`);
    check(writes.some(w => w.id === 'cover' && w.body.status === '質問'), 'reviews/cover not written');
    const lsKeys = await p2.evaluate(() => Object.keys(localStorage).filter(k => k.includes('|cover')));
    check(lsKeys.length === 0, 'db mode also wrote to localStorage');
    check(errs2.length === 0, `page errors (db): ${errs2.join('; ')}`);
  } finally {
    await browser.close();
    server.close();
  }
  for (const b of bad) console.log('NG ' + b);
  if (!bad.length) console.log('OK browser: local save survives reload, keys ignored while typing, filter, export, db writes');
  process.exit(bad.length ? 1 : 0);
})().catch(e => { console.error(e); server.close(); process.exit(2); });
