---
name: review-roundtrip
description: Stabilizes the loop where a person reviews an AI-made document or deck and the AI applies the comments. Generates a Markdown comment sheet shaped like the artifact (a global section, then one section per slide, heading or page, each with a short excerpt) from .pptx, .docx, .md or .pdf, so the reviewer writes next to the thing they mean from any device. Ingests the filled sheet into numbered comments with a work plan (global first, then independent locations that can run in parallel), records every outcome in the sheet and a log, carries unresolved items into the next round, and ends each reply with a hand-over block naming host, absolute paths and the commands to open the sheet. Use for 「コメントシートを作って」「レビュー用の md を用意して」「コメントを反映して」「コメントを取り込んで」「レビューの往復」, "make a review sheet", "apply the reviewer's comments", "comment round-trip" or when a deliverable goes to a person for comments. Judging the document is doc-review's job; rebuilding it is pptx-build's or docx's; serving a preview is preview-access's.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# review-roundtrip

One job: a person comments on a document or deck, the AI applies the comments, and nothing is
lost between the two. Not the review itself (doc-review), not the rebuild (pptx-build, docx),
not the preview (preview-access). The sheet, the bookkeeping, and the hand-over.

It exists because the same four things kept going wrong by hand: a comment with no location
("the second bullet" of which page?), an AI "done" with no record of what changed where, the
reviewer asking "where is the file again?" from another device, and every round applied
serially even when the comments touched different slides.

## The loop

```
PREPARE    build the artifact(s)            →  review_sheet.py new   →  one sheet
HAND OVER  reply ends with `where` block     (host, paths, how to open)
           ... the reviewer writes in the sheet, in Fude / any Markdown editor ...
INGEST     review_sheet.py check, ingest     →  ids, counts, work plan
APPLY      global comments first, then locations in parallel; fix the SOURCE, rebuild
RECORD     review_sheet.py resolve per comment  (mark + ↳ reply + log row)
NEXT       review_sheet.py new --carry      →  round N+1 sheet with the [ ] and [?] items
HAND OVER  reply ends with `where` block again
```

All commands are `python3 <skill-dir>/scripts/review_sheet.py <subcommand>`. Stdlib only;
`.pdf` needs poppler. Exit `0` ok, `1` findings, `2` usage error or precondition missing.

## 1. Prepare: the sheet

```bash
review_sheet.py new output/summary.pptx output/report.docx \
    --out review/review-r1.md --header "情報区分: 社外秘" [--reviewer NAME] [--depth 2] [--lang en]
```

- One sheet can cover several artifacts (a one-pager, a summary deck and a detailed Word
  file built from the same source). Each gets a section `A1`, `A2`, … and its own locations.
- Locations follow the artifact's own structure: a slide (`S3`, shown as `p.3 <title>`), a
  heading section (`H2`, shown with its text; deeper headings fold into the excerpt; raise
  `--depth` for finer sections), a page (`P4`). Every location carries a short excerpt so the
  reviewer can comment from a phone without opening the deck.
- The **global section** (`G`) comes first, for comments that belong to no single place.
- Put the sheet where the project keeps review material, next to the source, not in `/tmp`.
  The front matter records host, round, and a hash of each artifact.
- Do not hand-write the sheet. A hand-written one has no anchors, and the next round cannot
  carry anything.

## 2. Hand over

Every reply that creates or updates a sheet ends with the output of

```bash
review_sheet.py where review/review-r1.md [--url-template 'https://{addr}:3000/?file={relpath}']
```

verbatim: host, absolute path of the sheet, the log, each artifact with its timestamp, and
the commands that open the sheet (`fude-cli here <path>` on this host, `fude-cli remote <host>
<path>` from another machine, which GUI answers). The reviewer is often on another device
and has no scrollback; a path without a host is not an address. Never put a key or token in
the template. If the project uses a browser editor with a URL scheme, set
`REVIEW_SHEET_URL_TEMPLATE` once (placeholders `{path} {relpath} {host} {addr} {name}`;
`REVIEW_SHEET_URL_ROOT` makes `{relpath}` relative to the served root).

## 3. Ingest

```bash
review_sheet.py check  review/review-r1.md            # format, duplicate ids, stale artifact
review_sheet.py ingest review/review-r1.md [more sheets] [--json]
```

`ingest` gives every non-empty comment an id (`G-1`, `S3-2`, `A2.H4-1`), turns lines the
reviewer typed without a checkbox into comments, and prints the plan: global comments in
order, then comments grouped by location. It never rewrites the reviewer's words. A
`stale:` line means the artifact changed after the sheet was made; the comments refer to the
old version, so read them against it before deciding anything.

Several reviewers: one sheet per reviewer (`--reviewer`), ingested together in one call. Comments
on the same location from different people are listed under that location, together.

## 4. Apply

Order and parallelism come from the plan:

1. **Global comments first, serially.** They change scope, length or tone, and can make
   individual comments moot. Re-read the location list after they are done.
2. **Locations are independent.** When there are many and the format allows disjoint edits
   (one slide each in a deck spec, one section each in Markdown), hand each location group to
   a worker in parallel. Only the conductor writes the sheet (step 5); workers report back
   what they changed and where.
3. **Fix the source, not the output.** When a deck and a Word file both come from one
   `report.md` or `deck.yaml`, apply there, rebuild every output, and record which outputs
   changed. Editing a `.pptx` by hand drifts from its spec by the next round.
4. **Do not guess.** A comment that can be read two ways becomes `question` with the two
   readings in the note. The reviewer answers it in the next round.

Format hand-offs: `.pptx` to pptx-build (spec → rebuild, or extract then edit); `.docx` to the
docx skill or the project's pandoc pipeline; `.md` directly; `.pdf` to whatever produced it.

## 5. Record

```bash
review_sheet.py resolve review/review-r1.md S3-2 --status applied \
    --note "p.3 の 2 つ目の箇条書きを削り、根拠を注に移した (deck.yaml slide 3)" [--by worker-a]
review_sheet.py resolve review/review-r1.md G-1 --status declined --note "読み手の指定どおりの量"
review_sheet.py resolve review/review-r1.md S5-1 --status question --note "表を残すか図にするか"
```

Each call rewrites the mark (`[x]` applied, `[-]` declined, `[?]` question), adds a `↳` reply
under the comment, and appends a row to `review-log.md` beside the sheet. The note must name
**where** the change landed (slide or section, and the file edited). "Done" is not a note.
A comment marked applied without a location in its note is the failure this skill exists for.

## 6. Next round

```bash
review_sheet.py new output/summary.pptx output/report.docx --carry review/review-r1.md --out review/review-r2.md
```

The new sheet is built from the rebuilt artifacts (new excerpts, new hashes) and carries every
`[ ]` and `[?]` item to its location, marked as carried; items whose location disappeared land
in the global section with their old location named. Then hand over again (step 2).

## Rules

1. **The sheet is generated, never hand-written.** Anchors and hashes come from the artifact.
2. **Reviewer text is read-only.** The tool changes the mark and adds `↳` lines; nothing else.
3. **Global before local.** Then locations in parallel, one writer for the sheet.
4. **Every outcome has a location.** Applied means "changed X in file Y"; declined means why.
5. **Every reply ends with `where`.** Host, absolute paths, open commands. No `localhost`-only
   links, no keys.
6. **One sheet per reviewer per round.** Rounds are files; the log is the history.
7. **Keep the project's own confidentiality line** on every sheet (`--header`).

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| Hand-written comments file with "コメント:" blanks | No anchors, no ids, no carry; the next round starts from zero | `new`, then `--carry` |
| Asking for comments in chat | Lost with the session; no place to point at | A sheet beside the source |
| "Reflected your comments" with no per-comment record | The reviewer re-reads everything to find what moved | `resolve` with a located note |
| Applying slide comments before the "cut it in half" comment | Work discarded when the global change lands | Global first |
| Two workers editing the same sheet | Lost updates in a read-modify-write file | Workers report; the conductor resolves |
| Editing the `.pptx` directly when it has a spec | Drift from the spec at the next rebuild | Fix the source, rebuild |
| Reply without host and path | The reviewer on another device cannot open anything | `where` block, every time |
| Guessing an ambiguous comment | A confident wrong change costs a round | `question` with the readings |

## References

- `references/sheet-format.md` — the sheet grammar (front matter, anchors, comment lines,
  marks, replies, ids, hint lines), the log format, carry semantics, exit codes.
- `scripts/review_sheet.py` — `new` / `check` / `ingest` / `resolve` / `where`.
- `tests/run_tests.sh` — three-direction tests on pandoc-built fixtures, including a `.docx`
  with Japanese Word style ids.
