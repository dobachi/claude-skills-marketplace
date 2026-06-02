#!/usr/bin/env bash
# render_preview.sh — render a .pptx to PNGs for a visual QA pass.
# Uses LibreOffice headless. Fonts may substitute vs. PowerPoint, but layout,
# alignment, and the "no drifting bands" property are faithfully checked here.
#
# Usage: ./render_preview.sh deck.pptx [out_dir]
set -euo pipefail
PPTX="${1:?usage: render_preview.sh deck.pptx [out_dir]}"
OUT="${2:-$(dirname "$PPTX")/preview}"
mkdir -p "$OUT"

# pptx -> pdf -> png (one png per slide)
soffice --headless --convert-to pdf --outdir "$OUT" "$PPTX" >/dev/null 2>&1
PDF="$OUT/$(basename "${PPTX%.*}").pdf"

if command -v pdftoppm >/dev/null 2>&1; then
  pdftoppm -png -r 110 "$PDF" "$OUT/slide" >/dev/null 2>&1
  echo "rendered PNGs -> $OUT/slide-*.png"
else
  echo "rendered PDF -> $PDF  (install poppler-utils for per-slide PNGs)"
fi
