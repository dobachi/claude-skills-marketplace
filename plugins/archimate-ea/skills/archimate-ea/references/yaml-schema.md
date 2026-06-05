# Running-model YAML schema

`ea-model.yaml` is the single source of truth. The validator and both emitters
read exactly the fields below. Anything visual (coordinates, colours) is **not**
stored here — it is generated at emit time. See `emit-and-archi.md`.

A complete, valid example lives in `assets/ea-model.example.yaml`.

## Conventions

- **Multilingual text** — `name` and `documentation` are maps keyed by BCP-47
  language code: `name: { ja: 注文, en: Order }`. A plain string is also accepted
  (`name: Order`). All languages are emitted to XML as repeated `<name xml:lang>`.
- **Stable ids** — every `id` is permanent. Never renumber or reuse an id; it is
  the anchor that maps 1:1 to the XML `identifier` and (future) round-trip. Use
  kebab-case starting with a letter (`goal-revenue`, `appcomp-order`).

## Top-level keys

| key | required | purpose |
|-----|----------|---------|
| `model` | yes | header: `id`, `name`, `documentation`, `version` |
| `propertyDefinitions` | when properties used | declares custom property keys + types |
| `elements` | yes | the ArchiMate elements |
| `relationships` | yes | relationships between elements |
| `organizations` | no | logical folder tree (pure containment, no semantics) |
| `views` | no | named diagrams as **logical membership** (no geometry) |

## `model`

```yaml
model:
  id: model-digital-sales          # -> XML model identifier (required)
  name: { ja: …, en: … }
  documentation: { en: … }
  version: "0.3.0"                  # free text, your own model version
```

## `propertyDefinitions`

Declare a key once, reference it from any element's `properties`. Mirrors the XML
rule that properties reference a typed definition.

```yaml
propertyDefinitions:
  - { key: owner,      type: string, name: { en: Owner } }
  - { key: reviewDate, type: date,   name: { en: Review date } }
```

`type` ∈ `string | number | boolean | date | time` (Exchange-format property types).

## `elements`

```yaml
elements:
  - id: goal-revenue
    type: Goal                     # must be an ArchiMate 3.2 type (metamodel-and-relationships.md)
    name: { ja: …, en: … }
    documentation: { en: … }       # optional
    properties:                    # optional; keys must be in propertyDefinitions
      owner: CFO
      criticality: high
  - { id: junc-reqs, type: Junction, junctionType: and }   # Junction: junctionType ∈ and|or
```

## `relationships`

```yaml
relationships:
  - { id: r1, type: Realization, source: req-portal, target: goal-revenue }
  - { id: r2, type: Access,      source: appfunc-process, target: dataobj-order, accessType: readWrite }
  - { id: r3, type: Association, source: appcomp-portal, target: appsvc-order, isDirected: true }
  - { id: r4, type: Influence,   source: principle-x, target: req-portal, strength: "++" }
```

`source`/`target` are **element ids** (a Junction is an element, so it is a legal
endpoint). Modifiers:

| modifier | applies to | values |
|----------|-----------|--------|
| `accessType` | Access | `none \| read \| write \| readWrite` |
| `isDirected` | Association | boolean |
| `strength` | Influence | free text (`+`, `-`, `++`, …) — rendered in PlantUML; not an XML attribute |

## `organizations`

Logical folders for navigation in Archi. Items are element/relationship ids.
Nest with `children`.

```yaml
organizations:
  - label: { en: Application }
    items: [appcomp-portal, appcomp-order]
    children:
      - { label: { en: Services }, items: [appsvc-order] }
```

## `views`

A view is **which elements/relationships appear together** — logical membership
only. No coordinates. The viewpoint is a label (see `viewpoints.md`).

```yaml
views:
  - id: view-motivation
    name: { en: Motivation view }
    viewpoint: Motivation
    elements: [goal-revenue, req-portal, junc-reqs]
    relationships: [r-portal-junc, r-junc-goal]
```

A relationship listed in a view whose endpoints are not both in `elements`
produces a `view-dangling-edge` warning (and is skipped by the emitters).

## Future round-trip seam

v1 is generate-forward: emitters never write geometry, and nothing reads it back.
When round-trip lands, re-ingested layout will live in an **optional** per-view
`geometry` block (ignored by v1):

```yaml
  views:
    - id: view-motivation
      # geometry:                  # FUTURE — populated only by a re-ingester
      #   nodes: { goal-revenue: { x: 12, y: 24, w: 120, h: 55 } }
      #   bendpoints: { r-junc-goal: [ { x: 80, y: 40 } ] }
```

The stable ids above are what make that match-back possible — keep them stable.
