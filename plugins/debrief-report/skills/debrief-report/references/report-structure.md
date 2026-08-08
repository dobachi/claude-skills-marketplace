# Report Structure

Per-reader variants, section rules, length budgets, and the Markdown → slide mapping. This is
the common skeleton; the sections a specific event type adds are in `event-profiles.md`.

## Reader variants

| Reader | Deliverable | Length | What they want | What to cut |
|---|---|---|---|---|
| Executive | Deck 8–12 slides + 1-page summary | 5 min read | Decision, money, risk, competitive position, what you need from them | Method, session detail, vendor names below the decision threshold, venue |
| Manager / sponsor | Deck 12–20 slides or 3–5 page Markdown | 15 min | Objective vs result, issues, implications, resource asks, follow-ups | Verbatim quotes beyond the pivotal ones, glossary |
| Practitioners | Markdown, 5–15 pages | reference use | Technical detail, terminology, who to contact, raw material, links | Nothing — this is the archive; but keep the summary at the top |
| Mixed | Exec deck + practitioner Markdown, one source | — | — | — |

Never average an executive and a practitioner into one document. Build the practitioner
Markdown first (it holds everything), then derive the exec deck from it.

## Section rules

### Cover
Title (what and where), dates, location/venue, our attendees, counterpart organizations
and attendees, author, report date, **disclosure scope** (社内限 / 部門限 / NDA 有 / 公開可)
and the onward-sharing rule. Executives use this to judge whether they may forward it.

### Executive summary — the only page some readers open
- **3 conclusions**, each one sentence, each a claim (not a topic)
- **1 implication** for our organization
- **the ask** — approve / decide / assign / just be aware — naming who must act
- No new information appears here that is not developed later
- Written last, but placed second. It must stand alone if detached from the report

### Objective and result
State the objective the trip/meeting was approved for, then the result against it:
達成 / 一部達成 / 未達, one line of evidence each. If the objective shifted on site, say so
and why. This is the section that justifies the cost, and it is the one most often missing.

### Issues (3–5)
One section per issue. Structure inside each:

1. **Conclusion line** (the section heading is an action title — 「A社は2027年の段階導入を前提に動いている」, not 「A社について」)
2. **What we observed** — facts with ledger IDs, quotes where pivotal
3. **What it means** — labeled interpretation
4. **Open questions** — what remains unknown, and how we would find out

Three to five issues is the working range. More than five means the takeaways were not
grouped; fewer than three usually means the debrief was a status update, not a report.

### Implications for us
Not a repeat of the per-issue interpretations — the cross-cutting reading. Opportunities,
risks, what changes in our plan, what we now believe that we did not before, and what a
competitor would take from the same room.

### Actions
| 項目 | 担当 | 期限 | 意思決定者 | 状態 |
|---|---|---|---|---|
Every row has a named owner and a date. Rows needing a decision name the decision-maker.
"Continue to monitor" is not an action; give it a trigger and a review date or drop it.

### Appendix
Session/agenda table (all sessions, one line each, so nothing looks hidden), venue and
atmosphere, photos with captions, glossary, post-event research notes with sources,
evidence ledger, input inventory, contact list.

### Where profile sections go

Profile-specific sections (`event-profiles.md`) slot in **after the issues and before the
implications**, in this order: 潮流 (if the event was large enough to have one) → the
profile's own analysis sections (成熟度一覧 / 当社の発表と反応 / 審議・決定事項 …) → 競合や
注目組織 → implications → actions. The first three sections and the last two never move.

## Length budgets

| Total budget | Issues deep-dived | Appendix session lines | Photos in body |
|---|---|---|---|
| 1 page / 5 slides | 2 | all, one line each | 0 |
| 3 pages / 10 slides | 3 | all | 0–1 |
| 5+ pages / 20 slides | 4–5 | all + notable session notes | 1–2 |

A multi-day conference does **not** get a bigger budget by default — it gets a longer
appendix. The body stays at 3–5 issues however many sessions were attended.

When the material exceeds the budget, cut the number of deep-dived issues, not the
executive summary, the objective-vs-result section, or the actions.

## Markdown → slide mapping

For a `pptx-build` spec (`assets/deck.debrief-report.yaml` is the starter):

| Report section | Slide type | Notes |
|---|---|---|
| Cover | `title` | subtitle carries dates / location / disclosure scope |
| Executive summary | `bullets` | 3 conclusions; the ask as the last bullet |
| Objective and result | `two_col` | left: 目的, right: 結果（達成度） |
| Issue heading | `section` | numbered `01`, `02`, … |
| Issue body | `bullets` (1–2 per issue) | title = the conclusion line |
| Pivotal figure | `big_number` | with `source:` |
| Pivotal quote | `quote` | attribution to org if the speaker is unverified |
| Photo / captured slide | `image` | `caption` names it, `note` states the takeaway, `source` credits the author |
| Implications | `bullets` | |
| Actions | `two_col` or `bullets` | owner and date visible on the slide |
| Appendix divider | `section` | |

Rules carried from `pptx-build`: action titles, one message per slide, `source:` on every
number, exactly one accent, no decorative shapes. Run `validate_deck.py` and read the
printed narrative spine before rendering; then preview the PNGs at Gate 3.
