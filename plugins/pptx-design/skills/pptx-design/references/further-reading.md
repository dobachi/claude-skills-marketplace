# Further Reading — which source, and when

A deck raises questions this skill has already decided (see `clean-design-system.md`) and
questions it deliberately has not. This file routes the second kind. It is long on purpose:
you are not meant to read it, you are meant to **look up one row when a specific question
is open**, then go back to work.

## Contents

- [Rules of use](#rules-of-use) — cite only what you consulted; one source per question
- [Routing table](#routing-table) — **start here**: open question → the one source that answers it
- [A. Fetchable references and standards](#a-fetchable-references-and-standards) — URLs you can consult and quote (WCAG, color tools, typography, charts, diagrams, deck templates)
- [B. Books](#b-books) — narrative, visual design, data visualization, diagrams, cognition, accessibility; recommend, don't quote
- [C. Japanese-language sources](#c-japanese-language-sources) — 日本語スライドの体裁・書体・邦訳書
- [D. Samples](#d-samples--for-the-authors-eye-not-the-models) — sample decks and galleries, and why they need a human's eye
- [Attribution on the slide itself](#attribution-on-the-slide-itself) — design influence vs. a number that needs a source

## Rules of use

1. **Enter from the symptom, not the shelf.** Use the routing table below. If no row matches
   the open question, the answer is probably already in this skill's other references.
2. **Cite only what you actually consulted in this session.** §A entries are fetchable —
   fetch before quoting. §B/§C are books you cannot open: recommend them to the author, and
   never attribute a specific number, rule, or quotation to one you have not read. The
   distilled principles this skill runs on are in `SKILL.md` and the other references, and
   they stand on their own without a citation.
3. **One source per open question.** The author asked a design question, not for a syllabus.
4. **For "what is the rule?", prefer the primary standard** (WCAG) over any commentary on it.
5. **URLs are entry points, not permalinks.** If one fails, keep the title and author and
   search for it; say the link failed rather than paraphrasing from memory.

## Routing table

| When the open question is… | Go to | What you get there |
|---|---|---|
| The argument has no spine; the conclusion is buried | Minto, *The Pyramid Principle*; Duarte, *Resonate* | Governing thought, top-down structure, narrative arc |
| Who is this deck for, and what do they already believe? | Duarte, *slide:ology* (audience chapter); Heath & Heath, *Made to Stick* | Audience mapping, what makes an idea stick |
| Investor deck: how many slides, in what order | Sequoia "Writing a Business Plan"; Kawasaki "10/20/30"; YC Library | The canonical 10–15 slide sequence and the question each slide answers |
| Sales deck: how to open without leading with the product | Raskin, "The Greatest Sales Deck I've Ever Seen" | Name-the-change → stakes → promised land → gifts |
| This should be a document, not slides | Duarte, *Slidedocs*; Tufte, *The Cognitive Style of PowerPoint* | The read-not-present format, and the case against slideware for dense argument |
| Research / conference talk | Peyton Jones, "How to Give a Great Research Talk"; Doumont, *Trees, Maps, and Theorems*; 宮野公樹 | Talk structure for technical audiences |
| Which chart type for this data | FT Visual Vocabulary; Zelazny, *Say It with Charts*; Knaflic, *Storytelling with Data* | Chart choice driven by the comparison being made |
| What can be erased from this chart | Tufte, *The Visual Display of Quantitative Information*; Few, *Show Me the Numbers* | Data-ink ratio, chartjunk, grid/axis restraint |
| Too many series for four color slots | Knaflic (gray-the-rest); ColorBrewer; Viz Palette; IBM Carbon data-viz palettes | Emphasis by desaturation; tested categorical ramps |
| Is this axis / scale honest? | Cairo, *How Charts Lie*; Wong, *WSJ Guide to Information Graphics*; Huff, *How to Lie with Statistics* | Truncated axes, dual axes, log scales, area-vs-length distortion |
| A table would beat a chart here | Few, *Show Me the Numbers*; Schwabish, *Better Data Visualizations* | Table design, alignment, when tables win |
| One number carries the slide | Berinato, *Good Charts*; Knaflic | Big-number treatment and its supporting context |
| Is this diagram structure or decoration? | This skill's information test (`diagrams-and-architecture.md`); Bertin, *Semiology of Graphics*; Horn, *Visual Language* | What visual variables can and cannot encode |
| Architecture diagram: what level of detail | Simon Brown, C4 model; Richards & Ford, *Fundamentals of Software Architecture* | One diagram per zoom level, consistent element semantics |
| Why does a diagram help at all — I need to justify it | Tversky, *Mind in Motion*; Mayer, *Multimedia Learning* | Spatial cognition; the multimedia and spatial-contiguity principles |
| "Don't read your slides" — I need the evidence | Mayer, *Multimedia Learning* (redundancy principle); Sweller, cognitive load theory | Why identical spoken + written text lowers comprehension |
| How much fits on one slide, defensibly | Sweller / Mayer; Kosslyn, *Clear and to the Point* | Working-memory limits applied to slides |
| Typeface choice and setting | Butterick, *Practical Typography*; Lupton, *Thinking with Type*; Bringhurst, *The Elements of Typographic Style* | Point size, measure, leading, pairing |
| The grid is not holding | Müller-Brockmann, *Grid Systems in Graphic Design*; Elam, *Grid Systems* | Column/margin systems and why they work |
| Non-designer needs four rules that always help | Robin Williams, *The Non-Designer's Design Book* | Contrast, Repetition, Alignment, Proximity |
| The slide is loud and I cannot say why | Reynolds, *Presentation Zen* / *Presentation Zen Design* | Restraint, whitespace (*ma*), image-led slides |
| Contrast ratio: what exactly is required | WCAG 2.2 SC 1.4.3, SC 1.4.11; WebAIM Contrast Checker | The normative thresholds and a checker |
| Will this read for color-blind viewers | Color Oracle; Coblis; ColorBrewer (colorblind-safe filter) | Simulation and safe palettes |
| PowerPoint accessibility, practically | Microsoft, "Make your PowerPoint presentations accessible…"; W3C WAI, "How to Make Your Presentations Accessible to All" | Alt text, reading order, the built-in checker |
| Choosing and using photographs | Reynolds, *Presentation Zen Design*; Duarte, *slide:ology* | Full-bleed imagery, image as argument not decoration |
| Thinking through a diagram by hand first | Roam, *The Back of the Napkin* | Six ways of seeing, sketch-first |
| Japanese-language deck conventions | 伝わるデザイン (tsutawarudesign.com); 高橋・片山 | Japanese typography, UD fonts, slide hygiene |
| I want to look at good decks | §D below | Public sample decks and graphics desks |

---

## A. Fetchable references and standards

Reachable by URL; consult these before citing them. Entry points, not permalinks.

### Accessibility (normative)

- **WCAG 2.2** — <https://www.w3.org/TR/WCAG22/>. The standard itself.
  - Understanding SC 1.4.3 Contrast (Minimum) — <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html>
  - Understanding SC 1.4.11 Non-text Contrast — <https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html>
- **W3C WAI, "How to Make Your Presentations Accessible to All"** — <https://www.w3.org/WAI/teach-advocate/accessible-presentations/>
- **Microsoft, "Make your PowerPoint presentations accessible to people with disabilities"** —
  support.microsoft.com (search the title). Alt text, reading order, the Accessibility Checker.
- **WebAIM Contrast Checker** — <https://webaim.org/resources/contrastchecker/>

### Color

- **ColorBrewer** (Cynthia Brewer) — <https://colorbrewer2.org>. Sequential/diverging/qualitative ramps with a colorblind-safe filter.
- **Viz Palette** (Elijah Meeks, Susie Lu) — <https://projects.susielu.com/viz-palette>. Test a categorical palette against color deficiency and small marks.
- **Color Oracle** — <https://colororacle.org>. Full-screen color-blindness simulator.
- **Coblis** — <https://www.color-blindness.com/coblis-color-blindness-simulator/>. Upload a slide image, see it simulated.
- **Datawrapper blog** (Lisa Charlotte Muth) — <https://blog.datawrapper.de/>. The most practical writing on color for charts.
- **IBM Carbon — Data visualization** — <https://carbondesignsystem.com/data-visualization/getting-started/>. A production palette system with stated rules.
- **Material Design 3** — <https://m3.material.io>. Color roles and tonal palettes, if the brand has none.

### Typography

- **Matthew Butterick, *Practical Typography*** — <https://practicaltypography.com>. Free, complete, opinionated; the fastest answer to most type questions.
- **Google Fonts** — <https://fonts.google.com>. Licensing-safe families, including Noto for CJK coverage.

### Charts

- **FT Visual Vocabulary** — <https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary>. A poster mapping the comparison you want to make onto chart types. The single best first stop for chart choice.
- **Claus Wilke, *Fundamentals of Data Visualization*** — <https://clauswilke.com/dataviz/>. Full text free; strong on color and on directory-of-visualizations.
- **Kieran Healy, *Data Visualization: A Practical Introduction*** — <https://socviz.co>. Full text free.
- **Storytelling with Data blog** — <https://www.storytellingwithdata.com/blog>. Worked makeovers.
- **Junk Charts** (Kaiser Fung) — <https://junkcharts.typepad.com>. Critique-by-example.

### Diagrams

- **C4 model** (Simon Brown) — <https://c4model.com>. Context / Container / Component / Code, one level per diagram.
- **Mermaid** — <https://mermaid.js.org>. Text-defined diagrams; the default in `document-figures`.
- **PlantUML** — <https://plantuml.com>. When the notation needs to be formal (UML, ArchiMate).

### Deck genres and templates

- **Sequoia Capital, "Writing a Business Plan"** — <https://www.sequoiacap.com/article/writing-a-business-plan/>. The reference pitch sequence.
- **Guy Kawasaki, "The 10/20/30 Rule of PowerPoint"** — <https://guykawasaki.com/the_102030_rule/>
- **Y Combinator Library** — <https://www.ycombinator.com/library>. Search "pitch deck"; seed-deck guidance slide by slide.
- **Andy Raskin, "The Greatest Sales Deck I've Ever Seen"** — Medium (search the title). The strategic-narrative structure.
- **Nancy Duarte, *Slidedocs*** — <https://www.duarte.com/slidedocs/>. The read-don't-present hybrid format, itself published as one.
- **Simon Peyton Jones, "How to Give a Great Research Talk"** — microsoft.com/research (search the title). Slides and video.

---

## B. Books

You cannot open these. Recommend them to the author, and do not attribute specifics to
them from memory.

### Narrative, structure, delivery

- Barbara Minto, *The Pyramid Principle* — governing thought, MECE, top-down order. The origin of the consulting deck.
- Nancy Duarte, *slide:ology* — the craft book: audience, storyboarding, diagram types, data slides.
- Nancy Duarte, *Resonate* — narrative arc, the "what is / what could be" sparkline.
- Nancy Duarte, *HBR Guide to Persuasive Presentations* — the short, practical distillation.
- Nancy Duarte, *DataStory* — turning findings into a recommendation.
- Garr Reynolds, *Presentation Zen* — restraint, story, image-led design.
- Garr Reynolds, *Presentation Zen Design* — the visual companion: type, color, space, imagery.
- Chip Heath & Dan Heath, *Made to Stick* — why some ideas survive retelling (SUCCESs).
- Chris Anderson, *TED Talks* — through-line, structure, rehearsal.
- Jerry Weissman, *Presenting to Win* — the point-B story and audience benefit.
- Carmine Gallo, *Talk Like TED* — delivery patterns, analyzed.
- Jean-luc Doumont, *Trees, Maps, and Theorems* — the most rigorous short book on communicating technical work; slides, documents, and talks under one theory.

### Visual design and typography

- Robin Williams, *The Non-Designer's Design Book* — CRAP. The highest ratio of improvement to pages read.
- Ellen Lupton, *Thinking with Type* — type anatomy, hierarchy, grids.
- Robert Bringhurst, *The Elements of Typographic Style* — the reference work.
- Josef Müller-Brockmann, *Grid Systems in Graphic Design* — the source of the modular grid.
- Kimberly Elam, *Grid Systems: Principles of Organizing Type* — a short, diagrammatic introduction.
- Alex W. White, *The Elements of Graphic Design* — space as an active element.
- Dan Roam, *The Back of the Napkin* — thinking and selling with hand-drawn pictures.

### Data visualization

- Edward Tufte, *The Visual Display of Quantitative Information* — data-ink ratio, chartjunk, lie factor.
- Edward Tufte, *Envisioning Information* — layering, separation, small multiples.
- Edward Tufte, *Visual Explanations* — showing cause, motion, process.
- Edward Tufte, *Beautiful Evidence* — sparklines, evidence presentation.
- Edward Tufte, *The Cognitive Style of PowerPoint* — the essay-length case against slideware for serious analysis; read before defending a dense deck.
- Cole Nussbaumer Knaflic, *Storytelling with Data* — chart choice, decluttering, gray-the-rest emphasis, story.
- Cole Nussbaumer Knaflic, *Storytelling with Data: Let's Practice!* — exercises with worked solutions.
- Alberto Cairo, *The Functional Art* / *The Truthful Art* / *How Charts Lie* — visualization as journalism; honesty and uncertainty.
- Stephen Few, *Show Me the Numbers* — tables and graphs for business, in detail.
- Stephen Few, *Information Dashboard Design* — density without noise.
- Gene Zelazny, *Say It with Charts* — the classic message→chart-form mapping.
- Dona M. Wong, *The Wall Street Journal Guide to Information Graphics* — compact, prescriptive, print-grade.
- Scott Berinato, *Good Charts* — HBR's framing: which of four chart situations you are in.
- Jonathan Schwabish, *Better Data Visualizations* / *Better Presentations* — chart catalog and academic-to-audience translation.
- Andy Kirk, *Data Visualisation: A Handbook for Data Driven Design* — a full design process.
- Claus Wilke, *Fundamentals of Data Visualization* — also in print; see §A for the free text.
- William S. Cleveland, *The Elements of Graphing Data* — the perception experiments behind chart rankings.
- Naomi Robbins, *Creating More Effective Graphs* — before/after pairs.
- Colin Ware, *Information Visualization: Perception for Design* — the vision science underneath.
- Isabel Meirelles, *Design for Information* — structures of information graphics.
- Darrell Huff, *How to Lie with Statistics* — short, old, still the fastest inoculation.

### Diagrams, notation, architecture

- Jacques Bertin, *Semiology of Graphics* — the foundational theory of visual variables (position, size, value, texture, color, orientation, shape).
- Robert E. Horn, *Visual Language* — how words and images combine into a syntax.
- Simon Brown, *Software Architecture for Developers* — the C4 model in book form.
- Mark Richards & Neal Ford, *Fundamentals of Software Architecture* — trade-off analysis worth putting on a slide.
- Barbara Tversky, *Mind in Motion* — why spatial arrangement carries meaning; the case for diagrams.

### Cognition and learning

- Richard E. Mayer, *Multimedia Learning* — the redundancy, coherence, signaling, and spatial-contiguity principles. The evidence base for "don't read your slides" and "cut decorative graphics".
- Ruth Colvin Clark & Richard E. Mayer, *e-Learning and the Science of Instruction* — the same, applied.
- Stephen M. Kosslyn, *Clear and to the Point* — psychological principles for slide design.
- Stephen M. Kosslyn, *Graph Design for the Eye and Mind* — perception applied to charts.
- John Sweller et al., cognitive load theory — the primary literature behind slide density limits.

### Accessibility

- Sarah Horton & Whitney Quesenbery, *A Web for Everyone* — designing for the full range of users.
- Laura Kalbag, *Accessibility for Everyone* — short and practical.

---

## C. Japanese-language sources

- **伝わるデザイン｜研究発表のユニバーサルデザイン**（高橋佑磨・片山なつ）— <https://tsutawarudesign.com>。日本語スライドの体裁、書体選び、UDフォント、余白。無料で全文が読め、日本語資料の第一参照になる。
- 宮野公樹『学生・研究者のための 使える！PowerPointスライドデザイン』化学同人 — 研究発表に特化。1枚1メッセージの徹底。
- 山口周『外資系コンサルのスライド作成術』東洋経済新報社 — メッセージライン、チャートの型、作業の順序。
- ジーン・ゼラズニー『マッキンゼー流図解の技術』東洋経済新報社 — *Say It with Charts* の邦訳。
- バーバラ・ミント『考える技術・書く技術』ダイヤモンド社 — *The Pyramid Principle* の邦訳。
- コール・ヌッスバウマー・ナフリック『Google流資料作成術』日本実業出版社 — *Storytelling with Data* の邦訳。
- ガー・レイノルズ『プレゼンテーションZen』丸善出版 — *Presentation Zen* の邦訳。
- ナンシー・デュアルテ『ザ・プレゼンテーション』ダイヤモンド社 — *Resonate* の邦訳。
- ロビン・ウィリアムズ『ノンデザイナーズ・デザインブック』マイナビ出版 — *The Non-Designer's Design Book* の邦訳。
- 筒井美希『なるほどデザイン』エムディエヌコーポレーション — 目で見て分かる編集デザイン入門。
- 坂本伸二『デザイン入門教室』SBクリエイティブ — 配色・レイアウト・書体の基礎。
- ingectar-e『けっきょく、よはく。』ソシム — 余白の効かせ方をビフォー／アフターで。
- 木村博之『インフォグラフィックス』誠文堂新光社 — 図解表現の分類と作例。
- **BIZ UDゴシック / BIZ UDPゴシック**（モリサワ、Windows 同梱）— 日本語スライドの本文書体として無難。游ゴシックより字面が大きく、投影で潰れにくい。

---

## D. Samples — for the author's eye, not the model's

**Read this first:** you cannot see images. A sample deck tells you nothing until a human
looks at it and says what to imitate. Use §D by handing links to the author and asking
which specific property they want (density? type scale? color restraint? diagram style?),
then translate that answer into `clean-design-system.md` values. Never claim a deck
"looks like" anything you have not been shown.

- **Public startup decks** — Airbnb, Buffer, and Uber's early decks circulate publicly. Prefer the founders' own posts over aggregator sites, which re-crop and re-caption.
- **Duarte, Slidedocs** — <https://www.duarte.com/slidedocs/>. The sample slidedoc is itself the demonstration.
- **Information is Beautiful Awards** — <https://www.informationisbeautifulawards.com>. Award-winning information design, with entries described in text.
- **Newsroom graphics desks** — Financial Times, The Economist, Reuters Graphics, The New York Times' The Upshot. The working standard for honest business charts.
- **Reference implementation inside this marketplace** — `pptx-build/tests/fixtures/clean-deck.yaml`. A deck that satisfies `clean-design-system.md`, expressed as text you *can* read. When the question is "what does the house style look like concretely", this beats any image.

---

## Attribution on the slide itself

Citing a *data source* on a slide (the 8–10 pt gray "Source:" footnote) is a different
obligation from the reading above, and is covered in `data-visualization.md`. A design
influence needs no footnote; a number does.
