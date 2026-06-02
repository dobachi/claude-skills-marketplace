/*
 * brand-example — a worked example of a "provided template" expressed as a theme.
 *
 * This is how you honor a corporate/brand look with PptxGenJS (which cannot open
 * a binary .potx): transcribe the brand's palette + fonts into a theme module and
 * pass it with --theme. Everything else (grid, no-drift hairline, slide types)
 * stays identical — only the look changes.
 *
 *   node build_deck.js deck.yaml -o out.pptx --theme themes/brand-example.js
 *
 * The values below mirror the editorial navy palette from a real deck. Replace
 * them with the brand you're matching.
 */
module.exports = {
  name: "brand-example",
  layout: "LAYOUT_WIDE",

  color: {
    bg: "F4F7FB",     // cool off-white base
    ink: "0A1F44",    // deep navy primary text
    muted: "7A8AA6",  // cool gray-blue
    accent: "1E5AA8", // brand signature blue
  },

  font: {
    heading: "Yu Gothic Medium",
    body: "Yu Gothic",
    number: "Cambria",
  },

  rule: true,        // set false if the brand master already has its own title treatment
  pageNumbers: true,

  grid: {
    marginX: 0.92,
    top: 0.62,
    titleH: 0.95,
  },
};
