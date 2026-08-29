---
id: core-a11y-alt-text
status: active
tier: MUST
media: [pptx]
topic: a11y
statement: "文字以外の要素に代替テキストを付ける。代替テキストにはその要素から何が言えるかを書く"
values:
  - "対象: 図、グラフ、写真、アイコン、表以外の図形"
  - "書く内容: そこから言えること（「棒グラフ」ではなく「第3四半期に継続率が84%へ上がった」）"
  - "装飾目的の要素: 装飾として印を付ける。ただし本リポジトリは装飾を置かない（core-ornament-none）"
not_applicable_when: "同じ内容が本文に文として書かれている場合。その場合は装飾として印を付ける"
source:
  kind: normative
  key: wcag22
  ref: "WCAG 2.2 SC 1.1.1 Non-text Content"
done_when:
  - id: alt-text-present
    applies_to: element
    predicate: exists
    statement: "文字以外の各要素に、空でない代替テキストまたは装飾の印のいずれかが設定されている"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "図またはグラフを含むスライドがある場合に限り評価する。図を消して満たしてはならない"
  - id: alt-text-states-takeaway
    applies_to: element
    predicate: count
    statement: "代替テキストが要素の種類だけを述べているものが 0 個である"
    check: manual
    floor: "図またはグラフを含むスライドがある場合に限り評価する"
---

# 代替テキスト

## なぜ

規範である。WCAG 2.2 SC 1.1.1 が文字以外の要素に代替を求めており、
日本では JIS X 8341-3:2016 が同じ内容を持つ。**逸脱は選択ではなく欠陥である。**

## 「棒グラフ」と書かない

要素の種類を書いても、その要素が担っていた情報は伝わらない。
代替テキストに書くのは**そこから言えること**である。
これは `core-chart-takeaway-note` の注記と同じ内容になる。

| 悪い | 良い |
|---|---|
| 棒グラフ | 第3四半期に継続率が84%へ上がり、伸びは既存顧客に集中した |
| システム構成図 | 認証だけが分離されており、他の機能を止めずに更新できる |

## 確認

PowerPoint のアクセシビリティチェッカーが未設定の要素を検出する。
v0.2 でこの done_when を automated に昇格させる先はここである。
