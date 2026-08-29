---
id: core-chart-follows-question
status: active
tier: SHOULD
media: [pptx]
topic: chart
statement: "チャート種は「何を比較させたいか」から選ぶ。データの形から選ばない"
values:
  - "カテゴリ間の比較: 棒グラフ（ラベルが長ければ横棒）。値の順に並べる"
  - "時間変化: 折れ線"
  - "全体に対する割合 2要素: グラフにせず大きな数値で書く"
  - "全体に対する割合 3要素以上: 積み上げ棒1本"
  - "分布: ヒストグラム、箱ひげ図"
  - "相関: 散布図"
  - "順位: 値の順に並べた横棒"
not_applicable_when: "データ点が2つ以下のとき。グラフではなく文か大きな数値で書く"
source:
  kind: consensus
  key: ft-visual-vocabulary
  ref: "FT Visual Vocabulary／Cleveland & McGill 1984（符号化の精度順）"
done_when:
  - id: chart-earns-place
    applies_to: element
    predicate: count
    statement: "データ点が3つ未満のグラフが 0 個である"
    check: manual
    floor: "グラフまたは大きな数値を含むスライドが1枚以上ある"
---

# チャート種は問いから選ぶ

## なぜ

Cleveland & McGill 1984 は、量の読み取り精度に順位があることを示した。
共通軸上の位置がもっとも正確で、長さ、角度、面積の順に落ちる。
**棒グラフが円グラフより読みやすいのは好みではなく、符号化の性質である。**

## グラフにしない場合

- **1つの数値が主張であるとき** — 大きな文字で書く。1本の棒グラフより強い
- **値が2つのとき** — 文で足りる（「継続率は78%から84%に上がった」）

グラフが正当化されるのは、3点以上のデータにまたがる傾向や比較を
**見せる必要がある**ときである。
