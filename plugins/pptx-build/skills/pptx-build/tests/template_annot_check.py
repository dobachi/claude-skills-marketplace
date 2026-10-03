#!/usr/bin/env python3
"""テンプレート流し込みで、出典・章の名前・章番号・図がプレースホルダに入るかを確かめる。

その場で小さなテンプレートを作り（標準のレイアウトに、名前つきのプレースホルダを足す）、
build_deck.py --template で流し込み、できた .pptx を調べる。

    python3 template_annot_check.py            期待 0: すべてプレースホルダに入る
    python3 template_annot_check.py --no-source 期待 1: 出典の置き場がないテンプレートでは、
                                                出典が書かれず、警告が出る（黙って落とさない）
"""
import copy, os, subprocess, sys, tempfile
from pptx import Presentation
from pptx.util import Inches
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "..", "assets", "build_deck.py")


def add_named_ph(layout, name, idx, top):
    """本文プレースホルダを複製して、名前つきの注記プレースホルダにする。"""
    body = [p for p in layout.placeholders if p.placeholder_format.idx == 1][0]
    el = copy.deepcopy(body._element)
    ids = [int(e.get("id")) for e in layout.shapes._spTree.iter(qn("p:cNvPr")) if e.get("id")]
    el.nvSpPr.cNvPr.set("id", str(max(ids) + 1))
    el.nvSpPr.cNvPr.set("name", name)
    ph = el.nvSpPr.nvPr.find(qn("p:ph"))
    ph.set("type", "body"); ph.set("idx", str(idx))
    layout.shapes._spTree.insert_element_before(el, "p:extLst")
    new = [p for p in layout.placeholders if p.placeholder_format.idx == idx][0]
    new.left, new.top, new.width, new.height = Inches(0.5), Inches(top), Inches(6), Inches(0.3)


def make_template(path, with_source):
    prs = Presentation()
    content = prs.slide_layouts[1]                 # Title and Content
    add_named_ph(content, "Eyebrow (section label)", 20, 0.1)
    if with_source:
        add_named_ph(content, "Source", 21, 7.0)
    add_named_ph(prs.slide_layouts[2], "Section number", 22, 0.5)   # Section Header
    prs.save(path)


SPEC = """
slides:
  - {type: section, number: "01", title: "章"}
  - {type: bullets, title: "箇条書き", bullets: ["一", "二"], source: "出典A"}
  - {type: table, title: "表", columns: ["a", "b"], rows: [["1", "2"]], widths: [1, 3], source: "出典B"}
  - {type: bullets, title: "出典なし", bullets: ["三"]}
"""


def main():
    with_source = "--no-source" not in sys.argv
    tmp = tempfile.mkdtemp()
    tpl, spec, out = (os.path.join(tmp, n) for n in ("t.pptx", "d.yaml", "o.pptx"))
    make_template(tpl, with_source)
    open(spec, "w", encoding="utf-8").write(SPEC)
    r = subprocess.run([sys.executable, BUILD, spec, "-o", out, "--template", tpl],
                       capture_output=True, text=True)
    log = r.stdout + r.stderr
    prs = Presentation(out)
    slides = list(prs.slides)
    problems = []

    def texts(slide, placeholders_only):
        return [sh.text_frame.text for sh in slide.shapes
                if sh.has_text_frame and (sh.is_placeholder or not placeholders_only)]

    def expect(cond, msg):
        if not cond:
            problems.append(msg)

    for n, slide in enumerate(slides, 1):
        free = [sh for sh in slide.shapes if sh.has_text_frame and not sh.is_placeholder
                and sh.text_frame.text.strip()]
        expect(not free, "slide %d: 置き去りのテキストボックスがある" % n)
    expect("01" in texts(slides[0], True), "章番号がプレースホルダに入っていない")
    expect("01  章" in texts(slides[1], True), "章の名前がプレースホルダに入っていない")
    if with_source:
        expect("出典A" in texts(slides[1], True), "箇条書きの出典がプレースホルダに入っていない")
        expect("出典B" in texts(slides[2], True), "表の出典がプレースホルダに入っていない")
        empty = [sh for sh in slides[3].placeholders if sh.has_text_frame and not sh.text_frame.text.strip()]
        expect(not empty, "出典のないスライドに、空のプレースホルダが残っている")
        expect("warning" not in log, "警告が出た: " + log)
    else:
        expect("出典A" not in " ".join(texts(slides[1], False)), "置き場がないのに出典が書かれた")
        expect("has no source placeholder" in log, "出典を書けなかったのに警告がない")
        problems.append("出典の置き場がないテンプレート（期待どおり 1 を返す）") if not problems else None
    tbl = [sh for sh in slides[2].shapes if getattr(sh, "has_table", False) and sh.has_table]
    expect(tbl and tbl[0].table.columns[1].width > 2 * tbl[0].table.columns[0].width, "表の widths が効いていない")
    for p in problems:
        print("FINDING", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
