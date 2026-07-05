# Elicitation playbook

Per-layer question banks, Definition-of-Done gates, and the rule for when to slow
down to one question at a time. The facilitation loop (ELICIT → PROPOSE → VALIDATE
→ CHECKPOINT) is in SKILL.md; this is the content you pour into it.

## Pacing: batch vs. one-at-a-time

Default is **batched** — ask a focused set, then propose a model fragment the user
red-pens. Switch to **one question at a time** when the answer is structural and
expensive to get wrong:

- The root goals and the business problem being solved.
- Scope boundaries — what is in/out of this architecture.
- Top-level capabilities or the primary value streams.
- Hard constraints with legal/security/compliance weight.
- Any point where the user hesitates, contradicts an earlier answer, or where two
  readings lead to materially different models.

Everything else (filling out a layer once its shape is agreed) stays batched.

## Adaptive entry

Top-down (Motivation → down) is the default, but start where the user has material.
If they arrive with an application landscape, model that first, then fan **up** to
"what goals/requirements do these serve?" and **down** to technology. Always
reconnect upward to motivation before declaring a layer done — an element no
requirement or goal traces to is a prompt, not a fact.

## Per-layer question banks & Definition of Done

> The forward-trace half of each DoD below — "X realizes a Requirement", "each
> ApplicationComponent is realized/served by technology" — is machine-checked by
> `scripts/trace_coverage.py`, encoded as its rule table. Run it at every CHECKPOINT:
> it names the upper elements left without a downstream carrier and shows a per-Goal
> reach matrix so skew is visible. If you add or change a DoD rule here, mirror it in
> that script's `RULES` so prose and check stay in sync.

### Motivation
Ask: Who are the stakeholders and what does each care about? What external/internal
drivers force change? What is your honest assessment of the current state? What are
the goals (measurable outcomes)? Which requirements and constraints follow? Any
guiding principles?
**DoD:** every Goal has ≥1 Stakeholder/Driver behind it and ≥1 Requirement or
Outcome realizing it; constraints captured; no orphan motivation element.

### Strategy
Ask: What capabilities must the enterprise have to meet the goals? What resources
back them? What courses of action (initiatives) develop them? What value streams
deliver value to customers?
**DoD:** each Capability traces up to a Goal and is backed by a Resource or
CourseOfAction.

### Business
Ask: Who are the actors/roles? What business services do you offer externally?
What processes deliver them? What business objects/contracts are involved? What
events trigger the processes?
**DoD:** each BusinessService realizes a Requirement or supports a Capability; each
service is realized by ≥1 process; actors assigned to the roles/processes.

### Application
Ask: What application components/systems exist (or are needed)? What application
services do they expose, through which interfaces? What data objects do they own?
Which business processes do these services serve?
**DoD:** each ApplicationService serves a business process or realizes a
requirement; components assigned to their functions; data objects owned.

### Technology
Ask: What nodes/devices/system software host the components? What technology
services do they provide? What artifacts are deployed where? What networks connect
them?
**DoD:** each ApplicationComponent is realized/served by technology; artifacts
deployed on nodes; networks connect the nodes.

### Physical (when relevant)
Ask: What equipment, facilities, distribution networks, or materials are involved?
Skip entirely for pure-IT architectures.
**DoD:** physical elements connect to the technology that depends on them.

### Implementation & Migration
Ask: What is the current plateau and the target plateau? What gaps separate them?
What work packages close the gaps, producing what deliverables? What milestones?
**DoD:** each Gap links current→target plateaus; each Gap is addressed by a
WorkPackage; deliverables realize the target-state elements.

## Red-pen prompts (use after proposing a fragment)

- "I've added these as <types>. Wrong type for any of them?"
- "Did I miss an actor / system / constraint?"
- "This edge says X realizes Y — is that the real dependency, or is it the other
  way / a different relationship?"
- "Anything here you'd cut to keep scope honest?"
