#!/usr/bin/env python3
"""
drift_scan.py — mechanical drift detector for long documents written with an AI.

Long documents fail by drifting, not by being written badly: the register changes
between chapters, a term gets spelled two ways, the same paragraph reappears in a
later section, and the tail thins out. Those failures are boring enough to detect
with string matching, which is exactly why a script should do it — a model asked
to grade its own long draft carries position and self-preference bias (see
references/failure-modes.md).

This scanner REPORTS. It never edits and it cannot see meaning: a flagged
repetition may be a deliberate callback and a short section may be short on
purpose. Every hit is a prompt to look, not a verdict.

Usage:
    python3 drift_scan.py DRAFT.md
    python3 drift_scan.py DRAFT.md --spine DRAFT.spine.md
    python3 drift_scan.py DRAFT.md --json
    python3 drift_scan.py DRAFT.md --only style-mixing,cross-section-dup

Exit codes:
    0  no high/warn findings (info-level findings may still be present)
    1  at least one high or warn finding
    2  usage / read error

No dependencies. Python 3.8+.
"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------- thresholds

JA_SENT_WARN = 60          # 建議: "50〜60字ほどになってきたら読みにくくなっていないか意識する"
JA_SENT_HIGH = 100
EN_SENT_WARN = 40          # words
EN_SENT_HIGH = 60
DUP_SIM = 0.60             # char-trigram Jaccard for cross-section duplication
DUP_MIN_JA_CHARS = 24
DUP_MIN_EN_WORDS = 10
IMBALANCE_LOW = 0.40       # section shorter than 40% of the median
IMBALANCE_HIGH = 2.50      # ... or longer than 250%
IMBALANCE_MIN_SECTIONS = 4
OPENER_MIN_REPEATS = 3
MINORITY_LIST_CAP = 12     # how many minority-register sentences to print

CJK = r"぀-ヿ㐀-䶿一-鿿"
CJK_RE = re.compile(f"[{CJK}]")

# ------------------------------------------------------- register (文体) rules
# Checked in order: 敬体 first, so ました wins over the bare past た.
KEITAI = re.compile(
    r"(です|ます|ません|ました|ましたら|でした|でしょう|ましょう|ください|くださる|ませ|"
    r"ですね|ですが|ますが|ますね)$"
)
JOTAI = re.compile(
    r"(である|であった|であろう|だ|だった|だろう|した|する|しない|しなかった|"
    r"ない|なかった|いる|いた|ある|あった|れる|られる|なる|なった|"
    r"[くきしちにひみりぎじびぴえけせてねへめれげぜでべぺ]た|"
    r"[うくすつぬふむゆるぐずづぶぷ])$"
)

# ------------------------------------------------------------ notation drift
# Pairs that routinely split across chapters of a long Japanese document.
NOTATION_PAIRS = [
    ("サーバー", "サーバ"), ("ユーザー", "ユーザ"), ("コンピューター", "コンピュータ"),
    ("ブラウザー", "ブラウザ"), ("プロバイダー", "プロバイダ"), ("メモリー", "メモリ"),
    ("フォルダー", "フォルダ"), ("ドライバー", "ドライバ"), ("パラメーター", "パラメータ"),
    ("インターフェース", "インタフェース"), ("ディレクトリー", "ディレクトリ"),
    ("行う", "行なう"), ("表す", "表わす"), ("現れる", "現われる"), ("申し込み", "申込み"),
    ("引き続き", "引続き"), ("組み込み", "組込み"), ("問い合わせ", "問合せ"),
    ("できる", "出来る"), ("こと", "事"), ("とき", "時"), ("ください", "下さい"),
    ("ため", "為"), ("または", "又は"), ("さらに", "更に"), ("すでに", "既に"),
    ("email", "e-mail"), ("website", "web site"), ("dataset", "data set"),
]

# --------------------------------------------------- redundancy / 冗長 patterns
# 重言 examples are drawn from 建議「公用文作成の考え方」.
JUGEN = [
    "諸先生方", "各都道府県ごと", "各国ごと", "第1日目", "第１日目", "約", "違和感を感じ",
    "馬から落馬", "頭痛が痛", "まず最初", "今现在", "今現在", "後で後悔", "受注を受け",
    "一番最初", "一番最後", "過半数を超え", "元旦の朝", "電車に乗車", "犯罪を犯",
    "返事を返", "被害を被", "内定が決ま", "断トツ1位", "断トツ一位",
]
JUGEN_CTX = {  # patterns needing a second token nearby to avoid false positives
    "約": ("くらい", "ほど", "程度"),
}
DOUBLE_NEG = [
    "ないわけではない", "なくはない", "ないことはない", "ないとは言えない",
    "なくもない", "ないではない", "ざるを得ない",
]
EN_REDUNDANT = [
    "absolutely essential", "advance planning", "basic fundamentals", "close proximity",
    "end result", "each and every", "free gift", "future plans", "past history",
    "revert back", "unexpected surprise", "very unique", "completely eliminate",
]

OPEN_MARKERS = [
    "[要確認]", "[未確認]", "[要出典]", "[TBD]", "[unverified]", "[To be written]",
    "[執筆中]", "TODO", "TBD", "FIXME", "XXX",
]


# ------------------------------------------------------------------- parsing

def is_ja(text, threshold=0.30):
    """True when the text is predominantly Japanese.

    Presence of a CJK character is not enough: an English sentence citing 文体 or
    引用 is still an English sentence, and scoring it against the 60-character
    Japanese rule produces nonsense. Kana/kanji must carry a real share of it.
    """
    dense = re.sub(r"\s", "", text)
    if not dense:
        return False
    return len(CJK_RE.findall(dense)) / len(dense) >= threshold


def strip_frontmatter(lines):
    """Blank out a leading YAML frontmatter block. It is metadata, not prose."""
    if not lines or lines[0].strip() != "---":
        return lines
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() in ("---", "..."):
            return [""] * (i + 1) + lines[i + 1:]
    return lines


def strip_code_fences(lines):
    """Blank out fenced code blocks so their contents never reach a check."""
    out, in_fence = [], False
    for ln in lines:
        if re.match(r"^\s*(```|~~~)", ln):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else ln)
    return out


def split_sections(lines):
    """Split on ATX headings. Returns [{title, level, start, lines:[(lineno, text)]}]."""
    sections, cur = [], {"title": "(preamble)", "level": 0, "start": 1, "lines": []}
    for i, ln in enumerate(lines, start=1):
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            if cur["lines"] or cur["title"] != "(preamble)":
                sections.append(cur)
            cur = {"title": m.group(2).strip(), "level": len(m.group(1)),
                   "start": i, "lines": []}
        else:
            cur["lines"].append((i, ln))
    sections.append(cur)
    return [s for s in sections if any(t.strip() for _, t in s["lines"])] or sections


def sentences_of(section):
    """Yield (lineno, sentence, kind) where kind is body|list|quote."""
    for lineno, raw in section["lines"]:
        text = raw.strip()
        if not text:
            continue
        kind = "body"
        if re.match(r"^>", text):
            kind = "quote"
        elif text.startswith("|"):
            kind = "table"
        elif re.match(r"^([-*+]|\d+[.)])\s", text):
            kind = "list"
        text = re.sub(r"^>+\s*", "", text)
        text = re.sub(r"^([-*+]|\d+[.)])\s*", "", text)
        text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)   # links/images
        text = re.sub(r"`[^`]*`", "", text)                       # inline code
        text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)  # emphasis
        if not text.strip():
            continue
        if is_ja(text):
            parts = re.split(r"(?<=[。！？])", text)
        else:
            parts = re.split(r"(?<=[.!?])\s+", text)
        for p in parts:
            p = p.strip()
            if p:
                yield lineno, p, kind


def paragraphs_of(section):
    para, start = [], None
    for lineno, raw in section["lines"]:
        if raw.strip():
            if start is None:
                start = lineno
            para.append(raw.strip())
        elif para:
            yield start, " ".join(para)
            para, start = [], None
    if para:
        yield start, " ".join(para)


# -------------------------------------------------------------------- spine

def prose_corpus(lines, drop_tables=True, drop_quotes=True):
    """Text with the parts that legitimately contain variants removed.

    A document that DOCUMENTS a notation choice ("サーバー / サーバ") lists both
    variants on purpose, usually in a table or a quoted style rule. Counting
    those as drift is the scanner's most annoying false positive.
    """
    keep = []
    for ln in lines:
        s = ln.strip()
        if drop_tables and s.startswith("|"):
            continue
        if drop_quotes and s.startswith(">"):
            continue
        keep.append(ln)
    return "\n".join(keep)


def parse_spine(path):
    """Pull the glossary out of a spine file. Returns [(canonical, [banned...])]."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        sys.stderr.write("drift_scan: cannot read spine %s: %s\n" % (path, exc))
        raise SystemExit(2)
    rows, in_gloss = [], False
    for ln in lines:
        if re.match(r"^#{1,6}\s", ln):
            in_gloss = bool(re.search(r"(glossary|用語|語彙)", ln, re.I))
            continue
        if not in_gloss or not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2 or re.match(r"^[-: ]+$", cells[0]):
            continue
        if re.search(r"(canonical|正式|標準)", cells[0], re.I):
            continue
        canonical = cells[0]
        banned = [b.strip() for b in re.split(r"[,、/／]", cells[1]) if b.strip()
                  and b.strip() not in {"-", "—", "–"}]
        if canonical and canonical not in {"-", "—"}:
            rows.append((canonical, banned))
    return rows


# ------------------------------------------------------------------- checks

def finding(check, severity, section, line, message, detail=None):
    f = {"check": check, "severity": severity, "section": section,
         "line": line, "message": message}
    if detail:
        f["detail"] = detail
    return f


def check_style_mixing(sections):
    """建議: 一つの文書内では敬体と常体を混合しない。引用・箇条書きは除外。"""
    out = []
    per_section, doc = {}, Counter()
    for sec in sections:
        counts = Counter()
        hits = defaultdict(list)
        for lineno, sent, kind in sentences_of(sec):
            if kind != "body" or not is_ja(sent):
                continue
            core = re.sub(r"[。！？」』）\)\s]+$", "", sent)
            if not core:
                continue
            if KEITAI.search(core):
                counts["敬体"] += 1
                hits["敬体"].append((lineno, sent))
            elif JOTAI.search(core):
                counts["常体"] += 1
                hits["常体"].append((lineno, sent))
        if counts:
            per_section[sec["title"]] = (counts, hits)
            doc.update(counts)

    if len(doc) < 2 or min(doc.values()) == 0:
        return out

    majority = doc.most_common(1)[0][0]
    minority = "常体" if majority == "敬体" else "敬体"
    out.append(finding(
        "style-mixing", "high", "(document)", None,
        "文体が混在しています: %s %d文 / %s %d文。建議は一文書内での混合を禁じています。"
        % (majority, doc[majority], minority, doc[minority]),
        {"majority": majority, "counts": dict(doc)}))

    listed = 0
    for title, (counts, hits) in per_section.items():
        if counts.get(majority, 0) and counts.get(minority, 0):
            out.append(finding(
                "style-mixing", "high", title, None,
                "同一セクション内で混在: %s %d文 / %s %d文"
                % (majority, counts[majority], minority, counts[minority])))
        for lineno, sent in hits.get(minority, []):
            if listed >= MINORITY_LIST_CAP:
                break
            out.append(finding("style-mixing", "warn", title, lineno,
                               "少数派の文体(%s): %s" % (minority, sent[:70])))
            listed += 1
    return out


def check_long_sentences(sections):
    out = []
    for sec in sections:
        for lineno, sent, kind in sentences_of(sec):
            if kind in ("quote", "table"):
                continue
            if is_ja(sent):
                n = len(re.sub(r"\s", "", sent))
                if n >= JA_SENT_HIGH:
                    out.append(finding("long-sentence", "high", sec["title"], lineno,
                                       "一文 %d字。分割を検討: %s…" % (n, sent[:40])))
                elif n >= JA_SENT_WARN:
                    out.append(finding("long-sentence", "warn", sec["title"], lineno,
                                       "一文 %d字。係り受けが乱れていないか確認: %s…"
                                       % (n, sent[:40])))
            else:
                n = len(sent.split())
                if n >= EN_SENT_HIGH:
                    out.append(finding("long-sentence", "high", sec["title"], lineno,
                                       "Sentence of %d words: %s…" % (n, sent[:60])))
                elif n >= EN_SENT_WARN:
                    out.append(finding("long-sentence", "warn", sec["title"], lineno,
                                       "Sentence of %d words: %s…" % (n, sent[:60])))
    return out


def check_notation_drift(text, sections):
    out = []
    for a, b in NOTATION_PAIRS:
        # Count b only where it is not merely a prefix of a (サーバ inside サーバー).
        na = text.count(a)
        nb = len(re.findall(re.escape(b) + r"(?!ー)", text)) if b + "ー" == a else text.count(b)
        if na and nb:
            out.append(finding(
                "notation-drift", "warn", "(document)", None,
                "表記ゆれ: 「%s」%d件 / 「%s」%d件。スパインの glossary で片方に固定してください。"
                % (a, na, b, nb), {"variants": {a: na, b: nb}}))
    # Generic katakana long-vowel drift not covered by the table above.
    seen = set(a for a, b in NOTATION_PAIRS) | set(b for a, b in NOTATION_PAIRS)
    for token in set(re.findall(r"[ァ-ヶー]{3,}", text)):
        if not token.endswith("ー") or token in seen:
            continue
        base = token[:-1]
        if len(base) < 3 or base in seen:
            continue
        nb = len(re.findall(re.escape(base) + r"(?!ー)", text))
        if nb and text.count(token):
            out.append(finding(
                "notation-drift", "warn", "(document)", None,
                "表記ゆれ(長音): 「%s」%d件 / 「%s」%d件"
                % (token, text.count(token), base, nb)))
    return out


def check_glossary(text, sections, glossary):
    out = []
    for canonical, banned in glossary:
        for bad in banned:
            n = text.count(bad)
            if bad == canonical or not n:
                continue
            if canonical.startswith(bad):   # サーバ inside サーバー
                n = len(re.findall(re.escape(bad) + r"(?!%s)" % re.escape(canonical[len(bad):]), text))
                if not n:
                    continue
            out.append(finding(
                "glossary-violation", "high", "(document)", None,
                "用語集違反: 「%s」が%d件。スパインの canonical は「%s」です。" % (bad, n, canonical),
                {"banned": bad, "canonical": canonical, "count": n}))
        if canonical and canonical not in text:
            out.append(finding(
                "glossary-violation", "info", "(document)", None,
                "用語集の「%s」が本文に一度も現れません（不要な項目か、書き漏れか）。" % canonical))
    return out


def _trigrams(s):
    s = re.sub(r"\s", "", s)
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}


def check_cross_section_dup(sections):
    """Near-duplicate sentences in DIFFERENT sections — the restatement signature."""
    items = []
    for si, sec in enumerate(sections):
        for lineno, sent, kind in sentences_of(sec):
            if kind in ("quote", "table"):
                continue
            if is_ja(sent):
                if len(re.sub(r"\s", "", sent)) < DUP_MIN_JA_CHARS:
                    continue
            elif len(sent.split()) < DUP_MIN_EN_WORDS:
                continue
            items.append({"si": si, "sec": sec["title"], "line": lineno,
                          "text": sent, "tg": _trigrams(sent)})

    index = defaultdict(list)
    for idx, it in enumerate(items):
        for g in it["tg"]:
            index[g].append(idx)

    out, reported = [], set()
    for idx, it in enumerate(items):
        candidates = Counter()
        for g in it["tg"]:
            bucket = index[g]
            if len(bucket) > 40:          # ultra-common trigram, poor signal
                continue
            for j in bucket:
                if items[j]["si"] != it["si"]:
                    candidates[j] += 1
        for j, shared in candidates.items():
            if j < idx or (idx, j) in reported:
                continue
            other = items[j]
            union = len(it["tg"] | other["tg"])
            if not union:
                continue
            if shared / union >= DUP_SIM:
                reported.add((idx, j))
                sev = "high" if shared / union >= 0.85 else "warn"
                out.append(finding(
                    "cross-section-dup", sev, it["sec"], it["line"],
                    "「%s」の記述が「%s」(L%d) とほぼ重複 (類似度 %.2f)"
                    % (it["sec"], other["sec"], other["line"], shared / union),
                    {"a": it["text"][:120], "b": other["text"][:120]}))
    return out


def check_section_balance(sections):
    """Compare sections only against their PEERS at the same heading level.

    A `#` title section and its `##` chapters are not comparable; mixing them
    makes every chapter look like an outlier.
    """
    named = [s for s in sections if s["title"] != "(preamble)"]
    by_level = defaultdict(list)
    for sec in named:
        by_level[sec["level"]].append(sec)
    peers = max(by_level.values(), key=len) if by_level else []
    if len(peers) < IMBALANCE_MIN_SECTIONS:
        return []
    sizes = []
    for sec in peers:
        body = "".join(t for _, t in sec["lines"] if not t.strip().startswith("|"))
        sizes.append((sec["title"], sec["start"], len(re.sub(r"\s", "", body))))
    med = statistics.median([n for _, _, n in sizes]) or 0
    if med == 0:
        return []
    out = []
    for title, start, n in sizes:
        if n < med * IMBALANCE_LOW:
            out.append(finding(
                "section-imbalance", "warn", title, start,
                "本文 %d字。中央値 %d字 の %.0f%%。後半が薄くなる長文の劣化パターンに一致します。"
                % (n, med, 100.0 * n / med)))
        elif n > med * IMBALANCE_HIGH:
            out.append(finding(
                "section-imbalance", "info", title, start,
                "本文 %d字。中央値 %d字 の %.0f%%。分割を検討してください。"
                % (n, med, 100.0 * n / med)))
    return out


def check_redundant(sections):
    out = []
    for sec in sections:
        for lineno, sent, kind in sentences_of(sec):
            if kind in ("quote", "table"):
                continue
            for pat in JUGEN:
                if pat in sent:
                    ctx = JUGEN_CTX.get(pat)
                    if ctx and not any(c in sent for c in ctx):
                        continue
                    out.append(finding("redundant-expression", "warn", sec["title"], lineno,
                                       "重言の疑い「%s」: %s" % (pat, sent[:60])))
            for pat in DOUBLE_NEG:
                if pat in sent:
                    out.append(finding("redundant-expression", "info", sec["title"], lineno,
                                       "二重否定「%s」（強調の意図があれば可）: %s" % (pat, sent[:60])))
            low = sent.lower()
            for pat in EN_REDUNDANT:
                if pat in low:
                    out.append(finding("redundant-expression", "warn", sec["title"], lineno,
                                       "Redundant phrase '%s': %s" % (pat, sent[:60])))
    return out


def check_open_markers(sections):
    out = []
    for sec in sections:
        for lineno, raw in sec["lines"]:
            for marker in OPEN_MARKERS:
                if marker in raw:
                    out.append(finding("open-marker", "info", sec["title"], lineno,
                                       "未解決マーカー %s: %s" % (marker, raw.strip()[:70])))
                    break
    return out


def check_repeated_openers(sections):
    openers = defaultdict(list)
    for sec in sections:
        for start, para in paragraphs_of(sec):
            if para.startswith(("|", ">", "#")) or len(para) < 20:
                continue
            if is_ja(para):
                # Key on the leading connective ("また、" "さらに、" "一方で、"), which is
                # what actually repeats; a fixed-width prefix diverges too early.
                head = re.sub(r"\s", "", para)
                comma = head.find("、")
                key = head[:comma + 1] if 0 < comma <= 8 else head[:6]
                if len(key) < 2:
                    continue
            else:
                key = " ".join(para.split()[:3]).lower()
                if len(key) < 4:
                    continue
            openers[key].append((sec["title"], start))
    out = []
    for key, hits in sorted(openers.items(), key=lambda kv: -len(kv[1])):
        if len(hits) >= OPENER_MIN_REPEATS:
            where = ", ".join("%s:L%d" % (t, l) for t, l in hits[:6])
            out.append(finding("repeated-opener", "info", "(document)", None,
                               "段落の書き出し「%s」が%d回: %s" % (key, len(hits), where)))
    return out


# -------------------------------------------------------------------- driver

CHECKS = ["style-mixing", "long-sentence", "notation-drift", "glossary-violation",
          "cross-section-dup", "section-imbalance", "redundant-expression",
          "open-marker", "repeated-opener"]
SEV_ORDER = {"high": 0, "warn": 1, "info": 2}


def run(path, spine_path=None, only=None):
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        sys.stderr.write("drift_scan: cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)

    lines = strip_code_fences(strip_frontmatter(raw.splitlines()))
    text = "\n".join(lines)
    sections = split_sections(lines)
    glossary = parse_spine(spine_path) if spine_path else []
    enabled = set(only) if only else set(CHECKS)

    findings = []
    if "style-mixing" in enabled:
        findings += check_style_mixing(sections)
    if "long-sentence" in enabled:
        findings += check_long_sentences(sections)
    if "notation-drift" in enabled:
        findings += check_notation_drift(
            prose_corpus(lines, drop_tables=True, drop_quotes=True), sections)
    if "glossary-violation" in enabled and glossary:
        findings += check_glossary(
            prose_corpus(lines, drop_tables=False, drop_quotes=True), sections, glossary)
    if "cross-section-dup" in enabled:
        findings += check_cross_section_dup(sections)
    if "section-imbalance" in enabled:
        findings += check_section_balance(sections)
    if "redundant-expression" in enabled:
        findings += check_redundant(sections)
    if "open-marker" in enabled:
        findings += check_open_markers(sections)
    if "repeated-opener" in enabled:
        findings += check_repeated_openers(sections)

    findings.sort(key=lambda f: (SEV_ORDER[f["severity"]], f["check"], f["line"] or 0))
    stats = {
        "file": path,
        "spine": spine_path,
        "chars": len(re.sub(r"\s", "", text)),
        "sections": len([s for s in sections if s["title"] != "(preamble)"]),
        "glossary_terms": len(glossary),
        "counts": dict(Counter(f["severity"] for f in findings)),
    }
    return findings, stats


def render(findings, stats):
    lines = []
    lines.append("drift_scan: %s" % stats["file"])
    lines.append("  %d chars, %d sections, spine=%s (%d glossary terms)"
                 % (stats["chars"], stats["sections"],
                    stats["spine"] or "none", stats["glossary_terms"]))
    c = stats["counts"]
    lines.append("  findings: high=%d warn=%d info=%d"
                 % (c.get("high", 0), c.get("warn", 0), c.get("info", 0)))
    if not findings:
        lines.append("\n  No drift detected. This is not a quality judgement — "
                     "the scanner cannot see meaning.")
        return "\n".join(lines)
    current = None
    for f in findings:
        if f["severity"] != current:
            current = f["severity"]
            lines.append("")
        loc = f["section"]
        if f["line"]:
            loc += " L%d" % f["line"]
        lines.append("  %-4s [%s] %s — %s"
                     % (f["severity"].upper(), f["check"], loc, f["message"]))
    lines.append("\n  Reported, not decided. A repetition may be a deliberate callback; "
                 "a short section may be short on purpose.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Detect drift in a long AI-assisted document.")
    ap.add_argument("draft", help="Markdown draft to scan")
    ap.add_argument("--spine", help="Spine file, for glossary checks")
    ap.add_argument("--only", help="Comma-separated subset of: " + ",".join(CHECKS))
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    only = None
    if args.only:
        only = [c.strip() for c in args.only.split(",") if c.strip()]
        unknown = [c for c in only if c not in CHECKS]
        if unknown:
            sys.stderr.write("drift_scan: unknown check(s): %s\n" % ", ".join(unknown))
            return 2

    findings, stats = run(args.draft, args.spine, only)
    if args.json:
        print(json.dumps({"stats": stats, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        print(render(findings, stats))
    return 1 if any(f["severity"] in ("high", "warn") for f in findings) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(2)
