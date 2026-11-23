#!/usr/bin/env python3
"""find_pattern.py — pick a figure pattern from what the figure has to SAY.

Before drawing a figure, state its logic in a few words ("3つを比べる",
"循環を示す", "who does what") and search the catalog in
references/figure-patterns/patterns.yaml. Each hit says why it matched, when to
use it and when not, what makes it look good, the image of it, and a slide spec
that draws it with the native vocabulary.

Matching is plain and explainable, no model: a catalog keyword found in the
query (or a query word found in a keyword) scores; Japanese, which has no
spaces, is also compared by character pairs so 比較したい finds 比較.

usage:
  find_pattern.py "3つを比べる"            top 3 patterns, with snippet
  find_pattern.py "who does what" --top 5
  find_pattern.py "循環" --json             machine-readable
  find_pattern.py --list                    every pattern: id, logic, kind
  find_pattern.py --show swimlane           one pattern in full
  find_pattern.py --gallery OUT.yaml        write a deck with every pattern's spec

exit: 0 = found (or listed / written), 1 = nothing matched, 2 = usage error or
the catalog is missing / unreadable
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CATALOG = os.path.join(SKILL, "references", "figure-patterns", "patterns.yaml")

try:
    import yaml
except ImportError:
    print("find_pattern: PyYAML is required (pip install -r requirements.txt)", file=sys.stderr)
    sys.exit(2)

CJK = re.compile(r"[぀-ヿ㐀-鿿０-ｚ]")
STOP = {"a", "an", "the", "to", "of", "and", "or", "in", "on", "for", "with", "is", "are",
        "show", "shows", "showing", "want", "how", "i", "we", "it", "that", "this", "by", "be"}


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        print("find_pattern: cannot read catalog %s: %s" % (path, e), file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict) or not isinstance(data.get("patterns"), list):
        print("find_pattern: %s has no `patterns:` list" % path, file=sys.stderr)
        sys.exit(2)
    return data


def norm(s):
    return re.sub(r"\s+", " ", str(s).lower().replace("×", "x").replace("　", " ")).strip()


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def words(s):
    return {stem(w) for w in re.findall(r"[a-z0-9]+", norm(s)) if w not in STOP}


def bigrams(s):
    t = "".join(ch for ch in norm(s) if CJK.match(ch))
    return {t[k:k + 2] for k in range(len(t) - 1)}


def score(p, query):
    """(score, reasons). Keywords weigh most, then the logic and the names."""
    q = norm(query)
    qw, qb = words(query), bigrams(query)
    total, why = 0.0, []
    kws = [("ja", k) for k in (p.get("keywords") or {}).get("ja") or []] + \
          [("en", k) for k in (p.get("keywords") or {}).get("en") or []]
    for lang, k in kws:
        kn = norm(k)
        if not kn:
            continue
        if kn in q:
            total += 3.0 + 0.2 * len(kn)          # a longer phrase found whole is stronger
            why.append(k)
            continue
        if lang == "ja":
            kb = bigrams(kn)
            if kb and qb:
                hit = len(kb & qb) / len(kb)
                if hit >= 0.5:
                    total += 2.0 * hit
                    why.append("%s~" % k)
        else:
            kw = words(kn)
            if kw and kw <= qw:
                total += 2.5
                why.append(k)
            elif kw & qw:
                total += 0.8 * len(kw & qw) / len(kw)
                why.append("%s~" % k)
    for field in ("logic", "logic_ja", "id"):
        fw, fb = words(p.get(field, "")), bigrams(p.get(field, ""))
        if fw & qw:
            total += 1.0
            why.append("%s: %s" % (field, ", ".join(sorted(fw & qw))))
        elif fb and qb and len(fb & qb) >= 2:
            total += 0.6
            why.append("%s~" % field)
    for lang in ("ja", "en"):
        nm = (p.get("name") or {}).get(lang, "")
        if nm and norm(nm) in q:
            total += 3.0
            why.append("name: %s" % nm)
    return total, why


def snippet(p):
    return yaml.safe_dump([p.get("spec")], allow_unicode=True, sort_keys=False,
                          default_flow_style=None, width=100).rstrip()


def image_of(p, catalog):
    img = p.get("image")
    return os.path.join(os.path.dirname(os.path.abspath(catalog)), img) if img else None


def show(p, catalog, rank=None, sc=None, why=None, full=False):
    head = "%s%s  %s / %s" % ("%d. " % rank if rank else "", p["id"],
                               p["name"].get("ja", ""), p["name"].get("en", ""))
    if sc is not None:
        head += "   (score %.1f)" % sc
    print(head)
    print("   logic:      %s" % (p.get("logic_ja") or p.get("logic")))
    print("   draws with: %s  [%s]" % (p.get("kind"), p.get("build")))
    if why:
        print("   matched:    %s" % ", ".join(why[:8]))
    print("   use when:   %s" % p.get("use_when", ""))
    print("   not when:   %s" % p.get("avoid_when", ""))
    if full:
        for m in p.get("mistakes") or []:
            print("   mistake:    %s" % m)
    for d in (p.get("design") or [])[: None if full else 2]:
        print("   looks good: %s" % d)
    im = image_of(p, catalog)
    if im:
        print("   image:      %s%s" % (im, "" if os.path.exists(im) else "  (not rendered yet)"))
    print("   spec:")
    for line in snippet(p).splitlines():
        print("     " + line)
    print()


def gallery(data, out):
    slides = [{"type": "title", "title": "図のパターン集",
               "subtitle": "references/figure-patterns/patterns.yaml から生成（find_pattern.py --gallery）"}]
    for p in data["patterns"]:
        s = dict(p["spec"])
        s["notes"] = "pattern: %s — %s" % (p["id"], p.get("logic_ja", p.get("logic", "")))
        slides.append(s)
    head = ("# Generated by assets/find_pattern.py --gallery from references/figure-patterns/patterns.yaml.\n"
            "# Do not edit by hand: change the catalog and regenerate. One slide per pattern,\n"
            "# in catalog order (slide 1 is the title); the renders are references/figure-patterns/img/.\n")
    body = yaml.safe_dump({"meta": {"aspect": "16:9"}, "slides": slides}, allow_unicode=True,
                          sort_keys=False, width=100)
    with open(out, "w", encoding="utf-8") as f:
        f.write(head + body)
    print("wrote %s (%d patterns)" % (out, len(data["patterns"])))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Find a figure pattern for what the figure must show.")
    ap.add_argument("query", nargs="*", help="the logic, in Japanese or English")
    ap.add_argument("--top", type=int, default=3, help="how many patterns to show (default 3)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--list", action="store_true", help="list every pattern")
    ap.add_argument("--show", metavar="ID", help="show one pattern in full")
    ap.add_argument("--gallery", metavar="OUT", help="write a deck spec with every pattern")
    ap.add_argument("--catalog", default=CATALOG, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    data = load(a.catalog)
    pats = data["patterns"]

    if a.gallery:
        gallery(data, a.gallery)
        return 0
    if a.list:
        if a.json:
            print(json.dumps([{k: p.get(k) for k in ("id", "name", "logic", "kind", "build")}
                              for p in pats], ensure_ascii=False, indent=2))
        else:
            for p in pats:
                print("%-20s %-34s %-26s %s" % (p["id"], p.get("logic", ""), p.get("kind", ""),
                                                p["name"].get("ja", "")))
        return 0
    if a.show:
        hit = [p for p in pats if p["id"] == a.show]
        if not hit:
            print("find_pattern: no pattern %r — ids: %s" % (a.show, ", ".join(p["id"] for p in pats)),
                  file=sys.stderr)
            return 2
        if a.json:
            print(json.dumps(hit[0], ensure_ascii=False, indent=2))
        else:
            show(hit[0], a.catalog, full=True)
        return 0

    query = " ".join(a.query).strip()
    if not query:
        ap.print_usage(sys.stderr)
        print("find_pattern: give the logic to search for, e.g. \"3つを比べる\" or \"who does what\"",
              file=sys.stderr)
        return 2
    ranked = sorted(((score(p, query), p) for p in pats), key=lambda t: -t[0][0])
    ranked = [(sc, why, p) for (sc, why), p in ranked if sc >= 1.5][: max(1, a.top)]
    if a.json:
        print(json.dumps([{"id": p["id"], "score": round(sc, 2), "matched": why, "name": p["name"],
                           "logic": p.get("logic"), "kind": p.get("kind"), "build": p.get("build"),
                           "use_when": p.get("use_when"), "avoid_when": p.get("avoid_when"),
                           "design": p.get("design"), "image": image_of(p, a.catalog),
                           "spec": p.get("spec")} for sc, why, p in ranked],
                         ensure_ascii=False, indent=2))
    elif ranked:
        print("Patterns for: %s\n" % query)
        for k, (sc, why, p) in enumerate(ranked, 1):
            show(p, a.catalog, k, sc, why)
        print("Pick one, then adapt its spec. Full entry: find_pattern.py --show ID; "
              "all: --list; catalog: references/figure-patterns/README.md")
    if not ranked:
        if not a.json:
            print("No pattern matched %r. Say the logic in other words (比べる / 流れ / 循環 / 階層 / "
                  "重なり / 誰が何を / compare / sequence / cycle / overlap), or run --list." % query)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
