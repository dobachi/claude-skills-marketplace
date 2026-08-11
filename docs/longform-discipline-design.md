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

### 1.6.0 — contradiction, treated as a narrowing problem rather than a judgement problem

Contradiction detection had been parked as one heavy "should we add NLI?" decision. Splitting the
backlog revealed that had lumped two opposite failures together — **duplication** (saying the same
thing twice) and **contradiction** (saying incompatible things) — on the sole grounds that both
would use embeddings. Embeddings serve different roles in the two: for duplication, finding similar
sentences *is* the answer; for contradiction it is only a retrieval step feeding a classifier. The
practical consequence of the conflation was a wrong ordering — it implied duplication could not be
improved without also taking on NLI, which is false.

The reframing that made the rest tractable: **contradiction is n² in sentences**, roughly 2M pairs
for a 40,000-character draft. At 99% per-pair precision that is 20,000 false positives against a
handful of real conflicts. So the precision that matters comes from **the size of the candidate
set**, not the quality of the judgement — which means the useful work is narrowing, and narrowing is
mostly deterministic.

The ladder, of which steps 2 and 3 shipped here:

| Step | Covers | Cost |
|---|---|---|
| 1 `numeric-inconsistency` | same label, same unit, different value | shipped 1.2.0 |
| 2 `fact-conflict` | same label, incompatible date / version / 可否 | **here**, deterministic |
| 3 `claim-conflict-candidate` | where else the ledger's subjects are discussed | **here**, needs `--spine` |
| 4 free-form semantic contradiction | — | not implemented; only after 1–3 prove insufficient |

Step 3 is what the Claims ledger was always for. A claim recorded with its section turns "compare
every pair of sentences" into "read these two places", and the check renders **no verdict** — it
produces a reading list. That is the only form in which a human can actually check for contradiction,
and it costs nothing.

Step 2's precision argument is the same as the numeric check's: only values of the same kind
carrying the same label are ever compared. Measured on seven real documents: zero findings. On the
seeded fixture: 4/4, and the no-conflict variant is silent.

Three defects surfaced while building it, all in presentation or scoping rather than detection:

- The polarity display derived the negative form by string surgery (`する`→`しない`), which is wrong
  for 必要である/不要である. The matched surface form now travels with the value.
- `_measure_label` took the whole run before a number, so 「移行方式はブルーグリーンを採用する」
  labelled the fact 「移行方式はブルーグリーン」. A leading topic marker is now stripped: the part
  before `は` names the topic, the part after names what is being asserted.
- `claim-conflict-candidate` matched the document root for every claim, because an ancestor section's
  subtree contains everything below it. Sections shallower than the claim's own are now skipped.

What deliberately stays with the human, because no classifier finds it either: a commitment made in
the introduction and quietly dropped in the conclusion, a definition that shifted, a recommendation
that does not follow from its evidence. None of those are `p ∧ ¬p`. `content-review.md` 手順A4 / B1
is the procedure for them.

### 1.5.0 — tests, after checking what the official guidance actually says

The nested-document bug survived because the controls lived in a scratch directory and evaporated
with the session. Before building a replacement, the official guidance was read rather than assumed,
and it changed the plan in three ways.

**There is already a convention for testing a skill, not just its scripts.** Test cases go in
`evals/evals.json` inside the skill directory, with `prompt` / `expected_output` / `files` /
`assertions` ([spec](https://agentskills.io/skill-creation/evaluating-skills)). The invented format
this project was about to grow is unnecessary. The important part is the protocol, not the schema:
**run each case twice, with the skill and without, and read the delta.** A high with-skill pass rate
proves nothing on its own — and the guidance says to *delete* assertions that pass in both
configurations, which is the same instinct as requiring a detector to fire on defect-injected input.

**Bundling tests inside the skill directory is fine.** The spec: "A skill directory may contain any
files and directories beyond the required `SKILL.md`", and files cost no context until read. The
worry about bloating the distributed skill was unfounded.

**The order here was backwards.** "Create evaluations BEFORE writing extensive documentation. This
ensures your Skill solves real problems rather than documenting imagined ones." This skill reached
1.4.2 before anyone wrote a test.

Reading the guidance also surfaced violations that had been shipping: four reference files over 100
lines with no table of contents, and a repo-level rule ("frontmatter is name + description only")
that contradicted the spec's six fields — which is why `loop-goal` was being flagged for `metadata`,
a legal field. Only its top-level `version` is out of spec.

What now exists:

| Layer | Determinism | In CI | Catches |
|---|---|---|---|
| `tests/run_tests.sh` + 22 permanent fixtures | full | yes | the scanner silently breaking |
| `tools/validate_skills.py` (extended) | full | yes | spec drift, undocumented checks, dead links, missing TOCs |
| `evals/evals.json` (3 cases, 17 assertions) | probabilistic | no | SKILL.md's instructions not producing the intended behaviour |

Two things the harness taught while being written:

- **Exit codes are not enough.** Five checks report at `info` and deliberately do not fail the gate
  (a gate that is always red during drafting gets ignored). Their liveness is invisible to exit
  codes, so the harness grew a second assertion form — `has:<check>` / `no:<check>` on the output.
  The substring bug in `unverified-claim` is caught *only* by that form.
- **The harness must be proven to fail.** Reverting each of the three real bugs — the 1.4.1 nested
  resolution, the 1.4.2 sibling checks, the `"unverified"` substring — turns the suite red. A suite
  that has never failed is not evidence of anything.

The nested fixture is now permanent, and the rule generalises: **include a fixture shaped unlike
your own repository's documents**, because dogfooding can only ever exercise the shapes you already
have.

### 1.4.1 / 1.4.2 — the nested-document bug, and why it reached three checks

Every spine-driven check was written and validated against **flat** fixtures: `## 第1章` with prose
directly underneath. A real book is nested — `## 第1章` followed immediately by `### 1.1` — and in
that shape three defects compounded:

1. `split_sections` drops body-less sections, so a chapter heading whose first line is its own
   subheading did not exist as a section at all (12 of 23 chapters in the book this was found on).
2. `_section_index` returned the first substring match, so a chapter reference landed on a
   subsection of a *different* chapter.
3. A chapter's own lines stop at its first subheading, so a claim was compared against the lead
   sentence — sometimes against nothing.

On a real book that produced **11 HIGH + 7 WARN confidently wrong findings**, and missed the one
real problem. 1.4.1 fixed it for `claim-coverage` with a `keep_empty` section view, level-aware
resolution (shallowest heading wins), and `_subtree_body`.

1.4.2 applied the same fix to the two checks that shared the defect and had been left behind —
`check_intent_ledger` and `check_term_before_definition`. On the nested fixture, `intent-uncovered`
was reporting against `1.1 現状` for an intent targeting `第1章 背景` (a false positive), and
`term-before-definition` was **silently missing a true positive**: with the chapter resolved too
early in the document, uses that really did precede the definition fell outside the comparison. That
second symptom is the worse one — a missed finding is indistinguishable from a clean pass.

Two process lessons, both about how this repository validates:

- **Fixture shape is a hidden assumption.** Every control here was flat because the repository's own
  documents are flat, so dogfooding could not surface it. A nested fixture is now part of the control
  set, and any check that resolves a spine reference to a section must be exercised against it.
- **A shared helper spreads a defect silently.** `_section_index` and `_section_body` are used by
  three checks; the fix landed on one. When a helper is corrected, every caller has to be re-tested,
  not just the one whose symptom was reported.

### 1.4.0 — the intent ledger, which generalises the whole skill

Prompted by an observation that named the skill's own centre: *while writing with an AI, the point of
a correction slides into something else partway through* — and then, immediately, that it is not only
corrections.

That is one failure, and every other rule here is a special case of it. Terminology drifts because it
lives only in the conversation; so does the **aim**. You set out to strengthen an argument, five turns
later you are polishing wording, and nothing announced the change because nothing was written down
that the new work would fail against.

Three things get called the same thing and their fixes differ:

- **意図のすり替わり** — the category changes. Fixing the argument becomes fixing the wording. A hard
  target is replaced by a tractable proxy; structurally, Goodhart.
- **意図の漂流** — the category holds, the target slides. "Make §3 clearer" becomes "make §3 shorter".
- **訂正の増殖** — the fix is done and the editing keeps going.

The measured mechanism behind the first is already in `failure-modes.md`: models "make assumptions in
early turns and prematurely attempt to generate final solutions, on which they overly rely", and
"when LLMs take a wrong turn in a conversation, they get lost and do not recover" (arXiv:2505.06120).
That reframes it. Usually the aim does not drift *partway*; it was misread *early* and never
recovered. Mid-course correction is not the fix — an anchor checkable from outside is.

Hence **rule 8** and the spine's **意図台帳**: before the work, one row — 対象 / なぜ / 完了条件. Three
deterministic checks follow, all about the *condition*, never about meaning:

| Check | Catches |
|---|---|
| `intent-unmeasurable` | No exit condition, or one that cannot be failed against ("もっと良くする") |
| `intent-uncovered` | The condition's subject words are absent from its target, or the target does not exist |
| `intent-open` | Still open — the working list carried across sessions |

`intent-unmeasurable` is the root-cause check. An aim you cannot fail against is an aim whose
substitution you will not notice, so the scanner refuses the vague ones up front rather than trying to
detect drift afterwards.

One false positive shaped the design. Exit conditions are often *structural* — "§4の冒頭に結論が1文で
置かれている" — and none of those words belong in the prose, so a presence test always fails on them. A
META_TERMS filter strips document-structure vocabulary (章, 冒頭, 段落, 結論, section, heading…); if
nothing is left, the condition is structural and the presence test does not apply at all.

The procedural half is `content-review.md` 手順D, and **D3 is the whole point**: say in one line what
you are making right now, and compare it to the 意図 column. If they differ, the drift already
happened. Then choose deliberately — return to the original aim, or update the ledger **with a note**.
Silently continuing is the only wrong answer, and rewriting the exit condition to match what you now
have is not an update; it makes the drift official instead of visible.

Scale boundary with `loop-goal`: same principle, different unit. There the 終了条件 must reduce to a
detector's exit code because a machine consumes it. Here the unit is one piece of writing and the
完了条件 is prose, so it is checked for *measurability*, not executed.

### 1.3.0 — the content layer, which was the actual gap

Through 1.2.x the skill had eleven checks and every one of them was a *surface* check. The audit
that prompted this release was blunt: technical metrics 8/8, meaning-and-context metrics 0 complete,
2 partial, 5 not started. Worse, rule 7 ("hand the human a numbered list") had no method behind it —
the loop said to produce the list and nothing said how. A rule with no procedure is a promise.

**Four deterministic content checks.** These ask a different question from everything above: not
*is the draft internally consistent* but *does the draft do what the spine said it would*. They read
the spine's `Outline`, `Claims`, `Glossary → First defined` and `Contract → Audience`, and they do
not run at all without `--spine` — the header says so rather than reading as a clean pass.

| Check | What it can actually tell you |
|---|---|
| `claim-coverage` | The section never names what its outline claim is about. Absence is strong; presence proves nothing |
| `unverified-claim` | The claim ledger still says unverified — extraction, not judgement, so it cannot be wrong |
| `term-before-definition` | A glossary term appears earlier than the section that defines it |
| `unsourced-assertion` | A sentence asserting established fact with no citation and no `[要確認]` |

None of them judges meaning. `claim-coverage` in particular is a *presence* test: a section can name
every term in its claim and still fail to land it. That limit is stated in the check's own message.

**`references/content-review.md` is the part that was mandatory.** Three procedures — per section
(A1–A5), per adjacent pair (B1–B3), whole document (C1–C3) — plus the rules for assembling the review
list. Its central constraint: **every question is answered with a verbatim quote from the draft or
the word 無し, never a rating.** A quote can be checked; a rating cannot, and asking a model to rate
its own long draft is precisely what rule 6 exists to prevent. The list is ordered by section rather
than severity (sorting by importance means the tail goes unread), one line per item, machine findings
and judgement findings tagged differently because their reliability differs, and sections cleared
with no findings are recorded explicitly — silence is otherwise indistinguishable from unchecked.

**`unsourced-assertion` was narrowed by measurement, not intuition.** The obvious marker list —
必ず / 常に / always / never — fired 13 times across seven real documents and *every hit was a
prescriptive rule*: "never parallel", "the scanner reports, never edits". A rule is not a claim and
needs no source. Narrowed to phrases that assert something was established (実証されている, proven,
studies show): zero false positives on the same seven documents, and 4/4 on seeded assertions, with
the cited one correctly silent.

Two bugs, both of the kind that reads as success:

- `"unverified"` contains `"verified"`, and the status test used substring matching — so every open
  claim in the ledger was silently marked done and the check reported nothing.
- The outline table's header row was not filtered (the guard looked at column 0, which is `#`), so
  the scan reported a missing section named "Section".

And the corrected `term-before-definition` immediately caught a real mismatch in this project's own
test fixtures, where the spine claimed a term was first defined in §3 while the draft used it in §1.
The fixture was wrong, not the check.

### 1.2.0 — a correction, a content check, and a measured backend

**The correction first, because it changed the policy.** 1.1.0 shipped with an argument that
statistical/ML tooling did not belong in the gate, resting on ContraDoc's finding that GPT-4 is
"still unreliable" at document self-contradiction. That argument was wrong in three ways, and the
user caught all three:

1. **Category error.** ContraDoc measured a *prompted* model. A fixed-weight NLI classifier is the
   same kind of artifact as a sentence embedder: deterministic, calibratable, with published
   precision/recall. The same paragraph of this document had already argued embeddings belong in the
   gate *because* they are deterministic — and then excluded NLI on grounds that only apply to
   prompted models.
2. **Stale evidence.** ContraDoc is a 2023-11 preprint being used to settle a 2026 design decision,
   against this document's own rule that anything load-bearing and older than a year gets re-checked.
3. **Half a quote.** The span reads "While GPT4 performs the best and **can outperform humans on
   this task**, we find that it is still unreliable…". Only the second clause was used.

The corrected line is not "AI vs tools" but **"fixed weights vs prompted"**. A tokenizer, an
embedder, and an NLI classifier are all eligible for a gate; a prompted judge is not. What decides
whether an eligible tool *ships* is its measured precision at the operating point, nothing else.

**Applying that policy immediately produced a check that needs no ML at all.** Numeric
cross-section inconsistency — §2 saying 200ms and §7 saying 500ms for the same labelled quantity —
is a genuine *content* check, deterministic, and cheap. It had been missed because "content needs
meaning" had been treated as one undifferentiated category. Tables and blockquotes are excluded
(tabulating different values is what a table is for), and a label must repeat verbatim across
sections, which keeps precision high.

**The optional SudachiPy backend was then measured rather than assumed, and the measurement moved
the recommendation.** The backlog had ranked janome first for being pure-Python. That was wrong:

| Capability | stdlib | SudachiPy |
|---|---|---|
| notation drift on variants outside the built-in table | 0 / 8 | **6 / 8** |
| register classification, 24-sentence battery | 23 / 24 | 24 / 24 |

The backend earns its place on **terminology, not register** — the suffix regex was already at
23/24 and gains one literary ending (「…すべし。」). Only SudachiPy has `normalized_form`, which is the
capability that matters, so the janome-first ranking was dropped.

The first cut of that backend was unusable and only testing showed it: grouping by lemma produced
**31 / 12 / 41 findings on three real documents, nearly all false**. A dictionary lemma folds three
things that are not notation drift, and each needed an explicit filter — verb conjugation
(書け/書か/書い → 書く), letter case (`is`/`IS`), and translation (`reading`/`leading` both normalize
to リーディング, and スタイル/`style`). After filtering: **6/8 recall, zero false positives across six
real documents**.

Two bugs surfaced in that same loop, both invisible from the output alone:

- The token tuple conflated `pos[1]` (subtype) with `pos[5]` (inflection), so the noun filter never
  matched and the whole notation check was **silently disabled**. Precision looked perfect because
  nothing ran. Recall and precision have to be measured together or a disabled check reads as a
  clean one.
- The "already in the table" guard skipped a group if *any* member appeared in the built-in pair
  table, so インターフェイス/インターフェース was dropped because インターフェース appears in the
  unrelated インターフェース/インタフェース pair.

The scan header now names the active backend and, either way, states what is **not** being looked at
(章間の矛盾・主旨の達成・根拠の有無). `--no-backend` forces the stdlib path for comparison.

Still deliberately absent: embeddings and NLI. Not on principle now — on sequence. Cross-section
contradiction is O(n²) in sentences, so it needs embedding-based candidate retrieval before entailment
is affordable; the two are one pipeline, not two options. Neither ships before its precision is
measured the way the tokenizer's was.

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
