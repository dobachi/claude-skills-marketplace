---
id: core-density-one-message
status: active
tier: SHOULD
media: [pptx]
topic: density
statement: "1枚のスライドが述べる主張は1つにする。2つあるなら2枚に割る"
values: []
not_applicable_when: "なし"
source:
  kind: consensus
  key: mayer-multimedia
  ref: "Mayer, Multimedia Learning（一貫性原理）／Sweller, 認知負荷理論"
done_when:
  - id: one-claim-per-slide
    applies_to: slide
    predicate: count
    statement: "タイトルが逆接（しかし、一方で）または並列（および、かつ）で2つの主張を接続しているスライドが 0 枚である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドにタイトルがある"
---

# 1スライド1メッセージ

## なぜ

1枚に2つの主張を載せると、聞き手はどちらを聞けばよいか判断できない。
Mayer の一貫性原理は、学習に無関係な要素を足すと理解が下がることを示している。
第2の主張は、第1の主張にとっては無関係な要素である。

**スライドの枚数は無料である。** 割ることの代償はほぼ無く、混ぜることの代償は
理解の低下である。

## 判定

タイトルを主張文で書けば（`core-title-assertion`）、2つの主張を持つスライドは
タイトルが「〜だが、〜」「〜と〜」の形になるので、そこで検出できる。
**タイトルが書けないスライドは、主張が決まっていない。**

## やってはいけない対処

- 文字を小さくして2つとも載せる（`core-type-body-floor` 違反）
- 片方を第2階層に押し込む（主張は階層で消えない）
