#!/usr/bin/env python3
"""
distill_scan.py — mechanical cruft-candidate scanner for essence-distiller.

Flags CANDIDATES for subtraction only; never edits, never decides. Every hit must
be judged against the essence test and the invariants in SKILL.md (anchor to a
stated purpose, Chesterton's Fence, preserve behavior). Works on Markdown / plain
text / lightweight spec docs in Japanese, English, or mixed. No dependencies; 3.8+.

Usage:
    python3 distill_scan.py FILE            # human-readable report
    python3 distill_scan.py FILE --json     # machine-readable JSON

What it surfaces (each maps to a cruft category in SKILL.md):
    - filler / hedging phrases            (filler)
    - speculative-generality markers      (speculative generality / gold-plating)
    - near-duplicate sentences            (redundancy)
    - very long sentences                 (premature / wrong-altitude detail candidate)

This scanner is deliberately conservative: it points, it does not prune. The point
of the skill is a *judged* subtraction, not a regex delete.
"""
import sys
import re
import json
from collections import Counter

MIN_SENT_CHARS = 12
NGRAM_N = 3
DUP_SIM = 0.42          # redundancy: char-trigram Jaccard threshold
LONG_SENT_CHARS = 140   # over-long sentence (detail-dump candidate)

# Filler / hedging — words that usually do not change meaning.
FILLER = [
    # English
    "it is worth noting that", "it should be noted that", "it is important to note",
    "in order to", "the fact that", "at the end of the day", "needless to say",
    "basically", "essentially", "actually", "really", "very", "quite", "just",
    "in conclusion", "as mentioned", "as we can see", "of course", "obviously",
    # Japanese
    "言うまでもなく", "なお", "ちなみに", "基本的に", "実際のところ", "そもそも",
    "というのも", "ある意味", "いわゆる", "とても", "非常に", "かなり", "まさに",
]

# Hedges — reflexive qualifiers that soften without informing.
HEDGE = [
    "perhaps", "maybe", "possibly", "arguably", "somewhat", "relatively",
    "i think", "i believe", "it seems", "kind of", "sort of",
    "かもしれない", "と思われる", "と考えられる", "ように思う", "おそらく",
    "多少", "やや", "一応", "たぶん", "だろう",
]

# Speculative generality / gold-plating markers — future-proofing with no present need.
SPECULATIVE = [
    "in the future", "for now", "for future", "future-proof", "just in case",
    "to be safe", "might need", "may need", "could be extended", "extensible",
    "configurable", "pluggable", "for flexibility", "would be nice", "nice to have",
    "todo", "fixme", "eventually", "down the road",
    "将来的に", "今後", "念のため", "拡張できるように", "柔軟に", "できるように",
    "対応できるよう", "あると良い", "あれば良い", "いつか", "とりあえず",
]

def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)

def get_paragraphs(text):
    text = strip_code(text)
    # Drop heading LINES (not whole blocks) so body text glued to a heading with
    # no blank line in between is still analyzed. Also drop list markers' bullets.
    text = re.sub(r"^\s{0,3}#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    out = []
    for b in re.split(r"\n\s*\n", text):
        b = re.sub(r"^\s*[-*+]\s+", "", b, flags=re.MULTILINE).strip()
        if b:
            out.append(b)
    return out

def split_sentences(block):
    block = re.sub(r"\s+", " ", block).strip()
    parts = re.split(r"(?<=[。！？!?])\s*|(?<=[.!?])\s+", block)
    return [p.strip() for p in parts if p and len(p.strip()) >= MIN_SENT_CHARS]

def normalize(s):
    s = s.lower()
    s = re.sub(r"[\s　]", "", s)
    s = re.sub(r"[、。，．,.\-—–_:;：；！？!?\"'“”‘’()（）\[\]「」『』【】]", "", s)
    return s

def char_ngrams(s, n=NGRAM_N):
    s = normalize(s)
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def find_phrases(text, phrases):
    low = strip_code(text).lower()
    hits = Counter()
    for p in phrases:
        n = low.count(p)
        if n:
            hits[p] = n
    return hits

def detect_duplicates(sentences):
    grams = [(s, char_ngrams(s)) for s in sentences]
    pairs = []
    for i in range(len(grams)):
        for j in range(i + 1, len(grams)):
            sim = jaccard(grams[i][1], grams[j][1])
            if sim >= DUP_SIM:
                pairs.append({"similarity": round(sim, 2),
                              "a": grams[i][0], "b": grams[j][0]})
    pairs.sort(key=lambda p: p["similarity"], reverse=True)
    return pairs

def detect_long_sentences(sentences):
    out = []
    for s in sentences:
        n = len(re.sub(r"\s", "", s))
        if n >= LONG_SENT_CHARS:
            out.append({"chars": n, "preview": s[:70] + "…"})
    out.sort(key=lambda x: x["chars"], reverse=True)
    return out

def build_report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    paras = get_paragraphs(text)
    sentences = [s for p in paras for s in split_sentences(p)]
    return {
        "file": path,
        "counts": {"paragraphs": len(paras), "sentences": len(sentences)},
        "filler": dict(find_phrases(text, FILLER).most_common()),
        "hedging": dict(find_phrases(text, HEDGE).most_common()),
        "speculative": dict(find_phrases(text, SPECULATIVE).most_common()),
        "redundancy": detect_duplicates(sentences),
        "long_sentences": detect_long_sentences(sentences),
    }

def print_human(r):
    def hr(t): print("\n" + t + "\n" + "-" * len(t))
    print(f"distill_scan.py — {r['file']}")
    c = r["counts"]
    print(f"paragraphs={c['paragraphs']}  sentences={c['sentences']}")

    hr("Filler / hedging (category: filler) — trim to the core clause")
    fh = {**r["filler"], **r["hedging"]}
    print("  " + (", ".join(f"«{k}»×{v}" for k, v in fh.items()) or "none"))

    hr("Speculative-generality markers (category: speculative generality / gold-plating)")
    print("  " + (", ".join(f"«{k}»×{v}" for k, v in r["speculative"].items()) or "none"))

    hr(f"Near-duplicate sentences (category: redundancy, Jaccard >= {DUP_SIM})")
    if r["redundancy"]:
        for p in r["redundancy"][:20]:
            print(f"  [{p['similarity']}]  A: {p['a'][:70]}")
            print(f"          B: {p['b'][:70]}")
    else:
        print("  none")

    hr(f"Very long sentences (>= {LONG_SENT_CHARS} chars) — detail-dump candidates")
    print("\n".join(f"  ({s['chars']}) {s['preview']}" for s in r["long_sentences"])
          or "  none")

    print("\nNote: every item is a CANDIDATE, not a verdict. Anchor to the stated "
          "purpose, respect Chesterton's Fence, and preserve behavior before cutting.")

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
