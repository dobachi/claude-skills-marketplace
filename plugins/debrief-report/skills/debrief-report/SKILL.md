---
name: debrief-report
description: >-
  Turns raw records of an international academic conference, a commercial/vendor conference or
  trade show, a standards meeting, a customer visit, or an internal discussion into a
  reader-targeted report: a Markdown report as the source of truth plus a derived executive
  .pptx. Fixes reader / ask / disclosure scope / original objective / event profile FIRST,
  inventories every input (AI transcripts, photos, captured slides, proceedings, colleagues'
  notes) with reliability and confidentiality, restructures by issue rather than by session,
  and separates fact / interpretation / hearsay in a lightweight evidence ledger — because
  ASR drops qualifiers and misattributes speakers, a vendor roadmap is not a shipped product,
  and one keynote is not a trend. BLUF summary first; ends in implications and an action
  table with owner and due date. Use for 国際学会参加報告,
  カンファレンス報告, 展示会視察報告, 出張報告, 会議報告, 訪問報告, 議論のまとめ, trip report,
  conference debrief, meeting readout. Renders decks via pptx-build.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Debrief Report Builder

You turn what actually happened — an international conference, a vendor event or trade show,
a standards meeting, a customer visit, a long internal discussion — into a report a specific
reader can act on. Two deliverables from one source: a **Markdown report** (full content +
appendices + evidence ledger) and a **derived .pptx** for the reading audience. The Markdown
is the source of truth; the deck is a rendering of it.

**Out of scope**: summarizing one document (`document-summary`), rendering slides
(`pptx-build`), designing slides without producing a file (`design-for-agents`), external
research as the deliverable (`grounded-research`), minutes as a verbatim legal record.

## Non-negotiables

1. **Reader before content.** Nothing is drafted until Step 0 is answered. Reader, the ask,
   disclosure scope, and the *original objective* of the trip/meeting determine the entire
   structure. Never infer them silently — ask.
2. **Answer first.** The executive summary is the first content page, before venue,
   agenda, or context. An executive who reads only that page must be able to act.
3. **Organized by issue, not by session.** A chronological walk through sessions is a
   transcript, not a report. Decide 5–10 takeaways first, group them into 3–5 issues.
   Session-by-session detail goes in the appendix.
4. **Fact / interpretation / hearsay are labeled and separated.** What was said, what you
   conclude from it, and what someone reported second-hand are three different things.
5. **Records are unreliable evidence and are treated as such.** Auto-transcripts misattribute
   speakers and turn "may" into "will". Numbers, names, dates, commitments, and speaker
   attribution are verified against the source span before they enter the report.
6. **Coverage is stated, trends are counted.** At a multi-track event you saw a fraction —
   say which fraction. 「潮流」 needs **≥3 independent observations** (different speakers,
   organizations, or papers), named. One keynote is one keynote.
7. **A vendor announcement is not a shipped product.** Every announcement is classified
   GA / Preview / ロードマップ / コンセプト before it is discussed, and attributed as
   「<社名>の発表」 rather than as fact.
8. **Every report ends in implications and actions.** So-what for our side, plus an action
   table with owner and due date. A report with no ask and no next step has no value.
9. **Ship inside a week.** Debriefs decay fast. Cut scope (fewer deep-dive topics, more
   appendix table) rather than the deadline.

## Event profiles — pick one at Step 0

The workflow, the gates, and the core structure are identical for all events. What differs is
the extra intake, the extra sections, and the failure modes. Deltas: `references/event-profiles.md`.

| Profile | Reader's real question | Adds |
|---|---|---|
| **A. 国際学会 / academic** | Where is the field going, are we behind, who should we talk to? | 分野の潮流, 当社の発表と反応, 注目研究者・機関, 次の投稿・共同研究, 論文リスト（DOI/arXiv） |
| **B. 商業カンファレンス / 展示会** | What actually ships, at what price, what does it do to our roadmap and our vendors? | 発表の成熟度一覧, 当社への影響, 競合・他ベンダーの動き, 自社の出展・登壇の成果 |
| **C. 標準化会合・委員会** | What was decided, what is our exposure, what is due next? | 審議・決定事項, 文書版数, 当社のポジションと発言, 宿題 |
| **D. 商談・顧客訪問** | Where does the deal stand and what did we commit to? | 相手の関心と懸念, 合意事項と持ち帰り, 次回アクション |
| **E. 社内会議・討議** | What was decided and who does what? | 決定事項, 未決の論点, アクション |

A/B ship their own full asset sets (`assets/profiles/`); C–E use the base assets plus the
deltas in the reference. A trip mixing a conference with customer visits stays **one** report:
conference profile for the body, the visits as their own issue section — unless the
disclosure scopes differ, in which case split.

## Step 0 — intake (mandatory, before any drafting)

Ask and record these. Anything the user cannot answer becomes a stated assumption in the
report header.

| Field | Why it changes the report |
|---|---|
| **Primary reader** (executive / manager / practitioners / mixed) | Depth, jargon, length, whether a deck is even needed |
| **Event profile** (A–E above) | Extra sections, source conventions, which asset set to start from |
| **Our role** — 聴講 / 登壇・発表 / 出展・スポンサー / 委員・座長 / 主催 | If we presented or exhibited, the reception and the return on that spend are required sections |
| **The ask** — approve, decide, fund, share, archive | Determines the last section and the summary's closing line |
| **Original objective** of the trip/meeting (what was it approved for?) | The report must answer it explicitly — achieved / partly / not |
| **Disclosure scope** — internal, department, public, NDA/Chatham House — **and any embargo date** | Gates photos, quotes, company names, pre-announcement material, the whole delivery |
| **Deadline and length budget** | Decides how many issues get deep-dived |
| **Secondary readers** | Whether one deck plus a detail Markdown, or two renderings |

If the reader is "mixed", default to: exec deck (8–12 slides) + practitioner Markdown
with the detail. Do not average them into one document that satisfies neither.

## Workflow

| Step | Action | Gate |
|---|---|---|
| 0 | Intake above | — |
| 1 | **Input inventory** — list every file with type, origin, timestamp, reliability, confidentiality. Name what is *missing* (unrecorded sessions, hallway conversations). For multi-track events, fix the **coverage statement** here (attended N of M sessions; tracks not covered). `assets/input-inventory.md` | |
| 2 | **Read inputs** per type rules (`references/inputs-and-evidence.md`). Pull quotes verbatim with file + timestamp/page. Flag numbers and attributions to verify | |
| 3 | **Takeaways first** — write 5–10 candidate takeaways, then group into 3–5 issues. Drop what serves no reader | |
| 4 | **Outline with conclusions** — every section carries a one-line conclusion (an action title), not a topic label | **Gate 1: user reviews the outline** |
| 5 | **Extra research** only for what blocks a conclusion (unknown vendor, term, figure). Sourced, appendix-bound, marked as post-event, never mixed into on-site observation. Use `grounded-research` / `evidence-check` | |
| 6 | **Markdown report** from the profile's report template (`assets/`), with the evidence ledger | **Gate 2: user reviews the report** |
| 7 | **Deck** — derive a spec from the profile's deck yaml, build and preview with `pptx-build` | **Gate 3: user reviews the PNGs** |
| 8 | **Disclosure check** (below), then finalize the action table and deliver | |

Gates are checkpoints with the user, not self-review. Do not skip ahead of one.

## Default structure

Adjust order only for a stated reason; the first three are fixed.

1. **Cover** — title, dates, location/venue, attendees (ours and theirs), author, date of
   report, **disclosure scope**
2. **Executive summary** — 3 conclusions + implication + the ask. One page. Standalone
3. **Objective and result** — what this trip/meeting was for, and whether it was achieved
4. **Issues** (3–5) — one section per issue, each opening with its conclusion
5. **Implications for us** — so-what, opportunities, risks, what changes our plan
6. **Actions** — table: item / owner / due date / decision needed from whom
7. **Appendix** — session or agenda table, venue and atmosphere, photos, glossary,
   post-event research notes, **evidence ledger**, input inventory, **coverage statement**

Profile-specific sections slot in after 4 (see the profile table). Venue atmosphere,
headcount, and photos are appendix material — at most one page in the body, and only if the
reader's decision depends on scale or mood. Per-reader variants and per-section writing
rules: `references/report-structure.md`.

## Evidence discipline (lightweight ledger)

Every quote, number, commitment, and attributed statement in the body gets a ledger row.
Ordinary narrative does not.

```markdown
| ID | 主張・引用 | 種別 | 出典 | 位置 | 確度 |
|----|-----------|------|------|------|------|
| E-01 | 「2027年から段階導入を検討している」 | 引用 | transcript_day1.md | 01:12:30 / A社B氏 | 高（原文照合済） |
| E-02 | 導入コストは約3億円 | 数値 | slide_photo_07.jpg | p.12 | 中（撮影スライドの読み取り） |
| E-03 | 他社も同様に苦戦しているらしい | 伝聞 | 懇親会メモ | — | 低（発言者の伝聞） |
| I-01 | 当社は要件定義を前倒しすべき | 解釈 | E-01, E-02 由来 | — | — |
```

- `E-` = grounded in an input; `I-` = our interpretation. Interpretations never appear
  unlabeled in the body and never in the same bullet as a fact.
- **Speaker attribution is the highest-risk field.** If diarization is the only basis,
  write 「（発言者は要確認）」 or attribute to the organization, not the person.
- **Preserve qualifiers verbatim.** 「検討している」 is not 「決定した」; "may" is not "will".
- **Absence of a record is not absence of the event.** State what was not captured.

Full rules per input type (transcript, photo, screen capture, handout, own notes) and the
verification protocol: `references/inputs-and-evidence.md`.

## Disclosure check (before delivery, always)

- [ ] Every photo cleared: no unconsented faces, no other company's confidential screen,
      no badge/name-tag details, no venue security information
- [ ] Photographed or captured slides credited to their author, and permitted to circulate
      at this disclosure scope
- [ ] NDA / Chatham House material either removed or de-attributed as agreed
- [ ] Named individuals' statements safe to quote at this scope; otherwise attribute to
      the organization or generalize
- [ ] **Embargoed material** (pre-announcements, press/analyst previews, unpublished papers)
      held until its date, or removed from this version
- [ ] Report header states the disclosure scope and the handling rule for onward sharing

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Session-by-session chronology | Reproduces the agenda; forces the reader to synthesize | Regroup into 3–5 issues; agenda goes to the appendix |
| Summary placed after context and venue | The only page an executive reads is not the first | Executive summary immediately after the cover |
| 「〜という話があった」 with no so-what | Reports the room, not the meaning | Every issue closes with what it means for us |
| Equal depth for every session | Wastes the budget on what does not matter | Deep-dive the top issues; list the rest in a table |
| Photo gallery | Decoration; adds no information | Information test: delete it — if nothing changes, cut it |
| Transcript summarized verbatim into slides | Inherits ASR errors and dropped qualifiers | Verify quotes, numbers, attributions against source spans |
| Interpretation written as fact | Reader cannot tell observation from opinion | `I-` rows, separate 所感 block, hedged wording |
| Hearsay promoted to first-hand | 「らしい」 becomes a company's official position | Mark 伝聞 and name the chain |
| Actions with no owner or date | Nothing happens after the report | Action table with owner + due date + decision-maker |
| Post-event research blended into observation | Reader believes it was heard on site | Appendix, labeled 追加調査, with sources |
| Deck as the archive | Detail and evidence lost | Markdown is the source of truth; deck is derived |
| Delivered three weeks later | Decisions already made without it | Ship in a week; cut scope, not the deadline |
| 「〜が潮流だった」 from one keynote | An impression sold as a finding | ≥3 named independent observations, or write it as one speaker's claim |
| Roadmap or preview reported as available | Reader plans against a product that does not exist | 成熟度区分 (GA / Preview / ロードマップ / コンセプト) on every announcement |
| Vendor marketing language adopted as ours | The report argues the vendor's case | Neutral wording; vendor phrasing only inside a quote |
| Paper-by-paper listing with no synthesis | A bibliography, not a report | 3–5 論点 first; the paper list is an appendix |
| Our own talk / booth omitted | The part we paid for goes unreported | 当社の発表と反応 / 出展の成果 when we presented or exhibited |
| Coverage left unstated at a multi-track event | Reader reads absence as evidence | Coverage statement: attended N of M, tracks not covered |

## Assets

Base set (profiles C–E, and any event not otherwise covered):

- `assets/report-template.md` — Markdown report skeleton (all sections + ledger)
- `assets/input-inventory.md` — inventory table with reliability, confidentiality, coverage
- `assets/deck.debrief-report.yaml` — `pptx-build` starter spec matching that structure

Profile sets (A and B — they differ enough to warrant their own):

- `assets/profiles/academic-conference/` — `report-template.md` + `deck.yaml`
- `assets/profiles/commercial-conference/` — `report-template.md` + `deck.yaml`

`assets/README.md` maps profile → files. Copy the profile set, do not merge two of them.

## Related skills

`pptx-build` (render and preview the deck) · `design-for-agents` (deck design and critique without a file) ·
`marp-slides` (Markdown-authored slides) · `document-figures` (diagram a structure worth
drawing) · `pdf-extract` (handouts and proceedings) · `document-summary` (one source
document in depth) · `grounded-research` / `evidence-check` / `literature-search`
(post-event fact-finding) · `essence-distiller` (when the draft is too long).

## References

- `references/event-profiles.md` — per-profile deltas (A 国際学会 / B 商業カンファレンス・展示会 /
  C 標準化会合 / D 商談・訪問 / E 社内討議), the coverage statement, the trend-count rule, and
  merging several attendees' notes
- `references/report-structure.md` — per-reader variants, section-by-section writing rules,
  length budgets, and the Markdown → slide mapping
- `references/inputs-and-evidence.md` — how to read each input type, the ledger schema,
  the verification protocol, and the confidentiality rules
