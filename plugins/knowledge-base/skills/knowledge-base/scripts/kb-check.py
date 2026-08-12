#!/usr/bin/env python3
"""KB規約チェッカ（最小・stdlibのみ）。

kb-convention.md の不変条件を検査する。
- 各KBに manifest.yaml と INDEX（manifest.index）があるか（不変条件2・3）
- entities 形式のレコードが id/type/name を持ち、id がパターンに合うか
- relations（§6, 両形式）: 参照が実在レコードに解決するか / 語彙 / 自己参照
- 本文リンクと relations のずれ（片方だけ更新された状態の検出）

使い方: python3 scripts/kb-check.py [kb-root]   # 既定 kb-root = ./kb
終了コード: 0=問題なし（警告のみを含む） / 1=エラーあり / 2=KBが1つも無い（前提不成立）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kb_common import (  # noqa: E402
    ID_RE, REF_RE, RELATIONS, INVERSE_NAMES,
    load_kbs, body_links, qualify, build_graph,
)


def rel(path, root):
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "kb"
    root = os.path.expanduser(root)
    errors, warnings = [], []

    kbs = [kb for kb in load_kbs(root)]
    if not kbs:
        print(f"KB が見つかりません: {root}/*/manifest.yaml")
        return 2

    for kb in kbs:
        if not kb.kb:
            errors.append(f"{kb.dir}/manifest.yaml: 'kb' が無い")
        if not os.path.isfile(kb.index_path):
            errors.append(f"{kb.dir}: INDEX '{kb.index}' が無い（不変条件3）")

    kbs = [kb for kb in kbs if kb.kb]
    all_ids = {f"{kb.kb}/{rid}" for kb in kbs for rid in kb.records}
    _, edges = build_graph(kbs)
    # 「どちらかの向きで関係が張られているか」の判定に使う（§6 規則4）
    linked_pairs = {(e["src"], e["dst"]) for e in edges}
    linked_pairs |= {(e["dst"], e["src"]) for e in edges}

    for kb in kbs:
        for rid, rec in sorted(kb.records.items()):
            p = rel(rec["path"], root)
            fm, key = rec["fm"], f"{kb.kb}/{rid}"

            if kb.format == "entities":
                for req in ("id", "type", "name"):
                    if req not in fm:
                        errors.append(f"{p}: 必須 '{req}' が無い（entities）")
            if not ID_RE.match(rid):
                errors.append(f"{p}: id '{rid}' がパターン違反")

            # --- relations（§6） ---
            for rname, targets in rec["relations"].items():
                if rname in INVERSE_NAMES:
                    warnings.append(
                        f"{p}: relations.{rname} は導出専用の向き。"
                        f"'{INVERSE_NAMES[rname]}' として相手側に書く（§6 規則2）")
                elif rname not in RELATIONS:
                    warnings.append(f"{p}: relations.{rname} は語彙外（§6 語彙v1）")
                for t in targets:
                    if not REF_RE.match(t):
                        errors.append(f"{p}: relations.{rname} '{t}' がパターン違反")
                        continue
                    tkey = qualify(kb.kb, t)
                    if tkey == key:
                        errors.append(f"{p}: relations.{rname} が自分自身を指している")
                    elif tkey not in all_ids:
                        warnings.append(f"{p}: relations.{rname} -> '{t}' が未解決")

            # --- 本文リンクと relations のずれ（§6 規則4） ---
            for kind, raw, abspath in body_links(rec["path"], os.path.dirname(rec["path"])):
                if kind == "wiki":
                    tkey = qualify(kb.kb, raw)
                    if tkey not in all_ids:
                        warnings.append(f"{p}: 本文リンク [[{raw}]] が未解決")
                        continue
                else:
                    tid = kb.by_path.get(os.path.abspath(abspath))
                    if tid is None:
                        if abspath and not os.path.isfile(abspath):
                            warnings.append(f"{p}: 本文リンク ({raw}) の参照先が無い")
                        continue
                    tkey = f"{kb.kb}/{tid}"
                if tkey == key:
                    continue
                if (key, tkey) not in linked_pairs:
                    warnings.append(
                        f"{p}: 本文は {tkey} を参照しているが relations に無い"
                        f"（どちらかの向きに1本書く）")

        # INDEX のリンク切れ
        if os.path.isfile(kb.index_path):
            for kind, raw, abspath in body_links(kb.index_path, kb.dir):
                if kind == "md" and abspath and not os.path.isfile(abspath):
                    warnings.append(f"{rel(kb.index_path, root)}: リンク ({raw}) の参照先が無い")

    n_rec = sum(len(kb.records) for kb in kbs)
    print(f"KB: {len(kbs)}  レコード: {n_rec}  関係: {len(edges)}")
    for kb in kbs:
        n_rel = sum(len(v) for r in kb.records.values() for v in r["relations"].values())
        print(f"  - {kb.kb} ({kb.format}): {len(kb.records)} records, {n_rel} relations")
    print(f"\nエラー: {len(errors)}  警告: {len(warnings)}")
    for e in errors:
        print(f"  [ERROR] {e}")
    for w in warnings:
        print(f"  [WARN ] {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
