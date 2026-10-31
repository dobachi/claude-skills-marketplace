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

  # ---- 正常系: 構図の型（statement/cards/steps/matrix/split）が型として戻る ----
  "0|python3 $A/extract_deck.py $f/archetype-deck.pptx -o $TMP/arch.yaml"
  "0|python3 roundtrip_check.py $f/archetype-deck.yaml $f/archetype-deck.pptx"
  "0|python3 $A/validate_deck.py $f/archetype-deck.yaml"
  "0|python3 $A/audit_pptx.py $f/archetype-deck.pptx --quiet"

  # ---- 正常系: いま生成したデッキでも成り立つか ----
  # 固定フィクスチャだけを見ていると、build_deck.py 側の退行（パーツの命名を
  # 失う等）に気づけない。その場でビルドして、監査と往復の両方にかける。
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/fresh.pptx"
  "0|python3 $A/audit_pptx.py $TMP/fresh.pptx --quiet"
  "0|python3 roundtrip_check.py $f/archetype-deck.yaml $TMP/fresh.pptx"

  # ---- 同梱テーマ: どの見た目でも構図と監査が壊れないか ----
  # テーマは色・書体・造形の値しか変えない。値を変えたら監査が落ちる、という
  # 状態になっていないことを、明暗の両方で確かめる。
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/t1.pptx --theme $A/themes/editorial.json"
  "0|python3 $A/audit_pptx.py $TMP/t1.pptx --quiet"
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/t2.pptx --theme $A/themes/warm.json"
  "0|python3 $A/audit_pptx.py $TMP/t2.pptx --quiet"
  "0|python3 $A/build_deck.py $f/archetype-deck.yaml -o $TMP/t3.pptx --theme $A/themes/slate-dark.json"
  "0|python3 $A/audit_pptx.py $TMP/t3.pptx --quiet"

  # ---- テンプレート流し込み: 出典・章の名前・章番号が名前つきプレースホルダに入るか ----
  # 置き場のあるテンプレートでは全部プレースホルダに入り、置き去りのテキストボックスが
  # 出ない (0)。置き場のないテンプレートでは、出典を黙って落とさず警告する (1)。
  "0|python3 template_annot_check.py"
  "1|python3 template_annot_check.py --no-source"
  "has:期待どおり 1 を返す|python3 template_annot_check.py --no-source"

  # ---- panels: 2列の文章と編集できる図を1枚に組む ----
  # 4種の図（stacked_bar / staircase / flow / chips）と下段のまとめを含む版を
  # その場でビルドし、監査を通す (0)。描けない図の種類は検証で止める (1)。
  "0|python3 $A/validate_deck.py $f/panels-deck.yaml"
  "0|python3 $A/build_deck.py $f/panels-deck.yaml -o $TMP/panels.pptx"
  "0|python3 $A/audit_pptx.py $TMP/panels.pptx --quiet"
  "1|python3 $A/validate_deck.py $f/bad-panels.yaml"
  "has:panels figure kind 'pie'|python3 $A/validate_deck.py $f/bad-panels.yaml"

  # ---- 編集できる図: figure 型 / split の figure: / diagram 種 ----
  # 描いた図は画像ではなく素の部品で置く。生成・監査を通し (0)、描いた図を
  # 画像で貼る宣言（image_kind: drawing）、未知の種類、宙に浮いた矢印、
  # 図も画像もない split を検証で止める (1)。抽出器は素の図を黙って箇条書きに
  # せず、読み戻せないと報告する (1)。
  "0|python3 $A/validate_deck.py $f/figure-deck.yaml"
  "0|python3 $A/build_deck.py $f/figure-deck.yaml -o $TMP/figure.pptx"
  "0|python3 $A/audit_pptx.py $TMP/figure.pptx --quiet"
  "1|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:image_kind: drawing|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:edge names unknown node 'zz'|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:looks like a drawing, not a photograph|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "has:it needs \`figure:\`|python3 $A/validate_deck.py $f/bad-figure.yaml"
  "1|python3 $A/extract_deck.py $TMP/figure.pptx -o $TMP/figure-back.yaml"
  "has:native figure parts|python3 $A/extract_deck.py $TMP/figure.pptx -o $TMP/figure-back2.yaml"

  # ---- 1 枚物の型と lead: 行 ----
  # 報告ブリーフ（N 列 panels + 矢印）、進捗ダッシュボード（tiles）、計画タイムライン、
  # 意思決定メモ、イベント報告、lead: つきの箇条書き・表・2 列をビルドして監査を通す (0)。
  # tiles のない dashboard、5 列、選択肢にない推奨、7 枚のタイルは検証で止める (1)。
  "0|python3 $A/validate_deck.py $f/onepagers-deck.yaml --text $TMP/deck-text.md"
  "has:## 1. Launch slips two weeks|cat $TMP/deck-text.md"
  "has:**The hardware passed|cat $TMP/deck-text.md"
  "0|python3 $A/build_deck.py $f/onepagers-deck.yaml -o $TMP/onepagers.pptx"
  "0|python3 $A/audit_pptx.py $TMP/onepagers.pptx --quiet"
  "1|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:dashboard has no \`tiles:\`|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:5 columns|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:recommend.option 'C' is not one of|python3 $A/validate_deck.py $f/bad-onepagers.yaml"
  "has:7 tile(s)|python3 $A/validate_deck.py $f/bad-onepagers.yaml"

  # ---- 同梱サンプルの 1 枚物 5 本: 検証・生成・監査が通る ----
  "0|python3 $A/validate_deck.py $A/samples/onepager-brief.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-brief.yaml -o $TMP/s1.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s1.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-dashboard.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-dashboard.yaml -o $TMP/s2.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s2.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-timeline.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-timeline.yaml -o $TMP/s3.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s3.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-decision.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-decision.yaml -o $TMP/s4.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s4.pptx --quiet"
  "0|python3 $A/validate_deck.py $A/samples/onepager-event.yaml"
  "0|python3 $A/build_deck.py $A/samples/onepager-event.yaml -o $TMP/s5.pptx"
  "0|python3 $A/audit_pptx.py $TMP/s5.pptx --quiet"

  # ---- AI っぽさの癖: 検証器がデッキ単位で拾う ----
  # 全部「ラベル: 説明」の箇条書き、3 項目が 4 枚連続、本文中の矢印、主題の埋もれた
  # 長いタイトル。WARN なので --strict で落ちる (1)。
  "1|python3 $A/validate_deck.py $f/bad-tells.yaml --strict"
  "has:bullets are 'label: text'|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:four consecutive slides each show 3 items|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:arrows or em-dashes|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:the claim is buried in a sentence|python3 $A/validate_deck.py $f/bad-tells.yaml"
  "has:fills ~|python3 $A/validate_deck.py $f/bad-tells.yaml"

  # ---- 欠陥注入: 型の個数・軸・図の規約が効いているか ----
  "1|python3 $A/validate_deck.py $f/bad-archetypes.yaml"
  "has:matrix takes exactly 4 quadrants|python3 $A/validate_deck.py $f/bad-archetypes.yaml"
  "has:split is a figure beside its reading|python3 $A/validate_deck.py $f/bad-archetypes.yaml"

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
