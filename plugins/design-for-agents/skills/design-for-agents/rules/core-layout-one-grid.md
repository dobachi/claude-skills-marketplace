---
id: core-layout-one-grid
status: active
tier: SHOULD
media: [pptx]
topic: layout
statement: "全ての要素の左端を、側マージンか列端のいずれかに揃える。目測で置かない"
values:
  - "グリッドの定義: tokens/pptx.tokens.json の grid"
not_applicable_when: "全面配置の画像。ただし画像の上に載る文字はグリッドに従う"
source:
  kind: consensus
  key: williams-crap
  ref: "Williams, CRAP（整列・反復）／Müller-Brockmann, Grid Systems"
done_when:
  - id: left-edges-aligned
    applies_to: element
    predicate: member
    statement: "全ての要素の左端の値が、側マージンおよび列端として定義された値の集合に属する"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドに2つ以上の要素がある"
---

# グリッドは1つ

## なぜ

整列は、意図的な設計であることを示す最も安価な手段である。
そして**ずれは、生成された資料であることを示す最も分かりやすい徴候**でもある。
人が置いた要素は揃わないことがあるが、揃っていない要素が規則的に散らばるのは
機械が座標を都度決めた場合に起きる。

列端は「側マージンから導出する」。段組の幅を目分量で決めると、
段組を持つスライドとそうでないスライドで左端が合わなくなる。

## 判定

スライドを高速で送って、タイトルと本文の左端が動かないかを見る。
動くなら、そのスライドはグリッドに乗っていない。

## 実装

グリッドはスライドマスターのレイアウトが持つ（`pptx-master-placeholder`）。
スライドごとに座標を書くと、必ずずれる。
