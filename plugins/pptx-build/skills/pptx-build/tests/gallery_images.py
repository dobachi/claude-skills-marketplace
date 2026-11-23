#!/usr/bin/env python3
"""Re-render references/figure-patterns/img/ from assets/samples/figure-patterns.yaml.

Builds the sample deck, renders it with LibreOffice (assets/render_preview.sh),
and saves slide k+1 as the image of catalog entry k: 640 x 360, a small palette
so the folder stays a few hundred KB. A maintenance step, not a test: run it
after changing the catalog or a figure kind's look.

usage: gallery_images.py        exit 0 = written, 2 = cannot build or render
"""
import glob
import os
import subprocess
import sys
import tempfile

try:
    import yaml
    from PIL import Image
except ImportError:
    print("gallery_images: needs PyYAML and Pillow", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
A = os.path.join(SKILL, "assets")
CAT = os.path.join(SKILL, "references", "figure-patterns", "patterns.yaml")


def accent_px(im):
    raw = im.convert("RGB").tobytes()
    return sum(1 for k in range(0, len(raw), 3) if raw[k + 2] > 150 and raw[k] < 90)


def main():
    tmp = tempfile.mkdtemp()
    deck = os.path.join(tmp, "g.pptx")
    for cmd in ([sys.executable, os.path.join(A, "build_deck.py"),
                 os.path.join(A, "samples", "figure-patterns.yaml"), "-o", deck],
                ["bash", os.path.join(A, "render_preview.sh"), deck, os.path.join(tmp, "png")]):
        if subprocess.run(cmd, capture_output=True).returncode != 0:
            print("gallery_images: failed: %s" % " ".join(cmd), file=sys.stderr)
            return 2
    pats = yaml.safe_load(open(CAT, encoding="utf-8"))["patterns"]
    pngs = sorted(glob.glob(os.path.join(tmp, "png", "slide-*.png")))[1:]   # slide 1 = title
    if len(pngs) != len(pats):
        print("gallery_images: %d slides for %d patterns" % (len(pngs), len(pats)), file=sys.stderr)
        return 2
    out_dir = os.path.join(os.path.dirname(CAT), "img")
    os.makedirs(out_dir, exist_ok=True)
    for f, p in zip(pngs, pats):
        im = Image.open(f).convert("RGB").resize((640, 360), Image.LANCZOS)
        pal = im.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        if accent_px(im) and accent_px(pal) < accent_px(im) * 0.5:     # keep a small accent
            pal = im.quantize(colors=128, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        pal.save(os.path.join(out_dir, os.path.basename(p["image"])), optimize=True)
    print("gallery_images: wrote %d images to %s" % (len(pats), out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
