#!/usr/bin/env python3
"""既存の .pptx を、rules/ の完了条件に照らして検査する。

各検査の id は `<rule-id>#<check-id>` であり、rules/ の `done_when` と
1対1に対応する。閾値は tokens/pptx.tokens.json から読む（値をここに書かない）。

検証の状態:
  13 条件は、正常系（pptx-build のサンプル3本）で偽陽性ゼロ、欠陥を注入した
  異常系で全て発火することを確認済み。rules/ 側も `check: automated` にしてある。
  以下2件は実装済みだが**発火を確認していない**ので、rules/ 側は manual のまま。
    - pptx-diagram-smartart-none#no-smartart（python-pptx で SmartArt を作れない）
    - pptx-master-no-stock-theme#theme-is-not-stock（実物の Office テーマが要る）

終了コード:
  0  違反なし
  1  違反あり
  2  検査できない（ファイルが読めない、下限を割っている）

使い方:
  python3 scripts/check_deck.py deck.pptx
  python3 scripts/check_deck.py deck.pptx --json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:  # pragma: no cover
    print("python-pptx が要る: pip install -r assets/requirements.txt", file=sys.stderr)
    sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

# 出典行は本文ではない（core-source-line-on-data / core-type-body-floor の
# not_applicable_when）。フッタ帯の外（図の直下など）にも置かれるので、
# 位置ではなく書き出しで識別する。
SOURCE_PREFIXES = ("出典", "出所", "Source", "source", "Note", "注:", "注：")

# 下限: 対象を消して「違反なし」にするのを防ぐ
FLOOR_BODY_SLIDES = 3

ORNAMENT_TAGS = ("gradFill", "outerShdw", "innerShdw", "bevelT", "bevelB", "glow", "reflection")
STOCK_THEMES = {"ion", "facet", "wisp", "berlin", "celestial", "damask", "depth",
                "dividend", "droplet", "frame", "mesh", "metropolitan", "parallax",
                "quotable", "retrospect", "savon", "slice", "vapor trail", "view"}


def load_tokens() -> dict:
    return json.loads((ROOT / "tokens" / "pptx.tokens.json").read_text(encoding="utf-8"))


class Findings:
    def __init__(self) -> None:
        self.rows: list[tuple[str, int, str]] = []   # (check_id, slide_no, message)
        self.skipped: list[tuple[str, str]] = []     # (check_id, なぜ評価しなかったか)

    def add(self, check: str, slide: int, message: str) -> None:
        self.rows.append((check, slide, message))

    def skip(self, check: str, why: str) -> None:
        self.skipped.append((check, why))

    def of(self, check: str) -> list:
        return [r for r in self.rows if r[0] == check]


# ---------------------------------------------------------------- 走査の下ごしらえ

def iter_text(shape):
    """(段落, run) を返す。図形が文字を持たなければ何も返さない。"""
    if not getattr(shape, "has_text_frame", False):
        return
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            yield para, run


def shapes_of(slide):
    """グループを展開して全図形を返す。"""
    out = []
    def walk(container):
        for sh in container:
            if sh.shape_type == 6 and hasattr(sh, "shapes"):   # GROUP
                walk(sh.shapes)
            else:
                out.append(sh)
    walk(slide.shapes)
    return out


def is_smartart(shape) -> bool:
    xml = shape._element.xml
    return "graphicData" in xml and "diagramLayout" in xml


def alt_text_of(shape) -> str:
    el = shape._element
    nv = el.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvPr")
    if nv is None:
        nv = el.find(f".//{NS_A}cNvPr")
    return (nv.get("descr") or "").strip() if nv is not None else ""


def in_footer(shape, tok) -> bool:
    """フッタ線より下にある要素か。出典行とページ番号がここに入る。

    rules の not_applicable_when が「出典行・ページ番号は本文ではない」と
    定めているので、本文向けの検査から外す。
    """
    top = getattr(shape, "top", None)
    if top is None:
        return False
    return top >= Emu(int(tok["grid"]["footerTop"]["$value"] * 914400))


def is_source_line(text: str) -> bool:
    t = text.strip()
    return any(t.startswith(p) for p in SOURCE_PREFIXES)


def is_body_text(shape, tok) -> bool:
    """本文とみなす図形か。タイトル・フッタ・表の中・出典行は本文ではない。"""
    if not getattr(shape, "has_text_frame", False):
        return False
    if getattr(shape, "has_table", False):
        return False
    if getattr(shape, "is_placeholder", False) and shape.placeholder_format.idx == 0:
        return False
    if is_source_line(shape.text_frame.text):
        return False
    return not in_footer(shape, tok)


def body_slide_count(prs) -> int:
    """タイトルと本文の両方を持つスライドの数（下限の判定に使う）。"""
    n = 0
    for slide in prs.slides:
        has_title = any(sh.has_text_frame and sh.text_frame.text.strip()
                        and sh.is_placeholder and sh.placeholder_format.idx == 0
                        for sh in slide.shapes if hasattr(sh, "is_placeholder"))
        has_body = any(sh.has_text_frame and sh.text_frame.text.strip()
                       for sh in slide.shapes
                       if getattr(sh, "has_text_frame", False)
                       and not (getattr(sh, "is_placeholder", False)
                                and sh.placeholder_format.idx == 0))
        if has_title and has_body:
            n += 1
    return n


# ---------------------------------------------------------------- 検査

def check_type_scale(prs, tok, f):
    allowed = {v["$value"] for k, v in tok["fontSize"].items() if k != "$type"
               and isinstance(v, dict) and "$value" in v}
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            for _, run in iter_text(sh):
                if run.font.size is None:      # レイアウト継承。マスターが決めている
                    continue
                pt = round(run.font.size.pt, 1)
                if pt not in allowed:
                    f.add("core-type-one-scale#sizes-from-scale", i,
                          f"型スケールに無いサイズ {pt}pt「{run.text[:18]}」")


def check_body_floor(prs, tok, f):
    floor = tok["fontSize"]["body"]["$value"]
    sub = tok["fontSize"]["bodySub"]["$value"]
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            if not is_body_text(sh, tok):       # タイトル・フッタ・表は本文ではない
                continue
            for para, run in iter_text(sh):
                if run.font.size is None:
                    continue
                pt = run.font.size.pt
                limit = sub if para.level >= 1 else floor
                if pt < limit:
                    f.add("core-type-body-floor#body-not-below-floor", i,
                          f"本文 {pt}pt < 下限 {limit}pt「{run.text[:18]}」")


def check_font_families(prs, tok, f):
    fams = set()
    for slide in prs.slides:
        for sh in shapes_of(slide):
            for _, run in iter_text(sh):
                if run.font.name:
                    fams.add(run.font.name)
    if len(fams) > 2:
        f.add("core-type-two-families-max#at-most-two-families", 0,
              f"書体ファミリーが {len(fams)} 種: {', '.join(sorted(fams))}")


def check_density(prs, tok, f):
    top_max = tok["density"]["bulletsTopLevelMax"]["$value"]
    depth_max = tok["density"]["bulletDepthMax"]["$value"]
    cols_max = tok["density"]["tableColumnsMax"]["$value"]
    rows_max = tok["density"]["tableRowsMax"]["$value"]
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            if getattr(sh, "has_table", False):
                t = sh.table
                if len(t.columns) > cols_max or len(t.rows) > rows_max:
                    f.add("core-density-budget#table-within-budget", i,
                          f"表 {len(t.columns)}列 × {len(t.rows)}行 が上限 "
                          f"{cols_max}×{rows_max} を超える")
            if not is_body_text(sh, tok):
                continue
            paras = [p for p in sh.text_frame.paragraphs if p.text.strip()]
            top = sum(1 for p in paras if p.level == 0)
            if top > top_max:
                f.add("core-density-budget#bullets-within-budget", i,
                      f"第1階層の箇条書きが {top} 個（上限 {top_max}）")
            deepest = max((p.level for p in paras), default=0) + 1
            if deepest > depth_max:
                f.add("core-density-budget#nesting-depth", i,
                      f"箇条書きの階層が {deepest}（上限 {depth_max}）")


def check_ornament(prs, tok, f):
    slide_w = prs.slide_width
    title_bottom = Emu(int(tok["grid"]["titleTop"]["$value"] * 914400)) + \
        Emu(int(tok["grid"]["titleHeight"]["$value"] * 914400))
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            xml = sh._element.xml
            hit = [t for t in ORNAMENT_TAGS if f"<{NS_A[1:-1]}" not in xml and f"a:{t}" in xml]
            if hit:
                f.add("core-ornament-none#no-ornament-shapes", i,
                      f"装飾効果 {', '.join(sorted(set(hit)))} を持つ図形")
            # 自動図形は空のテキストフレームを持つので、has_text_frame では外せない。
            # 文字が入っているものだけを本文として除外する。
            has_words = (getattr(sh, "has_text_frame", False)
                         and sh.text_frame.text.strip())
            if has_words or getattr(sh, "has_table", False):
                continue
            if sh.width is None or sh.top is None:
                continue
            if sh.width >= slide_w * 0.95 and sh.top < title_bottom and "solidFill" in xml:
                f.add("core-ornament-none#no-title-band", i,
                      "タイトル領域にスライド幅いっぱいの塗り図形")


def check_underline(prs, tok, f):
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            for _, run in iter_text(sh):
                if run.font.underline:
                    f.add("core-emphasis-ladder#no-underline-emphasis", i,
                          f"下線「{run.text[:18]}」")


def check_alignment(prs, tok, f):
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            if not is_body_text(sh, tok):
                continue
            for para in sh.text_frame.paragraphs:
                if not para.text.strip() or para.alignment is None:
                    continue
                if str(para.alignment).startswith(("CENTER", "RIGHT", "JUSTIFY")):
                    f.add("core-layout-one-alignment#single-alignment-per-slide", i,
                          f"本文が {str(para.alignment).split()[0]} 揃え「{para.text[:18]}」")


def check_pie(prs, tok, f):
    limit = tok["density"]["pieSlicesMax"]["$value"]
    seen = False
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            if not getattr(sh, "has_chart", False):
                continue
            seen = True
            if "pie" not in str(sh.chart.chart_type).lower():
                continue
            n = len(list(sh.chart.plots[0].categories))
            if n > limit:
                f.add("core-chart-pie-limit#pie-slices-within-limit", i,
                      f"円グラフの区分が {n}（上限 {limit}）")
    if not seen:
        f.skip("core-chart-pie-limit#pie-slices-within-limit", "グラフが1つも無い")


def check_titles_unique(prs, tok, f):
    seen: dict[str, int] = {}
    for i, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if getattr(sh, "is_placeholder", False) and sh.placeholder_format.idx == 0:
                t = sh.text_frame.text.strip()
                if not t:
                    continue
                if t in seen:
                    f.add("core-a11y-reading-order#titles-unique", i,
                          f"タイトルが {seen[t]} 枚目と同一「{t[:24]}」")
                seen.setdefault(t, i)


def check_smartart(prs, tok, f):
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            if is_smartart(sh):
                f.add("pptx-diagram-smartart-none#no-smartart", i, "SmartArt 図形")


def check_alt_text(prs, tok, f):
    seen = False
    for i, slide in enumerate(prs.slides, 1):
        for sh in shapes_of(slide):
            if getattr(sh, "has_text_frame", False) or getattr(sh, "has_table", False):
                continue
            if sh.shape_type is None:
                continue
            seen = True
            if not alt_text_of(sh):
                f.add("core-a11y-alt-text#alt-text-present", i,
                      f"代替テキストが空の要素（{sh.shape_type}）")
    if not seen:
        f.skip("core-a11y-alt-text#alt-text-present", "文字以外の要素が1つも無い")


def check_stock_theme(prs, tok, f):
    for master in prs.slide_masters:
        part = master.part
        for rel in part.rels.values():
            if "theme" in rel.reltype:
                name = ""
                try:
                    name = rel.target_part.blob.decode("utf-8", "ignore")[:400]
                except Exception:
                    continue
                for stock in STOCK_THEMES:
                    if f'name="{stock}"' in name.lower():
                        f.add("pptx-master-no-stock-theme#theme-is-not-stock", 0,
                              f"同梱テーマ「{stock}」が設定されている")


CHECKS = [
    ("core-type-one-scale#sizes-from-scale", check_type_scale),
    ("core-type-body-floor#body-not-below-floor", check_body_floor),
    ("core-type-two-families-max#at-most-two-families", check_font_families),
    ("core-density-budget#bullets-within-budget", check_density),
    ("core-ornament-none#no-ornament-shapes", check_ornament),
    ("core-emphasis-ladder#no-underline-emphasis", check_underline),
    ("core-layout-one-alignment#single-alignment-per-slide", check_alignment),
    ("core-chart-pie-limit#pie-slices-within-limit", check_pie),
    ("core-a11y-reading-order#titles-unique", check_titles_unique),
    ("pptx-diagram-smartart-none#no-smartart", check_smartart),
    ("core-a11y-alt-text#alt-text-present", check_alt_text),
    ("pptx-master-no-stock-theme#theme-is-not-stock", check_stock_theme),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="rules/ の完了条件で .pptx を検査する")
    ap.add_argument("deck")
    ap.add_argument("--json", action="store_true", help="機械可読で出す")
    args = ap.parse_args(argv)

    path = pathlib.Path(args.deck)
    if not path.is_file():
        print(f"開けない: {path}", file=sys.stderr)
        return 2
    try:
        prs = Presentation(str(path))
    except Exception as exc:
        print(f".pptx として読めない: {exc}", file=sys.stderr)
        return 2

    tok = load_tokens()
    f = Findings()

    # 下限を先に見る。対象を消して「違反なし」にできないようにする
    bodies = body_slide_count(prs)
    if bodies < FLOOR_BODY_SLIDES:
        msg = (f"下限を割っている: タイトルと本文を持つスライドが {bodies} 枚 "
               f"（{FLOOR_BODY_SLIDES} 枚以上が必要）")
        print(json.dumps({"exit": 2, "reason": msg}, ensure_ascii=False) if args.json else msg,
              file=sys.stderr)
        return 2

    seen = set()
    for _, fn in CHECKS:
        if fn in seen:
            continue
        seen.add(fn)
        fn(prs, tok, f)

    if args.json:
        print(json.dumps({
            "deck": str(path), "slides": len(prs.slides), "body_slides": bodies,
            "violations": [{"check": c, "slide": s, "message": m} for c, s, m in f.rows],
            "skipped": [{"check": c, "why": w} for c, w in f.skipped],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"{path.name}: {len(prs.slides)} スライド（本文 {bodies} 枚）"
              f" / 検査 {len(CHECKS)} 件")
        for c, w in f.skipped:
            print(f"  対象なし {c} — {w}")
        for c, s, m in f.rows:
            where = f"スライド{s}" if s else "デッキ全体"
            print(f"  違反 {c}  [{where}] {m}", file=sys.stderr)
        print("違反なし" if not f.rows else f"\n違反 {len(f.rows)} 件", 
              file=sys.stderr if f.rows else sys.stdout)
    return 1 if f.rows else 0


if __name__ == "__main__":
    sys.exit(main())
