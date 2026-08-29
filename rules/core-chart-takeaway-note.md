---
id: core-chart-takeaway-note
status: active
tier: SHOULD
media: [pptx]
topic: chart
statement: "グラフには、そこから何が言えるかを述べた注記を添える"
values:
  - "キャプション: その図が何であるかを述べる（15pt）"
  - "注記: その図から何が言えるかを述べる（14pt）"
  - "注記は文にする。名詞句で終えない"
not_applicable_when: "付録に置いた参照用のグラフ。ただし付録であることを明示する"
source:
  kind: consensus
  key: alley-neeley-2005
  ref: "Alley & Neeley 2005（主張と証拠を対にする）"
done_when:
  - id: chart-has-note
    applies_to: element
    predicate: exists
    statement: "各グラフに、述語を含む注記が1つ存在する"
    check: manual
    floor: "グラフを含むスライドがある場合に限り評価する。グラフを消して満たしてはならない"
---

# 読み取りを聞き手に任せない

## なぜ

グラフは証拠であって主張ではない。同じグラフから複数の読み取りができるとき、
聞き手が選ぶのは発表者が意図したものとは限らない。**主張は書く。**

これは `core-title-assertion` をスライドの中の図に適用したものである。
タイトルがデッキ全体の主張を担い、注記が図の主張を担う。

## キャプションと注記は別物

| 行 | 述べること | 例 |
|---|---|---|
| キャプション | それが何か | 図3 四半期別の継続率 |
| 注記 | 何が言えるか | 第3四半期の落ち込みは新規顧客に限られ、既存顧客は横ばいだった |

キャプションだけを置いて注記を省くのが、もっとも多い欠落である。
