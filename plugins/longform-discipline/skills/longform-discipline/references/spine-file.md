# The Spine File

The document's state, kept on disk so it survives compaction, session boundaries, and the model's
own drift. The draft is the *output*; the spine is the *state*. If the two disagree, the spine is
what gets reconciled first.

Name it after the draft: `whitepaper.md` → `whitepaper.spine.md`. One spine per document.

## Why a file and not a prompt

Instructions repeated in conversation fall out of context the moment it is summarized. A file is
re-read at the start of every session and after every compaction, which is the property that makes
it worth maintaining. Same reason `CLAUDE.md` exists, applied to one document. See
`failure-modes.md` → *state outside the context window*.

## Rules

- **Update it in the same turn as the draft.** A spine updated "later" is already wrong.
- **Keep it short enough to load every time.** Roughly one screen per section entry. It is a
  control surface, not an archive; long background goes in a separate notes file.
- **Never let it contradict itself.** Contradictory persistent instructions get resolved
  arbitrarily. When the outline changes, delete the old entry — do not append the new one beside it.
- **The glossary is append-only in spirit, editable in fact.** Changing a term's canonical form
  means a sweep of the existing draft, not just a new spine row. Record the sweep.
- **Status values are honest, not aspirational.** `未着手 / 起草中 / 初稿 / 自己レビュー済 / 確定`
  (or `todo / drafting / drafted / reviewed / final`).

## Schema

```markdown
# <Document title> — spine

## Contract
- Purpose:        <what this document is for, one sentence>
- Audience:       <who reads it, and what they already know>
- Desired impact: <what the reader should do or believe afterwards>
- Target length:  <total>, currently <actual>
- Deliverable:    <file / format / deadline>

## Style contract
Decide these BEFORE drafting. Deciding them at the end means rewriting everything.
- 文体 / Register:  である調 | ですます調 | formal EN | ...
- 表記:             漢字/かな basis, 送り仮名, カタカナ長音 (サーバー vs サーバ)
- 数字:             半角/全角
- 記号:             括弧, 箇条書きの句点有無, ダッシュ
- Person / voice:   first person plural | impersonal | ...
- Citation style:   <style>, and where citations live
- Banned:           <phrasings this document does not use>

## Outline
Revisable. When a section fights its entry, change the entry and note why — do not force the prose.

| # | Section | Claim it must land | Budget | Status | Must not repeat |
|---|---------|--------------------|--------|--------|-----------------|
| 1 | ...     | ...                | 1,500字 | 初稿   | —               |
| 2 | ...     | ...                | 2,000字 | 起草中 | §1 の前提説明    |

### Outline changes
- 2026-08-11 §4 split into §4/§5 — the measurement discussion outgrew its entry.

## Glossary
Load-bearing terms only. Every row is a `drift_scan.py --spine` check.

| Canonical | Never write | Definition (as used in THIS document) | First defined |
|-----------|-------------|----------------------------------------|---------------|
| サーバー    | サーバ       | ...                                    | §2            |
| データ空間  | データスペース | ...                                  | §1            |

## 意図台帳 / Intent ledger
書く前・直す前に1行。**完了条件を先に書く**のが要点で、後から書くと「今できているもの」に
合わせて書いてしまい、ずれを固定するだけになる。

| ID | 対象 | 意図（なぜ） | 完了条件（何が真になれば終わりか） | 状態 |
|----|------|-------------|--------------------------------|------|
| I-1 | §3 | 前提が明示されていない | §3が調達制度の制約を明文で1文以上述べている | 対応中 |
| I-2 | §5 新規 | 主要な反論に答えていない | §5が反論3件に各1段落で答えている | 未着手 |

- **完了条件は「失敗しうる形」で書く。** 「もっと良くする」は失敗できないので条件ではない。
  `intent-unmeasurable` が弾く。
- **途中で変えるなら、行を書き換えず注記して変える。** 上書きはずれを公式化するだけで、
  見えなくする。
- **構造の条件でよい。** 「§4の冒頭に結論が1文で置かれている」のような条件は、語が本文に
  現れなくて当然なので presence テストの対象外になる。
- 状態: `未着手 / 対応中 / 完了`。ループの終了条件として自動化する段になったら `loop-goal`。

## Claims
Anything a reader could challenge. `unverified` rows are the human's review list.

| ID | Claim | Section | Source | Status |
|----|-------|---------|--------|--------|
| K-1 | ... | §3 | <url / doc> | verified |
| K-2 | ... | §5 | —          | unverified |

## Open questions
- [ ] <thing that is not decided yet, and who decides it>

## Session log
One line per session. This is what a fresh context reads to know where it is.
- 2026-08-11 §1–§3 drafted. §4 outline revised. Terminology: fixed サーバー.
```

## What the scanner actually reads

`drift_scan.py --spine` parses **six** sections. Two are enforced as rules; four drive the intent
and content checks, which ask whether the draft does what the spine said it would.

**Content — the spine is what makes these possible at all.** Without `--spine` they do not run,
and the scan header says so rather than reading as a clean pass:

| Spine section | Enforced as | Example finding |
|---|---|---|
| `## 意図台帳` → `完了条件` | Must exist and be failable; its subject words should appear in the target | `HIGH 意図 I-2 の完了条件「もっと良くする」は測れません` |
| `## Outline` → `Claim it must land` | The section must at least name what its claim is about | `HIGH 主旨「遅延と可用性の両立が実証された」の語が本文に1つも現れません` |
| `## Claims` → `Status` ≠ verified | Surfaced verbatim as the human's review list | `INFO 未検証の主張 K-2「可用性は99.9%を満たす」` |
| `## Glossary` → `First defined` | The term must not appear in an earlier section | `WARN 用語「コネクタ」は 第2章 で定義される予定ですが…` |
| `## Contract` → `Audience` | Read for the content-review procedure, not enforced mechanically | — |

Fill the `Claim it must land` column. An outline row without it is skipped silently — the check
cannot invent what a section was supposed to establish.

**Rules — these are checked whether or not you meant them as rules:**

| Spine line | Enforced as | Example finding |
|---|---|---|
| `- 文体 / Register: である調` | Every 敬体 sentence is a violation of the declared register | `HIGH 宣言は「常体」ですが、2文が宣言と異なります` |
| `- 数字: 半角` | Full-width digits in prose | `WARN 全角の数字が2件` |
| `- 記号: …箇条書きの句点なし` | List items ending in 。 | `WARN 2行が異なります` |
| `- Banned: 「させていただく」` | Substring match in prose (quotes excluded) | `HIGH 禁止された表現「させていただく」が1件` |
| `## Glossary` → `Never write` column | Banned variants of a canonical term | `HIGH 用語集違反:「サーバ」が1件` |

Two things follow from that:

- **Fill the alternatives in.** A line left as the template's `である調 \| ですます調 \| formal EN`
  is treated as *undecided* and silently skipped — the scanner will not guess which one you meant.
  Same for `半角/全角`. Check the header line of the scan output: it prints the contract it parsed,
  or `no style contract declared`.
- **A declared register replaces the mixing check.** With `文体` set, `style-mixing` stands down and
  `declared-style-violation` reports the same sentences against your stated intent instead of
  against the document's own majority. A document uniformly in the *wrong* register passes the
  first check and fails the second — which is the point.

## Re-entry prompt

At the start of a session, or after compaction, the spine is loaded and read *before* anything
else. A workable re-entry is exactly:

> Read `<draft>.spine.md`. We are writing §N. Load only §N's outline entry, the last ~300 words of
> §N-1, and the glossary. Do not load the rest of the draft.

That constraint is the point. Loading the whole draft to "get oriented" puts the working material
in the middle of a long context, which is where it is used worst.
