#!/usr/bin/env python3
"""review_sheet.py — the comment sheet that carries one review round between a reviewer
and an AI, for .pptx / .docx / .md / .pdf artifacts. Stdlib only (pdf needs poppler).

  new     <artifact>... [--out F] [--round N] [--reviewer NAME] [--header TEXT]
                        [--carry PREV] [--depth N] [--excerpt N] [--lang ja|en] [--force]
  check   <sheet>                      validate; stale artifact and ID problems are findings
  ingest  <sheet>... [--json] [--no-write]   assign IDs, list open comments, print the plan
  resolve <sheet> <id> --status applied|declined|question|open [--note TEXT] [--log F] [--by NAME]
  where   <sheet> [--url-template T]   the hand-over block: host, paths, how to open

Exit codes: 0 = ok / 1 = findings / 2 = usage error or precondition missing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

FORMAT_VERSION = 1
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
MARKS = {" ": "open", "x": "applied", "X": "applied", "-": "declined", "?": "question"}
MARK_OF = {"open": " ", "applied": "x", "declined": "-", "question": "?"}

L = {
    "ja": {
        "title": "レビューシート（第{n}回）",
        "howto": (
            "**書き方** 各箇所の `- [ ]` の後ろに書く。足りなければ行を増やす。空のまま残した行は「コメントなし」。"
            "記号は AI が処理後に書き換える: `[x]` 反映 / `[-]` 見送り / `[?]` 確認したい（AI の返事は `↳` の行）。"
            "`[?]` に答えるときは記号を `[ ]` に戻し、同じ行の続きに書く。斜体の行は説明なので消してよい。"
        ),
        "targets": "**対象**",
        "th": "| # | ファイル | 単位 |",
        "global": "全体",
        "global_hint": "*結論、構成、量、言い回し、読み手への合い方など、どこか一箇所に収まらないこと。*",
        "slide": "p.{n}",
        "page": "p.{n}",
        "head0": "冒頭（表紙・目次）",
        "untitled": "（無題）",
        "hidden": "（非表示）",
        "carried": "第{n}回から持ち越し",
        "carried_from": "（前回 {loc}）",
        "units": {"pptx": "{n} 枚", "docx": "見出し {n}", "md": "見出し {n}", "pdf": "{n} ページ"},
    },
    "en": {
        "title": "Review sheet (round {n})",
        "howto": (
            "**How to comment** Write after `- [ ]` under the item. Add lines as needed; an empty line means no comment. "
            "The AI rewrites the mark afterwards: `[x]` applied / `[-]` declined / `[?]` needs your answer (its reply is on the `↳` line). "
            "To answer a `[?]`, set the mark back to `[ ]` and continue on the same line. Italic lines are instructions; delete them if you like."
        ),
        "targets": "**Artifacts**",
        "th": "| # | File | Units |",
        "global": "Overall",
        "global_hint": "*Conclusion, structure, length, wording, fit for the reader: anything that belongs to no single place.*",
        "slide": "p.{n}",
        "page": "p.{n}",
        "head0": "Front matter (cover, contents)",
        "untitled": "(untitled)",
        "hidden": "(hidden)",
        "carried": "carried over from round {n}",
        "carried_from": "(round before: {loc})",
        "units": {"pptx": "{n} slides", "docx": "{n} headings", "md": "{n} headings", "pdf": "{n} pages"},
    },
}


def die(msg: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(f"review_sheet: {msg}", file=sys.stderr)
    sys.exit(code)


def sha8(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:8]


def now_iso() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


# ----------------------------------------------------------------------------- extraction
# A "unit" is one reviewable location: a slide, a heading section, a page.
# {"id": "S3", "label": "p.3 目的と結果", "excerpt": ["...", ...], "level": 1}


def _texts(el, tag: str) -> str:
    return "".join(t.text or "" for t in el.iter(tag))


def extract_pptx(path: Path, excerpt_n: int, lang: str) -> list[dict]:
    T = L[lang]
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "ppt/presentation.xml" not in names:
            die(f"not a .pptx (no ppt/presentation.xml): {path}")
        pres = ET.fromstring(z.read("ppt/presentation.xml"))
        rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rels.iter(f"{{{NS['rel']}}}Relationship")}
        units = []
        for i, sld in enumerate(pres.iter(f"{{{NS['p']}}}sldId"), start=1):
            rid = sld.get(f"{{{NS['r']}}}id")
            t = target.get(rid, "")
            name = t if t.startswith("ppt/") else "ppt/" + t.lstrip("/")
            if name not in names:
                units.append({"id": f"S{i}", "label": T["slide"].format(n=i) + " " + T["untitled"], "excerpt": [], "level": 1})
                continue
            root = ET.fromstring(z.read(name))
            hidden = root.get("show") == "0"
            title, body = "", []
            for sp in root.iter(f"{{{NS['p']}}}sp"):
                ph = sp.find(f".//{{{NS['p']}}}nvPr/{{{NS['p']}}}ph")
                paras = [_texts(p, f"{{{NS['a']}}}t").strip() for p in sp.iter(f"{{{NS['a']}}}p")]
                paras = [p for p in paras if p]
                if ph is not None and ph.get("type") in ("title", "ctrTitle") and not title:
                    title = " ".join(paras)
                else:
                    body.extend(paras)
            for tbl in root.iter(f"{{{NS['a']}}}tbl"):
                for tr in tbl.iter(f"{{{NS['a']}}}tr"):
                    cells = [_texts(tc, f"{{{NS['a']}}}t").strip() for tc in tr.iter(f"{{{NS['a']}}}tc")]
                    body.append(" | ".join(cells))
            if not title and body:
                title = body.pop(0)
            label = T["slide"].format(n=i) + " " + (title or T["untitled"]) + (" " + T["hidden"] if hidden else "")
            units.append({"id": f"S{i}", "label": label, "excerpt": body[:excerpt_n], "level": 1})
    return units


def _docx_para_text(p) -> str:
    return "".join(t.text or "" for t in p.iter(f"{{{NS['w']}}}t")).strip()


def extract_docx(path: Path, excerpt_n: int, depth: int, lang: str) -> list[dict]:
    T = L[lang]
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "word/document.xml" not in names:
            die(f"not a .docx (no word/document.xml): {path}")
        style_name = {}
        if "word/styles.xml" in names:
            st = ET.fromstring(z.read("word/styles.xml"))
            for s in st.iter(f"{{{NS['w']}}}style"):
                nm = s.find(f"{{{NS['w']}}}name")
                style_name[s.get(f"{{{NS['w']}}}styleId")] = (nm.get(f"{{{NS['w']}}}val") if nm is not None else "") or ""
        doc = ET.fromstring(z.read("word/document.xml"))
    body = doc.find(f"{{{NS['w']}}}body")
    blocks: list[tuple[int, str]] = []  # (level or 0 for body, text)
    for el in body:
        tag = el.tag.split("}")[1]
        if tag == "p":
            ps = el.find(f"{{{NS['w']}}}pPr/{{{NS['w']}}}pStyle")
            sid = ps.get(f"{{{NS['w']}}}val") if ps is not None else ""
            level = heading_level(sid, style_name.get(sid, ""))
            text = _docx_para_text(el)
            if text:
                blocks.append((level, text))
        elif tag == "tbl":
            for tr in el.iter(f"{{{NS['w']}}}tr"):
                cells = [" ".join(_docx_para_text(p) for p in tc.iter(f"{{{NS['w']}}}p")).strip()
                         for tc in tr.findall(f"{{{NS['w']}}}tc")]
                blocks.append((0, " | ".join(cells)))
    return units_from_blocks(blocks, excerpt_n, depth, T, "H")


def heading_level(style_id: str, style_name: str) -> int:
    """0 = body text; 1..9 = heading level. Title/表題 count as level 1."""
    for cand in (style_name, style_id):
        c = (cand or "").strip().lower()
        m = re.match(r"^(?:heading|見出し|überschrift|titre|título)\s*(\d)$", c)
        if m:
            return int(m.group(1))
        if c in ("title", "表題", "標題"):
            return 1
    if re.fullmatch(r"[1-9]", (style_id or "").strip()) and not style_name:
        return int(style_id)
    return 0


def extract_md(path: Path, excerpt_n: int, depth: int, lang: str) -> list[dict]:
    T = L[lang]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0
    if lines and lines[0].strip() == "---":  # skip front matter
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                i = j + 1
                break
    blocks: list[tuple[int, str]] = []
    fence = None
    for line in lines[i:]:
        s = line.rstrip()
        m = re.match(r"^(`{3,}|~{3,})", s)
        if m:
            if fence is None:
                fence = m.group(1)[0]
            elif s.startswith(fence * 3):
                fence = None
            continue
        if fence:
            continue
        h = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", s)
        if h:
            blocks.append((len(h.group(1)), re.sub(r"\s*<!--.*?-->\s*", " ", h.group(2)).strip()))
        elif s.strip():
            blocks.append((0, s.strip()))
    return units_from_blocks(blocks, excerpt_n, depth, T, "H")


def units_from_blocks(blocks, excerpt_n: int, depth: int, T, prefix: str) -> list[dict]:
    """Cut a (level, text) stream into units at headings of level <= depth. Deeper headings
    become excerpt bullets. Text before the first heading becomes unit H0 when non-empty."""
    levels = sorted({lv for lv, _ in blocks if lv})
    if not levels:
        texts = [t for _, t in blocks]
        return [{"id": f"{prefix}1", "label": T["head0"], "excerpt": texts[:excerpt_n], "level": 1}] if texts else []
    top = levels[0]
    cut = top + depth - 1
    units: list[dict] = []
    cur = None
    pre: list[str] = []
    n = 0
    for lv, text in blocks:
        if lv and lv <= cut:
            n += 1
            cur = {"id": f"{prefix}{n}", "label": text, "excerpt": [], "level": lv - top + 1}
            units.append(cur)
        elif cur is None:
            pre.append(text)
        else:
            cur["excerpt"].append(("- " + text) if lv else text)
    for u in units:
        u["excerpt"] = u["excerpt"][:excerpt_n]
    if pre:
        units.insert(0, {"id": f"{prefix}0", "label": T["head0"], "excerpt": pre[:excerpt_n], "level": 1})
    return units


def extract_pdf(path: Path, excerpt_n: int, lang: str) -> list[dict]:
    T = L[lang]
    if not shutil.which("pdftotext") or not shutil.which("pdfinfo"):
        die("pdf needs poppler-utils (pdftotext, pdfinfo)")
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    m = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    if not m:
        die(f"pdfinfo could not read {path}")
    units = []
    for i in range(1, int(m.group(1)) + 1):
        out = subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(path), "-"],
                             capture_output=True, text=True).stdout
        lines = [re.sub(r"\s{2,}", " ", s).strip() for s in out.splitlines() if s.strip()]
        title = lines[0] if lines else T["untitled"]
        units.append({"id": f"P{i}", "label": T["page"].format(n=i) + " " + title, "excerpt": lines[1:1 + excerpt_n], "level": 1})
    return units


def extract(path: Path, excerpt_n: int, depth: int, lang: str) -> tuple[str, list[dict]]:
    if not path.is_file():
        die(f"no such file: {path}")
    ext = path.suffix.lower().lstrip(".")
    if ext in ("pptx", "docx") and not zipfile.is_zipfile(path):
        die(f"not an Office file (not a zip container): {path}")
    if ext == "pptx":
        return ext, extract_pptx(path, excerpt_n, lang)
    if ext == "docx":
        return ext, extract_docx(path, excerpt_n, depth, lang)
    if ext in ("md", "markdown"):
        return "md", extract_md(path, excerpt_n, depth, lang)
    if ext == "pdf":
        return ext, extract_pdf(path, excerpt_n, lang)
    die(f"unsupported artifact type .{ext} (pptx / docx / md / pdf): {path}")


# ----------------------------------------------------------------------------- sheet model

LOC_RE = re.compile(r"<!--\s*loc:\s*([A-Za-z0-9.]+)\s*-->")
ART_RE = re.compile(r"<!--\s*art:\s*(A\d+)\s*-->")
COMMENT_RE = re.compile(r"^- \[([ xX?-])\]\s?(?:([A-Za-z0-9.]+-\d+):\s*)?(.*)$")
REPLY_RE = re.compile(r"^\s+(?:- )?↳\s?(.*)$")
BARE_RE = re.compile(r"^(?:[-*+]\s+|\d+[.)]\s+)?(.*)$")
HINT_RE = re.compile(r"^(\*[^*].*[^*]\*|_[^_].*[^_]_)$")


class Sheet:
    def __init__(self, path: Path):
        self.path = path
        text = path.read_text(encoding="utf-8")
        self.lines = text.splitlines()
        self.meta: dict = {}
        self.artifacts: list[dict] = []
        self.body_start = 0
        self._parse_front()
        self.locs: list[dict] = []  # {"id","label","start","end","comments":[...]}
        self._parse_body()

    # front matter: flat keys plus an `artifacts:` list of `- path:` items
    def _parse_front(self):
        if not self.lines or self.lines[0].strip() != "---":
            die(f"not a review sheet (no front matter): {self.path}")
        i = 1
        cur_art = None
        while i < len(self.lines) and self.lines[i].strip() != "---":
            line = self.lines[i]
            if line.startswith("  - "):
                cur_art = {}
                self.artifacts.append(cur_art)
                line = "    " + line[4:]
            if line.startswith("    ") and cur_art is not None:
                k, _, v = line.strip().partition(":")
                cur_art[k.strip()] = v.strip().strip('"')
            elif not line.startswith(" "):
                k, _, v = line.partition(":")
                self.meta[k.strip()] = v.strip().strip('"')
                if k.strip() != "artifacts":
                    cur_art = None
            i += 1
        if i >= len(self.lines) or self.meta.get("review_sheet") is None:
            die(f"not a review sheet (no review_sheet: in front matter): {self.path}")
        self.body_start = i + 1

    def _parse_body(self):
        cur = None
        for n in range(self.body_start, len(self.lines)):
            s = self.lines[n]
            if s.startswith("#"):
                if cur:
                    cur["end"] = n
                m = LOC_RE.search(s)
                cur = None
                if m:
                    label = LOC_RE.sub("", s).lstrip("#").strip()
                    cur = {"id": m.group(1), "label": label, "start": n, "end": len(self.lines), "comments": []}
                    self.locs.append(cur)
                continue
            if cur is None or not s.strip() or s.lstrip().startswith(">") or s.lstrip().startswith("<!--"):
                continue
            if HINT_RE.match(s.strip()):  # generator-written instruction line
                continue
            cm = COMMENT_RE.match(s)
            if cm:
                cur["comments"].append({"line": n, "mark": cm.group(1).replace("X", "x"), "id": cm.group(2),
                                        "text": cm.group(3).strip(), "cont": [], "replies": [], "loc": cur["id"]})
                continue
            rm = REPLY_RE.match(s)
            if rm and cur["comments"]:
                cur["comments"][-1]["replies"].append(rm.group(1))
                continue
            if s.startswith(("  ", "\t")) and cur["comments"]:
                cur["comments"][-1]["cont"].append(s.strip())
                continue
            # a bare line the reviewer typed without the checkbox: still a comment
            bm = BARE_RE.match(s.strip())
            cur["comments"].append({"line": n, "mark": " ", "id": None, "text": bm.group(1).strip(), "cont": [],
                                    "replies": [], "loc": cur["id"], "bare": True})

    def comments(self):
        for loc in self.locs:
            for c in loc["comments"]:
                yield c

    def full_text(self, c) -> str:
        return " ".join([c["text"], *c["cont"]]).strip()

    def save(self):
        self.path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def counts(sheet: Sheet) -> dict:
    out = {"open": 0, "applied": 0, "declined": 0, "question": 0, "blank": 0}
    for c in sheet.comments():
        if not sheet.full_text(c):
            out["blank"] += 1
        else:
            out[MARKS[c["mark"]]] += 1
    return out


def artifact_state(sheet: Sheet) -> list[tuple[dict, str]]:
    """(artifact, 'same' | 'changed' | 'missing')"""
    res = []
    for a in sheet.artifacts:
        p = Path(a.get("path", ""))
        if not p.is_file():
            res.append((a, "missing"))
        else:
            res.append((a, "same" if sha8(p) == a.get("sha256") else "changed"))
    return res


# ----------------------------------------------------------------------------- new


def cmd_new(args) -> int:
    T = L[args.lang]
    paths = [Path(p).resolve() for p in args.artifact]
    prev = Sheet(Path(args.carry)) if args.carry else None
    rnd = args.round or (int(prev.meta.get("round", "0")) + 1 if prev else 1)
    out = Path(args.out) if args.out else Path.cwd() / f"review-r{rnd}.md"
    if out.exists() and not args.force:
        die(f"{out} exists; use --force to overwrite", 1)

    arts = []
    for i, p in enumerate(paths, start=1):
        kind, units = extract(p, args.excerpt, args.depth, args.lang)
        arts.append({"idx": f"A{i}", "path": p, "kind": kind, "units": units, "sha": sha8(p)})
    multi = len(arts) > 1
    hdr = ["---", f"review_sheet: {FORMAT_VERSION}", f"round: {rnd}", f'reviewer: "{args.reviewer or ""}"',
           f"generated: {now_iso()}", f"host: {socket.gethostname()}", "artifacts:"]
    for a in arts:
        hdr += [f"  - path: {a['path']}", f"    kind: {a['kind']}", f"    sha256: {a['sha']}",
                f"    units: {len(a['units'])}"]
    hdr.append("---")

    body = ["", "# " + T["title"].format(n=rnd), ""]
    if args.header:
        body += [args.header, ""]
    body += [T["howto"], "", T["targets"], "", T["th"], "|---|---|---|"]
    for a in arts:
        body.append(f"| {a['idx']} | `{a['path']}` | {T['units'][a['kind']].format(n=len(a['units']))} |")
    body += ["", f"## {T['global']} <!-- loc: G -->", "", T["global_hint"], ""]

    carried: dict[str, list[dict]] = {}
    if prev:
        for c in prev.comments():
            if prev.full_text(c) and c["mark"] in (" ", "?"):
                carried.setdefault(c["loc"], []).append(c)

    def emit_carried(loc_id: str, lines: list[str]):
        for c in carried.pop(loc_id, []):
            cid = f"{c['id']}: " if c["id"] else ""
            lines.append(f"- [{c['mark']}] {cid}{c['text']}")
            lines += [f"  {x}" for x in c["cont"]]
            lines += [f"  - ↳ {r}" for r in c["replies"]]
            lines.append(f"  - ↳ {T['carried'].format(n=prev.meta.get('round', '?'))}")

    emit_carried("G", body)
    body += ["- [ ] ", ""]
    for a in arts:
        pre = f"{a['idx']}." if multi else ""
        h = "###" if multi else "##"
        if multi:
            body += [f"## {a['idx']}. {a['path'].name} <!-- art: {a['idx']} -->", ""]
        for u in a["units"]:
            body += [f"{h} {u['label']} <!-- loc: {pre}{u['id']} -->", ""]
            if u["excerpt"]:
                body += [f"> {x}" for x in u["excerpt"]] + [""]
            emit_carried(f"{pre}{u['id']}", body)
            body += ["- [ ] ", ""]
    # carried comments whose location no longer exists go to the global section
    if carried:
        gi = next(i for i, s in enumerate(body) if "<!-- loc: G -->" in s)
        ins = []
        for loc_id, cs in carried.items():
            for c in cs:
                cid = f"{c['id']}: " if c["id"] else ""
                ins.append(f"- [{c['mark']}] {cid}{T['carried_from'].format(loc=loc_id)} {c['text']}")
                ins += [f"  - ↳ {r}" for r in c["replies"]]
                ins.append(f"  - ↳ {T['carried'].format(n=prev.meta.get('round', '?'))}")
        # insert before the seeded blank item of the global section
        j = gi + 1
        while j < len(body) and body[j] != "- [ ] ":
            j += 1
        body[j:j] = ins

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(hdr + body).rstrip("\n") + "\n", encoding="utf-8")
    print(f"sheet: {out.resolve()}")
    for a in arts:
        print(f"  {a['idx']} {a['kind']} {a['path']} ({len(a['units'])} units, sha256 {a['sha']})")
    if prev:
        n = sum(1 for c in prev.comments() if prev.full_text(c) and c["mark"] in (" ", "?"))
        print(f"  carried from {prev.path}: {n}")
    return 0


# ----------------------------------------------------------------------------- check


def cmd_check(args) -> int:
    sheet = Sheet(Path(args.sheet))
    findings = []
    seen: dict[str, int] = {}
    for c in sheet.comments():
        if c["id"]:
            if c["id"] in seen:
                findings.append(f"duplicate id {c['id']} (lines {seen[c['id']] + 1} and {c['line'] + 1})")
            seen[c["id"]] = c["line"]
            if c["id"].rsplit("-", 1)[0] != c["loc"]:
                findings.append(f"id {c['id']} sits under location {c['loc']} (line {c['line'] + 1})")
        if c.get("bare") and sheet.full_text(c):
            findings.append(f"comment without a checkbox at line {c['line'] + 1}; `ingest` will normalize it")
    if not any(l["id"] == "G" for l in sheet.locs):
        findings.append("no global section (<!-- loc: G -->)")
    for a, state in artifact_state(sheet):
        if state == "missing":
            findings.append(f"artifact missing: {a.get('path')}")
        elif state == "changed":
            findings.append(f"artifact changed since the sheet was generated (stale sheet): {a.get('path')}")
    cnt = counts(sheet)
    print(f"sheet: {sheet.path.resolve()} (round {sheet.meta.get('round')}, {len(sheet.locs)} locations)")
    print("comments: " + ", ".join(f"{k} {v}" for k, v in cnt.items()))
    for f in findings:
        print(f"finding: {f}")
    return 1 if findings else 0


# ----------------------------------------------------------------------------- ingest


def assign_ids(sheet: Sheet) -> int:
    """Give every non-empty comment an id and a checkbox; write in place. Returns count changed."""
    changed = 0
    for loc in sheet.locs:
        used = set()
        for c in loc["comments"]:
            if c["id"]:
                m = re.search(r"-(\d+)$", c["id"])
                used.add(int(m.group(1)) if m else 0)
        nxt = (max(used) + 1) if used else 1
        for c in loc["comments"]:
            if c["id"] or not sheet.full_text(c):
                continue
            c["id"] = f"{loc['id']}-{nxt}"
            nxt += 1
            sheet.lines[c["line"]] = f"- [{c['mark']}] {c['id']}: {c['text']}"
            c.pop("bare", None)
            changed += 1
    return changed


def cmd_ingest(args) -> int:
    sheets = [Sheet(Path(p)) for p in args.sheet]
    report = {"sheets": [], "global": [], "locations": {}, "question": [], "stale": []}
    for sh in sheets:
        n = 0 if args.no_write else assign_ids(sh)
        if n:
            sh.save()
        report["sheets"].append({"path": str(sh.path.resolve()), "round": sh.meta.get("round"),
                                 "reviewer": sh.meta.get("reviewer", ""), "ids_assigned": n, "counts": counts(sh)})
        for a, state in artifact_state(sh):
            if state != "same":
                report["stale"].append({"sheet": str(sh.path), "artifact": a.get("path"), "state": state})
        for loc in sh.locs:
            for c in loc["comments"]:
                text = sh.full_text(c)
                if not text:
                    continue
                item = {"id": c["id"], "loc": loc["id"], "label": loc["label"], "text": text,
                        "status": MARKS[c["mark"]], "replies": c["replies"], "reviewer": sh.meta.get("reviewer", ""),
                        "sheet": str(sh.path.resolve()), "line": c["line"] + 1}
                if item["status"] == "question":
                    report["question"].append(item)
                elif item["status"] == "open":
                    (report["global"] if loc["id"] == "G" else
                     report["locations"].setdefault(loc["id"], {"label": loc["label"], "items": []})["items"]).append(item)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    for s in report["sheets"]:
        c = s["counts"]
        who = f" reviewer={s['reviewer']}" if s["reviewer"] else ""
        print(f"sheet: {s['path']} (round {s['round']}{who}) ids assigned: {s['ids_assigned']}; "
              + ", ".join(f"{k} {v}" for k, v in c.items()))
    for st in report["stale"]:
        print(f"stale: {st['artifact']} is {st['state']} since the sheet was generated; comments refer to the old version")
    print()
    print("## 1. global — apply first, in order")
    for it in report["global"] or []:
        print(f"- {it['id']}: {it['text']}")
    if not report["global"]:
        print("- (none)")
    print()
    print("## 2. by location — independent of each other; may run in parallel")
    for loc_id, g in report["locations"].items():
        print(f"### {loc_id} {g['label']}")
        for it in g["items"]:
            print(f"- {it['id']}: {it['text']}")
    if not report["locations"]:
        print("- (none)")
    if report["question"]:
        print()
        print("## 3. waiting for the reviewer [?]")
        for it in report["question"]:
            tail = f" ↳ {it['replies'][-1]}" if it["replies"] else ""
            print(f"- {it['id']} ({it['loc']}): {it['text']}{tail}")
    return 0


# ----------------------------------------------------------------------------- resolve

LOG_HEADER = ["# review log", "", "| time | round | sheet | id | location | comment | result | note |",
              "|---|---|---|---|---|---|---|---|"]


def md_cell(s: str, n: int = 80) -> str:
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def cmd_resolve(args) -> int:
    sheet = Sheet(Path(args.sheet))
    target = next((c for c in sheet.comments() if c["id"] == args.id), None)
    if target is None:
        print(f"review_sheet: no comment with id {args.id} in {sheet.path}", file=sys.stderr)
        return 1
    mark = MARK_OF[args.status]
    line = sheet.lines[target["line"]]
    sheet.lines[target["line"]] = re.sub(r"^- \[.\]", f"- [{mark}]", line, count=1)
    if args.note:
        rnd = sheet.meta.get("round", "?")
        who = f" {args.by}" if args.by else ""
        reply = f"  - ↳ r{rnd}{who}: {args.note}"
        # after the comment line, its continuation lines and existing replies
        ins = target["line"] + 1
        while ins < len(sheet.lines) and (REPLY_RE.match(sheet.lines[ins]) or sheet.lines[ins].startswith(("  ", "\t"))):
            ins += 1
        sheet.lines.insert(ins, reply)
    sheet.save()
    log = Path(args.log) if args.log else sheet.path.parent / "review-log.md"
    new = not log.exists()
    with log.open("a", encoding="utf-8") as f:
        if new:
            f.write("\n".join(LOG_HEADER) + "\n")
        f.write("| " + " | ".join([now_iso(), str(sheet.meta.get("round", "")), sheet.path.name, args.id, target["loc"],
                                   md_cell(sheet.full_text(target)), args.status, md_cell(args.note or "", 160)]) + " |\n")
    print(f"{args.id}: {args.status} -> {sheet.path} ; log {log}")
    return 0


# ----------------------------------------------------------------------------- where


def run_quiet(cmd: list[str], timeout: float = 5) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def cmd_where(args) -> int:
    sheet = Sheet(Path(args.sheet))
    host = socket.gethostname()
    user = os.environ.get("USER") or os.environ.get("USERNAME") or ""
    ts = run_quiet(["tailscale", "ip", "-4"]) if shutil.which("tailscale") else ""
    lan = run_quiet(["hostname", "-I"]).split()
    addr = ts.splitlines()[0] if ts else (lan[0] if lan else "")
    sp = sheet.path.resolve()
    st = sp.stat()
    mtime = dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
    cnt = counts(sheet)
    log = sp.parent / "review-log.md"
    tmpl = args.url_template or os.environ.get("REVIEW_SHEET_URL_TEMPLATE", "")
    if "token" in tmpl.lower() or "key" in tmpl.lower():
        die("the URL template must not carry a key or token; the reader's browser keeps it", 2)

    print("## 開く場所 / Where to open")
    print(f"- host: {host}" + (f" ({'tailscale ' if ts else ''}{addr})" if addr else "") + (f", user {user}" if user else ""))
    print(f"- sheet: {sp}  (round {sheet.meta.get('round')}, updated {mtime}, open {cnt['open']}, question {cnt['question']})")
    print(f"- log: {log}" + ("" if log.exists() else "  (not yet)"))
    for a, state in artifact_state(sheet):
        p = Path(a.get("path", ""))
        when = dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if p.is_file() else "-"
        flag = {"same": "", "changed": "  ⚠ changed after the sheet", "missing": "  ⚠ missing"}[state]
        print(f"- artifact {a.get('kind', '')}: {p}  (updated {when}){flag}")
    print(f"- open on this host:  fude-cli here {sp}")
    print(f"- open from another machine (after `fude-cli setup {host}`):  fude-cli remote {host} {sp}")
    if shutil.which("fude-cli"):
        chk = run_quiet(["fude-cli", "--check"], timeout=8)
        if chk:
            print(f"- fude-cli --check: {chk.splitlines()[0]}")
    if tmpl:
        rel = sp.name
        root = os.environ.get("REVIEW_SHEET_URL_ROOT", "")
        if root:
            try:
                rel = str(sp.relative_to(Path(root).resolve()))
            except ValueError:
                rel = str(sp)
        print("- url: " + tmpl.replace("{path}", str(sp)).replace("{relpath}", rel).replace("{host}", host)
              .replace("{addr}", addr).replace("{name}", sp.name))
    return 0


# ----------------------------------------------------------------------------- main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="review_sheet.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="generate a sheet from one or more artifacts")
    n.add_argument("artifact", nargs="+")
    n.add_argument("--out", "-o")
    n.add_argument("--round", type=int)
    n.add_argument("--reviewer", default="")
    n.add_argument("--header", default="", help="a line placed under the title, e.g. a confidentiality marking")
    n.add_argument("--carry", help="previous sheet; its open and [?] comments are carried over")
    n.add_argument("--depth", type=int, default=1, help="heading depth that makes a location (docx/md)")
    n.add_argument("--excerpt", type=int, default=4, help="excerpt lines per location")
    n.add_argument("--lang", choices=["ja", "en"], default="ja")
    n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)

    c = sub.add_parser("check", help="validate a sheet")
    c.add_argument("sheet")
    c.set_defaults(fn=cmd_check)

    g = sub.add_parser("ingest", help="assign ids and print the work plan")
    g.add_argument("sheet", nargs="+")
    g.add_argument("--json", action="store_true")
    g.add_argument("--no-write", action="store_true", help="do not write ids back into the sheet")
    g.set_defaults(fn=cmd_ingest)

    r = sub.add_parser("resolve", help="record the outcome of one comment")
    r.add_argument("sheet")
    r.add_argument("id")
    r.add_argument("--status", required=True, choices=sorted(MARK_OF))
    r.add_argument("--note", default="", help="what was done and where; written as a ↳ reply and into the log")
    r.add_argument("--log")
    r.add_argument("--by", default="", help="who resolved it, e.g. an agent name")
    r.set_defaults(fn=cmd_resolve)

    w = sub.add_parser("where", help="print the hand-over block")
    w.add_argument("sheet")
    w.add_argument("--url-template", help="e.g. https://{addr}:3000/?file={relpath}; also $REVIEW_SHEET_URL_TEMPLATE")
    w.set_defaults(fn=cmd_where)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except argparse.ArgumentError as e:  # pragma: no cover
        die(str(e))
