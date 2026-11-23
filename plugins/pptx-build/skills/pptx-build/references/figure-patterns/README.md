# Figure patterns

A figure is chosen by the **logic it has to show**, not by what looks interesting. This
catalog lists the generally recognised patterns — comparison, sequence, cycle, hierarchy,
overlap, funnel and the rest — each with when to use it, when not, the mistakes that make it
fail, what makes it look good, and a spec that draws it natively with this skill.

- `patterns.yaml` — the catalog (the source of truth; one entry per pattern)
- `img/` — a render of each pattern's spec (640 × 360, from `assets/samples/figure-patterns.yaml`)
- `../../assets/find_pattern.py` — search it by intent, in Japanese or English

## How to use it

1. **State the logic in one line** before drawing: 「3つの方式を同じ軸で比べる」, 「誰が何をするか」,
   "causes converging on one problem". If you cannot say it, the slide is not ready for a figure.
2. **Search**: `python3 assets/find_pattern.py "3つを比べる"` — ranked patterns, why each
   matched, the image path, and a spec to adapt. `--show ID` prints one entry in full, `--list` all.
3. **Pick one and adapt its spec.** Keep its design notes: one accent for the point, one shape per
   kind of thing, labels short and inside, everything on the grid.
4. **Validate.** `validate_deck.py` prints `pattern hint:` lines (INFO, never a failure) when a
   diagram's shape matches a pattern that would draw it better — a loop laid out as a line, a
   table built from loose boxes, every edge through one node, three scattered fills with no legend.

## Index

`native` = one figure kind draws the whole pattern; `composed` = built from existing parts as the
spec shows.

| Pattern | Name | Logic | Draws with |
|---|---|---|---|
| [`compare-matrix`](img/compare-matrix.png) | 比較表 / Comparison matrix | comparison | `matrix` (native) |
| [`a-vs-b`](img/a-vs-b.png) | 二者の対比 / A versus B | comparison (two) | `before_after`, `arrow: false` (native) |
| [`before-after`](img/before-after.png) | 変化の前後 / Before and after | before/after | `before_after` (native) |
| [`process-flow`](img/process-flow.png) | 一方向の流れ / Process flow | sequence | `flow` (native) |
| [`steps-detailed`](img/steps-detailed.png) | 説明つきの手順 / Numbered steps | sequence | `type: steps` (composed) |
| [`cycle`](img/cycle.png) | 循環 / Cycle | cycle | `cycle` (native) |
| [`feedback-loop`](img/feedback-loop.png) | 戻りのある流れ / Flow with feedback | feedback loop | `flow` + `feedback` (native) |
| [`hierarchy-org`](img/hierarchy-org.png) | 階層・組織図 / Hierarchy | hierarchy | `tree`, `direction: down` (native) |
| [`logic-tree`](img/logic-tree.png) | 分解の木（MECE） / Logic tree | MECE breakdown | `tree`, `direction: right` (native) |
| [`cause-effect`](img/cause-effect.png) | 原因と結果 / Cause and effect | cause-effect | `tree`, `direction: left` (native) |
| [`convergence`](img/convergence.png) | 収束 / Convergence | many to one | `diagram`, `edge_route: elbow` (composed) |
| [`divergence`](img/divergence.png) | 発散 / Divergence | one to many | `diagram`, `edge_route: elbow` (composed) |
| [`hub-spoke`](img/hub-spoke.png) | 中心と周辺 / Hub and spoke | hub-and-spoke | `hub` (native) |
| [`layers`](img/layers.png) | 層構造 / Layers | layers | `bands` (native) |
| [`part-whole`](img/part-whole.png) | 全体と内訳 / Part to whole | part-whole | `stacked_bar` or a chart (native) |
| [`matrix-2x2`](img/matrix-2x2.png) | 2×2 の位置づけ / 2×2 matrix | two axes | `type: matrix` (composed) |
| [`venn`](img/venn.png) | 重なり / Venn | overlap | `venn` (native) |
| [`funnel`](img/funnel.png) | 絞り込み / Funnel | funnel | `funnel` (native) |
| [`pyramid`](img/pyramid.png) | ピラミッド / Pyramid | pyramid | `pyramid` (native) |
| [`swimlane`](img/swimlane.png) | 誰が何をするか / Swimlane | who does what | `swimlane` (native) |
| [`timeline`](img/timeline.png) | 時系列 / Timeline | timeline | `timeline` (native) |
| [`roadmap`](img/roadmap.png) | ロードマップ / Roadmap | workstreams over time | `bands` with `cols` and `span` (composed) |
| [`maturity-staircase`](img/maturity-staircase.png) | 段階的な成熟 / Maturity staircase | staged growth | `staircase` (native) |
| [`value-chain`](img/value-chain.png) | 価値の連鎖 / Value chain | value chain | `diagram`, primary row + support rows (composed) |
| [`kpi-tiles`](img/kpi-tiles.png) | 主要な数字 / Key numbers | key figures | `tiles` (native) |
| [`system-context`](img/system-context.png) | 関係者と流れの全体像 / Context overview | relationships | `diagram` with `groups` (composed) |
| [`loop-on-layers`](img/loop-on-layers.png) | 土台の上で回るループ / Loop on foundations | cycle on layers | `stack` of `cycle` + `bands` (composed) |
| [`problem-solution`](img/problem-solution.png) | 課題・仕組み・ねらい / Problem → mechanism → aim | mapping | `matrix`, `flow: true` (native) |
| [`parallel-set`](img/parallel-set.png) | 並列の要素 / Parallel set | list of equals | `type: cards` (composed) |

## What every pattern shares (what makes it look good)

- **One alignment.** Boxes of one kind share a size and an edge; text in them is aligned one way.
- **One accent.** Color marks the point of the slide or a category explained by a legend — never
  variety. Three recurring fills with no legend make the reader guess.
- **Shape means kind.** Ellipses for actions or steps of a loop, boxes for actors and things; the
  same shape never means two things on one slide.
- **Labels inside or on the line.** A box carries a short noun; the sentence goes in `text`, beside
  it (pyramid, funnel) or in the caption. Edge labels sit on their arrow.
- **Whitespace, not lines.** Groups are a light panel, layers a label cell; no borders around
  everything, no shadows, no 3-D.

## Changing the catalog

Edit `patterns.yaml`, then regenerate the sample deck and the images:

```bash
python3 assets/find_pattern.py --gallery assets/samples/figure-patterns.yaml
python3 tests/gallery_images.py          # needs LibreOffice; rewrites img/
bash tests/run_tests.sh                  # patterns_check.py fails if the two drift apart
```

## Where the ideas come from

The descriptions are this skill's own; the ideas are widely taught. By title, without quotation:
Barbara Minto, *The Pyramid Principle* (MECE, logic and issue trees); Gene Zelazny, *Say It with
Charts*; Andrew Abela, *Chart Suggestions — A Thought-Starter* and *Advanced Presentations by
Design*; the Financial Times *Visual Vocabulary*; Microsoft Office's SmartArt categories (list,
process, cycle, hierarchy, relationship, matrix, pyramid); Edward Tufte, *The Visual Display of
Quantitative Information* and *Envisioning Information*; Robin Williams, *The Non-Designer's Design
Book* (contrast, repetition, alignment, proximity); Colin Ware, *Information Visualization —
Perception for Design*; Cole Nussbaumer Knaflic, *Storytelling with Data*; Nancy Duarte,
*slide:ology*; OMG, *BPMN 2.0* (pools and lanes); Michael E. Porter, *Competitive Advantage* (the
value chain); Kaoru Ishikawa, *Guide to Quality Control* (cause-and-effect diagram); the
Shewhart/Deming PDCA cycle; Russell Ackoff, *From Data to Wisdom*; the BCG growth-share matrix; John
Venn's set diagrams. Each catalog entry names the ones it draws on in `sources`.
