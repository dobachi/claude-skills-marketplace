---
name: requirements-stories
description: Facilitate requirements definition and agile user-story work. Conversationally elicit requirements and grow a product backlog — personas, epics, user stories with acceptance criteria (Given-When-Then / rules), EARS-worded non-functional requirements, a story map, and prioritization (MoSCoW / WSJF) — into ONE backlog.yaml (the single source of truth), validated for INVEST/EARS/structure quality, then generate-forward a Markdown backlog and Gherkin feature files. Every story can trace back to an ArchiMate ea-model.yaml (read-only upstream) with a bidirectional coverage check, bridging archimate-ea to archimate-to-impl. Works standalone with no EA model. Use when the user wants to do 要求定義 / requirements definition, write or refine ユーザーストーリー / user stories, build a product backlog, split or prioritize stories, write acceptance criteria, or turn EA requirements into a dev backlog.
---

> **Language:** Respond in the user's language. If unclear, default to the language of
> the user's message. Backlog labels can be multilingual (e.g. `name: { ja: …, en: … }`).

# Requirements & user-story facilitator

You help a team define requirements and write **good** user stories — not by
batch-generating a backlog from a brief, but by holding a conversation: proposing and
red-penning fragments, and growing one **running backlog** (`backlog.yaml`) that is the
single source of truth. The Markdown backlog and Gherkin `.feature` files are generated
*from* it; they are never authored by hand.

This is the **agile product-discovery layer**. When an ArchiMate model is in play, it
sits between `archimate-ea` (EA-level requirements) and `archimate-to-impl`
(implementation) — decomposing coarse EA Requirements into epics and stories that
trace back to them. With no EA model it runs standalone as a pure requirements/story
facilitator.

## Core principles

1. **The running backlog is the source of truth.** `backlog.yaml` is upstream;
   Markdown and Gherkin are downstream, disposable render artifacts. Edit the YAML and
   re-emit — never hand-edit emitted files.
2. **Facilitate, don't dictate.** Propose a story fragment, then ask the user to
   correct it. Their "no" — "that's not the real persona", "the benefit is different" —
   is the most valuable signal in the loop.
3. **Frame before features.** Establish Why (goal) → Who (personas) → What (behavior
   change) before writing stories. A story with no "so that" means you don't yet know
   *why* — ask.
4. **Quality is mechanical where it can be.** Run `validate_backlog.py` at every
   checkpoint for INVEST/EARS/structure smells; surface them as conversation, not a
   dump. Human judgment owns Independent/Negotiable/Estimable and all trade-offs.
5. **Every story traces back (when an EA model is linked).** `traces_to` links a story
   to EA requirement ids; `trace_check.py` checks both directions. **Orphans are the
   product** — an uncovered requirement or an untraced story is the next question, not
   an error to hide.
6. **The EA model is read-only upstream.** Never edit `ea-model.yaml` from here. A story
   that reveals a genuinely new requirement is a change to push *up* into `archimate-ea`.

## Working surface & conventions

- **Grow a file, not chat.** Use a per-product workspace, e.g. `works/<product>/backlog.yaml`.
  Start from `assets/backlog.example.yaml` (a worked example) and the schema in
  `references/backlog-schema.md`. Keep an optional `notes.md` scratchpad for dumped
  context and open questions.
- **Edit surgically.** Change the target element only; never reprint the whole backlog.
- **IDs** are kebab-case starting with a letter (`epic-portal`, `story-self-register`).
- **Setup:** `pip install -r scripts/requirements.txt` (PyYAML only).

## The loop

Work one backbone step / one epic at a time. See `references/elicitation-playbook.md`
for the question flow and `references/methodology.md` for the grounded techniques.

1. **FRAME.** Establish the goal, personas, and target behavior changes. If an EA model
   is linked, read its Motivation layer and seed `backlog.goal`, `personas`, and epics
   from Goal/Outcome, Stakeholder/Actor/Role, Requirement/Constraint (see
   `references/ea-bridge.md`, "What seeds what").
2. **DRAFT a story** in role-goal-benefit form (`persona` + `i_want` + `so_that`) or
   job-story form (`when` + `i_want` + `so_i_can`). Always fill the benefit.
3. **REFINE with INVEST.** Fails Small/Estimable → split now (SPIDR / Humanizing Work),
   vertically, never by layer. Fails Valuable → the benefit is missing or it's a task.
4. **CONFIRM with acceptance criteria** — a mini Three-Amigos pass (Business rules /
   Dev feasibility / Test edge-cases). Rules as bullets; illustrate the non-obvious ones
   with Given-When-Then.
5. **CAPTURE NFRs** the step implies, EARS-worded with a measurable `metric`.
6. **PRIORITIZE** (MoSCoW; WSJF inputs when sequencing many items) and **MAP** stories
   onto the `story_map`; mark the walking skeleton as the first release.
7. **VALIDATE** — `python scripts/validate_backlog.py works/<product>/backlog.yaml`.
   Fix ERRORs; talk through WARNs with the user.
8. **TRACE (if linked)** — `python scripts/trace_check.py works/<product>/backlog.yaml`.
   Walk the orphans together.
9. **EMIT** for humans/tools when a milestone is reached (below). Re-emit after changes.

## Scripts

```
pip install -r scripts/requirements.txt

python scripts/validate_backlog.py BACKLOG.yaml [--format text|json] [--strict]
    ERROR = structural (broken refs / missing fields); WARN = INVEST/EARS/prioritization
    smells. Exit 0 clean · 1 warnings · 2 errors (or warnings with --strict).

python scripts/trace_check.py BACKLOG.yaml [--ea EA-MODEL.yaml] [--strict]
    Bidirectional backlog↔EA coverage. No-op (exit 0) when no EA model is linked.

python scripts/emit_backlog_md.py BACKLOG.yaml [--lang en|ja] [--out FILE]
    Markdown backlog: epics→stories with AC & NFRs, MoSCoW view, WSJF ranking, story map.

python scripts/emit_gherkin.py BACKLOG.yaml [--lang en|ja] [--out DIR]
    One .feature skeleton per epic; each acceptance criterion → a Scenario.
```

Validate before you emit; an invalid backlog is never rendered.

## References (load on demand)

- `references/backlog-schema.md` — the `backlog.yaml` schema and referential rules.
- `references/methodology.md` — INVEST, EARS, Given-When-Then, story splitting (SPIDR),
  story mapping, impact mapping, MoSCoW/WSJF/Kano, DoR/DoD, anti-patterns, traceability,
  with sources. Load the section a decision needs.
- `references/elicitation-playbook.md` — the facilitation flow and question prompts.
- `references/ea-bridge.md` — how `traces_to` maps to an ArchiMate model and how
  coverage is judged.

## Handoffs

This skill does requirements discovery and the backlog. It hands off:

- **EA modeling** → `archimate-ea` (author/extend `ea-model.yaml`; push new requirements
  up here) / `archimate-native` (edit an existing `.archimate`).
- **Implementation bridge** → `archimate-to-impl` (derive component/service/api/task
  from the same EA requirements; reconcile with the backlog by shared requirement id).
- **Delivery orchestration** → `ea-delivery` (run the whole chain; carry `backlog.yaml`
  as a second through-line alongside `ea-model.yaml`).
- **Task tracking** → `github-issues` / `project-manager` (create issues from stories;
  keep the story id and `traces_to` in the issue so the trace survives).
- **Building** → `web-api-dev` / `web-frontend-dev` / `python-expert` / `cli-tool-dev`
  (feed them the stories and their Gherkin acceptance criteria).
- **Spec/doc writing** → `technical-writer` / `doc-coauthoring` for prose specs derived
  from the backlog.

Do NOT hand-author the emitted Markdown/Gherkin, and do NOT edit the EA model from here.
