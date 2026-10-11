#!/bin/bash
# dict_scan.py と同梱辞書が生きているかを確かめる。
#
# 「候補なし」だけを見ても、検査が壊れていれば気づけない。だから3方向を見る:
#
#   1. 自然な文章で騒がないか            (期待 0)
#   2. 欠陥を入れた文章で当たるか        (期待 1)
#   3. 前提を欠く入力で落ちるか          (期待 2)
#
# 加えて、--selftest が辞書の全見出し語について「自分の example に当たり、
# counter に当たらない」ことを確かめる。辞書に語を足したら、ここが最初の関門になる。
#
# 使い方:   ./run_tests.sh
# 終了コード: 0=全件一致 / 1=食い違いあり
set -u
cd "$(dirname "$0")" || exit 2
SCAN="../scripts/dict_scan.py"
f="fixtures"

# ─────────── 編集点: 検査を足したら、両方向の行を足す ───────────
# 書式1: 期待exit|dict_scan.py への引数
# 書式2: has:<文字列>|引数   出力にその文字列が現れること
#        no:<文字列>|引数    現れないこと
# どの行も --no-local 付きで実行する（作業ディレクトリの辞書に左右されないため）。
CASES=(
  # ---- 辞書そのもの ----
  "0|--selftest"
  "1|--selftest --dict $f/nomatch.ini"
  "2|--selftest --dict $f/broken.ini"

  # ---- 自然な文章で騒がないか。コード・前付け・URL・引用キーは読まない ----
  "0|$f/clean.md"
  "no:羅針盤|$f/clean.md"
  # 見出し専用の語は、本文の行末にあっても当たらない
  "no:head-nitsuite|$f/clean.md"

  # ---- 欠陥を入れた文章で、カテゴリごとに当たるか ----
  "1|$f/dirty.md"
  "has:wago-kiku [見出し]|$f/dirty.md"
  "has:head-nitsuite|$f/dirty.md"
  "has:wago-otoshikomu|$f/dirty.md"
  "has:meta-rashinban|$f/dirty.md"
  "has:meta-tabi|$f/dirty.md"
  "has:vogue-kaizodo|$f/dirty.md"
  "has:crown-kagi|$f/dirty.md"
  "has:calque-endofday|$f/dirty.md"
  "has:calque-samepage|$f/dirty.md"
  "has:light-eikyo|$f/dirty.md"
  "has:set-hopehelps|$f/dirty.md"
  "has:kata-empower|$f/dirty.md"
  "has:scaf-honsetsu|$f/dirty.md"
  "has:hedge-toieru|$f/dirty.md"
  "has:self-shojiki|$f/dirty.md"
  "has:infl-juyo|$f/dirty.md"
  "has:conn-koreniyori|$f/dirty.md"
  "no:wago-nigiru|$f/dirty.md"
  "has:meas-tekisetsu|$f/dirty.md"
  "has:meas-fukaketsu|$f/dirty.md"
  "has:hype-kakumei|$f/dirty.md"
  "has:hype-ohaba|$f/dirty.md"
  "has:closer-chumoku|$f/dirty.md"
  "has:red-mazusaisho|$f/dirty.md"
  "has:red-kakugoto|$f/dirty.md"
  "has:red-jisshi|$f/dirty.md"
  "has:kata-consensus|$f/dirty.md"

  # ---- 根拠の強さ: 表示され、絞り込める ----
  "has:(measured)|$f/dirty.md"
  "has:根拠の強さ|$f/dirty.md --summary"
  "has:meas-tekisetsu|$f/dirty.md --evidence measured"
  "no:hype-kakumei|$f/dirty.md --evidence measured"
  "no:meas-tekisetsu|$f/dirty.md --evidence folk"
  "2|$f/dirty.md --evidence nonsense"

  # ---- 絞り込み ----
  "1|$f/dirty.md --only vogue"
  "no:meta-rashinban|$f/dirty.md --only vogue"
  "0|$f/dirty.md --only wago-tatamu"
  "2|$f/dirty.md --only no-such-category"

  # ---- この repo の文書と形の違う入力 ----
  # 見出しも記法も無い平文
  "1|$f/plain.txt"
  "has:meta-zasho|$f/plain.txt"
  "has:wago-yoseru|$f/plain.txt"
  # Quarto: 前付け、見出し属性、相互参照、引用キー、~~~ のコード、表
  "1|$f/quarto.qmd"
  "has:meta-dodai|$f/quarto.qmd"
  "no:meta-honmaru|$f/quarto.qmd"
  "no:meta-zasho|$f/quarto.qmd"
  "no:meta-monosashi|$f/quarto.qmd"
  "no:wago-tatamu|$f/quarto.qmd"

  # ---- 許可リスト: 残すと決めた語句は黙る。同じ語の別の使い方は黙らない ----
  "0|$f/quarto.qmd --allow $f/allow.txt"
  "1|$f/terms.md --allow $f/allow.txt"
  "has:この分類が見直しに効く|$f/terms.md --allow $f/allow.txt"
  "2|$f/terms.md --allow $f/unknown-allow.txt"
  "2|$f/terms.md --allow $f/no-such-file.txt"

  # ---- プロジェクト辞書を重ねる ----
  "0|$f/quarto.qmd --allow $f/allow.txt --only vogue"
  "1|$f/quarto.qmd --allow $f/allow.txt --dict $f/project.ini"
  "has:proj-kimo|$f/quarto.qmd --allow $f/allow.txt --dict $f/project.ini"

  # ---- 出力形式 ----
  "has:decision|$f/dirty.md --format tsv"
  "has:\"id\": \"wago-kiku\"|$f/dirty.md --format json"
  "has:候補 |$f/dirty.md --summary"
  "no:→|$f/dirty.md --summary"

  # ---- 見出しの一覧: 文になっている見出しに印が付く。終了コードは 0 ----
  "0|$f/dirty.md --headings"
  "has:文	  この分類が見直しに効く|$f/dirty.md --headings"
  "no:文	データ連携について|$f/dirty.md --headings"

  # ---- 前提を欠く入力 ----
  "2|$f/no-such-file.md"
  "2|"
  "2|$f/dirty.md --lang xx"
  "2|$f/dirty.md --dict $f/broken.ini"
)
# ─────────────────────────────────────────────────────────────

fail=0
for c in "${CASES[@]}"; do
  expect="${c%%|*}"; args="${c#*|}"
  # shellcheck disable=SC2086
  out=$(python3 "$SCAN" --no-local $args 2>&1); got=$?
  case "$expect" in
    has:*) needle="${expect#has:}"
           if ! grep -qF -- "$needle" <<<"$out"; then
             echo "NG  出力に無い「$needle」: $args"; fail=1; fi ;;
    no:*)  needle="${expect#no:}"
           if grep -qF -- "$needle" <<<"$out"; then
             echo "NG  出力に現れた「$needle」: $args"; fail=1; fi ;;
    *)     if [ "$got" != "$expect" ]; then
             echo "NG  期待 $expect / 実際 $got: $args"; fail=1; fi ;;
  esac
done

# カレントディレクトリの辞書・許可リストを自動で読むこと
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
cp "$f/allow.txt" "$tmp/.ai-tell-allow.txt"; cp "$f/project.ini" "$tmp/.ai-tell-dict.ini"
abs_scan="$(cd "$(dirname "$SCAN")" && pwd)/dict_scan.py"; abs_f="$(cd "$f" && pwd)"
out=$(cd "$tmp" && python3 "$abs_scan" "$abs_f/quarto.qmd" 2>&1); got=$?
if [ "$got" != 1 ] || ! grep -qF "proj-kimo" <<<"$out" || grep -qF "wago-kiku" <<<"$out"; then
  echo "NG  カレントディレクトリの辞書・許可リストが読まれていない"; fail=1; fi

[ "$fail" = 0 ] && echo "OK  ${#CASES[@]} 件 + 自動読み込み 1 件"
exit "$fail"
