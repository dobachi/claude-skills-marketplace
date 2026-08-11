#!/bin/bash
# 検出器が生きているかを確かめる。README.md の期待値の表を走る形にしたもの。
#
# 「NG が出ない」だけを見ても、検出器が壊れていれば気づけない。
# 欠陥を注入した版で NG が出ること、前提を持たない文書で落ちることまで見る。
#
# 使い方:   ./test_detectors.sh
# 終了コード: 0=全件一致 / 1=食い違いあり
#
# ─────────── 編集点: 検出器を足したら1行足す ───────────
# 書式: 期待exit|コマンド…
# 期待は 0=OK 1=NG 2=引数エラー
CASES=(
  # 正常な版で偽陽性を出していないか
  "0|forbidden_phrases.py     f/clean.md"
  "0|refs_integrity.py        f/clean.md"
  "0|citation_presence.py     f/clean.md"
  "0|declared_counts.py       f/clean.md"
  "0|distribution.py          f/clean.md"
  "0|no_regression.py         f/clean.md f/clean.md"

  # 欠陥を注入した版で検出器が生きているか
  "1|forbidden_phrases.py     f/with_history.md"
  "1|refs_integrity.py        f/broken_ref.md"
  "1|citation_presence.py     f/uncited.md"
  "1|declared_counts.py       f/declared_mismatch.md"
  "1|no_regression.py         f/clean.md f/quotes_emptied.md"

  # 前提を持たない文書で「測定できない」と落ちるか
  "1|refs_integrity.py        f/no_markers.md"
  "1|declared_counts.py       f/no_markers.md"
  "1|distribution.py          f/no_markers.md"
  "1|no_regression.py         f/no_markers.md f/no_markers.md"

  # 第2層の台帳チェック（ゲート側・オフライン）
  "0|spans_verified.py        f/spans_doc.md f/spans_ledger_ok.tsv"
  "1|spans_verified.py        f/spans_doc.md f/spans_ledger_ng.tsv"
  "1|spans_verified.py        f/spans_doc.md f/spans_ledger_fail.tsv"
  "1|spans_verified.py        f/no_markers.md f/spans_ledger_ok.tsv"

  # 噛み合いレポートは判定しない。どの文書でも 0、引数エラーだけ 2
  "0|applicability_report.py  f/no_markers.md"
  "0|applicability_report.py  f/clean.md"
  "2|applicability_report.py"

  # 腐る資料の期限。測定日が無ければ NG
  "1|matrix_freshness.py      f/no_markers.md"
  "2|matrix_freshness.py"

  # ひな型・ネットワークを触るもの・引数エラー
  "2|_template.py"
  "2|span_verify.py"
  "2|refs_integrity.py        f/does_not_exist.md"
)

# 終了コードでは見られない期待。書式: 説明|出るべきでない文字列|コマンド…
ABSENT=(
  "clean.md では候補が出ない|欠落候補 1|citation_presence.py f/clean.md"
)
# ────────────────────────────────────────────────────────
set -u
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 2
# CASES 中の f/ は fixtures/ に展開する（表を読みやすくするためだけの略記）
fail=0
for c in "${CASES[@]}"; do
  want="${c%%|*}"; cmd="${c#*|}"
  cmd="${cmd//f\//fixtures/}"
  # shellcheck disable=SC2086
  python3 $cmd >/dev/null 2>&1
  got=$?
  if [ "$got" = "$want" ]; then
    printf '  OK   exit=%s  %s\n' "$got" "$cmd"
  else
    printf '  NG   exit=%s（期待 %s）  %s\n' "$got" "$want" "$cmd"
    fail=1
  fi
done

for a in "${ABSENT[@]}"; do
  why="${a%%|*}"; rest="${a#*|}"
  needle="${rest%%|*}"; cmd="${rest#*|}"
  cmd="${cmd//f\//fixtures/}"
  # shellcheck disable=SC2086
  if python3 $cmd 2>&1 | grep -qF "$needle"; then
    printf '  NG   「%s」が出た — %s\n' "$needle" "$why"
    fail=1
  else
    printf '  OK   %s\n' "$why"
  fi
done

echo
echo "テスト判定: $([ $fail -eq 0 ] && echo OK || echo NG)"
echo "保証しないこと"
echo "  - 期待値が正しいかは保証しない。fixture 側が壊れれば一緒に壊れる"
echo "  - ここに無い検出器は検査していない（CASES に足すこと）"
exit $fail
