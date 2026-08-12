#!/usr/bin/env bash
# kb-check.py / kb-graph.py のテスト。固定フィクスチャのみを使い、/tmp は使わない。
#
# 三方向:
#   clean    → 終了 0・警告0（検出器が鳴りすぎないこと）
#   broken   → 終了 1・注入した欠陥がすべて名指しで出ること
#   empty    → 終了 2（KBが1つも無い＝前提不成立をエラーと区別する）
#
# 使い方: bash tests/run_tests.sh
# 終了コード: 0 = 全通過, 1 = 失敗あり

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="$(dirname "$HERE")"
FIX="$HERE/fixtures"
CHECK="python3 $SKILL/scripts/kb-check.py"
GRAPH="python3 $SKILL/scripts/kb-graph.py"
fails=0

pass() { printf '  ok   %s\n' "$1"; }
fail() { printf '  FAIL %s\n' "$1"; fails=$((fails + 1)); }

expect_exit() { # <期待コード> <説明> <コマンド...>
  local want="$1" name="$2"; shift 2
  "$@" >/dev/null 2>&1
  local got=$?
  [ "$got" = "$want" ] && pass "$name (exit $got)" || fail "$name: exit $got, 期待 $want"
}

expect_has() { # <説明> <出力> <部分文字列>
  case "$2" in
    *"$3"*) pass "$1" ;;
    *) fail "$1: 出力に '$3' が無い" ;;
  esac
}

expect_lacks() { # <説明> <出力> <部分文字列>
  case "$2" in
    *"$3"*) fail "$1: 出力に '$3' が出てはいけない" ;;
    *) pass "$1" ;;
  esac
}

echo "== 方向1: 正常なKB =="
clean_out="$($CHECK "$FIX/clean" 2>&1)"
expect_exit 0 "clean は 0 で終わる" $CHECK "$FIX/clean"
expect_has "clean は無警告" "$clean_out" "エラー: 0  警告: 0"
expect_has "prose にも関係が読める" "$clean_out" "recipes (prose): 5 records, 5 relations"
# 対称な関係（related / contrasts_with）を「導出専用の向き」と誤検出した回帰の番人
expect_lacks "対称な関係を誤検出しない" "$clean_out" "導出専用"

echo "== 方向2: 欠陥を注入したKB =="
broken_out="$($CHECK "$FIX/broken" 2>&1)"
expect_exit 1 "broken は 1 で終わる" $CHECK "$FIX/broken"
expect_has "INDEX 欠落"        "$broken_out" "INDEX 'INDEX.md' が無い"
expect_has "id パターン違反"    "$broken_out" "id 'bad id' がパターン違反"
expect_has "自己参照"          "$broken_out" "が自分自身を指している"
expect_has "entities 必須欠落"  "$broken_out" "必須 'name' が無い"
expect_has "未解決の関係"       "$broken_out" "-> 'sharpen-before-it-is-dull' が未解決"
expect_has "語彙外の関係名"     "$broken_out" "relations.causes は語彙外"
expect_has "導出向きの誤記"     "$broken_out" "relations.applied_by は導出専用の向き"
expect_has "未解決の本文リンク" "$broken_out" "本文リンク [[stone-grit-guide]] が未解決"
expect_has "本文と関係のずれ"   "$broken_out" "本文は kitchen/knife-care を参照しているが relations に無い"
expect_has "INDEX のリンク切れ" "$broken_out" "リンク (gone-missing.md) の参照先が無い"

echo "== 方向3: 前提が無い =="
expect_exit 2 "KB が無ければ 2" $CHECK "$FIX/empty"

echo "== kb-graph =="
nb="$($GRAPH "$FIX/clean" --neighbors taste-as-you-go 2>&1)"
expect_has "逆向きを導出する"     "$nb" "<-applied_by- recipes/salt-the-water"
expect_has "書かれていない側は空" "$nb" "書かれている関係 (out):"
sum="$($GRAPH "$FIX/clean" 2>&1)"
expect_has "関係を数える"     "$sum" "関係: 6"
expect_has "KBをまたぐ関係"   "$sum" "KBをまたぐ関係: 2"
path="$($GRAPH "$FIX/clean" --path searing-is-not-sealing salt-the-water 2>&1)"
expect_has "経路を辿れる"     "$path" "salt-the-water"
orph="$($GRAPH "$FIX/broken" --orphans 2>&1)"
expect_has "孤立を見つける"   "$orph" "mise-en-place"
mer="$($GRAPH "$FIX/clean" --mermaid 2>&1)"
expect_has "Mermaid を出す"   "$mer" "flowchart LR"
expect_exit 1 "未知のidは失敗させる" $GRAPH "$FIX/clean" --neighbors no-such-record

echo
if [ "$fails" -eq 0 ]; then
  echo "全通過"
  exit 0
fi
echo "失敗: $fails"
exit 1
