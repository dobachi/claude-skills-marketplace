# Review sheet format

The grammar `review_sheet.py` writes and reads. Anything not described here is passed through
untouched, so the reviewer may add headings, notes or whole paragraphs; only the pieces below
have meaning to the tool.

## Contents

- Front matter
- Body layout
- Location anchors
- Comment lines
- Marks (status)
- Reply lines
- Hint lines
- Ids
- What the parser ignores
- Log file
- Carry semantics
- `where` output and URL templates
- Exit codes

## Front matter

```yaml
---
review_sheet: 1            # format version; its presence is what makes a file a sheet
round: 1
reviewer: ""               # --reviewer; one sheet per reviewer per round
generated: 2026-10-31T20:44:29+09:00
host: k16
artifacts:
  - path: /abs/path/summary.pptx
    kind: pptx             # pptx | docx | md | pdf
    sha256: b81349d8       # first 8 hex digits; `check` compares it with the file on disk
    units: 9               # slides / headings / pages found
---
```

Flat `key: value` lines plus one `artifacts:` list. The parser is deliberately small; do not
add nested structures by hand.

## Body layout

```
# レビューシート（第1回）
<--header line, e.g. a confidentiality marking>
<italic how-to line>
**対象**  table: A1 / A2 … with absolute paths and unit counts

## 全体 <!-- loc: G -->
*hint*
- [ ]

## A1. summary.pptx <!-- art: A1 -->          (only when more than one artifact)
### p.1 表紙 <!-- loc: A1.S1 -->
> excerpt line
> excerpt line
- [ ]
### p.2 要旨 <!-- loc: A1.S2 -->
…
```

With a single artifact the `art:` level is omitted, locations are `##`, and ids have no `A1.`
prefix (`S2`, `H3`, `P4`).

## Location anchors

A heading becomes a location when it carries `<!-- loc: ID -->`. The heading level does not
matter; the anchor does. A location runs from its heading to the next heading of any level.

| Artifact | Unit | Id | Shown as |
|---|---|---|---|
| `.pptx` | slide, in presentation order | `S<n>` | `p.<n> <title>`; `（非表示）` when hidden |
| `.docx` | heading section at depth ≤ `--depth` | `H<n>` | heading text; `H0` = text before the first heading |
| `.md` | same as `.docx` (ATX headings; fenced code ignored) | `H<n>` | same |
| `.pdf` | page | `P<n>` | `p.<n> <first line>` |

Slide titles come from the `title` / `ctrTitle` placeholder, else the first text on the slide.
Word heading levels are resolved through `styles.xml` names, so both pandoc ids (`Heading1`) and
Japanese Word ids (`1` named `見出し 1`) work. Deeper headings than `--depth` appear in the
excerpt as `- <heading>` lines. Tables appear as `cell | cell` lines.

`<!-- art: A<n> -->` marks an artifact section; it is only a divider.

## Comment lines

Inside a location, a comment is a top-level list item with a checkbox:

```
- [ ] S2-1: 結論を一文で。
  理由も添える。                 ← continuation: indented, belongs to the comment above
```

The reviewer may also write without the checkbox. `ingest` normalizes all of these to the
form above:

```
予算の根拠が弱い                  ← bare paragraph
- 日付を入れる                    ← bare list item
1. 表を図に                       ← numbered item
```

`check` reports bare lines as findings so they are not missed; `ingest` fixes them.

An empty `- [ ]` is "no comment" and is ignored everywhere (counted as `blank`).

## Marks (status)

| Mark | Status | Set by |
|---|---|---|
| `[ ]` | open | reviewer (also the reviewer's answer to a `[?]`) |
| `[x]` | applied | `resolve --status applied` |
| `[-]` | declined | `resolve --status declined` |
| `[?]` | question — the AI needs the reviewer's answer | `resolve --status question` |

To answer a `[?]`, the reviewer sets it back to `[ ]` and continues on the same line. `ingest`
then lists it as open again, with the AI's earlier `↳` reply still underneath.

## Reply lines

```
  - ↳ r1 worker-a: p.2 の本文を一文にした (deck.yaml slide 2)
  - ↳ 第1回から持ち越し
```

An indented line starting with `↳` (with or without `- `) is a reply and belongs to the comment
above. `resolve --note` writes `↳ r<round>[ <by>]: <note>` after the comment's continuation
lines and existing replies. The reviewer's text is never edited.

## Hint lines

A line wrapped entirely in `*…*` or `_…_` is an instruction written by the generator (the
how-to line, the global hint). The parser skips it. The reviewer may delete these lines.

## Ids

`<location>-<n>`: `G-1`, `S3-2`, `H5-1`, `A2.H4-1`. Assigned by `ingest` in file order per
location, continuing from the highest number already present, so running `ingest` twice
changes nothing and carried ids stay valid. `check` reports a duplicate id and an id whose
prefix does not match the location it sits under.

## What the parser ignores

- everything before the first `<!-- loc: … -->` heading (title, how-to, artifact table)
- blank lines, blockquote lines (`>`), HTML comments, hint lines
- headings without a `loc:` anchor end the current location and start nothing

## Log file

`resolve` appends to `review-log.md` in the sheet's directory (or `--log`). Created with a
header on first use; append-only afterwards.

```
| time | round | sheet | id | location | comment | result | note |
|---|---|---|---|---|---|---|---|
| 2026-10-31T20:45:03+09:00 | 1 | review-r1.md | S2-1 | S2 | 結論を一文で。 理由も添える。 | applied | p.2 の本文を一文にした (deck.yaml slide 2) |
```

Comment text is truncated to 80 characters, the note to 160; pipes are escaped.

## Carry semantics

`new --carry <previous sheet>`:

- round defaults to previous round + 1
- every non-empty comment marked `[ ]` or `[?]` is copied, with its id, continuation lines and
  replies, under the location with the same id in the new sheet, followed by a
  `↳ 第N回から持ち越し` line
- a carried comment whose location no longer exists goes into the global section prefixed
  `（前回 <loc>）`
- `[x]` and `[-]` items are not carried; the log keeps them

## `where` output and URL templates

```
## 開く場所 / Where to open
- host: k16 (tailscale 100.64.0.1), user dobachi
- sheet: /abs/review/review-r2.md  (round 2, updated 2026-10-31 20:45, open 3, question 1)
- log: /abs/review/review-log.md
- artifact pptx: /abs/output/summary.pptx  (updated 2026-10-31 20:45)
- open on this host:  fude-cli here /abs/review/review-r2.md
- open from another machine (after `fude-cli setup k16`):  fude-cli remote k16 /abs/review/review-r2.md
- fude-cli --check: Fude 0.8.21 on home answers via tcp://127.0.0.1:47985
- url: https://100.64.0.1:3000/?file=review-r2.md
```

An artifact that changed after the sheet was generated is flagged `⚠ changed after the sheet`.

`--url-template` (or `$REVIEW_SHEET_URL_TEMPLATE`) placeholders: `{path}` absolute path,
`{relpath}` path relative to `$REVIEW_SHEET_URL_ROOT` (else the file name), `{host}`, `{addr}`
(Tailscale IPv4, else the first LAN address), `{name}`. A template containing `token` or `key`
is refused: the reader's browser keeps the key after the first visit, and a key in a chat reply
is a key in a log.

## Exit codes

| Code | `new` | `check` | `ingest` | `resolve` | `where` |
|---|---|---|---|---|---|
| 0 | sheet written | valid, no findings | plan printed | recorded | printed |
| 1 | output exists (no `--force`) | findings (duplicate id, bare line, stale or missing artifact) | — | unknown id | — |
| 2 | unsupported type, missing file, not a zip, pdf without poppler | not a sheet | not a sheet | not a sheet | not a sheet, token in template |
