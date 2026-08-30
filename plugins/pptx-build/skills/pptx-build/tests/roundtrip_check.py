#!/usr/bin/env python3
"""roundtrip_check.py — does extract_deck.py get the CONTENT back?

    python3 roundtrip_check.py SPEC.yaml DECK.pptx

Renders nothing. It extracts DECK.pptx into a spec and compares it, slide by
slide, with the spec the deck was built from: type, title, and every string that
carries meaning (bullets, column headings, numbers, captions, quotes, table
cells, chart categories/series, source, speaker notes).

Formatting is ignored on purpose — the question is whether a refactor loses
words, not whether YAML round-trips byte for byte.

Exit 0 identical · 1 differences (printed) · 2 usage/read error.
"""
import os
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT = os.path.abspath(os.path.join(HERE, "..", "assets", "extract_deck.py"))


def _texts(items):
    out = []
    for it in items or []:
        out.append(it["text"] if isinstance(it, dict) else str(it))
    return out


def _canon(slide):
    """(type, title, [every meaningful string]) for one slide."""
    s = slide
    t = s.get("type", "bullets")
    body = []
    body += _texts(s.get("bullets"))
    # Roles are tagged, not flattened: a column heading that comes back as a
    # plain bullet keeps every word and still loses the structure, and an
    # untagged comparison would call that a clean round-trip.
    for key in ("left", "right"):
        col = s.get(key) or {}
        if col.get("heading"):
            body.append("%s.heading=%s" % (key, col["heading"]))
        body += _texts(col.get("bullets"))
    for key in ("subtitle", "number", "caption", "note", "quote", "attribution",
                "source", "notes", "text", "sub", "heading"):
        # `image` is deliberately excluded: extraction rewrites the figure into
        # its own media directory, so the path cannot match by construction.
        if s.get(key):
            body.append("%s=%s" % (key, s[key]))
    # composed archetypes: every item's role and position is part of the content
    if s.get("invert"):
        body.append("invert=1")
    lead = s.get("lead")
    if isinstance(lead, dict):
        body.append("lead.label=%s" % lead.get("label", ""))
        if lead.get("text"):
            body.append("lead.text=%s" % lead["text"])
    for key in ("cards", "steps", "quadrants", "rest"):
        for n, it in enumerate(s.get(key) or [], start=1):
            label = it if isinstance(it, str) else it.get("label", "")
            text = "" if isinstance(it, str) else it.get("text", "")
            body.append("%s[%d].label=%s" % (key, n, label))
            if text:
                body.append("%s[%d].text=%s" % (key, n, text))
    for key in ("x_axis", "y_axis"):
        if s.get(key):
            body.append("%s=%s" % (key, "|".join(str(v) for v in s[key])))
    if s.get("columns"):
        body += [str(c) for c in s["columns"]]
    for row in s.get("rows") or []:
        body += [str(c) for c in (row.values() if isinstance(row, dict) else row)]
    body += [str(c) for c in (s.get("categories") or [])]
    series = s.get("series") or []
    if isinstance(series, dict):
        series = [{"name": k, "values": v} for k, v in series.items()]
    for se in series:
        if se.get("name"):
            body.append(str(se["name"]))
        body += [("%g" % v) if isinstance(v, float) else str(v)
                 for v in (se.get("values") or [])]
    return t, (s.get("title") or "").strip(), [x.strip() for x in body if str(x).strip()]


def compare(src_spec, got_spec):
    diffs = []
    a, b = src_spec.get("slides") or [], got_spec.get("slides") or []
    if len(a) != len(b):
        diffs.append("slide count: expected %d, extracted %d" % (len(a), len(b)))
    for i, (x, y) in enumerate(zip(a, b), start=1):
        tx, titx, bx = _canon(x)
        ty, tity, by = _canon(y)
        if tx != ty:
            diffs.append("slide %d: type %r -> %r" % (i, tx, ty))
        if titx != tity:
            diffs.append("slide %d: title %r -> %r" % (i, titx, tity))
        missing = [s for s in bx if s not in by]
        added = [s for s in by if s not in bx]
        for s in missing:
            diffs.append("slide %d: LOST  %r" % (i, s[:60]))
        for s in added:
            diffs.append("slide %d: EXTRA %r" % (i, s[:60]))
    return diffs


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    spec_path, pptx_path = argv
    if not (os.path.exists(spec_path) and os.path.exists(pptx_path)):
        sys.stderr.write("missing input\n")
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "extracted.yaml")
        r = subprocess.run([sys.executable, EXTRACT, pptx_path, "-o", out],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 2 or not os.path.exists(out):
            sys.stderr.write("extraction failed\n")
            return 2
        with open(out, encoding="utf-8") as f:
            got = yaml.safe_load(f)
    with open(spec_path, encoding="utf-8") as f:
        src = yaml.safe_load(f)

    diffs = compare(src, got)
    if diffs:
        print("Round-trip differences (%s -> %s)" % (spec_path, pptx_path))
        for d in diffs:
            print("  " + d)
        return 1
    print("Round-trip clean: every slide's type, title and text came back.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
