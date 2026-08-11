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
    python3 drift_scan.py DRAFT.md --spine DRAFT.spine.md   # + glossary & style contract
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


# ---------------------------------------------------- optional morphological backend
# A fixed-weight tokenizer is deterministic: same input, same output, no sampling,
# no prompt or ordering sensitivity. That is what makes it eligible for a gate,
# where a prompted model is not. It is optional — every check degrades to the
# stdlib path without it, and the header says which path ran.

KEIGO_AUX = {"です", "ます", "まし", "ませ", "ましょ", "ましょう", "ましたら", "でし"}
FINAL_FORMS = ("終止形", "命令形", "意志推量形")

# SudachiPy raises past 49149 UTF-8 bytes. A book-length draft is routinely
# several times that, so the one document class this tool exists for is exactly
# the one a single tokenize() call cannot read. Chunk before handing text over.
SUDACHI_MAX_BYTES = 40000


def _tokenizer_units(text, limit):
    """Text as pieces that are individually under `limit` bytes where possible.

    Lines first, then sentences within an over-long line, then a hard character
    split as the last resort. Nothing is dropped: the pieces re-concatenate to
    the input exactly, so token counts match what one call would have produced.
    """
    for line in text.splitlines(keepends=True):
        if len(line.encode("utf-8")) <= limit:
            yield line
            continue
        buf, buf_bytes = "", 0
        for ch in line:
            cb = len(ch.encode("utf-8"))
            if buf and buf_bytes + cb > limit:
                yield buf
                buf, buf_bytes = "", 0
            buf += ch
            buf_bytes += cb
            if ch == "。":
                yield buf
                buf, buf_bytes = "", 0
        if buf:
            yield buf


def chunk_for_tokenizer(text, limit=SUDACHI_MAX_BYTES):
    """Group units into the fewest chunks that each stay under `limit` bytes."""
    if len(text.encode("utf-8")) <= limit:
        return [text]
    out, buf, buf_bytes = [], [], 0
    for unit in _tokenizer_units(text, limit):
        ub = len(unit.encode("utf-8"))
        if buf and buf_bytes + ub > limit:
            out.append("".join(buf))
            buf, buf_bytes = [], 0
        buf.append(unit)
        buf_bytes += ub
    if buf:
        out.append("".join(buf))
    return out


class Morph:
    """SudachiPy wrapper. `available` is False when the library is absent."""

    def __init__(self):
        self.name = None
        self.version = None
        self._tok = None
        self._mode = None
        try:
            import sudachipy
            from sudachipy import Dictionary, SplitMode
            self._tok = Dictionary().create()
            self._mode = SplitMode.C
            self.name = "sudachipy"
            self.version = getattr(sudachipy, "__version__", "?")
        except Exception:
            self._tok = None

    @property
    def available(self):
        return self._tok is not None

    def tokens(self, text):
        """[(surface, normalized_form, pos, subpos, inflection)].

        Both pos[0] and pos[1] are carried: the register rule keys on the
        coarse class plus the inflection, the notation rule keys on 名詞 +
        普通名詞/固有名詞. Collapsing them silently disables one of the two.

        Chunked before hand-off, because SudachiPy refuses input over 49149
        UTF-8 bytes and whole-draft callers exceed that by design.
        """
        out = []
        for chunk in chunk_for_tokenizer(text):
            for m in self._tok.tokenize(chunk, self._mode):
                pos = m.part_of_speech()
                out.append((m.surface(), m.normalized_form(), pos[0],
                            pos[1] if len(pos) > 1 else "",
                            pos[5] if len(pos) > 5 else ""))
        return out

    def register(self, sent):
        """敬体 / 常体 / None, from POS and inflection rather than a suffix regex.

        Measured against the regex on a 24-sentence battery: 24/24 vs 23/24 —
        it wins only on literary endings like 「…すべし。」. The regex anchors at
        the sentence end, so mid-sentence noise (ますます) never fooled it in the
        first place. Register is NOT why this backend earns its place; notation
        drift is (0/8 -> 6/8 on unlisted variants). Kept because it is free once
        the tokenizer is loaded and the regex still catches what it returns None
        for.
        """
        toks = self.tokens(sent)
        while toks and toks[-1][2] in ("補助記号", "記号"):
            toks.pop()
        if not toks:
            return None
        tail = toks[-3:]
        for surface, _norm, pos, _subpos, _infl in tail:
            if pos == "助動詞" and surface in KEIGO_AUX:
                return "敬体"
            if surface == "ください" and pos in ("動詞", "助動詞"):
                return "敬体"
        surface, _norm, pos, _subpos, infl = toks[-1]
        if pos in ("動詞", "形容詞", "助動詞", "形状詞") and infl.startswith(FINAL_FORMS):
            return "常体"
        if pos in ("動詞", "形容詞", "助動詞") and any(infl.startswith(f) for f in FINAL_FORMS):
            return "常体"
        return None          # 体言止め and anything unclear: missed, never guessed


MORPH = None                 # set once in run(); None means "stdlib path"


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


HEADER_LABELS = {"#", "id", "section", "claim", "claim it must land", "budget",
                 "status", "must not repeat", "source", "definition", "canonical",
                 "never write", "first defined", "章", "節", "主旨", "状態", "出典"}


def _is_header_row(cells):
    """True when two or more cells are column labels rather than data.

    One label can legitimately be a value ("Status" as a term); two in one row
    is a header. Letting the header through made the outline check report a
    missing section called "Section".
    """
    return sum(1 for c in cells if c.strip().lower() in HEADER_LABELS) >= 2


def _contract_value(raw):
    """A style-contract value, or None if the template placeholder is unfilled.

    The shipped template offers alternatives — `である調 | ですます調 | formal EN`.
    A line still carrying two or more of them was never decided, and guessing
    one would invent a rule the author did not write.
    """
    v = raw.strip().strip("`")
    if v in ("", "-", "—", "…", "..."):
        return None
    if len([a for a in v.split("|") if a.strip()]) > 1:
        return None
    if v.startswith("<") and v.endswith(">"):
        return None
    return v


def parse_spine(path):
    """Read a spine file.

    Returns {"glossary": [(canonical, [banned...])], "style": {...},
             "outline": [{"num","title","claim"}], "claims": [{...}],
             "audience": str|None}.

    Glossary and style are enforced as rules. Outline claims, the claim ledger
    and the audience line drive the CONTENT checks — the ones that ask whether
    the draft does what the spine said it would, rather than whether its surface
    is consistent.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        sys.stderr.write("drift_scan: cannot read spine %s: %s\n" % (path, exc))
        raise SystemExit(2)

    rows, style = [], {"register": None, "digits": None,
                       "list_period": None, "banned": []}
    outline, claims, first_defined, audience = [], [], {}, None
    section = None
    for ln in lines:
        if re.match(r"^#{1,6}\s", ln):
            if re.search(r"(glossary|用語|語彙)", ln, re.I):
                section = "glossary"
            elif re.search(r"(style contract|文体契約|スタイル)", ln, re.I):
                section = "style"
            elif re.search(r"(outline|アウトライン|章立て|構成)", ln, re.I):
                section = "outline"
            elif re.search(r"(claims?|主張|クレーム)", ln, re.I):
                section = "claims"
            elif re.search(r"(contract|契約|前提)", ln, re.I):
                section = "contract"
            else:
                section = None
            continue

        if section == "glossary" and ln.strip().startswith("|"):
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
                if len(cells) >= 4 and cells[3] not in {"-", "—", ""}:
                    first_defined[canonical] = cells[3]

        elif section == "outline" and ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 3 or re.match(r"^[-: ]+$", cells[0]):
                continue
            if _is_header_row(cells):
                continue
            claim = cells[2]
            if claim in {"-", "—", "", "..."} or claim.startswith("<"):
                claim = ""
            outline.append({"num": cells[0], "title": cells[1], "claim": claim})

        elif section == "claims" and ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 5 or re.match(r"^[-: ]+$", cells[0]):
                continue
            if _is_header_row(cells):
                continue
            claims.append({"id": cells[0], "claim": cells[1], "section": cells[2],
                           "source": cells[3], "status": cells[4]})

        elif section == "contract":
            m = re.match(r"^\s*[-*+]\s*(.+?)\s*[:：]\s*(.*)$", ln)
            if m and re.search(r"(audience|読者|対象)", m.group(1), re.I):
                val = _contract_value(m.group(2))
                if val:
                    audience = val

        elif section == "style":
            m = re.match(r"^\s*[-*+]\s*(.+?)\s*[:：]\s*(.*)$", ln)
            if not m:
                continue
            key, val = m.group(1), _contract_value(m.group(2))
            if val is None:
                continue
            if re.search(r"(文体|register)", key, re.I):
                if re.search(r"(である調|常体|plain)", val, re.I):
                    style["register"] = "常体"
                elif re.search(r"(ですます調|です・ます|敬体|polite)", val, re.I):
                    style["register"] = "敬体"
            elif re.search(r"(数字|digit|number)", key, re.I):
                # "半角/全角" is the template offering both, not a decision.
                if ("半角" in val) != ("全角" in val):
                    style["digits"] = "半角" if "半角" in val else "全角"
            elif re.search(r"(記号|箇条|list|punctuation)", key, re.I):
                if re.search(r"句点(を付け)?(な|無)し|句点を付けない", val):
                    style["list_period"] = False
                elif re.search(r"句点(を付ける|あり|有り)", val):
                    style["list_period"] = True
            elif re.search(r"(banned|禁止|使わない)", key, re.I):
                items = re.findall(r"[「『]([^」』]+)[」』]", val)
                if not items:
                    items = [p.strip() for p in re.split(r"[,、]", val) if p.strip()]
                style["banned"] = [i for i in items if len(i) >= 2]
    return {"glossary": rows, "style": style, "outline": outline,
            "claims": claims, "first_defined": first_defined,
            "audience": audience}


# ------------------------------------------------------------------- checks

def finding(check, severity, section, line, message, detail=None):
    f = {"check": check, "severity": severity, "section": section,
         "line": line, "message": message}
    if detail:
        f["detail"] = detail
    return f


def classify_register(sent):
    """敬体 / 常体 / None. 敬体 is tested first so ました beats the bare past た.

    Uses the morphological backend when one is loaded and falls back to the
    suffix regex when it returns None, so the backend can only add coverage.

    None means "not classifiable", not "neutral" — the failure direction is a
    missed finding rather than a false alarm, which is the right way round.
    """
    if MORPH is not None and MORPH.available:
        reg = MORPH.register(sent)
        if reg:
            return reg
    core = re.sub(r"[。！？」』）\)\s]+$", "", sent)
    if not core:
        return None
    if KEITAI.search(core):
        return "敬体"
    if JOTAI.search(core):
        return "常体"
    return None


def check_declared_style(sections, prose, style):
    """Check the draft against what the spine's Style contract DECLARED.

    check_style_mixing only sees internal inconsistency: a document written
    uniformly in 敬体 passes it even when the spine says である調. This is the
    check that compares the text to the stated intent.
    """
    out = []
    declared = style.get("register")
    if declared:
        counts, violations = Counter(), []
        for sec in sections:
            for lineno, sent, kind in sentences_of(sec):
                if kind != "body" or not is_ja(sent):
                    continue
                reg = classify_register(sent)
                if not reg:
                    continue
                counts[reg] += 1
                if reg != declared:
                    violations.append((sec["title"], lineno, sent))
        if counts and counts[declared] == 0:
            out.append(finding(
                "declared-style-violation", "high", "(document)", None,
                "スパインの宣言は「%s」ですが、本文に%sの文が1つもありません（%s %d文）。"
                % (declared, declared,
                   "常体" if declared == "敬体" else "敬体",
                   sum(counts.values())),
                {"declared": declared, "counts": dict(counts)}))
        elif violations:
            out.append(finding(
                "declared-style-violation", "high", "(document)", None,
                "スパインの宣言は「%s」ですが、%d文が宣言と異なります（%s %d文 / 全%d文）。"
                % (declared, len(violations),
                   "常体" if declared == "敬体" else "敬体",
                   len(violations), sum(counts.values())),
                {"declared": declared, "counts": dict(counts)}))
        for title, lineno, sent in violations[:MINORITY_LIST_CAP]:
            out.append(finding("declared-style-violation", "warn", title, lineno,
                               "宣言(%s)と異なる文末: %s" % (declared, sent[:70])))

    if style.get("digits"):
        want = style["digits"]
        pat, name = (r"[０-９]", "全角") if want == "半角" else (r"(?<![\w.])[0-9]", "半角")
        hits = len(re.findall(pat, prose))
        if hits:
            out.append(finding(
                "declared-style-violation", "warn", "(document)", None,
                "数字は「%s」と宣言されていますが、%sの数字が%d件あります。"
                % (want, name, hits), {"declared": want, "count": hits}))

    if style.get("list_period") is not None:
        want = style["list_period"]
        bad = []
        for sec in sections:
            for lineno, sent, kind in sentences_of(sec):
                if kind != "list" or not is_ja(sent):
                    continue
                ends = sent.rstrip().endswith("。")
                if ends != want:
                    bad.append((sec["title"], lineno))
        if bad:
            out.append(finding(
                "declared-style-violation", "warn", "(document)", None,
                "箇条書きの句点は「%s」と宣言されていますが、%d行が異なります（例 %s L%d）。"
                % ("あり" if want else "なし", len(bad), bad[0][0], bad[0][1]),
                {"declared_period": want, "count": len(bad)}))

    for phrase in style.get("banned", []):
        n = prose.count(phrase)
        if n:
            out.append(finding(
                "declared-style-violation", "high", "(document)", None,
                "スパインで禁止された表現「%s」が%d件あります。" % (phrase, n),
                {"banned": phrase, "count": n}))
    return out


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
            reg = classify_register(sent)
            if reg:
                counts[reg] += 1
                hits[reg].append((lineno, sent))
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

    # With a morphological backend, drift is found by grouping surface forms
    # under their dictionary-normalized form — no hand-maintained pair table,
    # so it catches variants the table above never listed.
    #
    # Normalized_form is a dictionary lemma, so it folds three things that are
    # NOT notation drift, and each needs an explicit filter. Measured on real
    # documents, the unfiltered version produced 31/12/41 findings that were
    # almost entirely these:
    #   conjugation   書け/書か/書い -> 書く      => nouns only
    #   letter case   is/IS, plugin/Plugin       => ASCII must differ beyond case
    #   translation   スタイル/style              => variants must share a script
    # A fourth guard (character overlap) catches synonym folding not seen here.
    if MORPH is not None and MORPH.available:
        by_norm = defaultdict(Counter)
        for surface, norm, pos, subpos, _infl in MORPH.tokens(text):
            if pos != "名詞" or subpos not in ("普通名詞", "固有名詞"):
                continue
            if len(surface) < 2:
                continue
            by_norm[norm][surface] += 1
        for norm, variants in sorted(by_norm.items()):
            forms = [s for s, _ in variants.most_common()]
            if len(forms) < 2:
                continue
            fset = set(forms)
            # Skip only a pair the table already reports, not every group that
            # happens to touch a tabled word: インターフェイス/インターフェース is a
            # different pair from the table's インターフェース/インタフェース.
            if any(a in fset and b in fset for a, b in NOTATION_PAIRS):
                continue
            if len({_script_class(f) for f in forms}) > 1:
                continue                          # 和英ペア: not a notation choice
            # The lemma must be written in the same script as the surfaces.
            # reading/leading both normalize to リーディング — that is Sudachi
            # translating, not folding a spelling, and it is a false positive.
            if any(_script_class(norm) != _script_class(f) for f in forms):
                continue
            if all(_script_class(f) == "ascii" for f in forms):
                if len({f.lower() for f in forms}) < 2:
                    continue                      # case only: not notation drift
            if not _mutually_similar(forms):
                continue                          # unrelated synonyms folded together
            listed = " / ".join("「%s」%d件" % (s, n) for s, n in variants.most_common())
            out.append(finding(
                "notation-drift", "warn", "(document)", None,
                "表記ゆれ(正規化形「%s」): %s" % (norm, listed),
                {"normalized": norm, "variants": dict(variants)}))
    return out


def _script_class(s):
    if re.fullmatch(r"[A-Za-z0-9._+-]+", s):
        return "ascii"
    if re.fullmatch(r"[ァ-ヶー・]+", s):
        return "kana"
    return "ja"


def _mutually_similar(forms, threshold=0.5):
    """Every pair of variants must share at least half their characters.

    A dictionary lemma can fold genuine synonyms, not just spellings. Requiring
    surface overlap keeps 見積り/見積もり and ヴァイオリン/バイオリン while dropping
    anything that merely means the same thing.
    """
    for i, a in enumerate(forms):
        for b in forms[i + 1:]:
            sa, sb = set(a), set(b)
            if not sa | sb:
                return False
            if len(sa & sb) / len(sa | sb) < threshold:
                return False
    return True


# Units that mean the same thing, folded before comparison.
UNIT_ALIASES = {
    "msec": "ms", "ミリ秒": "ms", "ミリセカンド": "ms",
    "秒": "s", "sec": "s", "seconds": "s", "second": "s",
    "分": "min", "minutes": "min", "minute": "min",
    "時間": "h", "hours": "h", "hour": "h",
    "％": "%", "パーセント": "%", "percent": "%",
    "文字": "字", "chars": "字", "characters": "字", "character": "字",
    "words": "語", "word": "語", "ワード": "語",
    "tokens": "token", "トークン": "token",
    "円": "JPY", "ドル": "USD", "usd": "USD",
    "人": "人", "件": "件", "回": "回", "倍": "倍", "個": "個",
}
UNIT_RE = (r"(?:ms|msec|ミリ秒|秒|sec|seconds?|分|minutes?|時間|hours?|日|週間|"
           r"ヶ月|か月|年|%|％|パーセント|percent|円|ドル|USD|usd|GB|MB|KB|TB|"
           r"件|人|回|倍|個|字|文字|chars?|characters?|語|words?|ワード|"
           r"トークン|tokens?)")
FULLWIDTH = str.maketrans("０１２３４５６７８９．％", "0123456789.%")
LABEL_STOP = {"これ", "それ", "この", "その", "以下", "以上", "次", "上記", "下記",
              "例", "図", "表", "計", "合計", "うち", "本書", "本章", "など",
              "the", "a", "an", "of", "is", "was", "are", "were", "to", "at",
              "in", "on", "for", "and", "or", "about", "than", "over", "under"}


def _measure_label(text, start, japanese):
    """The noun phrase a measurement is attached to, taken from what precedes it."""
    win = text[max(0, start - 26):start]
    if japanese:
        parts = [p for p in re.split(r"[。、（）()「」『』\[\]|:：=＝\s]+", win) if p]
        if not parts:
            return ""
        label = parts[-1]
        label = re.sub(r"(は|が|を|に|で|と|の|も|へ|より|から|まで)$", "", label)
        label = re.sub(r"(約|およそ|最大|最小|平均|合計|計|およそ)$", "", label)
        return label.strip()
    words = re.split(r"[\s(),:;=\[\]|]+", win)
    words = [w for w in words if w]
    while words and words[-1].lower() in LABEL_STOP:
        words.pop()
    return " ".join(words[-3:]).strip().lower()


def check_numeric_inconsistency(sections):
    """The same labelled quantity given two different values in two sections.

    A content check that needs no meaning: §2 saying 200ms and §7 saying 500ms
    for the same thing is an inconsistency whatever the sentences around it say.
    Tables and quotes are excluded — tabulating different values is their job.
    """
    pat = re.compile(r"([0-9０-９]+(?:[.．][0-9０-９]+)?)\s*(" + UNIT_RE + r")")
    seen = defaultdict(list)          # (label, unit) -> [(value, section, line)]
    for sec in sections:
        for lineno, sent, kind in sentences_of(sec):
            if kind in ("table", "quote"):
                continue
            japanese = is_ja(sent)
            for m in pat.finditer(sent):
                raw_val, raw_unit = m.group(1), m.group(2)
                value = raw_val.translate(FULLWIDTH)
                unit = UNIT_ALIASES.get(raw_unit.lower(), UNIT_ALIASES.get(raw_unit, raw_unit))
                label = _measure_label(sent, m.start(), japanese)
                if len(label) < 2 or label.lower() in LABEL_STOP:
                    continue
                if re.fullmatch(r"[0-9０-９.．,、]+", label):
                    continue
                seen[(label, unit)].append((value, sec["title"], lineno))

    out = []
    for (label, unit), hits in sorted(seen.items()):
        values = {v for v, _, _ in hits}
        sects = {s for _, s, _ in hits}
        if len(values) < 2 or len(sects) < 2:
            continue
        where = " / ".join("%s%s (%s L%d)" % (v, unit, s, l) for v, s, l in hits[:6])
        out.append(finding(
            "numeric-inconsistency", "high", "(document)", hits[0][2],
            "「%s」の数値が章をまたいで食い違っています: %s" % (label, where),
            {"label": label, "unit": unit, "values": sorted(values)}))
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



# ------------------------------------------------------- content / context
# These ask a different question from every check above. The surface checks ask
# "is the draft internally consistent?"; these ask "does the draft do what the
# spine said it would?" — which is why they need the spine and report nothing
# without one. None of them judges meaning: they check whether the words the
# claim is about are even present, whether the ledger still says unverified,
# whether a term is used before it is defined. A section can mention every term
# in its claim and still fail to land it; that judgement is the human's, and
# `references/content-review.md` is the procedure for it.

# Markers that assert EVIDENCE, not markers that sound strong. Measured on seven
# real documents, the obvious list ("必ず", "常に", "always", "never") fired 13
# times and every hit was a prescriptive rule — "never parallel", "必ず確認する
# こと" — which needs no source. A rule is not a claim. Narrowed to phrases that
# assert something was established about the world: zero false positives on the
# same seven documents.
STRONG_JA = ["証明されている", "実証されている", "実証された", "例外なく",
             "疑いの余地は", "統計的に有意", "研究によれば", "調査によれば",
             "明らかになった", "確立されている"]
STRONG_EN = ["proven", "undoubtedly", "definitively", "without exception",
             "studies show", "research shows", "it is established that",
             "demonstrably", "guarantees that"]
CITE_MARKERS = ["http://", "https://", "doi:", "出典", "参照", "引用", "注)", "脚注",
                "[^", "et al", "参考文献"]


def content_terms(text, limit=12):
    """The words a claim is *about*, for presence testing. Not meaning."""
    if MORPH is not None and MORPH.available and is_ja(text):
        terms = [s for s, _n, pos, sub, _i in MORPH.tokens(text)
                 if pos == "名詞" and sub in ("普通名詞", "固有名詞") and len(s) >= 2]
    else:
        terms = (re.findall(r"[一-龥]{2,}", text)
                 + re.findall(r"[ァ-ヶー]{3,}", text)
                 + re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text))
    seen, out = set(), []
    for w in terms:
        k = w.lower()
        if k in seen or k in LABEL_STOP:
            continue
        seen.add(k)
        out.append(w)
    return out[:limit]


def _norm_title(s):
    s = re.sub(r"\s+", "", s or "")
    s = re.sub(r"^(第?\d+[章節話]|§\d+|\d+[.)]|Chapter\s*\d+)", "", s, flags=re.I)
    return s


def _section_index(sections, ref):
    """Index of the document section an outline row / '§3' reference points at."""
    if not ref:
        return None
    named = [(i, s) for i, s in enumerate(sections) if s["title"] != "(preamble)"]
    ref_n = _norm_title(ref)
    for i, s in named:                                   # exact, then substring
        if ref_n and _norm_title(s["title"]) == ref_n:
            return i
    for i, s in named:
        if ref_n and (ref_n in _norm_title(s["title"]) or _norm_title(s["title"]) in ref_n):
            return i
    m = re.search(r"\d+", str(ref))                      # fall back to the number
    if m:
        want = m.group(0)
        for i, s in named:
            if re.search(r"(?<!\d)%s(?!\d)" % want, s["title"]):
                return i
    return None


def _section_body(sec):
    return "\n".join(txt for _ln, txt in sec["lines"])


def check_claim_coverage(sections, outline):
    """Does each section even mention what its outline claim is about?

    Absence is strong: a section that never names the claim's subject is not
    landing it. Presence proves nothing, which is why a pass here is not a pass.
    """
    out = []
    for entry in outline:
        claim = entry.get("claim")
        if not claim:
            continue
        idx = _section_index(sections, entry.get("title")) 
        if idx is None:
            idx = _section_index(sections, entry.get("num"))
        if idx is None:
            out.append(finding(
                "claim-coverage", "warn", entry.get("title") or entry.get("num"), None,
                "スパインのアウトライン「%s」に対応する見出しが本文に見つかりません。"
                % (entry.get("title") or entry.get("num"))))
            continue
        terms = content_terms(claim)
        if not terms:
            continue
        body = _section_body(sections[idx])
        missing = [w for w in terms if w not in body]
        hit = len(terms) - len(missing)
        title = sections[idx]["title"]
        if hit == 0:
            out.append(finding(
                "claim-coverage", "high", title, sections[idx]["start"],
                "この章が述べるはずの主旨「%s」の語が本文に1つも現れません。" % claim[:50],
                {"claim": claim, "missing": missing}))
        elif hit / len(terms) < 0.5:
            out.append(finding(
                "claim-coverage", "warn", title, sections[idx]["start"],
                "主旨「%s」の主要語のうち %d/%d が本文にありません（%s）。"
                % (claim[:40], len(missing), len(terms), "、".join(missing[:5])),
                {"claim": claim, "missing": missing}))
    return out


def check_unverified_claims(claims):
    """The spine's own claim ledger, surfaced as the human's review list."""
    out = []
    # Exact membership, not substring: "unverified" contains "verified", and a
    # substring test silently marked every open claim as done.
    ok = {"verified", "検証済", "検証済み", "確認済", "確認済み", "済", "done", "ok", "yes"}
    for row in claims:
        status = (row.get("status") or "").strip().lower()
        if status in ok:
            continue
        out.append(finding(
            "unverified-claim", "info", row.get("section") or "(document)", None,
            "未検証の主張 %s「%s」（出典: %s / 状態: %s）"
            % (row.get("id"), (row.get("claim") or "")[:50],
               row.get("source") or "—", row.get("status") or "—"),
            {"id": row.get("id"), "section": row.get("section")}))
    return out


def check_term_before_definition(sections, first_defined):
    """A glossary term used before the section the spine says defines it.

    The reader meets the word before its definition — an audience-assumption
    failure that no surface check sees.
    """
    out = []
    for term, where in first_defined.items():
        declared = _section_index(sections, where)
        if declared is None:
            continue
        for i, sec in enumerate(sections):
            if sec["title"] == "(preamble)" or i >= declared:
                continue
            if term in _section_body(sec):
                out.append(finding(
                    "term-before-definition", "warn", sec["title"], sec["start"],
                    "用語「%s」は %s で定義される予定ですが、それより前のこの章で使われています。"
                    % (term, where), {"term": term, "declared": where}))
                break
    return out


def check_unsourced_assertion(sections):
    """Absolute assertions with no citation and no [要確認] beside them."""
    out = []
    for sec in sections:
        for lineno, sent, kind in sentences_of(sec):
            if kind in ("table", "quote"):
                continue
            low = sent.lower()
            markers = [m for m in STRONG_JA if m in sent]
            markers += [m for m in STRONG_EN if m in low]
            if not markers:
                continue
            if any(c in sent or c in low for c in CITE_MARKERS):
                continue
            if any(m in sent for m in OPEN_MARKERS):
                continue
            out.append(finding(
                "unsourced-assertion", "info", sec["title"], lineno,
                "断定「%s」に出典も [要確認] もありません: %s"
                % (markers[0], sent[:60]), {"marker": markers[0]}))
    return out


# -------------------------------------------------------------------- driver

CHECKS = ["claim-coverage", "unverified-claim", "term-before-definition",
          "unsourced-assertion",
          "style-mixing", "declared-style-violation", "long-sentence",
          "notation-drift", "glossary-violation", "numeric-inconsistency",
          "cross-section-dup", "section-imbalance", "redundant-expression",
          "open-marker", "repeated-opener"]
SEV_ORDER = {"high": 0, "warn": 1, "info": 2}


def run(path, spine_path=None, only=None, use_backend=True):
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        sys.stderr.write("drift_scan: cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)

    global MORPH
    if use_backend and MORPH is None:
        MORPH = Morph()
    elif not use_backend:
        MORPH = None

    lines = strip_code_fences(strip_frontmatter(raw.splitlines()))
    text = "\n".join(lines)
    sections = split_sections(lines)
    spine = parse_spine(spine_path) if spine_path else {"glossary": [], "style": {}}
    glossary, style = spine["glossary"], spine["style"]
    outline = spine.get("outline") or []
    claims = spine.get("claims") or []
    first_defined = spine.get("first_defined") or {}
    enabled = set(only) if only else set(CHECKS)

    findings = []
    if "claim-coverage" in enabled and outline:
        findings += check_claim_coverage(sections, outline)
    if "unverified-claim" in enabled and claims:
        findings += check_unverified_claims(claims)
    if "term-before-definition" in enabled and first_defined:
        findings += check_term_before_definition(sections, first_defined)
    if "unsourced-assertion" in enabled:
        findings += check_unsourced_assertion(sections)
    if "declared-style-violation" in enabled and any(
            style.get(k) is not None and style.get(k) != []
            for k in ("register", "digits", "list_period", "banned")):
        findings += check_declared_style(
            sections, prose_corpus(lines, drop_tables=False, drop_quotes=True), style)
    # A declared register makes the mixing check redundant and noisier: every
    # sentence it would list is already reported against the declaration, more
    # precisely. Fall back to mixing only when nothing was declared.
    if "style-mixing" in enabled and not style.get("register"):
        findings += check_style_mixing(sections)
    if "long-sentence" in enabled:
        findings += check_long_sentences(sections)
    if "notation-drift" in enabled:
        findings += check_notation_drift(
            prose_corpus(lines, drop_tables=True, drop_quotes=True), sections)
    if "glossary-violation" in enabled and glossary:
        findings += check_glossary(
            prose_corpus(lines, drop_tables=False, drop_quotes=True), sections, glossary)
    if "numeric-inconsistency" in enabled:
        findings += check_numeric_inconsistency(sections)
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
        "style_contract": {k: v for k, v in style.items() if v},
        "backend": (MORPH.name + " " + MORPH.version)
                   if (MORPH is not None and MORPH.available) else None,
        "counts": dict(Counter(f["severity"] for f in findings)),
    }
    return findings, stats


def render(findings, stats):
    lines = []
    lines.append("drift_scan: %s" % stats["file"])
    declared = stats.get("style_contract") or {}
    lines.append("  %d chars, %d sections, spine=%s (%d glossary terms, %s)"
                 % (stats["chars"], stats["sections"],
                    stats["spine"] or "none", stats["glossary_terms"],
                    "style contract: " + ", ".join(
                        "%s=%s" % (k, v) for k, v in sorted(declared.items()))
                    if declared else "no style contract declared"))
    if stats.get("backend"):
        lines.append("  backends: %s — 文体判定は品詞ベース、表記ゆれは正規化形も照合"
                     % stats["backend"])
    else:
        lines.append("  backends: none — 文体判定は語尾マッチ、表記ゆれは既知パターンのみ "
                     "(sudachipy を入れると両方が品詞・正規化形ベースになります)")
    if stats.get("spine"):
        lines.append("  content: 主旨の語の不在 / 未検証の主張 / 定義前の用語 / 無出典の断定 "
                     "— 語の有無までで、主旨を landing しているかは見ていません")
    else:
        lines.append("  content: スパイン未指定のため、主旨・未検証の主張・定義前の用語は "
                     "一切見ていません（--spine を渡すと有効）")
    lines.append("  still human-only: 主旨を実際に述べているか・章間の論理接続・読者前提との齟齬"
                 "・数値以外の矛盾（references/content-review.md の手順 / doc-review）")
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
    ap.add_argument("--no-backend", action="store_true",
                    help="Force the stdlib path even if sudachipy is installed")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    only = None
    if args.only:
        only = [c.strip() for c in args.only.split(",") if c.strip()]
        unknown = [c for c in only if c not in CHECKS]
        if unknown:
            sys.stderr.write("drift_scan: unknown check(s): %s\n" % ", ".join(unknown))
            return 2

    findings, stats = run(args.draft, args.spine, only,
                          use_backend=not args.no_backend)
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
    except Exception:
        # Exit 2, never 1. An uncaught exception would otherwise exit 1 — the
        # same code as "findings found" — so a crashed run reads as a clean
        # signal to any loop gating on the exit code, with empty stdout looking
        # like "nothing to report".
        import traceback
        traceback.print_exc()
        sys.stderr.write(
            "\ndrift_scan: aborted before reporting. Exit code 2 (not 1) so a "
            "gate cannot mistake this for a completed run.\n")
        sys.exit(2)
