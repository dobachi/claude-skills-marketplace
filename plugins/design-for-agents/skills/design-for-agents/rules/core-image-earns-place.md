---
id: core-image-earns-place
status: active
tier: HOUSE
media: [pptx]
topic: image
statement: "消しても失われるものが無い画像を置かない"
values:
  - "置いてよい画像: 主張の証拠になるもの、対象そのものを示すもの、比較の対象"
  - "置かない画像: 話題に関連するだけの写真、雰囲気のための画像、余白を埋めるための画像"
not_applicable_when: "表紙と章扉。ただし1つのデッキの中で扱いを揃える"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め（情報テストを画像に当てたもの）"
done_when:
  - id: images-carry-information
    applies_to: element
    predicate: count
    statement: "消しても本文の意味が変わらない画像が 0 個である（表紙と章扉を除く）"
    check: manual
    floor: "本文スライドが3枚以上ある。画像を全て消して満たしてはならない"
---

# 画像も情報テストを通す

## 判定

`core-diagram-information-test` と同じ問いを画像に当てる。
**その画像を消したとき、聞き手が知り得なくなることがあるか。**

無いなら消す。余白が残ることは問題ではない（`core-density-budget`）。

## 典型的な不合格

| 置かれ方 | なぜ落ちるか |
|---|---|
| 「チーム」の話に握手の写真 | 話題と関連するだけで、何も述べていない |
| 「成長」の話に上向きの矢印の写真 | 主張はタイトルにあり、写真は繰り返しているだけ |
| 余白が寂しいので風景を敷く | 余白は空けている（`core-ornament-none`） |

## 全面配置

表紙と章扉では、画像を全面に置いてよい。文字を重ねるなら、
コントラスト比を確保する（`core-a11y-contrast-body`）。
半透明の板を敷くのが確実である。
