# Methodology reference — requirements & user stories

The grounded practice this skill facilitates. Load a section when a decision needs it;
you do not need to read it end-to-end. Each item gives the canonical template, when
to use it, the main pitfalls, and a source.

---

## 1. User story format

**Connextra / role-goal-benefit template:**
> **As a** `<role/persona>`, **I want** `<goal>`, **so that** `<benefit>`.

Origin: the Connextra XP team (~2001), popularized by Mike Cohn, *User Stories
Applied* (2004). A story is a **placeholder for a conversation**, not a spec — Cohn's
**3 C's: Card, Conversation, Confirmation**. The "so that" is technically optional but
carries the value rationale, so keep it.

**Job Story alternative (Alan Klement, Intercom):** drops the persona, centers the
triggering context:
> **When** `<situation>`, **I want** `<motivation>`, **so I can** `<expected outcome>`.

Use job stories when personas are weak/misleading and the *situation* drives design
more than the role. The schema supports both forms (`persona`+`so_that`, or
`when`+`so_i_can`).

Pitfalls: generic "As a user…" (kills context); missing/weak "so that"; developer
stories with no end-user value; over-specified stories that dictate the solution;
horizontal (backend-only/UI-only) slices. Source: Mountain Goat Software; Intercom.

---

## 2. INVEST — is this a good story? (Bill Wake, 2003)

| Letter | Means | Test |
|---|---|---|
| **I**ndependent | Minimal ordering dependencies | Can it ship in (almost) any order? |
| **N**egotiable | A promise to converse, not a frozen contract | Room to discuss the "how"? |
| **V**aluable | Value to a user/customer | Can you state the benefit in the user's terms? |
| **E**stimable | Team can size it | Can they give a rough estimate? If not → spike |
| **S**mall | Fits one iteration | A few days, well under a sprint? |
| **T**estable | Verifiable acceptance criteria | Can you write pass/fail before building? |

Use as a refinement checklist; a failing letter signals a split, a spike, or a
rewrite. Nuance: Wake himself now de-emphasizes **E**stimable. INVEST is for *stories*;
*tasks* use SMART. Source: Agile Alliance glossary; XP123 (Wake).

`validate_backlog.py` mechanizes V (so_that/so_i_can present), T (acceptance_criteria
present), and S (estimate ≤ 8, ≤ 8 criteria). I, N, E stay human judgment.

---

## 3. Acceptance criteria: two formats

**A. Given-When-Then / Gherkin (scenario-oriented, BDD):**
```gherkin
Scenario: <specific example>
  Given <initial context/state>
  When  <event/action>
  Then  <expected observable outcome>
```
Use for behavior with state/branching, and when criteria should double as
executable/living documentation. Keep steps **declarative**, not UI-coupled ("When I
submit valid credentials", not "When I click the blue button").

**B. Rule-oriented bullet (constraint/validation):**
> - The system rejects a transfer exceeding the available balance.

Faster for constraints and NFR-ish conditions. **Rule of thumb:** state rules as
bullets, then illustrate only the non-obvious ones with 1–3 Given-When-Then examples.
Rules + examples beat either alone. Source: Cucumber "Gherkin Rules"; Adzic,
*Specification by Example*. The schema's `acceptance_criteria` accepts either shape.

---

## 4. EARS — non-functional & system requirements (Mavin et al., RE'09)

Five patterns constrain natural-language requirements; every one uses **shall**.

| Pattern | Template | For |
|---|---|---|
| **Ubiquitous** | The `<system>` **shall** `<response>`. | Always-true invariants |
| **Event-driven** | **When** `<trigger>`, the `<system>` **shall** `<response>`. | Response to an event |
| **State-driven** | **While** `<state>`, the `<system>` **shall** `<response>`. | Behavior during a state |
| **Unwanted** | **If** `<condition>`, **then** the `<system>` **shall** `<response>`. | Errors/faults/invalid input |
| **Optional** | **Where** `<feature>`, the `<system>` **shall** `<response>`. | Behavior in some configs |

Compound forms combine keywords ("While `<state>`, when `<trigger>`, the system
shall…"). Use for NFRs and system requirements where ambiguity is costly. Pitfall: a
well-formed EARS sentence can still be wrong or untestable — pair each with a
**measurable metric**. Source: alistairmavin.com/ears; Mavin et al., RE 2009.
`validate_backlog.py` checks the keyword matches the declared `pattern` and that a
`metric` exists.

---

## 5. Functional vs non-functional; quality attributes

- **Functional:** *what* it does ("shall calculate tax").
- **Non-functional:** *how well* / under what constraint ("p95 < 200 ms at 1,000
  concurrent users"). Must be **measurable** or it's an untestable wish.
- **ISO/IEC 25010** product-quality taxonomy. **2011:** 8 characteristics —
  Functional Suitability, Performance Efficiency, Compatibility, Usability,
  Reliability, Security, Maintainability, Portability. **2023:** adds **Safety**;
  renames Usability→Interaction Capability, Portability→Flexibility (9 total). Cite the
  year. Use the characteristic name in `nfr.quality`.
- **Three channels to capture an NFR:** (1) cross-cutting NFR list (system-wide
  targets), (2) bake into the relevant story's acceptance criteria, (3) Definition of
  Done (global gates every story inherits). Source: ISO/IEC 25010:2023.

---

## 6. Elicitation techniques (BABOK) — combine several

Interviews · facilitated workshops · observation/job-shadowing · prototyping ·
document analysis · brainstorming · surveys/focus groups · interface analysis. Agile
additions: **Event Storming**, **5 Whys**, **Impact Mapping** (§10), **Story Mapping**
(§9), **Example Mapping** (rules/examples/questions on cards). No single technique
suffices. See `elicitation-playbook.md` for the question flow. Source: IIBA BABOK.

---

## 7. Prioritization

- **MoSCoW** (Clegg/DSDM): **Must / Should / Could / Won't (this time)**. Keep *Must*
  to the protected minimum (guidance: ≤~60% of effort) so Should/Could act as buffer.
  Pitfall: everything becomes "Must" (`validate_backlog.py` flags >60% by count on
  backlogs of ≥5 prioritized stories).
- **WSJF** (SAFe): sequence for economic value.
  > **WSJF = Cost of Delay ÷ Job Size**, where **CoD = User-Business Value +
  > Time Criticality + Risk-Reduction/Opportunity-Enablement**.
  Score each input *relatively* on modified-Fibonacci (1,2,3,5,8,13,20); highest
  first. The schema's `wsjf:` block feeds `emit_backlog_md.py`'s ranking. Pitfall:
  treating the numbers as absolute — they're relative.
- **Kano** (Kano): Must-be (basic) / Performance (linear) / Attractive (delighter) /
  Indifferent / Reverse. Delighters decay to expected over time. Balances table-stakes
  vs differentiators; maps roughly onto MoSCoW.
- **Value vs Effort (2×2):** do high-value/low-effort first ("quick wins"). Fast and
  coarse; weak on dependencies/risk. Source: SAFe; AltexSoft.

---

## 8. Story hierarchy & splitting

**Hierarchy:** Theme → Epic → (Feature, SAFe-only) → Story → Task. "Feature" is
SAFe-specific; plain Scrum uses Epic → Story. The constant: **stories are the smallest
independently valuable unit; tasks are not user-facing.**

**SPIDR (Mike Cohn)** — five cut lines, each producing independently shippable slices:
- **S**pike — split off research when unestimable.
- **P**aths — separate distinct flows (card vs PayPal).
- **I**nterfaces — split by UI/device/API surface (simple first).
- **D**ata — deliver one data type/subset first.
- **R**ules — relax business rules initially, add them back later.

**Humanizing Work flowchart (Lawrence)** — patterns: workflow steps · business-rule
variations · major effort · simple/complex (happy path first) · data variations · data
entry methods · deferred performance (make it work, then fast) · CRUD operations ·
break out a spike. **Meta-pattern:** find the core complexity, enumerate its variations,
build one thin end-to-end slice through the hard part first.

**Always split vertically** (thin end-to-end value), never by architectural layer.
Source: Mountain Goat Software (SPIDR); Humanizing Work.

---

## 9. User story mapping (Jeff Patton, 2014)

A 2-D backlog that keeps the narrative a flat list loses.
- **Backbone** (top row): high-level **activities**, left→right in the user's journey.
- **Steps** (2nd row): tasks to accomplish each activity.
- **Details** (below): stories/variations, ordered top→bottom by priority.
- **Walking skeleton:** the thinnest slice crossing *every* backbone step — a minimal
  end-to-end version that works; your first release.
- **Release slices:** horizontal lines; each slice spans the whole backbone.

Pitfall: mapping your *screens* instead of the user's *activities*; slicing per-feature
so early releases don't actually work. The schema's `story_map:` block captures this;
the first `releases` entry is the walking skeleton. Source: Patton, *User Story Mapping*.

---

## 10. Impact mapping (Gojko Adzic, 2012)

A mind-map answering **Why → Who → How → What**:
- **Why — Goal:** the measurable business objective (center).
- **Who — Actors:** who can help or obstruct it.
- **How — Impacts:** the **behavior change** in an actor that moves the goal (not a
  feature — a behavioral shift).
- **What — Deliverables:** features we *might* build to cause an impact — framed as
  assumptions/experiments.

Keeps teams on **outcomes over outputs** and prunes features with no path to the goal.
Pitfall: jumping straight to "What"; writing features at the Impact level. Pairs with
the EA bridge — the EA model's Goal/Outcome are the "Why", its Stakeholder/Actor the
"Who". Source: impactmapping.org.

---

## 11. Definition of Ready & Definition of Done

- **Definition of Done (DoD)** — an *official Scrum artifact* (2020 Scrum Guide, a
  commitment on the Increment). If an item doesn't meet the DoD it can't be released or
  shown at review. Typical: code reviewed; tests written & passing; acceptance criteria
  met; CI green; security/perf checks pass; docs updated; deployed to staging.
- **Definition of Ready (DoR)** — **NOT in the Scrum Guide**; an optional team
  convention. A checklist before pulling a story into a sprint: follows INVEST; clear
  acceptance criteria; dependencies resolved; small enough; designs available;
  Three-Amigos'd. Keep it lightweight — a rigid DoR creates mini-waterfall gating.

Don't present DoR as official Scrum. Source: 2020 Scrum Guide; Scrum.org; Scrum Alliance.

---

## 12. Three Amigos / Specification by Example

**Three Amigos:** a short, frequent conversation across three perspectives before/while
building a story — **Business (why)**, **Development (how)**, **Testing (how do we know
it's right / what breaks)**. Produces concrete acceptance examples before coding.

**Specification by Example (Adzic, 2011)** — derive requirements from concrete,
realistic examples; the agreed examples become **executable acceptance tests** and
**living documentation**. **Example Mapping** is the lightweight card format: Rules,
Examples, Questions. Feeds §3 acceptance criteria directly. Source: Adzic; J.F. Smart.

---

## 13. Anti-patterns to flag (don't silently fix — raise them)

Gold-plating (building beyond the need) · solutioning in requirements (specifying the
*how*, foreclosing options) · ambiguous/unmeasurable "shall" ("fast", "secure") ·
stories that are tasks ("As a developer I want to update the schema") · missing "so
that" · horizontal slicing · generic role ("As a user") · over-detailed/frozen stories
(kills the conversation) · acceptance criteria that just restate the story · everything
a "Must" · big up-front spec with no traceability. Source: Roman Pichler; Blueprint.

---

## 14. Traceability

> **Goal/Need → Requirement (Epic) → User Story → Acceptance Criterion/Test →
> Implementation → Verification.**

Forward (goal → deliverable: are all needs covered?) and backward (code/test →
requirement: why does this exist? no orphans). Together = **bidirectional**, required
by **ISO/IEC/IEEE 29148**. Lightweight mechanics: story IDs in commits/branches/PRs;
Gherkin scenarios living in the repo; issue-tracker links; an RTM in regulated
contexts. In this skill, `traces_to` links a story to EA element ids and
`trace_check.py` enforces both directions. See `ea-bridge.md`.

**Well-formed requirement (29148:2018):** necessary, appropriate, unambiguous,
complete, singular, feasible, verifiable, correct, conforming; the *set* complete,
consistent, non-redundant. Source: ISO/IEC/IEEE 29148:2018.

---

## Sources

- EARS: https://alistairmavin.com/ears/ · Mavin et al., RE'09
- INVEST: https://www.agilealliance.org/glossary/invest/
- Story template: https://www.mountaingoatsoftware.com/blog/why-the-three-part-user-story-template-works-so-well
- Job stories: https://www.intercom.com/blog/accidentally-invented-job-stories/
- SPIDR: https://www.mountaingoatsoftware.com/blog/five-simple-but-powerful-ways-to-split-user-stories
- Story splitting: https://www.humanizingwork.com/the-humanizing-work-guide-to-splitting-user-stories/
- Story mapping: https://jpattonassociates.com/the-new-backlog/
- Impact mapping: https://www.impactmapping.org/
- Specification by Example: https://gojko.net/2020/03/17/sbe-10-years.html · Gherkin rules: https://cucumber.io/blog/bdd/gherkin-rules/
- WSJF: https://framework.scaledagile.com/wsjf · MoSCoW/Kano: https://www.altexsoft.com/blog/most-popular-prioritization-techniques-and-methods-moscow-rice-kano-model-walking-skeleton-and-others/
- ISO/IEC 25010:2023: https://www.iso.org/standard/78176.html
- ISO/IEC/IEEE 29148:2018: https://www.iso.org/standard/72089.html
- Definition of Done: https://www.scrum.org/resources/what-definition-done
- Elicitation (BABOK): https://www.bridging-the-gap.com/elicitation-techniques-business-analysts/
- Story mistakes: https://www.romanpichler.com/blog/5-common-user-story-mistakes/
