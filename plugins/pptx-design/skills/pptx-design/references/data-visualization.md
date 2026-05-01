# Data Visualization Reference

Charts and tables for `.pptx` decks. Source principles: Edward Tufte (*The Visual Display of Quantitative Information*), Cole Nussbaumer Knaflic (*Storytelling with Data*), McKinsey/BCG visual conventions.

## Chart Choice Follows the Question

| Question | Recommended | Notes |
|---|---|---|
| Compare across categories | Horizontal bar (long labels), vertical bar (short labels) | Sort by value unless category order has meaning |
| Change over time | Line | Multiple series → at most 4–5 lines, gray non-emphasized |
| Part-to-whole, 2 parts | **Big number** ("84% retain") | Chart is overkill for two values |
| Part-to-whole, 3+ parts | Stacked bar (single bar) | Pie is acceptable only with ≤3 distinct slices |
| Part-to-whole over time | Stacked area, 100% stacked bar | Limit to ~5 categories |
| Distribution | Histogram, box plot | Box plot when comparing groups |
| Correlation | Scatter | Add trendline only if argument requires it |
| Geographic | Choropleth, point map | Verify projection and color scale |
| Ranking | Sorted horizontal bar | Top-N is cleaner than full list |

### When NOT to chart

- A single number is more powerful as huge type than as a one-bar chart.
- Two values rarely need a chart — a sentence works ("Retention rose from 78% to 84% over the quarter").
- Charts justify themselves when patterns, comparisons, or trends across ≥3 data points need to be *seen*.

## Tufte's Data-Ink Ratio

> **Maximize data-ink, erase non-data-ink.** Every pixel on the chart should encode information.

Erase by default:

- Gridlines (or lighten to 5–10% gray).
- Redundant axis labels.
- 3D effects — 3D bars, perspective tilts, exploded pies. They distort perception.
- Drop shadows, gradient fills, default Excel/PowerPoint themes.
- Legends when **direct labeling** works (label data points or line ends instead).
- Tick marks on every increment — keep min, max, and key values.
- Backgrounds, frames, decorative chart titles.

### Direct labeling

Place labels next to the data: end-of-line for time series, on-bar for bar charts, near-points for scatter. Spares the audience from bouncing between legend and chart.

### Gray-the-rest

When emphasizing one series, color **only that series** with the accent color. Others go to neutral gray. The eye lands on the argument instantly.

## Chartjunk to Reject

- 3D bars, exploded pies, gradient fills.
- Default Excel themes (chartreuse / orange / blue rainbow).
- Beveled bars and shadow effects.
- Pictographs that distort scale (image of dollars sized by value).
- Dual y-axes with unrelated scales (almost always misleading).
- Pie charts with >3 slices, near-equal slices, or values you want compared.

## Annotations and Callouts

- **Callout the takeaway** — never assume the audience will derive it. Add a short sentence + arrow pointing to the relevant data feature.
- Highlight specific data points (dot, vertical line, shaded region) where the argument lives.
- Source citation in 8–10 pt gray below the chart, e.g., *Source: Internal data, Q3 2026.*

## Tables

### Style

- **Remove vertical borders entirely.**
- Horizontal rules sparingly: header underline + total row only.
- Right-align numbers; left-align text; align decimals; consistent decimal precision per column.
- This is the Tufte / McKinsey table style.

### Emphasis

- **Bold** the row or column being argued for.
- Apply a light fill (5–10% opacity of accent color) to the emphasized row.
- Gray out non-emphasized rows.

### Tables vs charts

| Use a table when | Use a chart when |
|---|---|
| Precise values matter (financials, prices) | Patterns or comparisons matter |
| Audience will look up specific cells | Audience needs to see the trend |
| Multiple metrics per row need exact comparison | A single dimension drives the story |

If 2–3 numbers would suffice, **don't use a table** — call them out as text.

## Annotations Layer (PowerPoint specifics)

Build annotations as separate shapes, not inside the chart's title:

- Chart object stays clean and editable.
- Callouts live as text boxes + connector lines, layered above.
- Source footnote is a separate text box in the layout master.

## Chart Construction in PowerPoint

- **Insert → Chart**, paste data into the embedded sheet.
- For external data: paste as **picture** to lock visuals; or paste as **linked Excel** if the data updates.
- Set **theme colors** in Design → Colors so all charts stay on-palette.
- Save **chart templates** (`.crtx`) for chart styles you'll reuse — File → Save as Template from a chart's right-click menu.

## Pre-Delivery Chart Review

For each chart:

- [ ] Title is the takeaway, not the topic.
- [ ] Source cited.
- [ ] No 3D, no chartjunk.
- [ ] Direct labels (or legend justified).
- [ ] Accent color on the series in focus; others gray.
- [ ] Numbers reconcile with totals stated elsewhere.
- [ ] Color independence: meaning still readable in grayscale or for color-blind viewers.
- [ ] Alt text describes the takeaway, not just "bar chart."

## Anti-Patterns Specific to AI-Generated Decks

- **Chart auto-inserted from a SmartArt-style "data placeholder"** that has no real data.
- **Pie charts with 6+ slices** generated to "match" a list of items.
- **Multi-series line charts with 8+ series** in rainbow colors — unreadable.
- **Default Excel themes** rather than the deck's theme colors.
- **Charts where the underlying numbers contradict the narrative** — always reconcile claims and data before shipping.
