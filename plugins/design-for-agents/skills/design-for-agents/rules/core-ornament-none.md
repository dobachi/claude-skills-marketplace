---
id: core-ornament-none
status: active
tier: HOUSE
media: [pptx]
topic: ornament
statement: "意味を担わない図形・効果を置かない"
values:
  - "置かないもの: グラデーション、ドロップシャドウ、ベベル、光彩、反射、WordArt、クリップアート、装飾的な角丸枠、六角形、何も表さないコネクタ、タイトル背景の全幅カラーバンド"
not_applicable_when: "組織のテンプレートが装飾を含む場合。テンプレートを書き換えず、そのまま使う（pptx-constraint-template）"
source:
  kind: house
  key: house
  ref: "本リポジトリの決め"
done_when:
  - id: no-ornament-shapes
    applies_to: element
    predicate: absent
    statement: "グラデーション塗り、影、ベベル、光彩、反射のいずれかを持つ図形が存在しない"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドに本文または図が1つ以上ある"
  - id: no-title-band
    applies_to: slide
    predicate: absent
    statement: "タイトル領域の背景に、スライド幅いっぱいの塗り図形が存在しない"
    check: automated
    detector: "scripts/check_deck.py <deck.pptx>"
    floor: "本文スライドが3枚以上あり、各スライドにタイトルがある"
---

# 装飾を置かない

## なぜ具体名で書くのか

「装飾を控える」では行動が変わらない。**名指しされたものだけが消える。**

## 全幅バンドを特に禁じる理由

タイトル背景のカラーバンドは、スライドごとに描き直されるため座標が揺れる。
高速で送ると上下にずれて見え、これが**生成された資料の最も分かりやすい徴候**に
なる。区切りが要るならヘアライン1本で足りる（`core-color-four-slots`）。

## 判定

その要素を消したとき、聞き手が知り得なくなることがあるか。無いなら消す。
これは図に対する情報テストを、装飾にも適用したものである。

## クリーンは「少ない」ではない

3語しか載っていない白いスライドは、クリーンではなく空である。
装飾を消すことと、根拠を消すことは違う。**出典・単位・但し書きは残す。**
