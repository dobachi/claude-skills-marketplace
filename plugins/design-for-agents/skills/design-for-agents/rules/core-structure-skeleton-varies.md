---
id: core-structure-skeleton-varies
status: active
tier: HOUSE
media: [pptx]
topic: structure
statement: "同じ骨格のスライドを4枚以上続けない"
values:
  - "同一骨格の連続は3枚以下"
  - "骨格とはレイアウトと、置いた部品の構成である"
not_applicable_when: "本文スライドが5枚以下のとき。短い資料では反復が単調に見えるほど続かない"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: no-long-identical-run
    applies_to: deck
    predicate: count
    statement: "同じレイアウトかつ同じ部品構成のスライドが4枚以上連続する箇所が 0 である"
    check: manual
    floor: "本文スライドが6枚以上ある"
---

# 同じ骨格を続けない

## 反復は統一を作り、反復だけは単調を作る

スライド間で骨格が揃っていることは、デッキが設計されて見える条件である
（`core-layout-one-grid`）。**同時に、骨格が一度も変わらないデッキは、
内容の違いをレイアウトが均してしまう。**

散らかりと単調は反対に見えて、同じ失敗である。どちらも「内容の形に合わせて
置き方を決める」をしていない。

## 直し方は、装飾ではない

4枚続いたときに足すべきものは飾りではない。**その中に、箇条書きではない形を
していた内容が混ざっている。** 順序があるならステップ、等価な単位ならカード、
2軸なら象限に置き換える（`core-layout-archetype-fits-content`）。

置き換える先が無いなら、続いていること自体は正しい。同じ形の内容は同じ形で
見せるべきである。その場合は転換のページを挟む（`core-emphasis-dark-page`）。

## 確かめ方

スライド一覧の表示で目を細める。全ての縮小画像で、同じ位置に同じ濃さの塊が
見えるなら、そのデッキは論の起伏をレイアウトで消している。
