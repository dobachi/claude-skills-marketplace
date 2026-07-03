---
name: archimate-to-impl
description: Bridge an ArchiMate EA model's Application layer to implementation — derive a requirement→component→service→api→task traceability matrix, OpenAPI skeletons per ApplicationService, DataObject entity stubs, and a per-component task list, then check for orphans. Use to turn EA design into build work / トレーサビリティ / 設計から実装への橋渡し.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# ArchiMate → Implementation Bridge

You turn a designed EA model into build-ready work **without losing the thread back
to the requirements**. The `ea-model.yaml` produced by `archimate-ea` stays the
single source of truth; this skill reads its Application layer and generates-forward
a traceability matrix, API/entity skeletons, and an implementation task list — then
flags where the chain `requirement → component → service → api → task` is broken.

It hands structured input to the prose implementation skills (`web-api-dev`,
`python-expert`, `cli-tool-dev`, `tauri-dev`) and to task trackers (`github-issues`,
`project-manager`). It sits downstream of `tech-selector` (which fills the Technology
layer) and `archimate-ea` (which authored the model).

## Core principles

1. **The EA model is read-only upstream.** This skill never edits `ea-model.yaml`.
   Derived files are disposable — regenerate them, don't hand-edit; fix the model in
   `archimate-ea` and re-derive.
2. **Every artifact carries its trace.** Each API skeleton, entity stub, and task
   names the model element (`id`) it came from, so build work always points back to
   the requirement it serves.
3. **Orphans are the product.** The most valuable output is the gap list: a
   requirement no service implements, a component that serves nothing required. Do
   not paper over them — surface them as the next question for `archimate-ea`.
4. **Skeletons, not implementations.** Emit the contract shape (paths, methods,
   schemas) grounded in the model's Access/Realization edges; the dev skills flesh
   out the bodies.

## Traversal rules (how the trace is built)

| From | Relationship | To | Meaning |
|------|-------------|----|---------|
| ApplicationService | Realization | Requirement/Constraint | service satisfies requirement |
| ApplicationFunction | Realization | ApplicationService | function realizes service |
| ApplicationComponent | Assignment | ApplicationFunction | component runs function |
| ApplicationComponent | Assignment | ApplicationInterface | component exposes interface |
| ApplicationFunction | Access (accessType) | DataObject | function reads/writes data |
| ApplicationComponent | Association (directed) | ApplicationService | component uses/depends on service |

Full schema of the emitted `traceability.yaml`: `references/traceability-schema.md`.

## The bridge loop

1. **DERIVE** — run `derive.py`; it writes the traceability graph, one OpenAPI 3.0
   skeleton per ApplicationService (CRUD paths derived from each accessed DataObject's
   `accessType`), an entity stub per DataObject, and a per-component task list.
2. **CHECK** — run `trace_check.py`; present the orphans as decisions: is the
   uncovered requirement out of scope, or is a Realization edge missing? Feed real
   gaps back to `archimate-ea`; re-derive after the model changes.
3. **HAND OFF** — for each component task, invoke the recommended skill
   (`web-api-dev` when it exposes a service/interface, else `python-expert`) with the
   skeleton as its input. Track tasks via `github-issues` / `project-manager`.
4. **RE-DERIVE on model change.** The artifacts are downstream; whenever the model
   moves, regenerate rather than edit.

**Done when** every Requirement traces to at least one implementation task, every
ApplicationService has an API skeleton, and `trace_check.py` reports no orphans
(or each remaining orphan has a recorded "out of scope" decision).

## Running the scripts

```bash
cd plugins/archimate-to-impl/skills/archimate-to-impl
pip install -r scripts/requirements.txt          # PyYAML

# derive traceability + skeletons + tasks into out/
python3 scripts/derive.py ea-model.yaml -o out/
#   -> out/traceability.yaml  out/traceability.md  out/tasks.md
#      out/openapi/<service>.yaml   out/entities/<dataobject>.yaml

# check for traceability orphans (styled after archimate-ea's validator)
python3 scripts/trace_check.py ea-model.yaml            # text; exit 1 if warnings
python3 scripts/trace_check.py ea-model.yaml --format json
python3 scripts/trace_check.py ea-model.yaml --strict   # exit 2 on any warning (for CI/gates)
```

`trace_check.py` reports coverage gaps as WARN (the model is still valid ArchiMate —
these are not metamodel errors). Codes: `unimplemented-requirement`,
`service-no-requirement`, `service-no-impl`, `component-no-requirement`,
`service-no-interface`.

## Boundaries

- **Not** modelling — requirements/design live in `archimate-ea`.
- **Not** technology choice — that is `tech-selector` (Technology layer).
- **Not** the implementation itself — skeletons hand off to the dev skills.
- Reads `ea-model.yaml`; writes only to the output dir.
