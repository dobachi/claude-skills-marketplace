---
name: doc-refactor
description: >-
  Refactor prose documents — restructure and de-duplicate WITHOUT changing meaning,
  the way code refactoring preserves behavior. Use whenever a document (especially
  Markdown written together with AI) has grown redundant, lost its structure, has
  headings that no longer match their content, buries its conclusion, or repeats the
  same idea across sections. Triggers: "refactor this doc", "clean up the structure",
  "remove redundancy", "reorganize", "this got messy / bloated / lost the thread",
  "文章をリファクタリング", "構造を整理", "重複を削除", "冗長", "reverse outline", "逆アウトライン".
  Runs a diagnose-first workflow (reverse outline → issue inventory → confirm structural
  moves → refactor → change log) that preserves every claim, fact, figure, and the
  author's voice, and FLAGS substantive problems instead of silently fixing them. Use it
  even when the user only says the writing "feels bloated" or "lost the thread" after heavy
  AI editing. Not for translation, summarization, or fact-checking — it only re-shapes
  existing content.
---

# Doc Refactor

## Core idea: refactoring, not rewriting

Refactoring a document means improving its **structure** while preserving its **meaning** —
exactly like refactoring code preserves external behavior. The author (a human working with
AI) already decided *what to say*. This skill fixes *how it is arranged*: it removes
redundancy, restores structure, aligns headings with content, and orders ideas so a reader
can follow them — without inventing, deleting, or altering any actual content.

This distinction is the whole value of the skill. If you start "improving" the argument,
adding evidence, or smoothing the voice into something more generic, you have stopped
refactoring and started rewriting — which quietly destroys the author's work and their trust.
When in doubt, change less.

## Invariants — never violate these

Treat these as the document's "external behavior." A refactor MUST preserve all of them:

1. **Every distinct claim / assertion** the author made. Merging two *duplicate* claims is
   allowed; dropping a claim that carries unique meaning is not.
2. **Facts, figures, dates, names, citations, quotes, code, links.** Never edit these for
   style. Copy them verbatim.
3. **The author's stance and conclusions.** Do not soften, strengthen, or reverse them.
4. **The author's voice and register.** Refactoring rearranges sentences; it does not
   rewrite them into a house style. Reuse the author's own wording wherever possible.

When you find a **substantive** problem — a factual error, a logical gap, a weak or
unsupported argument, a missing piece — **flag it in the change log; do not fix it.** Fixing
substance is the author's job, and silently doing it hides the problem. This mirrors the
author's own verification-heavy workflow: surface issues, let them decide.

## Workflow

Always diagnose before touching the text. Showing the author the diagnosis first is the
single highest-leverage step — it lets them catch a misread before any edit happens.

### Pass 0 — Scope

Note the document type (blog post, technical memo, meeting minutes, spec, LinkedIn post…),
its primary language (Japanese / English / mixed), and the target medium. Different types
tolerate different structures — minutes stay chronological; a proposal wants answer-first.
Never edit in place destructively: the refactored version is a **new** artifact, and the
original is preserved so the author can diff.

### Pass 1 — Reverse outline (逆アウトライン)

Reconstruct the document's *actual* structure. For each section, write **one sentence stating
what the section really does** — not what its heading claims. Number them. This skeleton is
the diagnostic backbone; it makes the following visible at a glance:

- **Redundancy** — two lines that say the same job → merge/cut candidates.
- **Non-MECE** — overlapping sections (not mutually exclusive) or missing steps (not
  collectively exhaustive → gap; flag, don't fill).
- **Ordering** — the conclusion/answer sitting at the bottom instead of the top.
- **Heading–content mismatch** — the one-sentence reality differs from the heading's promise.

Present the reverse outline to the author before Pass 3.

### Pass 2 — Issue inventory

Classify every finding against the **refactoring catalog** (see
`references/refactoring-catalog.md`) and tag each with a safety level:

- **mechanical** — meaning-preserving and safe to apply directly (cut a padding sentence,
  collapse a cosmetic transition, unify a term).
- **structural** — moves or merges content across the document; **confirm with the author**
  before applying, because reordering can subtly shift emphasis.
- **substantive** — requires changing what the text asserts; **flag only, never apply.**

Run `scripts/diagnose.py` first to get mechanical candidates (see below), then apply
judgment on top — the script flags, you decide.

### Pass 3 — Plan & confirm

Summarize the planned operations. Apply mechanical ones; for structural ones, show the
proposed new order/merges and get a yes before executing. Keep this lightweight — a short
list the author can approve at a glance, not an interrogation.

**Reordering is always confirmed — never auto-applied.** In particular, do not silently
switch a document to answer-first (or any other order) based on a guess about its genre.
Genre only informs the *recommendation* you present ("this reads like a proposal, so I'd
suggest promoting the conclusion — shall I?"); the author decides. Reordering changes what a
reader encounters first and therefore what feels emphasized, so the author must see the
proposed order and approve it before you move anything. When unsure whether a change counts as
reordering, treat it as structural and ask.

### Pass 4 — Refactor

Apply the approved operations. While editing:

- Prefer the author's existing sentences; rearrange rather than regenerate.
- When merging duplicates, keep the stronger phrasing and fold in any unique detail from the
  weaker one so no information is lost.
- Preserve Markdown fidelity (heading levels, code fences, tables, links, callouts, footnotes).
- Fix heading hierarchy jumps (e.g. H2→H4) only when they are clearly unintended.

### Pass 5 — Verify & change log

Produce a **change log** that lists each change, the catalog operation it applies, and a
one-line rationale. Then run a **claim-preservation check**: confirm no distinct claim was
dropped, no fact altered, and list every item you **flagged but did not fix**. If you cannot
account for where a claim went, you removed too much — restore it.

## Mechanical helper: scripts/diagnose.py

A dependency-free (stdlib-only) detector. It **flags candidates; it never edits.** Run it at
the start of Pass 2:

```bash
python3 scripts/diagnose.py path/to/document.md            # human-readable report
python3 scripts/diagnose.py path/to/document.md --json      # machine-readable
```

It reports: the heading skeleton + hierarchy jumps; near-duplicate sentence pairs in two bands
— STRONG (likely restatement) and WEAK (looser echo to scan quickly), using character n-gram
Jaccard that works for JA and EN; sentence-initial connective frequency (cosmetic-transition
overuse); over-long paragraphs (split candidates); and the most-repeated terms (to spot
terminology drift). Every item is a *candidate* — you confirm or reject each with the
invariants in mind. The WEAK band trades precision for recall on purpose, so expect to reject
some of it.

## Refactoring operations (summary)

Full definitions, safety levels, and before/after examples are in
`references/refactoring-catalog.md`. Read it during Pass 2. The catalog:

1. Merge Duplicates（重複統合）· 2. Extract Common Point（共通項の抽出）· 3. Reorder: Answer-First
（結論先出し）· 4. Reorder: Logical / Importance（論理・重要度順）· 5. Split Overloaded Section
（肥大セクション分割）· 6. Merge Thin Sections（過分割の統合）· 7. Align Heading（見出し整合）·
8. Cut Padding（水増し削除）· 9. Collapse Cosmetic Transitions（装飾的接続の除去）· 10. Normalize
Terminology（用語統一）· 11. Trim Hedge Pile-up（冗長ヘッジの削減）.

For the underlying principles (pyramid principle, MECE, reverse outline, and the specific
structural failure modes of AI-co-written text), read `references/structure-principles.md`.

## Output format

Deliver three parts. Match the document's language (Japanese document → Japanese report).

1. **診断レポート / Diagnosis** — the reverse outline (before) + the issue inventory.
2. **リファクタリング済み文書 / Refactored document** — the new Markdown, original preserved.
3. **変更ログ / Change log** — operation-by-operation changes + the claim-preservation check
   + a "flagged but not fixed" list of substantive issues for the author to handle.

For a file input, save the refactored document as a new file (e.g. `*-refactored.md`) rather
than overwriting, and present both the report and the new file.

## Language handling

The document may be Japanese, English, or mixed. Diagnose and report in the document's
language. Japanese-specific care: split sentences on 。！？ and treat 「」『』（）as units;
watch for hedge pile-ups (〜と考えられる／〜する場合がある／〜ではないだろうか) and cosmetic
connectives (また／さらに／加えて／その上／なお) that add no logical link. Preserve the author's
level of formality (である体／ですます体) exactly — never convert between them.
