---
id: pptx-slop-rainbow-series
media: pptx
statement: "PowerPoint と Excel の既定配色をそのまま使った、8系列以上の折れ線グラフ"
why_it_appears: "データをそのまま貼ると既定のテーマが当たる。系列を減らす判断が発生しない"
instead: "系列を4つまでに絞る。3系列以上を色で分けるなら Okabe-Ito から取る。直接ラベルを置き、強調する1系列以外を灰にする"
violates: [core-chart-chartjunk-none, core-chart-direct-label, core-color-cvd-distinguishable, core-density-budget]
---

# 虹色の多系列グラフ

読めない。色の識別に頼っているため、色覚多様性でも崩れる。
系列が多いのはグラフの問題ではなく、**1枚に載せる量の問題**である。
