---
name: doc-review
description: >-
  Critical, read-only review of a prose document — it hunts for the substantive
  weaknesses (unsound argument, buried conclusion, thin evidence, unstated
  assumptions, missing counterargument, audience mismatch, internal contradiction)
  and returns a prioritized findings report the author decides on, WITHOUT editing
  the text. The prose counterpart of /code-review. Use when the user says "review
  this doc / proposal / spec / paper / report", "critique this", "poke holes",
  "what's weak here", "査読して", "文章レビュー", "ドキュメントレビュー",
  "レビューして", "指摘して", "穴を探して", "この論理は通っているか". Read-only and
  diagnostic by contract: it never rewrites (hand off to doc-refactor), never
  verifies facts against sources (hand off to verify-content / evidence-check),
  never restyles or de-AIs prose (ai-tell-reducer / humanize-prose), never
  summarizes (document-summary). Bilingual — Japanese and English.
---

# Doc Review

## Core idea: review, don't touch

Reviewing a document means forming and reporting **judgment** about it — what is
weak, what is missing, what a reader will misunderstand — while leaving the text
**exactly as the author wrote it**. This is the prose counterpart of `/code-review`:
find problems, rank them, explain them, propose a direction, and let the author
decide. You do not edit the document. Not one sentence.

That read-only contract is the whole point, and it is what separates this skill
from its neighbours:

| skill | default action | this skill's boundary |
|-------|----------------|-----------------------|
| **doc-review** (this) | **report findings, change nothing** | — |
| doc-refactor | rewrites structure, preserves meaning | you diagnose; if the author accepts structural fixes, hand off to doc-refactor to apply |
| verify-content / evidence-check | verify facts & citations vs sources | you *flag* a claim as unsupported; you do not go verify it |
| ai-tell-reducer / humanize-prose | rewrite AI-sounding prose | you *note* a voice/tell problem; you do not restyle |
| document-summary | produce a summary | you review; you do not summarize |

When a finding's proper fix belongs to another skill, **name that handoff in the
report** — do not do its job.

## What makes this worth more than "review this"

Any model, given "review this doc," will emit agreeable, generic, nitpicky feedback
("consider adding more detail," "great structure!"). That output is worthless. This
skill earns its keep only by refusing to produce it. Every finding must clear one
bar:

> **The finding test.** State the concrete consequence for a *specific reader*. If
> you cannot name who is misled, blocked, or unconvinced, and where, it is taste —
> drop it.

Two failure modes to actively suppress:

- **Sycophancy** — praise, hedged suggestions, "you might consider." Not a review.
  Report what is *wrong*, plainly. Praise only to mark a strength the author should
  protect during revision, never as filler.
- **Nitpicking** — comma-level, taste-level, or "I'd have phrased it differently"
  notes dressed up as findings. A sharp editor flags what changes the reader's
  understanding or the document's success, and stays silent on the rest.

Ground every finding in the text: quote the sentence or name the section. A finding
with no anchor is a hallucinated one.

## The dimensions (rubric)

Sweep these, weighted by genre (`references/genre-profiles.md`). Details, and a
worked good-vs-bad finding for each, are in `references/dimensions.md`.

1. **Argument soundness** — do the claims follow? Non-sequiturs, circular reasoning,
   correlation-as-cause, conclusions the evidence doesn't reach.
2. **Structure & altitude** — is the answer up front, or buried under preamble? Do
   sections deliver what their headings promise? Is the through-line followable?
3. **Evidence sufficiency** — is each load-bearing claim backed? Mark unsupported
   assertions (flag; verify-content confirms whether the support *exists*).
4. **Unstated assumptions** — what must the reader already believe for this to hold?
   Surface the load-bearing ones the author left implicit.
5. **Completeness & counterargument** — the missing case, the obvious objection not
   addressed, the alternative not considered, the "so what / now what" left open.
6. **Audience fit** — right altitude, jargon, and prior-knowledge assumptions for
   the *stated* reader? Too much or too little for who will actually read it.
7. **Clarity** — sentences a reader must re-read, ambiguous referents, undefined
   terms, buried qualifiers that flip a claim's meaning.
8. **Internal consistency** — a later section contradicting an earlier one; a number,
   term, or definition used two ways.

## Workflow

### Pass 0 — Scope (ask, don't assume)
Establish: document **genre**, **intended reader**, **the author's goal for the
document** (persuade? specify? decide? record?), and language. If the author's goal
is unstated and unguessable, ask one question — you cannot review fitness for a
purpose you don't know. Load the matching genre profile.

### Pass 1 — Read as the target reader
Read once, straight through, *as the intended reader*, and write down the single
takeaway you actually leave with. If that is not the takeaway the author intended,
that gap is often finding #1 — and no line-level note matters more than it.

### Pass 2 — Dimension sweep
Go through the rubric and collect **candidate** findings. Be greedy here; do not
self-censor yet. Anchor each to a quote/section as you go.

### Pass 3 — Adversarially verify your own findings
This pass is what makes the review trustworthy. For each candidate, argue the other
side: *is this real, or am I nitpicking / being agreeable / misreading?* Apply the
finding test. **Drop** any candidate that fails. For a review where much rides on
being right (a paper, a high-stakes proposal), spawn independent sub-agents to
attack the findings and keep only those that survive. A short list of sharp findings
beats a long list of soft ones.

**Findings are discovered, not allocated.** If a document is genuinely strong, the
honest result is few findings — or none above Minor — and a verdict that says so.
That is a *good* review, not a failed one. Never manufacture a Blocker or Major to
justify the effort: an invented finding is false criticism, which destroys the
author's trust faster than a missed one. When the sweep comes up empty, report that
plainly and stop.

### Pass 4 — Rank and report
Order by severity. Write the report (below). List handoffs. Do **not** edit the doc.

## Findings & severity

Each finding:
- **dimension** · **severity** · **location** (quote or section)
- **problem** — the concrete reader-failure (the finding test)
- **why it matters** — impact on the reader or the document's goal
- **direction** — how the author *could* fix it: name **what** to change and **why**.
  The moment you write the *replacement sentence itself*, you've crossed into
  rewriting (doc-refactor's job) — stop at the direction.
- **confidence** — how sure you are it's real (be honest; low-confidence findings
  are allowed if labelled, but never padding)

Severity:
- **Blocker** — the document fails its goal as written (reader reaches the wrong
  conclusion, the core argument doesn't hold, the decision can't be made from it).
- **Major** — a reader is materially misled, unconvinced, or slowed on a key point.
- **Minor** — real but small; worth fixing, won't sink the document.

## Deliverable — the review report (read-only)

```markdown
# Review — <doc>  (<genre>, reader: <who>, goal: <goal>)

**Verdict:** <1–2 sentences: does it meet its goal as written? the single biggest thing.>

**Reader takeaway (Pass 1):** <the takeaway you actually left with> — <matches / diverges from intent>

## Findings (most severe first)
### [Blocker] <title>  · <dimension>
- **Where:** "<quote>" / §<section>
- **Problem:** <who is misled/blocked, and how>
- **Why it matters:** <impact>
- **Direction:** <how they could fix it — not applied>
- **Confidence:** <high/med/low>

### [Major] …

## Strengths to preserve
<only genuine, specific strengths the author should not lose in revision>

## Handoffs
- Structural fixes accepted above → **doc-refactor**
- Unsupported claims (F<n>, F<m>) → **verify-content / evidence-check**
- Voice / AI-tell (F<k>) → **ai-tell-reducer**
```

Then stop. Applying anything is a separate, author-approved step.

### A worked finding (what "sharp" looks like)

The template is empty; this is a filled instance, so the bar is concrete. Target: a
one-page proposal recommending a vendor migration.

```markdown
# Review — Migrate billing to Vendor X  (proposal, reader: VP Eng approving spend, goal: get a yes/no)

**Verdict:** The recommendation is defensible but unreachable — the ask and its cost
are buried on page 2, and the one number the whole case rests on is unsupported. As
written, a skimming approver stalls before the decision.

**Reader takeaway (Pass 1):** "The team likes Vendor X." — diverges from intent (the
author wants a funded migration decision, not a preference).

## Findings (most severe first)
### [Blocker] The load-bearing cost claim has no source · evidence
- **Where:** "Vendor X will cut billing incidents by 70%."
- **Problem:** This 70% is the entire justification, but nothing backs it. The first
  thing a skeptical VP probes is exactly this figure; with no source, the meeting ends
  here and the decision is deferred.
- **Why it matters:** If the number is wrong or unfounded, the proposal collapses — and
  it's the single most load-bearing claim in the document.
- **Direction:** Cite the incident data behind the 70%, or soften the claim to what the
  evidence actually supports. (Whether the source is valid → verify-content.)
- **Confidence:** high
```

Note what makes it sharp: it names a *specific reader* (the VP), the *exact moment*
they're lost (the unsourced number), and the *consequence* (deferred decision) — not
"the evidence could be stronger."

## Anti-patterns

- **Editing the document.** The instant you rewrite a sentence you are not reviewing.
- **Praise as filler / sycophancy.** "Strengths to preserve" is for real, load-bearing
  strengths, not to soften the review.
- **Nitpick lists.** Twenty comma notes hide the one blocker. Cut to what matters.
- **Findings with no anchor.** Every finding quotes or points to text.
- **Doing the handoff's job** — rewriting (doc-refactor), verifying facts against
  sources (verify-content), restyling (ai-tell-reducer). Flag and hand off.
- **Reviewing against an unknown goal.** Fitness is relative to purpose; get it first.
- **A uniform checklist across genres.** A PRD and a paper fail differently
  (`references/genre-profiles.md`).

## References
- `references/dimensions.md` — each rubric dimension in depth, with a good-vs-bad
  finding and the tells that surface it.
- `references/genre-profiles.md` — per-genre weighting and the failure each genre is
  most prone to (proposal, spec/RFC/ADR, academic paper, business memo, docs, minutes).
