#!/bin/bash
# ゲートの例。停止条件は検出器の集合で組む（SKILL.md 手順4）。
# 1本だけをゲートにすると、通った瞬間に別の1本が落ちる。
#
# 使い方:   BASE=編集前.md ./gate.sh 対象.md
# 終了コード: 0=全部OK / 1=どれかNG
#
# ─────────── 編集点: この文書で回す検出器を並べる ───────────
# 消せば満たせる検出器しか無いゲートは意味を持たない。
# no_regression.py を必ず混ぜること（BASE 未設定なら下限が無いまま回る）
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/detectors" && pwd)"
TARGET="${1:?対象ファイルを渡す}"
BASE="${BASE:-}"

fail=0
for d in refs_integrity declared_counts citation_presence forbidden_phrases; do
  python3 "$DIR/$d.py" "$TARGET" || fail=1
done

if [ -n "$BASE" ]; then
  python3 "$DIR/no_regression.py" "$BASE" "$TARGET" || fail=1
else
  echo "⚠️ BASE 未設定。単調性の下限が無い＝消せば満たせる状態で回している"
  fail=1
fi
# ────────────────────────────────────────────────────────────

echo
echo "ゲート判定: $([ $fail -eq 0 ] && echo OK || echo NG)"
exit $fail
