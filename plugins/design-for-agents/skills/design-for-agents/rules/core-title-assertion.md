---
id: core-title-assertion
status: active
tier: SHOULD
media: [pptx]
topic: title
statement: "スライドのタイトルは主張を述べた1文にする。体言止めのトピック名にしない"
values: []
not_applicable_when: "表紙、目次、章扉、付録の見出し"
source:
  kind: consensus
  key: alley-neeley-2005
  ref: "Alley & Neeley 2005（assertion–evidence 構造）"
done_when:
  - id: all-titles-assertive
    applies_to: slide
    predicate: count
    statement: "タイトルが述語を含まないスライドが 0 枚である（表紙・目次・章扉・付録を除く）"
    check: manual
    floor: "本文スライドが3枚以上ある"
---

# タイトルは主張文にする

## なぜ

聞き手はタイトルしか読まないことがある。トピック名は「何について話すか」しか
伝えず、「それで何が言えるのか」を本文に探させる。

Alley & Neeley 2005 は、同じ内容を同じ言葉で話しながらスライドだけを変えた比較で、
主張タイトル＋視覚的証拠の構造のほうが、トピック名＋箇条書きより理解と記憶が
有意に高いことを報告している（p < .01）。**「見やすいから」ではなく
「理解されるから」である。**

## 例

| 悪い（トピック名） | 良い（主張文） |
|---|---|
| 第3四半期の売上 | 第3四半期の売上は前年比18%増で、伸びは既存顧客の更新が牽引した |
| 移行の課題 | 移行の障害は技術ではなく、9月の締めと重なる要員確保である |
| システム構成 | 認証だけを分離したため、他機能を止めずに更新できる |

## 注意

主張文にすると長くなる。**長くなったなら、そのスライドが2つの主張を持っている。**
タイトルを削るのではなく、スライドを割る（`core-density-one-message`）。
