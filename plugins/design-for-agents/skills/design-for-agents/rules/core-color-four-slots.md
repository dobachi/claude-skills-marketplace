---
id: core-color-four-slots
status: active
tier: HOUSE
media: [pptx]
topic: color
statement: "本文・見出し・装飾に使う色は paper / ink / muted / accent の4枠だけにする。5つ目を作らない"
values:
  - "paper: #FFFFFF"
  - "ink: #1A1A1A"
  - "muted: #6B7280"
  - "accent: #2F5DA8"
not_applicable_when: "グラフと表の内部（core-color-semantic-data-only）。組織のテンプレートがある場合はそちらが優先する（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: only-four-slots
    applies_to: element
    predicate: member
    statement: "グラフと表の内部を除く文字色の種類が 3 以下である（紙は背景なので数えない）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドに文字要素がある"
---

# 色は4枠

## 条件が数えるのは「色数」であって色値ではない

ブランドやテンプレートがあれば `accent` は差し替わる。**差し替わっても
「4枠しかない」は成り立つ**ので、完了条件は色数を数える。特定の色値と
一致するかを見るのは誤りである（この誤りは検出器を実物に当てて分かった）。

## なぜこれが HOUSE なのか

**4という数に外部の根拠は無い。** 決めないと色が増え続けるから決めている。
ブランドや組織テンプレートがあれば、そちらが即座に優先する。上書きされることは
このルールの失敗ではない。

決めておく効用は具体的である。色を足す判断が発生しなくなり、スライド間で
色が揺れなくなり、`accent` が本当に強調として効く。

## 各枠の役割

| 枠 | 使いどころ |
|---|---|
| paper | 背景。全スライド共通 |
| ink | 見出しと本文。純黒 `#000000` にはしない |
| muted | 第2階層、キャプション、出典行、ページ番号 |
| accent | ヘアライン1本と、1スライドにつき1箇所の強調 |

`accent` を1スライドで2回以上使わない。2回使えば、それは強調ではなく地の色である。

## ブランド色の入れ方

ブランドの主要色を `accent` に**転写する**。paper と ink は中立のまま置く。
転写前に `core-a11y-contrast-body` の閾値を確認する。
