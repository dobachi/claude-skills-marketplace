---
name: essence-distiller
description: >-
  Find the essence of an artifact and cut what is inessential — the via-negativa
  counterpart to doc-refactor, across prose/docs, specs & requirements, code, and
  diagrams. Separates what is load-bearing for the artifact's ONE purpose and
  audience from redundancy, gold-plating, decoration, filler, speculative
  generality, premature detail, and scope creep, then PROPOSES cuts with rationale
  and a "what would be lost" note. Deliberately meaning-changing, so:
  diagnose-first, non-destructive, propose-then-confirm; every cut anchored to a
  stated purpose + audience; Chesterton's Fence respected; correctness and behavior
  preserved. Use when the user says "cut this down to the essence", "strip the
  nice-to-haves", "remove the fluff / bloat", "over-engineered", "YAGNI review",
  "本質は何か", "本質だけ残して", "そぎ落として", "盛りすぎ". Hands off pure rearrange →
  doc-refactor; the code edit → /simplify; a diagram redraw → document-figures;
  a short derivative → document-summary; style tics → ai-tell-reducer. Bilingual JA/EN.
---

# Essence Distiller

## Core idea: subtraction, not rewriting

Human- and AI-authored artifacts accrete. A document grows a second introduction, a
spec sprouts a "would be nice" NFR, a function gains a config flag no one uses, a diagram
collects decorative boxes. Each addition felt reasonable; together they bury the point.

This skill does one thing: **separate the essence from the accident, then cut the
accident.** The essence is whatever is load-bearing for the artifact's *one purpose* and
*its audience*. The accident is everything the artifact would still fulfil that purpose
without — the redundancy, the gold-plating, the decoration, the filler, the speculative
generality, the premature detail, the scope creep.

Coined by Saint-Exupéry: *"Perfection is achieved not when there is nothing more to add,
but when there is nothing left to take away."* Named by Brooks (*No Silver Bullet*):
**essential** complexity is inherent to the problem; **accidental** complexity is a
contingent by-product of how it was built — and only the accidental kind can be removed
without changing what the artifact *is*.

### This is meaning-changing — and that is the point

`doc-refactor` preserves every claim and only rearranges. This skill *removes* content it
judges inessential. Because that changes meaning, it is **diagnose-first, non-destructive,
and propose-then-confirm**: you show what you'd cut and why *before* cutting, the user
decides, and the distilled result is a **new** artifact with the original preserved.

If, after diagnosis, nothing should be *cut* and the artifact only needs *rearranging*,
stop and hand off to `doc-refactor`. If the essence needs *more* evidence or a fixed
argument, that is `doc-review`'s job, not this one. Distilling only ever subtracts.

## The anchor: essence is purpose-relative (never skip Pass 0)

You cannot judge essence in the abstract. The same paragraph is essential in a decision
memo and inessential in a one-line status update. Brooks's own test is purpose-relative:

> If there is any way the audience would consider the artifact correct / complete /
> usable **without** a given element, that element is not essential *to this purpose*.

So the first move is always to fix the target. Everything downstream is measured against
it, and **the stated purpose is surfaced in the output** so the user can challenge it —
because re-aiming the purpose flips elements between essential and inessential.

Never distill against a purpose you merely guessed. If the artifact's purpose or audience
is ambiguous, **ask** (one or two sharp questions) before classifying anything.

## Invariants — never violate these

1. **Anchor every cut to a stated purpose + audience.** No purpose, no cut. The purpose you
   distilled against appears in the ledger.
2. **Propose, don't delete.** Cuts are recommendations with rationale; the user approves.
   The distilled artifact is a new file; the original is preserved for diffing.
3. **Chesterton's Fence.** Never propose removing something whose reason for existing you do
   not understand. If you cannot tell *why* an element is there or *what depends on it*,
   **flag it** — do not cut it.
4. **Preserve correctness and behavior.** For code and specs, external behavior / the
   contract is held fixed unless the user explicitly agrees a capability is out of scope.
   Distilling never silently drops a requirement or changes what code does.
5. **Concise ≠ lossy.** The goal is signal-to-noise, not a word count. Cutting essence to
   hit a length target is a failure, not a success. When a "cut" would remove something
   load-bearing, it is not a cut — it is damage.
6. **Name what is lost.** Every proposed cut carries a one-line "what would be lost" note.
   Honest subtraction states its cost.

## The essence test (apply to every element)

An *element* is a unit at the artifact's natural granularity: a section, paragraph, or
sentence; a requirement or acceptance criterion; a function, branch, parameter, or
abstraction; a diagram node, edge, or label. For each element, ask five questions:

1. **Purpose linkage** — does it serve the one purpose, or a different (or no) purpose?
2. **Subtraction test** — remove it in your head. Does the artifact still fulfil its
   purpose for this audience? If **yes** → cut candidate.
3. **Load-bearing / Chesterton's Fence** — does anything depend on it, and do you understand
   *why* it exists? If you can't tell → **flag, don't cut**.
4. **Audience necessity** — does *this* audience need it *now* to understand / decide / act?
   Or is it nice-to-have for a different audience, or for "someday"?
5. **Cost of keeping** — how much does it dilute the signal, add cognitive load, or create
   maintenance burden by staying?

Then classify the element:

- **Essential (E)** — load-bearing for the purpose. Keep and protect. Cutting it is damage.
- **Supporting (S)** — helps, but the artifact survives a lighter version. Do not cut —
  **trim, demote** (to an appendix / footnote / later phase), or **move**.
- **Inessential (I)** — the artifact fulfils its purpose without it. Cut candidate; tag it
  with a cruft category below.

## Cruft catalog (name what you cut)

Every Inessential element gets one of these names. Naming forces the judgment to be
defensible rather than a matter of taste. Full per-artifact detail is in `references/`.

- **Redundancy** — states what is already stated elsewhere; keep the strongest instance.
- **Gold-plating (YAGNI)** — capability / detail beyond what the purpose requires.
- **Accidental complexity** — a by-product of the chosen approach, not the problem itself.
- **Decoration / chartjunk** — ornament carrying no information (a decorated bullet, a
  gradient box, a restated heading). Structure-free adornment.
- **Filler / hedging** — words that do not change meaning: throat-clearing, reflexive
  qualifiers, transitional padding.
- **Speculative generality** — abstractions, hooks, config, or clauses for imagined futures.
- **Premature / wrong-altitude detail** — correct content at the wrong level or place
  (implementation detail in a vision doc; a design rationale inside a config value).
- **Scope creep** — content that serves a purpose *other* than the stated one.

## Workflow

Diagnose before cutting. Showing the diagnosis first is the highest-leverage step: it lets
the user catch a misread of the purpose before a single element is removed.

### Pass 0 — Scope & purpose (the anchor)

Identify the **artifact type** (prose/doc, spec/requirements, code, diagram — pick the
matching adapter in `references/`), the **primary language** (JA / EN / mixed), the **ONE
purpose**, the **audience**, and the **decision or action** the artifact must enable. If
purpose or audience is ambiguous, ask before proceeding. Load the matching adapter.

### Pass 1 — Articulate the irreducible core

Before touching anything, write the **irreducible core in 1–3 sentences**: what this
artifact must convey / do for its audience, stripped to the bone. Then name the **minimal
set of elements** that already deliver that core. This is the positive image of the
essence; everything outside it is a candidate for scrutiny. Forcing this first prevents
"trim a little everywhere" and makes the cuts principled.

### Pass 2 — Inventory & classify

Walk every element. Apply the five-question essence test plus the adapter's
artifact-specific rules. Tag each **E / S / I**, and each I with a cruft category. Run
`scripts/distill_scan.py` (optional) to surface mechanical candidates — repeated lines, hedge
words, over-long sentences, orphaned sections — but the script only *flags*; you judge.

### Pass 3 — Distillation Ledger & confirm

Present the ledger (format below): the irreducible core first, then the classified
elements, the proposed cuts with "what would be lost", and the flagged items. Get approval.
Batch obvious filler for a single yes; every cut that removes a distinct idea, a
requirement, a capability, or reorders emphasis is confirmed individually.

### Pass 4 — Produce the distilled artifact (or hand off)

Apply approved cuts into a **new** file (never destroy the original). Then route the rest:

- code → the actual edit belongs to **/simplify** or **/code-review**; this skill delivers
  the *scope decision* (which capability/abstraction is inessential), not the refactor.
- diagram → hand the redraw to **document-figures**.
- rearrange-only remainder → **doc-refactor**.
- a separate short derivative (keep the original whole) → **document-summary**.

### Pass 5 — Verify

Confirm the irreducible core still stands in the distilled version; every cut has a
rationale and a "what would be lost"; no flagged item was silently removed; behavior /
requirements / facts are intact. List anything you flagged but did not cut.

## Output: the Distillation Ledger

```
## Distilled against
Purpose: <the one purpose>   Audience: <who>   Enables: <decision/action>

## Irreducible core
<1–3 sentences>

## Ledger
| # | Element                | E/S/I | Cruft category       | Load-bearing? | Recommendation      |
|---|------------------------|-------|----------------------|---------------|---------------------|
| 1 | §Background para 2     | I     | redundancy           | no            | cut                 |
| 2 | NFR "99.999% uptime"   | I     | gold-plating         | no            | cut (→ Could, later)|
| 3 | Retry helper           | S     | —                    | yes           | keep; inline caller |
| 4 | Legacy compat branch   | ?     | —                    | unknown       | FLAG (why is it here?)|

## Proposed cuts — what would be lost
- Cut #1: removes the restated context; lost: nothing (duplicated in §Intro).
- Cut #2: drops the five-nines target; lost: an aspirational SLA — confirm it isn't contractual.

## Flagged (not cut)
- #4 Legacy compat branch: cannot determine what depends on it. Chesterton's Fence — confirm before removing.
```

## Boundaries with sibling skills

- **doc-refactor** — rearranges and de-duplicates while preserving *all* meaning. If the
  fix is "reorganize", not "remove", that is doc-refactor. Natural chain: distill decides
  what stays → doc-refactor arranges it.
- **doc-review** — diagnoses substantive weakness (thin evidence, missing counterargument).
  It adds nothing and cuts nothing; this skill only subtracts.
- **/simplify, /code-review** — perform the code edit and hunt bugs. This skill decides, at
  the scope/design level, *which* capability or abstraction is inessential; hand them the change.
- **document-summary** — produces a *separate* condensed derivative and leaves the source
  intact. This skill improves the source artifact itself by subtraction.
- **document-figures** — extracts/redraws diagrams. This skill decides what a diagram must
  convey and what to strip; document-figures does the drawing.
- **ai-tell-reducer / humanize-prose** — remove stylistic "AI tells". Distilling is about
  substance and scope, not voice. Filler removal overlaps at the sentence level; anything
  beyond a sentence (sections, requirements, features) is this skill's domain.

## Language

Match the artifact's language in all output. For Japanese artifacts, the ledger, the
irreducible core, and rationales are written in Japanese; the E/S/I tags and cruft
category names may stay in the shared vocabulary above for consistency.
