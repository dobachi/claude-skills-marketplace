#!/usr/bin/env python3
"""validate_deck.py — structure / logic / narrative checks for a deck spec.

A deck can render cleanly and still fail to *argue*. This tool reviews the spec
the way a good editor reviews a draft, in two layers:

  1. Mechanical lint (deterministic): action titles present, one-message-per-slide
     density, sources on data claims, section structure, duplicate titles, and the
     same overflow estimate the renderer uses. Each is a finding with a severity.

  2. Narrative spine: prints the title-only "ghost deck" — every slide's title in
     order, grouped by section. Reading the spine end-to-end is the cross-slide
     check no linter can do: does the storyline hold, do the section titles support
     their section, does the close deliver the open's promise, do any claims
     contradict? Judge it against references/narrative-and-logic.md.

Usage:
  python3 validate_deck.py SPEC.yaml            # report + spine, exit!=0 on ERROR
  python3 validate_deck.py SPEC.yaml --strict   # WARN also fails
  python3 validate_deck.py SPEC.yaml --json      # machine-readable findings + spine

Reuses build_deck's loaders/estimators so findings match what the renderer does.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_deck as B  # noqa: E402  — reuse spec/theme/grid/estimators

# A data claim worth a source: a NUMBER carrying a unit/magnitude (percent,
# currency, points, multiples, counts) — not every stray digit like "3つ" or
# "2026年" or "Q2", which would flag prose that makes no quantitative claim.
DATA_RE = re.compile(
    r"\d+(?:\.\d+)?\s*[%％]"            # 18% / 4.2 %
    r"|[¥$＄]\s*\d|\d+\s*(?:円|ドル)"   # ¥1000 / $5 / 100円
    r"|\d+(?:\.\d+)?\s*(?:pt|ppt|ポイント|倍|割|億|万|兆|件|社|人|名|時間|日|週|ヶ月|か月)"
    r"|\d+(?:\.\d+)?\s*[x×]\b",
    re.I)
# Sentence-like cues that suggest a title asserts something (an action title)
# rather than naming a topic: punctuation, particles, or predicate endings.
ASSERT_RE = re.compile(
    r"[、。，．:：!！?？%％]|[はがをにへとでもや]|する|した|して|れる|られる|"
    r"ない|べき|だ$|である|った|increase|grow|grew|fall|fell|rose|drove|wins?|"
    r"should|will|is|are|was|were|up|down", re.I)

CONTENT_TYPES = {"bullets", "two_col", "big_number", "image"}
ERROR, WARN, INFO = "ERROR", "WARN", "INFO"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _slide_title(s):
    if s.get("type") == "quote":
        return (s.get("quote") or "").strip()
    return (s.get("title") or "").strip()


def _looks_like_topic(title):
    """Heuristic: a bare topic label ('Q3 Results') rather than a takeaway.
    Deliberately conservative — emitted only as INFO, since real action-title
    judgment is part of the narrative read, not something a regex can settle."""
    t = title.strip()
    if not t:
        return False
    ascii_ratio = sum(ord(c) < 128 for c in t) / len(t)
    if ascii_ratio > 0.7:  # mostly English
        words = [w for w in re.split(r"\s+", t) if w]
        return len(words) <= 3 and not DATA_RE.search(t)
    # Japanese: short noun-ish phrase with no assertion cue
    return B._disp_width(t) <= 9 and not ASSERT_RE.search(t)


def _has_data_claim(s):
    if s.get("type") == "big_number":
        return True
    texts = [_slide_title(s)]
    for key in ("bullets",):
        for it in B._normalize_bullets(s.get(key)):
            texts.append(it["text"])
    for col in ("left", "right"):
        c = s.get(col) or {}
        texts.append(c.get("heading", ""))
        for it in B._normalize_bullets(c.get("bullets")):
            texts.append(it["text"])
    if s.get("caption"):
        texts.append(s["caption"])
    return any(DATA_RE.search(t or "") for t in texts)


def _body_overflows(s, theme, g):
    t = s.get("type", "bullets")
    if t == "two_col":
        col_w = (g["contentW"] - 0.5) / 2
        return any(
            B._bullets_height((s.get(k) or {}).get("bullets"), theme, col_w,
                              (s.get(k) or {}).get("heading")) > g["bodyH"] + 0.05
            for k in ("left", "right"))
    if t == "bullets":
        return B._bullets_height(s.get("bullets"), theme, g["contentW"]) > g["bodyH"] + 0.05
    return False


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def validate(spec, theme, g):
    slides = spec.get("slides") or []
    findings = []

    def add(sev, idx, msg):
        findings.append({"severity": sev, "slide": idx, "message": msg})

    # deck-level structure
    if not any(s.get("type") == "title" for s in slides):
        add(INFO, 0, "no title slide — add a title (with date/version) so the deck opens with its subject")
    n_sections = sum(1 for s in slides if s.get("type") == "section")
    if len(slides) >= 8 and n_sections == 0:
        add(INFO, 0, "%d slides and no section dividers — group the argument into 2–4 sections" % len(slides))

    seen_titles = {}
    section_has_content = True
    last_section_idx = None

    for i, s in enumerate(slides, start=1):
        t = s.get("type", "bullets")
        title = _slide_title(s)

        if t == "section":
            if last_section_idx is not None and not section_has_content:
                add(ERROR, last_section_idx, "section has no content slides before the next section — fill it or remove it")
            last_section_idx, section_has_content = i, False
            if not title:
                add(ERROR, i, "section divider has no title")
            continue
        if t in CONTENT_TYPES:
            section_has_content = True

        # title presence + quality (content slides)
        if t in CONTENT_TYPES:
            if not title:
                add(ERROR, i, "%s slide has no title — every content slide needs an action title (state the takeaway)" % t)
            else:
                key = title.lower()
                seen_titles.setdefault(key, []).append(i)
                if _looks_like_topic(title):
                    add(INFO, i, "title looks like a topic label, not a takeaway: %r — make it state the conclusion" % title)

        # title auto-fit overflow (mirrors the renderer's warning)
        if title and t in CONTENT_TYPES:
            _, over = B._fit_title_size(title, theme, g)
            if over:
                add(WARN, i, "title needs >2 lines even at the floor size — shorten or split: %r" % title)

        # one-message-per-slide density
        if t == "bullets":
            lvl0 = sum(1 for it in B._normalize_bullets(s.get("bullets")) if it["level"] == 0)
            total = len(B._normalize_bullets(s.get("bullets")))
            if lvl0 > 6:
                add(WARN, i, "%d top-level bullets — over ~6 signals more than one message; split the slide" % lvl0)
            elif total == 0:
                add(WARN, i, "bullets slide has no bullets")
        if _body_overflows(s, theme, g):
            add(WARN, i, "body won't fit at readable sizes — split into two slides (one message per slide)")

        # sources on data claims
        if t in CONTENT_TYPES and _has_data_claim(s) and not s.get("source"):
            sev = WARN if t == "big_number" else INFO
            add(sev, i, "shows a number/figure but has no source: — cite it (a data claim without a source is unverifiable)")

    if last_section_idx is not None and not section_has_content:
        add(ERROR, last_section_idx, "final section has no content slides — fill it or remove it")

    for key, idxs in seen_titles.items():
        if len(idxs) > 1:
            add(WARN, idxs[-1], "duplicate title on slides %s — titles should be unique (screen readers and TOCs navigate by title)"
                % ", ".join(map(str, idxs)))

    findings.sort(key=lambda f: (f["slide"], {ERROR: 0, WARN: 1, INFO: 2}[f["severity"]]))
    return findings


def build_spine(spec):
    """The title-only ghost deck, grouped by section — the cross-slide read."""
    spine = []
    section = None
    for i, s in enumerate(spec.get("slides") or [], start=1):
        t = s.get("type", "bullets")
        if t == "title":
            spine.append({"slide": i, "kind": "title", "section": None,
                          "text": _slide_title(s), "subtitle": s.get("subtitle")})
        elif t == "section":
            section = ("%s " % s.get("number") if s.get("number") is not None else "") + _slide_title(s)
            spine.append({"slide": i, "kind": "section", "section": section.strip(),
                          "text": _slide_title(s)})
        else:
            spine.append({"slide": i, "kind": t, "section": section,
                          "text": _slide_title(s) or "[no title]"})
    return spine


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def print_report(spine, findings):
    print("Narrative spine (title-only walkthrough)")
    print("  Read top to bottom: does this argue a single, coherent case?\n")
    for e in spine:
        if e["kind"] == "title":
            line = "  %2d  ▸ TITLE   %s" % (e["slide"], e["text"])
            if e.get("subtitle"):
                line += "  — %s" % e["subtitle"]
            print(line)
        elif e["kind"] == "section":
            print("  %2d  § %s" % (e["slide"], e["section"]))
        else:
            print("  %2d      %-10s %s" % (e["slide"], e["kind"], e["text"]))

    print("\nMechanical findings")
    if not findings:
        print("  none — clean.")
    else:
        for f in findings:
            where = "deck" if f["slide"] == 0 else "slide %d" % f["slide"]
            print("  %-5s %-8s %s" % (f["severity"], where, f["message"]))

    n_err = sum(f["severity"] == ERROR for f in findings)
    n_warn = sum(f["severity"] == WARN for f in findings)
    n_info = sum(f["severity"] == INFO for f in findings)
    print("\nSummary: %d error, %d warn, %d info" % (n_err, n_warn, n_info))
    print("Then read the spine above against references/narrative-and-logic.md:")
    print("  - Is there ONE governing thought the whole deck supports?")
    print("  - Does each section's titles add up to that section's claim (MECE, no gaps/overlaps)?")
    print("  - Does the closing deliver the opening's promise? Any claim contradicted later?")
    return n_err, n_warn


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate a deck spec's structure, logic, and narrative.")
    ap.add_argument("spec", help="deck spec (.yaml/.yml/.json)")
    ap.add_argument("--strict", action="store_true", help="exit nonzero on WARN too, not just ERROR")
    ap.add_argument("--json", action="store_true", help="emit JSON (findings + spine) instead of text")
    ap.add_argument("--theme", default=B.DEFAULT_THEME, help="theme JSON (affects size/overflow checks)")
    a = ap.parse_args(argv)

    spec = B.load_spec(a.spec)
    meta = spec.get("meta")
    theme = B._apply_size_defaults(B.apply_meta(B.load_theme(a.theme), meta), meta)
    g = B.make_grid(theme)

    findings = validate(spec, theme, g)
    spine = build_spine(spec)

    if a.json:
        print(json.dumps({"findings": findings, "spine": spine}, ensure_ascii=False, indent=2))
        n_err = sum(f["severity"] == ERROR for f in findings)
        n_warn = sum(f["severity"] == WARN for f in findings)
    else:
        n_err, n_warn = print_report(spine, findings)

    sys.exit(1 if (n_err or (a.strict and n_warn)) else 0)


if __name__ == "__main__":
    main()
