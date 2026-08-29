---
id: core-color-one-background
status: active
tier: HOUSE
media: [pptx]
topic: color
statement: "1つのデッキで背景の明暗を混ぜない。明るい地か暗い地のどちらかに統一する"
values:
  - "明るい地: paper #FFFFFF / ink #1A1A1A"
  - "暗い地: paper #111315 / ink #F2F2F2"
  - "純黒 #000000 と純白 #FFFFFF の組み合わせは使わない"
not_applicable_when: "全面配置の画像スライド。ただし画像の上に載る文字のコントラストは core-a11y-contrast-body に従う"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: one-background-mode
    applies_to: deck
    predicate: equal
    statement: "全スライドの背景色が同一である（全面配置の画像スライドを除く）"
    check: manual
    floor: "本文スライドが3枚以上ある"
---

# 背景は1つ

## なぜ

途中で背景が入れ替わるデッキは、2つのデッキを繋いだように読める。
明暗の切り替えは、章の区切りよりも強い断絶として働いてしまう。

## どちらを選ぶか

| 状況 | 選ぶ |
|---|---|
| 明るい部屋、印刷して配る | 明るい地 |
| 暗い会場、画面で読む | 暗い地 |

**選んだら最後まで変えない。** 途中で変えたくなったのは、たいてい
特定のスライドの見た目が気に入らないからであり、それは別の問題である。

## 純黒と純白を避ける理由

`#000000` を `#FFFFFF` に置くと、輪郭がにじんで見える（ハレーション）。
ink を `#1A1A1A` にするだけでこれは消える。コントラスト比は 17.4:1 あり、
規範上の余裕は十分にある。
