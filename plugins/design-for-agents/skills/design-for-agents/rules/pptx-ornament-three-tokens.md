---
id: pptx-ornament-three-tokens
status: active
tier: HOUSE
media: [pptx]
topic: ornament
statement: "部品の造形は、余白の基準単位・角丸半径・線幅の3つの値だけで決める"
values:
  - "余白の基準単位 0.083in"
  - "角丸半径 0.06in"
  - "線幅 0.75pt"
  - "部品どうしの間隔は基準単位の2倍"
  - "部品の内側の余白は基準単位の2倍"
not_applicable_when: "組織のテンプレートが図形の書式を定めている場合。テンプレートの値をそのまま使う（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: one-corner-radius
    applies_to: element
    predicate: equal
    statement: "角丸を持つ図形の角丸半径が全て同じ値である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "角丸を持つ図形が2つ以上ある"
  - id: one-line-weight
    applies_to: element
    predicate: equal
    statement: "線を持つ図形の線幅が全て同じ値である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "線を持つ図形が2つ以上ある"
  - id: gaps-on-the-scale
    applies_to: element
    predicate: member
    statement: "部品どうしの間隔が、基準単位の整数倍の集合に属する"
    check: manual
    floor: "並列に置いた部品が2つ以上ある"
---

# 造形は3つの値で決まる

## 「なぜか素人っぽい」の正体

角丸が2種類あり、隙間が3種類あり、影が1つだけ付いている。個々は誰も指摘しないが、
全体は雑に見える。逆に、部品が全てこの3つの値で一致していれば、ただの長方形でも
設計されて見える。

**整って見えることは、部品を足した結果ではなく、値が1つに揃った結果である。**

## 3つで足りる理由

部品の語彙が閉じている（`core-ornament-part-vocabulary`）ので、必要な造形の
自由度は「どれくらい丸いか」「どれくらい太いか」「どれくらい離すか」しかない。
角丸を 0 にすれば角のある意匠になり、それも1つの値である。

## 間隔を基準単位の倍数にする

0.083in は 96dpi の 8px にあたる。全ての隙間と内側の余白をこの整数倍にすると、
要素の左端と上端が自然に揃い、グリッド（`core-layout-one-grid`）と食い違わない。
値そのものに根拠は無いが、**倍数で揃っていることには効果がある。**

## 影・グラデーション・ベベルは値を持たない

3つの値に無いものは使わない（`core-ornament-none`）。
