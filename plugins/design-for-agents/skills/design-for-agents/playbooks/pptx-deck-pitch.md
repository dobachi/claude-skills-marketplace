---
id: pptx-deck-pitch
axis: deck
media: pptx
when:
  - "成果物が PowerPoint である"
  - "聞き手が社外または初対面である"
  - "持ち時間が20分以下である"
  - "目的が関心の獲得であり、その場での決裁を求めない"
ambiguous_if: "その場で決裁を求めるなら pptx-deck-decision を使う。社内向けで時間の制約が無いなら pptx-deck-explain を使う"
uses_rules:
  - core-title-assertion
  - core-density-one-message
  - core-density-budget
  - core-type-one-scale
  - core-type-body-floor
  - core-color-four-slots
  - core-emphasis-ladder
  - core-layout-one-grid
  - core-ornament-none
  - core-source-line-on-data
  - core-a11y-contrast-body
  - core-a11y-alt-text
  - pptx-master-placeholder
  - core-type-sans-projection
  - core-type-two-families-max
  - core-type-leading
  - core-layout-one-alignment
  - core-color-one-background
  - core-image-earns-place
  - core-image-resolution
  - core-image-license-verified
  - pptx-master-theme-colors
  - pptx-master-no-stock-theme
  - pptx-file-embed-fonts
  - core-layout-archetype-fits-content
  - core-ornament-part-vocabulary
  - core-emphasis-dark-page
  - core-title-one-line
  - core-structure-skeleton-varies
  - pptx-ornament-three-tokens
done_when:
  - id: within-slide-budget
    applies_to: deck
    predicate: count
    statement: "本編のスライドが16枚以上ある場合に 1、そうでなければ 0 である"
    check: manual
    floor: "本文スライドが5枚以上ある"
  - id: next-step-stated
    applies_to: deck
    predicate: exists
    statement: "次の接点を述べたスライドが1枚存在する"
    check: manual
    floor: "本文スライドが5枚以上ある"
needs_human:
  - "話し手の声（語り口）が資料と合っているか"
  - "使った画像がこの相手に対して適切な印象を作るか"
---

# ピッチ・営業資料

## 状況

持ち時間が短く、聞き手はこちらを知らない。**この場で決まらなくてよい。**
決めるのは次に会うかどうかであり、資料の役目はそこまで運ぶことである。

## 手順

1. **相手の世界で起きている変化を1枚で述べる。** 自社紹介から始めない。
   聞き手が自分の話だと認識するまで、こちらの話は届かない
2. **その変化で何が困るかを述べる。** 困りごとは相手の言葉で書く
3. **解決した状態を見せる。** 製品の説明ではなく、相手がどうなるか
4. **そこへ至る道として製品を置く。** ここで初めて製品名を出す
5. **証拠を出す。** 実績、第三者の評価、数値。出典行を付ける
6. **次の接点を書く。** 何を、いつ、誰と。ここが無いと資料は終わらない

## 決め打ち値

- **本編の枚数**: 15枚以下。付録は別に持つ
- **1枚あたりの語数**: 少ない側に倒す。話し手が内容を担う
- **強調**: 大きな数値を使う。1スライドに1つ（`core-emphasis-ladder`）
- **機能の一覧**: 本編に置かない。付録に置く

## よくある失敗

- **会社紹介から始める。** 聞き手はまだこちらに関心が無い
- **機能を並べる。** 機能は、困りごとが共有されたあとでなければ意味を持たない
- **枚数が多い。** 15枚を超えると持ち時間に収まらず、後半が飛ばされる。
  飛ばされるのは、たいてい次の接点を書いた最後の1枚である
- **数値に出所が無い。** 初対面の相手には、出所の無い数値は無いのと同じ
