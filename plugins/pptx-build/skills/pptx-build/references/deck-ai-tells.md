# Deck AI tells

The habits that make a generated deck recognisable as one. Each is harmless on a single slide;
as a pattern across the deck it is the tell. `validate_deck.py` reports the structural ones at
deck level (slide 0); the textual ones need the de-AI pass described at the end.

## Contents

- Structural tells (the validator catches these)
- Typographic tells
- Textual tells (ai-tell-reducer catches these)
- The de-AI pass
- What is not a tell

## Structural tells (the validator catches these)

| Tell | Why it reads as generated | Validator | Fix |
|---|---|---|---|
| Every bullet is `ラベル: 説明` | one scaffold applied to every thought, whatever its shape | WARN when ≥60% of ≥6 bullets match | keep the label where it IS the content (a speaker, a region); elsewhere write the sentence, or give pairs their shape (`table`, `cards`) |
| Same item count on four slides running | the rhythm of a template, not of the content | WARN at four consecutive | vary the count, or change the shape of one (a `figure`, a `statement`) |
| Exactly three items on (almost) every listed slide | the rule-of-three reflex | INFO when ≥80% of ≥5 | if the content does not come in threes, do not make it |
| Arrows and em-dashes inside text (`→` `—` `–`) | a relation written as a symbol instead of a verb | INFO at ≥3 | write it: へ移った / の結果 / つまり; or draw it as a `flow` |
| Long assertion titles | the claim is buried in a sentence and the type flattens | WARN past ~26 wide | short claim + `lead:` |
| A short list under a long title, lower half empty | filler; the slide exists because the outline had a heading | WARN under ~35% fill | add `lead:`, merge, or give the content its shape |
| Four identical skeletons in a row | the deck's rhythm is the layout's, not the argument's | `audit_pptx.py` rhythm check | a turn page (`statement`), a different composition |
| A drawn diagram pasted as a picture | pixels where words should be | ERROR on `image_kind: drawing`, WARN on undeclared non-photos | native `figure` |

## Typographic tells

Not detected mechanically; check in the rendered PNGs.

- **Uniform emphasis**: bold on the first words of every bullet. Bold one thing per slide or nothing.
- **Icons per bullet, one per idea**: the content does not have icons; the template did.
- **Every card the same height with the same two-line label**: real content is uneven; let the
  `lead` archetype or a `statement` break the row.
- **Gradient bands, drop shadows, rounded everything**: the default mode draws none; a template
  that insists is the template's choice.
- **Title case or sentence fragments in Japanese**: 体言止め headings in a row read as a table of
  contents, not an argument.

## Textual tells (ai-tell-reducer catches these)

The deck's words carry the same tells as prose: rhetoric with no occasion (「単なる X ではなく Y」),
significance attached to plain facts (「重要なのは」「注目すべきは」), inflated verbs (実現 / 推進 /
強化 / 最適化 / 加速), borrowed metaphors (座礁 / 着火 / 本丸), English-shaped Japanese
(無生物主語, 余分な代名詞), and headings written as full sentences where a noun phrase would do —
and the reverse, noun-phrase titles where a claim is needed. The `ai-tell-reducer` skill holds the
dictionary and the judgement; this skill only hands it the text.

## The de-AI pass

```bash
python3 validate_deck.py deck.yaml --text /tmp/deck-text.md
```

writes every sentence the audience will read — titles, leads, bullets, column text, captions,
takeaways, notes — as Markdown. Run ai-tell-reducer on that file, carry the edits back into the
spec (the Markdown is grouped by slide number so each line is easy to find), then build. Do this
before rendering, not after: a tell found on a PNG costs a rebuild.

## What is not a tell

- An action title on every content slide. That is the assertion–evidence structure, and it is
  what makes the spine readable (`references/narrative-and-logic.md`).
- A source line on every data slide. That is rigor.
- Repetition that the content has: four regions, four rows. Same shape for same content is
  correct; the tell is the same shape for different content.
