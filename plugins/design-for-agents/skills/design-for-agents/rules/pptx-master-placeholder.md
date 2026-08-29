---
id: pptx-master-placeholder
status: active
tier: HOUSE
media: [pptx]
topic: master
statement: "内容はレイアウトのプレースホルダに書く。スライドに直接テキストボックスを置かない"
values:
  - "使うレイアウト: スライドマスターに定義したもののみ"
  - "白紙レイアウト＋テキストボックスの組み合わせを使わない"
not_applicable_when: "なし"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: content-in-placeholders
    applies_to: slide
    predicate: count
    statement: "レイアウトのプレースホルダ外に文字要素を持つスライドが 0 枚である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドに文字要素が1つ以上ある"
  - id: unique-slide-titles
    applies_to: deck
    predicate: count
    statement: "タイトルプレースホルダが空のスライドが 0 枚である"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上ある"
---

# プレースホルダに書く

## なぜ

テキストボックスはスライドマスターの支配を受けない。スライドマスターを
直しても反映されず、書式の変更は全スライドを手で直す作業になる。
`core-type-one-scale` と `core-layout-one-grid` は、**スライドマスターが効いていて
初めて成立する**。

読み上げ順序と代替テキストもプレースホルダを前提に決まるため、
アクセシビリティの確認もテキストボックスでは通らない。

## 生成でこれが崩れる経路

python-pptx を手書きすると `slide_layouts[6]`（白紙）＋ `add_textbox()` に
落ちる。これはスライドマスターが何も支配していない状態であり、本ルールの正反対である。
**生成は `pptx-build` に渡す**（INDEX.md 第9節）。

## 確認

`pptx-build` の `audit_pptx.py` が、プレースホルダ外に内容を持つスライドを
検出して失敗させる。v0.2 でこの done_when を automated に昇格させる先はここである。
