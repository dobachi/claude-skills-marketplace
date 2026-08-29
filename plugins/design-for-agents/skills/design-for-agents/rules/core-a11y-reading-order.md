---
id: core-a11y-reading-order
status: active
tier: MUST
media: [pptx]
topic: a11y
statement: "スライド内の要素の読み上げ順序を、意味の通る順に設定する"
values:
  - "順序: タイトル、本文、図とその説明、出典行"
  - "全スライドのタイトルを空にしない"
  - "同一デッキ内でタイトルを重複させない"
not_applicable_when: "なし"
source:
  kind: normative
  key: wcag22
  ref: "WCAG 2.2 SC 1.3.2 Meaningful Sequence"
done_when:
  - id: reading-order-set
    applies_to: slide
    predicate: count
    statement: "読み上げ順序がタイトルより前に本文を置いているスライドが 0 枚である"
    check: manual
    floor: "本文スライドが3枚以上あり、各スライドに要素が2つ以上ある"
  - id: titles-unique
    applies_to: deck
    predicate: count
    statement: "タイトルが他のスライドと同一のスライドが 0 枚である（章扉を除く）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上ある"
---

# 読み上げ順序

## なぜ

規範である（WCAG 2.2 SC 1.3.2）。読み上げ順序は、画面に見えている配置とは
別に保持されており、**見た目が正しくても順序が壊れていることがある。**

## 崩れる経路

要素を後から追加すると、追加順が読み上げ順になる。図を最後に足したデッキでは、
図が本文より後ろに来るとは限らない。プレースホルダに書いていれば
レイアウトの順序が効く（`pptx-master-placeholder`）。

## タイトルの重複

同じタイトルのスライドが複数あると、読み上げでも目次でも区別が付かない。
主張タイトルにすれば重複はほぼ起きない（`core-title-assertion`）。
「続き」「（2）」を足すのではなく、それぞれの主張を書く。
