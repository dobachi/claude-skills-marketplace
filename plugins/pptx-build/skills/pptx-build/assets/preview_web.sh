#!/usr/bin/env bash
# preview_web.sh — one command from a .pptx to a browser preview, for a PC or a phone, so nobody
# has to download and open the .pptx.
#
#   .pptx --LibreOffice--> PDF --pdftoppm--> OUT/img/s-NNN.jpg --preview_web.py--> OUT/index.html
#
# The folder OUT is self-contained (index.html + img/). Publish it (e.g. as a Claude Artifact:
# file_path OUT/index.html, root OUT, files = the img/s-NNN.jpg that changed) or serve it with
# --serve. See references/web-preview.md.
#
# Usage:
#   preview_web.sh DECK.pptx [options]
#   preview_web.sh --serve-only [ADDR:]PORT -o OUT      # serve an existing folder, no rebuild
#
# Options:
#   -s, --spec FILE        deck spec (deck.yaml); titles/sections come from it. Default: read the .pptx
#   -o, --out DIR          output folder (default: <deck folder>/preview-web)
#   -r, --resolution DPI   JPEG resolution for pdftoppm (default 110; ~1467x825 for 16:9)
#   -q, --quality N        JPEG quality 1-100 (default 78)
#       --title TEXT       page title (default: the title slide's title)
#       --subtitle TEXT    line under the title (default: the title slide's date)
#       --lang auto|ja|en  UI words (default auto)
#       --serve [ADDR:]PORT  after building, serve OUT over HTTP in the background.
#                          ADDR defaults to 127.0.0.1 (this machine only).
#       --serve-only [ADDR:]PORT  serve OUT without rebuilding
#
# Env: PYTHON  interpreter for preview_web.py (default python3; it needs python-pptx and PyYAML),
#              e.g. PYTHON="uv run -q --with python-pptx --with pyyaml python"
#
# Exit: 0 done / 1 image count does not match the slide count / 2 usage, missing tool or input,
#       conversion failure, or port already taken by something else.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
usage() { sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'; }
die() { echo "preview_web.sh: $2" >&2; exit "$1"; }

DECK="" SPEC="" OUT="" RES=110 QUAL=78 TITLE="" SUB="" LANGUI=auto SERVE="" BUILD=1
HAVE_TITLE=0 HAVE_SUB=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--spec) SPEC="${2:?}"; shift 2 ;;
    -o|--out) OUT="${2:?}"; shift 2 ;;
    -r|--resolution) RES="${2:?}"; shift 2 ;;
    -q|--quality) QUAL="${2:?}"; shift 2 ;;
    --title) TITLE="${2?}"; HAVE_TITLE=1; shift 2 ;;
    --subtitle) SUB="${2?}"; HAVE_SUB=1; shift 2 ;;
    --lang) LANGUI="${2:?}"; shift 2 ;;
    --serve) SERVE="${2:?--serve needs [ADDR:]PORT}"; shift 2 ;;
    --serve-only) SERVE="${2:?--serve-only needs [ADDR:]PORT}"; BUILD=0; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) die 2 "unknown option $1 (see --help)" ;;
    *) [[ -z "$DECK" ]] || die 2 "one deck at a time ($DECK and $1)"; DECK="$1"; shift ;;
  esac
done
[[ "$RES" =~ ^[0-9]+$ ]] || die 2 "--resolution must be a number"
[[ "$QUAL" =~ ^[0-9]+$ && "$QUAL" -ge 1 && "$QUAL" -le 100 ]] || die 2 "--quality must be 1-100"

# ---------------------------------------------------------------- build
if [[ $BUILD -eq 1 ]]; then
  [[ -n "$DECK" ]] || { usage >&2; exit 2; }
  [[ -f "$DECK" ]] || die 2 "no such deck: $DECK"
  [[ -z "$SPEC" || -f "$SPEC" ]] || die 2 "no such spec: $SPEC"
  command -v soffice >/dev/null || die 2 "LibreOffice (soffice) is not installed"
  command -v pdftoppm >/dev/null || die 2 "pdftoppm is not installed (poppler-utils)"
  OUT="${OUT:-$(dirname "$DECK")/preview-web}"
  mkdir -p "$OUT/img"

  WORK="$(mktemp -d)"
  trap 'rm -rf "${WORK:?}"' EXIT
  # A private LibreOffice profile: a running soffice (or a stale lock) otherwise makes
  # --convert-to return 0 without writing anything.
  cp "$DECK" "$WORK/deck.pptx"
  timeout 900 soffice -env:UserInstallation="file://$WORK/lo" --headless \
    --convert-to pdf --outdir "$WORK" "$WORK/deck.pptx" >"$WORK/soffice.log" 2>&1 || true
  [[ -s "$WORK/deck.pdf" ]] || { cat "$WORK/soffice.log" >&2; die 2 "LibreOffice did not produce a PDF"; }

  # Render into a fresh folder, then swap: a server already serving OUT keeps working,
  # and no stale s-NNN.jpg from a longer deck survives.
  mkdir -p "$WORK/img"
  pdftoppm -r "$RES" -jpeg -jpegopt "quality=$QUAL" "$WORK/deck.pdf" "$WORK/img/s"
  find "$OUT/img" -maxdepth 1 -name 's-*.jpg' -delete
  mv "$WORK"/img/s-*.jpg "$OUT/img/"

  args=("$OUT" --lang "$LANGUI")
  if [[ -n "$SPEC" ]]; then args+=(--spec "$SPEC"); else args+=(--pptx "$DECK"); fi
  [[ $HAVE_TITLE -eq 1 ]] && args+=(--title "$TITLE")
  [[ $HAVE_SUB -eq 1 ]] && args+=(--subtitle "$SUB")
  # shellcheck disable=SC2086  # PYTHON may be a command with arguments
  $PY "$HERE/preview_web.py" "${args[@]}"
fi

# ---------------------------------------------------------------- serve
if [[ -n "$SERVE" ]]; then
  [[ -n "$OUT" ]] || die 2 "--serve-only needs -o OUT (the folder to serve)"
  [[ -f "$OUT/index.html" ]] || die 2 "$OUT/index.html does not exist; build first"
  if [[ "$SERVE" == *:* ]]; then ADDR="${SERVE%:*}"; PORT="${SERVE##*:}"; else ADDR=127.0.0.1; PORT="$SERVE"; fi
  [[ "$PORT" =~ ^[0-9]+$ ]] || die 2 "bad port in $SERVE"
  URL="http://$ADDR:$PORT/"
  if ss -ltnH "( sport = :$PORT )" 2>/dev/null | grep -q .; then
    # Something listens already. If it serves this folder, reuse it; never start a second one.
    if curl -s "$URL" 2>/dev/null | cmp -s - "$OUT/index.html"; then
      echo "already serving $OUT on $URL (reused)"
    else
      die 2 "port $PORT is taken by something else; pick another port (ss -ltnp | grep ':$PORT ')"
    fi
  else
    LOG="${TMPDIR:-/tmp}/preview-web-$PORT.log"
    nohup python3 -m http.server --bind "$ADDR" "$PORT" --directory "$OUT" >"$LOG" 2>&1 < /dev/null &
    disown || true
    ok=0
    for _ in $(seq 1 30); do
      if curl -s -o /dev/null -w '%{http_code}' "$URL" 2>/dev/null | grep -q 200; then ok=1; break; fi
      sleep 0.2
    done
    [[ $ok -eq 1 ]] || die 2 "the server did not answer on $URL (log: $LOG)"
    echo "serving $OUT on $URL  (log: $LOG)"
  fi
  [[ "$ADDR" == 127.0.0.1 || "$ADDR" == localhost ]] && \
    echo "note: $ADDR is reachable from this machine only; for another PC or a phone use e.g. --serve \$(tailscale ip -4):$PORT"
  echo "open:   $URL"
  echo "page N: ${URL}#p12   (any page number after #p)"
  echo "stop:   ss -ltnp | grep ':$PORT '   then   kill <pid>"
fi
