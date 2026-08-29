---
id: core-color-semantic-data-only
status: active
tier: HOUSE
media: [pptx]
topic: color
statement: "意味を担う色（赤＝減、緑＝増など）は、グラフと表の内部にだけ置く。本文と装飾には置かない"
values: []
not_applicable_when: "なし"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: semantic-color-confined
    applies_to: element
    predicate: absent
    statement: "グラフと表の外側に、4枠以外の色を持つ文字要素が存在しない"
    check: manual
    floor: "本文スライドが3枚以上ある"
---

# 意味色はデータの中だけ

## なぜ

本文に赤を置くと、それが「悪い知らせ」なのか「強調」なのか判別できなくなる。
色の意味は1つに固定したときだけ機能する。**データの中では意味色、外では4枠**、
という境界を引けば、判別は常に付く。

## 例

| 場面 | 可否 |
|---|---|
| 棒グラフで、減少した棒だけ赤 | 可 |
| 表のセルで、未達の行だけ赤字 | 可 |
| 本文の箇条書きで「重要」だけ赤 | 不可。`core-emphasis-ladder` に従う |
| タイトルの一部を赤 | 不可 |

## 併用

色だけに意味を持たせない（`core-color-cvd-distinguishable`）。
赤で減を示すなら、記号か符号を併記する。
