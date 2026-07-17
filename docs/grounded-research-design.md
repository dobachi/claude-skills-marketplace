# grounded-research — Concept and Design

Why the `grounded-research` skill is built the way it is, and why it deliberately does *not* do the thing most people reach for first.

This document is the rationale. The skill itself lives in
[`plugins/grounded-research/skills/grounded-research/`](../plugins/grounded-research/skills/grounded-research/);
its `references/evidence-base.md` carries the verbatim citations behind each rule.

## The problem

LLM research agents do not fail the way people expect. The intuition is that they invent
sources — fabricated URLs, made-up papers. That failure exists and is easy to catch: the
link doesn't resolve.

The failure that actually dominates is invisible to every check most workflows run:

> "even the strongest frontier models maintain link validity above 94% and relevance above 80%,
> yet achieve only 39-77% factual accuracy."
> — [*Cited but Not Verified*](https://arxiv.org/abs/2605.06635)

The link resolves. The page is genuinely about the topic. The claim still isn't in the source.
A citation checker scores this output green. A human skimming it sees a well-sourced report.
**Surface metrics stay healthy while the substance rots.**

Two corollaries follow, and both are counterintuitive enough that they have to be designed
around rather than left to judgement:

1. **Checking that a link works, or that a source is on-topic, measures nothing.** Only
   claim↔span entailment counts.
2. **Searching harder makes it worse.** The same study found Fact Check accuracy dropped
   ~42% on average as tool calls scaled from 2 to 150. Breadth dilutes attention across a
   longer context and the model starts citing by vibe.

## The tempting answer, and why it's wrong

The obvious design is: spawn several agents, let them debate, take the consensus. Multi-agent
verification *feels* like independent review. It isn't.

**Agents sharing a model do not provide independent verification — they provide correlated
errors with a consensus signal layered on top.** That is worse than no verification, because
it manufactures confidence.

> "We find substantial correlation in model errors -- on one leaderboard dataset, models agree
> 60% of the time when both models err." … "Crucially, however, larger and more accurate models
> have highly correlated errors, even with distinct architectures and providers."
> — [*Correlated Errors in Large Language Models*](https://arxiv.org/abs/2506.07962) (ICML 2025)

The sting is in the second sentence: correlation does not wash out with capability or vendor
diversity. It gets *worse*. So "add more agents" drives error toward a nonzero floor, not zero.

Debate is worse still, and for research specifically it is actively destructive:

> "multi-agent discussion erases up to 72% of issue-critical facts" … "agents can agree more
> while knowing less"
> — [*The Deliberative Illusion*](https://arxiv.org/abs/2606.03032)

"Agents can agree more while knowing less" is the exact output this skill exists to prevent:
a report that reads more confident and rests on less — and it looks *better* from the outside,
which is what makes it dangerous. Meanwhile the broader benchmark record finds debate "often
fail[s] to outperform simple single-agent baselines such as Chain-of-Thought and Self-Consistency,
even when consuming significantly more inference-time computation"
([*Stop Overvaluing MAD*](https://arxiv.org/abs/2502.08788)).

And self-critique doesn't rescue it, because a critic in the generator's own context has no
external signal — it re-runs the reasoning that produced the error and agrees with itself:

> "LLMs struggle to self-correct their responses without external feedback, and at times,
> their performance even degrades after self-correction."
> — [*LLMs Cannot Self-Correct Reasoning Yet*](https://arxiv.org/abs/2310.01798) (ICLR 2024)

## The design

Spend on **grounding and architecture**, not on opinion. Four roles, deliberately asymmetric.
No agent ever holds two.

| Role | Sees | Returns | Must NOT |
|---|---|---|---|
| **Lead** | Question, ledger, subagent returns | Plan, report | Search directly |
| **Retriever** (parallel) | One sub-question | `(span, URL, date, tier)` tuples | Return prose or conclusions |
| **Verifier** (parallel, blind) | One claim + one span | Supported / Partial / Unsupported / Disputed | See the draft or the reasoning |
| **Refuter** (gated) | One claim | Refuting spans, or NOTHING-FOUND | Debate anyone |

### Why retrievers return spans, not summaries

A Claude Code subagent returns **only its final message** to the parent. The parent cannot
inspect what it read. So an unfaithful summary and a faithful one are *indistinguishable
from the parent*. A verbatim span plus a URL is checkable; "the docs confirm this" is not.

This turns the strict subagent channel from a limitation into the enforcement mechanism.

### Why the verifier is blind

Blinding is what makes it a verifier instead of a second generator. It sees the claim and
the span — never the draft, never the generator's reasoning, never sibling claims. The
question it answers ("does this span state this claim?") is near-entailment, which models
do acceptably. Asked instead "is this report good?", it inherits the generator's job and
the generator's errors.

The span *is* the external feedback that Huang et al. showed self-correction lacks.

### Why parallel isolated contexts

This is the one multi-agent mechanism with a clean rationale, and it's the one Anthropic's
own production research system leans on — not debate:

> "Subagents facilitate compression by operating in parallel with their own context windows,
> exploring different aspects of the question simultaneously"
> — [Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)

Retrievers that cannot see each other cannot anchor on each other. Isolation is the
anti-correlation move that actually works. It also keeps breadth *out* of one long context,
which is where the 2→150 degradation happens.

Anthropic reports the multi-agent lead+subagent design beating single-agent Opus 4 "by 90.2%".
Treat that number carefully: **vendor-reported, internal eval, and the exemplar task was
parallel lookup** — the best case for fan-out. The cost side is the part to plan around:
"multi-agent systems use about 15× more tokens than chats."

### Why disagreement is surfaced, never averaged

When two sources conflict, that conflict is usually the most decision-relevant thing in the
report. Deliberation destroys it — consensus rises as the evidence base shrinks. So the
protocol is: register both, quote both, mark unresolved, characterize the conflict.

Most conflicts turn out to be **definitional** and dissolve once stated. That dissolution is
the finding; averaging the two numbers would have destroyed it.

### The artifacts

Two append-only tables, because they answer different questions:

- **Source Register** (`S-01`…) — *was this source real, and did we open it?* Catches
  fabricated URLs, unopened snippets, restatement laundering. Carries a T1–T4 tier.
- **Claim Ledger** (`C-01`…, `I-01`… for inference) — *does the source say this?* Catches the
  dominant failure. Status is set by the **blind verifier**, not the drafter.

The `C-`/`I-` convention and the Source-vs-Inference bright line are inherited deliberately
from [`document-summary`](../plugins/document-summary/skills/document-summary/), which had the
repo's strongest hallucination control — and which, before this skill existed, was locked to
single-source work that does no web search at all. The strongest defense was on the lowest-risk
task. `grounded-research` is its multi-source, web-sourced sibling.

## What this skill deliberately does NOT do

| Not built | Why |
|---|---|
| Multi-agent debate | Conformity; accuracy can drop; evidence gets erased |
| Majority voting over prose | Errors correlate; nothing discrete to vote on |
| Self-critique in the generator's context | Degrades without external feedback |
| "N agents review the report" | Task verification is itself a top multi-agent failure category |
| Confidence score as a publish gate | Verbalized confidence sits at 80–100% regardless of accuracy |
| Unbounded search breadth | Measurably degrades factual accuracy |

**If tempted to add agents, spend the same tokens on more per-claim verification of the
existing draft instead.** The evidence favors depth of grounding over breadth of opinion.

## Where it sits among the other skills

The repo already had three post-hoc auditors of *finished* documents, with mutually
incompatible verdict scales. `grounded-research` is not a fourth. It controls hallucination
**at generation time**, which nothing here did:

| Skill | When it acts | On what |
|---|---|---|
| **grounded-research** | During research | Multi-source, web; prevents ungrounded claims from being written |
| `fact-checker` | After writing | Full 7-dimension audit of a finished doc (Puppeteer) |
| `verify-content` | After writing | Lighter claim + reference pass |
| `evidence-check` | After writing | Reference/citation validity |
| `document-summary` | During writing | Single source, no web |
| `literature-search` | During research | Scholarly APIs; chain in as a retrieval backend |
| `doc-review` | After writing | The argument, not the facts |

The web-facing research skills — `competitive-analysis`, `market-sizing`, `tauri-research` —
now carry a compact ledger of their own and hand off to `grounded-research` when the stakes
justify the token cost.

## Validation: the skill was dogfooded on a live question

Run on *"is there an effective length limit on a Claude Code skill's `description`?"* — chosen
because this repo's own `skill-authoring-best-practices.md` says "Under 200 characters" while
its house style had drifted to ~900.

The run produced three things a prose-summarizing workflow would have missed:

1. **A definitional conflict, correctly not averaged.** 1,024 (Claude *API* docs: field maximum)
   and 1,536 (Claude *Code* docs: truncation of `description`+`when_to_use` **in the listing**)
   are different products and different mechanisms — not a contradiction.
2. **The blind verifier killed a drafted claim.** The draft said "Claude Code hard-limits
   description to 1,536 characters." Verdict: `Unsupported` — "the span applies the 1,536-character
   limit to the combined `description` and `when_to_use` text, not to the `description` field
   alone; and 'truncated … in the skill listing' describes display behavior, not a hard field
   limit." The claim had quietly grown a generalization the span never made. The verifier caught
   it *because* it never saw the draft.
3. **An empirical result that contradicts the docs.** Anthropic's own `claude-api` skill ships a
   **1,068-character** description — over the documented 1,024 maximum — and runs in Claude Code
   anyway. Measured with code, not counted by a model. All 17 skills under `anthropics/skills/skills/`
   exceed 200 characters; the shortest is 204.

Conclusion for this repo: **the 200-character rule has no primary source** and is contradicted
by Anthropic's own practice. The house style was right and the written convention was wrong.

The run also surfaced a real protocol violation worth recording: one retriever returned a
computed census instead of a verbatim span (self-flagged as "not a verbatim quote"). Per protocol
it was refused entry to the ledger and the figure was re-derived with a script — which then
exposed a version drift between the GitHub `raw` copies and the local clone (948/835/732 vs
941/785/688 characters for the same three skills). Access dates and a commit hash in the register
are what made that legible rather than confusing.

## Cost

Fan-out is not free: roughly 3–15× the tokens of a single agent, and Anthropic's own data shows
token spend explains ~80% of the performance variance on BrowseComp — meaning much of the
multi-agent gain is *compute*, not coordination cleverness. Budget accordingly:

| Depth | Sub-questions | Searches/retriever | Verification | Refutation |
|---|---|---|---|---|
| Quick | 3 | 3 | Load-bearing only | None |
| Standard | 5 | 5 | All `verifiable` claims | Load-bearing |
| Deep | 7 | 8 | All `verifiable` claims | Numeric + contested |

Two cheap levers: send retrievers and verifiers to a smaller model (their jobs are mechanical
and narrow — a lead-model reasoning budget buys nothing), and prune aggressively, since capping
breadth *saves* tokens and *improves* accuracy at the same time.

## Reading the evidence honestly

The design rests on findings of uneven strength, and the skill's own reference file labels them
rather than flattening them:

- **Strong** (peer-reviewed): correlated errors rising with capability (ICML 2025); SAFE's
  per-claim verification (NeurIPS 2024); self-correction failing without external feedback (ICLR 2024).
- **Moderate** (preprint, but broad or well-motivated): the citation-accuracy gap; the 2→150
  degradation.
- **Weak** (single preprint, or vendor self-report): the 72% factual-attrition figure; Anthropic's
  90.2%.

The *direction* is consistent across independent 2025–2026 studies; the exact magnitudes are not
settled. Anyone revisiting this design should re-check the sources rather than inherit these
numbers as folklore — which is the whole point of the skill it describes.
