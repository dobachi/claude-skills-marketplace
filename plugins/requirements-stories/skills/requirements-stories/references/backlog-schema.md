# `backlog.yaml` schema

The running model this skill grows. It is the **single source of truth**; the
Markdown backlog and Gherkin `.feature` files are generated *from* it and are
disposable. Hand-edit `backlog.yaml`, then re-emit — never hand-edit the emitted
files.

The file is plain YAML. Bilingual labels use `{ ja: …, en: … }` anywhere a `name`
or prose field appears; a plain string is also accepted. IDs are kebab-case and
start with a letter (`epic-portal`, `story-self-register`).

```yaml
backlog:
  id: backlog-<slug>              # required, unique
  name: { ja: …, en: … }          # required
  ea_model: ../ea-model.yaml      # optional — path to the ArchiMate model this backlog traces into.
                                  #   Relative to this backlog.yaml. Omit for standalone use.
  goal: { ja: …, en: … }          # optional — the product/impact goal (impact-mapping "Why")

# ── WHO ──────────────────────────────────────────────────────────────────
personas:                         # the roles that appear in "As a <persona>"
  - id: persona-<slug>            # required, unique
    name: { ja: …, en: … }        # required
    description: …                # optional — one line of who they are / their context
    traces_to: [ <ea-id> … ]      # optional — EA Stakeholder / BusinessActor / BusinessRole ids

# ── WHAT (coarse) ────────────────────────────────────────────────────────
epics:                            # large bodies of work; each usually maps to one EA Requirement
  - id: epic-<slug>               # required, unique
    name: { ja: …, en: … }        # required
    description: …                # optional
    priority: Must                # optional — MoSCoW: Must | Should | Could | Won't
    traces_to: [ <ea-id> … ]      # optional — EA Requirement / Constraint ids this epic realizes

# ── WHAT (fine) ──────────────────────────────────────────────────────────
stories:
  - id: story-<slug>              # required, unique
    epic: epic-<slug>             # optional — parent epic id (must exist)
    # Role-goal-benefit form (Connextra). Provide persona + i_want + so_that:
    persona: persona-<slug>       # who — must be a defined persona id (or a plain string role)
    i_want: { ja: …, en: … }      # what — the capability
    so_that: { ja: …, en: … }     # why — the benefit (INVEST-Valuable; omitting it warns)
    # …OR the Job-Story form (Klement). Provide when + i_want + so_i_can instead of persona/so_that:
    # when: { ja: …, en: … }      # the triggering situation
    # i_want: { ja: …, en: … }    # the motivation
    # so_i_can: { ja: …, en: … }  # the expected outcome
    priority: Must                # optional — MoSCoW (inherits epic's if omitted)
    estimate: 3                    # optional — story points; large values warn (INVEST-Small)
    wsjf:                          # optional — SAFe Weighted Shortest Job First inputs
      business_value: 8            #   relative, modified-Fibonacci (1,2,3,5,8,13,20)
      time_criticality: 5
      risk_reduction: 3            #   risk-reduction / opportunity-enablement
      job_size: 5                  #   duration/size; WSJF = (bv+tc+rr) / job_size
    status: ready                 # optional — draft | ready | in-progress | done
    traces_to: [ <ea-id> … ]      # optional — EA Requirement/Constraint ids (inherits epic's if omitted)
    acceptance_criteria:          # the "Confirmation" — how we know it's done (INVEST-Testable)
      - id: ac-<slug>             # optional id (auto-numbered in emit if omitted)
        # Gherkin (scenario) form — for behavior with state/branching:
        scenario: …               # optional short title
        given: … | [ …, … ]       # context (string or list)
        when:  … | [ …, … ]       # action/event
        then:  … | [ …, … ]       # observable outcome
        # …OR rule form — for constraints/validation (one line):
        # rule: "The system rejects a duplicate email."
    notes: …                      # optional — open questions, links, decisions

# ── HOW WELL (non-functional) ────────────────────────────────────────────
nfrs:                             # quality attributes, EARS-worded and measurable
  - id: nfr-<slug>                # required, unique
    pattern: event-driven         # EARS: ubiquitous | event-driven | state-driven | unwanted | optional
    quality: PerformanceEfficiency # optional — ISO/IEC 25010 characteristic
    text: { ja: …, en: … }        # the EARS sentence (must contain the pattern's keyword + "shall")
    metric: "p95 < 500 ms @ 1000 concurrent users"  # optional but strongly recommended (measurable threshold)
    applies_to: [ story-<slug> … ] # optional — stories this NFR constrains
    traces_to: [ <ea-id> … ]      # optional — EA Constraint/Requirement ids

# ── STORY MAP (Jeff Patton) ──────────────────────────────────────────────
story_map:                        # optional 2-D narrative view
  backbone:                       # activities left→right in the user's narrative flow
    - activity: { ja: …, en: … }
      steps:
        - step: { ja: …, en: … }
          stories: [ story-<slug> … ]   # ordered top→bottom by priority
  releases:                       # optional horizontal slices; the first is the walking skeleton
    - name: "Walking skeleton (MVP)"
      stories: [ story-<slug> … ]

# ── TEAM AGREEMENTS (optional) ───────────────────────────────────────────
definition_of_ready: [ … ]        # checklist a story meets before a sprint (NOT a Scrum-Guide artifact)
definition_of_done:  [ … ]        # quality gate every story inherits (Scrum-Guide commitment)
```

## Referential rules the validator enforces

- `id`s are unique across the whole file.
- `story.epic`, `story.persona` (when an id, not a free string), `story.applies_to`
  targets, `nfr.applies_to` story ids, and every `story_map` story id resolve to a
  defined element.
- Every `traces_to` id — on a persona, epic, story, or nfr — resolves to an element
  in the referenced `ea_model` (only checked when `ea_model` is set and readable).

## What is deliberately NOT here

There is no ArchiMate element for a user story, so stories do **not** live inside
`ea-model.yaml`. This file references the EA model by id (`traces_to`) instead,
keeping the EA model clean and letting the backlog also stand alone. See
`ea-bridge.md`.
