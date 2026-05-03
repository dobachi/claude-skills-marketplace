# Figure Extraction — Per-Format Recipes

Covers PDF, DOCX, PPTX, and HTML/web. Each section gives the file-format anatomy, the extraction commands, the caption-recovery strategy, and the failure modes.

## Common Output Schema

Every extractor emits `manifest.json` with this shape:

```json
{
  "source": "/abs/path/to/source.ext",
  "source_format": "pdf|docx|pptx|html",
  "extracted_at": "2026-05-03T12:00:00Z",
  "figures": [
    {
      "id": "F-01",
      "file": "figures/img-001.png",
      "source_reference": "source.pdf, p.7, fig.2",
      "source_page": 7,
      "bbox": [120, 340, 480, 620],
      "caption_candidate": "Figure 2: Revenue by segment, 2018-2024.",
      "caption_confidence": "recovered|reconstructed|none",
      "alt_text": null,
      "sha256": "abc123…"
    }
  ]
}
```

## PDF

### Anatomy
PDFs embed images as XObjects with `/Subtype /Image`. They have no concept of "figure" as such — a figure is an image plus its caption text positioned nearby on the page. There may be many embedded images per visual figure (multi-panel charts), and there may be vector drawings that have no image XObject at all (those need page-render extraction, not embedded extraction).

### Extraction commands

```bash
# Embedded raw images, with -p prefix giving page number in filename (img-001-p07.ppm)
pdfimages -all -p source.pdf out/img

# Page render at 150 DPI, layout-faithful (vector drawings preserved)
pdftocairo -png -r 150 source.pdf out/page

# Page text with positional bounding boxes (XML)
pdftotext -bbox-layout source.pdf out/page.xml
```

`-all` preserves the native image format (jpeg/png/jp2/ccitt) instead of converting everything to PPM. `-r 150` is enough for 1× display; bump to `-r 300` for print or zoom.

### Caption recovery (heuristic)

1. From `pdfimages -list source.pdf`, get each image's page and bounding box (`<x> <y> <width> <height>`).
2. From `pdftotext -bbox-layout source.pdf -` (or to a file), parse `<word>` elements with their `xMin/yMin/xMax/yMax`.
3. For each image, find words whose bbox lies within ~200pt below the image bbox (or within 40pt above, depending on convention — many academic papers caption above; books and reports caption below).
4. Concatenate those words into a caption candidate. If the candidate starts with "Figure N:" / "Fig. N:" / "図 N" — high confidence. Else medium.
5. Confidence: `recovered` if a "Figure N:" prefix matched; `reconstructed` if you wrote a description from neighboring text; `none` if no nearby text.

### Failure modes
- **Multi-panel figures**: `pdfimages` extracts each panel as a separate image. Detect by panels sharing a page and proximate bboxes; group them in the manifest with a parent figure ID.
- **Vector-only figures**: `pdfimages` returns nothing. Use `pdftocairo -png -f N -l N` to render the single page; treat the rendered page as the figure (note the bbox crop range in the manifest).
- **Inline math, equation as image**: usually small bbox; filter with `--min-px 200` (or accept and tag as equation).
- **Background images / decorations**: full-page-spanning images are usually decorative; filter or flag.

## DOCX

### Anatomy
DOCX is a ZIP. Relevant entries:

```
word/document.xml             # main body; contains <w:drawing> elements with image references
word/_rels/document.xml.rels  # maps relationship IDs to targets
word/media/image1.png         # the actual image bytes
```

A `<w:drawing>` contains `<a:blip r:embed="rIdN"/>`. The relationship file maps `rIdN` to a `Target` like `media/image1.png`. Alt text lives at `<wp:docPr@descr>` (and sometimes `@title`).

Captions are typically in a `<w:p>` paragraph immediately following the drawing, styled with `pStyle val="Caption"`.

### Extraction commands

```bash
# Unzip the docx into a temp dir
unzip -d tmp/ source.docx

# List images
ls tmp/word/media/

# Get alt text for each image
xmllint --xpath "//*[local-name()='docPr']/@descr" tmp/word/document.xml

# Get all Caption-styled paragraphs (likely figure captions, in document order)
xmllint --xpath "//*[local-name()='p'][.//*[local-name()='pStyle' and @*[local-name()='val']='Caption']]//text()" tmp/word/document.xml
```

### Caption recovery
1. Walk `<w:p>` elements in `document.xml` in document order.
2. When a `<w:drawing>` is encountered, capture the `r:embed` target via the relationships file.
3. Look ahead one paragraph; if it has `pStyle val="Caption"`, take its concatenated text as the caption (high confidence).
4. Else, fall back to the drawing's `descr` attribute (alt text) — medium confidence.
5. Else: confidence `none`.

### Failure modes
- **Inline images vs floating images**: DOCX has both `<w:drawing>` (DrawingML, the modern path) and the legacy `<v:shape>` (VML). Handle both; `xmllint --xpath` queries should accept either.
- **Group shapes**: `<wpg:wgp>` wraps multiple drawings; each child has its own `r:embed`. Treat them as a single figure with multiple files.
- **EMF/WMF**: legacy Microsoft vector formats — most renderers cannot display them in browsers. Document this; user converts via LibreOffice if needed.
- **Linked images** (not embedded): the relationship's `Target` is an external URL, not a `media/` path. Fetch separately or flag.

## PPTX

### Anatomy
Same ZIP idea, per-slide:

```
ppt/slides/slide1.xml             # slide 1 markup
ppt/slides/_rels/slide1.xml.rels  # slide 1 relationships
ppt/media/image1.png              # shared media pool
```

`<p:pic>` elements contain `<a:blip r:embed="rIdN"/>`. The relationship resolves to `../media/imageN.ext`. Alt text: `<p:nvPicPr><p:cNvPr@descr>`.

Per-slide titles: `<p:sp>` with `<p:ph type="title"/>` containing `<a:t>` text.

### Extraction commands

```bash
unzip -d tmp/ source.pptx

# List slides
ls tmp/ppt/slides/slide*.xml

# Per-slide, list embedded image relationships
for i in tmp/ppt/slides/_rels/slide*.xml.rels; do
  echo "$i:"
  xmllint --xpath '//*[local-name()="Relationship" and @Type[contains(., "image")]]/@Target' "$i"
done

# Per-slide title (alt-text proxy)
xmllint --xpath '//*[local-name()="sp"][.//*[local-name()="ph" and @type="title"]]//*[local-name()="t"]/text()' tmp/ppt/slides/slide5.xml
```

### Caption recovery
Slides rarely have figure captions per se. The recoverable signals are:
1. The slide title (high confidence as a "what is this slide about" summary).
2. The image's `descr` (alt-text) attribute.
3. Body text on the slide (medium confidence — may or may not refer to the figure).

Set `caption_confidence: recovered` only when alt-text is present; otherwise `reconstructed` and explicitly note the slide title was used as a proxy.

### Optional: slide-as-PNG render

For layout-faithful capture (the slide as the user sees it), use LibreOffice headless:

```bash
libreoffice --headless --convert-to png --outdir out/ source.pptx
# Or per-slide via filter:
libreoffice --headless --convert-to "png:impress_png_Export:SelectedPages=5" source.pptx
```

LibreOffice rendering preserves layout exactly; raw `unzip` does not. Use slide rendering when the deliverable is "the slide as a figure," and embedded extraction when the deliverable is "the chart that was on the slide."

### Failure modes
- **OLE-embedded charts**: PPTX charts are stored as `<c:chart>` references to `ppt/charts/chartN.xml` plus a fallback PNG in `ppt/media/`. The fallback PNG is what you usually want; the chart XML is the data source.
- **Group shapes** (`<p:grpSp>`): multiple pics per group; same group treatment as DOCX.
- **Animations / transitions**: irrelevant for static figure extraction.

## HTML / Web

### Anatomy
DOM contains `<img src="…" alt="…" srcset="…">` and `<figure><img><figcaption>…</figcaption></figure>`. Modern sites use `srcset` for responsive images — pick the highest-resolution variant.

### Extraction strategy

Puppeteer headless:

```js
await page.goto(url, {waitUntil: 'networkidle2'});
const figures = await page.evaluate(() => {
  const results = [];
  document.querySelectorAll('img').forEach((img, i) => {
    const figure = img.closest('figure');
    const caption = figure?.querySelector('figcaption')?.textContent?.trim() || null;
    let src = img.currentSrc || img.src;
    // currentSrc resolves srcset; falls back to src
    results.push({
      index: i,
      src,
      alt: img.alt || null,
      caption,
      width: img.naturalWidth,
      height: img.naturalHeight,
    });
  });
  return results;
});
```

Then download each `src` (resolve relative URLs against the page URL) via `fetch()` (Node 18+ built-in).

### Caption recovery
1. `<figcaption>` is the gold standard — `recovered`.
2. `alt` attribute — `recovered` (it is the source's own description).
3. Surrounding text (sibling `<p>`, `aria-describedby`) — `reconstructed`.
4. None — `none`.

### Filtering
- `--min-px N` drops images smaller than N×N (icons, sprites, tracking pixels).
- Filter by URL pattern for known noise (`googletagmanager`, `analytics`, base64 spacers).
- Optionally filter by parent `<picture>` vs orphan `<img>`.

### Full-page screenshot

For sites where the visual layout *is* the figure (dashboards, infographics, custom-rendered SVG):

```js
await page.screenshot({path: 'out/page.png', fullPage: true});
```

Document this as the fallback when DOM walking returns nothing useful.

### Failure modes
- **JavaScript-rendered images**: `waitUntil: 'networkidle2'` handles most; lazy-loaded images may need `page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))` plus a delay before screenshot.
- **Canvas-rendered charts** (Plotly, D3): not in the DOM as `<img>`; capture via `page.screenshot()` with the canvas element's bounding box.
- **CORS-blocked images**: download via Puppeteer's request interception or via Node `fetch` with the page's referer header.
- **Dynamic content / paywalls**: outside the scope of this skill; document as a user-handled prerequisite.

## Provenance Schema (`source_reference` field)

Use this grammar so downstream consumers can parse:

| Format | Example |
|---|---|
| PDF | `paper.pdf, p.7, fig.2` (or `paper.pdf, p.7, img.3` if no figure number recovered) |
| DOCX | `report.docx, fig.4` (or `report.docx, img.4` if no caption) |
| PPTX | `deck.pptx, slide 12, img.1` |
| HTML | `https://example.com/article, fig.3` (use the page URL, not just domain) |

Always include the source filename or URL — relative IDs alone are not provenance.
