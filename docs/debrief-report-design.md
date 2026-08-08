# debrief-report — Design Notes

Why the `debrief-report` skill is shaped the way it is. Written **2026-08-08**, alongside
the skill itself. The rationale lives here; `SKILL.md` and `references/` carry rules only.

Method note: this is a targeted best-practice review (four web searches plus one full-text
read), not a `grounded-research` run. The sources are listed at the end; claims below that
are design judgments rather than sourced findings are marked as such.

## The problem

Debriefing a trip, conference, or long meeting fails in a predictable way: the author walks
through the sessions in order, reproducing the agenda, and the reader is left to extract the
meaning. The raw material (AI transcripts, photos, captured slides, handouts, memory) is
abundant and uneven in reliability, so volume is never the constraint — **selection,
structure, and trustworthiness are**.

## Where the initial rough plan needed changing

The starting proposal was: collect inputs → structure → Markdown agenda → optional extra
research → pptx. Sound as a spine, but six things were missing or misplaced.

| Change | Reason |
|---|---|
| Added **Step 0** (reader / ask / disclosure scope / original objective) as a blocking step | The plan confirmed the reader "when creating". Everything downstream — depth, length, what may be shown, which section closes the report — is a function of those four, so they cannot be discovered mid-draft |
| Moved the **executive summary to position 2**, ahead of purpose and venue | The rough structure put it after 主旨・会場の様子. Trip-report guidance is unanimous that the summary opens the report; an executive who reads one page must read the conclusions, not the venue |
| Default organization changed from **per-session to per-issue** | The DevRel conference-summary practice is to fix 5–10 takeaways *first* and use them as the skeleton. Session-order narration is the transcript restated |
| Added **implications + action table (owner, due date)** as required sections | The rough structure ended at per-session summaries. Japanese 出張報告書 practice centers 成果 and 所感; the report's value is the so-what and the next move |
| Added **evidence discipline**: fact / interpretation / hearsay labels and a lightweight ledger keyed to file + timestamp | Measured failure modes of AI meeting notes — ASR degradation in noisy rooms, diarization error, dropped qualifiers, swapped owners and dates — make transcript claims unsafe to restate directly |
| Added a **disclosure-scope gate** before delivery | Design judgment. Debriefs uniquely mix other companies' materials, photographed slides, identifiable faces, and NDA/Chatham House content, and they get forwarded |
| **Markdown = source of truth, deck = derived** (the plan treated Markdown as an agenda) | Design judgment. Reader mix changes; a deck cannot hold appendices, evidence, or terminology. One source, two renderings, no rework when the audience shifts |

Also added: a one-week shipping norm (conference summaries lose value within weeks and are
stale after a month), and an explicit "what was not recorded" statement — a report built
from partial recordings otherwise reads as complete coverage.

## Event profiles (added after the first pass)

The first version handled meetings and visits well and conferences only generically. Large
events differ in ways that change the report, so five profiles were added — A 国際学会,
B 商業カンファレンス・展示会, C 標準化会合, D 商談・訪問, E 社内討議 — sharing one workflow
and one core structure, differing in intake, extra sections, source conventions, and failure
modes (`references/event-profiles.md`).

Three rules came out of the conference cases and now apply skill-wide:

- **Coverage statement.** At a multi-track event you attend a fraction of the sessions. Left
  unstated, a reader treats the report as complete and reads absence as evidence. The
  statement (attended N of M, tracks not covered, what public material filled the gap) is
  required, sourced to the program.
- **Trend claims need ≥3 named independent observations.** 「〜が潮流だった」 is a claim about
  a whole event; one keynote cannot carry it. Counting also forces the author back to the
  program instead of writing from impression. This is the operational form of the
  takeaways-first advice from the DevRel source.
- **Maturity classification for vendor announcements** (GA / Preview / ロードマップ /
  コンセプト). The failure it prevents — a reader planning against a roadmap slide — is the
  commercial-conference equivalent of the transcript failures the ledger already covers.
  Vendor statements are cited as 「<社名>の発表」, primary evidence of intent, not of reality.

Also profile-driven: the academic profile requires **当社の発表と反応** (the criticism received
is the most valuable and most-often-omitted output of presenting), paper-level citation with
DOI/arXiv and 査読付／未査読 marking, and original-language verbatim quotes because
second-language listening error stacks on ASR error. The commercial profile requires **自社の
出展・登壇の成果** whenever budget was spent, and an **embargo date** field in the disclosure
gate — pre-announcement and analyst material has a release date that ordinary confidentiality
scopes do not express.

### Why only two profiles get full template sets

A and B ship complete report + deck templates under `assets/profiles/`; C, D, and E use the
base assets plus a few extra sections listed in the reference. Five parallel template sets
would be roughly 80% identical text, and duplicated boilerplate drifts — a fix applied to one
copy silently leaves four wrong. A and B earn their own because their bodies genuinely differ
(成熟度一覧 and 出展成果 have no academic analogue; 論文リスト and 発表への反応 have no
commercial analogue). Both deck specs are linted by `pptx-build`'s `validate_deck.py`.

## Why one skill, not a mode of an existing one

`document-summary` summarizes **one** source faithfully; a debrief synthesizes many sources
of unequal reliability into a reader-targeted argument with actions. `pptx-build` renders a
deck from a spec but has no opinion on how a trip becomes that spec. `grounded-research`
answers a question from external sources. The gap — heterogeneous first-hand records →
structured report for a named reader — is a distinct workflow, so it is a distinct skill
that delegates rendering and fact-finding to those siblings.

## Design decisions worth recording

**Lightweight ledger over a full Claim Ledger.** `document-summary` requires every sentence
to trace to a ledger row. Applied to a three-day conference under a one-week deadline, that
cost would push the report past its shelf life. The compromise: rows are mandatory only for
quotes, numbers, commitments attributed to another party, and claims a reader might act on —
which is exactly the set that the measured transcript failure modes corrupt.

**Speaker attribution treated as the highest-risk field.** Diarization error is separate
from and additive to word error, so "who said it" is less reliable than "what was said".
The rule is to de-attribute to the organization rather than guess a person.

**Three to five issues.** Below three, it is a status update; above five, the takeaways were
never grouped. Design judgment, consistent with the 5–10 takeaway heuristic collapsing into
a smaller number of themes.

**Photos default to the appendix.** Carried from this repo's existing rule that a visual
must encode information — delete it and see whether any conclusion changes.

**Assets rather than prose examples.** Three templates ship: the report skeleton, the input
inventory, and a `pptx-build` deck spec matching the structure one-to-one. The deck spec is
validated by `pptx-build`'s own `validate_deck.py` (0 errors), so the two skills are known
to compose.

## Sources

- [出張報告書の書き方とは？無料テンプレート10選や必要性を解説 — NotePM](https://notepm.jp/blog/1286)
- [出張報告書に使えるテンプレート【例文付き】 — 経理プラス](https://keiriplus.jp/template/syutyouhoukokusyo01/)
- [How to Make a Business Travel Report: A Comprehensive Guide — travel-code](https://travel-code.com/news/business-travel-report-how-to-write-a-perfect-one)
- [What should a business travel report include? — Pliant](https://www.getpliant.com/en-us/blog/what-should-a-business-travel-report-include)
- [Writing a Good Conference Summary or Trip Report — DevRel Superpowers](https://avocadobytes.substack.com/p/writing-a-good-conference-summary)
- [How AI Meeting Notes Actually Work — Circleback](https://circleback.ai/blog/how-ai-meeting-notes-work)
- [Meeting Summarization: A Survey of the State of the Art (arXiv 2212.08206)](https://arxiv.org/pdf/2212.08206)
- [Interactive In-Meeting Speaker Correction with Human Feedback (arXiv 2509.18377)](https://arxiv.org/pdf/2509.18377)
