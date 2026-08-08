#!/usr/bin/env python3
"""audit_pptx.py — audit a FINISHED .pptx for master/layout hygiene.

`validate_deck.py` lints the spec. This lints the artifact, and catches the one
failure that spec-linting cannot see: a deck whose text was floated onto blank
slides as free textboxes instead of written into the layouts' placeholders —
what you get when a deck is assembled by hand-written python-pptx instead of by
`build_deck.py`, or when template-fill lands on the wrong layout.

    python3 audit_pptx.py deck.pptx
    python3 audit_pptx.py deck.pptx --quiet     # findings only, no per-slide table

Exit code is 1 when any ERROR is found, so it can gate a build.

What it checks
  ERROR  a slide carries body text but NO placeholder holds any of it
  ERROR  a slide is built on a layout that has no placeholders at all, yet has text
  WARN   free textboxes in the content area alongside filled placeholders
  WARN   a placeholder overrides its layout geometry (slide-level <a:xfrm>)
  WARN   an empty placeholder is left on the slide ("Click to add text")
  WARN   slides drawn from more than one slide master
  INFO   per-slide layout / placeholder / free-shape counts
"""
import argparse
import sys

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Emu

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"
_RANK = {ERROR: 0, WARN: 1, INFO: 2}

# Text this low on the page is a footnote (source line, page number) — a free
# textbox there is an annotation, not the slide's content.
FOOTER_BAND = 0.86        # fraction of slide height
DECORATION_CHARS = 6      # a free box this short is a marker, not body content


def _has_ph_marker(shape):
    """True for a table/chart graphicFrame that carries a <p:ph> placeholder marker."""
    el = shape._element
    nv = el.find(qn("p:nvGraphicFramePr"))
    if nv is None:
        return False
    nv_pr = nv.find(qn("p:nvPr"))
    return nv_pr is not None and nv_pr.find(qn("p:ph")) is not None


def _slide_level_geometry(ph):
    """True when the slide's own copy of a placeholder pins its position/size,
    overriding the layout (PowerPoint: the shape no longer follows the master)."""
    sp_pr = ph._element.find(qn("p:spPr"))
    return sp_pr is not None and sp_pr.find(qn("a:xfrm")) is not None


def audit(path):
    prs = Presentation(path)
    findings = []
    rows = []
    masters = set()
    page_h = prs.slide_height or Emu(6858000)

    def add(sev, idx, msg):
        findings.append((sev, idx, msg))

    for i, slide in enumerate(prs.slides, start=1):
        layout = slide.slide_layout
        masters.add(layout.slide_master.name or id(layout.slide_master))
        layout_phs = len(list(layout.placeholders))

        ph_text, ph_empty, ph_pinned, free_body, free_foot, graphics = 0, 0, 0, 0, 0, 0
        for sh in slide.shapes:
            if sh.is_placeholder or _has_ph_marker(sh):
                if not sh.has_text_frame:
                    graphics += 1                     # table/chart in a placeholder
                elif sh.text_frame.text.strip():
                    ph_text += 1
                else:
                    ph_empty += 1
                if sh.is_placeholder and _slide_level_geometry(sh):
                    ph_pinned += 1
                continue
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue                              # hairline, picture, spacer
            text = sh.text_frame.text.strip()
            in_footer = (sh.top or 0) >= page_h * FOOTER_BAND
            if in_footer or len(text) <= DECORATION_CHARS:
                free_foot += 1
            else:
                free_body += 1

        rows.append((i, layout.name, ph_text, graphics, ph_empty, free_body, free_foot))

        if free_body and not (ph_text or graphics):
            add(ERROR, i, "content is in free textboxes, not placeholders (layout %r) — "
                          "build this slide from a layout instead of floating text boxes"
                % layout.name)
        elif free_body:
            add(WARN, i, "%d free textbox(es) in the content area alongside placeholders — "
                         "move that text into the layout's placeholders" % free_body)
        if layout_phs == 0 and (free_body or free_foot):
            add(ERROR, i, "layout %r has no placeholders at all — the deck is not "
                          "master-governed on this slide" % layout.name)
        if ph_pinned:
            add(WARN, i, "%d placeholder(s) pin their own position/size, overriding the "
                         "layout — edits to the layout will not move them" % ph_pinned)
        if ph_empty:
            add(WARN, i, "%d empty placeholder(s) left on the slide — fill or delete them"
                % ph_empty)

    if len(masters) > 1:
        add(WARN, 0, "slides come from %d different slide masters — decks normally use one"
            % len(masters))
    if not rows:
        add(ERROR, 0, "the file has no slides")
    return rows, findings


def report(path, rows, findings, quiet=False):
    if not quiet:
        print("Slide inventory — %s" % path)
        print("  %-4s %-24s %5s %5s %5s %5s %5s" %
              ("#", "layout", "PH✓", "GFX", "PH∅", "FREE", "foot"))
        for i, name, ph_text, gfx, ph_empty, free_body, free_foot in rows:
            print("  %-4d %-24s %5d %5d %5d %5d %5d"
                  % (i, (name or "?")[:24], ph_text, gfx, ph_empty, free_body, free_foot))
        print("  PH✓ text in placeholders · GFX table/chart in a placeholder · "
              "PH∅ empty placeholder\n  FREE free textbox in the content area · "
              "foot footnote-band textbox (source, page number)\n")

    order = sorted(findings, key=lambda f: (_RANK[f[0]], f[1]))
    if order:
        print("Findings")
        for sev, idx, msg in order:
            where = "slide %-3d" % idx if idx else "deck     "
            print("  %-5s %s %s" % (sev, where, msg))
    else:
        print("Findings: none — every slide is built on a layout and writes into its "
              "placeholders.")
    n_err = sum(1 for f in findings if f[0] == ERROR)
    n_warn = sum(1 for f in findings if f[0] == WARN)
    print("\nSummary: %d error, %d warn (%d slides)" % (n_err, n_warn, len(rows)))
    return n_err


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit a .pptx for master/layout hygiene.")
    ap.add_argument("pptx")
    ap.add_argument("--quiet", action="store_true", help="findings only")
    a = ap.parse_args(argv)
    rows, findings = audit(a.pptx)
    sys.exit(1 if report(a.pptx, rows, findings, a.quiet) else 0)


if __name__ == "__main__":
    main()
