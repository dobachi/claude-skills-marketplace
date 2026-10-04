# Expression and stance: what counts do not find

The language catalogs list symptoms a reader can point at and often count. This file covers the two layers above that: how things are put (expression) and who is speaking to whom (stance). A draft can pass every surface check and still fail here, and these are the layers a reader reacts to when they say a text "feels like AI" without being able to say why.

Each entry gives the symptom, why it reads as machine-made, the **test** that decides whether an instance stays, and the fix. Examples come in Japanese and English. The quoted phrases illustrate the habit and are not a ban list: the same words are fine when they pass the test. **Never add facts, numbers, names, or anecdotes that were not in the source** (SKILL.md guardrails); where the fix needs something the source lacks, flag it.

**Register note:** the default register is formal (memo, paper, report). Fix the cause and land in the document's own register.

## Contents

Expression
- E1. Contrast against nobody ("not X but Y")
- E2. Self-posed questions and reveal setups
- E3. Punchline closers
- E4. Significance attached afterwards
- E5. Challenges-and-outlook endings
- E6. Borrowed metaphors and personified abstractions
- E7. Praise words in place of description
- E8. Performed emotion
- E9. Elegant variation
- E10. Emphasis by marking
- E11. Vogue words

Stance
- S1. No reader in mind
- S2. Everything weighted equally
- S3. Could be about anything
- S4. No trace of a choice
- S5. The same distance from everything

Then: Questions for the author.

---

## Expression

### E1. Contrast against nobody ("not X but Y")

**Symptom:** 「AではなくBだ」「単なるAではない」「AというよりB」 / "It's not X, it's Y," "not just X but Y," "Y rather than X," used where no one has claimed X.
**Why:** the construction is for correcting a misconception. Used without one, it manufactures tension the content does not have, and repeated it becomes the dominant rhythm of the piece.
**Test (opponent):** does anyone in this document's world hold X — the reader, a cited source, the prevailing practice? If the source names that view, the contrast is real.
**Fix:** state Y directly. Keep the contrast where X is a real position, and then say whose it is if the source does.

Before: このフレームワークは単なる開発手法ではなく、組織文化そのものである。
After: このフレームワークは、開発手順に加えて、意思決定の進め方まで定めている。〔元文に根拠がある場合。無ければ `[要具体化: 「組織文化」とは具体的に何を指すか]`〕

Before: Governance isn't a compliance exercise — it's a strategic asset.
After: Governance decides who can approve access, and that decision sets how fast a project moves. (If the source supports it; otherwise flag.)

Real contrast, keep: 「従来の定義ではコネクタを通信部品とみなすが、本稿では契約の執行点として扱う。」 The negated view is named and held by someone.

### E2. Self-posed questions and reveal setups

**Symptom:** 「では、なぜか。答えはシンプルだ」「ここからが本題だ」「結論から言おう」「ポイントは一つ。」 / "So what does this mean?", "Here's the thing:", "The answer is simple:", "But here's where it gets interesting."
**Why:** the sentence stages a reveal instead of making it. It carries no information and treats the reader as an audience to be held.
**Test (deletion):** remove the setup. If the next sentence stands on its own, the setup was staging.
**Fix:** delete it and begin with the content. A question survives when it is one the reader really has at that point and the answer is not immediate.

Before: では、なぜ移行は進まないのか。答えはシンプルだ。互換性である。
After: 移行が進まない理由は互換性にある。

### E3. Punchline closers

**Symptom:** a paragraph or section ends on a short quotable generalization that restates it: 「結局、信頼がすべてである。」「余裕は最強の武器。」 / "And that makes all the difference." "In the end, trust is everything."
**Why:** it is the closing beat of a speech applied to every paragraph. One such line can land; a piece where every paragraph has one reads as a template.
**Test (deletion):** cut the last sentence. If the paragraph already made the point, the closer added only cadence.
**Fix:** end on the last sentence that carries content. Do not replace the closer with a different one.

### E4. Significance attached afterwards

**Symptom:** a fact followed by an interpretation the source does not support: 「〜を示している」「〜を浮き彫りにしている」「〜の象徴と言える」「〜を物語っている」 / ", highlighting…", ", underscoring…", ", reflecting a broader trend," "marks a pivotal moment," "plays a crucial role." Also crowning ordinary things: 「〜の本質は」「鍵を握る」「核心である」.
**Why:** it performs analysis without doing any. In a report it is worse than padding, because it is an unsupported claim dressed as an observation.
**Test:** is the interpretation stated or entailed by the source? Would the reader draw it unaided from the fact?
**Fix:** if supported, keep it and connect it to its support. If the reader would draw it anyway, cut it. If unsupported, take it out of the rewrite and flag it `[要出典: …]` / `[needs source: …]`.

Before: 参加企業は前年の2倍になっており、これは業界全体の意識変革を示している。
After: 参加企業は前年の2倍になった。 `[要出典: 「意識変革」と解釈する根拠]`

Before: The library was adopted by three teams, underscoring its pivotal role in the platform.
After: Three teams adopted the library.

### E5. Challenges-and-outlook endings

**Symptom:** 「課題は残るものの、今後の発展が期待される」「引き続き注視が必要である」 / "Despite these challenges, X continues to…", "The future looks promising."
**Why:** it closes without committing to anything. The challenges are unnamed and the outlook would fit any subject.
**Test (swap):** would the ending fit a document about a different subject? Then it says nothing about this one.
**Fix:** name the specific open problem from the source, or stop at the last substantive point and flag the removed forecast.

### E6. Borrowed metaphors and personified abstractions

**Symptom:** stock figures that did not grow from the subject: 羅針盤, 架け橋, 両刃の剣, 氷山の一角, 土台, 旅, 地図 / double-edged sword, north star, tapestry, building blocks, tip of the iceberg. Abstractions given agency or mood: 「データが語る」「静かに広がっている」「技術が寄り添う」 / "quietly reshaping," "the data tells a story."
**Why:** a metaphor earns its place by showing something the literal statement cannot. These fit any subject equally, which is how the reader knows nothing was observed.
**Test (strip, then swap):** remove the figure. Is the literal remainder complete? Would the same figure serve a different topic unchanged?
**Fix:** keep the literal statement. Do not look for a better metaphor. If the literal remainder is itself generic (「組織の知識をつなぐ」 after removing 羅針盤), remove the sentence and flag what it may have been meant to say. A figure the author clearly chose and built on in the text stays.

Before: 標準化は、データ連携という長い旅の羅針盤となる。
After: 標準化は、データ連携で何を先に決めるかの基準になる。〔元文にその趣旨がある場合〕

### E7. Praise words in place of description

**Symptom:** adjectives and adverbs that evaluate: 魅力的な, 豊かな, 優れた, 強力な, 見事に, 洗練された / vibrant, rich, seamless, stunning, robust, "boasts." The tone drifts toward a brochure whatever the subject.
**Why:** an evaluation asks the reader to take the writer's word. A description lets them judge.
**Test (strip):** delete the praise word. If something is lost, name what property it stood for.
**Fix:** replace it with that property when the source gives it; otherwise delete it. In a document whose purpose is to evaluate, an evaluation backed by its criteria stays.

Before: 本システムは強力で柔軟な検索機能を備えている。
After: 本システムの検索は、全文検索と属性による絞り込みを組み合わせられる。〔元文にある場合。無ければ形容詞を削るだけにする〕

### E8. Performed emotion

**Symptom:** generic feeling or empathy that would fit any topic: 「不安に感じる方も多いでしょう」「ワクワクしますね」「大変ですよね」 / "This can be deeply challenging," "It's exciting to see."
**Why:** it is emotion nobody is having. The reader recognizes the gesture.
**Test (swap):** would the sentence fit a different subject?
**Fix:** cut it. Keep a reaction the author reports as their own with a reason given in the source.

### E9. Elegant variation

**Symptom:** one referent under rotating names: ツール → ソリューション → 仕組み → プラットフォーム / "the tool… the solution… the platform… the offering."
**Why:** it comes from avoiding repetition. In technical and policy writing a reader takes a new term for a new thing.
**Test:** do the terms refer to the same thing?
**Fix:** one term per referent throughout. Repetition is correct here.

### E10. Emphasis by marking

**Symptom:** emphasis carried by typography rather than by the sentence: words set in 「」 or "" that are neither quotations nor defined terms, a colon before a held-back word, asides in parentheses on every other sentence, bold on phrases.
**Why:** the mark tells the reader a word matters without the sentence showing why.
**Test:** is the mark doing its ordinary job — quoting, defining, listing?
**Fix:** remove the mark. If the emphasis was needed, move the word to where the sentence stresses it.

### E11. Vogue words

**Symptom:** words that spread through generated text in one period: 解像度, 言語化, 刺さる, 〜が効く, 腹落ち / delve, tapestry, align with, "resonates."
**Why:** readers learn them as a signature. The list changes with each model generation, so a fixed list is out of date by the time it is written.
**Test:** would this author, writing for this venue, use the word unprompted?
**Fix:** use the plain word. Treat the examples above as a snapshot.

---

## Stance

Rewording repairs these only in part. The repair is often a question to the author, and the honest report says so.

### S1. No reader in mind

**Symptom:** basics explained to an expert audience; a point re-explained shortly after it was made; address to everyone (「初心者の方にも上級者の方にも」); anticipated reactions nobody has (「驚くかもしれませんが」「意外に思われるでしょう」, "You might be wondering…"); sudden friendliness (「〜ですよね」) in an otherwise neutral text.
**Why:** a person writes to someone. A model writes to the average of every possible reader, so no actual reader feels addressed.
**Test (addressee):** name the reader this sentence serves. Would they need it?
**Fix:** take the reader that the document type and venue imply (a design review is read by engineers on the project; a board memo by people who will decide). Cut what that reader knows; keep what they would have to look up. If the reader cannot be inferred, ask or flag `[要著者判断: 想定読者]`.

### S2. Everything weighted equally

**Symptom:** every section the same length; every list item one sentence of the same shape; advantages and disadvantages in matching number; nothing marked as the part that matters most.
**Why:** thinking about a subject makes a writer lopsided: one point gets three paragraphs and another a clause. Even coverage reads as a survey by someone with no view.
**Test (weight):** where does the space go, and is that where the author's main point is?
**Fix:** when the source or the author indicates the main point, give it the room and fold minor items into a sentence. This is rearrangement and compression. Deleting a supported claim is a content change: leave it in and propose the cut as `[要著者判断: 削除候補 …]`. If nothing indicates the main point, ask. Uneven evidence in the source (one item backed by a result, the others bare) is worth pointing out in that flag, but does not settle the question.

### S3. Could be about anything

**Symptom:** general statements true of the whole category; no fact particular to this project, team, or dataset; advice that would be given to anyone.
**Why:** it is what the text looks like when no one's thinking went through it. This is the layer where "AI-ness" stops being a style and becomes an absence.
**Test (swap):** replace the subject with another of its kind. If the paragraph still holds, it is generic.
**Fix:** move the particulars the source does contain to the front and cut the general statements they make redundant. If the source has none, the rewrite cannot supply them. Report it plainly and flag `[要具体化: …]`.

### S4. No trace of a choice

**Symptom:** every option presented and none preferred; nothing tried and dropped; the conclusion is "it depends" without saying on what.
**Why:** a decision leaves marks, such as what was rejected and why, and their absence signals that no decision was made.
**Test:** can you tell from the text what the author would do?
**Fix:** if the source states a preference or a result anywhere, lead with it. If "it depends" is the true answer, name what it depends on from the source. Otherwise ask; do not choose for the author.

### S5. The same distance from everything

**Symptom:** uniform warmth, uniform polish, uniform confidence across the whole piece. No sentence is rougher or more guarded than the rest.
**Why:** people are closer to some parts of their subject than others, and it shows.
**Test:** this one is noticed in the whole, not in a sentence.
**Fix:** do not add roughness — that is fabrication of a persona. The applicable move is protective: where the author's own text is uneven, blunt, or oddly phrased in a way that is theirs, leave it. In a draft that mixes the author's writing with generated passages, edit the generated passages toward the author's, never the reverse.

---

## Questions for the author

Ask only when stance causes dominate and the user is present. Ask at most three, in one message, and make each answerable in a line. Skip any the draft already answers.

日本語:
1. この文章は誰が読みますか。その人は何を既に知っていますか。
2. 一つだけ伝わればよいとしたら、どの点ですか。
3. 検討して採らなかった案や、書かずに外した点はありますか。

English:
1. Who reads this, and what do they already know?
2. If one point lands, which should it be?
3. Was anything considered and rejected, or left out on purpose?

Use the answers as source material: the named reader sets what to cut (S1), the one point sets the weighting (S2), the rejected options supply the trace of choice (S4). Do not extend an answer beyond what the author said. If the author declines or is unavailable, proceed with the rewrite and carry the open items as flags.
