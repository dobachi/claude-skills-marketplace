# Review checks

What `review_native.py violations` and `orphans` look for. Errors are real
problems; warnings are advisory and drive dialogue. The metamodel checks reuse the
canonical ArchiMate 3.2 allowed-relationship matrix via the vocabulary bridge.

## Violations (`violations`)

| Code | Severity | Meaning |
|------|----------|---------|
| `unknown-type` | ERROR | a concept's native type has no canonical mapping (typo or unsupported type) |
| `unknown-relationship` | ERROR | a relationship's native type is unmapped |
| `dangling-source` / `dangling-target` | ERROR | a relationship points at an id that is not a concept |
| `illegal-relationship` | ERROR | the relationship type is not permitted between those element types (matrix); the message lists allowed alternatives |
| `dangling-diagram-object` | WARN | a view object references a concept that no longer exists (pre-existing corruption) |
| `dangling-connection` | WARN | a view connection references a relationship that no longer exists |

## Orphans (`orphans`)

- **No relationships** — a concept participating in nothing. Often an oversight; ask
  whether it should connect to something or be removed.
- **Unrealized goals/requirements** — a Goal/Requirement/Outcome that nothing
  `Realization`s or `Influence`s. Mirrors the design principle that a goal should
  trace to something concrete.

## How to use findings in conversation

Read findings to the user as questions, not a dump:
- illegal-relationship → "this says X *triggers* Y, but the metamodel only allows
  realize/serve there — which did you mean?"
- orphan → "Order Data connects to nothing — should the Order process access it?"
- unrealized goal → "nothing realizes 'Grow revenue' yet — which capability or
  requirement delivers it?"

Then, on agreement, make the fix with `edit_native.py` (dry-run → confirm → apply).

## What is NOT checked (yet)

Viewpoint conformance (whether a view's contents match its declared viewpoint),
naming conventions, and layer-crossing heuristics beyond the relationship matrix.
These are candidates for future checks.
