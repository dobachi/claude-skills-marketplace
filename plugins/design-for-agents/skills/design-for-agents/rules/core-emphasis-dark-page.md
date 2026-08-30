---
id: core-emphasis-dark-page
status: active
tier: HOUSE
media: [pptx]
topic: emphasis
statement: "論の転換に、地の暗いページを置く"
values:
  - "使ってよいのは章扉と、一文だけのページ"
  - "1つのデッキで3枚以下"
  - "暗い地は accent の明度 0.12"
  - "同じ役割のページは全て同じ扱いにする"
not_applicable_when: "デッキ全体が暗い地のとき。反転の向きが逆になるので、明るいページを転換に使う（core-color-one-background）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: turns-are-marked
    applies_to: deck
    predicate: exists
    statement: "章の変わり目に、地の色が本文スライドと異なるページが存在する"
    check: manual
    floor: "章が2つ以上ある"
  - id: dark-pages-limited
    applies_to: deck
    predicate: count
    statement: "地の暗いページが3枚以下である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが6枚以上ある"
  - id: same-role-same-ground
    applies_to: deck
    predicate: equal
    statement: "章扉の地の色が全ての章扉で一致する"
    check: manual
    floor: "章扉が2枚以上ある"
---

# 転換には、地の暗いページ

## 白いページだけのデッキは、全ページが同じ重さになる

1枚の中の強調（`core-emphasis-ladder`）は、そのスライドの中だけで働く。
デッキを通して見たとき、どこで論が変わったかを示すものが無いと、20枚が
同じ調子で流れる。聞き手には段落の切れ目が聞こえない。

暗いページはその段落記号である。**内容を足さずに、構造を見せる。**

## `core-color-one-background` との境界

あの規則が禁じているのは、**明暗が入り混じって二つのデッキに見える状態**である。
本ルールが許すのは、役割で決まった一貫した反転だけである。章扉を反転させるなら
全ての章扉を反転させる。気分で1枚だけ暗くするのは、あの規則の違反である。

## 全幅カラーバンドとは別物である

`core-ornament-none` が禁じるのはタイトル背景の全幅バンドで、理由は
**生成のたびに座標が変わり、スライド間でずれる**ことにある。暗いページは
ページ全体の地であって図形ではない。ずれる縁が無い。

## 使いすぎると効かない

3枚を超えると、それは転換の印ではなく2つ目のテンプレートである。
