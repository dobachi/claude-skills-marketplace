#!/bin/bash
# extract_deck.py（既存 .pptx → spec の抽出）と roundtrip_check.py が生きているかを
# 確かめる。
#
# 「抽出できた」だけを見ても意味がない。抽出器が静かに内容を落としていても、
# 出力は「きれいな spec」に見えるからだ。だから3方向を見る:
#
#   1. 正常系: build_deck.py が作ったデッキを抽出し、型・タイトル・全テキストが
#      戻ることを roundtrip_check.py で照合する            (期待 0)
#   2. 欠陥注入: (a) spec を1行書き換えた版で比較器が差を検出するか (期待 1)
#                (b) 手書き相当の乱雑なデッキで LOSS を報告するか   (期待 1)
#   3. 前提なし: .pptx でないファイル / 存在しないファイル         (期待 2)
#
# さらに連結テスト: 乱雑なデッキ → 抽出 → 再ビルド → audit_pptx.py が
# エラー0 になること（リファクタリングの成立条件そのもの）。
#
# 使い方:   ./run_tests.sh
# 終了コード: 0=全件一致 / 1=食い違いあり
set -u
cd "$(dirname "$0")" || exit 2
A="../assets"
f="fixtures"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# 依存が無い環境（CI の素の runner、python-pptx 未インストールの手元）では、
# 全ケースが ModuleNotFoundError で落ちて「スキルが壊れている」ように見える。
# それは嘘なので、検査を実行できないことを明示して抜ける。CI は
# assets/requirements.txt を入れてから呼ぶので、ここは通らない。
if ! python3 -c "import pptx, yaml" >/dev/null 2>&1; then
  echo "SKIP  python-pptx / PyYAML が無いため、このハーネスは何も検査していない"
  echo "      入れるには: pip install -r ../assets/requirements.txt"
  exit 0
fi

# ─────────── 編集点: 検査を足したら、両方向の行を足す ───────────
# 書式1: 期待exit|コマンド行        0=指摘なし / 1=指摘あり / 2=前提エラー
# 書式2: has:<文字列>|コマンド行    その文字列が出力に現れること
CASES=(
  # ---- 正常系: 自前の出力は無損失で戻る ----
  "0|python3 $A/extract_deck.py $f/clean-deck.pptx -o $TMP/clean.yaml"
  "0|python3 roundtrip_check.py $f/clean-deck.yaml $f/clean-deck.pptx"

  # ---- 欠陥注入(a): 比較器が差を検出できるか ----
  "1|python3 roundtrip_check.py $f/mutated-deck.yaml $f/clean-deck.pptx"

  # ---- 欠陥注入(b): 表現できない内容を LOSS として報告するか ----
  "1|python3 $A/extract_deck.py $f/messy-deck.pptx -o $TMP/messy.yaml"
  "has:grouped drawing|python3 $A/extract_deck.py $f/messy-deck.pptx -o $TMP/messy2.yaml"
  "has:exploded pie|python3 $A/extract_deck.py $f/messy-deck.pptx -o $TMP/messy3.yaml"

  # ---- 前提なし ----
  "2|python3 $A/extract_deck.py $f/not-a-deck.txt -o $TMP/x.yaml"
  "2|python3 $A/extract_deck.py $f/does-not-exist.pptx -o $TMP/x.yaml"
  "2|python3 roundtrip_check.py $f/clean-deck.yaml"
)

pass=0; fail=0
run() { eval "$1" >"$TMP/out" 2>&1; echo $?; }

for case in "${CASES[@]}"; do
  want="${case%%|*}"; cmd="${case#*|}"
  code="$(run "$cmd")"
  if [[ "$want" == has:* ]]; then
    needle="${want#has:}"
    if grep -qF -- "$needle" "$TMP/out"; then
      pass=$((pass+1))
    else
      fail=$((fail+1)); echo "NG  出力に次の文字列がない: $needle"; echo "    $cmd"
    fi
  elif [[ "$code" == "$want" ]]; then
    pass=$((pass+1))
  else
    fail=$((fail+1)); echo "NG  期待 exit=$want 実際 exit=$code"; echo "    $cmd"
    sed -n 1,8p "$TMP/out" | sed 's/^/    | /'
  fi
done

# ---- 連結: 乱雑なデッキを抽出して作り直すと、マスタ準拠のデッキになる ----
python3 "$A/extract_deck.py" "$f/messy-deck.pptx" -o "$TMP/chain.yaml" >/dev/null 2>&1
if python3 "$A/build_deck.py" "$TMP/chain.yaml" -o "$TMP/chain.pptx" >/dev/null 2>&1 \
   && python3 "$A/audit_pptx.py" "$TMP/chain.pptx" --quiet >"$TMP/audit" 2>&1; then
  pass=$((pass+1))
else
  fail=$((fail+1)); echo "NG  抽出→再ビルド→audit の連結が通らない"; sed -n 1,10p "$TMP/audit" | sed 's/^/    | /'
fi

echo "合格 $pass / 不合格 $fail"
[[ $fail -eq 0 ]] || exit 1
