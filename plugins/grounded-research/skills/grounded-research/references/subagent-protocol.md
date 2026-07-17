# Subagent Protocol

Exact contracts for the four agent roles. The asymmetry between them is the mechanism — a subagent that holds two roles provides no independent signal, because it shares the context that produced the error.

## Why the contracts are this strict

A Claude Code subagent gets its own context window and returns **only its final message** to the parent. The parent cannot inspect what it read. That strict channel is an asset for grounding *if* the channel carries evidence, and a liability if it carries prose: an unfaithful summary and a faithful one look identical from the parent.

So the rule is not stylistic. **Everything crossing a subagent boundary must be checkable without re-reading the source.** A verbatim span plus a URL is checkable. "The docs confirm this" is not.

## Role 1 — Retriever

One retriever per sub-question, spawned in parallel. Isolated contexts are the anti-correlation mechanism: retrievers that cannot see each other cannot anchor on each other's framing.

**Contract**

- Input: one sub-question, a search cap, a recency requirement, source constraints.
- Output: a list of span tuples. Nothing else.
- Forbidden: conclusions, summaries, recommendations, "in short", answering the sub-question in prose.

**Prompt shape**

```
Sub-question: <one question>

Find evidence. Return ONLY a JSON list of span tuples:
[{"span": "<verbatim quote from the page, source language, long enough to stand alone>",
  "url": "<url actually opened>",
  "title": "<page/document title>",
  "tier": "T1|T2|T3|T4",
  "accessed": "<YYYY-MM-DD>",
  "why": "<which part of the sub-question this bears on, max 15 words>"}]

Rules:
- Open every page you quote. A search-result snippet is NOT a source — snippets are
  generated text and often paraphrase the page wrongly.
- Quote verbatim. Never normalize numbers, units, dates, or hedge words.
- If a page restates another source, go get the original and quote THAT.
- At most <N> searches. Prefer fewer, better sources: retrieval breadth degrades accuracy.
- Discard anything you did not quote. Do not report what you skimmed.
- Do NOT answer the sub-question. Do NOT summarize. Spans only.
- If you find nothing, return [] and one line saying what you searched.

After the array, enumerate coverage — one line per thing the sub-question asked for:
  <item>: FOUND | NOT-FOUND (searched: <what>)
A span for one item is not coverage of the others.
```

**Tier ratings are the retriever's job**, not the lead's — the retriever is the only agent that saw the page. A retriever that opened only T4 pages should say so rather than dress them up.

**Check coverage, not just fidelity.** A sub-question that asks for three things and comes back with real, verbatim, correctly-cited spans for two of them looks flawless: every span checks out. Silent partial retrieval is the one contract failure spans cannot expose, because what came back is all true. Diff the return against what you asked for; anything unenumerated is `NOT-FOUND` until a retriever says otherwise.

**If a retriever returns prose anyway** (it happens): do not paraphrase it into the ledger. Either re-spawn with the contract restated, or treat the sub-question as unretrieved. Prose from a retriever is not evidence — it is a claim about evidence, with the evidence discarded.

**If a retriever returns computed or aggregated numbers** — a count, a census, an average — that is not a span either, however honest the JSON looks. It is arithmetic over sources you cannot see. Re-derive it yourself with a script over the raw artifacts, or drop it.

**Delegating a retriever.** On explicit user request, retrievers — and only retrievers — may be delegated to a foreign CLI agent (`agy`, `codex`, `gemini`) via `agent-delegate`. The span contract survives delegation because a span is checkable no matter who fetched it. Never delegate the lead; it holds the ledger. Two rules:

- **Canonicalize the URL.** Delegates return redirectors by default — `agy` returns `https://vertexaisearch.cloud.google.com/grounding-api-redirect/…` in place of the page; Google/Bing redirectors, AMP and proxies are the same hazard. All are opaque and expire. Add to the prompt: `Return the CANONICAL publisher URL after redirects (e.g. https://code.claude.com/docs/en/skills), never a search/grounding redirect, AMP, or proxy URL.` Resolve doubtful ones with `curl -sIL <url> | grep -i '^location:'`; if it won't canonicalize, re-fetch and register the real page.
- **Check the delegate's first spans once**, with `curl -sL <url> | grep -F "<span>"` — docs sites often serve raw Markdown at a `.md` suffix. A delegate that paraphrases is not a retriever; drop it.

Delegate for a separate quota pool, model heterogeneity, or tools Claude Code lacks (`agy`: Google Search grounding, scientific databases) — not for token cost, where the honest comparison is a Haiku retriever that is already cheap. Rationale: `docs/grounded-research-design.md`.

## Role 2 — Blind Verifier

One per `verifiable` claim, spawned in parallel. **Blinding is the entire value.** A verifier that sees the draft is re-running the generation that produced the error, from inside the same frame; it will agree with itself.

**Contract**

- Input: one claim, one span, and nothing else. Not the report. Not the reasoning. Not sibling claims. Not who wrote it.
- Output: a status and a one-sentence reason.
- The verifier answers a near-entailment question, which models do acceptably. It must never be asked "is this report good?" — a broad question hands the verifier the generator's job back.

**Prompt shape**

```
Claim: <claim, decontextualized — resolve every pronoun, date, and "it">
Span:  <verbatim quote>
Source: <url, tier, accessed date>

Does the span support the claim, on its own?

Answer with one of:
  Supported   — the span states the claim
  Partial     — the span supports part of it, or a weaker version
  Unsupported — the span does not establish the claim (topical relevance is NOT support)
  Disputed    — the span contradicts the claim

Then one sentence of reason, quoting the deciding words.

Do not be charitable. Do not fill gaps from what you know — if the span
doesn't say it, it isn't supported here, even if it's true in the world.
```

**Decontextualize the claim before sending it.** A claim ripped from the draft ("it grew 12% that year") is ambiguous, and ambiguous claims get mis-verified in both directions. Resolve every referent: "Vendor A's seat count grew 12% in FY2025".

**Verifier disagreement is a finding, not noise.** If `Partial` comes back on a claim you thought was solid, the claim is overstated — weaken it to what the span says. Do not re-run the verifier until it agrees. Re-rolling a verifier until it says what you want is the purest form of verification theater.

## Role 3 — Refuter (gated)

Refutation is asymmetric by design: there is no peer to conform to and no consensus to collapse toward, which is why it works where debate does not.

**Gate it.** Run only on claims that are load-bearing (the recommendation changes if it's wrong), numeric, contested, or surprising. Refuting everything is a budget sink.

**Prompt shape**

```
Claim: <decontextualized claim>

Your only job is to find the strongest evidence that this claim is FALSE,
misleading, out of date, or true only under conditions the claim omits.

Return verbatim spans + URLs, in the retriever format. If you find nothing
after <N> searches, return NOTHING-FOUND and say what you searched.

Do not argue. Do not evaluate the claim. Bring evidence or bring nothing.
```

`NOTHING-FOUND` is a genuine result and belongs in the report — "we looked for counter-evidence on this and found none" is worth more than a confidence score. But it is weak evidence of truth: absence of found refutation is not refutation of absence.

## Role 4 — Lead

The lead plans, holds the ledger, and writes. It does **not** search — searching pollutes the synthesis context with unregistered text, and unregistered text is exactly what leaks into the report as an uncited claim.

**Write the plan to a file before spawning.** Long runs truncate context; a plan in the context window is a plan you can lose.

**Budget honestly.** Subagent fan-out costs roughly 3–15× a single agent's tokens, and most of the measured benefit tracks token spend rather than coordination cleverness. Fan out for **parallel independent retrieval** and **isolated verification** — the two places isolation is the point. Do not fan out to generate opinions.

## Model heterogeneity

Where affordable, make the verifier differ from the generator — different model tier, different system prompt, different tool access. It reduces correlated errors; it does not eliminate them (error correlation is *higher* among stronger models, and does not wash out across vendors). Claim it as a mitigation, never as independence.

A cheap and effective split, mirroring the lead/subagent pattern: capable model as lead, cheaper model for retrievers and verifiers. The retriever's job is mechanical (open, quote, rate) and the verifier's job is narrow (entailment on one span) — neither needs the lead's reasoning budget, and a narrower model is *less* likely to smooth over a gap out of helpfulness.

## Budgets

| Depth | Sub-questions | Searches per retriever | Verification | Refutation |
|---|---|---|---|---|
| Quick | 3 | 3 | Load-bearing claims only | None |
| Standard | 5 | 5 | All `verifiable` claims | Load-bearing claims |
| Deep | 7 | 8 | All `verifiable` claims | Every numeric + contested claim |

Caps are ceilings, not targets. A retriever that answers its sub-question from one T1 source in one search has done the job better than one that burned eight searches and quoted five blogs.

## Failure modes to watch

| Symptom | What it means | Response |
|---|---|---|
| Retriever returns prose | Contract not held | Re-spawn or mark sub-question unretrieved |
| Retriever returns counts/averages it computed | Unverifiable arithmetic dressed as evidence | Re-derive with a script, or drop |
| Spans are all genuine but cover only part of the sub-question | Silent partial retrieval — invisible to span-checking | Re-spawn for the missing items, or record them as not-found |
| Span's URL is a redirector (`…grounding-api-redirect/…`, AMP, proxy) | Register row won't survive the month | Canonicalize, or re-fetch and register the real page |
| Every span is T3/T4 | The primary source exists and nobody opened it | Trace up before drafting |
| Verifier says `Supported` on everything | Verifier is being charitable, or saw too much context | Check blinding; check that claims are decontextualized |
| Several claims resting on one source | Corroboration theater | Mark it; one source is one source |
| Sub-questions need each other's answers | Decomposition failed; they aren't independent | Re-decompose, or run sequentially and say so |
| Ledger grows past ~40 claims | Question was too broad | Split into separate runs; a bloated ledger stops being read |
