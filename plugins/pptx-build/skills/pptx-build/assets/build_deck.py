#!/usr/bin/env python3
"""build_deck.py — Generate a clean, white-based .pptx that does not look AI-made.

Engine: python-pptx. Two rendering paths, ONE spec format:

  1. Default (no --template): build from a blank presentation and place text on a
     single shared grid. White background, dark ink, one restrained accent, and a
     short accent hairline whose coordinates are computed once from the grid — so
     it is identical on every slide of a family and cannot drift. This is the
     "looks human-designed" path.

  2. Template-fill (--template corporate.pptx/.potx): OPEN the real template and
     reuse its slide layouts and PLACEHOLDERS. Each spec slide is mapped to a
     layout, and its title/body/etc. are written into that layout's placeholders,
     so the deck inherits the template's master, theme, fonts, and logos. This is
     the path that actually honors a provided corporate template.

Usage:
  python3 build_deck.py SPEC.yaml -o out.pptx
  python3 build_deck.py SPEC.yaml -o out.pptx --theme themes/brand-example.json
  python3 build_deck.py SPEC.yaml -o out.pptx --template corp.pptx [--map map.json]

Inspect a template first to build/verify a map:  python3 inspect_template.py corp.pptx
"""
import argparse
import json
import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, PP_PLACEHOLDER
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_THEME = os.path.join(HERE, "themes", "minimal-white.json")


# ---------------------------------------------------------------------------
# Spec / theme / map loading
# ---------------------------------------------------------------------------
def load_spec(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if path.lower().endswith((".yaml", ".yml")):
        import yaml
        return yaml.safe_load(raw)
    return json.loads(raw)


def load_theme(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_meta(theme, meta):
    """meta.* in the spec overrides individual theme values for one deck."""
    meta = meta or {}
    for k in ("bg", "ink", "muted", "accent"):
        if meta.get(k):
            theme["color"][k] = str(meta[k]).lstrip("#")
    for k, dst in (("font_heading", "heading"), ("font_body", "body"), ("font_number", "number")):
        if meta.get(k):
            theme["font"][dst] = meta[k]
    if isinstance(meta.get("rule"), bool):
        theme["rule"] = meta["rule"]
    if isinstance(meta.get("page_numbers"), bool):
        theme["pageNumbers"] = meta["page_numbers"]
    if meta.get("aspect") in ("16:9", "4:3"):
        theme["aspect"] = meta["aspect"]
    return theme


# ---------------------------------------------------------------------------
# Grid — single source of truth, in inches.
# ---------------------------------------------------------------------------
def make_grid(theme):
    wide = theme.get("aspect", "16:9") != "4:3"
    over = theme.get("grid") or {}
    g = {
        "pageW": 13.33 if wide else 10.0,
        "pageH": 7.5,
        "marginX": over.get("marginX", 0.92 if wide else 0.75),
        "top": over.get("top", 0.62),
        "titleH": over.get("titleH", 0.95),
        "gap": 0.18,
        "footY": 7.04,
        "ruleLen": 1.05,
        "ruleH": 0.045,
    }
    g["contentW"] = g["pageW"] - 2 * g["marginX"]
    g["bodyTop"] = g["top"] + g["titleH"] + g["gap"]
    g["bodyH"] = g["footY"] - g["bodyTop"] - 0.1
    g["ruleY"] = {
        "content": g["top"] + g["titleH"] - 0.02,
        "title": 2.30,
        "section": 2.78,
        "quote": 2.02,
    }
    return g


# ---------------------------------------------------------------------------
# Low-level text helpers (the EA-font handling is what keeps Japanese on-brand).
# ---------------------------------------------------------------------------
def _set_run_font(run, name=None, size=None, bold=None, color=None):
    f = run.font
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if color is not None:
        f.color.rgb = RGBColor.from_string(color)
    if name:
        f.name = name  # inserts <a:latin> in the correct schema position
        rPr = run._r.get_or_add_rPr()
        latin = rPr.find(qn("a:latin"))
        for tag in ("a:ea", "a:cs"):
            el = rPr.find(qn(tag))
            if el is None:
                el = rPr.makeelement(qn(tag), {})
                latin.addnext(el)  # ea/cs follow latin per the schema
            el.set("typeface", name)


def _bullet_para(p, marker, level, font_name, space_after=9):
    """Give a paragraph a real hanging-indent bullet (no glyph flush, no tofu)."""
    p.level = level
    p.space_after = Pt(space_after)
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(0.30 + 0.22 * level))))
    pPr.set("indent", str(-int(Inches(0.22))))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum", "a:buFont"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": font_name}))
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": marker}))


def _no_bullet(p):
    pPr = p._p.get_or_add_pPr()
    for tag in ("a:buChar", "a:buAutoNum", "a:buFont"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    if pPr.find(qn("a:buNone")) is None:
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))


def add_textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def set_simple(tf, text, theme, font="body", size=18, bold=False, color="ink",
               align=PP_ALIGN.LEFT, line_spacing=None):
    p = tf.paragraphs[0]
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    _no_bullet(p)
    run = p.add_run()
    run.text = text
    _set_run_font(run, name=theme["font"][font], size=size, bold=bold,
                  color=theme["color"][color])
    return p


# ---------------------------------------------------------------------------
# DEFAULT MODE — build from scratch on the shared grid.
# ---------------------------------------------------------------------------
def _normalize_bullets(items):
    out = []
    for it in items or []:
        if isinstance(it, str):
            out.append({"text": it, "level": 0})
        else:
            out.append({"text": it.get("text", ""), "level": it.get("level", 0)})
    return out


def _fill_bullets(tf, theme, items, base=18):
    first = True
    for it in _normalize_bullets(items):
        lvl = it["level"]
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        _bullet_para(p, "–" if lvl == 0 else "•", lvl, theme["font"]["body"])
        run = p.add_run()
        run.text = it["text"]
        _set_run_font(run, name=theme["font"]["body"], size=base - (2 if lvl else 0),
                      color=theme["color"]["ink" if lvl == 0 else "muted"])


def _set_bg(slide, theme):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = RGBColor.from_string(theme["color"]["bg"])


def _hairline(slide, theme, g, y):
    if not theme.get("rule"):
        return
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(g["marginX"]), Inches(y),
                                 Inches(g["ruleLen"]), Inches(g["ruleH"]))
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor.from_string(theme["color"]["accent"])
    shp.line.fill.background()
    shp.shadow.inherit = False


def _title(slide, theme, g, text, size=30):
    tf = add_textbox(slide, g["marginX"], g["top"], g["contentW"], g["titleH"])
    set_simple(tf, text, theme, font="heading", size=size, bold=True, color="ink",
               line_spacing=1.1)


def _source(slide, theme, g, text):
    if not text:
        return
    tf = add_textbox(slide, g["marginX"], g["footY"] - 0.02, g["contentW"] - 0.9, 0.3)
    set_simple(tf, text, theme, font="body", size=10, color="muted")


def _page_number(slide, theme, g, n):
    if not theme.get("pageNumbers"):
        return
    tf = add_textbox(slide, g["pageW"] - g["marginX"] - 0.9, g["footY"], 0.9, 0.3)
    set_simple(tf, str(n), theme, font="body", size=10, color="muted", align=PP_ALIGN.RIGHT)


def _blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])  # 6 = Blank in the default master


def render_default(prs, theme, g, slides):
    for i, s in enumerate(slides, start=1):
        t = s.get("type", "bullets")
        slide = _blank_slide(prs)
        _set_bg(slide, theme)

        if t == "title":
            _hairline(slide, theme, g, g["ruleY"]["title"])
            tf = add_textbox(slide, g["marginX"], 2.45, g["contentW"], 1.2)
            set_simple(tf, s.get("title", ""), theme, font="heading", size=40, bold=True,
                       color="ink", line_spacing=1.1)
            if s.get("subtitle"):
                tf2 = add_textbox(slide, g["marginX"], 3.72, g["contentW"], 0.6)
                set_simple(tf2, s["subtitle"], theme, font="body", size=20, color="muted")

        elif t == "section":
            _hairline(slide, theme, g, g["ruleY"]["section"])
            if s.get("number") is not None:
                tf0 = add_textbox(slide, g["marginX"], 2.18, g["contentW"], 0.6)
                set_simple(tf0, str(s["number"]), theme, font="heading", size=22,
                           bold=True, color="accent")
            tf = add_textbox(slide, g["marginX"], 2.86, g["contentW"], 1.2)
            set_simple(tf, s.get("title", ""), theme, font="heading", size=34, bold=True,
                       color="ink", line_spacing=1.1)

        elif t == "quote":
            _hairline(slide, theme, g, g["ruleY"]["quote"])
            tf = add_textbox(slide, g["marginX"], 2.4, g["contentW"], 2.2, anchor=MSO_ANCHOR.MIDDLE)
            set_simple(tf, "“" + s.get("quote", "") + "”", theme, font="heading",
                       size=28, color="ink", line_spacing=1.25)
            if s.get("attribution"):
                tf2 = add_textbox(slide, g["marginX"], 4.5, g["contentW"], 0.5)
                set_simple(tf2, "— " + s["attribution"], theme, font="body", size=18,
                           color="muted")

        elif t == "two_col":
            _hairline(slide, theme, g, g["ruleY"]["content"])
            _title(slide, theme, g, s.get("title", ""))
            gutter = 0.5
            col_w = (g["contentW"] - gutter) / 2
            for idx, key in enumerate(("left", "right")):
                col = s.get(key) or {}
                x = g["marginX"] + idx * (col_w + gutter)
                tf = add_textbox(slide, x, g["bodyTop"], col_w, g["bodyH"])
                first = True
                if col.get("heading"):
                    p = tf.paragraphs[0]
                    _no_bullet(p)
                    p.space_after = Pt(8)
                    run = p.add_run()
                    run.text = col["heading"]
                    _set_run_font(run, name=theme["font"]["heading"], size=18, bold=True,
                                  color=theme["color"]["accent"])
                    first = False
                if first:
                    _fill_bullets(tf, theme, col.get("bullets"))
                else:
                    for it in _normalize_bullets(col.get("bullets")):
                        lvl = it["level"]
                        p = tf.add_paragraph()
                        _bullet_para(p, "–" if lvl == 0 else "•", lvl,
                                     theme["font"]["body"])
                        run = p.add_run()
                        run.text = it["text"]
                        _set_run_font(run, name=theme["font"]["body"],
                                      size=18 - (2 if lvl else 0),
                                      color=theme["color"]["ink" if lvl == 0 else "muted"])
            _source(slide, theme, g, s.get("source"))
            _page_number(slide, theme, g, i)

        elif t == "big_number":
            _hairline(slide, theme, g, g["ruleY"]["content"])
            _title(slide, theme, g, s.get("title", ""))
            tf = add_textbox(slide, g["marginX"], g["bodyTop"], g["contentW"],
                             g["bodyH"] * 0.62, anchor=MSO_ANCHOR.MIDDLE)
            set_simple(tf, str(s.get("number", "")), theme, font="number", size=88,
                       bold=True, color="accent")
            if s.get("caption"):
                tf2 = add_textbox(slide, g["marginX"], g["bodyTop"] + g["bodyH"] * 0.6,
                                  g["contentW"], 0.5)
                set_simple(tf2, s["caption"], theme, font="body", size=20, color="muted")
            _source(slide, theme, g, s.get("source"))
            _page_number(slide, theme, g, i)

        elif t == "image":
            has_title = bool(s.get("title"))
            if has_title:
                _hairline(slide, theme, g, g["ruleY"]["content"])
                _title(slide, theme, g, s["title"])
            y = g["bodyTop"] if has_title else g["top"]
            h = g["bodyH"] if has_title else g["footY"] - g["top"] - 0.4
            img = s.get("image")
            if img and os.path.exists(img):
                slide.shapes.add_picture(img, Inches(g["marginX"]), Inches(y),
                                         height=Inches(h))
            else:
                tf = add_textbox(slide, g["marginX"], y, g["contentW"], h,
                                 anchor=MSO_ANCHOR.MIDDLE)
                set_simple(tf, "[ image: %s ]" % (img or "missing"), theme, font="body",
                           size=16, color="muted", align=PP_ALIGN.CENTER)
            if s.get("caption"):
                _source(slide, theme, g, s["caption"])
            _page_number(slide, theme, g, i)

        elif t == "blank":
            if s.get("title"):
                _title(slide, theme, g, s["title"])
            _page_number(slide, theme, g, i)

        else:  # bullets (default)
            _hairline(slide, theme, g, g["ruleY"]["content"])
            _title(slide, theme, g, s.get("title", ""))
            tf = add_textbox(slide, g["marginX"], g["bodyTop"], g["contentW"], g["bodyH"])
            _fill_bullets(tf, theme, s.get("bullets"))
            _source(slide, theme, g, s.get("source"))
            _page_number(slide, theme, g, i)


# ---------------------------------------------------------------------------
# TEMPLATE-FILL MODE — open a real template, fill its placeholders.
# ---------------------------------------------------------------------------
def _ph_type_name(ph):
    try:
        return str(ph.placeholder_format.type).split(".")[-1].split(" ")[0]
    except Exception:
        return "?"


def _layout_index_by_role(prs):
    """Heuristic: pick a sensible layout index per slide type from layout names
    and placeholder types. Used when the spec/map does not pin layouts."""
    layouts = list(prs.slide_layouts)

    def find(pred, default=0):
        for i, lo in enumerate(layouts):
            if pred(lo):
                return i
        return default

    def has_types(lo, types):
        present = {ph.placeholder_format.type for ph in lo.placeholders}
        return any(t in present for t in types)

    def name_match(lo, *words):
        nm = (lo.name or "").lower()
        return any(w in nm for w in words)

    content = find(lambda lo: name_match(lo, "title and content", "content")
                   or has_types(lo, (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT)), 1)
    # image: a layout with a real PICTURE placeholder wins over any "...caption" name.
    img = find(lambda lo: has_types(lo, (PP_PLACEHOLDER.PICTURE,)), -1)
    if img < 0:
        img = find(lambda lo: name_match(lo, "picture", "image", "caption"), content)
    return {
        "title": find(lambda lo: name_match(lo, "title slide")
                      or has_types(lo, (PP_PLACEHOLDER.SUBTITLE,)), 0),
        "section": find(lambda lo: name_match(lo, "section"), content),
        "two_col": find(lambda lo: name_match(lo, "two content", "comparison",
                                              "two-col", "2 content"), content),
        "bullets": content, "big_number": content, "quote": content,
        "image": img,
        "blank": find(lambda lo: name_match(lo, "blank"), content),
    }


def _placeholders_by_role(slide):
    """Group a slide's placeholders into title / body[] / subtitle / picture by type."""
    roles = {"title": None, "subtitle": None, "body": [], "picture": None}
    for ph in slide.placeholders:
        t = ph.placeholder_format.type
        if t in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
            roles["title"] = ph
        elif t == PP_PLACEHOLDER.SUBTITLE:
            roles["subtitle"] = ph
        elif t in (PP_PLACEHOLDER.PICTURE, PP_PLACEHOLDER.OBJECT) and roles["picture"] is None \
                and t == PP_PLACEHOLDER.PICTURE:
            roles["picture"] = ph
        elif t in (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT, PP_PLACEHOLDER.SUBTITLE):
            roles["body"].append(ph)
    # body keeps left-to-right reading order
    roles["body"].sort(key=lambda p: (p.top or 0, p.left or 0))
    return roles


def _ph_by_idx(slide, idx):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    return None


def _set_ph_text(ph, text):
    """Write plain text into a placeholder, preserving its template formatting."""
    if ph is None or text is None:
        return
    ph.text_frame.text = str(text)


def _set_ph_bullets(ph, items):
    """Write multi-level bullets into a placeholder; the template styles them."""
    if ph is None:
        return
    tf = ph.text_frame
    tf.clear()
    norm = _normalize_bullets(items)
    if not norm:
        return
    for i, it in enumerate(norm):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = it["text"]
        p.level = min(it["level"], 8)


def render_template(prs, spec, map_cfg):
    slides = spec.get("slides") or []
    role_layout = _layout_index_by_role(prs)
    chosen = []

    for s in slides:
        t = s.get("type", "bullets")
        m = (map_cfg or {}).get(t, {})
        # layout: explicit per-slide > map > heuristic
        li = s.get("layout", m.get("layout", role_layout.get(t, 0)))
        layout = _resolve_layout(prs, li)
        slide = prs.slides.add_slide(layout)
        roles = _placeholders_by_role(slide)
        chosen.append((t, layout.name))

        def pick(role, default_ph):
            if role in m:  # explicit placeholder idx from the map wins
                return _ph_by_idx(slide, m[role])
            return default_ph

        title_text = s.get("title")
        if t == "quote":
            title_text = None  # quote has no title field
        _set_ph_text(pick("title", roles["title"]), title_text)

        if t == "title":
            _set_ph_text(pick("subtitle", roles["subtitle"]
                              or (roles["body"][0] if roles["body"] else None)),
                         s.get("subtitle"))
        elif t == "section":
            pass  # title placeholder already filled
        elif t == "two_col":
            bodies = roles["body"]
            left = pick("left", bodies[0] if len(bodies) > 0 else None)
            right = pick("right", bodies[1] if len(bodies) > 1 else None)
            _fill_col_placeholder(left, s.get("left") or {})
            if right is not None:
                _fill_col_placeholder(right, s.get("right") or {})
            elif left is not None:  # no second body: merge into one
                _append_col_placeholder(left, s.get("right") or {})
        elif t == "big_number":
            body = pick("body", roles["body"][0] if roles["body"] else None)
            parts = [str(s.get("number", ""))]
            if s.get("caption"):
                parts.append(s["caption"])
            _set_ph_bullets(body, parts)
            _set_ph_text(pick("source", None), s.get("source"))
        elif t == "quote":
            body = pick("body", roles["body"][0] if roles["body"] else None)
            lines = ["“" + s.get("quote", "") + "”"]
            if s.get("attribution"):
                lines.append("— " + s["attribution"])
            _set_ph_bullets(body, lines)
        elif t == "image":
            pic = pick("image", roles["picture"])
            img = s.get("image")
            if pic is not None and img and os.path.exists(img):
                try:
                    pic.insert_picture(img)
                except Exception:
                    slide.shapes.add_picture(img, pic.left, pic.top, height=pic.height)
            elif img and os.path.exists(img):
                slide.shapes.add_picture(img, Inches(1), Inches(1.5))
            _set_ph_text(pick("caption", None), s.get("caption"))
        elif t == "blank":
            pass
        else:  # bullets
            _set_ph_bullets(pick("body", roles["body"][0] if roles["body"] else None),
                            s.get("bullets"))
            _set_ph_text(pick("source", None), s.get("source"))

    return chosen


def _fill_col_placeholder(ph, col):
    if ph is None:
        return
    items = []
    if col.get("heading"):
        items.append({"text": col["heading"], "level": 0})
    items += _normalize_bullets(col.get("bullets"))
    _set_ph_bullets(ph, items)


def _append_col_placeholder(ph, col):
    if ph is None or not (col.get("heading") or col.get("bullets")):
        return
    tf = ph.text_frame
    if col.get("heading"):
        tf.add_paragraph().text = col["heading"]
    for it in _normalize_bullets(col.get("bullets")):
        p = tf.add_paragraph()
        p.text = it["text"]
        p.level = min(it["level"], 8)


def _resolve_layout(prs, ref):
    layouts = list(prs.slide_layouts)
    if isinstance(ref, int):
        return layouts[ref] if 0 <= ref < len(layouts) else layouts[0]
    if isinstance(ref, str):
        for lo in layouts:
            if (lo.name or "").lower() == ref.lower():
                return lo
        for lo in layouts:
            if ref.lower() in (lo.name or "").lower():
                return lo
    return layouts[0]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(spec, out, theme_path=DEFAULT_THEME, template=None, map_path=None):
    if template:
        prs = Presentation(template)
        map_cfg = None
        if map_path:
            with open(map_path, encoding="utf-8") as f:
                map_cfg = json.load(f)
        chosen = render_template(prs, spec, map_cfg)
        prs.save(out)
        print("wrote %s  (template-fill: %s)" % (out, os.path.basename(template)))
        for t, name in chosen:
            print("  %-11s -> layout %r" % (t, name))
    else:
        theme = apply_meta(load_theme(theme_path), spec.get("meta"))
        g = make_grid(theme)
        prs = Presentation()
        prs.slide_width = Inches(g["pageW"])
        prs.slide_height = Inches(g["pageH"])
        render_default(prs, theme, g, spec.get("slides") or [])
        prs.save(out)
        print("wrote %s  (default theme: %s)" % (out, theme.get("name", "?")))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Clean white-based .pptx generator (python-pptx).")
    ap.add_argument("spec", help="deck spec (.yaml/.yml/.json)")
    ap.add_argument("-o", "--out", required=True, help="output .pptx path")
    ap.add_argument("--theme", default=DEFAULT_THEME, help="theme JSON (default-mode only)")
    ap.add_argument("--template", help="open a real .pptx/.potx and fill its placeholders")
    ap.add_argument("--map", dest="map_path", help="role->placeholder map JSON (template mode)")
    a = ap.parse_args(argv)
    build(load_spec(a.spec), a.out, a.theme, a.template, a.map_path)


if __name__ == "__main__":
    main()
