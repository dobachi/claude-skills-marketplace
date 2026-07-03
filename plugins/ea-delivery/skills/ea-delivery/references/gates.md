# Gate definitions

A gate is a checklist run **before** a handoff and recorded in `delivery-ledger.yaml`.
Advance only on a pass. On a fail, turn the gap into the next question for the owning
skill and re-run the gate after the model changes. The conductor runs these; it does
not re-implement the checks — it invokes the owning skill's scripts.

## `model-valid` — requirements → design

- Run `archimate-ea`'s `validate_model.py MODEL.yaml`; require **0 errors** (WARN is
  acceptable but review it).
- No `Goal` or `Requirement` traces to nothing (archimate-ea's own Definition of Done).

Pass → descend into the design layers. Fail → the model has metamodel errors or
dangling motivation; fix in `archimate-ea`.

## `placeholders-identified` — design → tech-selection

- `validate_model.py` clean.
- Enumerate Technology-layer elements (`SystemSoftware | Node | TechnologyService`)
  whose product is still a generic placeholder. This list is the input to
  `tech-selector`. If none exist, tech-selection is a no-op — skip to bridge.

## `no-unselected-tech` — tech-selection → bridge

- Every enumerated placeholder now carries a `selected-product` property (the
  `tech-selector` Definition of Done).
- Each decision links to an ADR (`decision-adr`), and each ADR traces to at least one
  Requirement/Constraint.
- `validate_model.py` clean after write-back (tech-selector's `writeback.py --validate`
  already enforces this; confirm it ran).

Fail → a placeholder is unfilled or a decision has no rationale; return to
`tech-selector`.

## `no-orphans` — bridge → implementation

- Run `archimate-to-impl`'s `trace_check.py MODEL.yaml`.
- **Pass = exit 0** (no orphans), **or** every reported orphan has a recorded
  "out of scope" decision (note it in the ledger gate record and, ideally, in the
  model documentation).
- Every `ApplicationService` has an emitted API skeleton (`derive.py` output present).

Fail → an `unimplemented-requirement` or `component-no-requirement` remains without a
decision. Either add the missing Realization/service in `archimate-ea`, or record the
scope decision — do not silently proceed.

## `tasks-tracked` — implementation → service

- Every component task from `archimate-to-impl`'s `tasks.md` has an owner/tracker item
  (e.g. a `github-issues` entry) and a recommended skill assigned.
- Code for completed tasks is committed/reported (`commit-and-report`).
- **No `back_edge` is `open`** — a pending re-selection blocks service readiness.

Fail → untracked work or an open back-edge; resolve before declaring the service phase.

## Back-edge trigger (any downstream phase)

Not a handoff gate but a rule the conductor enforces continuously: if a phase surfaces
a **new non-functional requirement**, open a back-edge to `tech-selection`
(`references/delivery-ledger.md`), add the requirement to the model via `archimate-ea`,
and re-run the affected gates. Close the back-edge when the re-selection lands.
