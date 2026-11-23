#!/usr/bin/env python3
"""Checks that the 2.15 figure vocabulary draws what it promises, and that a
diagram which uses none of it still draws the way it did before.

Builds fixtures/vocab-deck.yaml and fixtures/figure-deck.yaml, then looks at the
shapes themselves (not a picture of them):

  1. cycle      every step is an ellipse and there is one arrow per step (closed loop)
  2. matrix     the legend lists each labelled mark; cells of one mark share one fill
  3. bands      each band has its label cell at the left edge of the figure
  4. stack      both parts are drawn, the second below the first
  5. diagram    `align: left` left-aligns a label-only box; `route` draws more than one
                segment per edge
  6. default    in figure-deck.yaml (no new options) a label-only box is still centered

usage: vocab_check.py            exit 0 = all hold, 1 = a check failed, 2 = cannot build
"""
import os
import subprocess
import sys
import tempfile

try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
except ImportError:
    print("SKIP python-pptx missing")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "..", "assets", "build_deck.py")
FAILS = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)


def build(spec, out):
    r = subprocess.run([sys.executable, BUILD, spec, "-o", out], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit(2)


def parts(slide, name):
    return [sh for sh in slide.shapes if sh.name == name]


def auto(sh):
    try:
        return sh.auto_shape_type
    except Exception:
        return None


def main():
    tmp = tempfile.mkdtemp()
    v = os.path.join(tmp, "v.pptx")
    f = os.path.join(tmp, "f.pptx")
    build(os.path.join(HERE, "fixtures", "vocab-deck.yaml"), v)
    build(os.path.join(HERE, "fixtures", "figure-deck.yaml"), f)
    s = Presentation(v).slides

    # 1. cycle: 4 ellipse steps, 4 arrows
    nodes = [n for n in parts(s[0], "part/node") if n.text_frame.text.strip() != "Weekly loop"]
    check(len(nodes) == 4 and all(auto(n) == MSO_SHAPE.OVAL for n in nodes),
          "cycle: expected 4 ellipse steps, got %s" % [auto(n) for n in nodes])
    check(len(parts(s[0], "part/connector")) == 4, "cycle: expected 4 arrows (a closed loop), got %d"
          % len(parts(s[0], "part/connector")))

    # 2. matrix: legend lists the three labelled marks; 'Required' cells share a fill
    legend = [t.text_frame.text for t in parts(s[1], "part/legend-text")]
    check(legend == ["Required by rule", "Voluntary or guidance", "Not covered"],
          "matrix legend: %r" % legend)
    req = [c for c in parts(s[1], "part/cell") if c.text_frame.text.startswith("Required")]
    fills = {str(c.fill.fore_color.rgb) if c.fill.type == 1 else "none" for c in req}
    check(len(req) == 4 and len(fills) == 1, "matrix: 'Required' cells %d, fills %s" % (len(req), fills))

    # 3. bands: three label cells at the same left edge, top to bottom
    labels = [n for n in parts(s[3], "part/node") if n.text_frame.text in ("Law", "Standard", "Voluntary")]
    check(len(labels) == 3 and len({n.left for n in labels}) == 1
          and [n.top for n in labels] == sorted(n.top for n in labels),
          "bands: label cells not stacked at one left edge")

    # 4. stack: the cycle steps sit above the band label cells
    steps = [n for n in parts(s[4], "part/node") if n.text_frame.text in ("Sense", "Decide", "Agree", "Act")]
    bands = [n for n in parts(s[4], "part/node") if n.text_frame.text in ("Shared words", "Trust")]
    check(len(steps) == 4 and len(bands) == 2 and max(n.top + n.height for n in steps) < min(n.top for n in bands),
          "stack: parts missing or overlapping")

    # 5. diagram: align left on a label-only box; routed edges are several segments
    hub = [n for n in parts(s[5], "part/node") if n.text_frame.text == "Hub"][0]
    check(hub.text_frame.paragraphs[0].alignment == PP_ALIGN.LEFT, "diagram align: left not applied")
    check(len(parts(s[5], "part/connector")) == 2 + 1 + 3 + 1,
          "diagram route: expected 7 segments (hv 2, straight 1, elbow 3, straight 1), got %d"
          % len(parts(s[5], "part/connector")))

    # 6. default unchanged: a label-only diagram box is centered
    d = Presentation(f).slides[0]
    sup = [n for n in parts(d, "part/node") if n.text_frame.text == "Supplier"][0]
    check(sup.text_frame.paragraphs[0].alignment == PP_ALIGN.CENTER,
          "default diagram: a label-only box is no longer centered")

    for m in FAILS:
        print("NG  " + m)
    print("vocab_check: %d failed" % len(FAILS) if FAILS else "vocab_check: all hold")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
