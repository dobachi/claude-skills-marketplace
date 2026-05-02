# Translation Fidelity Reference

Detailed guidance on the principles and mechanics of faithful translation. Source principles drawn from Eugene Nida (formal vs. dynamic equivalence), Lawrence Venuti (foreignization vs. domestication), Christiane Nord (functional translation theory), and standard practice in academic, legal, and technical translation.

## The Fidelity Spectrum

Translation choices live on a spectrum:

```
Foreignizing  ←─────────── Faithful (default) ───────────→ Domesticating
Word-for-word    Meaning-preserving, structure-preserving    Reader-natural, idiom-replaced
```

This skill defaults to **faithful** — meaning- and structure-preserving — not literal. Pure literal translation produces translationese and often distorts meaning. Pure domestication risks adding/omitting content. The translator's job is to land at "faithful": every source claim, hedge, and stance preserved, in language that reads naturally in the target.

Move toward **foreignizing** when:
- Legal or regulatory text — extreme literal fidelity required
- Religious / canonical texts — preservation of source phrasing matters
- Linguistic study or critical edition — source structure is the object

Move toward **domesticating** when:
- Marketing / consumer copy — user explicitly asked for adaptation
- Children's literature — cultural adaptation routine
- The user's stated goal is reader naturalness over source mirroring

In all cases, **document the choice** in translator's notes.

## Register and Tone

Match the source's register exactly. Common axes:

| Axis | Variants |
|---|---|
| Formality | Formal / Neutral / Informal / Colloquial |
| Politeness (Japanese) | 敬体 (です/ます) / 常体 (だ/である) / 尊敬語・謙譲語 |
| Stance | Objective / Persuasive / Critical / Reflective |
| Domain register | Academic / Legal / Technical / Journalistic / Conversational |
| Person | Third-person / First-person plural ("we") / Second-person address |

A formal academic source rendered in casual target language signals incompetence. The reverse is also wrong. Re-read the source paragraph aloud; re-read the translation aloud; compare felt register.

## Terminology

### First-occurrence convention

When a technical term is translated, on its first occurrence include the source term in parentheses, especially for emerging or contested terminology:

> 機械学習(machine learning)は…
> retrieval-augmented generation (RAG) is …

After the first occurrence, use the target term consistently.

### Translation policy per term

Decide once, apply everywhere. Options:

- **Translate** — established target equivalent exists (e.g., "machine learning" → "機械学習")
- **Transliterate** — phonetic rendering (e.g., "encoder" → "エンコーダー" in Japanese)
- **Keep original** — proper nouns, brand names, established acronyms, untranslatable terms (e.g., "transformer architecture" — usually kept as-is in non-English text)
- **Hybrid** — target equivalent + original in parens (default for first occurrence of a technical term)

### Glossary discipline

- Build the glossary before translating. Gather all technical terms by skimming the source.
- One source term → one target term. Document exceptions.
- For acronyms: expand on first occurrence (`OECD (Organisation for Economic Co-operation and Development)`); use the acronym afterward.
- Publish the glossary as part of the deliverable so the reviewer can audit.

## Named Entities

| Entity type | Default policy |
|---|---|
| Person names | Keep original spelling in Latin script; add transliteration in parens for non-Latin scripts on first occurrence |
| Place names | Use established target-language form if widely recognized (e.g., "東京" ↔ "Tokyo"); keep original otherwise |
| Organization names | Keep original; add target-language gloss if needed for clarity |
| Brand / product names | Keep original; trademarks are not translated |
| Government bodies / laws | Use established target-language translation if one exists; otherwise keep original with translator's note |
| Titles of works | Use published target-language title if one exists; otherwise translate with original in parens on first occurrence |

Document the policy in the glossary.

## Numbers, Dates, Units, Currencies

- **Numbers**: Use target-language conventions (e.g., commas vs. periods as thousands/decimal separators; Japanese 万・億 vs. English millions/billions).
- **Dates**: Convert format to target convention (e.g., "March 14, 2026" ↔ "2026年3月14日").
- **Units**: Do **not** silently convert (e.g., feet to meters). Convert only if the user requests; otherwise preserve source units. If converting, show both: "10 ft (about 3.0 m)".
- **Currencies**: Preserve source currency. If conversion is helpful, add in a translator's note with date of conversion rate.

## Hedges and Modal Qualifiers

The most common faithfulness failure. Translate every hedge.

| Source hedge | Common loss | Faithful target |
|---|---|---|
| "may", "could", "might" | Translated as definite | Preserve as 可能性, おそらく, …かもしれない |
| "tends to" | "is" | …傾向がある |
| "approximately" | "" (omitted) | およそ, 約 |
| "we believe" | "the data shows" | 我々は…と考える |
| "limited evidence suggests" | "evidence shows" | 限定的な証拠が…を示唆する |
| "in some cases" | "" (omitted) | 場合によっては |
| "preliminary" | "" or "definitive" | 暫定的な |

Reverse direction (Japanese → English) has analogous traps: "と思われる" is a hedge, not a definite assertion. Translate as "appears to" or "seems to".

## Voice and Sentence Structure

- **Active vs passive**: Preserve where it carries weight (academic abstracts often use passive deliberately; news articles often active). Switch only when grammatically required.
- **Sentence boundaries**: Long source sentences may be split for target-language readability — note the split in the ledger. Do not merge sentences silently; if merged, note the merge.
- **Logical connectors** ("however", "therefore", "moreover", しかし, したがって, さらに): preserve. They encode argument structure.
- **Topic-comment structure** (Japanese): may need restructuring in English target; preserve emphasis order where possible.

## Idioms, Proverbs, and Culture-Bound Expressions

Three options:

1. **Equivalent idiom** in the target (e.g., "kick the bucket" ↔ 「お陀仏になる」).
2. **Paraphrase** the meaning literally (most common; safest for formal texts).
3. **Literal translation + footnote** explaining the idiom (preserves the source flavor in literary translation).

Pick per-instance. Document in the ledger note column. Default: paraphrase for non-literary texts, equivalent idiom for marketing/literary.

Avoid: literal translation without note (creates confusion), or substitution with a culturally heavy target idiom that imports unintended associations.

## Ambiguity in the Source

Sources are sometimes deliberately ambiguous (legal documents, philosophical texts, certain literary forms). Default: **preserve ambiguity** if the target language allows. If forced to choose:

- Pick the most plausible reading
- State the choice and the alternative in a translator's note
- Never silently disambiguate

## Errors in the Source

If you spot a likely error (typo, wrong figure, factual inconsistency):

- Translate as-is. Translation is not editing.
- Note the apparent error in a translator's note: "The source states X; based on context, this may be a typo for Y."
- Let the user decide whether to correct in the published target version.

## Voice Consistency

Within a document, the translator's voice should be invisible. If the source has multiple authorial voices (e.g., a quoted excerpt embedded in commentary), preserve the distinction — quoted passages translated tightly; commentary translated in the commentator's register.

## Common Pitfalls Checklist

- [ ] Hedge dropped or strengthened
- [ ] Idiom translated literally without note
- [ ] Register mismatch
- [ ] Terminology drift (term A used inconsistently)
- [ ] Translator's gloss in the body instead of in a note
- [ ] Source ambiguity silently disambiguated
- [ ] Source error silently corrected
- [ ] Numbers, dates, or units silently converted
- [ ] Cultural reference dropped (or unmediated)
- [ ] Sentence merged/split without note in ledger
- [ ] Structure (headings, list items, code blocks, citations) altered
- [ ] Named entity rendered inconsistently
- [ ] First-occurrence original-in-parens convention skipped for technical terms
- [ ] Acronyms not expanded on first occurrence
- [ ] Quotation attribution lost or shifted
