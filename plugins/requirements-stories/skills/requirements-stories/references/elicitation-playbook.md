# Elicitation playbook — the facilitation flow

How to run the conversation that fills `backlog.yaml`. You are a facilitator: propose a
fragment, let the user correct it. Their "no" is the most valuable signal. Never
batch-generate a whole backlog from a one-line brief — grow it a slice at a time.

## Opening: frame before features (impact-map order)

Resist jumping to stories. Establish **Why → Who → What** first (impact mapping, §10 of
methodology.md):

1. **Why — the goal.** "What measurable outcome does this product/feature move?" If an
   EA model is linked, read its `Goal`/`Outcome` and confirm them. Record in
   `backlog.goal`.
2. **Who — the actors/personas.** "Who acts to reach that goal — and who could block
   it?" Seed personas from EA `Stakeholder`/`BusinessActor`/`BusinessRole`. Avoid the
   generic "user"; name the real role and its context. → `personas`.
3. **What behavior change** would move the goal? (Impacts.) This keeps you on outcomes,
   not a feature wishlist. The deliverables that cause those impacts become epics.

## Discovery techniques (pick by situation)

- **Interview / workshop** — ask open questions; capture verbatim, then reflect back.
- **Observation** — when the work is tacit, watch it; users under-report what they do.
- **5 Whys** — when a request sounds like a solution, drill to the underlying need
  ("You want an export button — so that…? …so that…?"). Strip solutioning back to the
  requirement.
- **Event Storming / workflow walk** — narrate the user's journey end to end; the steps
  become the story-map backbone.
- **Example Mapping** — for one story, put **Rules**, **Examples**, and **Questions** on
  cards. Rules → acceptance criteria; open Questions → `notes`; too many rules → split.

## From activity to story (the loop, one backbone step at a time)

For each step in the user's journey:

1. **Draft a story** in role-goal-benefit form (or job-story form if the situation
   drives it more than the role). Always fill the benefit — if you can't, you don't yet
   understand *why*; ask.
2. **Run it through INVEST** (§2). If it fails **Small** or **Estimable**, split it now
   (§8 SPIDR / Humanizing Work) — vertically, never by layer. If it fails **Valuable**,
   the "so that" is missing or it's really a task.
3. **Write acceptance criteria** (§3) via a mini Three-Amigos lens: Business (rules),
   Dev (feasibility), Test (what breaks / edge cases). Rules as bullets; illustrate the
   non-obvious ones with Given-When-Then.
4. **Surface NFRs** the step implies (latency, security, availability…). Word them in
   EARS (§4) with a measurable metric. Attach to the story (`applies_to`) or keep
   cross-cutting.
5. **Prioritize** (§7): MoSCoW at minimum; WSJF inputs if sequencing many items.

## Clarifying-question prompts (adapt, ask in the user's language)

- Goal/value: "How will we know this worked? What number moves?"
- Actors: "Besides the obvious user, who else touches this — approvers, admins,
  downstream systems?"
- Boundaries: "What is explicitly *out* of scope for now?"
- Rules & edges: "What must never happen? What are the invalid inputs / error paths?"
- Data: "What varies — data types, volumes, states? Do any justify separate stories?"
- NFRs: "How fast / how many at once / how available? Any compliance constraints?"
- Done: "What has to be true for this to be shippable?" → Definition of Done.

## Checkpoints

- **Validate early and often:** run `validate_backlog.py` at each checkpoint; surface
  smells as conversation, not a dump. Fix INVEST/EARS smells while context is fresh.
- **Trace when linked:** run `trace_check.py`; walk the orphans with the user — an
  uncovered EA requirement is a "did we forget this?", an untraced story is a "should
  this exist / does the EA model need to grow?".
- **Map for release:** once stories exist, lay out the `story_map`; draw the walking
  skeleton (thinnest end-to-end slice) as the first release.

## Anti-patterns to catch in the moment (§13)

Flag, don't silently fix: solutioning inside a requirement, gold-plating, everything a
"Must", a story that's a task, a criterion that just restates the story, an unmeasurable
NFR, horizontal slices. Name the smell and ask the user how to resolve it.
