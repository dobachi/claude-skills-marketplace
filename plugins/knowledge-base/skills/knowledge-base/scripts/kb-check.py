#!/usr/bin/env python3
"""KB規約チェッカ（最小・stdlibのみ）。

docs/design/kb-convention-spec.md の不変条件を検査する開発用ツール。
- 各KBに manifest.yaml と INDEX（manifest.index）があるか
- entities 形式のレコードが id/type/name を持ち、id がパターンに合うか
- relations の値（id または kb/id）が実在レコードに解決するか（未解決は警告）

使い方: python3 scripts/kb-check.py [kb-root]   # 既定 kb-root = ./kb
終了コード: エラーがあれば 1、警告のみ/問題なしは 0。
"""
import os, re, sys, glob

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REF_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*/)?[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_frontmatter(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return None
    fm, cur = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z0-9_]+:", line):
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            if v.startswith("[") and v.endswith("]"):
                fm[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                cur = None
            elif v == "":
                fm[k], cur = {}, k
            else:
                fm[k], cur = v, None
        elif line.startswith("  ") and cur and isinstance(fm.get(cur), dict):
            k, _, v = line.strip().partition(":")
            v = v.strip()
            fm[cur][k.strip()] = [x.strip() for x in v[1:-1].split(",") if x.strip()] \
                if v.startswith("[") else [v]
    return fm


def read_manifest(path):
    man = {}
    for l in open(path, encoding="utf-8"):
        if ":" in l and not l.startswith(" "):
            k, _, v = l.partition(":")
            man[k.strip()] = v.strip()
    return man


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "kb"
    errors, warnings = [], []
    kbs = {}  # kb -> set(ids)

    manifests = sorted(glob.glob(os.path.join(root, "*", "manifest.yaml")))
    if not manifests:
        print(f"KB が見つかりません: {root}/*/manifest.yaml")
        return 1

    # pass 1: inventory
    for man in manifests:
        d = os.path.dirname(man)
        m = read_manifest(man)
        kb = m.get("kb")
        if not kb:
            errors.append(f"{man}: 'kb' が無い")
            continue
        index = m.get("index", "INDEX.md")
        if not os.path.isfile(os.path.join(d, index)):
            errors.append(f"{d}: INDEX '{index}' が無い（不変条件3）")
        rec_ids = set()
        for r in glob.glob(os.path.join(d, "*.md")):
            if os.path.basename(r) == index:
                continue
            fm = parse_frontmatter(r)
            if fm and isinstance(fm.get("id"), str):
                rec_ids.add(fm["id"])
        kbs[kb] = (d, m.get("format"), rec_ids)

    all_ids = {f"{kb}/{i}" for kb, (_, _, s) in kbs.items() for i in s}

    # pass 2: per-record checks
    for kb, (d, fmt, _) in kbs.items():
        index = read_manifest(os.path.join(d, "manifest.yaml")).get("index", "INDEX.md")
        for r in glob.glob(os.path.join(d, "*.md")):
            if os.path.basename(r) == index:
                continue
            fm = parse_frontmatter(r) or {}
            rid = fm.get("id")
            if fmt == "entities":
                for req in ("id", "type", "name"):
                    if req not in fm:
                        errors.append(f"{r}: 必須 '{req}' が無い（entities）")
            if isinstance(rid, str) and not ID_RE.match(rid):
                errors.append(f"{r}: id '{rid}' がパターン違反")
            rel = fm.get("relations", {})
            if isinstance(rel, dict):
                for rname, targets in rel.items():
                    for t in targets:
                        if not REF_RE.match(t):
                            errors.append(f"{r}: relations.{rname} '{t}' がパターン違反")
                            continue
                        key = t if "/" in t else f"{kb}/{t}"
                        if key not in all_ids:
                            warnings.append(f"{r}: relations.{rname} -> '{t}' が未解決")

    print(f"KB: {len(kbs)}  レコード: {sum(len(s) for _, (_, _, s) in kbs.items())}")
    for kb, (_, fmt, s) in sorted(kbs.items()):
        print(f"  - {kb} ({fmt}): {len(s)} records")
    print(f"\nエラー: {len(errors)}  警告: {len(warnings)}")
    for e in errors:
        print(f"  [ERROR] {e}")
    for w in warnings:
        print(f"  [WARN ] {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
