---
id: pptx-master-theme-colors
status: active
tier: HOUSE
media: [pptx]
topic: master
statement: "色はテーマ色から選ぶ。図形や文字に色を直接指定しない"
values:
  - "設定場所: デザイン → バリエーション → 色 → 色のカスタマイズ"
  - "直接指定を使ってよい場所: なし"
not_applicable_when: "グラフの系列色で、テーマ色では色覚多様性に対応できない場合（core-color-cvd-distinguishable）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: colors-from-theme
    applies_to: element
    predicate: member
    statement: "文字と図形の色が、テーマ色として定義された色の集合に属する"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドに文字要素がある"
---

# テーマ色を使う

## なぜ

直接指定した色は、テーマを変えても追随しない。ブランドが変わったとき、
**全スライドを手で塗り直すことになる**。80枚のデッキでは、これは実際には
行われず、色が混ざったまま配られる。

これは `pptx-master-placeholder` と同じ理屈である。マスターが支配していない
ものは、後から一括で直せない。

## 崩れる経路

スポイトで色を拾う操作は、直接指定になる。他のファイルから貼り付けた図形も
元の色を持ち込む。貼り付けたら、色をテーマ色に付け直す。
