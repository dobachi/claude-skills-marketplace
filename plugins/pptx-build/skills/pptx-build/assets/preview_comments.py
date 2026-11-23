#!/usr/bin/env python3
"""preview_comments.py — bring the comments a `--comments` browser preview collected back
into the review loop.

Input (one of):
  * the Markdown the page's Export button gives ("p12 [slide-id] 要修正: …" lines), or
  * the Artifact db collection "reviews" as JSON: the folder ArtifactData `list` wrote with
    `out_dir` (OUT/reviews/<doc>.json), one such file, or a JSON list of documents.

Output:
  * default        the comment list, one line per slide in page order, review-roundtrip style
                   (`p12 [slide-id] 要修正: …`, continuation lines indented two spaces)
  * --json         the same as JSON records {page, slide, status, comment, updated}
  * --sheet FILE   write the comments into a review-roundtrip sheet made by
                   `review_sheet.py new DECK.pptx`: each one goes under its slide's location
                   (`<!-- loc: S12 -->`, or `A2.S12` with --artifact A2) as `- [ ] 要修正: …`.
                   Then run `review_sheet.py ingest` as usual. Re-running adds nothing twice.
  * --spec deck.yaml  map each comment by its slide id to the slide's page in THIS spec, so
                   comments written before slides were inserted land on the right slide.

A slide marked only with the first status label (e.g. OK) and no comment is listed in the
comment list but not written into a sheet (it asks for nothing); --keep-ok writes it too.

usage: preview_comments.py INPUT [--spec deck.yaml] [--sheet SHEET [--artifact A1] [--keep-ok]]
                           [--json] [-o OUT]
exit:  0 done / 1 findings (a slide id not in the spec, a page with no location in the sheet;
       the rest is still written) / 2 usage or unreadable input
"""
import argparse
import glob
import json
import os
import re
import sys

LINE = re.compile(r"^p(\d+|\?)(?:\s+\[([^\]\n]*)\])?(?:\s+(.*))?$")
LABELS_RE = re.compile(r"<!--\s*review-labels:\s*(.*?)\s*-->")
DEFAULT_LABELS = ["OK", "要修正", "質問", "Fix", "Question"]
PREFIXES = re.compile(r"^(?:[^\s:：]{1,20}: )*")


def die(code, msg):
    print(f"preview_comments: {msg}", file=sys.stderr)
    sys.exit(code)


def split_status(rest, labels):
    """'要修正: 矢印が逆' → ('要修正', '矢印が逆'); 'OK' → ('OK', ''); else ('', rest)."""
    rest = rest or ""
    for lab in sorted(labels, key=len, reverse=True):
        if rest == lab:
            return lab, ""
        if rest.startswith(lab + ": "):
            return lab, rest[len(lab) + 2:]
    return "", rest


def from_markdown(text):
    m = LABELS_RE.search(text)
    labels = [x.strip() for x in m.group(1).split(",") if x.strip()] if m else DEFAULT_LABELS
    out, cur = [], None
    for raw in text.splitlines():
        if cur is not None and raw.startswith("  ") and raw.strip():
            cur["comment"] = (cur["comment"] + "\n" + raw[2:]).strip("\n")
            continue
        cur = None
        hit = LINE.match(raw.strip()) if not raw.startswith((" ", "#", "<!--")) else None
        if not hit:
            continue
        status, comment = split_status(hit.group(3), labels)
        cur = {"page": int(hit.group(1)) if hit.group(1) != "?" else None, "slide": hit.group(2) or "",
               "status": status, "comment": comment, "updated": ""}
        out.append(cur)
    return out, labels


def body_of(d, fallback_id):
    """ArtifactData files may hold the body itself or {id, data, version}."""
    if isinstance(d.get("data"), dict):
        return d.get("id") or fallback_id, d["data"]
    return d.get("id") or fallback_id, d


def from_json(path):
    docs = []
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, "reviews", "*.json"))) or \
            sorted(glob.glob(os.path.join(path, "*.json")))
        if not files:
            die(2, f"no JSON documents in {path} (expected {path}/reviews/<doc>.json)")
        for f in files:
            try:
                docs.append(body_of(json.load(open(f, encoding="utf-8")), os.path.splitext(os.path.basename(f))[0]))
            except (OSError, ValueError) as e:
                die(2, f"cannot read {f}: {e}")
    else:
        try:
            d = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            die(2, f"cannot read {path}: {e}")
        items = d.get("docs") or d.get("documents") if isinstance(d, dict) else d
        if isinstance(d, dict) and items is None:
            items = [d]
        if not isinstance(items, list):
            die(2, f"{path}: expected a document, a list of documents or {{docs: [...]}}")
        for i, x in enumerate(items):
            if isinstance(x, dict):
                docs.append(body_of(x, f"doc{i + 1}"))
    out = []
    for doc_id, b in docs:
        page = b.get("page")
        if page is None and re.fullmatch(r"p\d+", doc_id):
            page = int(doc_id[1:])
        out.append({"page": int(page) if isinstance(page, (int, float, str)) and str(page).isdigit() else None,
                    "slide": str(b.get("slide") or ""), "status": str(b.get("status") or ""),
                    "comment": str(b.get("comment") or "").strip(), "updated": str(b.get("updated") or "")})
    return [r for r in out if r["status"] or r["comment"]], None


def spec_pages(path):
    try:
        import yaml
    except ImportError:
        die(2, "PyYAML is needed for --spec (pip install pyyaml)")
    try:
        doc = yaml.safe_load(open(path, encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        die(2, f"cannot read spec {path}: {e}")
    if not isinstance(doc, dict) or not isinstance(doc.get("slides"), list):
        die(2, f"{path} has no `slides:` list")
    pages, n = {}, 0
    for s in doc["slides"]:
        s = s if isinstance(s, dict) else {}
        if s.get("hidden"):
            continue
        n += 1
        if s.get("id") is not None:
            pages.setdefault(" ".join(str(s["id"]).split()), []).append(n)
    return {k: v[0] for k, v in pages.items() if len(v) == 1}


def line(r):
    head = f"p{r['page'] if r['page'] else '?'}" + (f" [{r['slide']}]" if r["slide"] else "")
    c = r["comment"].replace("\r\n", "\n").split("\n") if r["comment"] else [""]
    first = head + (f" {r['status']}" + (f": {c[0]}" if c[0] else "") if r["status"] else (f" {c[0]}" if c[0] else ""))
    return "\n".join([first] + ["  " + x for x in c[1:]])


def sheet_text(r):
    c = r["comment"].split("\n") if r["comment"] else [""]
    first = (f"{r['status']}: {c[0]}" if c[0] else r["status"]) if r["status"] else c[0]
    return [first] + c[1:]


def into_sheet(path, recs, art, keep_ok, first_label):
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except OSError as e:
        die(2, f"cannot read sheet {path}: {e}")
    if not any(x.startswith("review_sheet:") for x in lines[:5]):
        die(2, f"{path} is not a review sheet (make one with review_sheet.py new DECK.pptx)")
    added, skipped, missing = 0, 0, []
    for r in recs:
        if r["page"] is None:
            missing.append(line(r).split("\n")[0])
            continue
        if not keep_ok and r["status"] == first_label and not r["comment"]:
            skipped += 1
            continue
        loc = f"{art}.S{r['page']}" if art else f"S{r['page']}"
        start = next((i for i, x in enumerate(lines)
                      if x.startswith("#") and re.search(r"<!--\s*loc:\s*" + re.escape(loc) + r"\s*-->", x)), None)
        if start is None:
            missing.append(line(r).split("\n")[0])
            continue
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#")), len(lines))
        text = sheet_text(r)
        new = ["- [ ] " + text[0]] + ["  " + x for x in text[1:]]
        body = [x.rstrip() for x in lines[start + 1:end]]
        # already there? (ingest may have put an id like "S3-1: " in front)
        bare = PREFIXES.sub("", text[0].rstrip())
        if any(PREFIXES.sub("", x[6:]) == bare for x in body if re.match(r"^- \[.\] ", x)):
            skipped += 1
            continue
        blank = next((i for i in range(start + 1, end) if re.fullmatch(r"- \[ \]\s*", lines[i])), None)
        if blank is not None:
            lines[blank:blank + 1] = new
        else:
            last = max(i for i in range(start, end) if lines[i].strip())
            lines[last + 1:last + 1] = new
        added += 1
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{added} comment(s) added to {path}, {skipped} skipped (OK only, or already there)")
    return missing


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", help="exported Markdown, or the reviews JSON (folder, file or list)")
    ap.add_argument("--spec", help="deck spec: re-map slide ids to their pages in this spec")
    ap.add_argument("--sheet", help="review-roundtrip sheet to write the comments into")
    ap.add_argument("--artifact", help="the artifact section of a multi-artifact sheet (A1, A2 …)")
    ap.add_argument("--keep-ok", action="store_true", help="also write slides marked only OK")
    ap.add_argument("--json", action="store_true", help="print JSON records instead of lines")
    ap.add_argument("-o", "--out", help="write the comment list here instead of stdout")
    a = ap.parse_args()
    if not os.path.exists(a.input):
        die(2, f"no such input: {a.input}")
    if a.artifact and not re.fullmatch(r"A\d+", a.artifact):
        die(2, "--artifact takes A1, A2 …")
    is_json = os.path.isdir(a.input) or a.input.endswith(".json")
    if is_json:
        recs, labels = from_json(a.input)
    else:
        recs, labels = from_markdown(open(a.input, encoding="utf-8").read())
    if not recs:
        print("no comments in the input")
    findings = []
    if a.spec:
        pages = spec_pages(a.spec)
        for r in recs:
            if not r["slide"]:
                continue
            if r["slide"] in pages:
                if r["page"] != pages[r["slide"]]:
                    print(f"moved: [{r['slide']}] p{r['page']} -> p{pages[r['slide']]}", file=sys.stderr)
                r["page"] = pages[r["slide"]]
            else:
                findings.append(f"NG slide id [{r['slide']}] (p{r['page']}) is not in {a.spec}; kept at its old page")
    recs.sort(key=lambda r: (r["page"] is None, r["page"] or 0))
    if a.json:
        text = json.dumps(recs, ensure_ascii=False, indent=2) + "\n"
    else:
        text = "".join(line(r) + "\n" for r in recs)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"{len(recs)} comment(s) -> {a.out}")
    elif not a.sheet:
        sys.stdout.write(text)
    if a.sheet:
        first = (labels or ["OK"])[0]
        findings += [f"NG no location in the sheet for: {m}" for m in into_sheet(a.sheet, recs, a.artifact, a.keep_ok, first)]
    for f in findings:
        print(f, file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
