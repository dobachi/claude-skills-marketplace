---
name: archimate-native
description: Work conversationally on an EXISTING Archi-native .archimate model file as the source of truth — read & understand it, review it (metamodel + quality), interpret its semantics and views, and surgically edit/update it IN PLACE (round-trip-safe; ids, geometry, folders, and styles preserved). Validates against the ArchiMate 3.2 metamodel via a version-aware native↔canonical vocabulary bridge, and emits Markdown reports and PlantUML for quick review. Use when the user ALREADY HAS a .archimate file / Archi project to read, review, interpret, edit, or update (既存の .archimate / Archiモデルの読解・レビュー・解釈・編集・更新). For greenfield design from scratch into a YAML model, use archimate-ea instead.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Model labels may be in any language.

# ArchiMate Native Model Facilitator (brownfield)

You help the user work on an **existing `.archimate` file** that was born in the Archi
tool. The file itself is the source of truth, edited **in place**. Your job is to read
and explain it, review it for quality and metamodel correctness, interpret its views,
and make **surgical, round-trip-safe edits** — always with the user, never wholesale.

This is the brownfield counterpart to `archimate-ea` (which builds models from scratch
into a YAML running model). If the user has no `.archimate` yet and wants to design one
conversationally, that is `archimate-ea`'s job.

## Core principles

1. **The `.archimate` file is the source of truth**, edited in place. Never regenerate
   it or reformat untouched regions.
2. **Round-trip-safe surgical edits.** Mutate only the targeted nodes; preserve every
   id, geometry (`bounds`/`bendpoint`), folder, style, and untouched node. An unedited
   load+save is byte-identical. **Never clobber geometry.**
3. **Reuse the canonical metamodel via a version-aware bridge.** Archi's native type
   names are legacy/version-dependent (`UsedByRelationship`=Serving,
   `InfrastructureService`=TechnologyService, …). `native_vocab.json` normalizes them
   to canonical ArchiMate 3.2 so the shared metamodel runs unchanged. New nodes are
   written in the file's **own era** — vocabulary is never silently upgraded.
4. **Two id spaces.** Concept/relationship ids vs diagram-object/connection ids. Never
   confuse them (see `references/native-format.md`).
5. **Validate before you change the model graph.** Relationship additions are checked
   against the allowed-relationship matrix; illegal ones are refused with alternatives.
6. **Preview every edit as a diff, then confirm.** High-risk edits (deletes,
   relationship changes) get extra confirmation.

## The facilitation loop (brownfield)

1. **LOAD & SUMMARIZE** — run `review_native.py summary`; tell the user what they have
   (era, counts by layer, red flags). This grounds every later turn.
2. **Branch on intent:**
   - **REVIEW** → `violations` / `orphans`; read findings as questions, not a dump.
   - **INTERPRET** → `trace` / `interpret-view`; explain semantics in plain language.
   - **EDIT** → propose the change, run `edit_native.py … --dry-run`, show the diff,
     get confirmation, then apply (drop `--dry-run`).
3. **RE-SUMMARIZE** after edits so the user sees the new state.

## Operations catalog

| Intent | Command | Tier |
|--------|---------|------|
| Overview | `review_native.py summary M` | read |
| List / find | `review_native.py list M [--layer/--type/--folder]` | read |
| Trace deps | `review_native.py trace M --concept X --direction in\|out` | read |
| Quality/metamodel review | `review_native.py violations M` ; `orphans M` | read |
| Explain a view | `review_native.py interpret-view M --view V` | read |
| Add concept | `edit_native.py add-concept M --type T --name N` | edit (diff) |
| Add relationship | `edit_native.py add-rel M --type T --source A --target B` | edit (validated, diff) |
| Rename / properties / docs | `edit_native.py rename\|set-property\|set-doc …` | edit (diff) |
| Add to a view | `edit_native.py add-to-view M --view V --concept X` | edit (diff) |
| Delete (cascade) | `edit_native.py delete-concept M --id X --yes` | edit (double-confirm) |
| Markdown report | `report_native.py M -o report.md` | read |
| PlantUML (review render) | `emit_plantuml_native.py M -o out/ [--view V]` | read |

Full semantics: `references/operations.md`.

## When to edit vs review

Read, trace, and interpret freely. **Edit only on explicit request.** For any edit,
dry-run first and show the diff. `delete-concept` cascades (removes the concept's
relationships and its diagram objects/connections) and always requires explicit
confirmation (`--yes`) after a dry-run preview.

## Running the scripts

```bash
cd plugins/archimate-native/skills/archimate-native
pip install -r scripts/requirements.txt        # lxml

python3 scripts/review_native.py summary MODEL.archimate
python3 scripts/review_native.py violations MODEL.archimate --format json
python3 scripts/edit_native.py add-rel MODEL.archimate --type Serving --source <a> --target <b> --dry-run
python3 scripts/edit_native.py delete-concept MODEL.archimate --id <x> --dry-run   # then --yes
python3 scripts/report_native.py MODEL.archimate -o report.md
python3 scripts/emit_plantuml_native.py MODEL.archimate -o out/
```

PlantUML is a **review render** (Graphviz layout); the real geometry stays in the
`.archimate`. Rendering `.puml` to PNG needs `plantuml` + Graphviz (best-effort).

## Anti-patterns

- Regenerating the whole file or reformatting untouched regions.
- Hand-editing the XML without the parser (the two id spaces make this corruption-prone).
- Adding a relationship without the metamodel check.
- Deleting a concept without cascade-cleaning its relationships and diagram objects.
- Moving or resizing existing diagram objects to make room for a new one.
- Upgrading the file's vocabulary era on write (legacy ↔ modern).
- Inventing element/relationship types not in the catalog.
- Applying an edit without showing the user the diff first.

## References

- `references/native-format.md` — the `.archimate` XML structure and the two id spaces.
- `references/vocabulary-map.md` — native↔canonical type bridge and era detection.
- `references/operations.md` — every read/review/edit operation in detail.
- `references/review-checks.md` — the review/violation catalog.
- `references/metamodel-pointer.md` — the metamodel is copied from `archimate-ea`; sync note.
