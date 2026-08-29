# 出典台帳

ルールの `source.key` が指す先。**URL はここにしか書かない**（各ルールに再掲しない）。

## 使い方の規則

1. **読んでいないものに、具体的な数値・規則・引用を帰属させない。**
   本を推薦するのと、そこから数値を引くのは別である
2. **`kind: house` を規範のふりをさせない。** 出典が出せない値は
   「本リポジトリの決め」と書く。それは恥ではなく、上書き可能であることの表明である
3. **規範（`normative`）は条番号の粒度で指す。** 「WCAG に従う」ではなく
   「WCAG 2.2 SC 1.4.3」と書く

---

## normative — MUST に対応

| key | 出典 | 何を定めているか | URL |
|---|---|---|---|
| `wcag22` | W3C, Web Content Accessibility Guidelines (WCAG) 2.2, W3C Recommendation | SC 1.4.3 Contrast (Minimum): 本文 4.5:1、大きい文字（18pt 以上、または 14pt 以上の太字）3:1。SC 1.4.11 Non-text Contrast: 3:1 | https://www.w3.org/TR/WCAG22/ |
| `jis-x-8341-3` | JIS X 8341-3:2016（高齢者・障害者等配慮設計指針—情報通信における機器，ソフトウェア及びサービス—第3部：ウェブコンテンツ） | ISO/IEC 40500:2012（＝WCAG 2.0）と一致する内容。日本の公共調達で参照される。WCAG 2.1 / 2.2 に対応する JIS は未制定 | https://waic.jp/docs/jis2016/understanding/201604/ |

## consensus — SHOULD に対応

| key | 出典 | 何を支持するか | URL |
|---|---|---|---|
| `alley-neeley-2005` | Alley, M. & Neeley, K. A., "Rethinking the Design of Presentation Slides: A Case for Sentence Headlines and Visual Evidence", *Technical Communication* 52(4), 2005 | 主張タイトル＋視覚的証拠の構造（assertion–evidence）。トピック名の見出しより理解と記憶が有意に高い（p < .01） | https://writing.engr.psu.edu/2005_alley_neeley.pdf |
| `cleveland-mcgill-1984` | Cleveland, W. S. & McGill, R., "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods", *JASA* 79(387), 1984 | 量の符号化の精度順: 共通軸上の位置 > 非整列軸上の位置 > 長さ・方向・角度 > 面積 > 体積・曲率 > 濃淡・色。円グラフ（角度・面積）が棒（位置・長さ）に劣る根拠 | https://www.jstor.org/stable/2288400 |
| `okabe-ito` | Okabe, M. & Ito, K., "Color Universal Design (CUD): How to make figures and presentations that are friendly to colorblind people" | P型・D型・T型の色覚で識別可能な8色パレット（`#E69F00` `#56B4E9` `#009E73` `#F0E442` `#0072B2` `#D55E00` `#CC79A7` `#000000`） | https://jfly.uni-koeln.de/color/ |
| `tufte-1983` | Tufte, E. R., *The Visual Display of Quantitative Information*, Graphics Press, 1983 | データインク比、チャートジャンク。**方向のみを引く。具体的な閾値を帰属させない** | — |
| `mayer-multimedia` | Mayer, R. E., *Multimedia Learning*, Cambridge University Press | 冗長性原理（同一内容の音声＋文字は理解を下げる）、一貫性原理（無関係な要素は学習を妨げる）、signaling 原理。**方向のみを引く** | — |
| `sweller-clt` | Sweller, J., Cognitive Load Theory | 作業記憶の限界。1スライドの情報量の根拠となる方向。**「7±2」を引かない**（Miller 1956 は短期記憶の別の文脈であり、スライドの容量規定ではない） | — |
| `williams-crap` | Williams, R., *The Non-Designer's Design Book* | Contrast / Repetition / Alignment / Proximity。整列と反復が「設計された」印象を作る | — |
| `muller-brockmann` | Müller-Brockmann, J., *Grid Systems in Graphic Design* | グリッドによる配置。要素は目測ではなく構造で揃える | — |
| `minto-pyramid` | Minto, B., *The Pyramid Principle* | 結論を先に置く構造。支配的思考とその根拠の階層 | — |
| `c4model` | Brown, S., C4 model | 構造図は1枚につき1つのズームレベル。要素の意味を図の中で一貫させる | https://c4model.com |
| `ft-visual-vocabulary` | Financial Times, Visual Vocabulary | 「何を比較したいか」からチャート種を選ぶ対応表 | https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary |
| `butterick` | Butterick, M., *Practical Typography* | 文字サイズ、行長、行間、書体の組み合わせ | https://practicaltypography.com |
| `ms-a11y-pptx` | Microsoft, "Make your PowerPoint presentations accessible to people with disabilities" | 代替テキスト、読み上げ順序、一意のスライドタイトル、組み込みのアクセシビリティチェッカー | https://support.microsoft.com |

## house — HOUSE に対応

| key | 意味 |
|---|---|
| `house` | 本リポジトリの決め。外部の出典は無い。正解が複数あるなかから1つ選んだもの、または迷いを消すために決めた値。**ユーザ指定・ブランド・組織テンプレートがあれば即上書きされる** |

## 引いてはいけないもの

| 出典 | 理由 |
|---|---|
| Miller 1956「7±2」 | 短期記憶の項目数に関する研究であり、スライドの箇条書き数の根拠ではない。後続研究（Cowan 2001）は約4としており、いずれにせよスライド設計の規範として引くのは誤用 |
| 「学習定着率のピラミッド」（見た10%、聞いた20%…） | 出所不明の数値であり、原典が存在しない |
| 「人は視覚から情報の80%を得る」等の割合 | 出所不明 |
