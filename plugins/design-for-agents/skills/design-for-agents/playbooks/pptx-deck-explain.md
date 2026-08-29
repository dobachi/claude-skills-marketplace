---
id: pptx-deck-explain
axis: deck
media: pptx
when:
  - "成果物が PowerPoint である"
  - "聞き手の理解が目的であり、決裁を求めない"
ambiguous_if: "資料の最後に相手へ求める行動がある場合。それは意思決定資料であり pptx-deck-decision を使う"
uses_rules:
  - core-title-assertion
  - core-density-one-message
  - core-density-budget
  - core-diagram-information-test
  - core-diagram-arrow-one-meaning
  - core-diagram-one-abstraction
  - core-source-line-on-data
  - core-color-four-slots
  - core-type-one-scale
  - core-type-body-floor
  - core-layout-one-grid
  - core-ornament-none
  - core-a11y-contrast-body
  - core-a11y-alt-text
  - core-a11y-reading-order
  - pptx-master-placeholder
  - core-type-sans-projection
  - core-type-two-families-max
  - core-type-leading
  - core-layout-one-alignment
  - core-color-one-background
  - core-image-earns-place
  - core-image-icon-one-family
  - pptx-master-theme-colors
  - pptx-master-no-stock-theme
  - pptx-file-embed-fonts
done_when:
  - id: prior-knowledge-stated
    applies_to: deck
    predicate: exists
    statement: "聞き手に前提として求める知識を書いたスライドが1枚存在する"
    check: manual
    floor: "本文スライドが3枚以上ある"
  - id: terms-defined-before-use
    applies_to: deck
    predicate: count
    statement: "定義より前に使われている専門用語が 0 個である"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドに本文がある"
needs_human:
  - "聞き手の前提知識の見積もりが合っているか"
  - "図が実際に理解を助けているか"
---

# 技術説明資料

## 状況

聞き手は、この資料を見たあとで何かを理解している必要がある。
理解は、**知らない語が出てきた時点で止まる**。順序が内容より効く。

## 手順

1. **聞き手が既に知っていることを1枚書く。** 前提を明示すると、
   どこから説明するかが決まる。書けないなら、聞き手を特定できていない
2. **専門用語を洗い出し、初出の位置を決める。** 定義より前に使わない
3. **全体像を先に出す。** 部分の説明から始めると、聞き手はそれがどこの話か
   分からないまま聞くことになる
4. **図を描くか決める。** 情報テストを通す（`core-diagram-information-test`）。
   構造を符号化しないなら箇条書きか表にする
5. **1枚1主張で割る。** 説明資料は密度が上がりやすい
   （`core-density-one-message`）
6. **確認の手段を置く。** 節の終わりに、そこまでで何が分かったかを1枚

## 決め打ち値

- **図の抽象度**: 1枚につき1つのズームレベル（`core-diagram-one-abstraction`）
- **矢印**: 意味を1つに固定し、凡例を図の中に置く
- **配布を前提とする場合**: 発表者ノートに口頭で補う内容を書く。
  スライドの文字を増やして補わない

## よくある失敗

- **知っている順に話す。** 説明する側が学んだ順序と、聞き手が理解できる順序は
  違う。全体 → 部分 の順に置く
- **語の定義を後回しにする。** 一度分からなくなった聞き手は戻ってこない
- **図が構造を符号化していない。** 箱と矢印を置くこと自体が説明になっている
  と錯覚しやすい（`pptx-diagram-smartart-none`）
- **1枚に全部載せる。** 説明資料でもスライドは無料である
