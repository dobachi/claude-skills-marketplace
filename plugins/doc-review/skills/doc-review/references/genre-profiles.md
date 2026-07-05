# Genre profiles

A document is only "good" relative to its **genre** and **goal**. The same prose is
a strong meeting record and a failed proposal. Load the profile for the genre
established in Pass 0; it tells you which dimensions carry the most weight and the
failure that genre is most prone to. Weights are guidance, not a formula — a blocker
in a low-weight dimension is still a blocker.

Legend: dimensions are numbered as in `dimensions.md` (1 argument, 2 structure,
3 evidence, 4 assumptions, 5 completeness, 6 audience, 7 clarity, 8 consistency).

---

## Proposal / recommendation / pitch
**Goal:** get a decision-maker to say yes (or no) with confidence.
**Heaviest:** 2 (answer up front), 1 (argument), 5 (counterargument, cost, risk),
3 (evidence for the load-bearing claim).
**Most prone to:** burying the ask; a one-sided case with no risks or alternatives;
the pivotal number unsupported. If the reader can't find *what you want* and *what it
costs* in the first screen, that's usually finding #1.

## Spec / RFC / design doc / ADR
**Goal:** let an implementer build the right thing, and a reviewer find the flaw
before it's built.
**Heaviest:** 5 (edge cases, failure modes, alternatives considered), 4 (assumptions
& constraints), 8 (consistency of the described behaviour), 1 (does the design meet
the requirement).
**Most prone to:** the happy path only; "alternatives considered" missing or
strawmanned; an assumption about scale/load/ownership left implicit; the design and
the stated requirement drifting apart. For an ADR specifically: is the *decision*,
its *context*, and the *rejected options* each actually present?

## Academic paper / research writeup
**Goal:** convince a skeptical expert that the claim is true and novel.
**Heaviest:** 1 (do results support the claim), 3 (evidence & method), 5 (limitations,
threats to validity, related work), 8 (abstract vs body consistency).
**Most prone to:** claims broader than the results; missing limitations / threats to
validity; related work that doesn't engage the nearest prior art; an abstract that
promises more than the paper delivers. Overclaiming is the default failure — hold the
conclusion to exactly what the evidence reaches.

## Business memo / report / status update
**Goal:** inform a busy reader and, often, prompt an action.
**Heaviest:** 2 (BLUF — bottom line up front), 6 (right altitude for the exec),
7 (clarity), 5 (the "now what").
**Most prone to:** narrating activity instead of stating outcome and ask; too much
detail for the altitude; no clear action or owner. "We did X, Y, Z" with no "so the
decision is / we need" is the classic miss.

## Documentation / how-to / reference
**Goal:** let a reader accomplish a task or find an answer without the author present.
**Heaviest:** 6 (audience & prerequisites), 2 (findability, task order), 7 (clarity,
unambiguous steps), 5 (the failure/edge case the reader will actually hit).
**Most prone to:** assuming context the reader lacks (undefined prereqs); steps out
of the order the reader performs them; the common error case undocumented; "obvious"
gaps between steps where the reader gets stuck.

## Meeting minutes / record / log
**Goal:** be an accurate, retrievable record — *not* an argument.
**Heaviest:** 8 (consistency with what happened), 5 (decisions & action items with
owners captured), 7 (clarity).
**Most prone to:** decisions and owners buried in narrative or missing; editorializing
that turns a record into a position. Here, do **not** apply proposal/paper standards —
chronological and complete beats answer-first. Structure findings that would be valid
for a proposal are usually *invalid* here.

## Blog post / essay / LinkedIn
**Goal:** hold a general reader's attention and land one idea.
**Heaviest:** 2 (hook and through-line), 1 (the core claim actually earned),
6 (general-reader altitude), 7 (clarity).
**Most prone to:** no single clear takeaway; a hook the body doesn't pay off;
assumed insider context; padding around one thin idea.

---

## Cross-genre note
When the author's stated goal and the genre's default pull apart, **the stated goal
wins** — review against what they told you they're trying to do (Pass 0), and if the
genre convention would serve that goal better, that mismatch is itself a finding.
