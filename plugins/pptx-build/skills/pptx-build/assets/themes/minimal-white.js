/*
 * minimal-white — the default theme module.
 *
 * A "theme" here plays the role a .potx would in PowerPoint: it carries the
 * palette, fonts, and grid that every slide reads from. build_deck.js turns
 * `rule` into a MASTER-level hairline (never a per-slide band), so the accent is
 * identical on every slide and cannot drift.
 *
 * To honor a provided/brand template, copy this file, swap the values to match
 * the brand, and pass it with --theme. See themes/brand-example.js.
 */
module.exports = {
  name: "minimal-white",
  layout: "LAYOUT_WIDE", // 13.33 x 7.5 in (16:9). "LAYOUT_4x3" for 10 x 7.5.

  color: {
    bg: "FFFFFF",     // paper white (use "FAFAFA" for a softer feel)
    ink: "1A1A1A",    // near-black: avoids pure-black halation
    muted: "6B7280",  // secondary text, captions, sources
    accent: "2F5DA8", // THE single accent — hairline + emphasis only
  },

  // Japanese-friendly fonts (Yu Gothic ships with Windows; PowerPoint falls back
  // gracefully). Bold is applied per-run, so "Yu Gothic" + bold:true is fine.
  font: {
    heading: "Yu Gothic Medium",
    body: "Yu Gothic",
    number: "Yu Gothic Medium",
  },

  rule: true,        // draw the short master-level accent hairline (NOT a band)
  pageNumbers: true, // page numbers on content slides

  // Grid overrides (inches). Omit to use build_deck.js defaults. Override only
  // when a brand needs different margins.
  grid: {
    marginX: 0.92,
    top: 0.62,
    titleH: 0.95,
  },
};
