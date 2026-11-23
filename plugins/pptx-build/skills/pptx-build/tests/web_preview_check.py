#!/usr/bin/env python3
"""Check the page preview_web.py writes, without LibreOffice.

Copies the tiny fixture JPEG once per slide into a temp folder (what preview_web.sh
would render), runs preview_web.py with the given label source, and checks the page:
one <figure> per slide with p.N and its title, section chips that match the source,
the page-number jump form with max=N, the #pN hash handler, the PC keys, light/dark tokens, and no
external requests. With --images K it puts K images instead of N, to prove a mismatch
fails with a clear message.

usage: web_preview_check.py (--spec FILE | --pptx FILE) [--images K] [--expect-sections a,b]
exit:  0 page is right / 1 page is wrong or the generator refused (message printed) /
       2 cannot run
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..", "assets", "preview_web.py")
JPEG = os.path.join(HERE, "fixtures", "web-slide.jpg")


def count_slides(a):
    if a.spec:
        import yaml
        return [s for s in yaml.safe_load(open(a.spec, encoding="utf-8"))["slides"]
                if not (isinstance(s, dict) and s.get("hidden"))]
    from pptx import Presentation
    return [s for s in Presentation(a.pptx).slides if s.element.get("show") != "0"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--pptx")
    ap.add_argument("--images", type=int)
    ap.add_argument("--expect-sections", default=None,
                    help="comma-separated chip labels after the cover chip")
    a = ap.parse_args()
    if not (a.spec or a.pptx) or not os.path.isfile(JPEG):
        print("usage: web_preview_check.py (--spec FILE | --pptx FILE)", file=sys.stderr)
        return 2
    try:
        n = len(count_slides(a))
    except Exception as e:
        print(f"cannot read the label source: {e}", file=sys.stderr)
        return 2
    k = n if a.images is None else a.images

    out = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(out, "img"))
        for i in range(1, k + 1):
            shutil.copy(JPEG, os.path.join(out, "img", f"s-{i:03d}.jpg"))
        src = ["--spec", a.spec] if a.spec else ["--pptx", a.pptx]
        r = subprocess.run([sys.executable, GEN, out, *src, "--rev", "test"],
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        sys.stdout.write(r.stderr)
        if r.returncode != 0:
            print(f"generator exit {r.returncode}")
            return 1
        page = open(os.path.join(out, "index.html"), encoding="utf-8").read()
    finally:
        shutil.rmtree(out, ignore_errors=True)

    bad = []
    figs = re.findall(r'<figure id="s(\d+)"', page)
    if figs != [str(i) for i in range(1, n + 1)]:
        bad.append(f"expected figures s1..s{n}, got {len(figs)}")
    for i in (1, n):
        if f'<span class="n">p.{i}</span>' not in page:
            bad.append(f"caption p.{i} missing")
    if not re.search(r'<form id="go"[^>]*>.*?<input id="pn" type="number"[^>]*max="%d"' % n, page, re.S):
        bad.append("page-number jump form (#go / #pn max=N) missing")
    if "location.hash.match(/^#(?:p|s)(\\d+)$/)" not in page or "'hashchange'" not in page:
        bad.append("#pN hash handler missing")
    if "document.addEventListener('keydown'" not in page or "e.key==='j'" not in page or "t.tagName==='INPUT'" not in page:
        bad.append("PC keys (j/k/g, ignored while typing) missing")
    if "prefers-color-scheme: dark" not in page or ':root[data-theme="dark"]' not in page:
        bad.append("dark-mode tokens missing")
    if "safe-area-inset-top" not in page:
        bad.append("safe-area insets missing")
    if re.search(r'(?:src|href)="(?:https?:)?//', page) or "@import" in page:
        bad.append("page refers to an external resource")
    chips = re.findall(r'<nav>(.*?)</nav>', page, re.S)
    labels = re.findall(r'<a href="#s\d+">(.*?)</a>', chips[0]) if chips else []
    if a.expect_sections is not None:
        want = [x for x in a.expect_sections.split(",") if x]
        if labels[1:] != want:
            bad.append(f"section chips {labels[1:]} != expected {want}")
    for b in bad:
        print("NG", b)
    if not bad:
        print(f"OK {n} figures, chips {labels}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
