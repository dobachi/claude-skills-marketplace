#!/usr/bin/env python3
"""この文書で各検出器が噛むかを、マーカーの実測で人に見せる。

ゲートを組む前（フェーズ0）に読むもの。**この1本だけは判定しない。**
終了コードは 0=出力できた / 2=引数エラー のみで、1 は返さない。
噛んでいるかを判断するのは人であり、閾値も適否も機械が決める話ではないためである。

これが無くて実際に間違えた3件（ARCHITECTURE.md §7.1・§7.2、実験3のフェーズ0）:
出典表0件の文書で素通りを合格と読んだ / `^>` が0行なのに sed テストを書いた /
候補8件が全て偽陽性だった。

設計方針: 1目的 / 標準ライブラリのみ / 設定ファイルなし。

使い方:   python3 applicability_report.py <file>...
終了コード: 0=出力できた  2=引数エラー
"""

import re
import sys
from pathlib import Path

# ─────────── 編集点: 文書の書式と、依存する検出器 ───────────
# (表示名, 正規表現, 行頭一致か, このマーカーに依存する検出器)
MARKERS = [
    ("ROW   出典表の行", re.compile(r"^\|\s*S-\d+\s*\|"), True,
     ["refs_integrity", "declared_counts", "distribution", "no_regression"]),
    ("REF   参照記号 [S-xx]", re.compile(r"\[S-\d+\]"), False,
     ["refs_integrity", "distribution", "no_regression"]),
    ("DECL  件数の申告行", re.compile(r"(本文中の引用|取得不能).*\|\s*\**\d"), False,
     ["declared_counts"]),
    ("QUOTE 引用行 ^>", re.compile(r"^>"), True,
     ["declared_counts", "no_regression"]),
    ("SPAN  引用スパン 「」", re.compile(r"「[^」]*」"), False,
     ["declared_counts", "no_regression"]),
]

# SPAN は引用行の中にあるかで意味が変わる。declared_counts / no_regression は
# 引用行の中しか数えないため、本文中に散っていても指標は動かない
QUOTE_LINE = re.compile(r"^>")
NESTED = "SPAN  引用スパン 「」"

# マーカーの有無では成立を判定できない検出器。別掲する
NOT_MARKER_DRIVEN = {
    "citation_presence": "数字を含む断定文があるかで決まる。REF は検出を抑制する側",
    "forbidden_phrases": "語の不在を見るので書式に依存しない",
}
# ──────────────────────────────────────────────────────────────


def measure(lines):
    counts, samples = {}, {}
    for name, pat, at_head, _ in MARKERS:
        hits = [(i, l) for i, l in enumerate(lines, 1)
                if (pat.match(l) if at_head else pat.search(l))]
        counts[name] = sum(1 if at_head else len(pat.findall(l)) for _, l in hits)
        if hits:
            samples[name] = hits[0]
    inside = sum(len(re.findall(r"「[^」]*」", l)) for l in lines if QUOTE_LINE.match(l))
    return counts, samples, inside


def main():
    paths = [Path(a) for a in sys.argv[1:]]
    if not paths:
        print(__doc__)
        return 2

    for p in paths:
        if not p.is_file():
            print(f"{p}: 見つからない")
            return 2
        lines = p.read_text(encoding="utf-8").splitlines()
        counts, samples, inside = measure(lines)

        print(f"\n{p.name} — {len(lines)}行。検出器の噛み合い")
        for name, _, _, deps in MARKERS:
            n = counts[name]
            mark = "  " if n else "⚠️"
            extra = ""
            if name == NESTED and n:
                extra = f"  ← うち引用行の中 {inside}件"
                if not inside:
                    extra += "（本文中に散っているだけ。指標は動かない）"
            print(f"  {mark} {name:<22} {n:>4}件{extra}")
            if s := samples.get(name):
                print(f"       初出 L{s[0]}: {s[1].strip()[:56]}")

        print("\n  検出器ごとの成立")
        for d in sorted({d for _, _, _, deps in MARKERS for d in deps}):
            mine = [n for n, _, _, deps in MARKERS if d in deps]
            live = [n for n in mine if counts[n]]
            if not live:
                v = "空振り。依存するマーカーが全てゼロ"
            elif len(live) < len(mine):
                dead = [n.split()[0] for n in mine if not counts[n]]
                v = f"一部の指標が動かない（{' / '.join(dead)} がゼロ）"
            else:
                v = "噛んでいる"
            print(f"    {d:<20} {v}")
        for d, why in NOT_MARKER_DRIVEN.items():
            print(f"    {d:<20} マーカーでは判定しない — {why}")

    print("\n保証しないこと")
    print("  - 噛んでいることは、正しく噛んでいることを意味しない。実測: 候補が全て")
    print("    出典エントリの見出しで、本当の欠陥は対象外だった（実験3）")
    print("  - 件数が妥当かは見ない。0 でないことしか見ていない")
    print("  - 閾値の感度は見ていない（1目的のため範囲外）。MIN_LEN 等は手で振る")
    print("\n判定はしない。噛んでいるかを決めるのは人である。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
