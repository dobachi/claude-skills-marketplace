---
id: pptx-slop-pie-per-item
media: pptx
statement: "項目の数に合わせて作られた、区分が4つ以上の円グラフ"
why_it_appears: "箇条書きの項目数に合わせて機械的に円が生成される。データが割合ですらないこともある"
instead: "積み上げ棒1本、または値の順に並べた横棒。2要素なら大きな数値で書く"
violates: [core-chart-pie-limit, core-chart-follows-question]
---

# 項目数に合わせた円グラフ

円は角度と面積で量を符号化する。どちらも位置・長さより読み取り精度が低い
（Cleveland & McGill 1984）。**近い値を比べさせる用途に円は向かない。**
