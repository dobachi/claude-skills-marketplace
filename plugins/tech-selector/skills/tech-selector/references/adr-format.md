# ADR format (MADR-lite)

Each selection decision produces one Architecture Decision Record under `docs/adr/`,
named `NNNN-<kebab-topic>.md` (zero-padded sequence, e.g. `0003-relational-datastore.md`).
The `decision-adr` property written into the model references it by id (`ADR-0003`).

## Template

```markdown
# ADR-0003: Relational datastore selection

- Status: accepted            # proposed | accepted | superseded by ADR-XXXX
- Date: 2026-07-03
- Model target: `syssw-db`    # ea-model element this decision fills
- Drivers: `req-mobile`, `constraint-gdpr`   # Requirement/Constraint ids

## Context

What forces are at play — the requirements/constraints from the model that drive
this choice, and any scope boundaries. Link to the model, not a re-description.

## Decision

We will use **PostgreSQL 16** for `syssw-db`.

## Rationale

Summarize the weighted evaluation (link or embed the `score.py` matrix). State the
weighted total and the ranking. **If the sensitivity pass flagged the decision
fragile, say so here** and explain why the choice still holds (or what would change it).

## Rejected alternatives

- **DynamoDB** — highest throughput but fails the residency weighting and low team
  familiarity; rejected.
- **MySQL 8** — close second; rejected on weaker residency tooling.

## Consequences

What this enables and what it costs — operational burden, lock-in, migration paths,
and any new requirements/constraints this decision creates (feed those back into the
model via archimate-ea).
```

## Rules

- **Trace up.** Every ADR lists at least one Requirement/Constraint id under Drivers.
  An ADR that traces to nothing is a decision without a reason — go find the reason.
- **Record fragility.** If `score.py` reported the winner as fragile, the Rationale
  must acknowledge it. A silent fragile decision is the failure mode this skill exists
  to prevent.
- **One decision per ADR**, matching one `criteria.yaml` and one model target.
- **Supersede, don't rewrite.** When a decision changes, add a new ADR and set the old
  one's Status to "superseded by ADR-XXXX"; keep the history.
