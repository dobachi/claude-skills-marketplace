---
id: core-color-cvd-distinguishable
status: active
tier: SHOULD
media: [pptx]
topic: color
statement: "色だけで区別させる箇所では、P型・D型・T型の色覚で識別できる色の組を使う"
values:
  - "3系列以上を色で区別するとき: Okabe-Ito の8色から選ぶ（#E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 #000000）"
not_applicable_when: "色以外の手段（直接ラベル、位置、線種）で区別が付いている場合"
source:
  kind: consensus
  key: okabe-ito
  ref: "Okabe & Ito, Color Universal Design"
done_when:
  - id: no-color-only-encoding
    applies_to: element
    predicate: absent
    statement: "凡例の色だけで系列を区別しているグラフが存在しない（直接ラベル、位置、線種のいずれかを併用している）"
    check: manual
    floor: "グラフを含むスライドが1枚以上ある場合に限り評価する。グラフの系列数を減らして満たしてはならない"
---

# 色覚多様性で識別できること

## なぜ

赤と緑の組み合わせは、日本人男性のおよそ5%が区別しづらい。
**色を情報の唯一の担い手にしない**、が原則である。

## 順序

1. **色に情報を持たせない。** 系列名をグラフ上に直接置く（直接ラベル）ので
   足りるなら、それが最善である。凡例そのものを消せる
2. 系列を色で分けるしかないとき、Okabe-Ito の8色から取る
3. 赤／緑を「減／増」の意味で使うときは、記号（▲▼）か位置を併用する

## 注意

Okabe-Ito は**グラフと表の中で使う**（`core-color-semantic-data-only`）。
本文やヘアラインの色を8色に増やす根拠ではない。本文の色は4枠のままである。
