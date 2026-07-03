# `traceability.yaml` schema

`derive.py` writes this file (plus `traceability.md`, per-service OpenAPI skeletons,
per-DataObject entity stubs, and `tasks.md`) into the output dir. It is a **derived,
disposable** view of `ea-model.yaml` — regenerate it, never hand-edit. Ids are the
model's stable ids, so every row points back to the architecture.

## Top-level keys

```yaml
requirements: [ ... ]   # every Requirement/Constraint + whether an app service covers it
services:     [ ... ]   # every ApplicationService + its implementation + API skeleton
components:   [ ... ]   # every ApplicationComponent + its trace + a task
dataobjects:  [ ... ]   # every DataObject + entity name + who accesses it
```

## `requirements[]`

```yaml
- id: req-portal
  type: Requirement            # or Constraint
  name: Self-service portal
  realized_by_services: [appsvc-order]   # ApplicationService ids realizing it
  covered: true                # false => orphan requirement (trace_check WARN)
```

## `services[]`

```yaml
- id: appsvc-order
  name: Order API
  realizes_requirements: [req-portal]        # up-trace to Motivation
  implemented_by_functions: [appfunc-process]
  components: [appcomp-order]                 # via function Assignment
  used_by_components: [appcomp-portal]        # directed Association (dependency)
  interfaces: [appiface-rest]                 # protocol boundary
  data:                                       # from function Access edges
    - { id: dataobj-order, access: readWrite }
  api_skeleton: openapi/appsvc-order.yaml
```

## `components[]`

```yaml
- id: appcomp-order
  name: Order Service
  functions: [appfunc-process]
  interfaces: [appiface-rest]
  services: [appsvc-order]
  traces_to_requirements: [req-portal]        # empty => orphan component (WARN)
  data:
    - { id: dataobj-order, access: readWrite }
  task:
    id: TASK-appcomp-order
    title: Implement Order Service
    recommended_skill: web-api-dev            # web-api-dev if it exposes a service/interface,
                                              # else python-expert
```

## `dataobjects[]`

```yaml
- id: dataobj-order
  name: Order data
  entity: OrderData                           # CamelCase identifier for code/schema
  accessed_by:
    - { function: appfunc-process, access: readWrite }
```

## Derived files

- **`openapi/<service>.yaml`** — OpenAPI 3.0.3 skeleton. One resource per accessed
  DataObject; HTTP methods follow `accessType`: `read` → GET (collection + item),
  `write` → POST/PUT, `readWrite` → full CRUD + DELETE. Schemas are stubs (only `id`);
  `web-api-dev` fills the fields and bodies.
- **`entities/<dataobject>.yaml`** — entity stub keyed to the DataObject id.
- **`tasks.md`** — one section per component with its recommended skill and traces.

## Orphan codes (trace_check.py)

| code | meaning |
|------|---------|
| `unimplemented-requirement` | a Requirement/Constraint no ApplicationService realizes |
| `service-no-requirement` | an ApplicationService realizing no requirement |
| `service-no-impl` | an ApplicationService no function/component implements |
| `component-no-requirement` | an ApplicationComponent tracing to no requirement |
| `service-no-interface` | an implemented service whose components expose no interface |
