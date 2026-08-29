---
id: core-chart-direct-label
status: active
tier: SHOULD
media: [pptx]
topic: chart
statement: "系列名はグラフ上に直接置く。凡例で対応させない"
values:
  - "折れ線: 線の右端に系列名を置く"
  - "棒: 棒の上または中に値と名前を置く"
  - "散布図: 注目させる点の近くに置く"
not_applicable_when: "系列が5つ以上あり、直接置くと重なる場合。その場合は系列を減らすか、グラフを分ける"
source:
  kind: consensus
  key: tufte-1983
  ref: "Tufte（データインク比）／Cleveland & McGill 1984（対応付けの負荷）"
done_when:
  - id: no-legend-lookup
    applies_to: element
    predicate: count
    statement: "系列名を凡例だけで示しているグラフが 0 個である"
    check: manual
    floor: "グラフを含むスライドがある場合に限り評価する。系列を削って満たしてはならない"
---

# 直接ラベル

## なぜ

凡例は、聞き手に「色を覚えて、グラフに戻って、対応させる」作業をさせる。
系列名を線の隣に置けばその作業は消える。**凡例を消せることは副産物であり、
目的は対応付けの手間を無くすことである。**

色覚多様性への対処にもなる（`core-color-cvd-distinguishable`）。
色に頼らず系列が分かるなら、色の識別性は問題にならない。

## 1系列だけを強調するとき

強調する系列だけをアクセント色にし、**残りを灰にする**。
凡例を足すのではなく、色を引く。
