---
id: core-type-leading
status: active
tier: HOUSE
media: [pptx]
topic: type
statement: "行間を文字サイズの1.3倍、段落間隔を0.5行にする"
values:
  - "行間: 1.3倍"
  - "段落間隔: 0.5行"
  - "詰めて収めることをしない"
not_applicable_when: "組織のテンプレートが行間を定めている場合（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: leading-is-set
    applies_to: element
    predicate: member
    statement: "本文プレースホルダの行間が、定めた値の集合に属する"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドの本文が1行以上ある"
---

# 行間

## なぜこれが HOUSE なのか

1.3 という値に外部の根拠は無い。**決めておく理由は、行間が「収めるための調整弁」に
使われるのを止めるためである。**

文字サイズには下限があり（`core-type-body-floor`）、密度には上限がある
（`core-density-budget`）。行間を決めていないと、その2つを守ったまま
行間だけを詰めて収める、という逃げ道が残る。

## 崩れると何が起きるか

行間はスライドごとに違っても、1枚だけを見ているうちは気づかない。
高速で送ると、本文ブロックの高さが揃わないことで見える。
