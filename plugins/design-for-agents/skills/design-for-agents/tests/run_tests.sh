#!/usr/bin/env bash
# 検出器の陽性対照と陰性対照。
#
#   0  すべて通った
#   1  失敗あり
#   2  検査できない（python-pptx か pptx-build が無い）
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="$(dirname "$HERE")"
BUILD="$SKILL/../../../pptx-build/skills/pptx-build/assets"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

python3 -c "import pptx" 2>/dev/null || { echo "python-pptx が無い (pip install -r assets/requirements.txt)"; exit 2; }
[ -f "$BUILD/build_deck.py" ] || { echo "pptx-build が見つからない: $BUILD"; exit 2; }

fail=0
say() { printf "  %-8s %s\n" "$1" "$2"; }

echo "陽性対照 — pptx-build のサンプルは違反なしで通ること"
for y in "$BUILD"/samples/*.yaml; do
  n="$(basename "$y" .yaml)"
  python3 "$BUILD/build_deck.py" "$y" --out "$TMP/$n.pptx" >/dev/null 2>&1 \
    || { say NG "$n のビルドに失敗"; fail=1; continue; }
  if python3 "$SKILL/scripts/check_deck.py" "$TMP/$n.pptx" >/dev/null 2>&1; then
    say OK "$n"
  else
    say NG "$n が違反を出した（偽陽性）"
    python3 "$SKILL/scripts/check_deck.py" "$TMP/$n.pptx" 2>&1 | grep "^  違反" | sed 's/^/        /'
    fail=1
  fi
done

echo "陰性対照 — 欠陥を注入したデッキで、狙った条件が発火すること"
SRC="$(ls "$TMP"/*.pptx | head -1)"
python3 "$HERE/make_broken.py" "$SRC" "$TMP/broken.pptx" >/dev/null || { echo "注入に失敗"; exit 2; }
python3 "$SKILL/scripts/check_deck.py" "$TMP/broken.pptx" 2>&1 \
  | grep -oE "違反 [a-z0-9#-]+" | sed 's/違反 //' | sort -u > "$TMP/fired.txt"

python3 - "$HERE" "$TMP/fired.txt" <<'PY'
import sys, pathlib, importlib.util
here, fired_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("mb", pathlib.Path(here) / "make_broken.py")
mb = importlib.util.module_from_spec(spec); spec.loader.exec_module(mb)
fired = set(pathlib.Path(fired_path).read_text().split())
want = {c for cs in mb.INJECTED.values() for c in cs}
missing = sorted(want - fired)
for c in sorted(want & fired):
    print(f"  OK       {c}")
for c in missing:
    print(f"  NG       {c} — 欠陥を注入したのに発火しなかった")
for c, why in mb.NOT_INJECTABLE.items():
    print(f"  対象外   {c} — {why}")
sys.exit(1 if missing else 0)
PY
[ $? -ne 0 ] && fail=1

# 下限: 注入した条件が減っていないか（検査を消して通すのを防ぐ）
n_want=$(python3 -c "
import importlib.util,pathlib,sys
spec=importlib.util.spec_from_file_location('mb',pathlib.Path('$HERE')/'make_broken.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
print(len({c for cs in m.INJECTED.values() for c in cs}))")
if [ "$n_want" -lt 20 ]; then
  echo "下限を割っている: 陰性対照が狙う条件が $n_want 件（20 件以上が必要）"; exit 2
fi

echo
if [ "$fail" -eq 0 ]; then echo "すべて通った（陰性対照 $n_want 条件）"; else echo "失敗あり"; fi
exit "$fail"
