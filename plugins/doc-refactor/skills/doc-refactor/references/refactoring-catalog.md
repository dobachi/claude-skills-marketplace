# Refactoring Catalog

A catalog of document-refactoring operations, in the spirit of a code refactoring catalog:
each has a name, a trigger (when it applies), a safety level, the procedure, and a
before/after. **Safety levels** map to the workflow:

- **mechanical** — meaning-preserving; apply directly.
- **structural** — moves/merges content; confirm with the author first.
- **substantive** — would change what the text asserts; **flag only, never apply.**

The golden rule across all operations: **no distinct claim, fact, or figure may be lost.**
When an operation removes text, verify the removed text carried no unique information; if it
did, fold that information into what remains.

---

## 1. Merge Duplicates（重複統合） — mechanical / structural

**When:** two passages assert the same thing (often the same idea reworded in a later
section — a classic AI-co-writing artifact). Two reverse-outline lines describe the same job.

**Procedure:** keep the clearer/stronger passage; delete the other. Before deleting, scan the
weaker one for any unique detail, caveat, example, or citation and fold it into the survivor.
If the duplicates live in different sections, this becomes **structural** (a move) — confirm.

**Before:**
> § Background: The framework improves interoperability by decoupling schema from transport.
> … § Benefits: A key benefit is that interoperability improves because schema is decoupled
> from transport.

**After:**
> § Background: The framework improves interoperability by decoupling schema from transport.
> § Benefits: (removed the restatement; kept any benefit not already stated in Background.)

---

## 2. Extract Common Point（共通項の抽出） — structural

**When:** the same idea is threaded through several sections in fragments, so no single place
states it and the reader reassembles it themselves.

**Procedure:** state the shared point **once**, in the most logical location (often a lead or
a dedicated short section), and let the other sections reference it instead of re-explaining.
Do not delete section-specific nuance — only the repeated general statement is consolidated.

---

## 3. Reorder: Answer-First（結論先出し） — structural

**When:** the conclusion, recommendation, or main answer sits at the bottom after a long
build-up. The reverse outline shows the payoff in the last line.

**Procedure:** propose promoting the answer to the top (pyramid principle), then let the
supporting material follow. Preserve any genuine narrative reason for suspense (a case study, a
chronological log) — not every document should be answer-first (see structure-principles.md).
**Always confirm before applying**, and never auto-decide from genre: use genre only to shape
the recommendation you present, then let the author choose. Because reordering shifts what the
reader meets first, it is never mechanical.

**Before:** intro → data → analysis → *therefore we should adopt X*.
**After:** *We should adopt X* → because (grouped supporting points) → details/data.

---

## 4. Reorder: Logical / Importance（論理・重要度順） — structural

**When:** supporting points appear in arbitrary order, or a list mixes levels of importance.

**Procedure:** order points by one explicit principle — logical dependency, importance
(most→least), or sequence (time/steps) — and keep them at one level of abstraction (MECE).
State nothing new; only rearrange. Confirm, since ordering signals emphasis.

---

## 5. Split Overloaded Section（肥大セクション分割） — structural

**When:** one section (or paragraph) does three unrelated jobs; the reverse-outline line needs
"and" twice to describe it. `diagnose.py` flags it as an over-long paragraph.

**Procedure:** split along the natural seams into sections/paragraphs that each do one job,
adding accurate headings (see Align Heading). Move no content out of the document.

---

## 6. Merge Thin Sections（過分割の統合） — structural

**When:** several tiny sections each carry a fragment that only makes sense together;
the structure is more scaffolding than content.

**Procedure:** combine fragments that share one job under a single heading. The opposite of
Split; use when granularity is too fine, not too coarse.

---

## 7. Align Heading（見出し整合） — mechanical

**When:** a heading promises one thing and the section delivers something adjacent but
different (e.g. "How to measure results" that actually explains *why* to measure).

**Procedure:** either rename the heading to match the content, or move the mismatched content
to where it belongs. Renaming is mechanical; moving is structural. Also make sibling headings
**parallel** in grammatical form (all noun phrases, or all imperatives — not mixed).

---

## 8. Cut Padding（水増し削除） — mechanical

**When:** filler that adds no information — restatements of the heading, "It is important to
note that…", triadic bullets padded to look complete, sentences that only announce what the
next sentence will say.

**Test (bullets):** try merging three bullets into one sentence without losing meaning. If you
can, the list was padded — merge it.

**Procedure:** cut the filler. Keep anything that carries a distinct fact, example, or caveat.
Padding removal is mechanical *only* when you are certain nothing unique is lost.

---

## 9. Collapse Cosmetic Transitions（装飾的接続の除去） — mechanical

**When:** every paragraph opens with さらに／また／加えて／Furthermore／Moreover／In addition,
but the paragraphs are not actually logically linked — the connective is decoration.
`diagnose.py` flags connective overuse.

**Procedure:** remove the cosmetic connective, or, if a real relationship exists, make it
explicit ("A, therefore B" / "A, but B"). Do not invent a logical link that is not there —
if the paragraphs are merely a list, present them as one.

---

## 10. Normalize Terminology（用語統一） — mechanical

**When:** the same concept appears under several names (e.g. "データ連携基盤 / コネクタ基盤 /
連携基盤"), which reads as drift and can look like distinct concepts. `diagnose.py`'s repeated-
term report helps spot these.

**Procedure:** pick one canonical term (ask the author if genuinely ambiguous), apply it
consistently, and note the choice in the change log. Never merge terms that actually denote
different things — verify they are synonyms in context first.

---

## 11. Trim Hedge Pile-up（冗長ヘッジの削減） — mechanical / substantive

**When:** stacked hedges dilute a sentence (〜と考えられる場合があるかもしれない / "it could
potentially be argued that…").

**Procedure:** reduce redundant hedging to a single, clear caveat **while preserving the
author's actual epistemic stance.** Removing *genuine* uncertainty is **substantive** — if the
author meant "this is tentative," keep exactly one hedge. Never make a tentative claim sound
certain, or vice versa.

---

## Deciding mechanical vs. structural vs. substantive

Ask: *does this change what the document asserts, or only how it is arranged?*

- Only arrangement, within one spot → **mechanical** (apply).
- Only arrangement, but moving content across the document / changing order → **structural**
  (confirm, because position carries emphasis).
- The assertion itself, its certainty, or its evidence → **substantive** (flag, never apply).

If you cannot tell, treat it as the more cautious level.
