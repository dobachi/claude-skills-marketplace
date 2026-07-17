# Adapter: specs & requirements

Applies the essence test to requirement documents, PRDs, functional/technical specs,
RFCs, ADRs, user-story backlogs, and acceptance criteria. Use with the five-question test
in `SKILL.md`.

## What "purpose" and "load-bearing" mean here

- **Purpose** = the problem the system must solve for its users, and the decision the spec
  must let the reader make (build it / estimate it / approve it).
- **Load-bearing** = the **Must-have** behavior — the requirements without which the system
  fails its users. Brooks's test applies directly: a requirement whose absence users would
  *not* notice as "incorrect" is not essential to this release.

## Articulating the irreducible core

State the **minimum viable spec**: the smallest set of Must-have capabilities that solves
the core problem. Everything else — Should / Could / speculative NFR — is measured against
whether it earns its place in *this* scope.

## The MoSCoW / YAGNI lens

Re-classify every requirement:

- **Must** → essential. Keep.
- **Should** → supporting. Keep only if cheap; otherwise demote to a later phase.
- **Could / Won't-now** → inessential for this scope. Cut candidate (move to backlog, don't
  delete the idea).
- **"We might need…" / "to be safe…"** → speculative generality / gold-plating. Cut.

The decision rule is the YAGNI line: **"we know we need this" (keep) vs "we might need this
someday" (defer)**. Anything that entered the spec without a triggering user need or ticket
is a scope-creep candidate — call it out explicitly.

## Spec-specific cruft

| Category | What it looks like in a spec |
|---|---|
| Gold-plating | Over-tight NFRs ("99.999% uptime", sub-10ms latency) with no stated need; luxury features. |
| Speculative generality | "Configurable", "pluggable", "extensible to future providers" with one current case. |
| Redundancy | The same rule stated as a requirement *and* an acceptance criterion *and* in prose. |
| Premature detail | A chosen library / schema / algorithm baked into a *what*-level requirement. |
| Scope creep | Requirements serving a different persona or a different product than the stated one. |
| Filler | Boilerplate NFR sections copied wholesale with no tailoring. |

## Guardrails specific to specs (do not over-cut)

- **A requirement is a contract.** Never silently drop one. Cutting a requirement is a
  scope decision the stakeholder must confirm — surface it, name what capability is lost.
- **Distinguish gold-plating from a real constraint.** An SLA that looks aspirational may be
  contractual or regulatory. If you can't tell → **flag** (Chesterton's Fence), don't cut.
- **Keep the acceptance criteria that pin a Must.** Cutting the criterion, not the
  requirement, quietly makes the requirement untestable.
- **NFRs the domain mandates** (security, accessibility, data-retention law) are essential
  even when unglamorous — never mistake "boring" for "inessential".

## Handoffs

- The requirements are sound but disorganized/duplicated in wording → `doc-refactor`.
- A requirement is ambiguous, untestable, or contradictory → **flag** (a `doc-review` /
  requirements-quality matter), don't resolve it by cutting.
- Turning kept requirements into stories / EARS NFRs → `requirements-stories`.
- Kept requirements feeding EA design → `archimate-ea`.
