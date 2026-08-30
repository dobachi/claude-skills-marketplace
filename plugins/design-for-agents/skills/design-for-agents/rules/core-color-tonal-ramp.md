---
id: core-color-tonal-ramp
status: active
tier: HOUSE
media: [pptx]
topic: color
statement: "面・罫・強調の地に使う色は、accent と同じ色相の明度違いから作る。無彩色のグレーを併用しない"
values:
  - "面: accent の明度 0.965"
  - "強調された部品の面: accent の明度 0.93"
  - "罫: accent の明度 0.90"
  - "同系で並べるグラフの系列: accent の明度 0.58 / 0.72 / 0.85"
  - "作り方は HSL で明度を指定する。白と混ぜない"
not_applicable_when: "グラフで1系列だけを強調するとき。他系列は灰にする（core-emphasis-ladder）。組織のテンプレートが面と罫の色を定めている場合も従わない（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: surfaces-share-the-hue
    applies_to: element
    predicate: member
    statement: "面と罫に使われた色が、accent と同じ色相の集合に属する"
    check: manual
    floor: "面または罫を持つ図形が1つ以上ある"
  - id: tonal-series-are-labelled
    applies_to: element
    predicate: exists
    statement: "同系の明度差だけで系列を分けたグラフに、各系列の名前がマークの近くに文字として存在する"
    check: manual
    floor: "同系で系列を分けたグラフが1つ以上ある"
---

# 同じ色相の、明度違いで作る

## `core-color-four-slots` との境界

4枠が数えているのは**文字の色数**である。本ルールが決めるのは**面と罫の地の色**で、
枠を増やしていない。accent 1色から作った明度違いなので、色は増えない。

## 白と混ぜない

白との混色は明度と同時に彩度も下げる。薄い段ほど灰色に寄り、面が濁る。
日本語の細い字画の背後では特に目立つ。HSL で明度だけを動かし、彩度は保つ。

## 無彩色のグレーを併用しない理由

青の accent の隣に純粋なグレーの面を置くと、それは**2色使っている**のと同じに
見える。同じ面を accent 側へ数パーセント寄せるだけで、デッキ全体が1つの色相に
まとまる。手間はゼロで、効果は「考えて作られている」という印象そのものである。

## 同系ランプが誤りになる場合

- **系列が同じ種類のものでないとき。** 主役と背景の関係なら、accent 1つと灰で
  区別するほうが正しい
- **白黒印刷や色覚特性で潰れるとき。** 同系は色相の手がかりが無く、明度だけが
  頼りになる。凡例だけで系列を示すグラフに使わない。マークの近くに名前を置く
  （`core-chart-direct-label`）
