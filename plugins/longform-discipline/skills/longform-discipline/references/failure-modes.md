# Failure Modes — the evidence behind each rule

Every rule in `SKILL.md` traces to a measured finding here. Each row carries a verbatim span from
the source, so a reader can check the rule against the evidence rather than against this file's
summary of it. Spans were string-matched against the live pages on 2026-08-11 (63 spans, 0 not
found). Read this file when someone asks *why* a rule exists, or proposes breaking one.

Confidence note: findings are reported as the sources state them. **Benchmark numbers age fast, and
several rows below are already old enough to need re-checking before they are quoted as the current
state of the art.** Dates are given inline for that reason. A result about "GPT-4 in 2023" is
evidence about a 2023 model, not about whatever you are using now — treat the *mechanism* as the
durable part and the *number* as perishable.

---

## Axis 1 — Long input degrades

**Position matters.** Relevant material in the middle of a long context is used worst.

> "In particular, we observe that performance is often highest when relevant information occurs at
> the beginning or end of the input context, and significantly degrades when models must access
> relevant information in the middle of long contexts, even for explicitly long-context models."
> — Liu et al., *Lost in the Middle*, https://arxiv.org/abs/2307.03172

**Effective context is far shorter than advertised.** NoLiMa defines effective length as the point
where the score falls below 85% of the model's own base score, and finds it collapses early:

> "We evaluate 13 popular LLMs that claim to support contexts of at least 128K tokens. While they
> perform well in short contexts (<1K), performance degrades significantly as context length
> increases. At 32K, for instance, 11 models drop below 50% of their strong short-length baselines.
> Even GPT-4o, one of the top-performing exceptions, experiences a reduction from an almost-perfect
> baseline of 99.3% to 69.7%."
> — *NoLiMa* (ICML 2025), https://arxiv.org/abs/2502.05167

> "Even models with base scores exceeding 90.0% exhibit a significantly shorter effective length
> than their claimed lengths, generally limited to"
> — *NoLiMa* v3 §4.4, https://arxiv.org/html/2502.05167v3 (sentence continues past the quoted span)

RULER independently reports the same gap:

> "While these models all claim context sizes of 32K tokens or greater, only half of them can
> maintain satisfactory performance at the length of 32K."
> — *RULER*, https://arxiv.org/abs/2404.06654

**Length alone hurts — it is not only a retrieval problem.** This is the finding that kills
"just give it a better index":

> "even when models can perfectly retrieve all relevant information, their performance still
> degrades substantially (13.9%--85%) as input length increases but remains well within the models'
> claimed lengths."
> — *Context Length Alone Hurts LLM Performance Despite Perfect Retrieval*, https://arxiv.org/abs/2510.05381

Anthropic states the same effect and its architectural cause:

> "as the number of tokens in the context window increases, the model's ability to accurately
> recall information from that context decreases. While some models exhibit more gentle
> degradation than others, this characteristic emerges across all models."

> "Context, therefore, must be treated as a finite resource with diminishing marginal returns."

> "Every new token introduced depletes this budget by some amount, increasing the need to carefully
> cura[te]"
> — Anthropic, *Effective context engineering for AI agents*,
> https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

### ⚠ Disagreement — surfaced, not averaged

Vendor and some independent needle-in-a-haystack results are *flat*, not degrading:

> "Gemini 1.5 Pro achieves near-perfect “needle” recall (>99.7%) up to 1M tokens of “haystack” in
> all modalities, i.e., text, video and audio."
> — Google Cloud, https://cloud.google.com/blog/products/ai-machine-learning/the-needle-in-the-haystack-test-and-how-gemini-pro-solves-it

> "The model Gemini 2.5 Flash can answer needle-in-a-haystack questions with great accuracy
> regardless of document position including when the document is nearly at the input context limit."
> — *Retrieval Quality at Context Limit*, https://arxiv.org/abs/2511.05850

And the benchmarks on the degradation side draw methodological fire:

> "benchmarks like LongBench often do not provide proper metrics to separate long-context
> performance from the model's baseline ability, making cross-model comparison unclear"
> — *100-LongBench*, https://arxiv.org/abs/2505.19293

**Conflict type: measurement, not fact.** The flat results are literal-match retrieval — find a
sentence you can lexically match. NoLiMa exists *because* that is gameable, and constructs needles
with minimal lexical overlap. Google also labels its own strongest number an internal test:

> "While this was an internal test, Gemini 1.5 Pro supports a 2M token context window (the largest
> of any model provider today)."

**What this means for writing.** Finding a fact you can name is not the task. Holding an argument
consistent across 40,000 characters is closer to the latent-association and reasoning tasks that
degrade. Treat flat NIAH numbers as evidence that *lookup* survives long context, not that
*coherent long-form work* does.

---

## Axis 2 — Long output degrades

**There is a generation ceiling, and it is low.**

> "Current long context large language models (LLMs) can process inputs up to 100,000 tokens, yet
> struggle to generate outputs exceeding even a modest length of 2,000 words."

> "the model's effective generation length is inherently bounded by the sample it has seen during
> supervised fine-tuning (SFT)"

> "We can observe from the figure that the maximum output length of all models is around 2k words."
> — *LongWriter*, https://arxiv.org/abs/2408.07055 / https://arxiv.org/pdf/2408.07055

> "most LLMs cannot generate text that is longer than 4000 words"
> — *HelloBench*, https://arxiv.org/abs/2409.16191

**Quality falls as output grows** — and the failure is invisible from a benchmark that only tests
input handling:

> "despite strong results on Ruler, all models struggled with long text generation on LongGenBench,
> particularly as text length increased"
> — *LongGenBench*, https://arxiv.org/abs/2409.02076

> "current LLMs struggle with length requirements and information density in long-text generation,
> with performance deteriorating as text length increases"
> — *LongEval*, https://arxiv.org/abs/2502.19103

> "while some LLMs can generate longer text, many issues exist (e.g., severe repetition and quality
> degradation)"
> — *HelloBench*

Repetition is a known degeneration mode with a traced cause:

> "a strong correlation between the degeneration issue and the presence of repetitions in training data"
> — *Repetition In Repetition Out*, https://arxiv.org/abs/2310.10226

> "models often generate the repeated word until reaching the output token limit"
> — Chroma, *Context Rot*, https://www.trychroma.com/research/context-rot

---

## Axis 3 — Long sessions degrade

> "all the top open- and closed-weight LLMs we test exhibit significantly lower performance in
> multi-turn conversations than single-turn, with an average drop of 39% across six generation tasks"

> "Analysis of 200,000+ simulated conversations decomposes the performance degradation into two
> components: a minor loss in aptitude and a significant increase in unreliability. We find that
> LLMs often make assumptions in early turns and prematurely attempt to generate final solutions,
> on which they overly rely."

> "when LLMs take a wrong turn in a conversation, they get lost and do not recover"
> — *LLMs Get Lost In Multi-Turn Conversation*, https://arxiv.org/abs/2505.06120

That last sentence is the whole argument for re-entering fresh per section rather than continuing
one long thread: the recovery you are counting on does not happen.

**Errors compound rather than stay put:**

> "Crucially, we find that ChatGPT and GPT-4 can identify 67% and 87% of their own mistakes,
> respectively. We refer to this phenomenon as hallucination snowballing: an LM over-commits to
> early mistakes, leading to more mistakes that it otherwise would not make."
> — *How Language Model Hallucinations Can Snowball*, https://arxiv.org/abs/2305.13534

Note the shape of that finding: the model can *recognize* most of its own errors when asked
directly, but does not catch them while committed to a line of generation. That is an argument for
checking in a fresh context, not for asking mid-flow "are you sure?".

An unreviewed 2026 preprint reports the effect strengthening with scale — treat as suggestive only:

> "Bigger models snowball mistakes faster, through a failure mode that is dominant,
> self-perpetuating, causal and invisible to the model itself."
> — https://arxiv.org/abs/2607.18292 (single-author preprint, not peer reviewed)

---

## What works — planning and decomposition

**Plan-first measurably improves long-form coherence:**

> "with explicit storyline planning, the generated stories are more diverse, coherent, and on topic"
> — *Plan-And-Write*, https://arxiv.org/abs/1811.05701

> "Compared to similar-length stories generated directly from the same base model, human evaluators
> judged substantially more of Re3's stories as having a coherent overarching plot (by 14% absolute
> increase), and relevant to the given initial premise (by 20%)."
> — *Re3*, https://arxiv.org/abs/2210.06774

> "DOC substantially outperforms a strong Re3 baseline (Yang et al., 2022) on plot coherence (22.5%
> absolute gain), outline relevance (28.2%), and interestingness (20.7%)."
> — *DOC*, https://arxiv.org/abs/2212.10077

**Decomposition breaks the output ceiling:**

> "AgentWrite first breaks down long writing tasks into multiple subtasks, with each subtask
> requiring the model to write only one paragraph. The model then executes these subtasks
> sequentially, and we concatenate the subtask outputs to obtain the final long output."
> — *LongWriter*

**Sequential, with prior context — not parallel:**

> "we find that while +Parallel slightly improves the model's output length score, it impairs the
> output quality of AgentWrite, especially in terms of Coherence (-6%). This suggests that it is
> necessary to provide the model with the previously generated context in Step II of AgentWrite."
> — *LongWriter*

### ⚠ Decomposition is not free — this is why the seam pass is mandatory

The primary source's own ablation reports the cost:

> "By comparing quality scores across six dimensions, we find that AgentWrite significantly improves
> the Breadth and Depth scores (+5%), while slightly decreasing the Coherence and Clarity scores (-2%)."

> "outputs generated using AgentWrite occasionally contain minor repetitions. For instance, the
> model might restate content from previous paragraphs, or frequently provide summarization in its
> output."
> — *LongWriter*

**And a frozen plan is itself a failure mode:**

> "our evaluation reveals that they suffer from a severe length collapse in open-ended writing,
> where performance degrades sharply as target lengths exceed 2,000 words. We attribute this failure
> to the limitation of static hierarchical planning, which struggles to provide dynamic guidance
> over extended contexts."
> — *IS-CoT*, https://arxiv.org/abs/2606.09709 (preprint)

> "Current approaches rely on predefined workflows and rigid thinking patterns to generate outlines
> before writing, resulting in constrained adaptability during writing."
> — *Beyond Outlining*, https://arxiv.org/abs/2503.08275

So: plan, decompose, carry context forward — **and** revise the plan, repair the seams, and hunt
cross-section restatement. The gains and the costs come from the same mechanism.

---

## What works — state outside the context window

> "Structured note-taking, or agentic memory, is a technique where the agent regularly writes notes
> persisted to memory outside of the context window."

> "Compaction is the practice of taking a conversation nearing the context window limit,
> summarizing its contents, and reinitiating a new context window with the summary."

> "Sub-agent architectures provide another way around context limitations. Rather than one agent
> attempting to maintain state across an entire project, specialized sub-agents can handle focused
> tasks with clean context windows."
> — Anthropic, *Effective context engineering for AI agents*

> "Compact at meaningful workflow boundaries, not after every turn. Preserve enough working state
> for the next phase to make sense."
> — OpenAI Cookbook, https://developers.openai.com/cookbook/examples/agents_sdk/building_reliable_agents_memory_compaction

A persistent file re-read at session start is the pattern the spine file copies:

> "CLAUDE.md files are markdown files that give Claude persistent instructions for a project, your
> personal workflow, or your entire organization. You write these files in plain text; Claude reads
> them at the start of every session."

> "Project-root CLAUDE.md survives compaction: after /compact, Claude re-reads it from disk and
> re-injects it into the session."

…with the warning that makes spine hygiene a rule rather than a preference:

> "Consistency: if two rules contradict each other, Claude may pick one arbitrarily."
> — Claude Code docs, https://code.claude.com/docs/en/memory

For terminology specifically, document-level systems keep an explicit proper-noun store rather than
hoping the model remembers:

> "DelTA features a multi-level memory structure that stores information across various
> granularities and spans, including Proper Noun Records, Bilingual Summary, Long-Term Memory, and
> Short-Term Memory, which are continuously retrieved and updated by auxiliary LLM-based components."
> — *DelTA*, https://arxiv.org/abs/2410.08143

---

## Why the gate is a scan plus a human, never an AI score

**Self-contradiction is common and hard to detect automatically:**

> "Our analysis reveals the prevalence of self-contradictions, e.g., in 17.7% of all sentences
> produced by ChatGPT."

> "a large portion of self-contradictions (e.g., 35.2% for ChatGPT) cannot be verified using online text"
> — https://arxiv.org/abs/2305.15852

> "While GPT4 performs the best and can outperform humans on this task, we find that it is still
> unreliable and struggles with self-contradictions that require more nuance and context."
> — *ContraDoc*, https://arxiv.org/abs/2311.09182 (**2023-11 — stale; re-check before quoting**)

Read both halves of that sentence. It says GPT-4 **can outperform humans** at finding document
self-contradictions *and* that it remains unreliable on nuanced cases. It also measured a *prompted*
model in 2023. It is not evidence about a fixed-weight NLI classifier, and it is not evidence about
any model shipped since. Do not use it to rule out automated contradiction detection — use it to
insist that whatever you use is measured at its operating point before it becomes a gate.

**Model judges are biased in ways that survive prompting:**

> "position bias is not due to random chance and varies significantly across judges and tasks"

> "position bias is weakly influenced by the length of prompt components, it is strongly affected by
> the quality gap between solutions"
> — *Judging the Judges*, https://arxiv.org/abs/2406.07791

> "the quality ranking of candidate responses can be easily hacked by simply altering their order of
> appearance in the context"

> "Vicuna-13B could beat ChatGPT on 66 over 80 tested queries with ChatGPT as an evaluator."
> — *Large Language Models are not Fair Evaluators*, https://arxiv.org/abs/2305.17926

> "GPT-4 exhibits a significant degree of self-preference bias."
> — https://arxiv.org/abs/2410.21819

**And the human gate degrades if you let it be vague.** In a controlled study of AI-assisted work,
having the assistant made outcomes *worse* while making people *more* confident:

> "participants who had access to an AI assistant based on OpenAI's codex-davinci-002 model wrote
> significantly less secure code than those without access"

> "participants with access to an AI assistant were more likely to believe they wrote secure code
> than those without access to the AI assistant"
> — *Do Users Write More Insecure Code with AI Assistants?*, https://arxiv.org/abs/2211.03622

That study is about code, not prose, and it predates current models — so read it as a caution about
review *posture*, not as a measured prose result. The posture it argues for: hand the reviewer a
specific, numbered list of things to check. "Please review" is where over-trust lives.
