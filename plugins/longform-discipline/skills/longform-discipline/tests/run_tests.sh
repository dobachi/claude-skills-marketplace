#!/bin/bash
# drift_scan.py が生きているかを確かめる。
#
# 「NG が出ない」だけを見ても、検査が壊れていれば気づけない。1.4.1/1.4.2 で
# 実際にそうなった — トークンのタプルを取り違えて表記ゆれ検査が丸ごと無効化
# されていたとき、適合率は「完璧」に見えた。何も実行されていなかったから。
# だからここは3方向を見る:
#
#   1. 正常な版で偽陽性を出さないか        (期待 0)
#   2. 欠陥を注入した版で検査が生きているか  (期待 1)
#   3. 前提を持たない入力で落ちるか         (期待 2)
#
# --only を使って検査を1つずつ分離するので、終了コードだけで
# 「その検査が発火したか」を判定できる。
#
# 使い方:   ./run_tests.sh
# 終了コード: 0=全件一致 / 1=食い違いあり
set -u
cd "$(dirname "$0")" || exit 2
SCAN="../scripts/drift_scan.py"
f="fixtures"

# ─────────── 編集点: 検査を足したら、両方向の行を足す ───────────
# 書式1: 期待exit|drift_scan.py への引数
#   期待は 0=指摘なし / 1=指摘あり / 2=引数・読み取りエラー
# 書式2: has:<検査名>|引数   その検査が出力に現れること
#        no:<検査名>|引数    現れないこと
#   info 段の検査 (unverified-claim / intent-open / open-marker /
#   repeated-opener / unsourced-assertion) は終了コードを 1 にしない。
#   下書き中に常に赤いゲートは無視されるので、それは意図した設計。
#   だから終了コードだけでは検査の生死を判定できず、この形式が要る。
CASES=(
  # ---- 文書まるごと: 正常な版で騒がないか ----
  "0|$f/clean.md      --spine $f/clean.spine.md"
  "0|$f/conform.md    --spine $f/decl.spine.md"
  "0|$f/content-ok.md --spine $f/content.spine.md"
  "0|$f/intent.md     --spine $f/intent-ok.spine.md"

  # ---- 文書まるごと: 欠陥を注入した版で検査が生きているか ----
  "1|$f/dirty.md      --spine $f/dirty.spine.md"
  "1|$f/decl.md       --spine $f/decl.spine.md"
  "1|$f/content.md    --spine $f/content.spine.md"
  "1|$f/intent.md     --spine $f/intent.spine.md"

  # ---- 表層の検査を1つずつ ----
  "1|$f/dirty.md --spine $f/dirty.spine.md --only style-mixing"
  "0|$f/clean.md --spine $f/clean.spine.md --only style-mixing"
  "1|$f/dirty.md --spine $f/dirty.spine.md --only long-sentence"
  "0|$f/clean.md --spine $f/clean.spine.md --only long-sentence"
  "1|$f/dirty.md --spine $f/dirty.spine.md --only glossary-violation"
  "0|$f/clean.md --spine $f/clean.spine.md --only glossary-violation"
  "1|$f/dirty.md --spine $f/dirty.spine.md --only cross-section-dup"
  "0|$f/clean.md --spine $f/clean.spine.md --only cross-section-dup"
  "1|$f/dirty.md --spine $f/dirty.spine.md --only redundant-expression"
  "0|$f/clean.md --spine $f/clean.spine.md --only redundant-expression"
  "1|$f/dirty.md --spine $f/dirty.spine.md --only section-imbalance"
  "1|$f/decl.md  --spine $f/decl.spine.md  --only declared-style-violation"
  "0|$f/conform.md --spine $f/decl.spine.md --only declared-style-violation"
  "1|$f/num.md      --only numeric-inconsistency"
  "0|$f/clean.md    --only numeric-inconsistency"
  "has:unsourced-assertion|$f/assert.md --only unsourced-assertion"
  "no:unsourced-assertion|$f/clean.md   --only unsourced-assertion"
  "has:open-marker|$f/dirty.md --spine $f/dirty.spine.md --only open-marker"
  "no:open-marker|$f/clean.md  --spine $f/clean.spine.md --only open-marker"
  "has:repeated-opener|$f/opener.md   --only repeated-opener"
  "has:repeated-opener|$f/openeren.md --only repeated-opener"
  "no:repeated-opener|$f/clean.md     --only repeated-opener"
  "1|$f/notation.md --only notation-drift"      # 要 sudachipy。無ければ SKIP される
  "0|$f/clean.md    --only notation-drift"

  # ---- 内容・意図の検査を1つずつ ----
  "1|$f/content.md    --spine $f/content.spine.md --only claim-coverage"
  "0|$f/content-ok.md --spine $f/content.spine.md --only claim-coverage"
  "1|$f/content.md    --spine $f/content.spine.md --only term-before-definition"
  "0|$f/content-ok.md --spine $f/content.spine.md --only term-before-definition"
  "1|$f/intent.md     --spine $f/intent.spine.md  --only intent-unmeasurable"
  "0|$f/intent.md     --spine $f/intent-ok.spine.md --only intent-unmeasurable"
  "1|$f/intent.md     --spine $f/intent.spine.md  --only intent-uncovered"
  "0|$f/intent.md     --spine $f/intent-ok.spine.md --only intent-uncovered"

  # ---- 矛盾 (段2: 型のある事実 / 段3: 台帳による絞り込み) ----
  "1|$f/conflict.md    --only fact-conflict"
  "0|$f/conflict-ok.md --only fact-conflict"
  "0|$f/clean.md       --only fact-conflict"
  "has:claim-conflict-candidate|$f/conflict.md --spine $f/conflict.spine.md --only claim-conflict-candidate"
  "no:claim-conflict-candidate|$f/conflict.md --only claim-conflict-candidate"

  # ---- 入れ子の文書 (1.4.1 / 1.4.2 の回帰) ----
  # 章見出しの直後が小見出しの文書。平坦なフィクスチャだけで検証していたせいで
  # 3つの検査が確信をもって誤る欠陥を出荷した。ここが常設の防波堤。
  "0|$f/nested.md --spine $f/nested.spine.md    --only claim-coverage"
  "0|$f/nested.md --spine $f/nested.spine.md    --only intent-uncovered"
  "1|$f/nested.md --spine $f/nested.spine.md    --only term-before-definition"
  "0|$f/nested.md --spine $f/nested-ok.spine.md"

  # ---- スパイン無しなら内容・意図の検査は一切走らない ----
  "0|$f/content.md --only claim-coverage"
  "no:unverified-claim|$f/content.md --only unverified-claim"
  "has:unverified-claim|$f/content.md --spine $f/content.spine.md --only unverified-claim"
  "has:intent-open|$f/intent.md --spine $f/intent.spine.md --only intent-open"
  "no:intent-open|$f/intent.md  --spine $f/intent-ok.spine.md --only intent-open"
  "0|$f/intent.md  --only intent-unmeasurable"

  # ---- 未記入のテンプレートを推測しない ----
  "0|$f/decl.md --spine $f/tmpl.spine.md --only declared-style-violation"

  # ---- 引数・読み取りエラーは 2。1 (=指摘あり) と混ざらないこと ----
  "2|$f/does_not_exist.md"
  "2|$f/clean.md --spine $f/does_not_exist.spine.md"
  "2|$f/clean.md --only bogus-check"
  "2|"
)

pass=0; fail=0; skipped=0
HAS_SUDACHI=$(python3 -c "import sudachipy" 2>/dev/null && echo yes || echo no)

for case in "${CASES[@]}"; do
  want="${case%%|*}"; args="${case#*|}"
  # shellcheck disable=SC2086
  out=$(python3 "$SCAN" $args 2>&1); got=$?
  if [ "$args" = "$f/notation.md --only notation-drift" ] && [ "$HAS_SUDACHI" = "no" ]; then
    printf "  SKIP exit=%s  %s  (sudachipy 未導入)\n" "$got" "$args"; skipped=$((skipped+1)); continue
  fi
  case "$want" in
    has:*|no:*)
      check="${want#*:}"
      if printf '%s' "$out" | grep -q "\[$check\]"; then present=yes; else present=no; fi
      [ "${want%%:*}" = "has" ] && expect=yes || expect=no
      if [ "$present" = "$expect" ]; then
        printf "  OK   %-3s [%s]  %s\n" "${want%%:*}" "$check" "$args"; pass=$((pass+1))
      else
        printf "  NG   %-3s [%s] が %s  %s\n" "${want%%:*}" "$check" \
               "$([ "$present" = yes ] && echo 出た || echo 出ない)" "$args"
        fail=$((fail+1))
      fi
      ;;
    *)
      if [ "$got" = "$want" ]; then
        printf "  OK   exit=%s  %s\n" "$got" "$args"; pass=$((pass+1))
      else
        printf "  NG   exit=%s (期待 %s)  %s\n" "$got" "$want" "$args"
        printf "       %s\n" "$(printf '%s' "$out" | head -3)"
        fail=$((fail+1))
      fi
      ;;
  esac
done

# 検査名がひとつ残らず SKILL.md に文書化されているか。
# 実装だけ足して文書を忘れると、使う側から見えない検査になる。
undoc=$(python3 - <<'PY'
import re, pathlib
here = pathlib.Path(__file__).resolve().parent if "__file__" in dir() else pathlib.Path(".")
root = pathlib.Path("..").resolve()
script = (root / "scripts/drift_scan.py").read_text()
skill = (root / "SKILL.md").read_text()
checks = set(re.findall(r'"([a-z-]+)"', re.search(r"CHECKS = \[(.*?)\]", script, re.S).group(1)))
doc = set(re.findall(r"\| `([a-z-]+)` \|", skill))
print(" ".join(sorted(checks - doc)))
PY
)
if [ -z "$undoc" ]; then
  printf "  OK   全ての検査名が SKILL.md に記載されている\n"; pass=$((pass+1))
else
  printf "  NG   SKILL.md に無い検査: %s\n" "$undoc"; fail=$((fail+1))
fi

echo
echo "テスト判定: $([ "$fail" -eq 0 ] && echo OK || echo NG)  (成功 $pass / 失敗 $fail / スキップ $skipped)"
echo "保証しないこと"
echo "  - 期待値が正しいかは保証しない。fixture 側が壊れれば一緒に壊れる"
echo "  - CASES に無い検査は見ていない（検査を足したら両方向の行を足すこと）"
echo "  - SKILL.md の指示が意図通り働くかは見ていない。それは evals/evals.json"
[ "$fail" -eq 0 ] || exit 1
