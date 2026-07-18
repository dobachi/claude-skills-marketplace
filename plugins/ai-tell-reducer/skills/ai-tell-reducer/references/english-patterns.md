# English AI tells: symptom catalog

Each entry: symptom → why it reads as AI → fix. Before/after examples are illustrative; **never add facts, numbers, names, or examples that weren't in the source** (see SKILL.md guardrails). Fix only the tells actually prominent in *this* text, and keep the source's register. None of these words or structures is banned outright — the question is always whether it was *chosen* or fired on *autopilot*.

**Register note (important):** the default register is **formal/technical (memos, papers, reports)**. Some "after" examples below are written slightly loose to make the contrast vivid. For formal work, **fix the same cause but land in formal prose** — no contractions, no first/second person as a device, no fragments-as-punch. Casualizing is register damage in a report, not a de-AI fix. See SKILL.md's *Register calibration*. Casual tools return only when the user asks for a post/blog.

## Contents
1. Uniform rhythm / low burstiness (most visible)
2. Ornate vocabulary ("delve" family)
3. Copula inflation
4. "It's not X, it's Y" and "From X to Y"
5. Rule-of-three overuse
6. Em-dash overuse
7. Reflexive hedging / no stance
8. Meta-scaffolding and teacher voice
9. Vague authority ("studies show")
10. Empty stakes inflation
11. Formatting residue (bold lists, unicode)
12. Formulaic structure and dead endings
13. Localization defaults (spelling, Oxford comma)
14. Self-certifying meta-claims (asserting your own honesty/value)

---

## 1. Uniform rhythm / low burstiness (most visible)

**Symptom:** every sentence 15–20 words, subject-verb-object, every paragraph three-to-four lines. Perfect rectangles.
**Why:** models cluster toward the average; the hypnotic even rhythm pushes readers into skim mode and nothing sticks. This is the single most visible tell.
**Fix:** vary length and structure deliberately. Break a long sentence into a short one that lands. Let one run longer to build. Vary paragraph openings so three in a row don't start "The… / This… / AI…".

Before: The system improves data flow. It reduces manual work. It saves teams time. It also cuts costs across departments.
After: Moving data between departments is the manual bottleneck this system removes. Hand-copying disappears; hours and cost fall with it. (Three sentences of varied length, formal throughout — rhythm without slang.)

## 2. Ornate vocabulary ("delve" family)

**Symptom:** delve, leverage (v.), utilize, harness, unlock, unleash, streamline, robust, seamless, showcase, underscore, pivotal, tapestry, landscape, realm, paradigm, synergy, ecosystem, testament, beacon, multifaceted, meticulous, intricate, commendable, paramount, commence, elevate, transformative, groundbreaking, game-changer, cutting-edge.
**Why:** statistically popular, not good. Usage of these spiked in business/academic text right after LLMs went mainstream; readers now flag them.
**Fix:** plainest accurate word. use (not utilize), show (not showcase), use/gain from (not leverage), start (not commence), key/central (not pivotal), field/area (not landscape/realm). Keep the fancier word only when it's genuinely the precise one.

Before: We leverage a robust framework to unlock seamless synergies across the ecosystem.
After: The framework lets these teams share data without rebuilding their systems.

## 3. Copula inflation

**Symptom:** "serves as," "stands as," "represents," "marks," "acts as" where "is/are" would do.
**Why:** the model's repetition penalty pushes it off basic copulas toward fancier constructions.
**Fix:** restore the plain copula unless the verb carries real meaning.

Before: This serves as a testament to the platform's value and represents a pivotal shift.
After: This shows the platform works, and marks a real change in approach.

## 4. "It's not X, it's Y" and "From X to Y"

**Symptom:** the "It's not X — it's Y" reframe (often with an em dash); "From ancient traditions to modern innovations" sweeps.
**Why:** "It's not X, it's Y" is the single most-identified AI structural tell. "From X to Y" is usually a way to sound sweeping while saying nothing specific.
**Fix:** state the point directly. If the contrast is real and earns its place, keep one — not one per section.

Before: This isn't just a tool — it's a movement. From small startups to global enterprises, everyone benefits.
After: The tool does one thing well: it lets teams share data without a custom integration each time.

## 5. Rule-of-three overuse

**Symptom:** adjective-adjective-adjective, or three parallel clauses, in section after section. Stacked tricolons ("Products impress; platforms empower. Products solve; platforms create…").
**Why:** one tricolon is rhetoric; three back-to-back is pattern failure. The third item is often filler for symmetry.
**Fix:** if you can delete the third item and lose nothing, it was statistical comfort — cut it. Never use the structure twice in one piece.

Before: It's fast, reliable, and scalable. It's simple, powerful, and elegant.
After: It is fast, and it holds up under load. For this deployment, the second property is the one that matters.

## 6. Em-dash overuse

**Symptom:** 15–20+ em dashes in a short piece, used for every dramatic pause, aside, and pivot.
**Why:** AI over-produced them so heavily (2024–25) that readers now treat a dash-dense text as a tell. Collateral damage — but real.
**Fix:** keep one or two you actually mean; convert the rest to a period, comma, or parentheses. If two dashes sit in one paragraph, at least one goes.

Before: The result — and this is the key part — was faster delivery — something everyone wanted.
After: The result was faster delivery, which is what everyone wanted.

## 7. Reflexive hedging / no stance

**Symptom:** "may," "could," "might potentially," "it is often considered," "some would argue" on claims the text actually supports.
**Why:** trained caution produces perpetually balanced, temperature-free prose — you can't tell whose view it is.
**Fix:** commit where the source backs it. "This works for teams under ten; larger orgs will struggle" beats "this may offer some benefits for certain organizations." **Keep hedges that mark genuine uncertainty** — the aim is honest confidence, not fake certainty.

Before: This approach may potentially offer some benefits for certain use cases, though results can vary.
After: The approach works when the data is already standardized. Where it is not, it offers little.

## 8. Meta-scaffolding and teacher voice

**Symptom:** "In this article, we'll explore…," "Let's dive in / unpack this," a mini-summary closing every section, and hand-holding aimed at readers who don't need it.
**Why:** the pedagogical intro-point-point-point-conclusion frame screams template; the teacher voice condescends to expert readers.
**Fix:** delete the announcements and the redundant recaps. Start in the middle of the thought. Match the reader's actual expertise.

Before: In this section, we'll explore three benefits. Let's dive in. …To summarize, we covered three benefits.
After: The first payoff is the one people underestimate: …

## 9. Vague authority ("studies show")

**Symptom:** "studies show," "experts agree," "research proves," "several publications have noted" — with no name, paper, or date. Often inflates one source into "many."
**Why:** ghost citations signal confidence the text hasn't earned; a real E-E-A-T / trust red flag.
**Fix:** name the source if the draft has it. If it doesn't, **don't invent one** — either soften to what's actually known or flag `[needs source: …]` for the author.

Before: Studies show that data spaces cut costs, and experts agree they're the future.
After: [needs source: which study, what cost reduction] — or, if unknown: Data-space advocates argue the main payoff is lower integration cost.

## 10. Empty stakes inflation

**Symptom:** "in today's fast-paced world," "now more than ever," "the possibilities are endless," inflating a niche topic to world-historical weight.
**Why:** filler that raises the emotional register without adding information.
**Fix:** cut it and open on something concrete. Every argument does not need to be civilizationally important.

Before: In today's fast-paced digital landscape, data governance has never been more critical.
After: Most data-governance projects stall on a single question: who is authorized to approve access.

## 11. Formatting residue (bold lists, unicode)

**Symptom:** every bullet starts with a **bolded phrase**; bold scattered through running prose; unicode arrows (→), curly quotes, and other characters you don't get by typing normally; leftover markdown.
**Why:** hallmark of markdown chat output; hand-written prose rarely looks like this.
**Fix:** return to plain running prose where a list isn't genuinely warranted. Reserve bold for the one or two places it truly earns. Normalize stray unicode to what a keyboard produces.

## 12. Formulaic structure and dead endings

**Symptom:** rigid Intro → Point → Point → Point → Conclusion; sections titled "Challenges and Future Prospects"; endings like "Only time will tell" / "The future looks bright."
**Why:** the shape itself reads as generated; the empty ending is a non-commitment.
**Fix:** let structure follow the argument, not a template. End on a concrete action, a sharp observation, or a real question — not a horizon-gazing platitude.

## 13. Localization defaults (spelling, Oxford comma)

**Symptom:** American spelling (organize, color) and the Oxford comma appear by default because most models default to US English.
**Why:** not wrong — but a mismatch if the author writes British/other English, and the sudden consistency can itself read as machine-set.
**Fix:** match the author's established convention. If they write "organise" and "colour," keep it throughout. This is a consistency fix, not a correctness one.

## 14. Self-certifying meta-claims (asserting your own honesty/value)

**Symptom**: the prose vouches for itself — "to be honest," "we'll be objective here," "I'll give you the unvarnished truth," "this is the most important section," "let me be transparent," "no fluff, just facts," "I won't sugarcoat this."
**Why it reads as AI**: credibility is something a reader grants based on the content; asserting it is a substitute for earning it. Worse, it invites the opposite inference — if this part is honest, what about the rest? Models produce it when optimizing for "sound trustworthy" at the sentence level instead of at the evidence level. It is most jarring in reports, technical docs, and anything where claims are supposed to rest on sources.
**Fix**: cut the claim; keep only what enacts it. Instead of announcing balance, present the counter-evidence. Instead of promising no fluff, remove the fluff. Instead of labelling a section important, state the consequence that makes it important.

Before: This is the section that determines the report's value. I'll be honest here and avoid turning it into a sales pitch.
After: [delete and continue] X is a poor fit in three situations. Each one follows from a property of its design.

Before: To be transparent, I'll list every limitation I know of.
After: [just list them] Known limitations: ...

**Test**: delete the sentence. If no information is lost, it was a claim about the writing rather than the writing itself.
