---
id: core-chart-chartjunk-none
status: active
tier: SHOULD
media: [pptx]
topic: chart
statement: "データを表さない描画をグラフから消す"
values:
  - "消すもの: 3D・立体・傾き、分解円、影、グラデーション塗り、枠線、背景塗り"
  - "目盛線: 縦は使わない。横は値の読み取りに要るときだけ残し、色は #E5E7EB とする"
  - "目盛のラベル: 最小値・最大値・主張に関わる値だけを残す"
  - "使わないもの: PowerPoint と Excel の既定の配色、二軸、値に応じて絵を伸縮させる図"
not_applicable_when: "組織のテンプレートが配色を定めている場合はそちらに従う（pptx-constraint-template）"
source:
  kind: consensus
  key: tufte-1983
  ref: "Tufte（チャートジャンク、データインク比）"
done_when:
  - id: no-3d-charts
    applies_to: element
    predicate: absent
    statement: "3D 効果、影、グラデーション塗りのいずれかを持つグラフが存在しない"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "グラフを含むスライドがある場合に限り評価する。グラフを消して満たしてはならない"
  - id: no-dual-axis
    applies_to: element
    predicate: absent
    statement: "第2軸を持つグラフが存在しない"
    check: manual
    floor: "グラフを含むスライドがある場合に限り評価する"
---

# チャートジャンクを消す

## なぜ 3D を特に禁じるのか

好みの問題ではない。3D は奥行きによって手前の量を大きく見せる。
**読み取りを歪めるので、装飾ではなく誤りである。**

## 二軸を使わない理由

2つの系列に別々の目盛を与えると、交点や上下関係は目盛の取り方次第で作れる。
つまり**任意の関係を見せられる**。並べたいなら、グラフを2つに分けて縦に並べる。

## 順序

まず消す。足すのは最後である。目盛線・枠・背景・凡例を消してから、
まだ読み取れないものだけを足す。
