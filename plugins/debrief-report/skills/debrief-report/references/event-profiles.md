# Event Profiles

What changes by event type. The workflow, the gates, and the core structure are the same for
all of them; this file lists the deltas — extra intake questions, extra sections, source
conventions, and the failure modes specific to each.

Pick the profile at Step 0. A multi-purpose trip (conference + customer visits in the same
week) uses the conference profile for the body and gives the visits their own issue section —
one report, not two, unless the disclosure scopes differ.

---

## A. 国際学会 / Academic conference

**Reader's real question**: where is the field going, are we behind, who should we be talking
to, and what should we do differently next?

### Extra intake
- Our role: 聴講のみ / 口頭発表 / ポスター / 座長・オーガナイザ / 委員
- Whether our own presentation's reception must be reported (it usually must)
- Whether the audience is researchers (depth, method) or executives funding the travel (trend + positioning)

### Extra sections
- **分野の潮流** — what the field is converging on, with counts (below), not impressions
- **当社の発表と反応** — questions asked, criticisms raised, follow-ups requested. The
  criticism is the most valuable output of a conference and the most often omitted
- **注目すべき研究者・機関** — name, affiliation, what they work on, why they matter to us,
  contact status (話した / 名刺交換 / 未接触)
- **次の投稿・共同研究の候補** — venue, deadline, what we would need to have by then
- Appendix: **論文リスト** — 著者, タイトル, 会議/年, DOI or arXiv ID, 一行の要旨, 当社との関係

### Source conventions
- Cite papers, not sessions: `著者 (年) "タイトル", 学会名` + DOI/arXiv. A talk without a
  paper is cited as a talk and marked as such — slides shown on stage are not peer-reviewed.
- Three tiers of reliability at the same event, and they must not be flattened:
  査読付き論文 (高) > 招待講演・キーノートの主張 (中、査読なし) > 懇親会・廊下の話 (低、伝聞)
- Preprints: mark 未査読. Results announced as "under review" are not results yet.
- Quote English talks in **English verbatim** plus a translation. Non-native listening error
  stacks on top of ASR error; a paraphrased English quote re-translated into Japanese is
  two lossy steps away from what was said.

### Failure modes
| Failure | Fix |
|---|---|
| A per-paper list with no synthesis | 3–5 論点 first; the paper list is an appendix |
| One keynote's claim reported as "the field's direction" | Trend rule below (≥3 independent observations) |
| Our own talk's reception omitted | 当社の発表と反応 is a required section when we presented |
| Acceptance rate / scale quoted from memory | Take it from the program or the organizers' page, with a URL |
| Coverage silently partial | Coverage statement (below) — parallel tracks mean you saw a fraction |
| Preprint or work-in-progress cited as established | Mark 未査読 / 進行中 explicitly |

---

## B. 商業カンファレンス / ベンダーイベント / 展示会

**Reader's real question**: what is actually shippable, what does it cost, what does it mean
for our roadmap and our vendors, and what did competitors show?

### Extra intake
- Our role: 聴講 / 登壇 / 出展・スポンサー（費用と回収目標を確認する）
- Whether commercial terms (price, discount, roadmap dates) may appear at this disclosure scope
- **Embargo**: any pre-announcement, press, or analyst material and its release date

### Extra sections
- **発表の成熟度一覧** — every announcement classified before it is discussed:

  | 区分 | 意味 | 報告での扱い |
  |---|---|---|
  | GA | 今日買える・使える | 検証・採用判断の対象 |
  | Preview / Beta | 制限付き提供 | 条件（地域・SLA・課金）を明記 |
  | Announced / ロードマップ | 時期の宣言のみ | 「予定」であることを明記、過去の遅延実績があれば添える |
  | Vision / コンセプト | 出荷計画なし | 潮流の材料。計画の前提にはしない |

- **当社への影響** — 現行契約・ロードマップ・コストへの具体的な影響
- **競合・他ベンダーの動き** — what they showed, what they did not show
- **自社の出展・登壇の成果**（出展した場合）— リード数、商談化、反応、費用対効果
- Appendix: 収集資料・ブース資料一覧、担当者の連絡先

### Source conventions
- **Vendor claims are primary sources about the vendor's intentions, not about reality.**
  Cite them as 「<社名>の発表」, never as an established fact. Benchmarks, "up to N×",
  and customer-success numbers carry the vendor's own framing — record the number with its
  conditions or drop it.
- Prefer the official session recording, press release, or documentation URL over a
  photographed slide for anything quantitative.
- Customer case studies: record scale and conditions (規模・期間・前提), or the number is
  not transferable to us.
- Analyst sessions and paid-sponsor sessions are labeled as such.

### Failure modes
| Failure | Fix |
|---|---|
| Roadmap item reported as available | 成熟度一覧 — every announcement gets a 区分 |
| Marketing copy adopted as our language | Rewrite in neutral terms; keep the vendor's phrasing only inside a quote |
| Booth impressions presented as market share | Label as 観察・印象, or find a sourced figure |
| Embargoed material circulated early | Embargo date recorded at Step 0 and checked at the disclosure gate |
| Exhibition cost not reconciled | 自社の出展・登壇の成果 section when we spent budget |
| "N社が発表" from one booth conversation | Trend rule below |

---

## C. 標準化会合 / 業界団体・委員会

**Reader's real question**: what was decided, what is our exposure, and what must we do
before the next meeting?

- Extra sections: **審議・決定事項**（議題・結論・投票結果）, **文書版数**（ドラフト番号と
  日付）, **当社のポジションと発言**, **次回までの宿題（担当・期限）**
- Cite the document ID and revision, not the discussion: 決定は文書に残る
- Failure modes: 合意と個人的な発言を混同する / ドラフト版数を書かず後から追えなくなる /
  他社の立場を公式見解として断定する（会合の秘匿ルールを確認）

---

## D. 商談・顧客訪問・パートナー協議

- Extra sections: **相手の関心と懸念**, **合意事項と持ち帰り事項**, **次回アクション**
- Commitments — ours and theirs — are the highest-value and highest-risk content: every one
  gets a ledger row with the exact wording, and anything decision-bearing is confirmed in
  writing with the counterpart before the report asserts it
- Failure modes: 相手の社交辞令を合意として書く / 検討中を内諾と書く / 価格に条件を付け忘れる

---

## E. 社内会議・討議

- Extra sections: **決定事項**, **未決事項と論点**, **アクション**
- The lightest profile; the ledger covers decisions and commitments only
- Failure mode: 議論の経過をすべて書いて決定が埋もれる — 決定を先頭に

---

## Rules that apply to all large multi-track events (A and B especially)

### Coverage statement (required)

A conference with parallel tracks means you saw a fraction of it. State it in the report
header or the appendix:

> 全<N>セッション中<M>セッションに参加（トラック<X>は不参加）。本報告は参加分と公開資料に
> 基づく。<Y>分野は扱っていない。

Without this, a reader treats absence as evidence. If the program or proceedings are public,
link them so the reader can see what was not covered.

### Trend claims need counted evidence

「〜が潮流だった」 is a claim about the whole event, and a single keynote cannot support it.
Require **at least three independent observations** — different speakers, organizations, or
papers — and name them:

> 「エージェント運用の標準化」は基調講演を含む<5>セッションで扱われた（<A社>, <B大学>,
> <C社>, パネル<D>, ポスター<E>）。[E-07〜E-11]

If you have only one or two, write it as そのように述べた個別の主張, not as a trend. When
counts come from the program rather than attendance, say so.

### Merging multiple attendees' notes

- Each note keeps its author in the inventory; the ledger's 出典 column names who recorded it
- Where two attendees disagree about what was said, **report the disagreement**, do not average
- One author owns the merged report and its conclusions
