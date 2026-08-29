---
id: pptx-diagram-smartart-none
status: active
tier: HOUSE
media: [pptx]
topic: diagram
statement: "SmartArt を既定で使わない。図形を自分で置く"
values:
  - "使ってよい例外: 順序が内容に内在する工程で段が6以下のもの、深さ2以上の厳密な階層、包含を表す同心円"
  - "上の例外に当たる場合でも、情報テストを先に通す"
not_applicable_when: "組織のテンプレートが SmartArt を含む場合。テンプレートを書き換えない（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: no-smartart
    applies_to: element
    predicate: absent
    statement: "SmartArt 図形が存在しない（例外に当たると本文に明記したものを除く）"
    check: manual
    floor: "本文スライドが3枚以上ある"
---

# SmartArt を既定にしない

## なぜ

SmartArt は、箇条書きを「工程」や「枠組み」に見せかけるのがあまりに容易である。
**手で箱と矢印を置く作業そのものが、情報テストを強制する。**
既製の型に流し込むと、その判断が飛ばされる。

## 典型的な誤用

- 空白を埋めるために置く
- 順序が無い5つの考えを「5段階の工程」の型に入れる
- 中心と関係の無いものを「中心と放射」の型に入れる
- 繰り返さないものを「循環」の型に入れる
- 階層でないものを「ピラミッド」の型に入れる

いずれも、**型が主張していない構造を主張してしまっている**。
図が嘘をつくのは、装飾より重い欠陥である。
