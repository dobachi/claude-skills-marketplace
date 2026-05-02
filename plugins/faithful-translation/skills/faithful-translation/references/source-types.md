# Source Types: Translation Conventions per Genre

Different document genres have different fidelity priorities, structural conventions, and pitfalls.

## Academic Papers

**Fidelity priority**: Methodology language, hedges, effect sizes, citations, technical terms.

- Preserve passive voice in Methods/Results sections (academic register).
- Hedges are semantically critical — "p < 0.05" findings often qualified ("appears to", "suggests"). Never strengthen.
- Citations: keep the citation system intact (APA, MLA, Chicago, IEEE numeric). Do not localize citation style unless the user requests.
- Technical terminology: build a thorough glossary before drafting; many fields have established target-language equivalents in textbooks or terminology databases.
- Equations, code, figure references: do not translate variable names, code identifiers, or table/figure numbers.
- Latin terms (in vivo, prima facie, et al.): keep in Latin per scholarly convention.
- Author affiliations and address blocks: preserve original; add target-language gloss if the user wants.

**Common pitfalls**: smoothing methodological caveats, dropping "preliminary" / "limited" qualifiers, translating equation variables.

## Business Reports / Whitepapers

**Fidelity priority**: KPIs, forecasts, hedges in projections, defined terms.

- KPI definitions inside the document are defined terms — preserve consistently.
- Forecasts use hedge words ("expected to", "could reach", "in our base case scenario") — preserve.
- Numbers: preserve precision; do not round silently.
- Currency: preserve original currency. If a footnote conversion is added, include date and rate.
- Branded methodologies (e.g., "BCG Matrix", "OKR") — keep original term; add target-language gloss only if the audience needs it.
- Executive summary register is more direct; body sections often more analytical — match each section's register.

**Common pitfalls**: converting "we expect" to "we will", silently changing currency, translating proper-noun methodologies.

## News Articles

**Fidelity priority**: Lede, attributions, direct quotes, neutral register.

- **Lede**: preserve the news lede structure (5W1H typically in the first paragraph).
- **Attributions** ("said", "according to") — preserve exactly. Do not strengthen ("said" → "claimed") or weaken.
- **Direct quotes**: translate carefully; preserve the speaker's apparent register and stance. Note: when the source quotes a speaker who originally spoke a third language, translation chains can introduce drift — flag in a note.
- **Datelines** (CITY, Date —): preserve format conventions of the target outlet, or keep source format.
- **Neutral register**: avoid loaded vocabulary; preserve source's chosen terms (e.g., "rebels" vs. "freedom fighters" vs. "armed group" — translate the chosen term, do not substitute).

**Common pitfalls**: editorial color creeping in, attribution drift, dateline format mistakes.

## Legal / Contract Documents

**Fidelity priority**: Defined terms, obligations, exceptions, dates.

- **Extreme literal fidelity** required.
- **Defined terms** (often capitalized: "Party", "Effective Date") — never translated; or, if translated, translated identically every time per the glossary, and the original capitalized term retained on first occurrence.
- **Obligation language**: "shall" / "must" / "may" carry distinct legal weight — translate consistently; preserve the modal precisely.
- **Exception clauses** ("except as provided in §X.Y"): preserve cross-references; use the same section numbering.
- **Effective dates, jurisdictions, governing law**: preserve verbatim; numerals may be both spelled out and figured ("ten (10) days") — preserve both forms.
- **Boilerplate** (severability, entire agreement, force majeure): use established target-language equivalents from legal practice in the relevant jurisdiction; do not improvise.
- **For binding translations**: a certified translator may be required; flag this if the deliverable will be filed legally.

**Common pitfalls**: smoothing "shall" into "will", losing defined-term capitalization, translating section cross-references with new numbering.

## Technical Documentation / Software

**Fidelity priority**: Code, commands, parameter names, version-specific notes.

- **Code blocks, commands, file paths, variable names**: never translate.
- **UI element names** (button labels, menu items): match the published target-language UI if it exists; otherwise leave original with target-language gloss in parens.
- **Error messages**: if the application is localized, use the localized message; if not, leave the English message and translate the explanation.
- **Version-specific notes**: preserve version numbers verbatim.
- **Code comments inside code blocks**: translate or leave per user preference; default is to translate if the comments are explanatory, leave if they are tracking comments (`TODO`, `FIXME`).
- **API parameter names, JSON keys, env vars**: never translate.
- **Examples and tutorial flows**: preserve the literal commands; translate surrounding prose.

**Common pitfalls**: translating code identifiers, mismatched UI labels, dropping version numbers.

## Books / Long-form

**Fidelity priority**: Narrative voice, chapter structure, recurring imagery, character voice.

- **Chapter and section titles**: translate; preserve the structural hierarchy.
- **Recurring imagery and motifs**: render consistently across the book; build a motif glossary alongside the term glossary.
- **Character voice**: preserve idiolects, dialects, register variations between characters.
- **Footnotes and endnotes**: translate; preserve numbering.
- **Front matter** (preface, foreword, dedication): translate; preserve attribution.
- **Index and glossary at the back**: rebuild for the target language with target-language alphabetic order; cross-reference original and target terms.

**Common pitfalls**: flattening character voices, losing recurring imagery's coherence, restructuring chapters.

## Regulatory / Policy Documents

**Fidelity priority**: Scope, definitions, obligations, exceptions, effective dates, cross-references.

- Treat similarly to legal documents.
- **Definitions section**: translate once; lock terms; apply consistently.
- **Obligation gradations** ("shall", "must", "should", "may"): preserve precisely.
- **Cross-references** to other regulations: preserve verbatim including statute/regulation numbers.
- **Effective dates and transitional provisions**: preserve verbatim.
- **Annexes / schedules**: preserve numbering.

**Common pitfalls**: weakening obligations, dropping cross-references, translating regulation numbers.

## Marketing / Consumer Copy

**Fidelity priority**: Persuasive impact in the target market — often requires deliberate **adaptation** rather than faithful translation.

- This is the genre where **domestication** is usually appropriate.
- The user typically wants the deliverable to feel native in the target market.
- Document adaptation choices explicitly in translator's notes — what was changed and why.
- A pure faithful translation of marketing copy often fails commercially; clarify with the user up front whether they want faithful translation (preserve source feel) or adapted (target-market resonance).
- **Slogans, taglines**: may need full creative re-creation. Note this in the deliverable.

**Common pitfalls**: faithful translation that reads as awkward in the target market; or adaptation that deviates from product positioning.

## Scientific Reviews / Meta-analyses (Cochrane-style)

**Fidelity priority**: PICO elements, certainty ratings, exact effect estimates with confidence intervals.

- **PICO** (Population, Intervention, Comparison, Outcome): preserve precisely.
- **Effect estimates**: preserve numbers and units; preserve confidence intervals.
- **Certainty ratings** (GRADE: high / moderate / low / very low): use established target-language equivalents.
- **Quoted study findings**: preserve study identifiers.

**Common pitfalls**: rounding effect sizes, dropping confidence intervals, weakening certainty ratings.

## Quick-Reference Matrix

| Genre | Fidelity priority | Watch for |
|---|---|---|
| Academic | Methodology hedges, citations | Smoothing caveats |
| Business / whitepaper | KPIs, forecast hedges | Currency / number drift |
| News | Lede, attributions, neutral tone | Editorial color |
| Legal / contract | Defined terms, obligations | "Shall" → "will" drift |
| Technical / software | Code, commands, identifiers | Translating code |
| Book / long-form | Voice, motifs, structure | Flattening character voices |
| Regulatory | Cross-references, obligations | Weakened obligations |
| Marketing | Persuasive impact (often adapt) | Faithful when adapt is needed |
| Scientific review | Effect estimates, certainty | Dropping confidence intervals |
