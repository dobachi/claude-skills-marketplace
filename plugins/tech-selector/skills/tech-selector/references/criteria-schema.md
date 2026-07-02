# `criteria.yaml` schema

One file per selection decision. `score.py` reads exactly the fields below. A
complete example: `assets/criteria.example.yaml`.

## Top-level keys

| key | required | purpose |
|-----|----------|---------|
| `decision` | recommended | which model element this fills + which requirements drive it |
| `criteria` | yes | the evaluation axes, with weights and direction |
| `candidates` | yes (≥2) | the options, each with a raw score per criterion |

## `decision`

```yaml
decision:
  id: db-selection            # kebab-case; used as the ADR/traceability key
  title: { ja: …, en: … }     # plain string also accepted
  target: syssw-db            # ea-model element id the decision fills (writeback --target)
  drivers: [req-mobile, constraint-gdpr]   # Requirement/Constraint ids justifying the choice
```

`target` must be a Technology-layer element (`SystemSoftware | Node |
TechnologyService`). `drivers` are the ids `writeback.py` and the ADR trace back to.

## `criteria`

```yaml
criteria:
  - key: throughput           # unique per file; referenced by candidate scores
    name: { en: Write throughput }   # or a plain string
    weight: 5                 # non-negative number; relative importance
    direction: max            # max = higher raw score better | min = lower better
    driver: req-mobile        # optional: the Requirement/Constraint this axis serves
```

- **Every axis should carry a `driver`.** An axis with no requirement behind it is
  decoration — challenge it before scoring.
- `weight` is a decision the user owns. `score.py` reports how sensitive the winner
  is to each weight.

## `candidates`

```yaml
candidates:
  - id: postgres              # unique; stable handle for the option
    name: PostgreSQL 16       # display label
    scores: { throughput: 40, residency: 5, ops-cost: 3, team-skill: 5 }
    notes: { en: … }          # optional rationale for the raw numbers
```

- `scores` must cover **every** criterion `key`, with numeric values.
- Values are **raw metric values** (tps, USD, a 1–5 rating). `score.py` min-max
  normalizes per axis, so units need not match across axes — only be consistent
  within an axis. For `direction: min` (cost), lower raw values normalize to higher
  goodness automatically.
- Raw scores are **research output** (competitive-analysis / web), not invented here.

## How scoring works

1. Per criterion, min-max normalize across candidates to a 0..1 goodness (higher =
   better), inverting when `direction: min`. If all candidates tie on an axis, each
   gets goodness 1.0.
2. Weighted total = Σ(weight · goodness) / Σweight → 0..1 (reported for readability;
   ranking is unaffected by the denominator).
3. Sensitivity: each weight is multiplied by 0, 0.5, 0.75, 1.25, 1.5, 2.0 in turn;
   if the winner changes within ±50% (×0.5 or ×1.5), the decision is flagged
   **fragile** — record that caveat in the ADR.
