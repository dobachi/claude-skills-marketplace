# Browser preview: read a deck on a PC or a phone without the .pptx

## Contents

- [What it makes](#what-it-makes)
- [Building it](#building-it)
- [Where the labels come from](#where-the-labels-come-from)
- [Handing it over, way 1: a Claude Artifact](#handing-it-over-way-1-a-claude-artifact)
- [Handing it over, way 2: a local URL](#handing-it-over-way-2-a-local-url)
- [Page numbers are the review's coordinates](#page-numbers-are-the-reviews-coordinates)
- [Failure modes](#failure-modes)

Reading a deck should not require downloading a `.pptx` and opening PowerPoint.
`assets/preview_web.sh` turns the deck into a folder that any browser reads:

- **On a PC**: open the local URL or the Artifact in a tab and page through the whole deck, with
  the keyboard if you like. Nothing to download, no PowerPoint, nothing to keep in sync.
- **On a phone**: a reviewer between meetings scrolls the deck and answers with "p37: the arrow
  points the wrong way".

## What it makes

```
OUT/
  index.html        one page, inline CSS and JS, no external requests
  img/s-001.jpg     one JPEG per slide, in deck order (s-001 … s-NNN, zero-padded by pdftoppm)
```

The page shows one column of slides, each with `p.N` and its title, under a sticky header. On a
PC the column is centred and at most about 1070 px wide (a 16:9 slide is then ~600 px tall, one
slide per screen on a 1440×900 display) and the header lines up with it; on a phone it is full
width with a 16 px gutter.

| Part | What it does |
|---|---|
| Title line | `--title` (default: the title slide's title), then the date or `--subtitle`, the git revision of the spec's folder, the slide count |
| Section chips | Cover, then one chip per section slide; tap to jump |
| Page-number box | Type `37`, press the button, land on p.37 (the URL becomes `#p37`) |
| Current page | `p.37 / 144` — the slide whose caption is at the top of the screen |
| `#pN` links | `index.html#p37` opens on p.37; `#s37` also works |
| Keys (PC) | j or → next slide, k or ← previous, g puts the cursor in the page-number box (Esc leaves it). Ignored while typing in the box or with Ctrl/Cmd/Alt held; the key hint shows on screens 900 px and wider |

Light and dark follow the device's setting; the header respects notches (safe-area insets). The
images carry their real width and height so the page does not jump while they load.

## Building it

```bash
assets/preview_web.sh DECK.pptx [-s deck.yaml] [-o OUT] [-r 110] [-q 78] \
    [--title T] [--subtitle S] [--lang auto|ja|en] [--serve [ADDR:]PORT]
```

- `.pptx` → PDF with LibreOffice (a private profile, so a running LibreOffice does not swallow the
  conversion), → JPEG with `pdftoppm -r 110 -jpeg -jpegopt quality=78`, → `index.html` with
  `preview_web.py`.
- `-r 110` gives about 1467×825 for 16:9: sharp on a phone and on a PC at the capped width,
  ~100–250 KB a slide. Raise it (e.g. `-r 150`) when a PC reader zooms into small print; lower it
  for a very long deck.
- The old `img/s-*.jpg` are replaced, never left behind, and the folder itself is kept: a server
  already serving it keeps working.
- `PYTHON` picks the interpreter that has python-pptx and PyYAML, for example
  `PYTHON="uv run -q --with python-pptx --with pyyaml python"`.
- If the JPEGs already exist (rendered some other way), run the generator alone:
  `preview_web.py OUT --spec deck.yaml` (or `--pptx DECK.pptx`).

Exit codes: 0 written; 1 the number of images and the number of slides disagree; 2 a usage error,
a missing tool or input, a failed conversion, or a port taken by something else.

## Where the labels come from

- **With a spec** (`-s deck.yaml`): `slides[].title` for each caption, `type: section` for the
  chips, the `type: title` slide for the page title and `date`. Slides marked `hidden: true` are
  skipped, as in the PDF.
- **Without a spec**: the deck itself, through python-pptx. The caption is the title placeholder
  (or the first text on the slide), a section is a slide whose layout name says section / セクション
  / 中扉 / 章扉, and hidden slides are skipped. Any `.pptx` works, including one this skill did not
  build.

Nothing about a particular deck is in the generator; a deck-specific title goes in `--title`.

## Handing it over, way 1: a Claude Artifact

Publish the page with the Artifact tool:

- `file_path`: `OUT/index.html`
- `root`: `OUT`
- `files`: the images as `img/s-NNN.jpg` → `img/s-NNN.jpg` (paths relative to `root`)

The first publish sends every image. A later publish sends only images that changed; images left
out are kept. Which ones changed depends on the kind of edit:

| Edit | Images to publish |
|---|---|
| Text or figure fixed on existing slides | Only those slides' images |
| A slide inserted or deleted at p.K | **Every image from p.K to the end**, and the page (the count and the captions moved) |
| Slides removed from the end | The page, and `null` for the image paths that no longer exist |

After an insertion, p.40 in the new deck is what p.39 was. Publishing only the new slide leaves
the old images under the new numbers, and the page then shows one slide with another slide's
caption.

## Handing it over, way 2: a local URL

Where Claude Artifacts are not reachable, serve the same folder over HTTP:

```bash
assets/preview_web.sh DECK.pptx -s deck.yaml -o OUT --serve 8765       # build, then serve
assets/preview_web.sh --serve-only 8765 -o OUT                         # serve without building
```

It starts `python3 -m http.server --bind ADDR PORT --directory OUT` in the background (it outlives
the command), waits until the page answers, and prints the root URL, the `#pN` form, and how to
stop it. When something already listens on the port and serves this same page, it reuses it and
does not start a second server; when the port is taken by something else, it stops with exit 2.

- **Address.** The default is `127.0.0.1`: this machine only, which is enough when the reader
  is at this PC. For another PC or a phone, bind an address that device can reach: the
  VPN/overlay address (`--serve "$(tailscale ip -4):8765"`), else a LAN address. Do not bind `0.0.0.0` by default: the deck may be unpublished work and every network
  the machine is on would see it.
- **Prove it.** Fetch it before handing it over:
  `curl -s -o /dev/null -w '%{http_code}\n' http://ADDR:8765/index.html` and one image, both 200.
- **Rebuilds.** Re-running the build into the same `OUT` updates what the running server returns;
  no restart.
- **Stop.** Find the PID from the listening socket and kill that PID:
  `ss -ltnp | grep ':8765 '` → `pid=NNNN` → `kill NNNN`. Never `pkill -f http.server` or a pattern
  that also appears in your own command line: the shell running it matches and kills itself.

These are the same rules as the `preview-access` skill (reuse before starting, one address per
project, never hand over a link you did not fetch).

## Page numbers are the review's coordinates

Reviewers, on a PC or a phone, comment as "p37 …". The page-number box, the `#p37` links and the
current-page indicator exist so that a number in a comment is one tap away, both for the reviewer
and for whoever applies the comment. Two consequences:

- Rebuild and republish before the next round of comments whenever slides were inserted or
  removed, or the numbers in new comments refer to a deck the reviewer is not looking at.
- When handing over, link straight to what changed: `…/index.html#p37`.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Exit 1, "N image(s) … but M slide(s)" | The `.pptx` was built from another version of the spec, or hidden slides differ | Rebuild the `.pptx` from this spec, or drop `-s` and read labels from the deck |
| Exit 2, "LibreOffice did not produce a PDF" | The `.pptx` is broken or LibreOffice crashed | Open it in LibreOffice by hand; the log is printed |
| Captions right, pictures wrong after an insertion (Artifact) | Only the new image was published | Publish every image from the insertion point on |
| Another PC or a phone cannot open the URL | Bound to `127.0.0.1` | `--serve "$(tailscale ip -4):PORT"` (stop the old one first) |
