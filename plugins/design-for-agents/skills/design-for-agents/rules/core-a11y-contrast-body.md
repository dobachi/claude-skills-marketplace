---
id: core-a11y-contrast-body
status: active
tier: MUST
media: [pptx]
topic: a11y
statement: "文字と背景のコントラスト比を、本文で 4.5:1 以上、18pt 以上または 14pt 以上の太字で 3:1 以上にする"
values:
  - "本文: 4.5:1"
  - "大きい文字（18pt 以上、または 14pt 以上の太字）: 3:1"
  - "文字以外の要素（グラフの線、境界）: 3:1"
not_applicable_when: "装飾目的のみで、消しても情報が失われない要素。ただし本リポジトリはそもそも装飾を置かない（core-ornament-none）"
source:
  kind: normative
  key: wcag22
  ref: "WCAG 2.2 SC 1.4.3 Contrast (Minimum) / SC 1.4.11 Non-text Contrast"
done_when:
  - id: body-contrast-4-5
    applies_to: element
    predicate: ratio
    statement: "全ての文字要素について、前景色と背景色のコントラスト比が 4.5 以上である（18pt 以上または 14pt 以上の太字は 3 以上）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文の文字要素が各スライドに1つ以上ある"
---

# コントラスト比

## なぜ

これは好みではなく規範である。WCAG 2.2 SC 1.4.3 が閾値を定めており、
日本では JIS X 8341-3:2016（ISO/IEC 40500:2012 ＝ WCAG 2.0 と一致）が
公共調達で参照される。**逸脱は選択ではなく欠陥である。**

## 上書きされない

ブランド色がこの閾値を満たさない場合、閾値ではなく**使い方**を変える。
多くのブランドブルーは白地の本文サイズで 4.5:1 を割るが、ヘアラインや
見出しとしてなら使える。

## 本リポジトリの既定値（実測値）

| 前景 | 背景 | 比 |
|---|---|---|
| ink `#1A1A1A` | paper `#FFFFFF` | 17.4:1 |
| muted `#6B7280` | paper `#FFFFFF` | 4.83:1 |
| accent `#2F5DA8` | paper `#FFFFFF` | 6.46:1 |
| ink `#F2F2F2` | paper `#111315`（暗色） | 16.63:1 |
| muted `#9AA1AC` | paper `#111315`（暗色） | 7.15:1 |

muted は 4.83:1 であり余裕が小さい。**muted をこれ以上薄くしない。**
