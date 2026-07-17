# Adapter: prose & documents

Applies the essence test to essays, memos, proposals, reports, READMEs, blog posts,
meeting notes, PR descriptions, and similar prose. Use with the five-question test in
`SKILL.md`.

## What "purpose" and "load-bearing" mean here

- **Purpose** = the one thing the reader should *understand, decide, or do* after reading.
  A proposal → approve/reject a decision. A README → get someone running the thing. Status
  notes → know what changed and what's blocked.
- **Load-bearing** = the thesis/answer, and the minimal chain of claims and evidence the
  conclusion actually rests on. Remove a load-bearing claim and the conclusion no longer
  follows.

## Articulating the irreducible core

Write the document's **thesis in one sentence** plus the **reader action** it enables. If
you cannot, the document has no essence yet — that is a `doc-review` finding (missing
thesis), not something to distill. Everything that does not support the thesis or the
action is under scrutiny.

## Reverse outline (fast diagnosis)

For each section, write **one sentence stating what it actually does for the reader** (not
what its heading promises). This exposes, at a glance:

- **Two sections doing the same job** → redundancy; keep the stronger.
- **A section serving a different purpose** → scope creep; cut or spin out.
- **A section that supports nothing above it** → orphan; likely inessential.
- **The answer sitting at the bottom** → not a cut, a *reorder*; hand to `doc-refactor`.

## Prose-specific cruft

| Category | What it looks like in prose |
|---|---|
| Redundancy | A second introduction; a summary that restates the body; the same point in §2 and §5. |
| Gold-plating | Caveats, edge cases, and background the audience doesn't need to act. |
| Filler / hedging | "It's worth noting that", "in order to", "basically", reflexive "I think / perhaps", throat-clearing openers, ceremonial closers ("in conclusion, …"). |
| Decoration | Bullet lists with no parallel structure; bold on non-key phrases; a heading that only restates the sentence under it. |
| Premature detail | Implementation minutiae in a vision doc; a full config dump where a link would do. |
| Speculative generality | "In the future we might…", hypothetical scenarios that carry no current decision. |
| Scope creep | A related-but-separate topic that deserves its own document. |

## Keep, even when tempting to cut

- A single concrete example that makes an abstract claim graspable — often the most
  load-bearing sentence in the section.
- A counterargument the thesis needs to answer. Removing it makes the argument *look*
  cleaner and *be* weaker.
- The one caveat that prevents a reader from acting wrongly.

## Trim vs cut vs demote (for Supporting content)

- **Trim** a padded sentence to its core clause.
- **Demote** useful-but-secondary detail to a footnote, appendix, or linked doc.
- **Move** a fact to the one place it is load-bearing; delete its other appearances.

## Handoffs

- Buried lede / wrong order but nothing to remove → `doc-refactor`.
- Weak or unsupported argument → **flag** as a `doc-review` matter; do not "fix" by cutting.
- Sentence-level style tics (em-dash spam, "delve", tricolons) → `ai-tell-reducer`.
- Need a short standalone version but keep the original → `document-summary`.
