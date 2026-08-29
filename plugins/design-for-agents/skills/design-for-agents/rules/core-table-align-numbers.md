---
id: core-table-align-numbers
status: active
tier: SHOULD
media: [pptx]
topic: table
statement: "数値は右揃えにし、小数点の桁数を列ごとに揃える。文字は左揃えにする"
values:
  - "数値の列: 右揃え"
  - "文字の列: 左揃え"
  - "小数点以下の桁数: 列内で同一"
  - "見出しの揃え: その列の内容に合わせる"
not_applicable_when: "なし"
source:
  kind: consensus
  key: butterick
  ref: "Butterick, Practical Typography（数字の組み方）"
done_when:
  - id: numbers-right-aligned
    applies_to: element
    predicate: count
    statement: "数値の列で右揃えになっていないものが 0 個である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "数値の列を持つ表がある場合に限り評価する。列を消して満たしてはならない"
  - id: decimals-consistent
    applies_to: element
    predicate: equal
    statement: "各数値列について、小数点以下の桁数が列内で同一である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "数値の列を持つ表がある場合に限り評価する"
---

# 数値の揃え

## なぜ

右揃えにすると桁が縦に並び、桁数の違いが位置の違いとして見える。
これは Cleveland & McGill の言う「共通軸上の位置」であり、
**表の中でもっとも精度の高い比較になる。**

桁数が列内で揃っていないと、この位置の情報が崩れる。
1.5 と 1.50 を混ぜない。

## よくある崩れ

- 単位を各セルに書いて桁がずれる → 単位は見出しに1度だけ書く
- 中央揃えにする → 桁が揃わないので、比較ができなくなる
