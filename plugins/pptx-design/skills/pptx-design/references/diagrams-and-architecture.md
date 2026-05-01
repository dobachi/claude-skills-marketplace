# Diagrams and Architecture Reference

The single highest-leverage skill for `.pptx` design quality. AI-generated decks fail here more than anywhere else.

## The Information Test

Before drawing **any** boxes, arrows, or shapes on a slide, answer two questions out loud:

1. **What structural information does this visual encode?** Pick one or more:
   - **Relationship** between entities
   - **Flow direction** (data, temporal, control)
   - **Hierarchy** (parent → child, abstract → concrete)
   - **Containment** (X is part of Y)
   - **Parallelism** (A and B happen concurrently)
   - **Temporal order** (1 before 2 before 3)
   - **Grouping** (set membership, classification)
   - **Spatial / topological** (network adjacency, geographic)

2. **If I deleted the shapes and arrows and left only the text, what would I lose?**

If the answer to (2) is "nothing meaningful," the visual is **decoration**. It is not a diagram — it is bullets in costume. Choose one of the three fixes:

- **Delete the shapes.** Present as a list, sentence, or table.
- **Replace with a chart** if the underlying content is quantitative.
- **Actually encode the structure.** Redraw with meaningful arrows, hierarchy, grouping, or boundaries — see the type catalog below.

## When a Diagram Earns Its Place

- Relationships among **≥3 entities** with non-obvious structure.
- Multi-step **processes with branching** or parallelism.
- **System architectures** — components, boundaries, data flow.
- **Hierarchies with depth** — org charts, taxonomies, nested capabilities.
- **Matrices** — 2×2 segmentation (BCG, Eisenhower), positioning maps.
- **State transitions** — finite state machines, lifecycle stages.
- **Sequence / time-ordered** interactions — UML sequence, swimlanes.
- **Set relationships** — Venn diagrams (only when overlap actually has meaning).

If your content fits none of these, **a list or table is correct**. Don't manufacture a diagram.

## Diagram Type Catalog

| Type | Encodes | Use when | Don't use when |
|---|---|---|---|
| **Bullet list** | Set membership, ordering when the order matters | Items are parallel and self-contained | Items have non-trivial relationships |
| **Numbered list** | Strict sequence | Steps must execute in order | Steps are parallel or unordered |
| **Table** | Two-dimensional comparison | Multiple attributes per item | One attribute (just a list) |
| **Flow chart** | Process with decisions / branching | Branching matters; parallel paths | Linear sequence (use numbered list) |
| **Swimlane** | Process × responsibility | Multiple actors; handoffs matter | One actor (use flow chart) |
| **Sequence diagram** | Temporal interaction between actors | Order of messages matters | High-level architecture (use C4) |
| **State machine** | Discrete states + transitions | System has states with explicit transitions | Continuous progression |
| **ER diagram** | Entities + relationships + cardinality | Designing/documenting data model | Conceptual relationships (use concept map) |
| **Hierarchy / org / tree** | Parent–child structure | Strict hierarchy with depth | Network with cycles |
| **Network / graph** | Many-to-many connections | Connections themselves are the content | Hierarchy (use tree) |
| **Mindmap** | Brainstorm radiating from a center | Exploration / ideation | Final analytical content (rarely belongs in a finished deck) |
| **Matrix (2×2)** | Two-axis classification | Segmentation, positioning | Three or more dimensions |
| **Venn diagram** | Set overlap | Overlap region is meaningful and labeled | "Three circles" decoration |
| **Concept map** | Loose semantic relationships | Knowledge mapping | Strict process or hierarchy |
| **System / architecture** | Components, boundaries, data flow | Showing what talks to what | Logic flow within a single component |
| **Deployment** | Physical/cloud topology | Mapping software to infrastructure | Logical architecture (use C4 component) |
| **Gantt / roadmap** | Tasks × time | Project timeline | Conceptual sequence (use process) |
| **Big number + label** | One headline metric | Single takeaway per slide | More than one number to compare |

## Architecture Diagram Conventions

### Pick a level (C4 model)

[Simon Brown's C4 model](https://c4model.com) is the de facto convention:

| Level | Audience | Shows |
|---|---|---|
| **Context** | Anyone | The system + its users + external systems |
| **Container** | Architects, devs | Apps, services, databases inside the system |
| **Component** | Devs | Internal building blocks of one container |
| **Code** | Devs (rare in slides) | Class-level structure |

**Don't mix levels** in one diagram. Don't put "Kubernetes pod" and "user clicks button" on the same canvas.

### Arrow direction must mean one thing

Within a single diagram, every arrow must mean the same thing. Pick one:

- **Data flow** — arrow head shows where data goes
- **Dependency** — arrow points to what is depended on (e.g., A → B means A calls B)
- **Call direction** — arrow points to the callee
- **Time** — arrow points forward in time

State the convention in a **legend**. Mixing conventions in one diagram is a critical defect.

### Other rules

- **Every box has a definition.** A label alone is not enough — readers must know what each box is. Add a one-line subtitle inside the box, or label it with a familiar product/component name.
- **Group by boundary** that matters: deployment boundary, trust boundary, organizational ownership, network zone. Use containers (rounded rectangles + dashed border) to show the grouping.
- **Label edges** when protocol or payload matters (e.g., `HTTPS / JSON`, `gRPC`, `Kafka topic: orders`).
- **Source of truth**: keep diagram source files (draw.io, Excalidraw, Mermaid, PlantUML) versioned alongside the deck. The `.pptx` carries an exported PNG/SVG.
- **Legend** for any non-obvious shape, color, or line style. If you used dashed lines for async, say so.
- **Consistent abstraction** — every box at the same level of detail.

## SmartArt: When It Works vs. Theater

PowerPoint's SmartArt is the most common source of decorated bullets in AI-generated decks. The defaults make it almost too easy to dress up a bullet list as a "process" or "framework."

### Legitimate uses

- **Truly sequential horizontal process** with 3–6 steps where order is intrinsic — and you don't need branching. (SmartArt → Process → Basic Process.)
- **Strict hierarchy** with depth ≥2 levels and limited breadth. (SmartArt → Hierarchy → Organization Chart.)
- **Parallel concentric layers** when the layers actually represent containment (e.g., target market → addressable → obtainable). (SmartArt → Relationship → Target.)

### Theater (avoid)

- SmartArt used to fill empty space.
- "5-step process" SmartArt where the steps are not actually sequential — they're four ideas in colored arrows.
- "Hub and spokes" SmartArt where the spokes don't share a common relationship to the hub.
- Cycle SmartArt for items that don't repeat or cycle.
- Pyramid SmartArt where the levels don't represent a real hierarchy.
- Any SmartArt added because "the slide looked empty."

### Default rule

**Don't reach for SmartArt.** Build shapes manually. The act of drawing each box and arrow forces you to apply the information test.

## AI-Deck Anti-Patterns (named explicitly)

These are the failure modes you must reject by default. Each has a fix.

| Anti-pattern | Why it fails the information test | Fix |
|---|---|---|
| **Decorated bullets** — colored rectangles around list items | Shape carries no structural meaning; removing shapes loses nothing | Delete the shapes; present as a clean list. If you wanted hierarchy, redraw as a hierarchy. |
| **"5-step process" SmartArt** for non-sequential items | Implies an ordering that doesn't exist | If items are parallel, use a list or 2×2; if 3 of them are sequential, draw only those 3 |
| **Decorative arrows** — connectors with no meaning | Arrow direction encodes nothing | Remove arrows, OR pick one meaning (flow / dependency / time) and apply consistently |
| **Hexagons / pentagons / clouds as filler** | Shape choice is decorative | Use rectangles unless the shape carries semantic meaning (e.g., cloud = cloud service in a known notation) |
| **Center-and-spokes** with mismatched spokes | Implies the spokes share a relationship to the center, but they don't | Restructure as a list, table, or proper diagram |
| **3D / gradient-filled shapes** in architecture diagrams | Adds visual noise; no information | Flat 2D; use color or border for grouping |
| **Same template repeated** for unrelated content (e.g., "stack of three boxes" on every slide) | Repetition without semantic meaning | Match the visual to the content's actual structure |
| **Inconsistent box sizes for equally-important items** | Implies a hierarchy that doesn't exist | Equal size = equal weight; reserve size variation for actual emphasis |
| **Arrows that loop without reason** | Suggests a cycle that doesn't happen | Linear arrows for linear flow; loop only for true cycles |
| **Mixed abstraction levels** ("Database" next to "User journey") in one diagram | Audience can't reason about it | Split into two diagrams at consistent levels (C4) |
| **No legend on a custom notation** | Audience can't decode | Add a small legend, or use a standard notation (UML, C4, BPMN) |

## The Fix Recipe

When reviewing or generating a slide that contains shapes:

1. **Apply the information test.** Speak the structural meaning out loud.
2. If it fails, choose one:
   - **Delete the shapes.** Present as text.
   - **Replace with a chart** if data-driven.
   - **Encode actual structure.** Pick a diagram type from the catalog and redraw with meaningful arrows, hierarchy, or grouping.
3. **Add a legend** for any non-obvious convention.
4. **State the diagram type and what it encodes** in the slide's action title or speaker notes — this exposes anti-patterns immediately.

## Tools

- **PowerPoint shapes + Format → Align + Smart Guides** — fine for small diagrams, when you'll iterate inside the deck.
- **External diagramming**: draw.io / diagrams.net (free), Excalidraw (sketchy aesthetic, great for whiteboards), Lucidchart, Miro, Figma. Export SVG (preferred) or PNG.
- **Code-as-diagram**: Mermaid, PlantUML, Graphviz, Structurizr (C4-native). Source-controlled; regenerable.
- **Architecture-specific**: Structurizr (C4), Eraser, Ilograph.

Whichever tool you pick, **keep the source file**. Slides ship the rendered image; the team edits the source.

## Pre-Delivery Diagram Review

For each diagram in the deck:

- [ ] Information test passes — the visual encodes structure that text alone cannot.
- [ ] Diagram type matches the structural meaning.
- [ ] Arrows have one consistent meaning; convention is in the legend (or obvious).
- [ ] Every box has a definition or label that is meaningful to the audience.
- [ ] Abstraction level is uniform within the diagram.
- [ ] Notation is standard (UML, C4, BPMN) or has a legend.
- [ ] Color encodes meaning consistently with the rest of the deck.
- [ ] No SmartArt theater, decorated bullets, or filler shapes.
- [ ] Source file (draw.io/Mermaid/etc.) is saved and findable.
- [ ] Image is high-resolution; not pixelated when projected.
