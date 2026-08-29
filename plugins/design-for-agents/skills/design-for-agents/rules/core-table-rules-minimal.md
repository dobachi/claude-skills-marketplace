---
id: core-table-rules-minimal
status: active
tier: SHOULD
media: [pptx]
topic: table
statement: "表の縦罫を引かない。横罫は見出しの下と合計行の上だけに引く"
values:
  - "縦罫: 引かない"
  - "横罫: 見出し下に1本、合計行の上に1本"
  - "セルの塗り: 強調する1行にだけ、アクセント色の薄い塗りを置く"
not_applicable_when: "組織のテンプレートが表の書式を定めている場合はそちらに従う（pptx-constraint-template）"
source:
  kind: consensus
  key: tufte-1983
  ref: "Tufte（データインク比を表に適用したもの）"
done_when:
  - id: no-vertical-rules
    applies_to: element
    predicate: absent
    statement: "縦罫を持つ表が存在しない"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "表を含むスライドがある場合に限り評価する。表を消して満たしてはならない"
---

# 表の罫線

## なぜ

罫線はデータを表さない。列は余白で分かれるので、縦罫が担っている情報は無い。
格子状の表は、読み手の目を升目に閉じ込めて、行どうしの比較を妨げる。

## 何が残るか

| 要素 | 可否 |
|---|---|
| 見出しの下の横罫1本 | 残す |
| 合計行の上の横罫1本 | 残す |
| 行ごとの縞模様 | 使わない（行数が多いなら付録に移す） |
| 縦罫 | 引かない |
| 外枠 | 引かない |
