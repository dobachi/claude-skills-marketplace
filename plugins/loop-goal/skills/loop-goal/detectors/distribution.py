#!/usr/bin/env python3
"""出典の使われ方の分布を測る。1件ずつ見ても出てこない欠陥を拾う。

実測では、per-claim の照合が満点のまま S-01（Wikipedia）が
90件中18件を占め、§1〜§2 の骨格を単独で支えていた（設計への示唆 §3）。
全件を横に並べて初めて単一障害点だと分かる。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下のブロックだけ）。

使い方:   python3 distribution.py <file>...
終了コード: 0=閾値内  1=超過  2=引数エラー
"""

import re
import sys
from collections import Counter
from pathlib import Path

# ─────────── 編集点: 文書の書式と、許容する偏りを書き換える ───────────
ROW = re.compile(r"^\|\s*(S-\d+)\s*\|.*\|\s*(T\d)\s*\|(.*)\|")   # ID, Tier, 照合欄
REF = re.compile(r"\[(S-\d+)\]")
FETCH_FAIL = "⚠️"

MAX_TOP_SHARE = 20.0    # 最頻出典が全参照に占める割合の上限(%)
MAX_T3_SHARE = 70.0     # 二次情報(T3)が出典表に占める割合の上限(%)
MAX_UNVERIFIED = 10.0   # 未照合の出典が出典表に占める割合の上限(%)
TOP_N = 5
# ─────────────────────────────────────────────────────────────────────


def report(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    table = {m.group(1): (m.group(2), m.group(3)) for l in lines if (m := ROW.match(l))}
    refs = Counter(s for l in lines if not ROW.match(l) for s in REF.findall(l))
    n = sum(refs.values())
    if not n or not table:
        print(f"\n{path.name} — 出典参照 {n}件 / 出典表 {len(table)}件。測定できない")
        return 1

    top = refs.most_common(TOP_N)
    share = top[0][1] / n * 100
    tiers = Counter(t for t, _ in table.values())
    t3 = tiers.get("T3", 0) / len(table) * 100
    unver = sum(1 for _, v in table.values() if FETCH_FAIL in v) / len(table) * 100

    print(f"\n{path.name} — 参照 {n}件 / 出典 {len(table)}件")
    for s, c in top:
        print(f"       {s}  {c:>3}件 ({c / n * 100:4.1f}%)  {'▇' * round(c / n * 60)}")
    checks = [
        (f"最頻出典の占有率  {share:.1f}%", share, MAX_TOP_SHARE),
        (f"T3(二次情報)比率  {t3:.1f}%  [{' / '.join(f'{t} {tiers.get(t, 0)}' for t in ('T1', 'T2', 'T3'))}]",
         t3, MAX_T3_SHARE),
        (f"未照合の出典比率  {unver:.1f}%", unver, MAX_UNVERIFIED),
    ]
    bad = 0
    for label, value, limit in checks:
        over = value > limit
        bad += over
        print(f"  {'NG' if over else 'OK':<4} {label}   上限 {limit:.0f}%")
    return bad


def main():
    paths = [Path(a) for a in sys.argv[1:]]
    if not paths:
        print(__doc__)
        return 2
    total = 0
    for p in paths:
        if not p.is_file():
            print(f"{p}: 見つからない")
            return 2
        total += report(p)

    print("\n保証しないこと")
    print("  - 偏りが誤りとは限らない。単一の一次資料に集中するのは正常なこともある")
    print("  - 閾値に根拠はない。この文書で許すと決めた線であり、妥当性は人が判断する")
    print("  - Tier は自己申告。出典が実際に信頼できるかは見ない")
    print(f"\n判定: {'NG' if total else 'OK'}（超過 {total}件）")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
