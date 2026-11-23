#!/usr/bin/env python3
"""Checks the figure-pattern catalog and the 2.16 figure kinds.

  1. catalog    every entry has the fields find_pattern.py and the README rely on,
                ids are unique, sources name a reference, the image exists, and its
                spec passes validate_deck.py with no ERROR
  2. gallery    assets/samples/figure-patterns.yaml is what --gallery writes now
                (the catalog and the sample deck cannot drift apart)
  3. shapes     fixtures/patterns-deck.yaml draws what each new kind promises,
                looking at the shapes themselves:
                pyramid apex on top and levels widening; funnel stages narrowing;
                venn = translucent ovals; tree right = leaves in one column, tree
                down = root above, tree left = root at the right with arrows into
                it; hub = one line per spoke; swimlane = one band per lane, each step
                inside its lane, every connector square; before_after = one arrow
                shape, or one connector per row with `pairs`

usage: patterns_check.py         exit 0 = all hold, 1 = a check failed, 2 = cannot run
"""
import os
import subprocess
import sys
import tempfile

try:
    import yaml
    from lxml import etree
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
except ImportError:
    print("SKIP python-pptx / PyYAML missing")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
A = os.path.join(SKILL, "assets")
CAT = os.path.join(SKILL, "references", "figure-patterns", "patterns.yaml")
sys.path.insert(0, A)
import build_deck as B          # noqa: E402
import validate_deck as V       # noqa: E402

FAILS = []
FIELDS = ("id", "name", "logic", "logic_ja", "kind", "build", "use_when", "avoid_when",
          "mistakes", "design", "keywords", "sources", "image", "spec")


def check(ok, msg):
    if not ok:
        FAILS.append(msg)


def parts(slide, name):
    return [sh for sh in slide.shapes if sh.name == name]


def taper(sp):
    """(top edge width, bottom edge width) of a freeform, from its path points."""
    pts = [(int(q.get("x")), int(q.get("y"))) for q in sp._element.xpath(".//a:pathLst//a:pt")]
    lo, hi = min(y for _, y in pts), max(y for _, y in pts)
    span = lambda yy: (max(x for x, y in pts if y == yy) - min(x for x, y in pts if y == yy))
    return span(lo), span(hi)


def catalog():
    data = yaml.safe_load(open(CAT, encoding="utf-8"))
    refs = data.get("references") or {}
    pats = data.get("patterns") or []
    check(len(pats) >= 20, "catalog: only %d patterns" % len(pats))
    ids = [p.get("id") for p in pats]
    check(len(ids) == len(set(ids)), "catalog: duplicate ids")
    theme = B._apply_size_defaults(B.apply_meta(B.load_theme(B.DEFAULT_THEME), {}), {})
    g = B.make_grid(theme)
    for p in pats:
        pid = p.get("id", "?")
        for f in FIELDS:
            check(p.get(f) not in (None, "", [], {}), "catalog %s: missing `%s`" % (pid, f))
        kw = p.get("keywords") or {}
        check(len(kw.get("ja") or []) >= 3 and len(kw.get("en") or []) >= 3,
              "catalog %s: needs 3+ keywords in ja and en" % pid)
        for s in p.get("sources") or []:
            check(s in refs, "catalog %s: source %r is not in references" % (pid, s))
        check(p.get("build") in ("native", "composed"), "catalog %s: build must be native/composed" % pid)
        img = os.path.join(os.path.dirname(CAT), p.get("image", ""))
        check(os.path.isfile(img), "catalog %s: image missing: %s" % (pid, p.get("image")))
        readme = open(os.path.join(os.path.dirname(CAT), "README.md"), encoding="utf-8").read()
        check("`%s`" % pid in readme, "catalog %s: not listed in figure-patterns/README.md" % pid)
        spec = {"meta": {}, "slides": [p.get("spec") or {}]}
        errs = [f["message"] for f in V.validate(spec, theme, g) if f["severity"] == "ERROR"]
        check(not errs, "catalog %s: spec has errors: %s" % (pid, errs))


def gallery(tmp):
    out = os.path.join(tmp, "g.yaml")
    r = subprocess.run([sys.executable, os.path.join(A, "find_pattern.py"), "--gallery", out],
                       capture_output=True, text=True)
    check(r.returncode == 0, "gallery: --gallery failed: %s" % r.stderr)
    shipped = os.path.join(A, "samples", "figure-patterns.yaml")
    check(os.path.exists(out) and open(out, encoding="utf-8").read()
          == open(shipped, encoding="utf-8").read(),
          "gallery: assets/samples/figure-patterns.yaml is stale — run find_pattern.py --gallery")


def shapes(tmp):
    out = os.path.join(tmp, "p.pptx")
    r = subprocess.run([sys.executable, os.path.join(A, "build_deck.py"),
                        os.path.join(HERE, "fixtures", "patterns-deck.yaml"), "-o", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit(2)
    s = Presentation(out).slides

    # pyramid: three freeform levels, the first (apex) on top, each wider than the last
    lv = [sh for sh in parts(s[0], "part/node") if sh.shape_type == MSO_SHAPE_TYPE.FREEFORM]
    check(len(lv) == 3, "pyramid: expected 3 freeform levels, got %d" % len(lv))
    if len(lv) == 3:
        check(lv[0].top < lv[1].top < lv[2].top and lv[0].width < lv[1].width < lv[2].width,
              "pyramid: levels are not apex-first and widening")
        check(all(taper(v)[0] < taper(v)[1] for v in lv) and taper(lv[0])[0] == 0,
              "pyramid: a level is wider at its top than its bottom, or the apex is not a point")
        check(len([c for c in parts(s[0], "part/connector")]) == 3, "pyramid: expected 3 leader lines")
    # funnel: stages narrowing downward
    st = [sh for sh in parts(s[1], "part/node") if sh.shape_type == MSO_SHAPE_TYPE.FREEFORM]
    check(len(st) == 3 and st[0].width > st[1].width > st[2].width and st[0].top < st[2].top,
          "funnel: stages do not narrow downward")
    check(all(taper(v)[0] > taper(v)[1] for v in st), "funnel: a stage widens downward")
    # venn: three ovals with alpha in their fill
    ov = [sh for sh in parts(s[2], "part/node") if getattr(sh, "auto_shape_type", None) == MSO_SHAPE.OVAL]
    check(len(ov) == 3, "venn: expected 3 ovals, got %d" % len(ov))
    check(all(b"alpha" in etree.tostring(o._element)
              for o in ov), "venn: circles are not translucent")
    # tree right: leaves share one left edge, to the right of the root
    nodes = parts(s[3], "part/node")
    root = [n for n in nodes if n.text_frame.text == "Late deliveries"][0]
    leaves = [n for n in nodes if n.text_frame.text.split("\n")[0] in
              ("Seasonal peaks missed", "Ward data a week old", "Approval waits for a signature",
               "Carrier slots booked late", "Wrong dock")]
    check(len(leaves) == 5 and len({n.left for n in leaves}) == 1 and leaves[0].left > root.left,
          "tree right: leaves are not one aligned column to the right of the root")
    check(not any(c._element.xpath(".//a:tailEnd") for c in parts(s[3], "part/connector")),
          "tree right: default arrows should be none")
    # tree down: root above the leaves
    nd = parts(s[4], "part/node")
    r0 = [n for n in nd if n.text_frame.text == "Hospital board"][0]
    lf = [n for n in nd if n.text_frame.text in ("Wards", "Pharmacy", "Supply office", "Estates")]
    check(len(lf) == 4 and all(n.top > r0.top for n in lf) and len({n.top for n in lf}) == 1,
          "tree down: leaves are not one row below the root")
    # tree left: root at the right; arrows point into it
    nl = parts(s[5], "part/node")
    r1 = [n for n in nl if n.text_frame.text == "Stock-out"][0]
    check(all(n.left < r1.left for n in nl if n is not r1), "tree left: the root is not at the right")
    check(any(c._element.xpath(".//a:tailEnd") for c in parts(s[5], "part/connector")),
          "tree left: no arrowhead into the effect")
    # hub: one line per spoke
    check(len(parts(s[6], "part/connector")) == 5, "hub: expected 5 spokes, got %d"
          % len(parts(s[6], "part/connector")))
    # swimlane: three lane bands; Ship inside the Supplier lane; all connectors square
    bands = parts(s[7], "part/group")
    check(len(bands) == 3, "swimlane: expected 3 lanes, got %d" % len(bands))
    ship = [n for n in parts(s[7], "part/node") if n.text_frame.text == "Ship"][0]
    if len(bands) == 3:
        lane = sorted(bands, key=lambda b: b.top)[2]
        check(lane.top <= ship.top and ship.top + ship.height <= lane.top + lane.height,
              "swimlane: a step is drawn outside its lane")
    check(all(c.width == 0 or c.height == 0 for c in parts(s[7], "part/connector")),
          "swimlane: a connector runs diagonally")
    # before_after: one arrow shape; with pairs, one connector per row
    check(len(parts(s[8], "part/arrow")) == 1, "before_after: expected one arrow shape")
    check(len(parts(s[9], "part/connector")) - 2 == 2,
          "before_after pairs: expected one arrow per row (2) besides the 2 heading rules")


def main():
    tmp = tempfile.mkdtemp()
    catalog()
    gallery(tmp)
    shapes(tmp)
    for m in FAILS:
        print("NG  " + m)
    print("patterns_check: %d failed" % len(FAILS) if FAILS else "patterns_check: all hold")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
