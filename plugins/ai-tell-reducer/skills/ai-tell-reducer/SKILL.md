---
name: ai-tell-reducer
description: >-
  Reduce the "AI-ness" of writing while preserving meaning, facts, register, and the
  author's voice, without fabricating anything. Diagnoses three layers: surface (uniform
  rhythm, scaffolding, em-dash / bold / rule-of-three tics), expression (rhetoric with no
  occasion such as "not X but Y", significance attached to plain facts, borrowed
  metaphors, inflated vocabulary), and stance (reflexive hedging, no reader in mind,
  everything weighted equally). Judges by effect on the reader, not by counts. Works on
  Japanese and English; for Japanese it also removes English-shaped phrasing (翻訳調):
  inanimate subjects, surplus pronouns, calqued idioms, literal English syntax, katakana.
  Use when the user wants a draft to sound less like AI or more natural; when they say
  "AIっぽさ" "AI感を消す" "人間らしく" "自然にリライト" "翻訳調" "英語っぽい日本語"
  "日本語として不自然" "de-slop" "humanize" or "sounds like ChatGPT"; or when they hand
  over an AI-drafted text to polish. Also use proactively on prose that clearly shows
  these tells.
---

# AI Tell Reducer

Make writing stop reading like a machine wrote it — without changing what it says, and without inventing anything to fill the gaps.

## The one idea

Most advice on this is a ban list: never write "delve," never use an em dash, never do the rule of three. Delete the flagged tokens and you get text that is *clean but nobody's* — the AI smell is gone and so is any voice. That is not the goal.

Four principles do the real work:

1. **Cause over symptom.** "Delve," "これにより," the em dash, "〜です。〜ます。" on repeat — these are symptoms. The causes are a small set of habits (below). Fix the cause and most symptoms disappear on their own; chase symptoms and the text stays hollow.
2. **Deliberate over autopilot.** Every so-called AI pattern is a legitimate tool a good writer chooses on purpose. A single tricolon is elegant; three stacked ones are pattern-failure. The test is never "does this pattern appear?" but "was it *chosen*, or did it run on autopilot?" Keep the deliberate instances; cut the reflexive ones.
3. **Effect over count.** A count ("three identical sentence endings," "two dashes in a paragraph") is how you *notice* a place worth looking at. It is never how you decide. Counts differ by model, genre, and year — the flagged vocabulary of one model generation is gone in the next, and a pattern that marks AI in a report (no 体言止め at all) is the opposite of the one that marks it in a social post (体言止め in every line). Decide with the tests below, which ask what a sentence does for its reader. A draft that passes every count can still read as machine-made, and a draft edited to pass counts acquires a new uniform texture.
4. **Form, not content.** This skill changes *how* something is said. It never adds facts, numbers, names, sources, or anecdotes to make prose feel lived-in. Humanizing by fabrication is the worst possible fix, especially for technical, policy, or academic writing.

## Guardrails (never violate)

- **Do not fabricate.** No new facts, figures, dates, proper nouns, citations, quotes, examples, or claims that were not in the source. Sharpen and concretize only from what is already there or strictly entailed. Where a passage is vague *because a specific is genuinely missing*, do not invent one — flag it (see Output) so the author can supply it.
- **Preserve meaning and every load-bearing claim.** Numbers, named entities, hedges that carry real epistemic weight, and technical terms stay intact. Removing a reflexive "一般的に" is fine; removing a "roughly" that marks genuine uncertainty is not.
- **Preserve register and voice.** Match the source's formality, person (first/third), and domain. A formal standards memo stays a formal standards memo — do not "humanize" it into a coffee-chat. If the author has a voice already, amplify it; don't overwrite it with a generic-friendly one.
- **This is not detector evasion.** The aim is prose a sharp human would be happy to publish — readable, specific, with a pulse. Do not add typos, unicode tricks, or noise to game an AI detector. If the user's actual goal is beating a detector, say plainly that this skill optimizes for quality, not evasion, and that the two only partly overlap.

## Register calibration (read before rewriting)

**Default register is formal and technical: internal memos, papers, research reports.** Treat that as the baseline. Casual or social-post register (LinkedIn, blog) unlocks extra tools — but only when the user explicitly asks for it.

This matters because most published "humanize your AI writing" advice is written for blogs and marketing, and its signature moves are *wrong* for formal work. In a memo, paper, or report, the following are not de-AI fixes — they are register damage:

- contractions and colloquialisms dropped in for flavor
- first/second person ("I think," "you'll notice") inserted as a *device* where the document doesn't already use it
- one-word sentence fragments as rhetorical "punches"
- chatty openers ("Here's the thing," "Turns out…") and rhetorical questions to the reader
- emotional stakes-raising

The AI tells still get fixed in formal prose — but with the **formal toolkit**:

- **Cut reflexive hedges** to state what the evidence supports. In a paper, confidence comes from precision and citation, not swagger. Keep every hedge that marks genuine methodological uncertainty or a real limit on the claim.
- **Kill treadmill restatement.** Formal writing earns trust through information density; padding reads as AI *and* as weak scholarship.
- **Deflate diction toward the precise word, not the chatty one.** "use" over "utilize," yes — but the target is exact technical vocabulary, not conversational vocabulary. Formal ≠ inflated, and formal ≠ casual.
- **Vary sentence length within formal bounds.** A short declarative sentence is still formal. Rhythm comes from varying length, not from fragments or slang.
- **Break formulaic scaffolding** — cut "In this section we will…" and per-section recaps — while keeping the genuine signposting a long report needs. A real "Section 3 evaluates…" that orients the reader is not the empty AI recap that restates what was just said.
- **Replace ghost citations** ("studies show," "研究によれば") with a real source, or flag for the author. Non-negotiable in papers and reports.
- **Prefer active voice and named agents** where the field allows — but many academic venues expect measured passive constructions, so follow the discipline's convention rather than stripping every passive.

When the user *does* ask for LinkedIn/blog register, the casual tools come back on the table: contractions, first/second person, fragments, a conversational opener. Match the platform — but the guardrails (no fabrication, preserve claims) never relax.

**Japanese:** keep the document's own 常体（だ・である）/ 敬体（です・ます）. Papers and many reports use 常体; internal memos vary. Never switch between them just to manufacture rhythm.

**Japanese that thinks in English.** Japanese model output often keeps English structure under Japanese words: an inanimate subject acting on people (「このデータは私たちに〜を教えてくれる」), pronouns English cannot drop (「それは」「私たちの」「あなたのチーム」), light-verb calques (「影響を持つ」「アクションを取る」), translated idioms (「一日の終わりに」「同じページにいる」), chat set phrases (「素晴らしい質問ですね」「お役に立てれば幸いです」), and English punctuation in running text (「——」, a colon before the punchline). Fix these in every register: the test is whether a writer thinking in Japanese from the start would have written it this way. Keep established loanwords, field terminology, and phrasing the author evidently chose. Faithfulness of an actual translation belongs to `faithful-translation`, not here. Catalog and tests: `references/japanese-translationese.md`.

## Workflow

1. **Read the whole thing first.** Identify the language (may be mixed JP/EN) and the author's evident voice. Fix the register per *Register calibration* above: assume formal/technical (memo, paper, report) unless the user signalled a post or blog. What the piece is *for* decides which fixes are in bounds.
2. **Diagnose in three layers, stance first.** Walk the causes below from the top layer down and mark which are actually present. Most drafts have two or three dominant ones. The order matters: if the stance layer is where the draft fails, polishing its surface produces a smoother version of the same empty text — say so in the report rather than hiding it under a clean rewrite. Then read the matching references:
   - Expression and stance, both languages → `references/expression-and-stance.md`
   - Japanese surface symptoms → `references/japanese-patterns.md`
   - Japanese that reads as translated from English (翻訳調) → `references/japanese-translationese.md`. Read it for every Japanese text, not only when the user mentions it: English-shaped phrasing is one of the most common reasons Japanese model output reads as machine-made.
   - English surface symptoms → `references/english-patterns.md`
3. **Ask the author, when the fix needs them (optional).** Several stance causes cannot be repaired by rewording, because what is missing is the author's own choice: who the reader is, which point matters most, what was considered and dropped. If the user is present and those causes dominate, ask up to three short questions before rewriting (wording in `references/expression-and-stance.md`). Their answers are source material, so using them is not fabrication. If the user is not available, or the skill was invoked by another skill, do not stop — rewrite what form can fix and flag the rest.
4. **Rewrite, causes first.** Fix stance and expression, then rhythm and structure, then mop up the surface tics. Change the *minimum* that fixes the problem. Minimum applies to sentences that survive the tests; a sentence that fails them goes, even when that shortens the text a great deal. If a sentence already reads like a person wrote it, leave it alone — and leave the author's own odd-but-theirs phrasing alone too.
5. **Verify** with four passes:
   - *Read-aloud test:* if a line isn't something the author would actually say out loud in this context, it's not fixed yet.
   - *So-what test:* for each paragraph, what does the reader know or do differently after it? If nothing, it's padding — cut or sharpen.
   - *Over-correction check:* has the rewrite traded one template for another? Look for the replacement patterns listed under *Over-correction* below.
   - *Fabrication check:* re-scan the rewrite against the source. Every fact, number, and name must trace back. Delete anything that crept in.
6. **Report** (see Output). Lead with the result the user asked for; keep the process notes short; surface the flags.

## The tests

These decide whether an instance stays. Each asks about the reader, and none of them is a count.

| Test | Ask | If the answer is no |
|---|---|---|
| Deletion | Does removing this sentence lose information? | It was framing, a claim about the writing, or restatement. Cut it. |
| Swap | Would this sentence stop being true if the subject were swapped for a different product, project, or topic? | It is generic. Tie it to this subject from the source, or flag it. |
| Opponent | Does anyone in this document's world actually hold the view being negated ("not X but Y")? | The contrast is manufactured. State Y directly. |
| Strip | With the metaphor or praise word removed, is something concrete left? | The figure was the whole sentence. Remove it and flag what it may have meant. If something concrete is left, keep that plain version. |
| Addressee | Can you name who this sentence is for, and would that reader need it? | It is written to nobody, or to everybody. Cut or retarget. |
| Weight | Does the space go to the point the author most needs to make? | Everything is weighted equally. Rebalance, or ask which point is the main one. |

### Cut, or flag?

The tests say a sentence should go. What happens next depends on whether it asserts anything:

- **It asserts nothing** (an announcement, a reveal setup, a restated closer): cut it. No flag.
- **It asserts something the source does not support** (an attached interpretation, a forecast, praise, a metaphor with a vague claim inside it): take it out of the rewrite *and* list it as a flag, quoting the original, so the author sees what went and can restore it with support.
- **It asserts something the source does support, and you think the document is better without it:** leave it in the rewrite and propose the cut as a flag. Removing a supported claim is the author's decision.

Deleting framing can also remove something the author meant. An announcement may be the only statement of a section's scope, and a self-posed question may raise a point the text never answers. When the deletion exposes a mismatch like that, flag it. Problems of argument or structure noticed along the way belong to `doc-review` and `doc-refactor`: name them in the report and do not fix them here.

## The root causes

Twelve causes in three layers. The surface layer is what a count can find. The other two are what a reader actually reacts to, and no count finds them.

### Stance: who is speaking, to whom

**1. No stance / reflexive hedging.**
Trained to be safe, models qualify everything ("may," "could," "often considered," "一概には言えませんが," "状況によって異なります") and present every side even when the content warrants a position. The result is temperature-free — you can't tell whose view it is. *Fix:* where the source actually supports a claim, state it plainly; cut the reflexive cushions. Keep hedges that mark *real* uncertainty — the goal is honest confidence, not manufactured swagger.

**2. No reader in mind.**
The text addresses everyone at once: it explains basics to an expert audience, re-explains what it said two paragraphs ago, anticipates reactions nobody has ("驚くかもしれませんが," "you might be wondering"), or turns suddenly friendly ("〜ですよね"). A person writes to someone; a model writes to the average of all possible readers. *Fix:* take the reader the document and venue imply, and cut what that reader already knows. If the reader cannot be determined, ask or flag.

**3. Everything weighted equally.**
Every item gets the same length and the same level of detail; pros and cons balance exactly; nothing is marked as the part that matters. A person who has thought about a subject is lopsided about it. *Fix:* give the main point the room and compress the minor ones into a clause — when the source or the author says which is which. If the source only hints at it (one item has evidence and the others have none), that is a reason to flag the question, not a licence to choose. Compression is a form change. Dropping a claim is not, so propose cuts as flags.

**4. Could be about anything.**
The sentences survive the swap test: no fact particular to this project, no reason this was written, no sign of anything tried and rejected. This is the absence of thought rather than a fault of style, and it is the cause rewording can do least about. *Fix:* pull forward whatever particulars the source does contain. Beyond that, ask the author or flag — never supply a motive, an anecdote, or a preference on their behalf.

### Expression: how things are put

**5. Rhetoric with no occasion.**
Rhetorical figures fire where nothing calls for them: "not X but Y" against a view nobody holds ("単なるツールではなく、〜だ"), a self-posed question answered at once ("では、なぜか。答えはシンプルだ"), an aphorism closing every paragraph, an empty pivot ("ここからが本題だ," "Here's where it gets interesting"). The devices are sound; what is missing is the judgment about when a moment deserves one. *Fix:* say the thing directly. Keep a figure only where the tension it resolves is real.

**6. Significance attached afterwards.**
A plain fact gets an interpretation bolted on: "〜を示している," "〜を浮き彫りにする," "〜の象徴である," ", highlighting…," "marks a pivotal moment." Ordinary things are crowned "本質," "鍵," "核心." The ending gestures at challenges and a bright future. *Fix:* keep the interpretation only if the source supports it, and then tie it to that support. Otherwise leave the fact to stand alone, or flag.

**7. Borrowed imagery and praise.**
Metaphors arrive ready-made rather than from the subject (羅針盤, 架け橋, 両刃の剣, tapestry, north star), abstractions get personified ("データが語る," "静かに広がる"), and adjectives evaluate instead of describing (魅力的, 豊かな, seamless, vibrant). Generic emotional language is the same failure in another key. *Fix:* apply the strip test. Replace praise with the property that earned it, if the source has it.

**8. Abstraction over specifics (the treadmill).**
The text hovers over an idea, restating it in slightly different words without advancing — 400 words of padding around 100 words of content. Vague nouns stand in for concrete things. *Fix:* cut restatement; make each sentence carry new information. Replace a vague word with the specific one *if it's recoverable from the source*. If it isn't, flag it — don't paper over the gap with more abstraction (and never invent the specific).

**9. Inflated diction.**
Simple copulas become "serves as / stands as / represents"; plain verbs become "utilize / leverage / harness"; ordinary nouns get dressed up ("tapestry," "landscape," 「〜化」「情報設計」). It reads thesaurus-run. *Fix:* plainest accurate word wins. "is" over "serves as," "use" over "utilize," 「〜を使う」over「〜を活用していく」— unless the fancier word is genuinely the precise one. Word lists date quickly, so treat any list as examples of the habit rather than as the definition of it.

**10. Meta-claims about the writing's own quality.**
The text asserts its own honesty, balance, or importance instead of demonstrating them: "正直に書きます," "誠実に検証しました," "we'll be objective here," "this is the most important section," "隠さず列挙します," "重要なので強調しておきます." This is the model satisfying "be trustworthy" as a *statement* rather than as a property of the content — and it backfires: a reader who is told the author is being honest starts wondering which parts weren't. It reads worst in reports and technical documents, where credibility is supposed to come from evidence. *Fix:* delete the claim and keep only what enacts it. Don't announce neutrality — present the counter-evidence. Don't say you'll list things openly — list them. Don't call a section valuable — show why the distinction matters.

### Surface: what a count can find

**11. Uniform rhythm.**
AI writing clusters toward the average: every sentence medium-length, every paragraph three-to-four lines, the same subject-verb-object shape repeating. Human prose is uneven. *Fix:* let length follow content — a point that needs qualification runs long, a conclusion can be short. Do not vary length for its own sake: a run of short sentences is as uniform as a run of medium ones.

**12. Formulaic scaffolding.**
The intro announces itself ("本記事では…," "In this article…"), every section ends with a mini-summary, the body marches intro-point-point-point-conclusion, and the pedagogical voice hand-holds ("Let's explore," "まず〜について見ていきましょう"). *Fix:* delete the announcements and the redundant summaries. Start in the middle of the thought. Trust the reader.

The language catalogs turn the surface causes, and the language-specific forms of the others, into checkable before/after fixes (Japanese sentence-ending monotony, 読点 overuse, 英語直訳 metaphors; English vocabulary, em-dash and bold-list overuse). Japanese written in English patterns — syntax, idioms, set phrases, katakana, punctuation — has its own catalog, because it cuts across causes 5, 7, 9 and 11 and needs a different test (would a writer thinking in Japanese have written this?).

## Over-correction

A rewrite that removes one template usually installs another. Before reporting, check that the result has not become any of these:

- **Staccato.** Runs of short declaratives, or 体言止め used as a punchline. In social posts this is itself a recognized AI voice.
- **Synonym swap.** "leverage" became "utilize"; "まとめると" became "要するに"; "not X but Y" became "Y rather than X." The habit is intact.
- **New decoration.** One stock metaphor replaced by another; a deleted closer replaced by a different quotable line.
- **Grafted persona.** A first-person voice, an anecdote, an opinion, or slang that the source did not have.
- **Casualized register.** A report that now reads like a blog post.
- **Stripped structure.** Signposting a long document genuinely needed has been deleted along with the empty kind.
- **Sanded-off author.** The author's own idiosyncratic phrasing was normalized. Unevenness that belongs to the author is not a tell.
- **Over-Japanized.** A calqued English idiom replaced with a Japanese proverb, established loanwords (レイテンシ, ワークロード) forced into native words, or subjects dropped where who-does-what is the point.

## Output

Adapt to what the user asked for. Write the report in the language the user wrote their request in. Default when they hand over a draft to fix:

1. **The rewrite, first and clean.** No track-changes markup inside it. If the source was a file, write the result to a file; if it was inline and short, inline is fine.
2. **What changed (brief).** A few lines naming the dominant causes you found, by layer, and the moves you made — not a line-by-line diff. Enough that the author understands the edit and can push back. If whole sentences or paragraphs were removed, say so first and say what they were. If the stance layer is the real problem and the rewrite could only partly address it, say that here.
3. **Flags (only if any).** Places where the honest fix needs the author. List them after the rewrite, each quoting the span it concerns; the rewrite itself stays free of markup. Never fill a flag with invented content:
   - `[要具体化: …]` / `[needs specific: …]` — a vague claim that needs a real specific.
   - `[要出典: …]` / `[needs source: …]` — an attribution or interpretation with no support in the source.
   - `[要著者判断: …]` / `[author call: …]` — a choice only the author can make: the intended reader, which point is the main one, whether a hedge is load-bearing, a proposed cut, or something the rewrite dropped that the author may have meant.

If the user only wants a **diagnosis** ("what makes this sound like AI?"), skip the rewrite: name the causes by layer with short quoted examples from their text and the fix for each. If they want a **before/after study**, pair a handful of representative lines.

Do not bury the rewrite under process narration. The author wants the fixed text, then a short why — in that order.

## Worked examples (miniature, formal default)

**Surface and stance.** Source (JP, research-report register, 常体): 「本節では、データスペースにおける相互運用性の課題について整理する。相互運用性は、極めて重要な要素である。これにより、異なる組織間でのデータ交換が円滑化される。多くの場合、標準化がその鍵を握ると言えるだろう。」

Diagnosis: formulaic announcement (本節では…整理する), abstract inflation (極めて重要な要素), 「これにより」+ nominalized passive (円滑化される), reflexive hedge closing the author's own claim (多くの場合…と言えるだろう).

Rewrite: 「相互運用性は、組織を越えたデータ交換が成立するか否かを左右する。形式が異なるまま接続できなければ、交換は始まらない。その成否を大きく規定するのは標準化である。」

What changed: cut the self-announcement and opened on the claim; replaced abstract "極めて重要な要素" with what that importance *consists of* (交換の成否を左右する) — recoverable from the source's own logic, not invented; removed 「これにより」and the nominalized passive 円滑化される; committed the final claim by dropping "多くの場合…と言えるだろう" (the source already asserted it — this removes a reflexive hedge, not a real one). Stayed in 常体; added no facts, no citations.

Note the restraint: nothing was made chattier. No contractions, no first person, no fragments-as-punch — those would fix the AI smell by *breaking* the report register. And had 標準化's role actually required outside support, the move would be to flag `[要出典: 標準化が成否を規定する根拠]`, never to attach an invented "研究によれば."

**Expression.** Source (JP, same register): 「本ツールは単なる変換器ではない。部門間のデータをつなぐ架け橋である。導入企業は増えており、これはデータ活用の重要性の高まりを示している。」

Diagnosis: a contrast against a view nobody in the document holds (単なる変換器ではない — opponent test fails), a borrowed metaphor (架け橋 — the strip test leaves "部門間のデータをつなぐ"), and significance attached to a fact with no support in the source (〜の高まりを示している). No count would flag this passage: its sentence lengths vary and it contains no listed word.

Rewrite: 「本ツールは、変換によって部門間のデータをつなぐ。導入企業は増えている。」
Flag: `[要出典: 導入増が「データ活用の重要性の高まり」を示すという解釈の根拠]`

The rewrite is shorter and plainer than the source, and that is the correct result. Resist putting a new flourish where the old one was.
