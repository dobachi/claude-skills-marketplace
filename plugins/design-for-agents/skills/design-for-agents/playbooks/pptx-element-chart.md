---
id: pptx-element-chart
axis: element
media: pptx
when:
  - "定量データをグラフで示すスライドを作る"
ambiguous_if: "示したい値が2つ以下の場合。グラフではなく大きな数値か文で書く（core-chart-follows-question）"
uses_rules:
  - core-chart-follows-question
  - core-chart-pie-limit
  - core-chart-direct-label
  - core-chart-chartjunk-none
  - core-chart-takeaway-note
  - core-color-cvd-distinguishable
  - core-color-semantic-data-only
  - core-source-line-on-data
  - core-density-budget
  - core-a11y-alt-text
  - core-color-tonal-ramp
done_when: []
needs_human:
  - "グラフの数値が本文の主張と一致しているか（数値の突き合わせ）"
  - "軸の取り方が誤解を招かないか"
---

# グラフのスライド

## 状況

グラフは証拠であって主張ではない。**そのグラフから何が言えるかは、
発表者が書かなければ伝わらない。**

## 手順

1. **何を比較させたいかを1文で書く。** ここからチャート種が決まる
   （`core-chart-follows-question`）。データの形から選ばない
2. **グラフにするか決める。** データ点が2つ以下なら、大きな数値か文にする
3. **系列を絞る。** 4系列まで。超えるならグラフを分ける
4. **消す。** 目盛線、枠、背景、凡例、3D、影（`core-chart-chartjunk-none`）
5. **直接ラベルを置く。** 系列名を線や棒の隣に置く
6. **強調を1つ決める。** 主張に関わる系列だけをアクセント色にし、残りを灰にする
7. **注記を書く。** そこから何が言えるかを文で（`core-chart-takeaway-note`）
8. **出典行を置く。** 出所と時点

## 決め打ち値

- **系列の上限**: 4（円グラフの区分は3）
- **色**: 3系列以上を色で分けるときだけ Okabe-Ito から取る
- **目盛線**: 縦は使わない。横は読み取りに要るときだけ `#E5E7EB`
- **キャプション 15pt / 注記 14pt / 出典行 11pt**
- **第2軸**: 使わない

## よくある失敗

- **タイトルが話題になっている。** 「四半期別売上」ではなく、そのグラフから
  言えることを書く（`core-title-assertion`）
- **凡例で色を対応させる。** 直接ラベルにすれば凡例は要らなくなる
- **項目数に合わせて円グラフを作る。** 4つ以上あるなら横棒にする
- **数値が本文と食い違う。** グラフを作ったあと、本文の主張と突き合わせる。
  これは人が確認する（needs_human）
