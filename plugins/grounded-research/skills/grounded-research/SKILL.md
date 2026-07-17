---
name: grounded-research
description: Runs multi-source research with hallucination control built into the architecture — parallel retrieval subagents that return only quoted spans, an append-only Source Ledger where no claim ships without a source row, blind per-claim verification, and disagreement surfaced rather than averaged. Use when the user wants a researched answer or report from the web and being wrong is expensive — "調査して", "リサーチして", "裏を取って", "research this", "investigate", "gather evidence on". Not a post-hoc auditor of a finished document (hand off to `fact-checker` / `verify-content`), not single-source summarization (`document-summary`), not academic literature search by API (`literature-search`).
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message. Sources can be in any language; quoted spans stay in the source language.

# Grounded Research

Runs research that is hard to hallucinate *by construction*, rather than research that is checked for hallucination afterwards. Retrieval and synthesis are separated into different agents with different contexts; every claim in the report binds to a quoted span in the **Source Ledger**; a blind verifier re-checks claims against spans without ever seeing the draft.

The central empirical fact this skill is designed around: frontier models keep link validity above 94% and source relevance above 80% while factual accuracy of the claims those links support sits at 39–77%. **Citations resolve, sources are on-topic, and the claim still isn't in the source.** Every surface-level citation check scores that output green. Only claim↔span entailment catches it.

**Out of scope**: auditing a document someone else already wrote (`fact-checker` for the full 7-dimension audit, `verify-content` for a lighter pass). Single-source summarization (`document-summary`). Academic literature via Semantic Scholar / OpenAlex / CrossRef APIs (`literature-search` — chain it in as a retrieval backend when the question is scholarly). Critiquing a draft's argument (`doc-review`).

## Core Principles

1. **Retrieval agents do not write prose. Synthesis agents do not search.** A retrieval subagent returns `(quoted span, URL, accessed date)` tuples only — never a summary, never a conclusion. The parent cannot see what a subagent read, so a subagent's prose summary is unauditable by construction. Spans are auditable.
2. **No source, no claim.** Every sentence in the report body carries a `C-` ID that binds to a ledger row with a verbatim span. Claims without a row are moved to the inference block or deleted. This is enforced mechanically at the verification gate, not by good intentions.
3. **The verifier is blind.** Per-claim verification subagents see the claim and the span — never the draft, never the generator's reasoning, never the other claims. This is what makes it a verifier instead of a second generator.
4. **Disagreement is the highest-value signal. Never average it.** When two sources or two subagents conflict, render both with attribution and mark it unresolved. Do not vote, reconcile, or debate it away.
5. **Breadth belongs in parallel isolated contexts, never in one long one.** Cap searches per sub-question and discard sources you did not quote. Piling retrieved text into one context degrades accuracy — more searching produces worse grounding, not better.
6. **Source quality is upstream of everything.** A well-cited content farm passes every citation metric. Rate and record source tier before quoting.
7. **Confidence numbers are triage, never a gate.** Self-reported confidence clusters at 80–100% regardless of actual accuracy. Use it to decide what to verify first; never to decide what ships unverified. Evidence status is the gate.

## Architecture

Four agent roles, deliberately asymmetric. Never let one agent hold two roles.

| Role | Sees | Returns | Must NOT |
|---|---|---|---|
| **Lead** (you) | The question, the ledger, subagent returns | Plan, report | Search the web directly; write claims not in the ledger |
| **Retriever** (parallel subagents) | One sub-question, a search budget | Span tuples + tier rating | Return prose, conclusions, or "the source basically says…" |
| **Verifier** (parallel subagents, blind) | One claim + one span | `Supported / Partial / Unsupported / Disputed` + reason | See the draft, the reasoning, or other claims |
| **Refuter** (gated subagents) | One claim + freedom to search | Refuting spans, or `NOTHING-FOUND` | Argue with anyone; it reports, it does not debate |

Write the plan to a file before spawning anything. Subagent fan-out costs 3–15× the tokens of a single agent, and roughly 80% of the measured benefit is explained by token spend alone — so spend it where it buys grounding, not opinion.

Detail on subagent contracts and prompt shapes: `references/subagent-protocol.md`.

## Workflow

| Step | Action | Output |
|---|---|---|
| 1. Intake | Capture: the question, decision it feeds, depth (Quick / Standard / Deep), recency requirement, source constraints, output language. Narrow an underspecified question before spending anything | Scoped question |
| 2. Decompose | Break into 3–7 independent sub-questions. Independent means a retriever can answer one without another's output | Sub-question list |
| 3. Retrieve (parallel) | One retriever subagent per sub-question, each with its own context and a search cap. Each returns span tuples only | Raw span tuples |
| 4. Register sources | Fold every returned tuple into the **Source Register** with tier and access date. Discard sources nothing was quoted from | Source Register |
| 5. Draft claims | Build the **Claim Ledger**: each claim bound to `S-` rows. Tag each `verifiable / interpretive / speculative` | Claim Ledger |
| 6. Verify (parallel, blind) | One blind verifier per `verifiable` claim. Route conflicts to step 7 | Per-claim status |
| 7. Reconcile disagreement | Sources conflict → render both, mark unresolved. **Never** average or debate | Disagreement block |
| 8. Refute (gated) | Refutation subagent on load-bearing, numeric, and contested claims only | Refutation results |
| 9. Draft report | Body cites `C-` IDs. Inferences to the inference block | Draft |
| 10. **Grounding gate** | Walk every body sentence → `C-` ID → `S-` row → span. Any break: fix, demote, or delete. Non-negotiable | Verified draft |
| 11. Coverage | State what was searched, what was not found, and what the search could not cover | Coverage block |

Depth presets: Quick = 3 sub-questions, no refutation, spot-check verification. Standard = 5 sub-questions, verify all `verifiable` claims, refute load-bearing ones. Deep = 7 sub-questions, full verification, refutation on every numeric and contested claim.

## Source Register (mandatory)

```markdown
| ID    | Source                          | URL                | Tier | Accessed   | Retriever |
|-------|---------------------------------|--------------------|------|------------|-----------|
| S-01  | ISO/IEC 25010:2011 §4.2         | https://…          | T1   | 2026-07-17 | sub-2     |
| S-02  | Vendor pricing page             | https://…          | T3   | 2026-07-17 | sub-1     |
| S-03  | Analyst blog restating S-02     | https://…          | T4   | 2026-07-17 | sub-1     |
```

| Tier | What | Examples |
|---|---|---|
| **T1** | Primary, authoritative, dated | Standards, statutes, filings, peer-reviewed papers, official API docs, the actual source code |
| **T2** | Primary but interested | Vendor docs, company blogs, press releases, maintainer posts |
| **T3** | Secondary with named authorship and a date | Reputable journalism, signed technical writeups |
| **T4** | Restatement, aggregation, undated, or SEO-shaped | Content farms, listicles, undated blogs, AI-written roundups |

Rules: **quote from the lowest tier number available.** If T3/T4 restates a T1/T2 source, go get the original and register that instead — a restatement's error is invisible from the restatement. Never register a source a retriever did not open (a search-result snippet is not a source). Two claims resting on the same T4 source is not corroboration. URLs must be **canonical** — never a search/grounding redirector, AMP, or proxy link, which are opaque and expire. For repo or package sources, register the commit or version too: the same file at two revisions is two artifacts.

## Claim Ledger (mandatory)

```markdown
| ID    | Claim                              | Source | Span (verbatim)                       | Kind         | Status      |
|-------|------------------------------------|--------|---------------------------------------|--------------|-------------|
| C-01  | Latency budget is 200 ms p99        | S-01   | "…p99 latency MUST NOT exceed 200ms…" | verifiable   | Supported   |
| C-02  | Pricing starts at $49/seat/month    | S-02   | "$49 per seat per month"              | verifiable   | Supported   |
| C-03  | Adoption is accelerating            | S-03   | "usage grew 12% QoQ"                  | interpretive | Partial     |
| C-04  | Vendor A and B disagree on limits   | S-01; S-04 | see disagreement block            | verifiable   | Disputed    |
| I-01  | This favors the managed option      | —      | —                                     | inference    | —           |
```

- **C-** = source-grounded, **I-** = inference. Body prose carries only `C-` IDs; `I-` rows live in a labeled inference block.
- **Span** is verbatim from the source, in the source language, long enough to stand alone. A span that only proves the *topic* was discussed does not support the claim.
- **Kind**: `verifiable` (checkable against a span) / `interpretive` (a reading of evidence) / `speculative` (projection). Only `verifiable` claims enter blind verification — do not spend the verification budget on claims no span could settle.
- **Status**: `Supported` / `Partial` / `Unsupported` / `Disputed` / `Unverified`. Set by the **blind verifier**, not by the drafter.
- The register is **append-only**. A source that turns out to be wrong gets a claim marked `Disputed`; the row is never edited away.

Schema details, span rules, and edge cases: `references/source-ledger.md`.

## Grounding Gate

Run before delivery. Non-negotiable.

1. **Body sentence → `C-` ID?** No ID: move to inference block or delete.
2. **`C-` → `S-` → span?** Any broken hop is a hallucinated claim regardless of how reasonable it reads.
3. **Span actually entails the claim?** Not "is about the same topic". Re-read the span cold, without the claim in mind, and ask what it establishes on its own.
4. **Numbers exact?** Units, dates, currency, base rates, denominators. Numeric claims resting on a paraphrase and not a verbatim span do not ship.
5. **Hedges preserved?** The source's "may" is not your "does". The source's "in this sample" is not your "in general".
6. **Tier honest?** No T1 claim standing on a T4 restatement.
7. **Disagreements intact?** Nothing quietly resolved between draft and final.
8. **Coverage stated?** What was not found is part of the finding.

## Disagreement Protocol

When sources conflict, this is what the reader is paying for. Do not smooth it.

1. Register both sources; write both spans into the ledger; mark the claim `Disputed`.
2. Characterize the conflict: different measurement, different date, different scope, different definition, or genuine factual dispute. Most conflicts are definitional and dissolve once stated.
3. If one source is a strictly higher tier *and* the lower-tier source is a restatement of nothing, say so and prefer it — with the disagreement still visible.
4. If it does not dissolve: report both, attribute both, mark unresolved, and state what evidence would settle it.
5. **Never** resolve a disagreement by asking agents to discuss it. Deliberation converges on stance while dropping the evidence that created the disagreement — the report gets more confident and less grounded, which is the exact failure this skill exists to prevent.

## Quality Rubric (6 axes)

| Dimension | Strong | Adequate | Weak |
|---|---|---|---|
| **Grounding** | Every claim → span; spans entail claims | Minor paraphrase drift | Claims supported only by topical relevance |
| **Source quality** | T1/T2 primaries; restatements traced to originals | Mixed, tiers labeled | T4 aggregators cited as fact |
| **Verification** | All verifiable claims blind-verified | Load-bearing claims verified | Drafter graded its own claims |
| **Disagreement handling** | Conflicts surfaced, characterized, attributed | Conflicts noted | Conflicts averaged or silently dropped |
| **Coverage honesty** | Not-found and out-of-reach stated explicitly | Gaps mentioned | Silence implies completeness |
| **Auditability** | A reader can re-derive every claim from the ledger | Ledger present, minor gaps | No ledger, or spans too short to check |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| **Subagents return summaries** | Parent can't see what they read; an unfaithful summary is undetectable | Span tuples only |
| **Citing a search snippet** | The page was never opened; snippets are model-written | Open it or don't cite it |
| **Link-validity as verification** | Links resolve at 94% while claim accuracy sits at 39–77% | Verify claim↔span entailment |
| **Multi-agent debate to settle facts** | Agents conform rather than challenge; accuracy can *drop*, evidence is discarded, tokens 2–3× | Blind verification + refutation; surface disagreement |
| **Majority vote across same-model agents** | Errors correlate (and correlate *more* in stronger models); voting manufactures false confidence | Vote on nothing; ground on spans |
| **Self-critique in the generator's context** | Intrinsic self-correction without external feedback degrades output | Blind verifier with its own context |
| **"N agents review the report"** | Verification is itself a top empirical source of multi-agent failure | One narrow job per agent |
| **Confidence score as publish gate** | Overconfident and not acted on faithfully | Gate on evidence status |
| **More searches = better** | Accuracy degrades as retrieval breadth grows; noise crowds out signal | Cap per sub-question; prune unquoted sources |
| **Restatement laundering** | T4 blog cited for a T1 fact it garbled | Trace to the original, register that |
| **Corroboration theater** | Three sources all restating one press release | Corroboration requires independent origin |
| **Silent non-findings** | Reader assumes coverage that never happened | Coverage block |
| **Inference smuggled into the body** | Reader can't tell evidence from the researcher's reading | `I-` rows, separate block |

## Deliverable Template

```markdown
# <question>

**Depth**: <Quick/Standard/Deep>  **Date**: <date>  **Sub-questions**: <n>  **Sources**: <n> (T1: <n>, T2: <n>, …)

## Bottom line
<the answer, in one or two sentences>

## Findings
- <claim> [C-01]
- <claim> [C-02]

## Disagreement / unresolved
- <claim>: S-01 says X, S-04 says Y. Conflict type: <definitional/temporal/…>. Unresolved. Settled by: <what evidence would decide it>

## What we could not establish
<not found; out of reach — paywalled, no primary source, no data past <date>>

---

## Source Register
<table>

## Claim Ledger
<table>

## Inferences
<I- rows — the researcher's reading, not the sources'>
```

## Iteration Modes

| Mode | When to use |
|---|---|
| **Deepen** | Promote a sub-question to its own Standard/Deep run; ledger carries forward |
| **Re-verify** | Re-run blind verification on an existing ledger (e.g., after sources age) |
| **Refute** | Run refutation on a claim someone pushed back on |
| **Trace up** | Replace T3/T4 rows with the T1/T2 originals they restate |
| **Chain out** | Hand the ledger to `document-summary`, `strategy-memo`, or `market-sizing`; hand a finished doc to `fact-checker` |

## References (consult when relevant)

- `references/source-ledger.md` — register/ledger schema, span selection rules, tiering edge cases, append-only discipline
- `references/subagent-protocol.md` — exact contracts and prompt shapes for retriever / blind verifier / refuter, budgets, and what to do when a subagent returns prose anyway
- `references/evidence-base.md` — why this design and not debate/voting: the findings, effect sizes, and citations behind each rule
