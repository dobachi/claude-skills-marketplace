# `delivery-ledger.yaml` schema

The conductor's own state file, kept alongside `ea-model.yaml`. It records where the
delivery is, what each phase produced, which gates passed, and which back-edges are
open. It is **not** the architecture — `ea-model.yaml` is. The ledger only tracks
process state; never put model content here.

A complete example: `assets/delivery-ledger.example.yaml`.

## Top-level keys

```yaml
delivery:            # header: what is being delivered and where it stands
phases:              # per-phase status, owning skill, and produced artifacts
gates:               # gate results, one per handoff attempted
back_edges:          # open/closed loops back to an earlier phase
```

## `delivery`

```yaml
delivery:
  model: ea-model.yaml       # the through-line source of truth
  phase: bridge              # current phase (the state-machine cursor)
  entry_phase: requirements  # where this run started (adaptive entry)
  updated: "2026-07-03"      # ISO date of last ledger change
```

`phase` ∈ `requirements | design | tech-selection | bridge | implementation | service`.

## `phases`

One entry per phase. `status` ∈ `pending | in-progress | done`.

```yaml
phases:
  requirements:   { status: done, skill: archimate-ea, artifacts: [ea-model.yaml] }
  design:         { status: done, skill: archimate-ea }
  tech-selection: { status: done, skill: tech-selector,
                    artifacts: [docs/adr/0003-relational-datastore.md] }
  bridge:         { status: in-progress, skill: archimate-to-impl,
                    artifacts: [out/traceability.yaml, out/openapi/] }
  implementation: { status: pending, skill: web-api-dev }
  service:        { status: pending, skill: project-manager }
```

## `gates`

Append one record each time a handoff gate is run. `status` ∈ `passed | failed`.

```yaml
gates:
  - { at: "tech-selection→bridge", check: no-unselected-tech, status: passed, on: "2026-07-03" }
  - { at: "bridge→implementation", check: no-orphans, status: failed, on: "2026-07-03",
      note: "req-mobile unimplemented — decide scope or add a service" }
```

Gate `check` names match `references/gates.md`: `model-valid`, `placeholders-identified`,
`no-unselected-tech`, `no-orphans`, `tasks-tracked`.

## `back_edges`

A downstream phase that discovers something belonging upstream opens a back-edge, routed
by kind: a new **non-functional** requirement → `tech-selection`; a new **functional**
requirement or design gap (including an orphan marked `promoted` in a `gaps.yaml`) →
`design`. `to` ∈ `design | tech-selection`, `status` ∈ `open | closed`. **An open
back-edge of any kind blocks the `service` gate.**

```yaml
back_edges:
  - from: bridge
    to: tech-selection
    reason: "event-driven order service needs a message broker (new NFR)"
    opened: "2026-07-03"
    status: open
    # closed: "2026-07-04"   # set when the re-selection lands
  - from: implementation
    to: design
    reason: "promoted orphan: retention outcome needs a requirement in the model"
    opened: "2026-07-05"
    status: open
```

## Rules

- **Advance only through a passed gate.** No gate record → the phase has not advanced.
- **The ledger tracks process, the model holds content.** New requirements go into
  `ea-model.yaml` via `archimate-ea`, not into the ledger.
- **Close what you open.** A run is not `done` while any back-edge is `open`.
