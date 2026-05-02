---
name: document-summary
description: Produces structured summaries of documents and literature in Executive or Professional mode, with a mandatory source-grounded Claim Ledger and explicit Source vs Inference separation to prevent hallucinated content
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Output language can differ from source language.

# Document Summary Expert

Produces faithful, structured summaries of documents and literature. Every claim in the summary traces to a source span via the **Claim Ledger** — the mandatory verification artifact. Inferences not present in the source are confined to a separately labeled `[Inference]` block.

**Out of scope**: faithful translation without summarization (use `faithful-translation`). Multi-source synthesis or evidence verification against external sources (use `verify-content` or `evidence-check`).

## Core Principles

1. **Source-grounded.** Every claim in the summary maps to a source span (section / page / paragraph / quote). No claim ships without a ledger entry.
2. **Source vs Inference rigorously separated.** Anything not directly supported by the source goes in a clearly labeled `[Inference]` block, never mixed into the body.
3. **Preserve hedges and stance.** "May" is not "is"; "limited evidence suggests" is not "shows". The author's epistemic stance is part of what's being summarized.
4. **Negative space matters.** Note explicitly what the source does *not* address when relevant to the audience.
5. **Mode determines structure.** Executive uses Pyramid/BLUF and is decision-relevant; Professional preserves methodology, evidence, limitations, and counterclaims.
6. **Output language is user-specified.** Source can be any language; output can be any language. Cross-lingual summarization is supported natively.
7. **Self-verification is mandatory.** Before delivery, walk every output sentence and confirm it traces to a ledger entry (or is in the `[Inference]` block).

## Modes

### Executive Mode

- **Audience**: decision-makers, executives, sponsors, busy stakeholders.
- **Length**: ~1 page (300–600 words).
- **Structure**: BLUF — bottom line in the first sentence; Minto Pyramid for supporting points.
- **Content**: decision-relevant claims only. Methodology compressed to one line. No technical jargon without gloss.
- **Decisions and implications**: explicit. End with "what this means for the audience."
- **Citations**: section/page references in the ledger; rarely direct quotes in the body.

### Professional Mode

- **Audience**: domain practitioners, researchers, analysts, technical reviewers.
- **Length**: variable; typically 1–4 pages.
- **Structure**: depends on source genre — IMRAD-derived for empirical academic; SCQA or analytical for business; topic-organized for technical/regulatory.
- **Content**: methodology, evidence with effect sizes, limitations, counterclaims, scope conditions, glossary if needed.
- **Citations**: section/page references plus selected direct quotes for pivotal claims.
- **Negative space**: explicit section noting what the source does *not* address.

Selection guide: `references/structural-patterns.md`.

## Workflow

| Step | Action | Output |
|---|---|---|
| 1. Intake | Capture: source type, length, source language, target audience, mode (Executive / Professional), output language, length budget, any specific questions to answer | Brief summary of constraints |
| 2. Structural extraction | Identify sections, key claims, evidence, methodology, limitations, conclusions; build a structural map | Source map |
| 3. Build Claim Ledger | For every notable claim, record: source span, verbatim quote (if pivotal), confidence level, paraphrase | Ledger table |
| 4. Mode → structure | Pick the structural pattern for the mode + source genre (Pyramid for Executive; IMRAD-derived / SCQA / topic for Professional) | Outline |
| 5. Draft summary | Each output claim must reference a ledger entry. Draft in the target language directly | Draft |
| 6. **Self-verification pass** | Walk every output sentence: does it trace to a ledger entry? If not, mark `[Inference]` (and move to the inference block) or remove | Verified draft |
| 7. Inference block | Aggregate any inferences (synthesis, implication, expert reading) into a clearly labeled block, separate from the body | Inference block |
| 8. Negative space | Note what the source does NOT address (if relevant to the audience's likely questions) | Negative-space block |
| 9. Finalize | Headers, citations, ledger appendix, polish in target language | Deliverable |

## Claim Ledger (mandatory)

The Claim Ledger is the integrity artifact. Required for every summary.

```markdown
| ID    | Claim (in target language)                | Source span         | Verbatim?       | Confidence | Original (if pivotal) |
|-------|-------------------------------------------|---------------------|-----------------|------------|-----------------------|
| C-01  | The intervention reduced X by 18%         | §4.2, p.18, ¶2     | Paraphrase      | High       | "...18%"              |
| C-02  | Effect held only in subgroup A             | §4.3, p.19, ¶1     | Paraphrase      | High       |                       |
| C-03  | Authors hedge: "may not generalize"        | §6, p.24, ¶3        | Direct quote    | High       | "may not generalize"  |
| C-04  | Mechanism is hypothesized to be Z          | §5, p.21, ¶3        | Paraphrase      | Medium     | "we hypothesize..."   |
| I-01  | This implies portfolio rebalancing         | (inference)         | Inference       | —          | —                     |
```

Conventions:
- **C-** prefix for source-grounded claims; **I-** prefix for inferences.
- **Confidence**: High (explicit in source) / Medium (implicit; reasonable reading) / Low (heavy interpretation).
- **Verbatim**: Direct quote / Paraphrase / Aggregate (multiple spans → one claim).
- **Source span**: section, page, paragraph; or chapter/verse for sources structured that way.
- **Original (if pivotal)**: include the source-language quote for hedge-bearing claims, methodology, central findings.

Detail: `references/claim-ledger.md`.

## Self-Verification Protocol

Before delivery, run this pass. It is non-negotiable.

1. **Every output sentence → ledger entry?** If a sentence in the summary body does not trace to a `C-` ledger ID, either (a) move it to the `[Inference]` block as an `I-` entry, or (b) remove it.
2. **Hedges preserved?** Spot-check ledger entries — are hedge words ("may", "limited", "suggests") preserved in the paraphrase?
3. **Quantitative precision?** Numbers in the summary match the source (or explicitly rounded with the source value preserved in the ledger).
4. **Stance preserved?** If the source is hedged, cautious, or critical, does the summary read with the same stance?
5. **Negative space addressed?** If the audience would reasonably expect coverage of X and the source does not cover X, note it.
6. **No imported common knowledge.** Anything that "everyone knows" but is not in the source is either omitted or moved to `[Inference]`.

## Quality Rubric (6 axes)

| Dimension | Strong | Adequate | Weak |
|---|---|---|---|
| **Faithfulness** | Every claim traces to ledger; hedges preserved | Minor hedge softening | Hallucinated specifics; stance shifted |
| **Completeness** | Audience's key questions answered | Some gaps acknowledged | Missing pivotal claims |
| **Compression** | On budget; signal density appropriate to mode | Slightly over/under | Bloated or skeletal |
| **Structural fit** | Pattern matches source genre × mode | Pattern present but loose | Wrong pattern for the genre |
| **Audience fit** | Tone, depth, and decision-relevance match | Mostly fits | Mismatched (too technical for execs, or vice versa) |
| **Citability** | Ledger complete; citations resolvable | Ledger present, minor gaps | Ledger incomplete or absent |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| **Hallucinated specifics** — numbers, dates, methodology details not in source | Fabrication; readers cannot trust | Self-verification pass; if not in ledger, remove or move to `[Inference]` with caveat |
| **Stripped hedges** — "may" → "is", "limited evidence" → "evidence" | Misrepresents author's confidence | Preserve hedge words verbatim in paraphrase |
| **Generalized beyond source scope** — "in this study" → "in general" | Overclaims | Preserve scope conditions (population, setting, time) |
| **Imported common knowledge** — adding facts the summarizer "knows" | Source-grounding violated | Either omit or move to `[Inference]` block |
| **Conflated multiple sources** | Single-source summary contaminated | This skill is single-source; for synthesis use `verify-content` |
| **Source vs Inference mixed** | Reader cannot tell what's the author vs. the summarizer | Strict separation: `[Inference]` block always isolated |
| **Lost negative space** — reader assumes coverage that isn't there | Misleads by omission | Explicit "the source does not address X" line |
| **Lost author voice / stance** | Critical author rendered neutral; cautious author rendered confident | Preserve stance — quote pivotal hedged claims directly |
| **Cherry-picked supporting claims** | Counterclaims dropped; one-sided | Include limitations, counterclaims, dissenting findings |
| **Quote without context** | Misleading | Provide context in the ledger note column |
| **Skipping the ledger** | No verification possible | Ledger is mandatory; reject deliverable without it |
| **Over-compression in Professional mode** | Methodology and limitations lost | Match length budget to mode; Professional is not Executive |
| **Under-compression in Executive mode** | Decision-makers lose patience | 1 page max for Executive; cut to decision-relevant only |

## Deliverable Templates

### Executive Mode template

```markdown
# Executive Summary: <document title>

**Source**: <full citation>  **Date**: <date>  **For**: <audience>  **Mode**: Executive
**Source language → Output language**: <e.g., English → Japanese>

## Bottom line
<1-sentence headline takeaway>

## What the source establishes
- <claim 1> [C-01]
- <claim 2> [C-02]
- <claim 3> [C-03]

## Implication for <audience>
<1–3 sentences on the so-what>

## What the source does NOT address
<1–2 sentences on relevant negative space>

---

## Claim Ledger
<full table>

## Inferences
<I- entries — clearly separated from the body claims>
```

### Professional Mode template

```markdown
# Summary: <document title>

**Source**: <full citation>  **Mode**: Professional
**Audience**: <audience>  **Source → Output language**: <pair>

## Abstract
<3–5 sentence abstract>

## Context / Research question
<what gap this source addresses>

## Methodology
<approach, sample, design, limitations of design>

## Key findings
- <finding 1, with effect size if applicable> [C-0X]
- <finding 2> [C-0X]

## Evidence and analysis
<how the source supports its claims>

## Limitations and counterclaims
<what the source itself acknowledges or what is methodologically constrained>

## Conclusions
<author's stated conclusions, hedge-preserving>

## What the source does NOT address
<negative space relevant to the audience>

## Glossary (optional)
<technical terms with target-language equivalents>

---

## Claim Ledger
<full table>

## Inferences (clearly labeled)
<I- entries>
```

## Iteration Modes

| Mode | When to use |
|---|---|
| **Mode toggle** | Switch between Executive and Professional outputs from the same ledger |
| **Drill-down** | Audience requests deeper coverage of a specific claim — pull more from the source for that claim's ledger row |
| **Cross-lingual** | Source in language A, summary in language B — same workflow; ledger keeps source-language original quotes for pivotal claims |
| **Audience pivot** | Reshape an existing summary for a different audience (e.g., Professional → Executive) — re-apply structure step but preserve ledger |
| **Verification audit** | Re-run the self-verification pass on an existing summary; surface any unrooted claims |

## References (consult when relevant)

- `references/claim-ledger.md` — schema details, verification protocol, edge cases (implicit claims, aggregated claims, hedged claims, cross-lingual claims)
- `references/structural-patterns.md` — Minto Pyramid / IMRAD / SCQA / PREP / Decision Memo / BLUF / inverted pyramid — when to use each
- `references/source-types.md` — extraction priorities and structural conventions per genre (academic / business / white paper / news / book / regulatory / technical / systematic review)
