# Review dimensions — in depth

Each dimension below has: what to look for, the **tells** that surface it, and a
**good vs bad finding** so the bar is concrete. The bad version always fails the
finding test (no named reader consequence, or it's taste); the good version names a
specific reader and what goes wrong for them.

---

## 1. Argument soundness
Do the stated conclusions actually follow from the stated premises?

**Tells:** "therefore / thus" bridging a gap the evidence doesn't cover; a single
example generalized to a rule; correlation described as cause; a conclusion broader
than the section that supports it; an "obviously" or "clearly" doing the work a
missing step should do.

- ✅ *Good:* "§3 concludes 'caching will cut p99 latency in half,' but the only data
  shown is average latency on a warm cache. A reader deciding whether to fund the
  work can't tell if the tail — the thing they care about — improves at all. The
  claim outruns its evidence."
- ❌ *Bad:* "The argument in §3 could be stronger." (No reader, no specific gap —
  taste.)

## 2. Structure & altitude
Is the conclusion reachable quickly, and does the document's shape match how the
reader needs to consume it?

**Tells:** the actual answer appears on page 3; a heading promises X and the section
delivers Y; long preamble before the point; a "background" section the reader must
hold in memory for pages before it pays off; the real recommendation hidden in a
mid-paragraph clause.

- ✅ *Good:* "The recommendation (adopt option B) first appears in the final
  paragraph of §5. An executive reader skimming for the decision will stop before
  reaching it and leave not knowing what you're asking for. The answer needs to be
  in the first screen."
- ❌ *Bad:* "Consider restructuring for better flow." (Which reader loses what,
  where? Unanchored.)

## 3. Evidence sufficiency
Is each load-bearing claim actually supported — and is the support the right *kind*?

**Tells:** numbers with no source; "studies show" / "it's well known"; a strong
causal or quantitative claim backed only by assertion; a citation that, read
closely, doesn't support the sentence it's attached to.

Flag the gap; you do **not** go verify whether the support exists — that's
verify-content / evidence-check. Your job is "this claim is carrying weight and
nothing here holds it up."

- ✅ *Good:* "'Most users abandon at this step' (§2) is the premise the whole
  proposal rests on, but no funnel data is cited. If that number is wrong the
  proposal collapses — it's the first thing a skeptical approver will probe."
- ❌ *Bad:* "Add more data." (Where, and why does it matter?)

## 4. Unstated assumptions
What must the reader already accept for the argument to work? Surface the
load-bearing implicit ones.

**Tells:** a recommendation that only makes sense under an unstated constraint
(budget, timeline, org structure); reasoning that assumes the reader shares the
author's context; a "we should X" that presumes a goal never stated.

- ✅ *Good:* "The whole plan assumes the team keeps its current headcount — never
  stated. A reader who knows a reorg is coming will read the timeline as fantasy.
  Make the assumption explicit so it can be challenged or protected."
- ❌ *Bad:* "There are some assumptions here." (Which one is load-bearing? What
  breaks?)

## 5. Completeness & counterargument
The missing case, the unaddressed objection, the alternative not considered, the
unanswered "so what / now what."

**Tells:** a one-sided case with no risks section; the obvious "why not just…"
never addressed; a recommendation with no cost or downside named; analysis that
stops before telling the reader what to *do*.

- ✅ *Good:* "The proposal never addresses the buy-vs-build alternative, which is
  the first question the steering committee asked last quarter. Its absence reads as
  either unaware or evasive; either way the proposal stalls there."
- ❌ *Bad:* "You could add a counterargument." (Which one, and what does its absence
  cost?)

## 6. Audience fit
Right altitude, vocabulary, and assumed prior knowledge for the *stated* reader.

**Tells:** deep implementation detail in a document for executives; undefined
domain jargon in a document for newcomers; re-explaining basics to experts; a
mismatch between the reader named in Pass 0 and the reader the prose actually
addresses.

- ✅ *Good:* "This is addressed to 'new team members' (Pass 0) but §4 assumes
  familiarity with the legacy billing model, undefined anywhere. A newcomer stops
  here. Either define it or link it."
- ❌ *Bad:* "Mind your audience." (Where does the mismatch bite?)

## 7. Clarity
Sentences that force a re-read, ambiguous referents, undefined terms, a qualifier
that quietly flips a claim.

**Tells:** "this/it/that" with no clear antecedent; a sentence you had to read
twice; a term introduced without definition and reused; a buried "not" or "unless"
that reverses the meaning of a key claim.

- ✅ *Good:* "'This makes the migration unnecessary' (§6) — 'this' could refer to
  either the new schema or the feature flag, and the two lead to opposite plans. A
  reader can't tell which you mean, and it's the pivotal sentence of the section."
- ❌ *Bad:* "Some sentences are hard to read." (Which, and does it change meaning?)

## 8. Internal consistency
A later section contradicting an earlier one; a number, term, or definition used two
ways.

**Tells:** the summary says one thing and the body another; a metric quoted as 40%
in §2 and 55% in §5; a term defined narrowly then used broadly; a recommendation
that conflicts with a constraint stated earlier.

- ✅ *Good:* "The executive summary says the launch is 'Q2'; the timeline in §5 puts
  GA in Q3. A reader quoting the summary will commit to a date the plan doesn't
  support. One of them is wrong."
- ❌ *Bad:* "Check for consistency." (Point to the specific collision.)

---

## The verification pass (why it exists)

Candidate findings from the sweep are *hypotheses*. Pass 3 turns each into: "would a
sharp editor say this to the author's face, and be right?" Argue the opposing side —
maybe the assumption *is* stated two paragraphs up; maybe that reader doesn't exist;
maybe you misread the referent. Kill what doesn't survive. This is the difference
between a review the author trusts and one they learn to ignore.
