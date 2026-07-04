# Structure Principles

Background for diagnosing and refactoring document structure. Read during Pass 1–2. These are
lenses for *diagnosis*, not licenses to rewrite: they tell you what "good structure" looks
like so you can move the author's existing content toward it without changing the content.

## Reverse outline (逆アウトライン / post-draft outline test)

The primary diagnostic. After a document exists, reconstruct its outline by writing **one
sentence per section describing what the section actually does** — deliberately ignoring the
heading's promise. Then read the skeleton on its own:

- If two lines describe the same job → **redundancy** (→ Merge Duplicates / Extract Common).
- If the skeleton doesn't tell a coherent story top-to-bottom → **structure problem** (→
  Reorder / Split / Merge).
- If a line contradicts its heading → **heading–content mismatch** (→ Align Heading).

This is more reliable than reading top-to-bottom because it strips away transition words and
formatting that make a disorganized document *feel* organized.

## Pyramid principle (Barbara Minto)

For argumentative / recommending documents (proposals, analyses, decision memos):

1. **Answer first.** Lead with the conclusion/recommendation, then support it. Busy readers
   want the result before the derivation. (Counter-intuitive for those trained on scientific
   papers, which build to the conclusion — hence a frequent structural fix.)
2. **Group and summarize.** Each idea is a summary of the ideas grouped beneath it; supporting
   points cluster under the main claim (roughly 3 per group is comfortable).
3. **Order logically.** Within a group, order by structure, importance, or sequence — and keep
   members at the same level of abstraction.

**When NOT to recommend answer-first:** chronological records (meeting minutes, changelogs,
incident timelines), narrative/teaching pieces where discovery is the point, and reference
material. Use genre to decide **what to recommend**, not to reorder automatically — every
reordering is proposed and confirmed with the author (see the workflow's Pass 3). Match the
structure to the genre; don't impose the pyramid everywhere.

## MECE (Mutually Exclusive, Collectively Exhaustive)

A test for how a topic is divided into sections/points:

- **Mutually Exclusive** — sections don't overlap. Overlap *is* redundancy; it's the thing
  Merge Duplicates / Extract Common Point removes.
- **Collectively Exhaustive** — no gap in the coverage the document set out to provide. A gap
  is **substantive** — you **flag** it (the author must fill it); you never invent the missing
  content to make the set look complete.

So MECE splits neatly onto the safety levels: fixing overlap is refactoring; filling gaps is
authoring.

## Paragraph and heading hygiene

- **One idea per paragraph.** A paragraph doing several jobs is a Split candidate.
- **Descriptive, parallel headings.** Headings should state the section's content in keywords
  and share grammatical form across siblings (all noun phrases, or all imperatives).
- **Shallow hierarchy.** Prefer at most a few heading levels; unintended jumps (H2→H4) are
  usually accidental and safe to normalize.

## Structural failure modes of AI-co-written text

The specific patterns to hunt for — these are why documents drift when drafted with an AI over
several turns:

- **Cross-section restatement.** The same concept re-explained in "Background," "Benefits,"
  and "Best practices," each in slightly different words. → Merge Duplicates / Extract Common.
- **Cosmetic transitions.** Furthermore / Moreover / さらに / また opening paragraphs that
  aren't actually connected. The connective simulates cohesion the logic doesn't have. →
  Collapse Cosmetic Transitions.
- **Heading–content drift.** A heading written for the intended content, but the content
  wandered. → Align Heading.
- **List padding / triadic bullets.** Points expanded to a tidy three even when there are
  really one or two distinct ideas. → Cut Padding (merge-three-into-one test).
- **Hedge pile-up.** Stacked qualifiers that blur the claim. → Trim Hedge Pile-up (keeping the
  author's real level of certainty).
- **Uniform rhythm.** Every paragraph the same length and shape, which flattens emphasis. A
  weak signal on its own; use it only to notice Split/Merge candidates, not as a reason to
  rewrite sentences.
- **Buried conclusion.** The actual recommendation sitting mid-document under a mild heading.
  → Reorder: Answer-First.

## A caution on de-duplication across a document *set*

Within a single document, repeating the same idea is almost always noise to remove. But the
"don't repeat yourself" instinct from code does **not** fully transfer to documentation:
across a *set* of documents, some context is deliberately repeated so a reader landing in the
middle isn't lost. This skill refactors **one document at a time**, so treat internal
repetition as a defect — but if the author says a passage is intentionally duplicated for
standalone readability (e.g. an abstract that restates the conclusion by design), respect
that and leave it.
