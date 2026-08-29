---
id: core-type-sans-projection
status: active
tier: SHOULD
media: [pptx]
topic: type
statement: "本文にはサンセリフ体を使う。セリフ体・装飾体・コンデンス体を本文に使わない"
values:
  - "本文: サンセリフ体"
  - "日本語: Noto Sans JP など、ウェイトが揃っているファミリー"
  - "セリフ体を使ってよい場所: 印刷して配る資料の本文、および引用"
not_applicable_when: "組織のテンプレートが書体を定めている場合（pptx-constraint-template）"
source:
  kind: consensus
  key: butterick
  ref: "Butterick, Practical Typography（投影・低解像度での可読性）"
done_when:
  - id: body-is-sans
    applies_to: element
    predicate: member
    statement: "本文プレースホルダの書体が、サンセリフとして宣言した書体の集合に属する"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドの本文が1行以上ある"
---

# 本文はサンセリフ

## なぜ

投影は解像度が低く、観客との距離がある。セリフの細い部分は、その条件で最初に
消える。**画面で見て問題が無いことは、投影して問題が無いことを意味しない。**

コンデンス体は字幅を詰めることで情報量を稼ぐが、それは
`core-type-body-floor` が禁じている操作を書体で行っているのと同じである。

## 配布するとき

書体をファイルに埋め込む（`pptx-file-embed-fonts`）。埋め込まないと、
開いた環境に無い書体は別のものに置き換わり、行が溢れて配置が崩れる。
