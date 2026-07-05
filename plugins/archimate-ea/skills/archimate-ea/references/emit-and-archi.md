# Emitters, PlantUML rendering, and Archi import

Both emitters call the validator first and **refuse to emit on ERROR-level
problems** (override with `--force`). Generate-forward: never hand-edit emitted
files — edit the YAML and re-emit.

## PlantUML (`emit_plantuml.py`)

One `.puml` per view under `<out>/views/`, each `@startuml` + `!include
<archimate/Archimate>`. Element types map to stdlib macros via
`archimate_metamodel.json → macros`:

| ArchiMate type | macro | ArchiMate type | macro |
|----------------|-------|----------------|-------|
| Goal | `Motivation_Goal` | ApplicationComponent | `Application_Component` |
| Requirement | `Motivation_Requirement` | ApplicationService | `Application_Service` |
| BusinessProcess | `Business_Process` | DataObject | `Application_DataObject` |
| BusinessService | `Business_Service` | Node | `Technology_Node` |
| Capability | `Strategy_Capability` | Artifact | `Technology_Artifact` |

Relationships map to `Rel_Composition / Rel_Aggregation / Rel_Assignment /
Rel_Realization / Rel_Serving / Rel_Access / Rel_Influence / Rel_Association /
Rel_Triggering / Rel_Flow / Rel_Specialization`. Modifiers render as labels:
Access → `R/W/RW`, Influence → its strength string. A `Junction` element emits
`Junction(alias)` and edges route through it. Unknown macros fall back to a plain
`rectangle`. `--lang` picks the label language (`auto` = first provided per element).

**If PlantUML errors on a macro name:** stdlib macro spellings vary slightly by
version (e.g. SystemSoftware, Physical_* elements). Update the `macros` map in the
JSON to match your installed `archimate/Archimate` stdlib.

### Rendering to PNG/SVG

`assets/render_plantuml.sh [-f png|svg] <out>/views/*.puml`. Needs the `plantuml`
CLI (or `PLANTUML_JAR=…`) **and** Graphviz `dot` **and** the ArchiMate stdlib. The
script degrades gracefully (clear message, exit 0) when tooling is absent —
emit+validate is the testable core; rendering is best-effort.

## Open Group Exchange XML (`emit_archimate_xml.py`)

Targets namespace `http://www.opengroup.org/xsd/archimate/3.0/`. Children are
written in the schema-mandated order: `name → documentation → elements →
relationships → organizations → propertyDefinitions → views`. Geometry
(`--layout`, default `layered`): the schema requires `x/y/w/h`, so the emitter
computes positions from the model's **logical structure** — each ArchiMate layer
becomes a horizontal band (motivation at top, descending to technology /
implementation) and nodes within a band are ordered by a barycenter sweep to line
related elements up and reduce crossings. The view therefore reads top-down on
import, without hand-layout. `--layout grid` is the old row-major placeholder and
`none` emits zeros — use either only when you intend to run Archi's own auto-layout.

### Gotchas this emitter handles (and you should know)

- **Two reference spaces.** A relationship's `source`/`target` are **element ids**;
  a view `<connection>`'s `source`/`target` are **node ids**. Mixing them is the
  classic Archi import failure. Each `<node>` has its own id *and* an `elementRef`;
  each `<connection>` has its own id *and* a `relationshipRef`.
- **Junctions** are encoded as elements with `xsi:type="AndJunction"` /
  `"OrJunction"` (from `junctionType`), not as a relationship attribute.
- **Multilingual** labels are repeated `<name xml:lang="…">`, never comma-joined.
- **accessType** is capitalized in XML (`Write`), lowercase in YAML (`write`).
- **View-object xsi:type** differs from element type: `<node>`→`Element`,
  `<connection>`→`Relationship`, `<view>`→`Diagram`.
- **Influence strength** is a notation modifier, not a schema attribute — kept in
  YAML and rendered in PlantUML, but omitted from XML to stay XSD-valid.
- **id sanitization** — ids must be valid XML identifiers; offending ids are
  sanitized on emit (the validator warns first).

### Optional XSD validation

`--xsd /path/to/archimate3_Diagram.xsd` validates the output against the official
schema. The XSD is **not vendored** (licensing) — download it from The Open Group
and pass the path. Without it, the emitter still produces well-formed XML.

### Importing into Archi

1. `File → Import → Open Exchange File`.
2. Select the emitted `model.xml`.
3. Elements, relationships, properties, junctions, organizations, and views appear.
4. Views open with the `layered` structure-aware layout — layers stacked top-down.
   If you want a different arrangement, `Edit → Auto-layout` (or right-click →
   Format) re-flows the view with Archi's own algorithm.
