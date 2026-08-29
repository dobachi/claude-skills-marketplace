---
id: pptx-deck-decision
axis: deck
media: pptx
when:
  - "成果物が PowerPoint である"
  - "聞き手に決裁・承認・予算・採用可否のいずれかを求める"
ambiguous_if: "説明が目的か決裁が目的か判別できない場合。推測せず「この資料を見た相手に何をしてほしいか」をユーザに聞く"
uses_rules:
  - core-title-assertion
  - core-density-one-message
  - core-density-budget
  - core-source-line-on-data
  - core-color-four-slots
  - core-type-one-scale
  - core-type-body-floor
  - core-layout-one-grid
  - core-ornament-none
  - core-emphasis-ladder
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
  - pptx-master-theme-colors
  - pptx-master-no-stock-theme
  - pptx-file-embed-fonts
done_when:
  - id: ask-slide-exists
    applies_to: deck
    predicate: exists
    statement: "相手に求める行動を1文で書いたスライドが1枚存在する"
    check: manual
    floor: "本文スライドが3枚以上ある"
  - id: titles-form-argument
    applies_to: deck
    predicate: count
    statement: "タイトルだけを順に並べたとき、結論に到達しない箇所が 0 である"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドにタイトルがある"
needs_human:
  - "提示した選択肢が、意思決定者にとって本当に選択肢になっているか"
  - "反対意見への備えが足りているか"
---

# 意思決定資料

## 状況

聞き手は、この資料を見たあとで何かを決める。決めるためには、選択肢と、
選ばなかった場合に起きることが要る。**情報を網羅した資料は、決裁の役に立たない。**

## 手順

1. **求める行動を1文で書く。** 「〜を承認いただきたい」。ここが書けないなら、
   この資料はまだ意思決定資料ではない
2. **結論を先頭に置く。** 支配的な主張を1つ決め、その根拠を下に並べる
   （ピラミッド構造）。時系列で並べない
3. **タイトルだけで筋を作る。** 全スライドのタイトルを主張文で書き出し、
   上から読んで論が通るかを見る。内容を作るのはこのあと
   （`core-title-assertion`）
4. **各主張に証拠を1つ割り当てる。** 数値・グラフ・表のいずれか。
   証拠が無い主張は、格を下げるか落とす
5. **選ばなかった案を書く。** 検討した代替案と、採らなかった理由。
   これが無いと「他は考えたのか」で止まる
6. **決めた後に何が起きるかを書く。** 費用、期日、担当、後戻りの可否
7. **形を整える。** ここで初めてトークンとルールを当てる

## 決め打ち値

- **枚数**: 本編は上限を置かない。ただし決裁に要らないものは付録に移す
- **冒頭**: 1枚目に結論、2枚目に求める行動
- **出典行**: 数値を載せた全スライドに置く（`core-source-line-on-data`）
- **1スライドに複数のグラフ**: 同じ問いに答えるなら可。別の問いなら割る

## よくある失敗

- **経緯から始める。** 相手は経緯を知りたいのではなく、決めたい。
  経緯は付録に置く
- **選択肢が1つ。** 比較対象が無い提案は、承認ではなく追認を求めている
- **数値の出所が無い。** 決裁の場でもっとも多い差し戻しの理由である
- **「今後検討」で終える。** 決められないなら、何を決めれば前に進むのかを書く
