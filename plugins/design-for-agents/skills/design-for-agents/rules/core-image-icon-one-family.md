---
id: core-image-icon-one-family
status: active
tier: HOUSE
media: [pptx]
topic: image
statement: "アイコンは1つのファミリーに統一し、大きさと線の太さを揃え、単色で塗る"
values:
  - "ファミリー: 1つ"
  - "塗り: accent か ink の単色"
  - "大きさ: 同じ役割のアイコンは同じ大きさ"
  - "使わないもの: クリップアート、絵文字調の多色アイコン"
not_applicable_when: "組織のテンプレートがアイコンを含む場合（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: icons-one-family
    applies_to: deck
    predicate: count
    statement: "アイコンのファミリーが2つ以上ある場合に 1、そうでなければ 0 である"
    check: manual
    floor: "アイコンを含むスライドがある場合に限り評価する。アイコンを消して満たしてはならない"
  - id: icons-single-color
    applies_to: element
    predicate: member
    statement: "全アイコンの塗り色が、accent と ink の集合に属する"
    check: manual
    floor: "アイコンを含むスライドがある場合に限り評価する"
---

# アイコンは1系統

## なぜ

輪郭線のものと塗りつぶしのものを混ぜる、線の太さが違うものを混ぜる、
というのは**別々の場所から拾ってきたことがそのまま見える**。

多色のアイコンは、色4枠（`core-color-four-slots`）を無効にする。
アイコン1つで色が3つ増えることがある。

## そもそも要るか

アイコンも `core-image-earns-place` の対象である。
項目の横に飾りとして並べたアイコンは、消しても何も失われない。
