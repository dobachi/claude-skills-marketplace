# Sample decks — argument-shaped, not just good-looking

These are reference specs you can build and read. Each one is chosen to demonstrate a **different argument structure**, because the right structure follows from *what you're trying to make the audience do* — not from a visual template. They embody widely-used best practice (Minto's Pyramid Principle, SCQA framing, McKinsey/BCG action titles), and each validates to a clean narrative spine.

Build and inspect any of them:

```bash
cd assets
python3 validate_deck.py samples/recommendation-scqa.yaml   # read the spine + lint
python3 build_deck.py    samples/recommendation-scqa.yaml -o /tmp/out.pptx
./render_preview.sh /tmp/out.pptx                            # eyeball the PNGs
```

| Sample | Argument shape | Use it when… | Structure it shows |
|---|---|---|---|
| `recommendation-scqa.yaml` | **"We should do X."** | proposing a decision/investment | SCQA opening → governing thought (answer-first) → 3 MECE reasons → plan → ask |
| `progress-review.yaml` | **"On track, except Y — approve the fix."** | status / business review (often read async) | bottom-line-up-front → KPIs vs target → risk & cause → ask |
| `analysis-decision.yaml` | **"Among the options, choose B."** | option/vendor/build-vs-buy decisions | decision-first → explicit MECE criteria → comparison → residual-risk resolution → ask |

## What to copy from them

- **Action titles everywhere.** Every content title is a *claim* ("更新率は過去最高で、定着は計画を上回って推移している"), never a topic ("更新率"). The titles, read alone, are the argument — run `validate_deck.py` and read the printed spine to feel it.
- **Answer first (Pyramid Principle).** The governing thought appears near the top, then the body proves it. The audience never waits for the point.
- **SCQA opening.** The first content slide frames the *complication* so the question — and your answer — is earned, not asserted into a vacuum.
- **MECE groupings.** Supporting reasons / criteria don't overlap and don't leave gaps. Three clean reasons beat five fuzzy ones.
- **Sources on every data claim.** Each number carries a `source:` footnote. The validator enforces this; the samples model it.
- **The close delivers the open.** Each deck ends on an *ask* that resolves the opening complication — the loop shuts.

## How to adapt

1. Pick the sample whose **argument shape** matches your goal (recommend / review / decide).
2. Replace the titles first — write each as the *takeaway*, then fill the body to prove it.
3. Run `validate_deck.py` and fix findings; read the spine against `references/narrative-and-logic.md`.
4. Build, render, and run the pre-delivery checklist in `SKILL.md`.

For genre-level conventions on top of this logic (investor pitch, sales narrative, conference talk), see the **pptx-design** skill's `references/genres-and-qa.md`.
