---
id: core-ornament-part-vocabulary
status: active
tier: HOUSE
media: [pptx]
topic: ornament
statement: "描く部品は、ヘアライン・面・カード・ステップの箱・矢印・象限・連番・チップの8種だけにする"
values:
  - "ヘアライン: 領域の分割"
  - "面: まとまり、または対象の指定"
  - "カード: 等価な単位"
  - "ステップの箱: 順序の一段"
  - "矢印: 順序または依存。ステップの中だけ"
  - "象限: 2軸上の位置"
  - "連番: 順序の中での位置。ステップの中だけ"
  - "チップ: 定められた集合に属する状態"
not_applicable_when: "組織のテンプレートが独自の部品を含む場合。テンプレートを書き換えず、そのまま使う（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: parts-from-vocabulary
    applies_to: element
    predicate: member
    statement: "本文領域に置いた図形が、8種の部品のいずれかに属する"
    check: manual
    floor: "図形を1つ以上置いたスライドが1枚以上ある"
---

# 部品の語彙は閉じている

## `core-ornament-none` との境界

`core-ornament-none` は「装飾的な角丸枠」を置かないと定めている。本ルールが
挙げる8種は**意味を担うので装飾ではない**。カードは「これらは等価である」を、
象限は「2軸上のここにある」を運ぶ。取り除けば意味が減る。

その判定は `core-diagram-information-test` と同じである。**取り除いても
意味が変わらない部品は、この一覧に載っていても装飾である。**

## なぜ語彙を閉じるのか

部品を足す判断が発生しなくなる。六角形、雲、リボン、意味のないコネクタが
入り込む余地は、「その形に何を担わせるか」を毎回決めているから生まれる。
決めておけば、迷いは「どの部品か」だけになり、無い形は最初から候補にならない。

一覧に無い形が要るときは、内容の構造がこの語彙で表せていない。図として描き
（`core-diagram-information-test`）、画像として置くか、文章で書く。

## 強調は部品を増やさない

強調したいものがあっても部品を足さない。`core-emphasis-ladder` の順で、
位置・孤立・サイズ・太さ・アクセント色を使う。強調された部品は1スライドに1つである。
