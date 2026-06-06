# The Archi-native `.archimate` format

Grounded on real models (Archisurance, ArchiMetal, OpenDay). This is **Archi's own
native serialization**, not the Open Group Exchange format — different schema,
different vocabulary.

## Root & namespaces

```xml
<?xml version="1.0" encoding="UTF-8"?>
<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns:archimate="http://www.archimatetool.com/archimate"
                 name="…" id="…" version="3.1.1">
  <purpose>…</purpose>            <!-- optional -->
  <documentation>…</documentation> <!-- optional -->
  <folder …> … </folder>
</archimate:model>
```

Only the root is namespaced (`archimate:` prefix). `<folder>`, `<element>`,
`<bounds>`, `<child>` are **unqualified** (no namespace). Indentation is **2 spaces**.
The `version` attribute is the Archi file version and drives era detection
(`vocabulary-map.md`).

## Folders

`<folder name id type>` organize everything; types: `business`, `application`,
`technology`, `motivation`, `strategy`, `implementation_migration`, `relations`,
`connectors`, `diagrams`, `other`. Folders nest and contain `<element>`.

## Concepts and relationships — both are `<element>`

- **Concept**: `<element xsi:type="archimate:BusinessActor" id name>` with optional
  `<documentation>` child and `<property key value/>` children. (documentation
  precedes properties.)
- **Relationship**: `<element xsi:type="archimate:AssignmentRelationship" id source target [name]/>`.
  `source`/`target` are **concept ids**. The presence of `source`+`target` is the
  robust discriminator (works across vocabulary eras).

## Diagrams (views)

```xml
<element xsi:type="archimate:ArchimateDiagramModel" id name viewpoint="N">
  <child xsi:type="archimate:DiagramObject" id textAlignment fillColor
         targetConnections="connId…" archimateElement="<conceptId>">
    <bounds x y width height/>
    <sourceConnection xsi:type="archimate:Connection" id
                      source="<diagObjId>" target="<diagObjId>" relationship="<relId>">
      <bendpoint startX startY endX endY/>
    </sourceConnection>
    <child …/>                 <!-- nested containment -->
  </child>
  <child xsi:type="archimate:Group" …/>             <!-- visual-only -->
  <child xsi:type="archimate:Note" …/>              <!-- visual-only -->
  <child xsi:type="archimate:DiagramModelReference" model="<viewId>"/>
</element>
```

## Two id spaces (the classic corruption source)

- **Concept/relationship ids** — referenced by relationship `source`/`target` and by
  `DiagramObject.archimateElement` / `Connection.relationship`.
- **Diagram-object/connection ids** — referenced by `Connection.source`/`target` and
  `DiagramObject.targetConnections`.

A `Connection` joins **diagram-object** ids, and separately names the **relationship**
id it visualizes. Never resolve one id space with the other map. `native_model.py`
keeps them in separate indexes.

## Round-trip / minimal-diff policy

The skill parses with `remove_blank_text=False`, mutates only targeted nodes, and
writes with Archi's exact `<?xml … "UTF-8"?>` declaration (double quotes) + trailing
newline. An unedited load+save is **byte-identical**. Inserted nodes get explicit
2-space indentation; existing `<bounds>`/`<bendpoint>` are never touched. Every edit
is previewed as a unified diff (`--dry-run`) before writing.
