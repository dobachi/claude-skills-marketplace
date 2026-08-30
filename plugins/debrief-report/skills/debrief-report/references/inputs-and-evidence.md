# Inputs and Evidence

How to read each input type, the ledger schema, the verification protocol, and the
confidentiality rules.

## Contents

- [Input inventory (Step 1)](#input-inventory-step-1) — 入力の棚卸し
- [Per-type rules](#per-type-rules) — 入力の種類ごとの扱い
- [Ledger schema](#ledger-schema) — 根拠台帳の項目
- [Verification protocol (run before Gate 2)](#verification-protocol-run-before-gate-2) — Gate 2 前に走らせる検証
- [Confidentiality](#confidentiality) — 秘匿区分の付け方

## Input inventory (Step 1)

Build the table in `assets/input-inventory.md` before reading anything in depth. Two
columns decide how the material may be used: **reliability** (how much weight a claim from
it can carry) and **confidentiality** (whether it may appear at this disclosure scope).

Then write the **missing list**: sessions without a recording, conversations captured only
in memory, handouts not received, people not met. The report states this explicitly —
a reader who assumes complete coverage will misread silence as absence.

## Per-type rules

### AI transcripts (Plaud, Otter, Teams/Zoom, etc.)
The most information-dense and the least reliable input. Known failure modes: word error
rates degrade sharply in noisy rooms and crosstalk; speaker diarization adds its own error;
downstream summarizers drop qualifiers and swap owners and dates.

- Quote **verbatim** with `file + timestamp`. Never quote from a summary of a transcript.
- **Verify before use**: proper nouns, numbers, dates, commitments, negations
  (「〜しない」/「〜ではない」 are the most damaging to lose), and speaker attribution.
- Preserve hedges exactly: 検討中 ≠ 決定, 「可能性がある」 ≠ 「予定である」.
- If diarization is the only basis for who said something, attribute to the organization
  or add 「（発言者は要確認）」. Do not put an unverified sentence in a named person's mouth.
- Translated transcripts: keep the original-language quote in the ledger for pivotal claims.
- Machine-generated summaries that came with the transcript are a **starting index**, not a
  source. Trace each of their claims back to the transcript span before adopting it.

### Photos
- Venue, room, crowd, exhibits. Almost always appendix material.
- Apply the information test: if deleting the photo changes nothing the reader concludes,
  cut it. Scale, layout, and physical artifacts occasionally pass; "we were there" does not.
- Every kept photo needs a caption naming what it shows and a note stating the takeaway.
- Faces, badges, name tags, other companies' screens, and security arrangements: check
  before publishing at the stated scope.

### Screen captures and photographed slides
- Read the content out and cite as `file + page/slide`; do not paste an unreadable image
  and call it evidence.
- A photographed slide is **someone else's copyrighted work**. Credit the author, session,
  and date, and confirm the event permitted photography and circulation.
- Numbers read off a photo are reliability 中 at best — mark them and, where they matter,
  confirm against the official handout or the speaker's published material.

### Handouts, proceedings, papers, official documentation
- Highest reliability among event inputs. Prefer them over transcripts for numbers.
- Academic: cite `著者 (年) "タイトル", 会議名` + DOI/arXiv, and mark 査読付 vs 未査読(preprint).
  A talk with no paper behind it is cited as a talk.
- Commercial: prefer the vendor's official documentation, pricing page, or press release URL
  over a photographed slide for anything quantitative.
- Use `pdf-extract` for extraction, `document-summary` when one document needs depth.
- Cite `document + page`.

### Programs, session lists, exhibitor lists
- The authority for scale figures (session count, attendance, acceptance rate, exhibitor
  count) and for the **coverage statement**. Cite the URL; do not quote scale from memory.
- Also the honest record of what you did *not* attend — link it so the reader can see it.

### Vendor announcements, keynotes, booth conversations
- A vendor statement is a primary source about the **vendor's intentions**, not about
  reality. Record it as 「<社名>の発表」 and classify: GA / Preview / ロードマップ / コンセプト.
- Benchmarks and "up to N×" numbers travel only with their conditions (scale, workload,
  configuration, period). No conditions recorded → the number does not enter the report.
- Booth explanations are one employee's account; reliability 低〜中, and the follow-up
  contact for verification goes in the inventory.

### Foreign-language sessions
- Quote in the **original language verbatim**, with a translation beside it. Listening error
  in a second language stacks on top of ASR error, and a re-translated paraphrase is two
  lossy steps from what was said.
- Machine-translated transcripts lose hedges twice over; check qualifiers against the
  original audio or the speaker's own slides for anything pivotal.
- Keep technical terms in the original with the translation in parentheses on first use.

### Colleagues' notes (multi-attendee events)
- Keep the recorder's name in the inventory and in the ledger's 出典 column.
- Where two attendees disagree, report the disagreement rather than averaging it.
- One author owns the merged report and its conclusions.

### Own notes and memory
- Legitimate and often the only record of hallway conversations, and the weakest evidence.
- Mark reliability 低〜中 and label as 自メモ. Anything decision-bearing that exists only in
  a note should be confirmed with a counterpart in writing before the report asserts it.

### Post-event research
- Only for what blocks a conclusion: an unknown company, term, standard, or figure.
- Always sourced, always appendix, always labeled 追加調査 with the date.
- Never presented as something observed at the event. Use `grounded-research`,
  `evidence-check`, or `literature-search`.

## Ledger schema

```markdown
| ID | 主張・引用 | 種別 | 出典 | 位置 | 確度 |
```

| Column | Values / rules |
|---|---|
| `ID` | `E-nn` grounded in an input; `I-nn` our interpretation |
| 主張・引用 | Verbatim for quotes (in the original language); otherwise a one-line claim |
| 種別 | 引用 / 数値 / 事実 / 伝聞 / 解釈 |
| 出典 | The input file, document, or 自メモ |
| 位置 | timestamp / page / slide number / — |
| 確度 | 高（原文照合済・一次資料） / 中（読み取り・要確認） / 低（伝聞・記憶） |

Rows are required for: every quote, every number, every commitment or intention attributed
to another party, and every claim a reader might act on. Ordinary connective narrative
needs no row. `I-` rows cite the `E-` rows they derive from.

## Verification protocol (run before Gate 2)

1. **Quotes** — each one re-read against its source span, character by character.
2. **Numbers** — each traced to a source; unit, scale (億/million), period, and basis
   (実績/計画/見込) preserved.
3. **Attribution** — each named speaker verified; unverified ones de-attributed.
4. **Qualifiers** — 検討/予定/決定, may/will, 一部/全体 preserved as spoken.
5. **Negations** — every 「〜しない」「見送る」「対象外」 double-checked; ASR drops these.
6. **Fact vs interpretation** — walk the body: any sentence not traceable to an `E-` row is
   either moved to an `I-` labeled block or removed.
7. **Hearsay** — 伝聞 rows marked as such in the body, with the chain named.
8. **Negative space** — what was not captured is stated; the coverage statement is present
   for any multi-track event.
9. **Post-event research** — nothing from Step 5 sits in the observation sections.
10. **Trend claims** — every 「潮流」 sentence names ≥3 independent observations
    (`event-profiles.md`); one-off claims are rewritten as one speaker's position.
11. **Maturity** — every vendor announcement carries GA / Preview / ロードマップ / コンセプト,
    and no roadmap item is written as available.

## Confidentiality

| Scope | What it permits |
|---|---|
| 公開可 | Anything already public (published slides, press releases, public sessions) |
| 社内限 | Internal circulation; still credit external authors, still check photos |
| 部門限 / 関係者限 | Named-recipient distribution; state the onward-sharing rule in the header |
| NDA / Chatham House | Content may be used, **attribution may not**. De-attribute or drop |

Rules that apply at every scope: credit other parties' materials; do not publish faces or
badges without consent; do not carry another company's confidential figures into a document
with a wider circulation than they were given for; state the scope on the cover.
