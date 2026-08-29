---
id: core-type-two-families-max
status: active
tier: SHOULD
media: [pptx]
topic: type
statement: "1つのデッキで使う書体ファミリーを2つまでにする"
values:
  - "上限: 2ファミリー"
  - "望ましい形: 1ファミリーのウェイト差だけで階層を作る"
not_applicable_when: "組織のテンプレートが書体を定めている場合（pptx-constraint-template）"
source:
  kind: consensus
  key: butterick
  ref: "Butterick, Practical Typography（書体の組み合わせ）"
done_when:
  - id: at-most-two-families
    applies_to: deck
    predicate: count
    statement: "デッキ内で使われている書体ファミリーが3つ以上ある場合に 1、そうでなければ 0 である"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドに文字要素がある"
---

# 書体は2つまで

## なぜ

階層は書体の種類ではなく、**大きさ・太さ・色**で作る（`core-emphasis-ladder`）。
書体を増やして階層を作ろうとすると、階層の数だけ書体が要ることになり、
デッキ全体の統一が失われる。

1ファミリーで Light / Regular / Medium / Bold を使い分ける方が、
2ファミリーを組み合わせるより整う。**迷ったら1つにする。**

## 崩れる経路

貼り付けである。他のファイルからコピーした表や図は、元の書体を持ち込む。
プレースホルダに書けば書体はスライドマスターが決めるが、
テキストボックスと貼り付けた図はそこから外れる（`pptx-master-placeholder`）。
