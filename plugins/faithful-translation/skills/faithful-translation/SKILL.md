---
name: faithful-translation
description: Produces source-faithful translations across any language pair with a parallel sentence ledger for verification, terminology preservation, register matching, and translator's notes
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Translation output language follows the user's instruction.

# Faithful Translation Expert

Produces translations that preserve source meaning, register, structure, and stance — with a verifiable parallel ledger linking every target sentence to its source sentence.

**Out of scope**: summarization or compression. If the user wants a shorter version, route them to the `document-summary` skill (or chain: faithful translation → summary).

## Core Principles

1. **Faithfulness first.** Preserve meaning, register, hedges, and stance over fluency when they conflict — but pursue both.
2. **Parallel ledger is mandatory.** Every target sentence maps to a source sentence (or explicit merge/split note). The ledger is the verification artifact.
3. **No additions, no omissions, no shifts.** If a hedge ("may", "perhaps", "ある程度") exists in the source, it must exist in the target. Do not "improve" the source by clarifying or smoothing.
4. **Cultural mediation only when necessary, with a translator's note.** Idioms and culture-bound terms get adapted only when literal translation breaks meaning; mark the choice in a note.
5. **Terminology consistency.** Build a glossary up front; one source term → one target term throughout (unless context requires variation, which is documented).
6. **Preserve structure.** Section/heading hierarchy, paragraph boundaries, list structure, citation style, code blocks, and quote attribution are kept intact unless the user explicitly asks otherwise.

## Workflow

| Step | Action | Output |
|---|---|---|
| 1. Intake | Capture: source language, target language, domain, audience, register (formal/casual/legal/academic), purpose (publish / internal / reference), special instructions (e.g., keep proper nouns in original) | Brief summary of constraints |
| 2. Glossary | Extract technical terms, named entities, acronyms; decide target-language equivalents and translation policy (translate / transliterate / keep original) | Term table |
| 3. Pass 1: literal translation | Sentence-by-sentence translation; build parallel ledger; flag uncertain choices | Draft + ledger |
| 4. Pass 2: fluency review | Re-read target text alone for naturalness; tighten without changing meaning | Polished draft |
| 5. Verification | Walk the ledger end-to-end: every source sentence has a target; no additions; hedges preserved; terminology consistent | Verification report |
| 6. Translator's notes | Document any cultural mediation, ambiguous source readings, or structural decisions | Notes block |
| 7. Final output | Translated document + glossary + ledger + notes | Deliverable |

## Parallel Ledger Schema

The ledger is the integrity check for the translation. Required for every project.

```markdown
| #   | Source                                  | Translation                              | Note                          |
|-----|-----------------------------------------|------------------------------------------|-------------------------------|
| 1   | <source sentence 1>                      | <target sentence 1>                       |                               |
| 2   | <source sentence 2>                      | <target sentence 2 + 3 (split)>           | Split for readability          |
| 3-4 | <source sentences 3 + 4 (merged)>        | <target sentence 5>                       | Merged; source separately short |
| 5   | <idiom or culture-bound>                 | <adapted target>                          | Adapted; literal would mislead |
```

Conventions:
- One row per source sentence, even when split or merged in the target. Note the operation.
- Keep the source verbatim. The ledger is auditable evidence.
- Notes column for: split / merge / adaptation / ambiguity / terminology choice / register adjustment.

Detail: `references/translation-fidelity.md`.

## Glossary Format

```markdown
| Source term     | Target term         | Policy        | Rationale                              |
|-----------------|---------------------|---------------|----------------------------------------|
| machine learning | 機械学習            | Standard term | Established Japanese technical term    |
| transformer     | Transformer         | Keep original | Proper noun for the architecture       |
| OECD            | OECD                | Acronym kept  | Globally recognized; first occurrence expanded |
| bottom line     | 結論                 | Adapted       | Literal "底線" misleads in Japanese    |
```

## Quality Rubric

| Dimension | Strong | Adequate | Weak |
|---|---|---|---|
| **Fidelity** | All claims, hedges, stance preserved; no additions/omissions | Minor hedge softening | Stance shifted; details added or dropped |
| **Register match** | Tone and formality match source | Mostly matches | Casual source rendered formally (or vice versa) |
| **Terminology** | Consistent glossary application | One or two slips | Inconsistent; readers confused |
| **Fluency** | Reads naturally in target language | Occasional awkwardness | Translationese throughout |
| **Cultural appropriateness** | Idioms / references handled with notes where needed | Mostly handled | Literal translations of idioms |
| **Verifiability** | Complete ledger; verification clean | Ledger present, minor gaps | No ledger or ledger incomplete |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| **Translator's gloss inside the text** — adding clarifying phrases not in source | Distorts source; reader can't distinguish author from translator | Move to a translator's note; keep the body clean |
| **Hedge stripping** — "may" → "is", "ある程度" → "fully" | Misrepresents author's confidence | Match the source's hedge level word-for-word |
| **Literal idiom translation** — "kick the bucket" → "バケツを蹴る" | Confuses readers | Equivalent idiom, paraphrase, or note |
| **Register drift** — formal academic source rendered casually (or vice versa) | Audience perceives wrong tone | Re-read for register; adjust word choice |
| **Inconsistent terminology** | Reader assumes different meaning | Glossary lock-in |
| **Smoothing source ambiguity** | Source ambiguity may be deliberate | Preserve ambiguity; flag in note |
| **"Improving" source logic** — fixing what looks like an error | Translation should not editorialize | Translate as-is; note any error in translator's note |
| **Filling gaps** — adding context the source assumes the reader knows | Hallucinated content | If essential for target audience, add as a note, not in the body |
| **Inconsistent named-entity handling** | Reader cannot follow the same entity | Decide policy per entity in the glossary; apply throughout |
| **Skipping the ledger** | No verification; faithfulness unauditable | Ledger is mandatory; reject the deliverable without it |

## Deliverable Format

```markdown
# Translation: <document title>

**Source language**: …  **Target language**: …
**Domain**: …  **Audience**: …  **Register**: …
**Date**: …

---

<translated document body, structure preserved>

---

## Glossary
<term table>

## Translator's Notes
1. <note 1: cultural adaptation in §2>
2. <note 2: ambiguous source phrasing in §4 — interpretation chosen>
…

## Parallel Ledger
<full table>

## Verification Report
- [ ] Every source sentence has a target (or explicit merge/split note)
- [ ] No additions found
- [ ] No omissions found
- [ ] Hedges preserved
- [ ] Terminology consistent with glossary
- [ ] Register matches source
- [ ] Structure (headings, lists, citations, code blocks) preserved
```

## Iteration Modes

| Mode | When to use |
|---|---|
| **Glossary first** | Highly technical source; lock terminology before drafting |
| **Sentence-by-sentence** | Default; produces ledger as a byproduct |
| **Pass 2 only** | User has a draft translation; review for fidelity, register, terminology |
| **Adapt** | User explicitly wants domestication (e.g., marketing copy); make adaptation choices explicit in notes |
| **Back-translation check** | High-stakes texts (legal, medical); back-translate the target and compare |

## References (consult when relevant)

- `references/translation-fidelity.md` — fidelity principles, register, terminology, named entities, hedges, idioms, common pitfalls
- `references/source-types.md` — translation conventions per document genre (academic / business / news / legal / technical / regulatory)
