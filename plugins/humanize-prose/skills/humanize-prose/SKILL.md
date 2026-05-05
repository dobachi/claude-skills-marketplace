---
name: humanize-prose
description: Rewrite AI-generated or AI-assisted text so it reads as human-authored. Identifies and removes common AI tells (em-dash overuse, "delve"/"leverage", tricolons, reflex bullet lists, "いかがでしたでしょうか", generic openers/closers) while preserving meaning, register, and factual content. Bilingual — English and Japanese. Reader-experience focused, not AI-detector evasion. Triggers when the user asks to "humanize," "make less AI-sounding," "rewrite this AI draft," "AIっぽさを取りたい," "人間らしく," or supplies text marked as AI-generated.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Humanize Prose

Rewrite text that sounds machine-generated into prose that reads as written by a human, in either English or Japanese.

## Operating Principle

The goal is **reader experience**, not detector evasion.

- A reader should not get the "this was written by AI" feeling. That is the only success criterion.
- AI detection tools (GPTZero, Originality.ai, etc.) are unreliable — they false-positive on careful human writing and false-negative on sloppy AI output. This skill does not target them and offers no guarantees against them.
- **Preserve** meaning, factual claims, register (formal vs casual), and any technical precision. Only style changes.

If you cannot improve the text without changing its meaning, say so and stop.

## When to Activate

- The user asks to "humanize," "make less AI-sounding," "rewrite," "fix AI style," "AIっぽさを軽減," "人間らしく," "自然な文章に."
- The user supplies text and says it was AI-generated or AI-assisted.
- You see a block of prose with multiple AI tells stacked: tricolon-heavy, em-dash-rich, bullet-reflexive, generic-opener-and-closer.

When you activate, briefly state the register you detected and the strategy strength so the user can redirect.

## Workflow

### Step 1 — Register detection

Classify the input into one of three registers:

| Register | Cues | Rewrite strength |
|----------|------|------------------|
| **Casual** (blog, essay, SNS) | Personal voice expected, contractions OK, opinions welcome | High |
| **Business** (memo, report, email) | Formal but plain, no slang, third-person leaning | Medium |
| **Technical/academic** (paper, doc, spec) | Precision-first, hedges are caveats not filler, may include math/code | Low |

When the input is mixed, choose the dominant register and flag the inconsistency in the response.

### Step 2 — Surface AI tells

Read through and list each instance you find, organized by category. Quote a short span and label the category — vocabulary, phrasing, structure, punctuation, opener/closer. Keep this list concise (one line per tell).

### Step 3 — Rewrite

Apply the strategies below at the strength matching the register. Do not over-rewrite — if a sentence is already natural, leave it.

### Step 4 — Self-check

Before returning, confirm:

- Same meaning? (No claims added or dropped.)
- Same facts? (Numbers, names, dates, citations all preserved.)
- Same register? (Did not casualize a formal document or stiffen a casual one.)
- No new AI tells introduced? (Did not produce choppy short-sentence runs or saccharine informality as an over-correction.)
- Reads aloud as one human voice?

## Rewrite Strategies (10)

These apply to both languages unless noted.

**S1 — Strip filler intros.** Remove "It's important to note that," "Essentially," "Fundamentally," "In essence," "When it comes to X." JP: 「〜することが重要です」「〜が大切です」「結論から申し上げますと」. Move the substantive content to the front.

**S2 — Reduce tricolons.** LLMs love `X, Y, and Z`. Most of the time, two items or one is enough. If three are genuinely needed, keep them.

**S3 — Vary sentence length deliberately.** Mix short and long. AI output tends to converge on a uniform middle length. A two-word sentence next to a 30-word one is fine — sometimes better.

**S4 — Replace abstractions with specifics.** "Many users" → "37 users" if you have the number. "Various sources" → name them. **Never invent specifics.** If the original lacked them and you don't have them, leave the abstraction or hedge it explicitly.

**S5 — Cut em-dash overuse.** LLMs scatter em-dashes (—) like punctuation confetti. Use commas, colons, parentheses, or sentence breaks instead. JP: avoid using ダッシュ as a generic separator; use 読点・句点 or 括弧.

**S6 — Replace clichéd vocabulary.** See `references/ai-tells-en.md` and `references/ai-tells-ja.md` for word-by-word substitution tables. Common offenders: *delve, leverage, robust, comprehensive, multifaceted, holistic, intricate, tapestry, realm, landscape, ever-evolving, navigate*.

**S7 — Convert reflex bullets to prose.** AI output reaches for bullet lists even when prose would flow better. If a list has 3 items that are actually one continuous idea, write the prose. Keep bullets for genuinely parallel, scannable, or numerically-meaningful lists.

**S8 — Drop generic closers.** Cut "In conclusion," "Ultimately," "All in all," "In summary." JP: 「まとめ」「最後に」「以上のように」「いかがでしたでしょうか」. Let the last concrete point be the ending.

**S9 — Allow contractions / particle variation (register-permitting).** EN casual: "do not" → "don't," "we are" → "we're." JP casual: 終助詞・口語的助詞のゆらぎ（「〜だ」「〜だよ」「〜だね」「〜なんだ」など）. Skip this in formal/technical text.

**S10 — Allow asymmetry.** Vary paragraph length. Insert a parenthetical aside. Use a sentence fragment for emphasis. Genuine human writing isn't perfectly balanced — AI output usually is.

## Register-Specific Calibration

### Casual (blog / essay / SNS) — strength: high

Apply all ten strategies. Encourage:
- First-person voice and explicit opinion ("I find," "私は〜と思う")
- Sentence fragments for emphasis
- Colloquial diction
- Personal anecdote or aside
- Mixed paragraph lengths
- Contractions / 口語助詞

### Business (memo, report, email) — strength: medium

Apply S1, S2, S5, S6, S7, S8 fully. Hold back on S9 (contractions optional, register-dependent) and S10 (keep paragraphs reasonably structured). Aim for direct, plain formal prose. Goals:
- No empty hedges
- No tricolons
- Concrete numbers and named entities
- Short paragraphs that say one thing each

### Technical / academic — strength: low

Be conservative. Apply S1, S6, S7, S8 — these target style without touching precision. **Do not** apply:
- S4 if it would invent specifics that aren't in the source
- S9 (contractions are jarring in formal academic prose; English math papers don't use them)
- S10 to the point of choppiness

Important distinction: **technical hedges are not AI tells.** Phrases like "may indicate," "appears to," "we conjecture," 「〜と考えられる」「〜と推測される」 are precision tools in technical writing. Leave them. Strip only the empty filler hedges (S1).

## Output Format

For short inputs (under ~200 words / 400 字), return the rewrite directly with a one-line note about register and strategy strength applied.

For longer inputs, return three blocks:

```
## Detected register
<casual / business / technical>, strength <high/medium/low>

## AI tells found
- L3 (vocabulary): "delve into the multifaceted realm" → cliché stack
- L7 (closer): "In conclusion, …" → generic closer
- L9 (structure): three reflex bullets describing one continuous idea
- ...

## Rewrite
<rewritten text>

## Preservation check
- Meaning: preserved
- Facts (numbers, names): preserved (none in source)
- Register: preserved (business)
- Notes: tightened paragraph 2; merged bullets into prose
```

If the user explicitly asks for a diff, provide a before/after table for each changed sentence.

## Anti-Patterns (failure modes of the rewriter)

- **Over-casualizing formal text** — turning a board-meeting memo into a tweet. Match the original register.
- **Inventing specifics** — replacing "many studies" with "27 studies" when the source didn't say 27. This is fabrication. Either keep the abstraction, or hedge ("a number of studies").
- **Removing necessary technical hedges** — "may indicate" in a paper is a precision claim, not filler.
- **Choppy over-correction** — varying sentence length so aggressively that the result becomes a series of stubs.
- **Introducing new tells** — replacing "leverage" with "utilize" (still bizspeak), replacing "in conclusion" with "in summary" (still a generic closer). Aim for actual prose, not a synonym swap.
- **Personality grafting** — stamping a fake voice onto neutral text. If the original had no personal voice, don't fabricate one.

## References

- `references/ai-tells-en.md` — English AI tell catalog: vocabulary / phrasing / structure / punctuation / closers, with concrete replacements.
- `references/ai-tells-ja.md` — Japanese AI tell catalog: 常套句 / 語尾 / 構文 / 形式名詞 / 開始・終結 / 段落構造, 置換例つき.

Consult these as a checklist when running Step 2 (surface AI tells).

## A Note on AI Detectors

Tools like GPTZero, Originality.ai, ZeroGPT measure surface statistical features (perplexity, burstiness) that correlate weakly with AI authorship. They false-positive on:
- Careful, edited human writing
- Non-native English
- Highly structured technical writing

And false-negative on:
- AI output that has been even lightly edited
- Newer or fine-tuned models

This skill **does not target detector scores** and offers no guarantee they will go down. The aim is the human reader's perception. If you do happen to score lower on a detector after applying this skill, that's a side effect, not the point.
