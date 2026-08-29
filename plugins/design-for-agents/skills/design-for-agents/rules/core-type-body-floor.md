---
id: core-type-body-floor
status: active
tier: HOUSE
media: [pptx]
topic: type
statement: "本文サイズは下限を下回らない。収まらないときは文字を縮めず、内容を削るかスライドを割る"
values:
  - "本文の下限: 18pt"
  - "第2階層の下限: 16pt"
  - "自動縮小を許すのはタイトルのみ（30pt から 24pt まで）"
not_applicable_when: "出典行・ページ番号（11pt）、表の中（15pt）、キャプション（15pt / 注記 14pt）。これらは本文ではない"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: body-not-below-floor
    applies_to: element
    predicate: count
    statement: "本文プレースホルダ内の文字サイズが 18pt 未満の要素が 0 個である（第2階層は 16pt 未満で 0 個）"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドの本文が1行以上ある"
---

# 本文下限は目標ではなく床

## なぜ

「収まらないから小さくする」は、情報量の問題を可読性の問題にすり替える操作である。
量は減っていないので、聞き手の負荷は下がらず、読めなくなる分だけ悪化する。

**下限は、内容を割る判断を強制するための装置である。** 18pt で収まらないなら、
そのスライドは密度予算を超えている（`core-density-budget`）。

## 順序

1. 消せる要素を消す（情報テスト）
2. スライドを割る（`core-density-one-message`）
3. 付録に移す
4. **文字を縮める — これは選択肢に無い**

## 自動縮小

PowerPoint の自動縮小はタイトルにだけ許す。本文で有効にすると、上の判断が
すべて自動で回避され、下限が機能しなくなる。
