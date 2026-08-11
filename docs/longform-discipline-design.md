# longform-discipline — Design Notes

Why the `longform-discipline` skill is shaped the way it is, and how much to trust the evidence
behind each rule. Written **2026-08-11** alongside the skill. Rationale lives here; `SKILL.md` and
`references/` carry rules only.

Method note: this skill was built on a `grounded-research` **Deep** run — 7 independent retrieval
subagents returning verbatim spans only, an append-only source register and claim ledger, 18 blind
per-claim verifiers, 2 refutation subagents, and a mechanical span check that re-fetched every
source and string-matched every span. Final gate: **63 spans, 0 NOT-FOUND, 0 UNREACHABLE**. That
process caught three things a normal literature pass would have shipped, described under
*What the process caught* below.

## The problem this skill solves

The marketplace already had the long-document *workflow* covered — `doc-coauthoring` drafts,
`doc-refactor` restructures, `doc-review` critiques, `essence-distiller` cuts. None of them
addresses the thing that actually breaks a 40,000-character document: it drifts. The register
changes between chapters written on different days, a term acquires two spellings, the same
argument reappears in three places in three shapes, and the last third is visibly thinner than
the first.

That is not a writing-quality problem and it is not fixed by a better drafting conversation. It is
a *state* problem, and it has measured mechanisms. So the skill is deliberately a **cross-cutting
layer**, not a fifth workflow: it constrains how the other skills are used rather than replacing
them.

Scope was set with the user up front: 数万字〜10万字超 plus academic long-form, hybrid character
(discipline + minimal workflow + inspection script), bilingual JA/EN.

## Design decisions

**Three decay axes, kept separate.** Long *input*, long *output*, and long *session* degrade
independently and have different fixes. Collapsing them into "the context window is too small" is
the most common practitioner error, and it leads to buying a bigger context window for a problem
that a bigger context window makes worse. The evidence is separated the same way in
`references/failure-modes.md`.

**The spine file, not a longer prompt.** The single most load-bearing design choice. Persistent
instructions repeated in conversation vanish the moment the context is summarized; a file on disk
is re-read at session start and after compaction. This copies the `CLAUDE.md` pattern, and it also
copies document-level machine translation, where systems maintain an explicit Proper Noun Record
rather than trusting the model to remember terminology across a document. The spine holds purpose,
audience, outline with status, glossary, style contract, claims, and a session log — i.e. exactly
what a fresh context needs to resume without loading the draft.

**The style contract is fixed before drafting, not after.** Japanese makes this non-negotiable:
deciding 敬体 vs 常体 at the end means rewriting every sentence. Encoded as a spine section, and
enforced by the scanner.

**Sequential sections with the prior tail — never parallel.** This is the one place the evidence
gives a directly actionable number: LongWriter's own ablation shows parallel section generation
improves length while costing 6% coherence, and its authors conclude the previously generated
context must be supplied. Parallelism is the obvious optimization and it is measurably wrong.

**The seam pass is mandatory, and this is the skill's least obvious rule.** Decomposition is
usually sold as a pure win. It is not. The primary source reports that its own pipeline improves
Breadth and Depth by 5% while *decreasing* Coherence and Clarity by 2%, and that outputs
"occasionally contain minor repetitions… restate content from previous paragraphs". So the same
mechanism that makes long output possible is also what produces the stitched-together reading and
the cross-section duplication. A skill that recommends decomposition without mandating seam repair
is recommending half a method. `cross-section-dup` in the scanner exists specifically for this.

**The outline is revisable.** The refutation pass earned this rule. Plan-first has strong measured
support (Re3 +14%/+20% on plot coherence and premise relevance; DOC +22.5%/+28.2%/+20.7% over Re3),
but two later papers attribute long-form collapse past ~2,000 words specifically to *static*
hierarchical planning and criticize outline-first pipelines as rigid. Without that pass the skill
would have said "outline first" and stopped, which is the wrong lesson.

**Gate on a scanner plus a human, never on an AI score.** Three independent findings converge here:
self-contradiction is common (17.7% of ChatGPT sentences in one analysis) and automatic detection is
unreliable on the nuanced cases; LLM judges carry position, order and self-preference bias strong
enough that reordering candidates flips rankings; and people reviewing AI output do worse while
feeling more confident. The last of those is a code study and predates current models, so the skill
uses it to argue for *review posture* — hand the human a numbered list of specific things to check —
rather than quoting it as a prose result.

**The scanner reports, never edits.** Same contract as `essence-distiller`'s `distill_scan.py`. A
flagged repetition may be a deliberate callback and a short section may be short on purpose; the
scanner cannot see meaning and says so in its own output.

## What the process caught

Three failures that a normal literature review ships, listed because they are the argument for
running the process rather than trusting the retrieval:

1. **A stale benchmark number.** A retriever quoted NoLiMa's v1 HTML: "12 popular LLMs… 10 models
   drop below 50%". The current (v3, ICML) abstract says **13** and **11**. The span check caught it
   because the span was not on the canonical page. Two revisions are two artifacts.
2. **A fabricated-looking span that was real, and a real span that was wrong.** A span attributed to
   a 2026 snowballing preprint could not be found on the page — it turned out to be LaTeX-mangled
   body math the retriever had reflowed. The paper exists; the quote as written did not. Replaced
   with the abstract's plain-language sentence, and the source demoted to T2 (unreviewed,
   single-author).
3. **Two overstated claims, caught by blind verification.** "Merely altering the order can flip an
   LLM judge's ranking; Vicuna-13B beat ChatGPT on 66/80" and "participants wrote less secure code
   *and* were more confident" both came back `Partial` — each span supported only half of its claim.
   Both were split into two ledger rows with their own spans rather than weakened into vagueness.

Six further claims came back `Partial` on decontextualization grounds (the span said "this task",
the claim said "ContraDoc") and were narrowed to exactly what the span states.

## Confidence and what is not settled

**The long-input degradation finding is genuinely disputed, and the skill says so.** Needle-in-a-
haystack results from vendors are flat — Google reports >99.7% recall to 1M tokens — while NoLiMa,
RULER and others report steep decay. The conflict is *measurement*, not fact: literal-match
retrieval survives long context, latent-association and reasoning tasks do not, and NoLiMa exists
precisely because lexical overlap makes NIAH gameable. `references/failure-modes.md` renders both
sides with attribution and marks it unresolved rather than picking a winner. Practitioner
implication, stated in the reference: flat NIAH numbers are evidence that *lookup* survives, not
that *coherent long-form work* does.

**Generation-ceiling numbers age fastest.** "~2k words single-pass", "most LLMs cannot exceed 4000
words" are 2024 measurements. The mechanism (SFT-bounded effective generation length) is more
durable than the number. The skill leans on the mechanism and the reference tells the reader to
re-check anything load-bearing older than a year.

**Two supporting sources are unreviewed preprints** (the snowballing-at-scale paper, IS-CoT). Both
are labeled as such inline. Neither carries a rule on its own.

**The Japanese rules are from public-document style guides** (文化審議会建議「公用文作成の考え方」,
JTF日本語標準スタイルガイド), which are the right authority for 実務文書 and the wrong one for
fiction or transcripts. `references/japanese.md` ends with an explicit "do not apply here" section,
and preserves the sources' own hedges — 建議 says a sentence's appropriate length "は一概に決められない"
before offering 50–60字, so the scanner treats 60 characters as an inspection line, not a rule.

## The scanner

`drift_scan.py`, stdlib-only, Python 3.8+, nine checks, ~0.04s on a 12,000-character document.
Exit `0` / `1` / `2` so it can serve as a `loop-goal`-style stop condition.

Validated with a positive control (a document seeded with every defect — all nine check classes
fired) and a negative control (a clean document of the same shape — zero findings), plus runs
against real repository documents. Three false-positive classes surfaced in that testing and were
fixed rather than documented away:

- **Markdown table cells read as sentences.** `README_ja.md` produced 15 "over-long sentence"
  findings that were all table rows. Tables are now their own line kind, excluded from sentence
  length, redundancy and duplication checks.
- **Documents that document notation choices.** `references/japanese.md` lists サーバー/サーバ etc.
  in a table *on purpose*, and scored 10 false notation-drift hits against itself. Notation checks
  now run on a prose corpus with tables and blockquotes removed.
- **Heading levels compared across depths.** Section-imbalance compared the `#` title section
  against `##` chapters, making every chapter an outlier. It now compares peers at one heading
  level only.

### 1.1.0 — enforcing the declaration, not just internal consistency

`style-mixing` only ever saw *inconsistency*: a document written uniformly in 敬体 passed it even
when the spine said である調. That is a real gap — the spine's Style contract was the one part of the
control surface the scanner did not read, so it was advice rather than a rule.

`declared-style-violation` closes it by parsing the Style contract and comparing the draft to the
stated intent: register, digit width, list punctuation, and banned phrasings. When a register is
declared, `style-mixing` stands down rather than double-reporting — the declared check lists the
same sentences, measured against intent instead of against the document's own majority.

The design risk here is guessing. The shipped template offers alternatives (`である調 | ですます調 |
formal EN`, `半角/全角`), and a scanner that picked the first one would invent a rule the author never
wrote. So an undecided line is skipped, and the scan header prints the contract it actually parsed —
or `no style contract declared` — so a silently-skipped contract is visible rather than mistaken for
a clean pass. Testing caught one hole in that guard: `半角/全角` was initially read as 半角, because
only `|` alternatives were rejected.

The section-level claim ("Claim it must land") stays unenforced on purpose. It needs meaning, which
this scanner does not have; that belongs to `doc-review` and the human gate.

One bug found the same way: `repeated-opener` never fired on Japanese, because an 8-character key
diverges before two paragraphs with the same connective can match. It now keys on the leading
connective up to the first 、.

The remaining known limitation is 文体 classification. It is suffix matching, not parsing, so a
sentence ending in an unusual construction may be silently unclassified rather than misclassified —
the failure direction is a missed finding, not a false alarm. Quotes and list items are excluded per
建議, which permits differing sentence endings in 引用・従属節・箇条書き.

## Boundaries

Deliberately **not** in this skill, to keep the cross-cutting layer thin:

| Job | Owner |
|---|---|
| The drafting conversation, context gathering, reader testing | `doc-coauthoring` |
| Restructuring without changing meaning | `doc-refactor` |
| Critique of the argument | `doc-review` |
| Deciding what to cut | `essence-distiller` |
| AI tells and register repair | `ai-tell-reducer` / `humanize-prose` |
| Fact and citation verification | `verify-content` / `fact-checker` / `evidence-check` |
| JA↔EN | `faithful-translation` |
| Gathering the sources in the first place | `grounded-research` |
