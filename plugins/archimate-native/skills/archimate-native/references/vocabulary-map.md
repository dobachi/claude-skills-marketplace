# Vocabulary map: Archi-native ↔ canonical ArchiMate 3.2

Archi's native `xsi:type` names are **version-dependent** and differ from the
canonical ArchiMate 3.2 names used by the shared metamodel
(`archimate_metamodel.json`). `native_vocab.json` bridges them; `native_model.py`
applies it.

## Two eras

| Era | Archi file `version` | Examples |
|-----|----------------------|----------|
| **legacy** | ≤ 4.0 (e.g. `3.1.1`) | `UsedByRelationship`, `RealisationRelationship`, `SpecialisationRelationship`, `InfrastructureService/Function/Interface`, `Network`; no Strategy layer |
| **modern** | ≥ 4.1 | `ServingRelationship`, `RealizationRelationship`, `TechnologyService/Function/Interface`, `CommunicationNetwork`; Strategy layer (Resource/Capability/CourseOfAction/ValueStream) |

**Detection:** the presence of any modern-only native type is decisive; otherwise the
root `version` regex decides. (`native_model.NativeModel.era`.)

## Key mappings

| Native (legacy) | Native (modern) | Canonical |
|-----------------|-----------------|-----------|
| `UsedByRelationship` | `ServingRelationship` | `Serving` |
| `RealisationRelationship` | `RealizationRelationship` | `Realization` |
| `SpecialisationRelationship` | `SpecializationRelationship` | `Specialization` |
| `InfrastructureService` | `TechnologyService` | `TechnologyService` |
| `InfrastructureFunction` | `TechnologyFunction` | `TechnologyFunction` |
| `Network` | `CommunicationNetwork` | `CommunicationNetwork` |
| `CompositionRelationship` | (same) | `Composition` |
| `BusinessActor`, `ApplicationComponent`, `Node`, … | (same) | identity |

Two rules cover the rest:
- **Relationships** carry a `Relationship` suffix in the file; canonical keys do not
  (`CompositionRelationship` → `Composition`).
- **Concepts** are mostly identity — any native type already in the metamodel element
  catalog maps to itself.

## Reading vs writing

- **Reading (`to_canonical`)**: a union map handles both eras, so a file of either
  vintage parses correctly. Both `native_type` (preserved) and `canonical_type`
  (used for metamodel checks and PlantUML macros) are stored per concept/relationship.
- **Writing (`to_native`)**: new nodes are spelled in the file's **own era**
  (`canonical_to_native_by_era[era]`), so adding a Serving relationship to a legacy
  file writes `UsedByRelationship`, never `ServingRelationship`. The vocabulary era is
  never silently upgraded.

## Why this lets us reuse the metamodel unchanged

Every native type is normalized to canonical before any metamodel call
(`relationship_allowed`, `layer_of`, `plantuml_macro`). So `archimate_metamodel.py`
needs **zero** Archi-awareness — the native-ness is fully absorbed by the bridge.
See `metamodel-pointer.md`.
