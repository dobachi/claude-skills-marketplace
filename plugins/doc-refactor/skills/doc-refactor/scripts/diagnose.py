#!/usr/bin/env python3
"""
diagnose.py — mechanical, dependency-free diagnostics for doc-refactor.

Flags CANDIDATES only; never edits. A human/Claude confirms or rejects each item
against the refactoring invariants. Works for Japanese, English, and mixed Markdown.

Usage:
    python3 diagnose.py DOCUMENT.md            # human-readable report
    python3 diagnose.py DOCUMENT.md --json     # machine-readable JSON

Detections:
    - heading skeleton + hierarchy jumps (e.g. H2 -> H4)
    - near-duplicate sentence pairs (character n-gram Jaccard)
    - sentence-initial connective frequency (cosmetic-transition overuse)
    - over-long paragraphs (split candidates)
    - most-repeated terms (terminology-drift spotting)

No third-party dependencies; Python 3.8+.
"""
import sys
import re
import json
from collections import Counter

# ---- tunables ----------------------------------------------------------------
# Jaccard over char n-grams. Two bands so we can surface more candidates without
# flooding the strong list: STRONG is calibrated to catch reworded restatements
# (e.g. "相互運用性が向上する" vs "相互運用性が高まる" ~0.46) while staying above the
# shared-vocabulary noise floor; WEAK surfaces looser echoes for a quick human scan.
DUP_STRONG = 0.40
DUP_WEAK = 0.30
WEAK_MAX = 8                 # cap weak-band pairs shown, to avoid flooding
NGRAM_N = 3
LONG_PARA_CHARS = 600        # paragraph length (chars) that suggests a Split
MIN_SENT_CHARS = 12          # ignore very short fragments in dup detection
TOP_TERMS = 15

CONNECTIVES = [
    # Japanese sentence-initial connectives that are often cosmetic
    "また", "さらに", "加えて", "その上", "なお", "そして", "しかし", "したがって",
    "そのため", "一方", "つまり", "このように", "こうした", "そこで",
    # English
    "furthermore", "moreover", "in addition", "additionally", "however",
    "therefore", "thus", "consequently", "on the other hand", "in conclusion",
    "as a result", "that said", "importantly", "notably",
]

# ---- parsing -----------------------------------------------------------------
def strip_code_blocks(text):
    """Remove fenced code blocks so code is never analyzed as prose."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)

def get_headings(text):
    heads = []
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
            heads.append({"line": i, "level": len(m.group(1)), "text": m.group(2)})
    return heads

def get_paragraphs(text):
    text = strip_code_blocks(text)
    # drop headings, list markers kept (list padding still worth flagging as long para)
    blocks = re.split(r"\n\s*\n", text)
    paras = []
    for b in blocks:
        b = b.strip()
        if not b or b.startswith("#"):
            continue
        paras.append(b)
    return paras

def split_sentences(block):
    # Japanese terminators 。！？ and Western . ! ? ; keep it simple and robust.
    block = re.sub(r"\s+", " ", block).strip()
    parts = re.split(r"(?<=[。！？!?])\s*|(?<=[.!?])\s+", block)
    return [p.strip() for p in parts if p and len(p.strip()) >= MIN_SENT_CHARS]

def normalize(s):
    s = s.lower()
    s = re.sub(r"[\s\u3000]", "", s)
    s = re.sub(r"[、。，．,.\-—–_:;：；！？!?\"'“”‘’()（）\[\]「」『』【】]", "", s)
    return s

def char_ngrams(s, n=NGRAM_N):
    s = normalize(s)
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i+n] for i in range(len(s) - n + 1)}

def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

# ---- detections --------------------------------------------------------------
def detect_hierarchy_jumps(heads):
    jumps = []
    prev = None
    for h in heads:
        if prev is not None and h["level"] - prev > 1:
            jumps.append({"line": h["line"], "from": prev, "to": h["level"],
                          "text": h["text"]})
        prev = h["level"]
    return jumps

def detect_duplicates(sentences):
    grams = [(s, char_ngrams(s)) for s in sentences]
    strong, weak = [], []
    for i in range(len(grams)):
        for j in range(i + 1, len(grams)):
            sim = jaccard(grams[i][1], grams[j][1])
            if sim < DUP_WEAK:
                continue
            item = {"similarity": round(sim, 2), "a": grams[i][0], "b": grams[j][0]}
            (strong if sim >= DUP_STRONG else weak).append(item)
    strong.sort(key=lambda p: p["similarity"], reverse=True)
    weak.sort(key=lambda p: p["similarity"], reverse=True)
    return strong, weak[:WEAK_MAX]

def detect_connectives(sentences):
    counts = Counter()
    for s in sentences:
        low = s.lower().lstrip("　 ")
        for c in CONNECTIVES:
            head = s.lstrip("　 ")
            if head.startswith(c) or low.startswith(c):
                counts[c] += 1
                break
    return counts

def detect_long_paras(paras):
    out = []
    for idx, p in enumerate(paras):
        n = len(re.sub(r"\s", "", p))
        if n >= LONG_PARA_CHARS:
            out.append({"index": idx, "chars": n, "preview": p[:60] + "…"})
    return out

def detect_repeated_terms(text):
    text = strip_code_blocks(text)
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    # English words
    en = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text)
    # Japanese katakana runs and kanji runs (rough noun proxy)
    kata = re.findall(r"[\u30A0-\u30FF]{3,}", text)
    kanji = re.findall(r"[\u4E00-\u9FFF]{2,}", text)
    stop = {"this", "that", "with", "from", "which", "their", "these", "those",
            "have", "will", "also", "such", "than", "then", "they", "been",
            "する", "こと", "ため", "よう", "もの"}
    terms = [w.lower() for w in en] + kata + kanji
    counts = Counter(t for t in terms if t not in stop)
    return counts.most_common(TOP_TERMS)

# ---- report ------------------------------------------------------------------
def build_report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    heads = get_headings(text)
    paras = get_paragraphs(text)
    sentences = [s for p in paras for s in split_sentences(p)]
    dup_strong, dup_weak = detect_duplicates(sentences)
    return {
        "file": path,
        "counts": {"headings": len(heads), "paragraphs": len(paras),
                   "sentences": len(sentences)},
        "reverse_outline_skeleton": [
            {"level": h["level"], "heading": h["text"]} for h in heads],
        "hierarchy_jumps": detect_hierarchy_jumps(heads),
        "duplicate_candidates": dup_strong,
        "duplicate_candidates_weak": dup_weak,
        "connective_frequency": dict(detect_connectives(sentences).most_common()),
        "long_paragraphs": detect_long_paras(paras),
        "repeated_terms": detect_repeated_terms(text),
    }

def print_human(r):
    def hr(t): print("\n" + t + "\n" + "-" * len(t))
    print(f"diagnose.py — {r['file']}")
    c = r["counts"]
    print(f"headings={c['headings']}  paragraphs={c['paragraphs']}  "
          f"sentences={c['sentences']}")

    hr("Heading skeleton (fill in one-sentence reality per heading in Pass 1)")
    if r["reverse_outline_skeleton"]:
        for h in r["reverse_outline_skeleton"]:
            print(f"{'  ' * (h['level'] - 1)}H{h['level']}: {h['heading']}")
    else:
        print("(no headings found — the document may need structure, not just cleanup)")

    hr("Heading hierarchy jumps (possible accidental nesting)")
    print("\n".join(f"  line {j['line']}: H{j['from']} -> H{j['to']}  «{j['text']}»"
                    for j in r["hierarchy_jumps"]) or "  none")

    hr(f"Near-duplicate sentences — STRONG (Jaccard >= {DUP_STRONG}) — Merge/Extract candidates")
    if r["duplicate_candidates"]:
        for p in r["duplicate_candidates"][:20]:
            print(f"  [{p['similarity']}]  A: {p['a'][:70]}")
            print(f"          B: {p['b'][:70]}")
    else:
        print("  none")

    hr(f"Near-duplicate sentences — WEAK ({DUP_WEAK} <= Jaccard < {DUP_STRONG}) — looser echoes, scan quickly")
    if r["duplicate_candidates_weak"]:
        for p in r["duplicate_candidates_weak"]:
            print(f"  [{p['similarity']}]  A: {p['a'][:70]}")
            print(f"          B: {p['b'][:70]}")
    else:
        print("  none")

    hr("Sentence-initial connective frequency (watch for cosmetic transitions)")
    print("\n".join(f"  {k}: {v}" for k, v in r["connective_frequency"].items())
          or "  none")

    hr(f"Over-long paragraphs (>= {LONG_PARA_CHARS} chars) — Split candidates")
    print("\n".join(f"  para #{p['index']} ({p['chars']} chars): {p['preview']}"
                    for p in r["long_paragraphs"]) or "  none")

    hr("Most-repeated terms (scan for terminology drift / synonyms of one concept)")
    print("  " + ", ".join(f"{t}×{n}" for t, n in r["repeated_terms"]))

    print("\nNote: every item above is a CANDIDATE. Confirm each against the invariants "
          "(preserve every claim, fact, figure, and the author's voice) before acting.")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    report = build_report(args[0])
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

if __name__ == "__main__":
    main()
