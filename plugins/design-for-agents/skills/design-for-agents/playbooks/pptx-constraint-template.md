---
id: pptx-constraint-template
axis: constraint
media: pptx
when:
  - "組織が配布した .pptx または .potx のテンプレートを使うことが決まっている"
ambiguous_if: "テンプレートが「参考」であり従う義務が無い場合。ユーザに従うかどうかを聞く"
uses_rules:
  - pptx-master-placeholder
  - core-title-assertion
  - core-density-one-message
  - core-density-budget
  - core-type-body-floor
  - core-source-line-on-data
  - core-a11y-contrast-body
  - core-a11y-alt-text
  - core-a11y-reading-order
done_when:
  - id: layouts-from-template
    applies_to: slide
    predicate: member
    statement: "全スライドのレイアウトが、テンプレートが定義したレイアウトの集合に属する"
    check: manual
    floor: "本文スライドが3枚以上ある"
  - id: template-unmodified
    applies_to: deck
    predicate: equal
    statement: "スライドマスターとレイアウトの定義が、元のテンプレートと一致する"
    check: manual
    floor: "本文スライドが3枚以上ある"
needs_human:
  - "テンプレートの体裁が守れないほど内容が収まらない場合に、どちらを崩すか"
---

# コーポレートテンプレート準拠

## 状況

組織のテンプレートがある。**このとき本リポジトリの HOUSE ルールは全て上書きされる。**
色4枠も型スケールもグリッドも、テンプレートが持っているものが優先する。
上書きされることは失敗ではない（INDEX 第7節）。

## 手順

1. **テンプレートを開き、レイアウトの一覧を取る。** どのレイアウトが
   何のためにあるかを確認する
2. **内容をレイアウトに割り当てる。** 白紙レイアウトを使わない
3. **テンプレートを書き換えない。** 色も書体も余白も、テンプレートのまま使う
4. **本リポジトリの HOUSE ルールを外す。** 色4枠、型スケール、グリッド、
   ヘアラインは適用しない。テンプレートの上に重ねると、どちらでもない
   見た目になる
5. **MUST は残る。** コントラスト比、代替テキスト、読み上げ順序は
   テンプレートに関わらず守る。テンプレートが満たしていないなら、
   その事実を報告する
6. **SHOULD は残る。** 主張タイトル、1枚1主張、密度予算、グラフと表の作法は
   テンプレートと衝突しない

## 決め打ち値

- **使うレイアウト**: テンプレートが定義したものだけ
- **追加する図形**: プレースホルダに収まらないものは足さない
- **色**: テンプレートのテーマ色。Okabe-Ito もここでは使わない。
  ただし系列が3つ以上あり、テーマ色で識別できない場合は報告する
- **生成**: `pptx-build --template <file>` に渡す。テンプレートの
  スライドマスターをそのまま継承する

## よくある失敗

- **テンプレートの上に本リポジトリの設計を重ねる。** 結果はどちらの体裁でもない
- **白紙レイアウトにテキストボックスを置く。** テンプレートを使っている意味が
  無くなる（`pptx-master-placeholder`）
- **テンプレートのアクセシビリティ違反を黙って引き継ぐ。** 直せないなら
  報告する。守れなかった事実を残す
- **収まらないので体裁を崩す。** 崩す前に内容を割る（`core-density-budget`）。
  それでも収まらないなら、どちらを崩すかは人が決める
