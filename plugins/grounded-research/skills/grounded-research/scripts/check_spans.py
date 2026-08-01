#!/usr/bin/env python3
"""check_spans.py - Verify that every quoted span in a research report actually
appears in the source it is attributed to.

This is the mechanical half of the grounding gate. The blind verifier checks
claim <-> span. This checks span <-> page: it re-fetches each registered URL and
looks for the span as a literal substring. A span that was paraphrased,
normalized, stitched together, or invented outright fails here and nowhere else.

Usage:
  python3 check_spans.py <report.md> [options]

  <report.md> must contain the skill's Source Register table (rows starting
  with an S- ID and carrying a URL) and Claim Ledger table (rows starting with
  a C- ID, a Source column of S- IDs, and a Span column).

Body quotes are checked too: any blockquote whose attribution line names an
S- ID (`> — S-02, Vendor pricing page (T2, accessed …)`) is matched against
that source's page, and against the ledger span it should have been copied
from. Those rows appear with claim id `body`.

Options:
  --cache-dir <dir>   Where to cache fetched page text (default: a temp dir).
                      Reused across runs, so re-checks are free.
  --local <S-ID=path> Read this source from a local file instead of fetching.
                      Repeatable. Use for paywalled or JS-rendered pages you
                      saved by hand.
  --timeout <sec>     Per-URL fetch timeout (default: 20).
  --min-fragment <n>  Ignore ellipsis fragments shorter than n characters
                      (default: 8). Short fragments match by accident.
  --json              Emit JSON instead of a Markdown table.
  --quiet             Only report spans that are not EXACT.

Verdicts:
  EXACT       Span found verbatim. Ships.
  NORMALIZED  Found only after whitespace/quote/dash folding. Ships, but the
              ledger span should be corrected to the page's actual characters.
  NOT-FOUND   Page fetched, span absent. Blocks delivery.
  UNREACHABLE Page could not be fetched or parsed (PDF, paywall, JS-rendered).
              Not a pass - check by hand and record that you did.

Exit codes:
  0  every span EXACT or NORMALIZED
  1  at least one NOT-FOUND
  2  no NOT-FOUND, but at least one UNREACHABLE (manual check required)
  3  usage / parse error (no ledger found, unreadable report)

Requires: Python 3.8+, stdlib only. Uses `pdftotext` for PDF sources if it is
on PATH; without it, PDFs are UNREACHABLE.
"""

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (compatible; grounded-research span-checker)"

# ---------------------------------------------------------------- report parsing


def _cells(line):
    """Split a Markdown table row into stripped cells."""
    line = line.strip()
    if not line.startswith("|"):
        return []
    return [c.strip() for c in line.strip("|").split("|")]


def parse_report(text):
    """Return (sources, claims).

    sources: {"S-01": {"url":..., "title":...}}
    claims:  [{"id":..., "sources":[...], "span_cell":...}]
    Tables are located by row shape, not by heading, so a report that renames
    its sections still checks.
    """
    sources, claims = {}, []
    for line in text.splitlines():
        cells = _cells(line)
        if len(cells) < 3:
            continue
        cid = cells[0]
        if re.fullmatch(r"S-\d+", cid):
            url = ""
            for c in cells[1:]:
                m = re.search(r"https?://[^\s)\]>|]+", c)
                if m:
                    url = m.group(0).rstrip(".,;")
                    break
            sources[cid] = {"url": url, "title": cells[1] if len(cells) > 1 else ""}
        elif re.fullmatch(r"C-\d+", cid):
            refs, span_cell = [], ""
            for c in cells[1:]:
                found = re.findall(r"S-\d+", c)
                if found and not refs:
                    refs = found
                    continue
                if refs and not span_cell and c and c != "—":
                    span_cell = c
            if refs:
                claims.append({"id": cid, "sources": refs, "span_cell": span_cell})
    return sources, claims


QUOTE_RE = re.compile(r"[\"“”「『‘’']")


def extract_spans(span_cell):
    """Pull the quoted segment(s) out of a Span cell.

    Handles "…", “…”, 「…」 and a bare unquoted cell. Multiple spans in one
    cell (a claim resting on two sources) are separated by ; or by adjacent
    quoted segments.
    """
    if not span_cell or span_cell in {"—", "-", "see disagreement block"}:
        return []
    segs = re.findall(
        r"“(.+?)”|「(.+?)」|『(.+?)』|\"(.+?)\"", span_cell
    )
    out = [next(g for g in tup if g) for tup in segs]
    if not out:
        out = [s.strip() for s in span_cell.split(";") if s.strip()]
    return [s for s in (x.strip() for x in out) if s]


ATTRIB_RE = re.compile(r"^\s*(?:—|--|–|-)\s*(S-\d+)")


def parse_body_quotes(text):
    """Blockquote blocks in the body whose attribution line names an S- ID.

    Returns [{"source": "S-02", "quote": "..."}]. Blocks without an S- attribution
    are ignored - they are not making a sourcing claim.
    """
    out, block = [], []
    for line in text.splitlines() + [""]:
        stripped = line.strip()
        if stripped.startswith(">"):
            block.append(stripped.lstrip(">").strip())
            continue
        if block:
            sid, body = None, []
            for entry in block:
                m = ATTRIB_RE.match(entry)
                if m:
                    sid = m.group(1)
                else:
                    body.append(entry)
            quote = " ".join(b for b in body if b).strip()
            quote = quote.strip("“”\"「」『』")
            if sid and quote:
                out.append({"source": sid, "quote": quote})
            block = []
    return out


ELLIPSIS_RE = re.compile(r"…|\.\.\.|・・・")


def fragments(span, min_len):
    """An elided span is a set of fragments; every one of them must be present."""
    parts = [p.strip() for p in ELLIPSIS_RE.split(span)]
    parts = [p for p in parts if len(p) >= min_len]
    return parts or [span.strip()]


# ---------------------------------------------------------------- fetching


def html_to_text(raw):
    raw = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return html.unescape(raw)


def fetch(url, timeout, cache_dir):
    """Return (text, None) or (None, reason). Cached by URL hash."""
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    cached = os.path.join(cache_dir, key + ".txt")
    if os.path.exists(cached):
        with open(cached, encoding="utf-8", errors="replace") as fh:
            return fh.read(), None

    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            body = resp.read()
    except urllib.error.HTTPError as exc:
        return None, "HTTP %s" % exc.code
    except Exception as exc:  # network, TLS, DNS, timeout
        return None, type(exc).__name__

    if "pdf" in ctype or url.lower().endswith(".pdf"):
        if not shutil.which("pdftotext"):
            return None, "PDF (pdftotext not on PATH)"
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(body)
            pdf_path = tmp.name
        try:
            text = subprocess.run(
                ["pdftotext", "-layout", pdf_path, "-"],
                capture_output=True, timeout=timeout,
            ).stdout.decode("utf-8", "replace")
        except Exception as exc:
            return None, "pdftotext failed: %s" % type(exc).__name__
        finally:
            os.unlink(pdf_path)
    else:
        text = body.decode("utf-8", "replace")
        if "html" in ctype or "<html" in text[:2000].lower():
            text = html_to_text(text)

    os.makedirs(cache_dir, exist_ok=True)
    with open(cached, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text, None


# ---------------------------------------------------------------- matching

FOLD = {
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "–": "-", "—": "-", "−": "-", " ": " ",
}


def fold(s):
    s = unicodedata.normalize("NFKC", s)
    for a, b in FOLD.items():
        s = s.replace(a, b)
    return s


def match(fragment, page):
    """EXACT > NORMALIZED > None. Whitespace-stripped comparison is the CJK
    rung: HTML extraction breaks Japanese sentences across lines."""
    if fragment in page:
        return "EXACT"
    f_folded, p_folded = fold(fragment), fold(page)
    if f_folded in p_folded:
        return "NORMALIZED"
    f_ws = re.sub(r"\s+", " ", f_folded).strip()
    p_ws = re.sub(r"\s+", " ", p_folded)
    if f_ws and f_ws in p_ws:
        return "NORMALIZED"
    f_none = re.sub(r"\s+", "", f_folded)
    p_none = re.sub(r"\s+", "", p_folded)
    if f_none and f_none in p_none:
        return "NORMALIZED"
    # Case-only difference: usually a sentence-initial letter lowercased when
    # eliding. Real, but a ledger fix, not a fabrication - so NORMALIZED.
    if f_ws and f_ws.casefold() in p_ws.casefold():
        return "NORMALIZED"
    if f_none and f_none.casefold() in p_none.casefold():
        return "NORMALIZED"
    return None


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(add_help=True, description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--local", action="append", default=[], metavar="S-ID=path")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--min-fragment", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    try:
        with open(args.report, encoding="utf-8") as fh:
            report = fh.read()
    except OSError as exc:
        print("cannot read report: %s" % exc, file=sys.stderr)
        return 3

    sources, claims = parse_report(report)
    if not claims:
        print("no Claim Ledger rows (C-nn) found in %s" % args.report, file=sys.stderr)
        return 3

    local = {}
    for item in args.local:
        if "=" not in item:
            print("--local expects S-ID=path, got %r" % item, file=sys.stderr)
            return 3
        sid, path = item.split("=", 1)
        local[sid.strip()] = path.strip()

    cache_dir = args.cache_dir or os.path.join(tempfile.gettempdir(), "span-check-cache")
    os.makedirs(cache_dir, exist_ok=True)

    pages, results = {}, []

    def page_for(sid):
        if sid in pages:
            return pages[sid]
        if sid in local:
            try:
                with open(local[sid], encoding="utf-8", errors="replace") as fh:
                    raw = fh.read()
                text = html_to_text(raw) if "<html" in raw[:2000].lower() else raw
                pages[sid] = (text, None)
            except OSError as exc:
                pages[sid] = (None, "local file: %s" % exc)
            return pages[sid]
        url = sources.get(sid, {}).get("url", "")
        if not url:
            pages[sid] = (None, "no URL in Source Register")
        else:
            pages[sid] = fetch(url, args.timeout, cache_dir)
        return pages[sid]

    for claim in claims:
        spans = extract_spans(claim["span_cell"])
        if not spans:
            continue
        # A claim with N sources and N spans pairs them in order; otherwise
        # every span is checked against every cited source (first hit wins).
        pairs = (
            list(zip(claim["sources"], spans))
            if len(spans) == len(claim["sources"])
            else [(sid, sp) for sp in spans for sid in claim["sources"]]
        )
        seen = set()
        for sid, span in pairs:
            if (claim["id"], span) in seen:
                continue
            text, err = page_for(sid)
            if text is None:
                verdict, detail = "UNREACHABLE", err
            else:
                frags = fragments(span, args.min_fragment)
                verdicts = [match(f, text) for f in frags]
                if all(v == "EXACT" for v in verdicts):
                    verdict, detail = "EXACT", ""
                elif all(v for v in verdicts):
                    verdict, detail = "NORMALIZED", "matched after folding"
                else:
                    missing = [f for f, v in zip(frags, verdicts) if not v]
                    verdict = "NOT-FOUND"
                    detail = "missing: " + " | ".join(m[:60] for m in missing)
            if verdict != "NOT-FOUND":
                seen.add((claim["id"], span))
            results.append({
                "claim": claim["id"], "source": sid,
                "url": sources.get(sid, {}).get("url", ""),
                "span": span, "verdict": verdict, "detail": detail,
            })
        # de-duplicate the cross-product case: one hit is enough
        hits = {r["span"] for r in results
                if r["claim"] == claim["id"] and r["verdict"] in ("EXACT", "NORMALIZED")}
        results[:] = [r for r in results
                      if not (r["claim"] == claim["id"] and r["verdict"] == "NOT-FOUND"
                              and r["span"] in hits)]

    # Body quotes: what the reader actually sees. Checked against the page, and
    # against the ledger span they are supposed to have been copied from.
    all_spans = {}
    for claim in claims:
        for sp in extract_spans(claim["span_cell"]):
            for sid in claim["sources"]:
                all_spans.setdefault(sid, []).append(sp)
    for bq in parse_body_quotes(report):
        text, err = page_for(bq["source"])
        if text is None:
            verdict, detail = "UNREACHABLE", err
        else:
            frags = fragments(bq["quote"], args.min_fragment)
            verdicts = [match(f, text) for f in frags]
            if all(v == "EXACT" for v in verdicts):
                verdict, detail = "EXACT", ""
            elif all(v for v in verdicts):
                verdict, detail = "NORMALIZED", "matched after folding"
            else:
                missing = [f for f, v in zip(frags, verdicts) if not v]
                verdict = "NOT-FOUND"
                detail = "missing: " + " | ".join(m[:60] for m in missing)
        q = re.sub(r"\s+", " ", fold(bq["quote"])).strip()
        if not any(q in re.sub(r"\s+", " ", fold(s)) for s in all_spans.get(bq["source"], [])):
            detail = (detail + "; " if detail else "") + "not copied from any ledger span"
            if verdict == "EXACT":
                verdict = "NORMALIZED"
        results.append({"claim": "body", "source": bq["source"],
                        "url": sources.get(bq["source"], {}).get("url", ""),
                        "span": bq["quote"], "verdict": verdict, "detail": detail})

    not_found = [r for r in results if r["verdict"] == "NOT-FOUND"]
    unreachable = [r for r in results if r["verdict"] == "UNREACHABLE"]

    if args.json:
        print(json.dumps({"results": results,
                          "summary": {"total": len(results),
                                      "not_found": len(not_found),
                                      "unreachable": len(unreachable)}},
                         ensure_ascii=False, indent=2))
    else:
        shown = [r for r in results if not (args.quiet and r["verdict"] == "EXACT")]
        print("| Claim | Source | Verdict | Span (first 60) | Detail |")
        print("|---|---|---|---|---|")
        for r in shown:
            span = r["span"][:60].replace("|", "\\|")
            detail = r["detail"][:80].replace("|", "\\|")
            print("| %s | %s | %s | %s | %s |" % (r["claim"], r["source"],
                                                  r["verdict"], span, detail))
        print("\n%d spans checked - %d NOT-FOUND, %d UNREACHABLE"
              % (len(results), len(not_found), len(unreachable)))

    if not_found:
        return 1
    if unreachable:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
