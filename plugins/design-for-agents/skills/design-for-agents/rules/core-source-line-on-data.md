---
id: core-source-line-on-data
status: active
tier: HOUSE
media: [pptx]
topic: source
statement: "数値・グラフ・表・引用を載せたスライドに、出典行を置く"
values:
  - "位置: フッタ線の下"
  - "大きさ: 11pt"
  - "色: muted"
  - "書く内容: 出所と時点（例: 社内データ、2026年第3四半期）"
not_applicable_when: "そのスライドの数値が、同じデッキ内の別スライドで出典を示した数値と同一である場合。ただし付録では再掲する"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: data-slides-cite
    applies_to: slide
    predicate: exists
    statement: "数値、グラフ、表、引用のいずれかを含む各スライドに、出典行が1つ存在する"
    check: manual
    floor: "グラフ、表、または数値を含むスライドが1枚以上ある。数値を消して満たしてはならない"
---

# 出典行

## なぜこれが HOUSE なのか

外部の規範ではない。**削られやすいものを、削られない位置に固定するための決めである。**

出典は、余白を作る作業のときに最初に消える。位置と大きさと色をあらかじめ
決めておけば、消す判断が発生しない。

## クリーンにするときに消してよいものではない

装飾を消すことと、根拠を消すことは違う。
**出典・単位・但し書きは残す**（`core-ornament-none`）。

## 時点を書く

出所だけでは足りない。同じ社内データでも、いつ時点かで数値は変わる。
デッキが再利用されたときに誤りになるのは、この一行が無いときである。
