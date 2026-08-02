#!/usr/bin/env python3
"""Triage a PDF before extracting from it.

Answers the three questions that decide the extraction path:
  1. Is there a text layer, and on which pages?
  2. Is the page image-only (a scan) or digitally generated?
  3. Does the text look multi-column (where reading order usually breaks)?

Requires poppler-utils (pdfinfo, pdftotext, pdffonts, pdfimages). Python stdlib only.
Degrades gracefully: anything it cannot measure is reported as "unknown", never guessed.

Usage:
    python3 triage_pdf.py FILE.pdf [--pages 1-20] [--json]
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter

# A page with fewer than this many characters has, in practice, no usable text layer.
EMPTY_CHARS = 10
# Between EMPTY_CHARS and this, the page is likely furniture only (header/footer/page number).
SPARSE_CHARS = 100
# Minimum width, in PDF points, of an empty vertical band that counts as a column
# gutter. Body-text word spacing runs 2-5pt; real column gutters run 12-24pt. The
# test is applied to a whole horizontal band, so a gutter must be empty across every
# line in that band — which word spacing effectively never is.
GUTTER_MIN_PT = 8
# Horizontal bands a page is split into before looking for gutters.
BANDS = 12
# A band with fewer words than this carries too little text to judge its layout.
BAND_MIN_WORDS = 12
# A band whose text spans less than this fraction of the page is a heading, not a layout.
BAND_MIN_SPAN = 0.4


def need(binary):
    if shutil.which(binary) is None:
        print(f"error: {binary} not found. Install poppler-utils.", file=sys.stderr)
        sys.exit(2)


def run(cmd):
    """Run a command, returning stdout as text. Returns None on failure."""
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=300)
    except (subprocess.TimeoutExpired, OSError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", errors="replace")


def page_count(path):
    info = run(["pdfinfo", path])
    if not info:
        return None
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    return int(m.group(1)) if m else None


def page_text(path, page):
    return run(["pdftotext", "-f", str(page), "-l", str(page), path, "-"]) or ""


def has_embedded_fonts(path, page):
    """Digitally generated pages embed fonts; pure scans do not."""
    out = run(["pdffonts", "-f", str(page), "-l", str(page), path])
    if out is None:
        return None
    # Header is 2 lines; any further line is a font entry.
    return len([ln for ln in out.splitlines()[2:] if ln.strip()]) > 0


def image_count(path, page):
    out = run(["pdfimages", "-list", "-f", str(page), "-l", str(page), path])
    if out is None:
        return None
    return len([ln for ln in out.splitlines()[2:] if ln.strip()])


def _columns_in_band(boxes, width):
    """Column count for one horizontal band, from a vertical-gutter search.

    Marks every 1%-of-width slot that a word overlaps, then counts runs of empty
    slots wide enough to be a column separator rather than inter-word spacing.
    """
    if len(boxes) < BAND_MIN_WORDS:
        return None

    # One slot per PDF point, so the gutter threshold is a real typographic width.
    n = int(width) + 1
    slots = [False] * n
    for x0, x1 in boxes:
        a = max(0, min(n - 1, int(x0)))
        b = max(0, min(n - 1, int(x1)))
        for i in range(a, b + 1):
            slots[i] = True

    occupied = [i for i, s in enumerate(slots) if s]
    if not occupied:
        return None
    left, right = occupied[0], occupied[-1]
    # A band that spans too little of the page is a heading, not a column layout.
    if (right - left) < BAND_MIN_SPAN * width:
        return None

    gutters, run_len = 0, 0
    for i in range(left, right + 1):
        if slots[i]:
            if run_len >= GUTTER_MIN_PT:
                gutters += 1
            run_len = 0
        else:
            run_len += 1
    return gutters + 1


def column_estimate(path, page):
    """Estimate column count for a page.

    Measured per horizontal band, not over the whole page: full-width titles,
    figures and footnotes bridge the gutter and would otherwise mask a genuine
    two-column body. The page's column count is the widest layout seen in any
    band that carries enough text to judge.
    """
    xml = run(["pdftotext", "-bbox", "-f", str(page), "-l", str(page), path, "-"])
    if not xml:
        return None
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None

    width = height = None
    boxes = []
    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag == "page":
            if el.get("width"):
                width = float(el.get("width"))
            if el.get("height"):
                height = float(el.get("height"))
        elif tag == "word" and el.get("xMin") and el.get("yMin"):
            boxes.append((float(el.get("xMin")), float(el.get("xMax")),
                          float(el.get("yMin"))))

    if not width or not height or len(boxes) < BAND_MIN_WORDS:
        return None

    band_h = height / BANDS
    per_band = []
    for b in range(BANDS):
        lo, hi = b * band_h, (b + 1) * band_h
        in_band = [(x0, x1) for x0, x1, y in boxes if lo <= y < hi]
        c = _columns_in_band(in_band, width)
        if c:
            per_band.append(c)

    if not per_band:
        return None
    # Report the layout that governs the body text — the modal band. Taking the max
    # would let one figure with gaps between sub-images promote the whole page.
    counts = Counter(per_band)
    top = max(counts.values())
    return max(c for c, n in counts.items() if n == top)


def classify(chars, fonts, images, columns):
    if chars < EMPTY_CHARS:
        if images:
            return "scan", "image-only page, no text layer"
        return "blank", "no text and no image"
    if chars < SPARSE_CHARS:
        return "sparse", "very little text — likely furniture only, or a failed text layer"
    if fonts is False and images:
        return "scan+text", "image page carrying a text layer (already OCR'd, quality unverified)"
    if columns and columns >= 2:
        return "multi-column", f"text layer present, ~{columns} columns"
    if columns is None:
        return "text", "text layer present; too little body text to judge column layout"
    return "text", "text layer present, single-column"


def main():
    ap = argparse.ArgumentParser(description="Triage a PDF before extraction.")
    ap.add_argument("pdf")
    ap.add_argument("--pages", help="page range, e.g. 1-20 (default: all, capped at 50)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    for b in ("pdfinfo", "pdftotext"):
        need(b)

    total = page_count(args.pdf)
    if total is None:
        print(f"error: cannot read {args.pdf} (encrypted, corrupt, or not a PDF)", file=sys.stderr)
        sys.exit(1)

    if args.pages:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", args.pages)
        if not m:
            print("error: --pages expects N or N-M", file=sys.stderr)
            sys.exit(2)
        first = int(m.group(1))
        last = int(m.group(2) or m.group(1))
    else:
        first, last = 1, min(total, 50)
    last = min(last, total)

    rows = []
    for p in range(first, last + 1):
        text = page_text(args.pdf, p)
        chars = len(text.strip())
        fonts = has_embedded_fonts(args.pdf, p)
        images = image_count(args.pdf, p)
        columns = column_estimate(args.pdf, p) if chars >= SPARSE_CHARS else None
        kind, note = classify(chars, fonts, images, columns)
        rows.append({"page": p, "chars": chars, "fonts": fonts, "images": images,
                     "columns": columns, "kind": kind, "note": note})

    kinds = Counter(r["kind"] for r in rows)
    scanned = kinds["scan"]
    multicol = kinds["multi-column"]
    textual = kinds["text"] + kinds["scan+text"] + multicol

    if scanned and textual:
        path, why = "B (mixed)", "some pages have no text layer; OCR those, extract natively from the rest"
    elif scanned:
        path, why = "B", "no text layer — OCR is mandatory before anything else"
    elif multicol:
        path, why = "B", "multi-column text layer — reading order needs a layout-aware parser"
    elif textual:
        path, why = "A", "text layer present and single-column"
    else:
        path, why = "B", "no usable text found — treat as a scan and verify manually"

    summary = {
        "file": args.pdf, "pages_total": total, "pages_examined": len(rows),
        "kinds": dict(kinds), "recommended_path": path, "reason": why,
    }

    if args.json:
        print(json.dumps({"summary": summary, "pages": rows}, ensure_ascii=False, indent=2))
        return

    print(f"{args.pdf}  —  {total} pages, examined {first}-{last}\n")
    print(f"{'page':>5} {'chars':>7} {'imgs':>5} {'cols':>5}  kind")
    print("-" * 56)
    for r in rows:
        cols = r["columns"] if r["columns"] else "-"
        imgs = r["images"] if r["images"] is not None else "?"
        print(f"{r['page']:>5} {r['chars']:>7} {imgs:>5} {cols:>5}  {r['kind']}")

    print("\nsummary: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    print(f"recommended path: {path} — {why}")
    if len(rows) < total:
        print(f"note: examined {len(rows)} of {total} pages; rerun with --pages to widen")
    print("\nPaths are described in the skill's routing table. Spot-check one dense page "
          "against the rendered PDF before trusting any of this.")


if __name__ == "__main__":
    main()
