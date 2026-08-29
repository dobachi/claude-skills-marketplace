---
id: pptx-master-no-stock-theme
status: active
tier: HOUSE
media: [pptx]
topic: master
statement: "PowerPoint に同梱されているテーマをそのまま使わない"
values:
  - "使わないもの: Ion、Facet、Wisp などの同梱テーマを未変更のまま適用すること"
  - "作るもの: 本リポジトリのトークンを写したテーマ（色4枠・型スケール・グリッド）"
not_applicable_when: "組織のテンプレートがある場合。そちらをそのまま使う（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: theme-is-not-stock
    applies_to: deck
    predicate: absent
    statement: "同梱テーマの名前がテーマ名として設定されているデッキが存在しない"
    check: manual
    floor: "本文スライドが3枚以上ある"
---

# 同梱テーマを使わない

## なぜ

同梱テーマは見た目で分かる。**「決めなかった」ことが、そのまま外から見える。**
これは紫のグラデーションと同じ問題で、指示しなかった判断が既定値で埋まった
結果である。

同梱テーマは装飾（帯、斜めの図形、影）を含むものが多く、
`core-ornament-none` と正面から衝突する。

## 代わりにすること

スライドマスターで、本リポジトリのトークンを写す。
色4枠、型スケール、グリッド、フッタ位置。30分で終わり、
以後はスライドごとの判断が発生しなくなる。
