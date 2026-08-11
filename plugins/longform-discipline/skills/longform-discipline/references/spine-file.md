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
- 表記:             漢字/かな basis, 送り仮名, カタカナ長音 (サーバー vs サーバ), 数字 (半角/全角)
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

## Re-entry prompt

At the start of a session, or after compaction, the spine is loaded and read *before* anything
else. A workable re-entry is exactly:

> Read `<draft>.spine.md`. We are writing §N. Load only §N's outline entry, the last ~300 words of
> §N-1, and the glossary. Do not load the rest of the draft.

That constraint is the point. Loading the whole draft to "get oriented" puts the working material
in the middle of a long context, which is where it is used worst.
