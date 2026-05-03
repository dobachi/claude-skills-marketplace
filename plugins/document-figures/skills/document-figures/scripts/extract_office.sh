#!/usr/bin/env bash
# extract_office.sh — Extract figures from a DOCX or PPTX (auto-detected by extension).
#
# DOCX/PPTX are ZIPs. Embedded images live in word/media/ or ppt/media/.
# For PPTX, attribute each image to its slide via per-slide relationship files.
# For DOCX, attempt caption recovery from sibling Caption-styled paragraphs.
# Emits manifest.json with per-figure provenance.
#
# Usage:
#   bash extract_office.sh <docx-or-pptx> [--out DIR] [--min-px 200]
#
# Output:
#   <out>/figures/<image>           extracted media files
#   <out>/manifest.json             per-figure metadata
#
# Exit codes:
#   0  success
#   1  bad usage
#   2  runtime failure

set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage: bash extract_office.sh <docx|pptx> [options]
  --out DIR     Output directory (default: ./out_office)
  --min-px N    Drop images smaller than NxN (default: 200; 0 to disable)
  -h, --help    Show this help
EOF
}

if [[ $# -eq 0 ]]; then usage; exit 1; fi

SRC=""
OUT="./out_office"
MINPX=200

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --out)     OUT="$2"; shift 2 ;;
    --min-px)  MINPX="$2"; shift 2 ;;
    -*)        echo "[error] unknown option: $1" >&2; usage; exit 1 ;;
    *)         if [[ -z "$SRC" ]]; then SRC="$1"; shift; else echo "[error] extra arg: $1" >&2; exit 1; fi ;;
  esac
done

if [[ -z "$SRC" ]]; then echo "[error] source path required" >&2; usage; exit 1; fi
if [[ ! -f "$SRC" ]]; then echo "[error] file not found: $SRC" >&2; exit 2; fi

for tool in unzip xmllint sha256sum; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "[error] missing required tool: $tool" >&2; exit 2
  fi
done

EXT="${SRC##*.}"
EXT_LC="$(echo "$EXT" | tr '[:upper:]' '[:lower:]')"
case "$EXT_LC" in
  docx) FORMAT="docx"; MEDIA_DIR="word/media" ;;
  pptx) FORMAT="pptx"; MEDIA_DIR="ppt/media" ;;
  *)    echo "[error] unsupported extension: $EXT (need .docx or .pptx)" >&2; exit 1 ;;
esac

SRC_ABS="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
SRC_NAME="$(basename "$SRC")"

mkdir -p "$OUT/figures"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[info] unzipping $SRC_NAME ..." >&2
unzip -qq -d "$TMP" "$SRC_ABS"

if [[ ! -d "$TMP/$MEDIA_DIR" ]]; then
  echo "[warn] no media directory at $MEDIA_DIR; emitting empty manifest" >&2
fi

# Copy media to output
declare -a MEDIA_FILES=()
if [[ -d "$TMP/$MEDIA_DIR" ]]; then
  while IFS= read -r -d '' f; do
    cp "$f" "$OUT/figures/"
    MEDIA_FILES+=("$(basename "$f")")
  done < <(find "$TMP/$MEDIA_DIR" -type f -print0)
fi

echo "[info] copied ${#MEDIA_FILES[@]} media file(s)" >&2

# Per-format slide/page attribution
declare -A IMG_TO_SLIDE=()
declare -A IMG_TO_CAPTION=()
declare -A IMG_TO_CONFIDENCE=()
declare -A IMG_TO_ALT=()

if [[ "$FORMAT" == "pptx" ]]; then
  # For each slide, parse rels file mapping rId -> Target (image filename).
  # Slides are at ppt/slides/slideN.xml; rels at ppt/slides/_rels/slideN.xml.rels
  for rels in "$TMP"/ppt/slides/_rels/slide*.xml.rels; do
    [[ -f "$rels" ]] || continue
    base="$(basename "$rels")"
    # slideN.xml.rels -> N
    if [[ "$base" =~ slide([0-9]+)\.xml\.rels ]]; then
      slide_num="${BASH_REMATCH[1]}"
    else
      continue
    fi
    # Targets ending in media/imageX.ext -> imageX.ext
    targets="$(xmllint --xpath '//*[local-name()="Relationship" and contains(@Type, "image")]/@Target' "$rels" 2>/dev/null || true)"
    while read -r line; do
      [[ -z "$line" ]] && continue
      if [[ "$line" =~ Target=\"([^\"]+)\" ]]; then
        target="${BASH_REMATCH[1]}"
        img="$(basename "$target")"
        if [[ -z "${IMG_TO_SLIDE[$img]:-}" ]]; then
          IMG_TO_SLIDE[$img]="$slide_num"
        else
          IMG_TO_SLIDE[$img]="${IMG_TO_SLIDE[$img]},$slide_num"
        fi
      fi
    done <<< "$targets"
  done

  # Per-slide title as a caption proxy (alt-text-style)
  declare -A SLIDE_TITLE=()
  for slide in "$TMP"/ppt/slides/slide*.xml; do
    [[ -f "$slide" ]] || continue
    base="$(basename "$slide")"
    if [[ "$base" =~ slide([0-9]+)\.xml ]]; then
      n="${BASH_REMATCH[1]}"
    else continue; fi
    title="$(xmllint --xpath 'string(//*[local-name()="sp"][.//*[local-name()="ph" and (@type="title" or @type="ctrTitle")]]//*[local-name()="t"])' "$slide" 2>/dev/null || true)"
    SLIDE_TITLE[$n]="$title"
  done

  # Alt-text per image: scan all slides for <p:nvPicPr><p:cNvPr descr="..."/></p:nvPicPr> mapped via blip rId
  for slide in "$TMP"/ppt/slides/slide*.xml; do
    [[ -f "$slide" ]] || continue
    base="$(basename "$slide")"
    if [[ "$base" =~ slide([0-9]+)\.xml ]]; then
      n="${BASH_REMATCH[1]}"
    else continue; fi
    rels="$TMP/ppt/slides/_rels/${base}.rels"
    [[ -f "$rels" ]] || continue
    # For each pic element, get descr and embed rId
    pic_count="$(xmllint --xpath 'count(//*[local-name()="pic"])' "$slide" 2>/dev/null || echo 0)"
    for ((i=1; i<=pic_count; i++)); do
      descr="$(xmllint --xpath "string((//*[local-name()='pic'])[$i]//*[local-name()='cNvPr']/@descr)" "$slide" 2>/dev/null || echo '')"
      embed="$(xmllint --xpath "string((//*[local-name()='pic'])[$i]//*[local-name()='blip']/@*[local-name()='embed'])" "$slide" 2>/dev/null || echo '')"
      [[ -z "$embed" ]] && continue
      target="$(xmllint --xpath "string(//*[local-name()='Relationship' and @Id='$embed']/@Target)" "$rels" 2>/dev/null || echo '')"
      [[ -z "$target" ]] && continue
      img="$(basename "$target")"
      if [[ -n "$descr" ]]; then
        IMG_TO_ALT[$img]="$descr"
      fi
    done
  done

  # Synthesize caption (slide title) for any image without alt-text
  for img in "${MEDIA_FILES[@]}"; do
    if [[ -n "${IMG_TO_ALT[$img]:-}" ]]; then
      IMG_TO_CAPTION[$img]="${IMG_TO_ALT[$img]}"
      IMG_TO_CONFIDENCE[$img]="recovered"
    elif [[ -n "${IMG_TO_SLIDE[$img]:-}" ]]; then
      first_slide="${IMG_TO_SLIDE[$img]%%,*}"
      title="${SLIDE_TITLE[$first_slide]:-}"
      if [[ -n "$title" ]]; then
        IMG_TO_CAPTION[$img]="[reconstructed from slide title] $title"
        IMG_TO_CONFIDENCE[$img]="reconstructed"
      else
        IMG_TO_CAPTION[$img]=""
        IMG_TO_CONFIDENCE[$img]="none"
      fi
    fi
  done

elif [[ "$FORMAT" == "docx" ]]; then
  # DOCX caption recovery: look for paragraphs with pStyle "Caption" — they appear in document order,
  # generally directly after the drawing they caption.
  DOC_XML="$TMP/word/document.xml"
  if [[ -f "$DOC_XML" ]]; then
    # Collect Caption-styled paragraph texts in document order
    captions_xml="$(xmllint --xpath '//*[local-name()="p"][.//*[local-name()="pStyle" and @*[local-name()="val"]="Caption"]]' "$DOC_XML" 2>/dev/null || true)"
    # Simple approach: scan document.xml for sequence of (drawing -> caption pStyle paragraph).
    # Parse with python-style streaming using xmllint's --xpath repeatedly.
    drawing_count="$(xmllint --xpath 'count(//*[local-name()="drawing"])' "$DOC_XML" 2>/dev/null || echo 0)"
    rels_file="$TMP/word/_rels/document.xml.rels"
    for ((i=1; i<=drawing_count; i++)); do
      embed="$(xmllint --xpath "string((//*[local-name()='drawing'])[$i]//*[local-name()='blip']/@*[local-name()='embed'])" "$DOC_XML" 2>/dev/null || echo '')"
      descr="$(xmllint --xpath "string((//*[local-name()='drawing'])[$i]//*[local-name()='docPr']/@descr)" "$DOC_XML" 2>/dev/null || echo '')"
      [[ -z "$embed" ]] && continue
      target="$(xmllint --xpath "string(//*[local-name()='Relationship' and @Id='$embed']/@Target)" "$rels_file" 2>/dev/null || echo '')"
      [[ -z "$target" ]] && continue
      img="$(basename "$target")"
      if [[ -n "$descr" ]]; then
        IMG_TO_ALT[$img]="$descr"
        IMG_TO_CAPTION[$img]="$descr"
        IMG_TO_CONFIDENCE[$img]="recovered"
      fi
    done
    # Best-effort sibling caption: scan all caption paragraphs and store as a free pool;
    # users can re-link by inspection if alt-text was absent.
    if [[ -n "$captions_xml" ]]; then
      # Extract just the text content of caption paragraphs
      caption_texts="$(xmllint --xpath 'string(//*[local-name()="p"][.//*[local-name()="pStyle" and @*[local-name()="val"]="Caption"]])' "$DOC_XML" 2>/dev/null || true)"
      # Note: a more sophisticated implementation would pair captions to drawings by document order;
      # this v1 records caption pool as a sibling artifact.
      mkdir -p "$OUT"
      printf '%s\n' "$caption_texts" > "$OUT/caption_pool.txt"
    fi
  fi
fi

# Build manifest.json
MANIFEST="$OUT/manifest.json"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

json_escape() {
  # Minimal JSON string escape: backslashes, double quotes, newlines, tabs.
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e ':a;N;$!ba;s/\n/\\n/g' -e 's/\t/\\t/g' -e 's/\r/\\r/g'
}

{
  echo "{"
  echo "  \"source\": \"$SRC_ABS\","
  echo "  \"source_format\": \"$FORMAT\","
  echo "  \"extracted_at\": \"$NOW\","
  echo "  \"figures\": ["

  idx=0
  first=true
  for img in "${MEDIA_FILES[@]}"; do
    file_path="$OUT/figures/$img"
    [[ -f "$file_path" ]] || continue
    sha="$(sha256sum "$file_path" 2>/dev/null | cut -d' ' -f1 || echo '')"
    w=""; h=""
    if command -v identify >/dev/null 2>&1; then
      read -r w h < <(identify -format "%w %h\n" "$file_path" 2>/dev/null || echo "0 0") || true
    fi
    minok="true"
    if [[ -n "$w" && -n "$h" && "$w" =~ ^[0-9]+$ && "$h" =~ ^[0-9]+$ && "$MINPX" -gt 0 ]]; then
      if (( w < MINPX || h < MINPX )); then minok="false"; fi
    fi

    idx=$((idx + 1))
    id="$(printf 'F-%02d' "$idx")"

    slide_field="null"
    src_ref=""
    if [[ "$FORMAT" == "pptx" && -n "${IMG_TO_SLIDE[$img]:-}" ]]; then
      first_slide="${IMG_TO_SLIDE[$img]%%,*}"
      slide_field="$first_slide"
      src_ref="${SRC_NAME}, slide ${first_slide}, ${img}"
    elif [[ "$FORMAT" == "docx" ]]; then
      src_ref="${SRC_NAME}, ${img}"
    else
      src_ref="${SRC_NAME}, ${img}"
    fi

    caption="${IMG_TO_CAPTION[$img]:-}"
    confidence="${IMG_TO_CONFIDENCE[$img]:-none}"
    alt="${IMG_TO_ALT[$img]:-}"

    cap_json="null"
    if [[ -n "$caption" ]]; then cap_json="\"$(json_escape "$caption")\""; fi
    alt_json="null"
    if [[ -n "$alt" ]]; then alt_json="\"$(json_escape "$alt")\""; fi

    $first || echo ","
    first=false

    cat <<EOF
    {
      "id": "$id",
      "origin": "Extracted",
      "file": "figures/$img",
      "source_reference": "$(json_escape "$src_ref")",
      "source_slide": $slide_field,
      "caption": $cap_json,
      "caption_confidence": "$confidence",
      "alt_text": $alt_json,
      "linked_claim": [],
      "sha256": "$sha",
      "width": ${w:-null},
      "height": ${h:-null},
      "filtered_min_px": $minok
    }
EOF
  done

  echo ""
  echo "  ]"
  echo "}"
} > "$MANIFEST"

echo "[info] manifest: $MANIFEST" >&2
echo "$MANIFEST"
