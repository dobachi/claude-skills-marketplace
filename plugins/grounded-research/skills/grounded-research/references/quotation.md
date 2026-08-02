# Quotation & Span Check

Two rules with one purpose: what the source said reaches the reader in the source's own
words, and a machine — not a model — confirms those words are on the page.

The blind verifier checks **claim ↔ span**. Nothing in the pipeline checks **span ↔ page**:
the retriever *asserts* its span is verbatim, and a drifted or invented span is indistinguishable
from a faithful one at every downstream step. `scripts/check_spans.py` closes that hop.

## Part 1 — Quoting in the body

### What gets quoted

Quote — do not paraphrase — when the claim is:

- **numeric** (any figure, date, price, threshold, percentage, version)
- **definitional** (what a term, requirement level, or scope means)
- **load-bearing** (the recommendation changes if it is wrong)
- **contested or `Disputed`** (both sides quoted, never one paraphrased against the other's quote)
- **hedged in the source** ("may", "in this sample", "up to") — paraphrase is where hedges die

Everything else stays a paraphrase carrying its `C-` ID. Quoting every sentence produces a
transcript, not a report; the quote is a spotlight and loses its force if it is always on.

### Form

```markdown
- Vendor A's published entry price is $49 per seat per month [C-02]:
  > "$49 per seat per month, billed annually"
  > — S-02, Vendor A pricing page (T2, accessed 2026-08-01)
```

- The quote block carries the `S-` ID, the source name, the tier, and the access date.
  A quote whose attribution is only a URL cannot be traced back through the ledger.
- The claim sentence carries the `C-` ID. Both IDs appear: the reader jumps to the ledger row
  from the claim and to the register row from the quote.

### Editing inside a quote

The quoted characters are the source's, not yours. Permitted, and nothing else:

| Operation | Notation | Note |
|---|---|---|
| Elision | `…` | Only within a sentence or between sentences; never across a scope boundary that changes meaning |
| Clarifying insertion | `[the API]` | Square brackets, yours, minimal |
| Translation | separate line below, labeled | The original stays; see below |
| Added emphasis | `**bold**` + `(emphasis added)` | Rare. Unmarked emphasis is an edit |

Forbidden: normalizing numbers or units ("roughly 18%" → "18%"), dropping a hedge, fixing the
source's typo silently, changing tense or person to fit your sentence, joining two non-adjacent
sentences without `…`, or trimming a scope qualifier ("12%" without "in the EU trial").

If the quote does not fit your sentence, rewrite **your sentence**.

### Translation

Quote in the source language. Put the translation on the line below, labeled, never inside the
quote marks:

```markdown
> 「月額 49 ドルから利用できます」
> — S-02, 料金ページ (T2, accessed 2026-08-01) / 訳: "Available from $49 per month"
```

A translated quote presented as the quote is a paraphrase with quotation marks around it, and
the span check will fail it — correctly.

### The quote is the span

Body quotes are **copied from the ledger's Span column**, character for character. Never retype
a quote from the draft, from the retriever's chat output, or from memory. If the body quote and
the ledger span differ, the ledger wins and the body is wrong.

This is what makes the mechanical check possible at all: one string, checked once, appears in
both places.

## Part 2 — Span check (`scripts/check_spans.py`)

Run it on the finished report, as part of the grounding gate. It parses the report's own
Source Register and Claim Ledger, re-fetches each registered URL, and looks for each span as a
literal substring.

```bash
python3 scripts/check_spans.py report.md                     # all spans
python3 scripts/check_spans.py report.md --quiet              # only non-EXACT
python3 scripts/check_spans.py report.md --local S-04=saved.html   # paywalled/JS page saved by hand
python3 scripts/check_spans.py report.md --json               # machine-readable
```

Stdlib only. Elided spans are split on `…` and every fragment must be found. Pages are cached,
so re-running after a ledger fix costs nothing. Exit codes: `0` clean, `1` NOT-FOUND present,
`2` UNREACHABLE present, `3` the check could not run.

The Span column is located **from the table header**, so column order does not matter. A ledger
with no Span column at all — the pre-v1.2 shape `ID | Claim | Source | Kind | Status` — reports
`Claim Ledger has no Span column: N claims, 0 checkable spans` and exits `3`. That is the honest
answer: nothing was verified. It is deliberately not one NOT-FOUND per row, which would read as
N hallucinations when the truth is one missing column, and would train you to ignore the tool.

**Body quotes are checked too.** Any blockquote whose attribution line names an `S-` ID is
matched against that source's page *and* against the ledger span it should have been copied
from; those rows report as claim `body`. `not copied from any ledger span` means either the
quote drifted during drafting or a quote entered the body that never went through the ledger —
both are the same defect, a claim the audit trail does not cover. Blockquotes without an `S-`
attribution are ignored, so ordinary block quoting in the prose costs nothing.

### Verdicts

| Verdict | Meaning | Action |
|---|---|---|
| `EXACT` | Span is on the page, character for character | Ships |
| `NORMALIZED` | Found only after folding whitespace, quote/dash characters, or letter case | Ships, but **correct the ledger span to the page's actual characters** — then it should be EXACT |
| `NOT-FOUND` | Page fetched, span absent | **Blocks delivery.** Triage below |
| `UNREACHABLE` | Could not fetch or parse (PDF without `pdftotext`, paywall, login, JS-rendered, dead link) | Not a pass. Check by hand, then record that you did |

### NOT-FOUND triage

`NOT-FOUND` is a finding, not a tooling annoyance. In order of likelihood:

| Cause | Signature | Fix |
|---|---|---|
| Retriever paraphrased and called it a span | Reads fluently, no odd characters | Re-open the page, take a real span. If none exists, the claim is `Unsupported` |
| Span stitched from two places | Long, argues the claim too neatly | Split into two spans and two claim rows, or elide with `…` |
| Number normalized in the span | Span has a clean figure, page has a hedged one | Restore the page's characters; re-check whether the claim still holds |
| Quoted from a search snippet | URL is a search/redirector, or the page was never opened | Open the page or drop the source — snippets are generated text |
| Page changed since retrieval | Access date is old; other spans from the same source also fail | Re-retrieve. If the old text mattered, register an archive snapshot as a separate row |
| Text lives in an image, table render, or JS payload | Page fetches fine, everything from it fails | Save the rendered page and pass `--local`; if impossible, mark the source UNREACHABLE-by-hand |

Never resolve a `NOT-FOUND` by loosening the span until it matches. The span exists to prove the
claim; a span trimmed to whatever the page happens to contain proves nothing.

### What the check does not prove

- **Not that the claim is true.** The span can be on the page and still fail to support the claim —
  that is the blind verifier's job, and it stays.
- **Not that the source is any good.** A T4 content farm's spans match perfectly.
- **Not that the page is the original.** Restatement laundering is invisible to string matching; trace up.
- **Not permanence.** It proves the text was there on the day it ran. Record the date.

### Recording the result

The report states the outcome, in the coverage section:

```markdown
**Span check**: 24 spans, 22 EXACT, 2 NORMALIZED (ledger corrected), 0 NOT-FOUND,
1 UNREACHABLE (S-07, paywalled — verified by hand 2026-08-01). Tool: scripts/check_spans.py, 2026-08-01.
```

A report that ran the check and says so is auditable. A report that ran it and stays quiet is
indistinguishable from one that did not.
