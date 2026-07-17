# Source Register & Claim Ledger Reference

Schema, span rules, tiering, and edge cases for the two artifacts that make a research report auditable. The register records what was read; the ledger records what may be said. Everything else in this skill exists to keep those two honest.

Related: `document-summary` uses a Claim Ledger for a *single* source with section/page spans. This is its multi-source, web-sourced sibling — same `C-`/`I-` convention, but spans point at registered sources rather than at pages of one document, and status is set by a blind verifier rather than by the drafter.

## Why two tables

One table conflates two different failure modes. **The register answers "was this source real and did we open it?"** — it catches fabricated URLs, unopened snippets, and restatement laundering. **The ledger answers "does the source say this?"** — it catches the far more common failure, where the source is genuine, relevant, and simply does not contain the claim.

Keeping them separate also lets one source carry many claims, and one claim rest on many sources, without duplicating either.

## Source Register

```markdown
| ID    | Source                    | URL      | Tier | Accessed   | Retriever | Note |
|-------|---------------------------|----------|------|------------|-----------|------|
| S-01  | RFC 9110 §9.3.1           | https://…| T1   | 2026-07-17 | sub-2     |      |
| S-02  | Vendor A pricing page     | https://…| T2   | 2026-07-17 | sub-1     | prices region-dependent |
| S-03  | TechBlog "A vs B" (2023)  | https://…| T4   | 2026-07-17 | sub-1     | restates S-02; superseded |
```

### Field rules

- **ID** — `S-01`… Assigned on registration, never reused, never renumbered. Claims reference these IDs; renumbering silently rewrites history.
- **Source** — enough to identify it without the URL: document title plus the section actually quoted. "Vendor docs" is not a source identifier.
- **URL** — the **canonical** URL of the page that was *opened*: the publisher's own address, after redirects. Not a search URL, not a Google cache, not a link the retriever saw referenced elsewhere, and **not a redirector**. Search-engine redirects, grounding-API redirects (`vertexaisearch.cloud.google.com/grounding-api-redirect/…`), AMP URLs, and proxy links are all opaque and most of them expire — a row nobody can re-derive next month is a row that does nothing. Resolve with `curl -sIL <url> | grep -i '^location:'` and register the destination. If a URL cannot be canonicalized, do not register the source; re-fetch the page directly.
  - **Version the artifact, not just the date, when the source is a repo or a package.** The same file served from `raw.githubusercontent.com/…/main/…` and from a local clone pinned at an older commit will differ. Both are T1; they are not the same artifact. Register the commit hash, tag, or version alongside the URL — otherwise two spans that look like corroboration are a contradiction you cannot see.
- **Tier** — T1–T4 (below). Assigned by the retriever, which is the only agent that saw the page.
- **Accessed** — the date. Web pages change; a claim without an access date is unauditable six months on. For pages that matter and might move, register an archive snapshot URL alongside.
- **Retriever** — which subagent brought it. Makes it visible when one retriever supplied everything, which usually means the decomposition collapsed.
- **Note** — supersession, region/version scope, paywall status, "restates S-0X".

### Append-only discipline

The register is append-only. When a source turns out to be wrong, superseded, or retracted:

- **Do not delete the row.** Add a Note (`superseded by S-07`, `retracted 2026-03`) and re-status the claims that rest on it.
- Claims resting on it become `Disputed` or `Unsupported`, not invisible.

The reason is that the register is the audit trail. A register you can edit is a register that always agrees with the report, which makes it decorative. This is also why claims carry status rather than being deleted when they fail — a reader learning that a plausible claim was checked and failed has learned something.

### Tiering edge cases

| Situation | Tier | Reasoning |
|---|---|---|
| Vendor's own API docs for their own product | T2 | Primary but interested. Right about the interface, unreliable about comparisons |
| Vendor's benchmark of a competitor | T4 | Interested party, adversarial subject. Register it as a *claim about a claim*, never as fact |
| Source code of the thing being asked about | T1 | It's the ground truth. Prefer it over docs when they disagree — and that disagreement is itself a finding |
| Peer-reviewed paper | T1 | But check retraction status; `literature-search` has the machinery |
| Preprint | T2 | Not yet reviewed. Say so in the report; don't quietly render it as T1 |
| Wikipedia | T3 as a map, T4 as a fact | Use it to find the primaries in its footnotes, then register those. Never the terminal source for a load-bearing claim |
| Reputable journalism reporting a filing | T3 | The filing is T1. Trace up — the reporter's paraphrase is where numbers drift |
| Stack Overflow answer | T3 if dated and specific | Check the version it was written against; the accepted answer is often years stale |
| Undated page | Demote one tier | You cannot assess currency, so treat it as weaker than its content suggests |
| AI-written roundup / SEO listicle | T4 | Its claims have unknown provenance and it will cite confidently. Never terminal |
| Archived snapshot of any of the above | Same tier as original | Archiving preserves text, not authority |

**Trace up before drafting.** The rule "quote from the lowest tier number available" is the highest-yield habit in this skill. A T4 restatement's error is invisible from the T4 page — the drift happened upstream, and the restatement reads perfectly fluent. Retrieval agents default to well-ranked aggregators over authoritative-but-lower-ranked primaries (academic PDFs, standards, filings), so this must be pushed for deliberately; it doesn't happen on its own.

## Claim Ledger

```markdown
| ID    | Claim                          | Source     | Span (verbatim)                  | Kind         | Status      | Note |
|-------|--------------------------------|------------|----------------------------------|--------------|-------------|------|
| C-01  | Idle timeout defaults to 60s   | S-01       | "…the default idle timeout is 60 seconds…" | verifiable | Supported | |
| C-02  | Vendor A is cheaper at 50 seats| S-02; S-05 | "$49/seat/mo"; "$61/seat/mo"     | verifiable   | Supported   | arithmetic in body |
| C-03  | Migration typically takes weeks| S-03       | "took us about three weeks"      | interpretive | Partial     | one anecdote, not "typically" |
| I-01  | Managed option fits this team  | —          | —                                | inference    | —           | based on C-01, C-02 |
```

### Span selection

The span is the load-bearing part of the whole apparatus. Get it wrong and everything downstream is theater.

- **Verbatim.** Never normalize numbers, units, dates, or hedges while quoting. "roughly 18%" does not become "18%" in a span.
- **Standalone.** Long enough that a blind verifier who sees only the span can rule on the claim. If the deciding word is a pronoun, extend the span until it isn't.
- **Deciding, not decorative.** The span must contain the words that make the claim true, not words near them. A span that only proves the page discusses the topic supports nothing — this is precisely the failure where link validity and topical relevance stay green while factual accuracy collapses.
- **Source language.** Do not translate inside the span. Translate in the Claim column; keep the original in the span so a reader fluent in either can audit.
- **One claim per row.** A body sentence bundling two claims gets two rows.
- **Numbers demand exactness.** A numeric claim standing on a paraphrase rather than a verbatim span does not ship. Preserve confidence intervals, denominators, base rates, and the units.

### Kind

| Kind | Meaning | Gets verified? |
|---|---|---|
| `verifiable` | A span could settle it | Yes — blind verifier |
| `interpretive` | A reading of evidence ("adoption is accelerating" from one QoQ figure) | No — but the underlying figures must be `verifiable` rows |
| `speculative` | Projection past the evidence | No — and it belongs in the inference block, not the body |

Tagging first is a cost control: verification budget spent on unfalsifiable prose is budget not spent on the numbers. It is also honesty — an `interpretive` claim rendered in the body with a citation reads to the reader as a fact the source stated.

### Status

Set by the **blind verifier**, never by the drafter. A drafter grading its own claims is self-critique in the generator's own context, which degrades rather than improves output.

| Status | Meaning | What ships |
|---|---|---|
| `Supported` | Span states the claim | Body, with `C-` ID |
| `Partial` | Span supports a weaker version | Weaken the claim to what the span says, then ship |
| `Unsupported` | Span doesn't establish it | Find a real span, demote to `I-`, or delete |
| `Disputed` | A source contradicts it | Disagreement block, both sides attributed |
| `Unverified` | Not checked (budget, or `interpretive`) | Only with the status visible to the reader |

`Partial` is the most informative status and the most often ignored. It usually means the claim quietly grew a generalization the source never made — "in our deployment" became "typically". Fix the claim; don't re-roll the verifier.

## The Source vs Inference bright line

The body contains only `C-` claims. Inferences — implications, synthesis with prior knowledge, recommendations, "this suggests" — go in a labeled block at the end as `I-` rows.

Inferences are often the most valuable part of a research report. That is not a reason to blur the line; it's the reason the line matters. The reader must be able to tell what the sources established from what the researcher concluded, because the second one is where your judgement enters and where the reader may reasonably disagree.

Examples that belong in `I-`, not the body:
- "This favors the managed option for a team this size" — a recommendation
- "These figures are consistent with the broader market trend" — synthesis with unregistered knowledge
- "Extrapolating, they'd hit the limit by Q3" — projection
- "Vendor A is probably repricing soon" — speculation

An `I-` row should cite the `C-` rows it rests on. An inference resting on nothing is a guess, and should be labeled one or dropped.

## Coverage and negative space

The report states what was **not** established, as a first-class section:

- **Searched, not found** — "no primary source for A's seat pricing above 500 seats"
- **Out of reach** — paywalled, login-walled, PDF unparseable, non-indexed
- **Out of date** — "no data past 2024-Q2"
- **Out of scope** — sub-questions deliberately not asked

Silence reads as completeness. A report that quietly omits what it couldn't find misleads by omission more effectively than a wrong claim does, because there's nothing for the reader to check. This is the research analogue of `document-summary`'s negative-space audit.

## Common mistakes

- **Skipping the register because "it's a quick question."** Quick runs get a smaller ledger, not no ledger. The gate is the skill.
- **Registering a source nobody opened.** A search snippet is generated text about a page, not the page.
- **Spans trimmed to the deciding number, losing its scope.** "12%" without "in the EU trial" is a different claim.
- **Renumbering IDs when the ledger is reorganized.** Breaks every body citation silently.
- **Marking everything `Supported`.** Verifier is being charitable, or wasn't blind.
- **Three T4 sources treated as corroboration.** If they all restate one press release, that's one source with three URLs.
- **Editing the register to match the report.** Backwards — the report follows the register.
- **Claims that outlived their spans.** After an edit, the body says more than the span; the gate catches this only if you actually re-walk it.
- **Inference block used as an amnesty.** Moving an unsupported factual claim to `I-` doesn't launder it — `I-` is for reasoning, not for facts you couldn't source.
