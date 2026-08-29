---
id: core-layout-one-alignment
status: active
tier: SHOULD
media: [pptx]
topic: layout
statement: "1枚のスライドの中で文字の揃えを混ぜない。本文は左揃えにする"
values:
  - "本文・見出し: 左揃え"
  - "表の数値: 右揃え（core-table-align-numbers）"
  - "中央揃えを使う場所: 表紙と章扉のみ"
not_applicable_when: "組織のテンプレートが中央揃えを定めている場合（pptx-constraint-template）"
source:
  kind: consensus
  key: williams-crap
  ref: "Williams, CRAP（整列）"
done_when:
  - id: single-alignment-per-slide
    applies_to: slide
    predicate: count
    statement: "本文の揃えが左揃え以外のスライドが 0 枚である（表紙と章扉を除く）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドの本文が1行以上ある"
---

# 揃えを混ぜない

## なぜ左揃えか

左揃えは、行頭が1本の線として立つ。これが `core-layout-one-grid` の
グリッドと一致する。中央揃えは行ごとに行頭が動くので、**揃えるべき線が
存在しなくなる。**

中央揃えは儀礼的に読める。表紙と章扉ではそれが適切だが、本文では
読み手が毎行の開始位置を探すことになる。

## 混在が生む印象

1枚の中で左・中央・右が混ざると、要素が偶然そこに置かれたように見える。
これは装飾の問題ではなく、**設計されていないことの徴候**として読まれる。
