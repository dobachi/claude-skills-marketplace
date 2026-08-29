---
id: core-diagram-one-abstraction
status: active
tier: SHOULD
media: [pptx]
topic: diagram
statement: "1枚の図に置く要素の抽象度を揃える。異なる階層を1枚に混ぜない"
values:
  - "1枚の図に置くのは1つのズームレベルだけ"
  - "階層が2つ以上要るなら、図を分ける"
  - "同じ重要度の要素は同じ大きさで描く"
not_applicable_when: "なし"
source:
  kind: consensus
  key: c4model
  ref: "Brown, C4 model（1枚につき1つのズームレベル）"
done_when:
  - id: uniform-abstraction
    applies_to: element
    predicate: count
    statement: "異なる抽象度の要素を含む図が 0 個である"
    check: manual
    floor: "図を含むスライドがある場合に限り評価する。要素を消して満たしてはならない"
  - id: equal-weight-equal-size
    applies_to: element
    predicate: equal
    statement: "同じ階層にある要素の大きさが同一である"
    check: manual
    floor: "図を含むスライドがある場合に限り評価する"
---

# 抽象度を揃える

## なぜ

「データベース」と「顧客の行動」を同じ図に並べると、読み手は
その2つがどういう関係にあるのか推論できない。**混在した図は、
細かく直すのではなく、階層ごとに分ける。**

## 大きさは重みである

同じ重要度の要素を違う大きさで描くと、無い階層があるように読める。
大きさを変えてよいのは、実際に強調したいときだけである
（`core-emphasis-ladder`）。

## 出典の管理

図の元ファイル（Mermaid、PlantUML、draw.io）をデッキと一緒に版管理する。
スライドに載せるのは書き出した画像である。元が無い図は直せない。
