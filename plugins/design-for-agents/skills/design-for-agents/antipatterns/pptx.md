# アンチパターン一覧（PowerPoint）

**正は各ファイルである。** この表は転記であり、ここで新しい内容を決めない。
生成に入る直前に読む（INDEX.md 第6節）。

抽象的な戒めではなく、**具体名で禁止する**。名指しされたものだけが消える。

| id | やってはいけないこと | 代わりにすること |
|---|---|---|
| [`pptx-slop-decorated-bullets`](pptx-slop-decorated-bullets.md) | 箇条書きの各項目を色付きの矩形や角丸枠で囲んだもの | 図形を消して箇条書きに戻す。階層を見せたいなら、階層として描き直す |
| [`pptx-slop-fake-process`](pptx-slop-fake-process.md) | 順序が無い項目を「5段階の工程」の型に流し込んだ SmartArt | 項目が並列なら箇条書きか 2×2 にする。実際に順序があるものだけを工程として描く |
| [`pptx-slop-filler-shapes`](pptx-slop-filler-shapes.md) | 六角形、雲、角丸の装飾枠、クリップアートなど、意味を持たない図形 | 四角を使う。既知の図法で意味を持つ形（雲＝クラウドサービスなど）だけを例外とする。余白は空けたままにする |
| [`pptx-slop-meaningless-arrows`](pptx-slop-meaningless-arrows.md) | 向きに意味を持たない矢印、および1枚の図の中で意味が混ざった矢印 | 矢印を消す。残すなら、データの流れ／依存／呼び出し／時間 から1つ選び、凡例に書く |
| [`pptx-slop-pie-per-item`](pptx-slop-pie-per-item.md) | 項目の数に合わせて作られた、区分が4つ以上の円グラフ | 積み上げ棒1本、または値の順に並べた横棒。2要素なら大きな数値で書く |
| [`pptx-slop-rainbow-series`](pptx-slop-rainbow-series.md) | PowerPoint と Excel の既定配色をそのまま使った、8系列以上の折れ線グラフ | 系列を4つまでに絞る。3系列以上を色で分けるなら Okabe-Ito から取る。直接ラベルを置き、強調する1系列以外を灰にする |
| [`pptx-slop-repeated-shape`](pptx-slop-repeated-shape.md) | 内容の構造と関係なく、全スライドで同じ図形の型（3つ並べた箱など）を使い回すこと | 内容が実際に持っている構造に合わせて選ぶ。並列な項目なら箇条書き、比較なら表、量ならグラフ |
| [`pptx-slop-shrunken-body`](pptx-slop-shrunken-body.md) | 枠に収めるために本文の文字を下限より小さくしたスライド | 消せる要素を消す。スライドを割る。付録に移す。文字を縮めるのは選択肢に無い |
| [`pptx-slop-title-band`](pptx-slop-title-band.md) | タイトルの背景に敷いた、スライド幅いっぱいのカラーバンド | 白地に ink のタイトル。区切りが要るならヘアライン1本（tokens の grid.hairlineLength / hairlineWeight） |
| [`pptx-slop-topic-titles`](pptx-slop-topic-titles.md) | 「第3四半期の売上」のような、体言止めのトピック名のタイトル | そのスライドで言えることを1文で書く（「第3四半期の売上は前年比18%増で、伸びは既存顧客の更新が牽引した」） |

## 共通する原因

上の多くは、**指示しなかった判断が既定値で埋まった**結果である。
SmartArt の型、Excel の既定配色、自動縮小、既定のテーマ。
どれも「決めなかったとき」に選ばれるものであり、
決め打ち値（`tokens/pptx.tokens.json`）はこれを防ぐために置いてある。
