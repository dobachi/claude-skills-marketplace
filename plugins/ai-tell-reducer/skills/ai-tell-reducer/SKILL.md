---
name: ai-tell-reducer
description: >-
  Reduce the "AI-ness" of a piece of writing — the patterns that make prose read as
  machine-generated (uniform sentence rhythm, reflexive hedging, vague abstraction,
  formulaic scaffolding, inflated vocabulary, and surface tics like em-dash / bold /
  rule-of-three overuse) — while preserving meaning, facts, register, and the author's
  voice, and WITHOUT fabricating anything. Works on Japanese and English text. Use
  whenever the user wants a draft to sound less like AI, more natural, or more human;
  when they mention "AIっぽさ" "AIっぽい文章" "AI感を消す/軽減" "人間らしく" "自然にリライト"
  "de-slop" "humanize" "sounds like ChatGPT/Claude" or "make this less robotic"; or when
  they hand over an AI-drafted text to polish. Also use proactively when reviewing or
  rewriting prose that clearly shows these tells, even if the user never names them.
---

# AI Tell Reducer

Make writing stop reading like a machine wrote it — without changing what it says, and without inventing anything to fill the gaps.

## The one idea

Most advice on this is a ban list: never write "delve," never use an em dash, never do the rule of three. Delete the flagged tokens and you get text that is *clean but nobody's* — the AI smell is gone and so is any voice. That is not the goal.

Three principles do the real work:

1. **Cause over symptom.** "Delve," "これにより," the em dash, "〜です。〜ます。" on repeat — these are symptoms. The causes are a small set of habits (below). Fix the cause and most symptoms disappear on their own; chase symptoms and the text stays hollow.
2. **Deliberate over autopilot.** Every so-called AI pattern is a legitimate tool a good writer chooses on purpose. A single tricolon is elegant; three stacked ones are pattern-failure. The test is never "does this pattern appear?" but "was it *chosen*, or did it run on autopilot?" Keep the deliberate instances; cut the reflexive ones.
3. **Form, not content.** This skill changes *how* something is said. It never adds facts, numbers, names, sources, or anecdotes to make prose feel lived-in. Humanizing by fabrication is the worst possible fix, especially for technical, policy, or academic writing.

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

## Workflow

1. **Read the whole thing first.** Identify the language (may be mixed JP/EN) and the author's evident voice. Fix the register per *Register calibration* above: assume formal/technical (memo, paper, report) unless the user signalled a post or blog. What the piece is *for* decides which fixes are in bounds.
2. **Diagnose root causes.** Walk the five causes below and mark which are actually present. Most drafts have two or three dominant ones, not all five. Then scan the matching language catalog for the concrete symptoms:
   - Japanese → `references/japanese-patterns.md`
   - English → `references/english-patterns.md`
   - Mixed → both, applied to the relevant spans.
3. **Rewrite, causes first.** Fix rhythm, stance, specificity, structure, and diction — then mop up the surface tics. Change the *minimum* that fixes the problem. Over-editing swaps one uniform texture for another. If a sentence already reads like a person wrote it, leave it alone.
4. **Verify** with three quick passes:
   - *Read-aloud test:* if a line isn't something the author would actually say out loud in this context, it's not fixed yet.
   - *So-what test:* for each paragraph, what does the reader know or do differently after it? If nothing, it's padding — cut or sharpen.
   - *Fabrication check:* re-scan the rewrite against the source. Every fact, number, and name must trace back. Delete anything that crept in.
5. **Report** (see Output). Lead with the result the user asked for; keep the process notes short; surface the flags.

## The six root causes

**1. Uniform rhythm (the most visible tell).**
AI writing clusters toward the average: every sentence medium-length, every paragraph three-to-four lines, the same subject-verb-object shape repeating. Human prose is uneven — a long winding sentence, then a short one that lands, then a medium one to breathe. *Fix:* vary sentence length and opening structure deliberately. Break at least one long sentence into a short punch; let at least one run longer. Vary how paragraphs start.

**2. No stance / reflexive hedging.**
Trained to be safe, models qualify everything ("may," "could," "often considered," "一概には言えませんが," "状況によって異なります") and present every side even when the content warrants a position. The result is temperature-free — you can't tell whose view it is. *Fix:* where the source actually supports a claim, state it plainly; cut the reflexive cushions. Keep hedges that mark *real* uncertainty — the goal is honest confidence, not manufactured swagger.

**3. Abstraction over specifics (the treadmill).**
The text hovers over an idea, restating it in slightly different words without advancing — 400 words of padding around 100 words of content. Vague nouns stand in for concrete things. *Fix:* cut restatement; make each sentence carry new information. Replace a vague word with the specific one *if it's recoverable from the source*. If it isn't, flag it — don't paper over the gap with more abstraction (and never invent the specific).

**4. Formulaic scaffolding.**
The intro announces itself ("本記事では…," "In this article…"), every section ends with a mini-summary, the body marches intro-point-point-point-conclusion, and the pedagogical voice hand-holds ("Let's explore," "まず〜について見ていきましょう"). *Fix:* delete the announcements and the redundant summaries. Start in the middle of the thought. Trust the reader.

**5. Inflated diction.**
Simple copulas become "serves as / stands as / represents"; plain verbs become "utilize / leverage / harness"; ordinary nouns get dressed up ("tapestry," "landscape," 「〜化」「情報設計」). It reads thesaurus-run. *Fix:* plainest accurate word wins. "is" over "serves as," "use" over "utilize," 「〜を使う」over「〜を活用していく」— unless the fancier word is genuinely the precise one.

**6. Meta-claims about the writing's own quality.**
The text asserts its own honesty, balance, or importance instead of demonstrating them: "正直に書きます," "誠実に検証しました," "we'll be objective here," "this is the most important section," "隠さず列挙します," "重要なので強調しておきます." This is the model satisfying "be trustworthy" as a *statement* rather than as a property of the content — and it backfires: a reader who is told the author is being honest starts wondering which parts weren't. It reads worst in reports and technical documents, where credibility is supposed to come from evidence. *Fix:* delete the claim and keep only what enacts it. Don't announce neutrality — present the counter-evidence. Don't say you'll list things openly — list them. Don't call a section valuable — show why the distinction matters. **Test:** if deleting the sentence removes no information, it was a claim, not content.

The two language catalogs turn each cause into specific, checkable before/after fixes for that language's particular tics (Japanese sentence-ending monotony, 読点 overuse, 英語直訳 metaphors; English vocab blacklist, "It's not X, it's Y," em-dash and bold-list overuse). Read the relevant one before rewriting.

## Output

Adapt to what the user asked for. Default when they hand over a draft to fix:

1. **The rewrite, first and clean.** No track-changes markup inside it. If the source was a file, write the result to a file; if it was inline and short, inline is fine.
2. **What changed (brief).** A few lines naming the dominant causes you found and the moves you made — not a line-by-line diff. Enough that the author understands the edit and can push back.
3. **Flags (only if any).** Places where the honest fix needs the author: a vague claim that needs a real specific, a hedge you weren't sure was load-bearing, a stance you softened because you couldn't tell if the source backed it. Mark inline in the report as `[要具体化: …]` / `[needs specific: …]` — never filled with invented content.

If the user only wants a **diagnosis** ("what makes this sound like AI?"), skip the rewrite: name the causes with short quoted examples from their text and the fix for each. If they want a **before/after study**, pair a handful of representative lines.

Do not bury the rewrite under process narration. The author wants the fixed text, then a short why — in that order.

## Worked example (miniature, formal default)

Source (JP, research-report register, 常体): 「本節では、データスペースにおける相互運用性の課題について整理する。相互運用性は、極めて重要な要素である。これにより、異なる組織間でのデータ交換が円滑化される。多くの場合、標準化がその鍵を握ると言えるだろう。」

Diagnosis: formulaic announcement (本節では…整理する), abstract inflation (極めて重要な要素), 「これにより」+ nominalized passive (円滑化される), reflexive hedge closing the author's own claim (多くの場合…と言えるだろう).

Rewrite: 「相互運用性は、組織を越えたデータ交換が成立するか否かを左右する。形式が異なるまま接続できなければ、交換は始まらない。その成否を大きく規定するのは標準化である。」

What changed: cut the self-announcement and opened on the claim; replaced abstract "極めて重要な要素" with what that importance *consists of* (交換の成否を左右する) — recoverable from the source's own logic, not invented; removed 「これにより」and the nominalized passive 円滑化される; varied sentence length; committed the final claim by dropping "多くの場合…と言えるだろう" (the source already asserted it — this removes a reflexive hedge, not a real one). Stayed in 常体; added no facts, no citations.

Note the restraint: nothing was made chattier. No contractions, no first person, no fragments-as-punch — those would fix the AI smell by *breaking* the report register. And had 標準化's role actually required outside support, the move would be to flag `[要出典: 標準化が成否を規定する根拠]`, never to attach an invented "研究によれば."
