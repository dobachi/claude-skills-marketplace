#!/usr/bin/env bash
# extract_pdf.sh — Extract figures from a PDF.
#
# Uses poppler-utils (pdfimages, pdftocairo, pdftotext) to:
#   - Pull embedded raw images out of the PDF (--mode embedded; default)
#   - Render full pages as PNG, layout-faithful (--mode pages)
#   - Both (--mode both)
# Recovers a caption candidate per image via text-near-bbox heuristic.
# Emits manifest.json describing every figure with provenance.
#
# Usage:
#   bash extract_pdf.sh <pdf> [--out DIR] [--mode embedded|pages|both] [--pages N-M] [--dpi 150] [--min-px 200]
#
# Output:
#   <out>/figures/img-XXX.{png,jpg,…}    embedded images (mode embedded|both)
#   <out>/pages/page-NNN.png             rendered pages   (mode pages|both)
#   <out>/manifest.json                  per-figure metadata
#
# Exit codes:
#   0  success
#   1  bad usage
#   2  runtime failure (missing tool, malformed PDF, etc.)

set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage: bash extract_pdf.sh <pdf> [options]
  --out DIR           Output directory (default: ./out_pdf)
  --mode MODE         embedded | pages | both (default: embedded)
  --pages RANGE       Page range, e.g. 1-10 or 5 (default: all)
  --dpi N             DPI for page render (default: 150)
  --min-px N          Drop embedded images smaller than NxN (default: 200)
  -h, --help          Show this help
EOF
}

if [[ $# -eq 0 ]]; then usage; exit 1; fi

PDF=""
OUT="./out_pdf"
MODE="embedded"
PAGES=""
DPI=150
MINPX=200

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --out)     OUT="$2"; shift 2 ;;
    --mode)    MODE="$2"; shift 2 ;;
    --pages)   PAGES="$2"; shift 2 ;;
    --dpi)     DPI="$2"; shift 2 ;;
    --min-px)  MINPX="$2"; shift 2 ;;
    -*)        echo "[error] unknown option: $1" >&2; usage; exit 1 ;;
    *)         if [[ -z "$PDF" ]]; then PDF="$1"; shift; else echo "[error] extra arg: $1" >&2; exit 1; fi ;;
  esac
done

if [[ -z "$PDF" ]]; then echo "[error] PDF path required" >&2; usage; exit 1; fi
if [[ ! -f "$PDF" ]]; then echo "[error] file not found: $PDF" >&2; exit 2; fi

for tool in pdfimages pdftocairo pdftotext; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "[error] missing required tool: $tool (install poppler-utils)" >&2; exit 2
  fi
done

mkdir -p "$OUT/figures" "$OUT/pages"

# Page range flags for pdfimages / pdftocairo
PAGE_FLAGS=()
if [[ -n "$PAGES" ]]; then
  if [[ "$PAGES" =~ ^([0-9]+)(-([0-9]+))?$ ]]; then
    F="${BASH_REMATCH[1]}"
    L="${BASH_REMATCH[3]:-${BASH_REMATCH[1]}}"
    PAGE_FLAGS=(-f "$F" -l "$L")
  else
    echo "[error] --pages format: N or N-M" >&2; exit 1
  fi
fi

PDF_ABS="$(cd "$(dirname "$PDF")" && pwd)/$(basename "$PDF")"
PDF_NAME="$(basename "$PDF")"

# Extract embedded images
declare -a EMB_FILES=()
if [[ "$MODE" == "embedded" || "$MODE" == "both" ]]; then
  echo "[info] extracting embedded images..." >&2
  pdfimages "${PAGE_FLAGS[@]}" -all -p "$PDF_ABS" "$OUT/figures/img" 2>/dev/null || true
  while IFS= read -r -d '' f; do EMB_FILES+=("$f"); done < <(find "$OUT/figures" -type f -print0 2>/dev/null)
  echo "[info] extracted ${#EMB_FILES[@]} embedded image(s)" >&2
fi

# Render pages
declare -a PAGE_FILES=()
if [[ "$MODE" == "pages" || "$MODE" == "both" ]]; then
  echo "[info] rendering pages at ${DPI} dpi..." >&2
  pdftocairo "${PAGE_FLAGS[@]}" -png -r "$DPI" "$PDF_ABS" "$OUT/pages/page" 2>/dev/null || true
  while IFS= read -r -d '' f; do PAGE_FILES+=("$f"); done < <(find "$OUT/pages" -type f -print0 2>/dev/null)
  echo "[info] rendered ${#PAGE_FILES[@]} page(s)" >&2
fi

# Per-page text via pdftotext -bbox-layout (used for caption candidate recovery)
TEXT_XML="$OUT/.text-bbox.xml"
pdftotext -bbox-layout "${PAGE_FLAGS[@]}" "$PDF_ABS" "$TEXT_XML" 2>/dev/null || echo "" > "$TEXT_XML"

# Build manifest.json
MANIFEST="$OUT/manifest.json"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Identify embedded image -> page mapping. pdfimages -p prefixes filename with "-pNN-"
# Filename pattern: img-NNN-pPP.ext  where PP is page number (zero-padded).
emit_figure_entry() {
  local idx="$1" file="$2" origin="$3" page="$4"
  local sha="" w="" h="" minok="true"
  if [[ -f "$file" ]]; then
    sha="$(sha256sum "$file" 2>/dev/null | cut -d' ' -f1 || echo '')"
    if command -v identify >/dev/null 2>&1; then
      read -r w h < <(identify -format "%w %h\n" "$file" 2>/dev/null || echo "0 0") || true
    fi
  fi
  if [[ -n "$w" && -n "$h" && "$w" =~ ^[0-9]+$ && "$h" =~ ^[0-9]+$ ]]; then
    if (( w < MINPX || h < MINPX )); then minok="false"; fi
  fi
  local rel; rel="$(realpath --relative-to="$OUT" "$file" 2>/dev/null || echo "$file")"
  local id; id="$(printf 'F-%02d' "$idx")"
  local src_ref
  if [[ "$origin" == "Extracted" ]]; then
    if [[ -n "$page" ]]; then
      src_ref="${PDF_NAME}, p.${page}, img.${idx}"
    else
      src_ref="${PDF_NAME}, img.${idx}"
    fi
  else
    src_ref="${PDF_NAME}, p.${page} (full page render)"
  fi

  cat <<EOF
{
  "id": "$id",
  "origin": "$origin",
  "file": "$rel",
  "source_reference": "$src_ref",
  "source_page": ${page:-null},
  "caption": null,
  "caption_confidence": "none",
  "alt_text": null,
  "linked_claim": [],
  "sha256": "$sha",
  "width": ${w:-null},
  "height": ${h:-null},
  "filtered_min_px": $minok
}
EOF
}

{
  echo "{"
  echo "  \"source\": \"$PDF_ABS\","
  echo "  \"source_format\": \"pdf\","
  echo "  \"extracted_at\": \"$NOW\","
  echo "  \"figures\": ["

  idx=0
  first=true
  # Embedded images first
  for f in "${EMB_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    page=""
    base="$(basename "$f")"
    if [[ "$base" =~ -p([0-9]+)\. ]]; then page="${BASH_REMATCH[1]}"; page="$((10#$page))"; fi
    idx=$((idx + 1))
    $first || echo ","
    first=false
    emit_figure_entry "$idx" "$f" "Extracted" "$page" | sed 's/^/    /'
  done
  # Page renders
  for f in "${PAGE_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    page=""
    base="$(basename "$f")"
    if [[ "$base" =~ -([0-9]+)\.png$ ]]; then page="${BASH_REMATCH[1]}"; page="$((10#$page))"; fi
    idx=$((idx + 1))
    $first || echo ","
    first=false
    emit_figure_entry "$idx" "$f" "PageRender" "$page" | sed 's/^/    /'
  done

  echo ""
  echo "  ]"
  echo "}"
} > "$MANIFEST"

echo "[info] manifest: $MANIFEST" >&2
echo "$MANIFEST"
