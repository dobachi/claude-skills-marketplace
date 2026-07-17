# Evidence Base

Why this skill grounds and verifies instead of debating and voting. Each rule below names the finding it rests on, so a future maintainer can re-check the design against the literature rather than inheriting it as folklore.

**This file follows its own skill.** Every span below was opened and quoted verbatim on 2026-07-17. Claims that were not span-verified are quarantined in the last section, labeled as such.

## The finding the whole design hangs on

**Surface citation metrics stay green while factual accuracy collapses.**

> "even the strongest frontier models maintain link validity above 94% and relevance above 80%, yet achieve only 39-77% factual accuracy."
> — *Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents*, Onweller et al. (T2, preprint), https://arxiv.org/abs/2605.06635

Links resolve. Sources are on-topic. The claim still isn't in the source. This is why the skill verifies claim↔span **entailment** and treats link-checking as worthless — every check that stops at "the URL works" or "the page is about this" scores that failure as a pass.

The same paper kills "search harder" as a remedy:

> "Fact Check accuracy drops by approximately 42% on average across two frontier models as tool calls scale from 2 to 150."

Hence: cap searches per sub-question, prune unquoted sources, and put breadth in parallel isolated contexts rather than one long one. *Evidence strength: moderate — one broad 14-model study, preprint, not peer-reviewed. Treat the exact magnitudes as indicative and the direction as well-motivated.*

## Why per-claim verification against spans

Decompose → retrieve → verify per claim is the best-evidenced design available, and it beats the humans it disagrees with:

> "SAFE agrees with crowdsourced human annotators 72% of the time" … "on a random subset of 100 disagreement cases, SAFE wins 76% of the time" … "SAFE is more than 20 times cheaper than human annotators"
> — *Long-form factuality in large language models* (SAFE), Wei et al., NeurIPS 2024 (T1), https://arxiv.org/abs/2403.18802

The skill's blind verifier is SAFE's core move — atomic claim, targeted evidence, per-claim ruling — adapted to subagents. *Evidence strength: strong — peer-reviewed, code and data released.*

## Why the verifier is blind

> "LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction."
> — *Large Language Models Cannot Self-Correct Reasoning Yet*, Huang et al., ICLR 2024 (T1), https://arxiv.org/abs/2310.01798

A verifier that sees the draft and the reasoning is doing intrinsic self-correction with extra steps: it re-runs the generation that produced the error, inside the same frame, and agrees with itself. Blinding it to everything but the claim and the span is what supplies the external signal — the span is the external feedback. *Evidence strength: strong.*

This is also why the verifier's question must stay narrow. "Does this span state this claim?" is near-entailment. "Is this report good?" hands the generator's job back to the verifier and inherits the generator's errors.

## Why NOT multi-agent debate

The intuitive design — spawn agents, let them argue, take the consensus — is the one the evidence rejects.

> "MAD often fail to outperform simple single-agent baselines such as Chain-of-Thought and Self-Consistency, even when consuming significantly more inference-time computation."
> — *Stop Overvaluing Multi-Agent Debate*, Zhang et al. (T2, preprint), https://arxiv.org/abs/2502.08788

For a *research* skill specifically, debate is worse than merely wasteful — it destroys the evidence base while raising apparent confidence:

> "multi-agent discussion erases up to 72% of issue-critical facts" … "stance homogenization, the collapse of diverse positions toward consensus" … "agents can agree more while knowing less"
> — *The Deliberative Illusion*, Wan et al. (T2, preprint), https://arxiv.org/abs/2606.03032

"Agents can agree more while knowing less" is the exact output this skill exists to prevent: a report that reads more confident and rests on less. It is also invisible from the outside — the deliberated report *looks* better. *Evidence strength: moderate — preprint, but the mechanism is corroborated by the conformity findings below and the direction is consistent across several independent 2025–2026 studies.*

The one consistently positive debate finding is not about debate at all:

> "we further explore the role of model heterogeneity and find it as a universal antidote to consistently improve current MAD frameworks."
> — Zhang et al., ibid.

Which the skill takes as: differ the verifier from the generator (model tier, system prompt, tool access). Not as: hold a debate.

## Why NOT majority voting across subagents

> "We find substantial correlation in model errors -- on one leaderboard dataset, models agree 60% of the time when both models err." … "Crucially, however, larger and more accurate models have highly correlated errors, even with distinct architectures and providers."
> — *Correlated Errors in Large Language Models*, Kim, Garg, Peng & Garg, ICML 2025 (T1), https://arxiv.org/abs/2506.07962

This is the load-bearing negative result for every ensemble method, and its sting is in the second sentence: **correlation does not wash out with capability or vendor diversity — it gets worse.** Same-model subagents do not vote independently; they produce correlated errors with a consensus signal layered on top, which is worse than no verification because it manufactures confidence. Error rate under correlated voting approaches a nonzero floor, not zero.

Corollary the skill enforces: **model heterogeneity is a mitigation, never independence.** Claim it modestly.

Note the boundary. Voting helps where errors are *stochastic* (sampling noise in reasoning paths — the self-consistency setting). It fails where errors are *systematic*, i.e. shared training priors. Factual grounding is overwhelmingly systematic: if the model believes a wrong fact, all twenty samples believe it. *Evidence strength: strong — peer-reviewed, 350+ models.*

## Why isolated retrieval subagents, and what they cost

Anthropic's production research system is the closest thing to a reference implementation, and it leans on isolation rather than deliberation:

> "Subagents facilitate compression by operating in parallel with their own context windows, exploring different aspects of the question simultaneously"
> — *How we built our multi-agent research system*, Anthropic Engineering (T2), https://www.anthropic.com/engineering/multi-agent-research-system

Separate contexts are the anti-correlation mechanism that actually works: subagents that cannot see each other cannot anchor on each other. Citation is likewise a **separate terminal pass by a narrow agent**, not something the synthesizer does inline:

> "The system exits the research loop and passes all findings to a CitationAgent, which processes the documents and research report to identify specific locations for citations."

The headline number, and the reason to read it carefully:

> "Multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2%"

*Evidence strength: weak-to-moderate for the 90.2% — vendor-reported, internal eval, not a public benchmark, and the exemplar task (find all board members of IT S&P 500 companies) is embarrassingly parallel lookup, i.e. the best case for fan-out.* Do not generalize it to synthesis- or verification-heavy research. The cost side is the part to plan around:

> "Agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats."

And the honest scope limit, from the same source:

> "Some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today."

Which is why the skill's decomposition step insists sub-questions be *independent*. If they need each other's answers, fan-out is the wrong tool and the skill says so rather than fanning out anyway.

## Not span-verified

Reported by a research pass but **not independently re-opened**, so treat as leads rather than as evidence. Listed because they shaped the design and a maintainer revisiting it should check them properly first:

- Smit et al., *Should we be going MAD?* (ICML 2024), https://arxiv.org/abs/2311.17371 — debate does not reliably beat self-consistency; tuned variants can, i.e. it's hyperparameter-sensitive.
- Wynn et al., *Talk Isn't Always Cheap*, https://arxiv.org/abs/2509.05396 — debate accuracy can decline via conformity even when strong models outnumber weak ones.
- Bertalanič & Fortuna, *The Cost of Consensus*, https://arxiv.org/abs/2605.00914 — sycophantic conformity, consensus collapse discarding correct answers, 2.1–3.4× tokens. Small models only.
- *Why Do Multi-Agent LLM Systems Fail?* (MAST), https://arxiv.org/abs/2503.13657 — task verification is itself one of three top failure categories. Adding verifiers is not free of the disease it treats.
- Manakul et al., *SelfCheckGPT*, https://arxiv.org/abs/2303.08896 — sampling-consistency as a per-sentence triage signal.
- Dhuliawala et al., *Chain-of-Verification* (ACL Findings 2024), https://arxiv.org/abs/2309.11495 — factored verification questions; the factoring is the trick.
- Cohen et al., *LM vs LM* (EMNLP 2023), https://arxiv.org/abs/2305.13281 — cross-examination detects incoherence, not falsehood.
- Song et al., *VeriScore*, https://arxiv.org/abs/2406.19276 — extract only *verifiable* claims; the basis for the `kind` column.
- Wanner et al., *DnDScore*, https://arxiv.org/abs/2412.13175 — decontextualization; the basis for resolving referents before verification.
- Gao et al., *ALCE* (EMNLP 2023), https://arxiv.org/abs/2305.14627 — citation-quality benchmark.
- Min et al., *FActScore* (EMNLP 2023), https://arxiv.org/abs/2305.14251 — atomic claim decomposition.
- Tian et al., *Just Ask for Calibration* (EMNLP 2023), https://aclanthology.org/2023.emnlp-main.330/ — verbalized confidence beats conditional probabilities for RLHF'd models. The strongest argument *for* asking; still not a publish gate, since verbalized confidence clusters at 80–100% regardless of accuracy.

## Design summary

| Rule in the skill | Rests on |
|---|---|
| Verify claim↔span entailment; never link validity | Cited but Not Verified |
| Blind the verifier | Huang et al. (self-correction fails without external feedback) |
| Per-claim verification, atomic claims | SAFE |
| Cap searches; prune unquoted sources | Cited but Not Verified (2→150 degradation) |
| Isolated parallel retrievers; spans not prose | Anthropic multi-agent system; subagent channel returns only the final message |
| Citation as a separate terminal pass | Anthropic CitationAgent |
| No debate; surface disagreement instead | The Deliberative Illusion; Stop Overvaluing MAD |
| No majority voting | Kim et al. (correlated errors rise with capability) |
| Heterogeneity as mitigation, not independence | Zhang et al. (heterogeneity helps); Kim et al. (it doesn't suffice) |
| Sub-questions must be independent | Anthropic (shared-context/dependency domains are a bad fit) |
| Confidence as triage, never a gate | Tian et al. vs. the overconfidence literature |
