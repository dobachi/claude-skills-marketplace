---
id: core-chart-pie-limit
status: active
tier: SHOULD
media: [pptx]
topic: chart
statement: "円グラフは区分が3つ以下で、かつ区分どうしを比較させないときにだけ使う"
values:
  - "円グラフの区分の上限: 3"
  - "4区分以上: 積み上げ棒1本、または横棒"
  - "分解円グラフ（切り離した円）は使わない"
not_applicable_when: "なし"
source:
  kind: consensus
  key: cleveland-mcgill-1984
  ref: "Cleveland & McGill 1984（角度・面積は位置・長さより読み取り精度が低い）"
done_when:
  - id: pie-slices-within-limit
    applies_to: element
    predicate: count
    statement: "区分が4つ以上の円グラフが 0 個である"
    check: manual
    floor: "グラフを含むスライドがある場合に限り評価する。区分を統合して満たしてはならない"
---

# 円グラフは3区分まで

## なぜ

円グラフは角度と面積で量を符号化する。Cleveland & McGill 1984 の順位では、
どちらも位置・長さより精度が低い。**近い値どうしを比べさせる用途に円は向かない。**

## 上流の矛盾について

本ルールの元にした pptx-design（2026-08-29 に本プラグインへ統合し廃止）は、
`clean-design-system.md` で「円は6区分まで」、
`data-visualization.md` で「円は3区分まで、それを超えるものはチャートジャンク」と
書いており、値が食い違っていた。**符号化の性質に根拠がある厳しい側（3）を採った。**

## 代わりに使うもの

| 見せたいこと | 代わり |
|---|---|
| 全体に対する割合（2要素） | 大きな数値（「84%が継続」） |
| 全体に対する割合（3要素以上） | 積み上げ棒1本 |
| 区分どうしの比較 | 横棒（値の順に並べる） |
