# Adapter: diagrams

Applies the essence test to diagrams — architecture/flow/sequence diagrams, slide
graphics, ER/UML, mind maps, and the "boxes and arrows" that fill decks and docs. Use with
the five-question test in `SKILL.md`.

## What "purpose" and "load-bearing" mean here

- **Purpose** = the **one structural relationship** the diagram must make the viewer grasp:
  a flow, a hierarchy, a dependency, a state transition, a mapping, a sequence.
- **Load-bearing** = the nodes and edges that *are* that relationship. If removing an
  element doesn't change what the viewer understands about the structure, it isn't
  load-bearing.

## The core test: does it encode structure?

Adapted from Tufte's data-ink ratio: **every mark should carry information about the
relationship.** A diagram element earns its place only if it changes what the viewer knows.
Apply the information test to each mark:

- Would two viewers reconstruct the *same* structure from the layout, or is the arrangement
  arbitrary? Arbitrary placement = decoration masquerading as a diagram.
- Does this box/arrow/color/icon distinguish something, or just fill space?

A picture that is really a bulleted list wearing shapes — decorated bullets, a SmartArt
"cycle" with no actual cycle, five parallel boxes that are just five list items — has **no
structural essence**. The honest distillation is often "this should be a list / a table /
one sentence", not a tidier diagram.

## Diagram-specific cruft

| Category | What it looks like |
|---|---|
| Decoration / chartjunk | Gradients, drop shadows, 3-D, clip-art icons, background images, ornamental frames — none encode structure. |
| Redundancy | The same entity drawn twice; a legend restating obvious labels; an arrow label that repeats the arrow's obvious meaning. |
| Gold-plating | Detail beyond the diagram's level: every field of every table in an architecture overview; every retry path in a happy-path flow. |
| Wrong-altitude detail | Implementation nodes in a context diagram; system boxes in a class diagram. |
| Scope creep | A second relationship crammed into one diagram (a flow *and* a deployment topology) — split it. |
| Noise nodes | "Start"/"End" bubbles, decorative hubs, and pass-through boxes that add no branch. |

## Keep, even when it looks like clutter

- A label that disambiguates an otherwise ambiguous edge (direction, cardinality, condition).
- The one legend entry a non-expert audience needs to read the notation.
- A grouping boundary (swimlane, subgraph) that *is* part of the structure being shown.

## Distillation moves

- **Strip** non-structural styling to a neutral, consistent notation (one shape vocabulary).
- **Split** a diagram carrying two relationships into two single-purpose diagrams.
- **Drop a level** — replace nested internal detail with a single node plus a link to a
  detail diagram (demote, don't delete).
- **Demote to text** — if the "diagram" encodes no structure, recommend a list/table/sentence.
- **Merge** duplicate nodes into one.

## Handoffs

- Redrawing the distilled diagram (Mermaid-first) → `document-figures`.
- The diagram lives on a slide and the deck needs structural rework → `pptx-design` /
  `marp-slides`.
- Chesterton's Fence: an edge whose meaning you can't determine → **flag**, don't drop; a
  seemingly stray arrow may encode a real dependency.
