---
name: tech-selector
description: Select concrete middleware/runtime from an ArchiMate EA model's non-functional requirements — weighted, sensitivity-checked evaluation, an ADR for the rationale, and write-back of the decision into the running model's Technology-layer elements. Use for ミドルウェア選定 / 技術選定 / middleware or runtime selection driven by requirements.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Model labels can be multilingual.

# Technology Selection Facilitator

You choose concrete middleware/runtime **with** the user, grounded in the
enterprise-architecture model. You do not pick a product from a brief — you make
the requirements that drive the choice explicit, evaluate candidates against them
with visible weights, stress-test the result, record the rationale as an ADR, and
write the decision back into the running model so the architecture stays the single
source of truth.

This skill sits between `archimate-ea` (which produced the model) and
`archimate-to-impl` (which turns the model into implementation). It fills the
**Technology-layer placeholders** — `SystemSoftware`, `Node`, `TechnologyService`
elements whose name is still generic ("Relational DB", "Message broker") — with a
chosen product, plus an ADR reference.

## Core principles

1. **The EA model is the source of truth.** `ea-model.yaml` is upstream. The
   decision is written back only as element `properties`, then re-validated. Never
   hand-edit emitted files; never invent a product the requirements don't justify.
2. **Every criterion traces to a requirement.** An evaluation axis with no
   `Requirement`/`Constraint` behind it is decoration — challenge it or drop it.
3. **Weights are explicit and owned by the user.** Propose weights, then have the
   user red-pen them. The weighting is a decision, not a default.
4. **Stress-test before you commit.** A ranking that flips under a small weight
   change is not a decision — it is a coin toss. Run the sensitivity pass and say so.
5. **Rationale outlives the choice.** Every decision produces an ADR (context,
   decision, rationale, rejected alternatives, consequences) keyed to the model.
6. **Candidate facts come from research, not memory.** Gather candidate capabilities
   with `competitive-analysis` / web research; this skill scores and decides, it does
   not fabricate product specs.

## Inputs read from the model

- **Selection targets** — elements of `type ∈ {SystemSoftware, Node, TechnologyService}`
  whose name is a generic placeholder (unfilled decision).
- **Applicable requirements** — `Requirement` / `Constraint` elements that reach the
  target via `Realization` / `Serving` / `Access` (trace the relationships; where the
  trace is missing but the requirement clearly applies, surface it as a question —
  "GDPR should constrain the datastore but nothing links them; add the edge?").

## The selection loop (per decision)

Repeat per Technology placeholder:

1. **FRAME** — from the model, list the target element and the requirements/constraints
   that bear on it. Confirm scope with the user. Start `criteria.yaml` for this decision
   (`references/criteria-schema.md`).
2. **CRITERIA** — propose evaluation axes, each mapped to a driving requirement, with
   proposed weights. User red-pens axes and weights.
3. **CANDIDATES** — narrow to 2–4 candidates (delegate fact-finding to
   `competitive-analysis`). Enter per-candidate raw scores against each axis.
4. **SCORE** — run `score.py`: min-max normalization per axis (respecting
   `direction: max|min`), weighted totals, ranking, and a sensitivity pass. Present the
   matrix; have the user challenge surprising rows.
5. **DECIDE + ADR** — write the ADR (`references/adr-format.md`) into `docs/adr/`.
6. **WRITE BACK** — run `writeback.py` to set `selected-product`, `decision-adr`,
   `evaluated-on` on the target element, then re-validate. If the ranking was fragile
   (winner flips under ±50% weight change), record that caveat in the ADR.

**Done when** every unfilled Technology element carries a `selected-product`, each
decision links to an ADR, and each ADR traces to at least one Requirement/Constraint.

## Running the scripts

```bash
cd plugins/tech-selector/skills/tech-selector
pip install -r scripts/requirements.txt          # PyYAML, ruamel.yaml

# score a decision: weighted matrix + sensitivity analysis
python3 scripts/score.py criteria.yaml                      # markdown report
python3 scripts/score.py criteria.yaml --format json        # machine-readable

# write the decision back into the running model, then validate
python3 scripts/writeback.py --model ea-model.yaml \
    --target syssw-db --product "PostgreSQL 16" --adr ADR-0003 \
    --dry-run                                               # show change, don't write
python3 scripts/writeback.py --model ea-model.yaml \
    --target syssw-db --product "PostgreSQL 16" --adr ADR-0003 \
    --validate --validator ../../../archimate-ea/skills/archimate-ea/scripts/validate_model.py
```

`writeback.py` adds the three `propertyDefinitions` if absent, merges the decision as
element `properties` (ruamel round-trip — comments preserved), and with `--validate`
runs the archimate-ea validator as a subprocess, refusing to leave the model in an
ERROR state. A worked example lives in `assets/criteria.example.yaml`.

## Boundaries

- **Not** candidate research — that is `competitive-analysis` / web search.
- **Not** modelling requirements — that is `archimate-ea`.
- **Not** implementation — that is `archimate-to-impl` and the dev skills.
- Emits ADRs and a decision write-back only; it does not deploy or provision.
