# Structural Patterns Reference

Patterns for organizing summaries. Each pattern was developed for a specific rhetorical or analytical purpose; matching the pattern to the source genre × audience mode is half the work of a good summary.

## Selection Matrix

| Source genre | Executive mode → use | Professional mode → use |
|---|---|---|
| Empirical academic paper | Pyramid + key findings | IMRAD-derived (Introduction / Methods / Results / Discussion) |
| Theoretical / review paper | Pyramid + thesis-first | Argument-structured (thesis → contributions → positioning) |
| Business report | Pyramid / Decision Memo | SCQA |
| Whitepaper | Pyramid / Decision Memo | Problem-Approach-Evidence-Recommendation |
| News article | Inverted pyramid (compressed) | Inverted pyramid (full) |
| Book (non-fiction) | Pyramid + chapter map | Argument-structured chapter-by-chapter |
| Regulatory / policy | Decision Memo (impact-led) | Topic-organized (scope / definitions / obligations / exceptions) |
| Technical documentation | Decision Memo (use case-led) | Topic-organized (purpose / prerequisites / procedure / parameters) |
| Systematic review / meta-analysis | Pyramid + headline effect | Cochrane-style (PICO / methods / results / certainty / implications) |

## Pyramid Principle (Barbara Minto)

The most useful pattern for executive summaries.

- **Answer first.** State the conclusion, recommendation, or headline finding in the first sentence.
- **Then 3 supporting arguments**, each one a parallel claim.
- **Each argument has supporting evidence** (drawn from the ledger).
- The structure is hierarchical: the reader can stop at any level and have a coherent answer.

### Template

```markdown
## Bottom line
<one-sentence headline>

## Why
- **Reason 1** — <claim 1, supporting evidence summary> [C-01]
- **Reason 2** — <claim 2, supporting evidence summary> [C-02]
- **Reason 3** — <claim 3, supporting evidence summary> [C-03]

## What this means
<implication for the audience>
```

### When to use

- Executive summaries
- Business decision memos
- Status reports for sponsors

### Pitfalls

- More than 5 supporting points — the pyramid loses its force; consolidate.
- Reasons that are not parallel — make them all of one logical type (e.g., all causes, or all consequences).
- Reasons that don't actually support the bottom line — ensure rigorous answer-first logic.

## BLUF (Bottom Line Up Front)

US military origin. Variant of the Pyramid emphasizing the takeaway in the **opening sentence**.

```markdown
<one-sentence takeaway>. <one or two sentences of context>. <key facts>. <recommendation or implication>.
```

Useful for: very short summaries (single paragraph), email-formatted summaries, briefings under 200 words.

## Decision Memo

Variant of the Pyramid optimized for action.

```markdown
## Situation
<what's the context, in 2-3 sentences>

## Options
- Option A — <description, ledger refs>
- Option B — <description, ledger refs>
- Option C — <description, ledger refs>

## Recommendation
<which option, why>

## Risks and mitigations
<top 2-3 risks; how addressed>

## Open questions
<numbered list>
```

When summarizing a single source, use this when the source is itself analytical/recommending (e.g., a McKinsey report, a strategy memo, a regulatory impact assessment).

## SCQA (Situation, Complication, Question, Answer)

McKinsey-favored narrative structure for analytical summaries.

- **Situation**: stable starting context the reader accepts
- **Complication**: what changed; what disrupted the situation
- **Question**: the implicit question raised by the complication
- **Answer**: the source's answer (or your summary of it)

```markdown
## Situation
<context>

## Complication
<what changed>

## Question
<the question that arises>

## Answer
<the source's claim, with supporting points>
```

When to use: business analytical reports, white papers, narrative-driven Professional summaries.

## PREP (Point, Reason, Example, Point)

Short-form pattern; useful for paragraphs, talking points, and tight segments inside larger summaries.

```markdown
**Point**: <claim>
**Reason**: <why it's true / source's argument> [C-XX]
**Example**: <concrete instance from source> [C-XX]
**Point**: <restate, possibly sharpened>
```

Use as a building block within Pyramid or SCQA — not as a top-level pattern for an entire summary.

## IMRAD (Introduction, Methods, Results, Discussion)

The standard structure for empirical academic papers. **Mirror it in Professional summaries** of empirical research — readers expect this organization and use it to find specific information quickly.

```markdown
## Introduction (Background and Research Question)
- Gap the source addresses [C-01]
- Research question / hypothesis [C-02]

## Methods
- Design [C-03]
- Sample / participants [C-04]
- Measurement / analysis [C-05]
- Methodological limitations acknowledged by authors [C-06]

## Results
- Primary finding (with effect size and confidence interval) [C-07]
- Secondary findings [C-08]
- Subgroup or sensitivity analyses [C-09]

## Discussion
- Authors' interpretation [C-10]
- Limitations [C-11]
- Implications and future work [C-12]
```

Don't reorganize empirical papers into a thesis-first structure for Professional summaries — readers familiar with the genre expect IMRAD.

For Executive mode, **collapse** IMRAD into a Pyramid with the headline finding first.

## Argument-Structured (for theoretical / review papers)

```markdown
## Thesis
<central claim, often spanning multiple sentences> [C-01]

## Contributions
- Contribution 1 — <novelty> [C-02]
- Contribution 2 — <novelty> [C-03]

## Argument structure
<how the source builds its case section by section>

## Positioning
<how the source positions itself relative to prior work> [C-XX]

## Implications
<what the source claims its argument implies> [C-XX]
```

## Inverted Pyramid (news convention)

- **Lede**: who, what, when, where, why, how — first paragraph.
- **Key facts** in descending order of importance.
- **Background and context** later.
- **Quotes and color** later still.

The reader can stop at any point and have the most important information. This is also why news pieces can be cut from the bottom by editors. Mirror it for Professional summaries of news; collapse heavily for Executive.

## Cochrane-Style (systematic review / meta-analysis)

For Professional summaries of evidence syntheses:

```markdown
## Background
<the clinical/research question, in PICO form>

## Methods
- Eligibility criteria
- Search strategy
- Included studies (number, quality)

## Results
- Primary outcome — pooled effect estimate with 95% CI [C-XX]
- Secondary outcomes [C-XX]
- Heterogeneity / subgroup findings [C-XX]
- Certainty (GRADE) [C-XX]

## Authors' conclusions
<conclusions, hedge-preserving> [C-XX]

## Limitations of the evidence
<as acknowledged by reviewers> [C-XX]
```

## Topic-Organized (regulatory / technical / policy)

When the source has heterogeneous topics (e.g., a regulation covering scope, definitions, obligations, exceptions), summarize topic by topic in the source's order.

```markdown
## Scope
## Defined terms
## Obligations
## Exceptions / safe harbors
## Effective dates and transition
## Penalties / enforcement (if applicable)
```

Resist the temptation to reorganize regulatory documents into a Pyramid — readers need to navigate by topic.

## Hybrid Patterns

Many real summaries combine patterns. Common combinations:

- **Pyramid + IMRAD**: Executive bottom line at the top, IMRAD structure for the body. Use when the audience is mixed (some need decision, some need methodology).
- **Decision Memo + SCQA**: Situation/Complication/Question framing followed by Options/Recommendation. Use for strategy memos.
- **Inverted Pyramid + analysis block**: News-style top, longer analytical body. Use for current-events analyses.

## Negative Space (every Professional summary should include this)

A dedicated block stating what the source does NOT address but the audience might reasonably expect:

```markdown
## What the source does NOT address
- <topic 1 the audience might assume is covered but isn't>
- <scope condition the source implies but doesn't state>
- <comparison or alternative the source doesn't engage with>
```

This is one of the highest-value sections — it prevents readers from assuming coverage that isn't there.

## Length and Compression Guidance

| Mode | Source length | Output length |
|---|---|---|
| Executive | Any | 1 page (300–600 words) |
| Professional, short article | 5–15 pages | 1 page |
| Professional, paper / report | 15–50 pages | 2–4 pages |
| Professional, book / large report | 50+ pages | 4–8 pages, possibly chapter-by-chapter |

If the source has methodology, limitations, and counterclaims that don't fit the budget, prioritize:

1. Research question / thesis
2. Methodology / scope (compressed)
3. Primary finding(s) with hedge preservation
4. Limitations the author acknowledges
5. Implications (carefully separating source vs. inference)
6. Negative space

Cut secondary findings, exhaustive subgroup analyses, and historical context first.
