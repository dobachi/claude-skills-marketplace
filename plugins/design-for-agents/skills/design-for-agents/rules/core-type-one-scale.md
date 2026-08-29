---
id: core-type-one-scale
status: active
tier: HOUSE
media: [pptx]
topic: type
statement: "文字サイズは型スケールに定めた集合からだけ選ぶ。スライドごとに新しいサイズを作らない"
values:
  - "型スケールの定義: tokens/pptx.tokens.json の fontSize"
not_applicable_when: "組織のテンプレートがある場合はそちらのスケールに従う（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: sizes-from-scale
    applies_to: element
    predicate: member
    statement: "全ての文字要素のサイズが、tokens/pptx.tokens.json の fontSize に定めた値の集合に属する"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドにタイトルと本文がある"
---

# 型スケールは1本

## なぜこれが HOUSE なのか

具体的な数値（40 / 34 / 30 / 18 …）に外部の根拠は無い。
**根拠があるのは「1本に固定する」という部分だけ**で、それは反復が
「設計された」印象を作るという整列・反復の原則（Williams, CRAP）による。

## 揺れが生まれる経路

サイズは、収まらないスライドで1つだけ小さくすることから崩れ始める。
1枚が 17pt になり、次が 16.5pt になり、デッキ全体でサイズが揃わなくなる。
**収まらないときはサイズではなく内容を動かす**（`core-type-body-floor`）。

## 実装

スケールはスライドマスターのレイアウトに持たせる（`pptx-master-placeholder`）。
個々のスライドでサイズを指定できる状態にしておくと、必ず指定される。
