#!/usr/bin/env node
"use strict";
/*
 * build_deck.js — Generate a clean, white-based .pptx that does not look AI-made.
 *
 * Engine: PptxGenJS (the same library used in this user's own decks).
 *
 * Design tenets (see references/anti-band-design.md):
 *   - Grid-first. Every coordinate comes from ONE grid computed once, so edges
 *     line up across the whole deck and nothing drifts.
 *   - NO per-slide full-width band. Any accent (a short hairline) lives on the
 *     Slide MASTER, so it is identical on every slide by construction — it
 *     cannot drift. Masters are the only place chrome lives.
 *   - White background, dark ink, exactly one restrained accent.
 *   - "Template" = a swappable JS theme module (palette + fonts + master), not a
 *     binary .potx. See themes/minimal-white.js and references/template-mode.md.
 *
 * Usage:
 *   node build_deck.js SPEC.yaml -o out.pptx
 *   node build_deck.js SPEC.json -o out.pptx --theme themes/brand-example.js
 */
const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const a = { theme: path.join(__dirname, "themes", "minimal-white.js") };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "-o" || t === "--out") a.out = argv[++i];
    else if (t === "--theme") a.theme = argv[++i];
    else if (!a.spec) a.spec = t;
  }
  if (!a.spec || !a.out) {
    console.error("usage: node build_deck.js SPEC.{yaml,json} -o out.pptx [--theme themes/x.js]");
    process.exit(2);
  }
  return a;
}

function loadSpec(p) {
  const raw = fs.readFileSync(p, "utf8");
  if (/\.ya?ml$/i.test(p)) return require("js-yaml").load(raw);
  return JSON.parse(raw);
}

// ---------------------------------------------------------------------------
// Theme + meta overrides. meta.* in the spec tweaks the theme without editing it.
// ---------------------------------------------------------------------------
function loadTheme(p) {
  // shallow-clone so meta overrides don't mutate the cached module
  const t = require(path.resolve(p));
  return { ...t, color: { ...t.color }, font: { ...t.font }, grid: { ...t.grid } };
}

function applyMeta(theme, meta) {
  meta = meta || {};
  const cmap = { bg: "bg", ink: "ink", muted: "muted", accent: "accent" };
  for (const k in cmap) if (meta[k]) theme.color[cmap[k]] = String(meta[k]).replace(/^#/, "");
  if (meta.font_heading) theme.font.heading = meta.font_heading;
  if (meta.font_body) theme.font.body = meta.font_body;
  if (meta.font_number) theme.font.number = meta.font_number;
  if (typeof meta.rule === "boolean") theme.rule = meta.rule;
  if (typeof meta.page_numbers === "boolean") theme.pageNumbers = meta.page_numbers;
  if (meta.aspect === "4:3") theme.layout = "LAYOUT_4x3";
  else if (meta.aspect === "16:9") theme.layout = "LAYOUT_WIDE";
}

// ---------------------------------------------------------------------------
// Grid — single source of truth, in inches (PptxGenJS native unit).
// ---------------------------------------------------------------------------
function makeGrid(theme) {
  const wide = theme.layout !== "LAYOUT_4x3";
  const g = Object.assign({
    pageW: wide ? 13.33 : 10,
    pageH: 7.5,
    marginX: wide ? 0.92 : 0.75,
    top: 0.62,
    titleH: 0.95,
    gap: 0.18,
    footY: 7.04,
    ruleLen: 1.05,
    ruleH: 0.045,
  }, theme.grid || {});
  g.contentW = g.pageW - 2 * g.marginX;
  g.bodyTop = g.top + g.titleH + g.gap;
  g.bodyH = g.footY - g.bodyTop - 0.1;
  g.ruleY = { content: g.top + g.titleH - 0.02, title: 2.30, section: 2.78, quote: 2.02 };
  return g;
}

// ---------------------------------------------------------------------------
// Masters — the ONLY place the accent hairline + page number live, so they are
// identical on every slide and cannot drift. One master per slide "family".
// ---------------------------------------------------------------------------
function hairline(g, theme, y) {
  if (!theme.rule) return [];
  return [{ rect: { x: g.marginX, y, w: g.ruleLen, h: g.ruleH,
    fill: { color: theme.color.accent }, line: { type: "none" } } }];
}

function pageNumberOpt(g, theme) {
  if (!theme.pageNumbers) return undefined;
  return { x: g.pageW - g.marginX - 0.9, y: g.footY, w: 0.9, h: 0.3,
    fontFace: theme.font.body, fontSize: 10, color: theme.color.muted, align: "right" };
}

function defineMasters(pres, theme, g) {
  const bg = { color: theme.color.bg };
  pres.defineSlideMaster({ title: "TITLE", background: bg,
    objects: hairline(g, theme, g.ruleY.title) });
  pres.defineSlideMaster({ title: "SECTION", background: bg,
    objects: hairline(g, theme, g.ruleY.section) });
  pres.defineSlideMaster({ title: "QUOTE", background: bg,
    objects: hairline(g, theme, g.ruleY.quote) });
  pres.defineSlideMaster({ title: "CONTENT", background: bg,
    objects: hairline(g, theme, g.ruleY.content), slideNumber: pageNumberOpt(g, theme) });
  pres.defineSlideMaster({ title: "PLAIN", background: bg,
    slideNumber: pageNumberOpt(g, theme) });
}

// ---------------------------------------------------------------------------
// Text helpers
// ---------------------------------------------------------------------------
function addTitle(slide, theme, g, title, size) {
  slide.addText(title, { x: g.marginX, y: g.top, w: g.contentW, h: g.titleH,
    fontFace: theme.font.heading, fontSize: size || 30, bold: true,
    color: theme.color.ink, align: "left", valign: "top", lineSpacingMultiple: 1.1 });
}

function bulletRuns(theme, items, base) {
  base = base || 18;
  const out = [];
  (items || []).forEach((it) => {
    const text = typeof it === "string" ? it : (it.text || "");
    const level = typeof it === "object" && it ? (it.level || 0) : 0;
    out.push({ text, options: {
      bullet: { characterCode: level === 0 ? "2013" : "2022", indent: 16 + 10 * level },
      indentLevel: level,
      fontFace: theme.font.body, fontSize: base - (level ? 2 : 0),
      color: level === 0 ? theme.color.ink : theme.color.muted,
      paraSpaceAfter: 9, breakLine: true } });
  });
  return out;
}

function source(slide, theme, g, text) {
  if (!text) return;
  slide.addText(text, { x: g.marginX, y: g.footY - 0.02, w: g.contentW - 0.9, h: 0.3,
    fontFace: theme.font.body, fontSize: 10, color: theme.color.muted, align: "left" });
}

// ---------------------------------------------------------------------------
// Slide renderers
// ---------------------------------------------------------------------------
const RENDER = {
  title(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "TITLE" });
    slide.addText(s.title, { x: g.marginX, y: 2.45, w: g.contentW, h: 1.2,
      fontFace: theme.font.heading, fontSize: 40, bold: true, color: theme.color.ink,
      align: "left", valign: "top", lineSpacingMultiple: 1.1 });
    if (s.subtitle) slide.addText(s.subtitle, { x: g.marginX, y: 3.72, w: g.contentW, h: 0.6,
      fontFace: theme.font.body, fontSize: 20, color: theme.color.muted, align: "left" });
  },

  section(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "SECTION" });
    if (s.number != null) slide.addText(String(s.number), { x: g.marginX, y: 2.18, w: g.contentW,
      h: 0.6, fontFace: theme.font.heading, fontSize: 22, bold: true, color: theme.color.accent });
    slide.addText(s.title, { x: g.marginX, y: 2.86, w: g.contentW, h: 1.2,
      fontFace: theme.font.heading, fontSize: 34, bold: true, color: theme.color.ink,
      valign: "top", lineSpacingMultiple: 1.1 });
  },

  bullets(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "CONTENT" });
    addTitle(slide, theme, g, s.title);
    slide.addText(bulletRuns(theme, s.bullets), { x: g.marginX, y: g.bodyTop,
      w: g.contentW, h: g.bodyH, valign: "top" });
    source(slide, theme, g, s.source);
  },

  two_col(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "CONTENT" });
    addTitle(slide, theme, g, s.title);
    const gutter = 0.5, colW = (g.contentW - gutter) / 2;
    ["left", "right"].forEach((key, i) => {
      const col = s[key] || {};
      const x = g.marginX + i * (colW + gutter);
      const runs = [];
      if (col.heading) runs.push({ text: col.heading, options: { bullet: false,
        fontFace: theme.font.heading, fontSize: 18, bold: true, color: theme.color.accent,
        paraSpaceAfter: 8, breakLine: true } });
      runs.push(...bulletRuns(theme, col.bullets));
      slide.addText(runs, { x, y: g.bodyTop, w: colW, h: g.bodyH, valign: "top" });
    });
    source(slide, theme, g, s.source);
  },

  big_number(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "CONTENT" });
    addTitle(slide, theme, g, s.title);
    slide.addText(String(s.number), { x: g.marginX, y: g.bodyTop, w: g.contentW, h: g.bodyH * 0.62,
      fontFace: theme.font.number || theme.font.heading, fontSize: 88, bold: true,
      color: theme.color.accent, align: "left", valign: "middle" });
    if (s.caption) slide.addText(s.caption, { x: g.marginX, y: g.bodyTop + g.bodyH * 0.6,
      w: g.contentW, h: 0.5, fontFace: theme.font.body, fontSize: 20, color: theme.color.muted });
    source(slide, theme, g, s.source);
  },

  quote(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "QUOTE" });
    slide.addText("“" + s.quote + "”", { x: g.marginX, y: 2.4, w: g.contentW, h: 2.2,
      fontFace: theme.font.heading, fontSize: 28, color: theme.color.ink,
      valign: "middle", lineSpacingMultiple: 1.25 });
    if (s.attribution) slide.addText("— " + s.attribution, { x: g.marginX, y: 4.5,
      w: g.contentW, h: 0.5, fontFace: theme.font.body, fontSize: 18, color: theme.color.muted });
  },

  image(pres, theme, g, s) {
    const hasTitle = !!s.title;
    const slide = pres.addSlide({ masterName: hasTitle ? "CONTENT" : "PLAIN" });
    if (hasTitle) addTitle(slide, theme, g, s.title);
    const y = hasTitle ? g.bodyTop : g.top;
    const h = hasTitle ? g.bodyH : g.footY - g.top - 0.4;
    if (s.image && fs.existsSync(s.image)) {
      slide.addImage({ path: s.image, x: g.marginX, y, w: g.contentW, h,
        sizing: { type: "contain", w: g.contentW, h } });
    } else {
      slide.addText("[ image: " + (s.image || "missing") + " ]", { x: g.marginX, y, w: g.contentW,
        h, fontFace: theme.font.body, fontSize: 16, color: theme.color.muted, align: "center",
        valign: "middle" });
    }
    if (s.caption) source(slide, theme, g, s.caption);
  },

  blank(pres, theme, g, s) {
    const slide = pres.addSlide({ masterName: "PLAIN" });
    if (s.title) addTitle(slide, theme, g, s.title);
  },
};

// ---------------------------------------------------------------------------
// Build
// ---------------------------------------------------------------------------
async function build(spec, out, themePath) {
  const theme = loadTheme(themePath);
  applyMeta(theme, spec.meta);
  const g = makeGrid(theme);

  const pres = new PptxGenJS();
  pres.layout = theme.layout || "LAYOUT_WIDE";
  defineMasters(pres, theme, g);

  for (const s of spec.slides || []) {
    const type = s.type || "bullets";
    (RENDER[type] || RENDER.bullets)(pres, theme, g, s);
  }
  await pres.writeFile({ fileName: out });
  console.log("wrote", out);
}

if (require.main === module) {
  const a = parseArgs(process.argv.slice(2));
  build(loadSpec(a.spec), a.out, a.theme).catch((e) => {
    console.error(e); process.exit(1);
  });
}

module.exports = { build };
