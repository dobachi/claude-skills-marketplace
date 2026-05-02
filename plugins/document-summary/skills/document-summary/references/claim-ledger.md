# Claim Ledger Reference

Detailed schema, verification protocol, and edge cases for the source-grounded Claim Ledger that anchors every summary in this skill. The ledger is the single most important defense against hallucinated content.

## Why the Ledger

LLM-generated summaries reliably introduce content not in the source — fabricated numbers, strengthened hedges, imported common knowledge, generalizations beyond scope. The ledger forces explicit binding between every summary claim and a source span, surfacing the failure modes before delivery rather than after.

## Schema

```markdown
| ID    | Claim                                | Source span         | Verbatim?       | Confidence | Original quote (pivotal) | Note |
|-------|--------------------------------------|---------------------|-----------------|------------|--------------------------|------|
| C-01  | <paraphrase in target language>      | §<sec>, p.<n>, ¶<m> | Direct / Para / Aggregate | High / Med / Low | <source-language quote, if pivotal> | optional |
| I-01  | <inference, in target language>      | (inference)         | Inference       | —          | —                        | <basis> |
```

### Field details

#### ID

- `C-01`, `C-02`, … for **source-grounded claims**.
- `I-01`, `I-02`, … for **inferences** that do not directly trace to a source span.
- IDs must be referenced from the summary body (e.g., "The intervention reduced X by 18% [C-01]").

#### Claim

- Written in the **target language** of the summary.
- Should stand alone — readable without the source.
- Match the source's hedging exactly. If the source says "may", the claim says "may", not "does".
- One claim per row. If a sentence in the body bundles two claims, split into two ledger rows.

#### Source span

Standard format: `§<section>, p.<page>, ¶<paragraph>`. Examples:

- `§4.2, p.18, ¶2`
- `Abstract, p.1`
- `Methods §2, p.5–6`
- `Table 3, p.10`
- `Figure 2 caption, p.7`

For non-paginated sources (web articles, blog posts, regulations): use section names or paragraph counts. For source code documentation: use file:line references. For books: use chapter and section. For Bible / canonical texts: use book-chapter-verse.

If a claim **aggregates** multiple spans, list them all: `§4.2, p.18, ¶2; §5.1, p.20, ¶1`.

#### Verbatim?

| Value | Meaning |
|---|---|
| **Direct quote** | The summary uses the exact source wording (in source or target language) |
| **Paraphrase** | Same meaning, different wording |
| **Aggregate** | Synthesized from multiple source spans into one claim |
| **Inference** | Reserved for `I-` rows; not in the source |

Most claims are paraphrases. Reserve direct quotes for **pivotal claims**: central findings, hedge-bearing claims, recommendations, defining terms, controversial assertions.

#### Confidence

| Level | Meaning |
|---|---|
| **High** | Claim is explicitly stated in the source |
| **Medium** | Claim is implied or follows directly from explicit content; reasonable reading |
| **Low** | Claim requires interpretation; multiple readings possible |
| (Inference rows skip this — they are not source-grounded) |

If you find yourself wanting to use Low for a body claim, consider whether it should be in `[Inference]` instead.

#### Original quote (for pivotal claims)

Include the source-language verbatim quote for:
- The central thesis or research question
- Hedge-bearing claims ("may", "could", "limited evidence", "preliminary")
- Quantitative findings (effect sizes with confidence intervals)
- Recommendations or normative claims
- Definitions of terms
- Counterclaims or limitations the author acknowledges

For non-pivotal paraphrases, this column can be empty.

#### Note

Optional. Use for:
- Aggregation explanation ("from §4.2 and §5.1")
- Context for a quote
- Translation note (e.g., "term X rendered as Y per glossary")
- Disambiguation note (e.g., "claim refers to subgroup A, not all participants")

## Self-Verification Protocol

Run before delivery. Non-negotiable.

### Step 1: Body → Ledger trace

For each sentence in the summary body:

1. Does it reference a `C-` ID? If not, identify the implicit ledger entry.
2. Does the corresponding ledger row exist?
3. Does the body sentence accurately reflect the ledger entry's paraphrase?
4. If no ledger entry exists for the sentence:
   - **Option A**: Find source support; create the ledger entry.
   - **Option B**: Move to `[Inference]` block as a new `I-` entry.
   - **Option C**: Remove the sentence.

### Step 2: Ledger → Source spot-check

For 3–5 representative ledger entries (especially pivotal ones):

1. Open the source at the cited span.
2. Confirm the source actually says what the ledger paraphrase claims.
3. Confirm hedge words are preserved.
4. Confirm quantitative precision is correct.

### Step 3: Hedge audit

Scan ledger paraphrases for hedge words. Common hedge classes:

| Source family | Examples | Common loss |
|---|---|---|
| Modal | may, could, might, possibly | dropped or strengthened |
| Frequency | tends to, often, sometimes | "is" / "always" |
| Magnitude | approximately, roughly, around | exact number stated |
| Evidence | suggests, indicates, points to | "shows", "proves" |
| Scope | in some cases, in this sample, under conditions X | dropped (overgeneralization) |
| Authorial | we believe, we hypothesize, we propose | rendered as fact |

### Step 4: Stance audit

Re-read the source's authorial stance:

- Cautious / hedged?
- Critical / skeptical?
- Confident / advocating?
- Neutral / descriptive?

Re-read your summary. Does it carry the same stance? If the author repeatedly hedges and you've smoothed those hedges, fix it.

### Step 5: Negative space audit

What questions would the audience reasonably expect this summary to answer? Walk those questions:

- If the source addresses it → ensure your summary does too.
- If the source does NOT address it → add an explicit "the source does not address X" line.

## Source vs Inference: The Bright Line

The body of the summary contains **only** source-grounded claims (`C-` rows). Inferences (`I-` rows) live in a clearly labeled `[Inference]` or `## Inferences` block at the end.

Examples of inferences (must be in the inference block, not the body):

- "This implies portfolio rebalancing" — implication for the audience
- "These findings align with the broader literature on X" — synthesis with external knowledge
- "If extrapolated, this suggests…" — projection beyond source scope
- "An expert reading this would likely conclude…" — interpretive overlay

Even when an inference is reasonable and useful, it does not belong in the source-grounded body. The reader must always be able to tell which claims come from the source and which come from the summarizer.

## Edge Cases

### Implicit claims

The source assumes something without stating it ("the standard model assumes…"). Two options:

- **Stated implicit**: if the assumption is foundational and the audience needs it, include in the body with confidence Medium and note "implicit in §X".
- **Skipped**: if not central to the summary, omit.

Avoid: stating implicit assumptions as if they were explicit findings.

### Aggregated claims

Multiple source spans support one summary claim (e.g., "the authors repeatedly emphasize methodological caution"). Mark Verbatim as **Aggregate**, list all source spans, and note the aggregation in the Note column.

### Quantitative claims

Preserve precision. If the source says "17.8%", do not summarize as "around 18%" without preserving the precise figure in the ledger. Confidence intervals must be preserved when relevant.

### Hedged claims

Hedges are part of the claim. "X may reduce Y" and "X reduces Y" are different claims. The ledger must preserve the hedge in the paraphrase. For pivotal hedge-bearing claims, include the source quote in the Original column.

### Methodology claims vs Finding claims

Tag separately. Confusing methodology with findings is a common failure:

- Methodology: "Study used a randomized controlled design with N=200"
- Finding: "The intervention reduced outcome X by 18%"
- Limitation: "Small sample limits generalization"

Each gets its own ledger row.

### Counterclaims and limitations

Always include the limitations section's claims as ledger rows. Many AI summaries drop these; do not.

### Cross-lingual ledger

When source language ≠ output language:

- Claim column: target language paraphrase
- Original quote column: source-language verbatim, especially for pivotal claims
- Note column: any translation/terminology decisions
- The ledger remains the verification artifact; a reviewer fluent in either language can audit.

### Sources where pagination is unavailable

For web articles, blog posts, podcasts (transcripts), code repositories: substitute the most stable identifier — section heading, timestamp, file:line.

For dynamic sources: capture an archive timestamp (e.g., URL + access date or archive.org snapshot URL) so the summary remains auditable later.

### Long sources

For book-length sources, the ledger may grow large. Group by section in the ledger. Consider building a per-chapter mini-ledger and aggregating.

### Quoted material inside the source

If the source itself quotes a third party, distinguish:
- The source's claim about the quote ("Smith (2023) argues X")
- The quote itself

Tag these separately. Do not present the inner quote as the source author's own claim.

### Ambiguous source

If a source claim is ambiguous in the original language and translation forces disambiguation, add a Note. If both readings matter, create two ledger rows with confidence Medium each, and document the choice.

## Common Mistakes

- Skipping the ledger because "the summary is short" — always required, regardless of length.
- Listing only finding claims; dropping methodology, limitations, counterclaims.
- Mixing inferences into the body without `I-` labeling.
- Confidence inflation — marking everything High when much is Medium or implicit.
- Missing the Original column for pivotal hedge-bearing claims.
- Source spans too coarse ("from §4") — use paragraph-level precision when possible.
- Ledger paraphrases that are themselves hallucinations — paraphrasing without checking.
