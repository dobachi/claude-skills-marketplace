# Refactor Mode — rebuilding a deck that already exists

The third thing this skill does. Default mode builds from scratch, template-fill
mode builds into a corporate template, and **refactor mode reads an existing
`.pptx` back into a spec** so the deck can be re-argued as text and re-rendered
as a master-governed file.

Use it when the user hands over a deck: inherited, generated, assembled by
several people, or written in a hurry. `extract_deck.py` is the entry point.

## Contents

- [Why extract instead of patching](#why-extract-instead-of-patching)
- [The chain](#the-chain)
- [What extraction recovers](#what-extraction-recovers)
- [What it cannot carry over](#what-it-cannot-carry-over)
- [Exit codes and the report](#exit-codes-and-the-report)
- [Editing the extracted spec](#editing-the-extracted-spec)
- [Refilling the original template](#refilling-the-original-template)
- [When NOT to rebuild](#when-not-to-rebuild)

## Why extract instead of patching

Patching a broken deck with python-pptx keeps everything that was wrong with it:
text still sits in free textboxes, the master still governs nothing, the band
still drifts. Extraction keeps only what carries meaning — words, numbers,
figures, notes — and the rebuild puts them back into real layout placeholders.

It also moves the argument into a text file, which is the only place an argument
is cheap to change. Reordering, splitting and merging slides is a diff in YAML
and a drag-and-drop marathon in PowerPoint.

## The chain

```bash
cd assets

# 1. Recover the content. Images land next to the spec, in deck_media/.
python3 extract_deck.py old.pptx -o deck.yaml
#    exit 0 = nothing lost · 1 = read the LOSS lines · 2 = not a .pptx
#    --slides 3-9,12   only part of the deck
#    --media-dir figs  where extracted images go
#    --no-notes        drop speaker notes instead of carrying them

# 2. Fix the ARGUMENT in deck.yaml (this is the actual work — see below).

# 3. Lint the spec and read the narrative spine.
python3 validate_deck.py deck.yaml

# 4. Rebuild — default clean look, or back into the original template.
python3 build_deck.py deck.yaml -o refactored.pptx
python3 build_deck.py deck.yaml -o refactored.pptx --template corp.pptx

# 5. Audit the artifact, then look at it.
python3 audit_pptx.py refactored.pptx
./render_preview.sh refactored.pptx
```

Relative `image:` paths in the spec resolve **against the spec file**, so a spec
and its `deck_media/` directory can be moved together and built from anywhere.

## What extraction recovers

| From the old deck | Into the spec |
|---|---|
| Title placeholder, or the topmost largest line | `title:` |
| Body text, with indent levels | `bullets:` (`level:` preserved) |
| Two body blocks side by side | `two_col:` with `left`/`right`; a **bold first line** becomes `heading:` |
| A table | `columns:` + `rows:` (header row when the table declares one) |
| A chart | `chart:` kind, `categories:`, `series:` with values |
| An embedded picture larger than ~6% of the slide | `image:` + the file, written into the media directory |
| A short large number alone in the body | `big_number:` with its `caption:` |
| Text opening with a quotation mark | `quote:` + `attribution:` |
| A footer line starting with 出典 / Source / ※ | `source:` |
| Speaker notes | `notes:` |
| Slide size | `meta.aspect` |
| The template's accent1, when it is not a stock Office color | `meta.accent` |

Hand-typed bullet glyphs (`・`, `●`, `- `) are stripped — PowerPoint's own
bullets live in the paragraph properties, so a glyph in the text is someone
typing one by hand.

Classification is deliberately conservative: an ambiguous slide falls through to
`bullets`, which loses no text. Re-read the extracted types before rebuilding —
the extractor's job is to lose nothing, not to guess cleverly.

## What it cannot carry over

These are reported per slide, not silently dropped:

| Not carried | Why, and what to do |
|---|---|
| **SmartArt** | It is a diagram format, not content. Its text is kept as bullets. If it encoded a real structure, redraw it (`document-figures`) and place it as `type: image`; if it did not, it was decorated bullets and the bullets are now honest |
| **Grouped drawings** | The text survives, the arrangement does not. Same decision as SmartArt |
| **Decorative shapes** (bands, boxes, connectors) | Dropped by design — that is the point of the refactor. Reported so you can check none of them carried meaning |
| **Icons and logos** (images under ~6% of the slide) | Dropped; the master carries the logo |
| **Animations, transitions, embedded media** | Not represented in the spec |
| **Per-shape colors, fonts, positions** | Replaced by the theme or the template. This is intended: the look is supposed to come from the master |
| **Second table/chart/figure on one slide** | Only the first goes into the spec. A slide carries one message — split it |

## Exit codes and the report

`extract_deck.py` writes the spec to `-o` and the report to stderr, so
`-o -` pipes a clean spec to stdout.

| Exit | Meaning |
|---|---|
| `0` | Everything mapped; no loss reported |
| `1` | Extracted, but something could not be represented — the `LOSS` lines say what and on which slide |
| `2` | The file could not be read as a `.pptx` |

Severities: `LOSS` needs a decision from you (redraw, split, or accept the drop).
`WARN` means it came through changed (a 3-D chart flattened, an exploded pie
closed, text recovered from inside a group). `INFO` records what was dropped as
furniture — footers, page numbers, decoration.

## Editing the extracted spec

The extracted spec is content, not a finished deck. Before rebuilding:

1. **Rewrite topic titles into action titles.** Extraction cannot invent a
   takeaway; `validate_deck.py` flags the ones that look like labels.
2. **Split slides carrying two messages**, and delete ones carrying none.
3. **Check every `bullets:` slide that should have been something else** — a
   list of four parallel items with a bold lead line is a `two_col`; a slide
   whose message is one figure is a `big_number`.
4. **Put the sources back.** A number that lost its footnote needs `source:`.
5. **Read the spine** that `validate_deck.py` prints, end to end, against
   `narrative-and-logic.md`.

Judgment about *what* to fix, and in what order, belongs to **pptx-design**'s
`references/refactor-playbook.md`. Do not silently change a claim while cleaning
up — report it instead.

## Refilling the original template

When the deck must stay in the organization's template, extract and rebuild with
`--template` pointed at the original file:

```bash
python3 inspect_template.py old.pptx            # its layouts and placeholders
python3 build_deck.py deck.yaml -o refactored.pptx --template old.pptx
```

The old file works as its own template: the master, theme, fonts and logos come
through, while the content is rewritten into real placeholders. See
`template-mode.md`.

## When NOT to rebuild

- Only a few slides need edits and the deck is already master-governed — patch
  it in PowerPoint. `audit_pptx.py old.pptx` answers this in one command: no
  errors means the master is intact and a rebuild would throw away working work.
- The file is in a review cycle with tracked comments — rebuilding loses them.
- The deck is mostly custom diagrams — extraction gives you their text and
  nothing else, so the rebuild is mostly redrawing.
