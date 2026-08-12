#!/usr/bin/env python3
"""KB の関係（relations）を辿る・見るためのツール（stdlibのみ）。

規約 §6 のとおり、関係はレコードに1方向だけ書かれる。逆向きはここで導出する。
索引は作らず、毎回 Markdown から読む（KB内にDBを置かないため）。

使い方:
  python3 scripts/kb-graph.py <kb-root>                     # 全体の要約
  python3 scripts/kb-graph.py <kb-root> --neighbors <id>    # 1ホップ（両方向）
  python3 scripts/kb-graph.py <kb-root> --backlinks <id>    # 逆向きだけ
  python3 scripts/kb-graph.py <kb-root> --path <id> <id>    # 2レコード間の最短経路
  python3 scripts/kb-graph.py <kb-root> --orphans           # 関係ゼロのレコード
  python3 scripts/kb-graph.py <kb-root> --hubs [N]          # 次数の多い順
  python3 scripts/kb-graph.py <kb-root> --mermaid           # Mermaid 図を出力

<id> は `id`（KB内で一意なら）または `kb/id`。
"""
import os
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kb_common import RELATIONS, load_kbs, build_graph, neighbors  # noqa: E402


def resolve(ref, nodes):
    if ref in nodes:
        return ref
    hits = [k for k in nodes if nodes[k]["id"] == ref]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"レコードが見つかりません: {ref}")
    sys.exit("複数のKBに同じ id があります。kb/id で指定してください: " + ", ".join(sorted(hits)))


def label(key, nodes):
    return f"{key} — {nodes[key]['title']}"


def cmd_neighbors(key, nodes, edges, incoming_only=False):
    out, inc = neighbors(key, edges)
    print(label(key, nodes))
    if not incoming_only:
        print("\n  書かれている関係 (out):")
        if not out:
            print("    (なし)")
        for r, dst in sorted(out):
            print(f"    -{r}-> {label(dst, nodes) if dst in nodes else dst + ' [未解決]'}")
    print("\n  逆向き（導出, in）:")
    if not inc:
        print("    (なし)")
    for r, src in sorted(inc):
        print(f"    <-{r}- {label(src, nodes)}")


def cmd_path(a, b, nodes, edges):
    adj = collections.defaultdict(list)
    for e in edges:
        adj[e["src"]].append((e["dst"], e["rel"], ">"))
        adj[e["dst"]].append((e["src"], RELATIONS.get(e["rel"], e["rel"]), "<"))
    prev, q = {a: None}, collections.deque([a])
    while q:
        cur = q.popleft()
        if cur == b:
            break
        for nxt, r, d in adj[cur]:
            if nxt not in prev:
                prev[nxt] = (cur, r, d)
                q.append(nxt)
    if b not in prev:
        print(f"経路なし: {a} … {b}")
        return
    chain, cur = [], b
    while prev[cur]:
        p, r, d = prev[cur]
        chain.append((p, r, d, cur))
        cur = p
    for p, r, d, c in reversed(chain):
        arrow = f"-{r}->" if d == ">" else f"<-{r}-"
        print(f"{label(p, nodes)}\n    {arrow}\n{label(c, nodes)}\n")


def cmd_mermaid(nodes, edges):
    def nid(k):
        return "n_" + k.replace("/", "__").replace("-", "_").replace(".", "_")

    print("flowchart LR")
    for k, n in sorted(nodes.items()):
        t = n["title"]
        t = t[:28] + "…" if len(t) > 28 else t
        print(f'  {nid(k)}["{t}"]')
    for e in sorted(edges, key=lambda e: (e["src"], e["rel"], e["dst"])):
        if e["dst"] not in nodes:
            continue
        style = "---" if RELATIONS.get(e["rel"]) == e["rel"] else "-->"
        print(f'  {nid(e["src"])} {style}|{e["rel"]}| {nid(e["dst"])}')


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    root = os.path.expanduser(args[0])
    opts = args[1:]

    kbs = [kb for kb in load_kbs(root) if kb.kb]
    if not kbs:
        sys.exit(f"KB が見つかりません: {root}")
    nodes, edges = build_graph(kbs)

    if opts and opts[0] in ("--neighbors", "--backlinks"):
        if len(opts) < 2:
            sys.exit(f"{opts[0]} には id が要ります")
        cmd_neighbors(resolve(opts[1], nodes), nodes, edges,
                      incoming_only=(opts[0] == "--backlinks"))
        return 0
    if opts and opts[0] == "--path":
        if len(opts) < 3:
            sys.exit("--path には id が2つ要ります")
        cmd_path(resolve(opts[1], nodes), resolve(opts[2], nodes), nodes, edges)
        return 0
    if opts and opts[0] == "--mermaid":
        cmd_mermaid(nodes, edges)
        return 0

    deg = collections.Counter()
    for e in edges:
        deg[e["src"]] += 1
        if e["dst"] in nodes:
            deg[e["dst"]] += 1
    orphans = sorted(k for k in nodes if deg[k] == 0)

    if opts and opts[0] == "--orphans":
        print("関係ゼロのレコード:" if orphans else "関係ゼロのレコードはありません")
        for k in orphans:
            print(f"  {label(k, nodes)}")
        return 0
    if opts and opts[0] == "--hubs":
        n = int(opts[1]) if len(opts) > 1 else 10
        for k, c in deg.most_common(n):
            print(f"  {c:3d}  {label(k, nodes)}")
        return 0

    by_rel = collections.Counter(e["rel"] for e in edges)
    cross = [e for e in edges if e["dst"] in nodes
             and nodes[e["dst"]]["kb"] != nodes[e["src"]]["kb"]]
    unresolved = [e for e in edges if e["dst"] not in nodes]

    print(f"レコード: {len(nodes)}  関係: {len(edges)}  KB: {len(kbs)}")
    print("\n関係の内訳:")
    for r, c in by_rel.most_common():
        mark = "" if r in RELATIONS else "  ← 語彙外"
        print(f"  {c:3d}  {r}{mark}")
    print(f"\nKBをまたぐ関係: {len(cross)}   未解決の参照: {len(unresolved)}")
    for e in unresolved:
        print(f"  {e['src']} -{e['rel']}-> {e['dst']}")
    print("\n次数が多いレコード（ハブ）:")
    for k, c in deg.most_common(5):
        print(f"  {c:3d}  {label(k, nodes)}")
    if orphans:
        print(f"\n関係ゼロのレコード ({len(orphans)}):")
        for k in orphans:
            print(f"       {label(k, nodes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
