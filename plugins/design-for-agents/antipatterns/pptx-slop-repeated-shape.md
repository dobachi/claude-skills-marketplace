---
id: pptx-slop-repeated-shape
media: pptx
statement: "内容の構造と関係なく、全スライドで同じ図形の型（3つ並べた箱など）を使い回すこと"
why_it_appears: "型を当てはめると速く作れる。内容がその構造を持っているかは確認されない"
instead: "内容が実際に持っている構造に合わせて選ぶ。並列な項目なら箇条書き、比較なら表、量ならグラフ"
violates: [core-diagram-information-test, core-diagram-one-abstraction]
---

# 同じ型の使い回し

反復は、同じ意味のものに対して行われたときだけ「設計された」印象を作る。
意味の違うものに同じ型を当てると、**無い共通性を主張することになる。**

なお、タイトルの位置・余白・色の反復は別物であり、これは守る
（`core-layout-one-grid`）。
