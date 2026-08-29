---
id: pptx-slop-title-band
media: pptx
statement: "タイトルの背景に敷いた、スライド幅いっぱいのカラーバンド"
why_it_appears: "スライドごとに描き直されるため、座標が1枚ごとにずれる。高速で送ると上下に揺れて見え、これが生成された資料の最も分かりやすい徴候になる"
instead: "白地に ink のタイトル。区切りが要るならヘアライン1本（tokens の grid.hairlineLength / hairlineWeight）"
violates: [core-ornament-none, core-color-four-slots, core-layout-one-grid]
---

# 全幅カラーバンド

同じ帯を全スライドに置いたつもりでも、座標が1枚ごとに再計算されると揃わない。
スライドマスターに置けば揃うが、**そもそも帯が担っている情報が無い**。
