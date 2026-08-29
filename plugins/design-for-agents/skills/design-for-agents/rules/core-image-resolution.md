---
id: core-image-resolution
status: active
tier: HOUSE
media: [pptx]
topic: image
statement: "画像は表示サイズで解像度を満たすものを使い、縦横比を変えない"
values:
  - "投影・画面: 表示サイズで 150dpi 以上"
  - "印刷して配る: 表示サイズで 300dpi 以上"
  - "拡大して不足するものは使わない。縮小して使う"
  - "縦横比: 変更しない"
not_applicable_when: "なし"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: no-stretched-images
    applies_to: element
    predicate: count
    statement: "縦横比が元画像と異なる画像が 0 個である"
    check: manual
    floor: "画像を含むスライドがある場合に限り評価する。画像を消して満たしてはならない"
  - id: resolution-sufficient
    applies_to: element
    predicate: ratio
    statement: "各画像の表示サイズあたりの解像度が 150 以上である"
    check: manual
    floor: "画像を含むスライドがある場合に限り評価する"
---

# 画像の解像度と比率

## なぜ

粗い画像は、内容と無関係に資料全体の信用を落とす。**直せるのは差し替えだけで、
拡大した時点で情報は戻らない。**

縦横比を変えた画像は、人物や製品が実際と違う形で提示されることになる。
比率を変えてよい理由は無い。

## 実務

- 拡大は不足を生む。**足りないものは縮小して使う**か、差し替える
- 図やロゴは SVG など拡大に耐える形式で受け取る
- PowerPoint の画像圧縮（ファイル → 圧縮）は配布前に効かせてよいが、
  印刷して配るなら 300dpi の設定を選ぶ
