# Narrative & Logic — the cross-slide check

`validate_deck.py` catches the mechanical faults (missing titles, dangling sections, data without a source, too-dense slides). It **cannot** judge whether the deck *argues* well. That is a reading task — done against this framework, using the **narrative spine** the validator prints (every title in order, grouped by section).

A deck is not a list of slides; it is **one argument delivered in sequence**. Use these four lenses.

## 1. Pyramid Principle (Minto) — answer first, then support

- **One governing thought.** The whole deck supports a single top-line claim. State it early (title slide or first content slide), not as a reveal at the end. If you can't write the governing thought in one sentence, the deck has no spine yet.
- **Vertical logic.** Each slide's **body proves its title**. The title asserts; the bullets/chart are the evidence. If the body doesn't support the title, one of them is wrong.
- **Horizontal logic.** The titles, read in order, must themselves form the argument — the "ghost deck" test. The spine the validator prints *is* your horizontal logic. Read it alone: if it doesn't make the case without the bodies, the storyline is broken.
- **Grouping is MECE.** The supporting arguments under a claim should be **M**utually **E**xclusive and **C**ollectively **E**xhaustive — no overlap, no gap. Three non-overlapping reasons beat five that bleed into each other.

## 2. SCQA — earn the question before you answer it

Open by framing *why this matters now* (Barbara Minto's S-C-Q-A; Duarte's "what is" vs "what could be"):

- **Situation** — the stable context the audience agrees with.
- **Complication** — what changed / what's now at risk (the tension).
- **Question** — the question the complication forces.
- **Answer** — your governing thought, which the rest of the deck proves.

A deck that opens straight into data, with no complication, gives the audience no reason to care. Check the first 1–3 slides carry an S-C-Q before the body starts.

## 3. Action titles — the title must state the takeaway

Every content title is a **claim**, not a topic. "Q3 revenue" is a label; "Q3 revenue grew 18%, driven by enterprise renewals" is a claim. (McKinsey/BCG convention.) The validator flags *short, topic-shaped* titles as INFO — but only a human/model read tells whether a grammatically-complete title actually states the **so-what**. For each title ask: *"so what?"* If the answer is the same sentence, it's an action title; if you can still ask "and therefore?", it's a topic.

## 4. Summary consistency — the close delivers the open's promise

- The **answer promised in the opening** must be the **conclusion delivered at the close**. If the deck opens "we should reallocate budget" and closes on "here are some metrics," the loop never shut.
- **No contradiction across slides.** A number, claim, or recommendation on slide 4 must not be undercut by slide 9. Reconcile figures that appear more than once.
- The **next-steps / ask** must follow from the argument, not arrive from nowhere.

## The cross-slide checklist (read the spine, then verify)

Run `python3 validate_deck.py SPEC.yaml`, then read the printed spine against:

- [ ] **One governing thought** — can you state, in one sentence, what the whole deck argues? Is it stated early?
- [ ] **Horizontal logic** — do the titles alone tell that story, in order, with no leap?
- [ ] **SCQA opening** — is there a complication that earns the question before the answer?
- [ ] **Section grouping is MECE** — within each section, do the titles add up to the section's claim with no overlap or gap? Across sections, do they cover the argument without repeating it?
- [ ] **Every title is a claim** — apply the "so what?" test to each; no surviving topic labels.
- [ ] **Vertical logic** — does each slide's body actually prove its title? (Read the bodies for the slides whose titles carry the most weight.)
- [ ] **Close delivers the open** — does the final section/ask resolve the opening complication? Any claim contradicted later? Do repeated numbers reconcile?

Findings here are not mechanical — record them as edits to titles, slide order, or splits/merges, then re-run the validator and re-read the spine.

## See also

- `references/spec-format.md` — how titles, sections, and sources map to spec fields.
- `assets/samples/` — argument-shaped example decks (recommendation / review / decision), each annotated with the structure it embodies. Validate them to see a clean spine.
- pptx-design `references/genres-and-qa.md` — genre-specific anchor structures (pitch, sales, internal review, talk) that sit *on top of* this logic.
