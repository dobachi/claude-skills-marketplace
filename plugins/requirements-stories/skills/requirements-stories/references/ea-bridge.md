# The EA bridge — linking a backlog to an ArchiMate model

This skill sits between `archimate-ea` (which authors EA-level requirements) and
`archimate-to-impl` (which turns the Application layer into build work). It fills the
missing **agile product-discovery layer**: decomposing coarse EA Requirements into
epics and user stories with acceptance criteria, prioritized and mapped.

```
archimate-ea ──► ea-model.yaml ──► requirements-stories ──► archimate-to-impl ──► build
 (Motivation:      (read-only         (backlog.yaml:            (Application layer
  Goal/Requirement  upstream)          epics/stories/AC/NFR      → components/services
  /Constraint/                          + traces_to ea ids)       /api/tasks)
  Stakeholder)
```

## Design decision: a separate file, not a new ArchiMate element

ArchiMate 3.2 has **no element type for a user story**. Forcing fine-grained stories
into the Motivation layer as extra `Requirement` elements would bloat the EA model and
break `archimate-ea`'s metamodel validator. So stories live in their own
`backlog.yaml`, which **references** the EA model by id via `traces_to`. Consequences:

- The EA model stays clean and metamodel-valid; `archimate-ea`/`archimate-native`
  keep working unchanged.
- The backlog **also works standalone** — omit `backlog.ea_model` and `traces_to`, and
  the skill is a pure agile requirements/story facilitator.
- The EA model is **read-only upstream**, exactly as in `archimate-to-impl`. This skill
  never edits `ea-model.yaml`; when a story reveals a genuinely new requirement, that
  is a change to push *up* into `archimate-ea`, not a silent edit here.

## What seeds what

When an EA model is linked, read its Motivation layer and use it to seed the backlog
(you propose, the user corrects):

| EA element (ea-model.yaml) | Seeds | backlog.yaml field |
|---|---|---|
| `Requirement`, `Constraint` | epics / NFRs | `epics[].traces_to`, `nfrs[].traces_to` |
| `Stakeholder`, `BusinessActor`, `BusinessRole` | personas ("As a …") | `personas[].traces_to` |
| `Goal`, `Outcome` | the benefit ("so that …"), impact-map goal | `backlog.goal`, `stories[].so_that` |
| `Driver`, `Assessment` | the "why"/problem context | story rationale, `notes` |

A `Constraint` usually becomes an NFR (often EARS `unwanted`/`ubiquitous`); a
`Requirement` usually becomes an epic that fans out into stories.

## `traces_to` — how the link is written

Any persona, epic, story, or NFR may carry `traces_to: [<ea-id>, …]` naming the EA
element ids it realizes. A story with no `traces_to` **inherits its epic's**. Keep the
grain coarse — trace an epic to its `Requirement` and let its stories inherit, adding a
story-level `traces_to` only when a story serves a *different* requirement.

## `trace_check.py` — bidirectional coverage (orphans are the product)

Run it whenever the backlog or the EA model changes. It reports **WARN**s (the EA model
is still valid — these are coverage gaps, decisions for you, not errors):

**Forward — is every EA requirement realized?**
- `uncovered-requirement` — a `Requirement`/`Constraint` no epic/story/NFR traces to.
  Coverage is strictly *direct*: the requirement needs a story of its own. Decide: out
  of scope (record it), or a missing story (add one)?
- `goal-not-addressed` — a `Goal`/`Outcome` that no traced requirement contributes to.
  Goals are checked *transitively*: a goal counts as addressed if a referenced
  requirement reaches it over ArchiMate contribution edges (Realization/Influence/
  Serving), e.g. `req → junction → goal`.

**Backward — does every story point back?**
- `untraced-story` — a story with no `traces_to` (directly or via its epic). Either
  scope creep to cut, or a real new requirement to push up into `archimate-ea`.
- `dangling-trace` — a `traces_to` id absent from the EA model (typo, or the element
  was renamed/removed upstream).
- `persona-trace-type` — a persona tracing to something that isn't a Stakeholder/
  BusinessActor/BusinessRole.

```
python scripts/trace_check.py backlog.yaml            # uses backlog.ea_model
python scripts/trace_check.py backlog.yaml --ea path/to/ea-model.yaml   # override
```

## Handing off downstream

- `archimate-to-impl` derives `requirement → component → service → api → task` from the
  *same* EA requirements your stories trace to. Reconcile the two task lists by their
  shared EA requirement id: a story with no matching implementation task (or vice
  versa) is a gap in one of the two views.
- Push stories to `github-issues` / `project-manager`; put the `traces_to` ids and the
  story id in the issue so the trace survives into the tracker (commit/branch/PR names).
- Emit Gherkin (`emit_gherkin.py`) so acceptance criteria live in the repo as the
  executable trace to behavior.

## Round-trip discipline

`backlog.yaml` is the source of truth for the *backlog*; `ea-model.yaml` is the source
of truth for the *architecture*. Fix each in its own file and re-run the checks. Never
hand-edit the emitted Markdown/Gherkin, and never edit the EA model from here — feed
changes back to `archimate-ea`.
