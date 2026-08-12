#!/usr/bin/env python3
"""KBスクリプト共通部（stdlibのみ）。

kb-check.py（検証）と kb-graph.py（関係の活用）が共有する、
最小のフロントマター解析・KB走査・関係語彙・本文リンク抽出。

ここに置く理由: 同じ解析を2つのスクリプトに複製すると、片方だけ直したときに
検証と活用で見え方がずれる。規約 §6 が「関係は1方向にだけ書き、逆は導出」と
決めているので、導出の実装は1つでなければならない。
"""
import os
import re
import glob

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REF_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*/)?[A-Za-z0-9][A-Za-z0-9._-]*$")

# 規約 §6 の語彙 v1。値は逆関係名（対称なら自分自身）。
RELATIONS = {
    "related": "related",
    "applies": "applied_by",
    "part_of": "has_part",
    "contrasts_with": "contrasts_with",
    "supersedes": "superseded_by",
}
# 導出された向きの名前（レコードには書かない）。対称な関係は自分自身が逆なので除く。
INVERSE_NAMES = {v: k for k, v in RELATIONS.items() if v != k}

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")


def _split_list(v):
    return [x.strip() for x in v.strip()[1:-1].split(",") if x.strip()]


def parse_frontmatter(path):
    """先頭の YAML フロントマターを最小限に解析する。

    対応するのは規約が使う範囲だけ: スカラ、インラインリスト `[a, b]`、
    1段のネスト（`relations:` 配下）でのインラインリストとブロックリスト。
    見つからなければ None。
    """
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    m = FM_RE.match(txt)
    if not m:
        return None
    fm, cur, cur_key = {}, None, None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_]+:", line):  # トップレベル
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            cur, cur_key = None, None
            if v.startswith("[") and v.endswith("]"):
                fm[k] = _split_list(v)
            elif v == "":
                fm[k], cur = {}, k
            else:
                fm[k] = v
        elif line.startswith("  ") and cur and isinstance(fm.get(cur), dict):
            s = line.strip()
            if s.startswith("- ") and cur_key:  # ブロックリストの続き
                fm[cur][cur_key].append(s[2:].strip())
                continue
            k, _, v = s.partition(":")
            k, v = k.strip(), v.strip()
            if v.startswith("[") and v.endswith("]"):
                fm[cur][k] = _split_list(v)
                cur_key = None
            elif v == "":
                fm[cur][k] = []
                cur_key = k
            else:
                fm[cur][k] = [v]
                cur_key = None
    return fm


def read_manifest(path):
    man = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if ":" in line and not line.startswith(" ") and not line.startswith("#"):
                k, _, v = line.partition(":")
                man[k.strip()] = v.strip()
    return man


def body_links(path, record_dir):
    """本文中のレコード参照を返す: [(表記, 生の値, 解決用パス or None)]。

    `[[id]]` は id 参照、`[text](rel.md)` は相対パス参照として拾う。
    http(s) リンクとアンカーのみのリンクは対象外。
    """
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    body = FM_RE.sub("", txt, count=1)
    out = []
    for m in WIKILINK_RE.finditer(body):
        raw = m.group(1).strip()
        if REF_RE.match(raw):
            out.append(("wiki", raw, None))
    for m in MDLINK_RE.finditer(body):
        raw = m.group(1)
        if "://" in raw:
            continue
        out.append(("md", raw, os.path.normpath(os.path.join(record_dir, raw))))
    return out


class KB:
    def __init__(self, directory, manifest):
        self.dir = directory
        self.manifest = manifest
        self.kb = manifest.get("kb")
        self.format = manifest.get("format")
        self.index = manifest.get("index", "INDEX.md")
        self.records = {}      # id -> dict(path, fm, relations)
        self.by_path = {}      # 絶対パス -> id

    @property
    def index_path(self):
        return os.path.join(self.dir, self.index)


def load_kbs(root):
    """root 直下の各サブディレクトリ（manifest.yaml を持つもの）を KB として読む。

    root 自身が manifest.yaml を持つ場合は、その1つを KB として扱う。
    """
    manifests = sorted(glob.glob(os.path.join(root, "*", "manifest.yaml")))
    if os.path.isfile(os.path.join(root, "manifest.yaml")):
        manifests.insert(0, os.path.join(root, "manifest.yaml"))
    kbs = []
    for man in manifests:
        d = os.path.dirname(man)
        kb = KB(d, read_manifest(man))
        if not kb.kb:
            kb.kb = None
        for r in sorted(glob.glob(os.path.join(d, "**", "*.md"), recursive=True)):
            if os.path.abspath(r) == os.path.abspath(kb.index_path):
                continue
            fm = parse_frontmatter(r) or {}
            rid = fm.get("id")
            if not isinstance(rid, str):
                continue
            rel = fm.get("relations", {})
            rel = rel if isinstance(rel, dict) else {}
            kb.records[rid] = {"path": r, "fm": fm, "relations": rel}
            kb.by_path[os.path.abspath(r)] = rid
        kbs.append(kb)
    return kbs


def qualify(kb_id, ref):
    """参照を kb/id に正規化する。"""
    return ref if "/" in ref else f"{kb_id}/{ref}"


def build_graph(kbs):
    """(nodes, edges) を返す。

    nodes: kb/id -> dict(kb, id, title, path)
    edges: list of dict(src, dst, rel)   ※ レコードに書かれた向きのみ。
           逆向きは neighbors() が RELATIONS の逆関係名で導出する。
    """
    nodes, edges = {}, []
    for kb in kbs:
        for rid, rec in kb.records.items():
            key = f"{kb.kb}/{rid}"
            nodes[key] = {
                "kb": kb.kb,
                "id": rid,
                "title": rec["fm"].get("title", rid),
                "path": rec["path"],
            }
    for kb in kbs:
        for rid, rec in kb.records.items():
            src = f"{kb.kb}/{rid}"
            for rname, targets in rec["relations"].items():
                for t in targets:
                    edges.append({"src": src, "dst": qualify(kb.kb, t), "rel": rname})
    return nodes, edges


def neighbors(key, edges):
    """1ホップの隣接を両方向で返す: (out, incoming)。

    out      = そのレコードに書かれた関係
    incoming = 他レコードに書かれた関係から導出した逆向き（保存しない）
    """
    out = [(e["rel"], e["dst"]) for e in edges if e["src"] == key]
    inc = []
    for e in edges:
        if e["dst"] == key:
            inv = RELATIONS.get(e["rel"], e["rel"])
            inc.append((inv, e["src"]))
    return out, inc
