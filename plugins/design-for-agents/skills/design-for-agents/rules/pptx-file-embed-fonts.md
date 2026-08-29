---
id: pptx-file-embed-fonts
status: active
tier: HOUSE
media: [pptx]
topic: file
statement: "配布するファイルには書体を埋め込む"
values:
  - "設定: ファイル → オプション → 保存 → ファイルにフォントを埋め込む"
  - "埋め込む範囲: 使用されている文字のみ（編集を渡す場合は全文字）"
not_applicable_when: "PDF に書き出して配る場合。書体は PDF に含まれる"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: fonts-embedded
    applies_to: deck
    predicate: exists
    statement: "配布するファイルに書体の埋め込み設定が有効になっている"
    check: manual
    floor: "本文スライドが3枚以上ある"
---

# 書体を埋め込む

## なぜ

埋め込まないと、開いた環境に無い書体は別のものに置き換わる。字幅が変われば
行が溢れ、`core-density-budget` も `core-layout-one-grid` も同時に崩れる。
**送った側にはそれが見えない。**

日本語書体は特に置き換わりやすい。環境ごとに入っているものが違う。

## 送る前に

書体を持たない環境で開く可能性があるなら、PDF も併せて渡す。
体裁を保証したいだけなら PDF の方が確実である。
