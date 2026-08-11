#!/usr/bin/env python3
"""検出器のひな型。コピーして冒頭の編集点だけ書き換える。

このままでも動く（TODO / FIXME の残りを検出する）。動く状態から削るほうが早い。
設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
関数本体は触らなくてよい。編集点は下のブロックだけ。

使い方:   python3 _template.py <file>...
終了コード: 0=OK  1=NG  2=引数エラー / 出荷前の未記入
"""

import re
import sys
from pathlib import Path

# ═══════════ 編集点 ここから ═══════════

# 【1】検出器の種類（ARCHITECTURE.md §3）
#   "spec"    仕様から書ける判定（対応関係・数の一致・存在確認）。実例なしで先に書いてよい
#   "example" 実例からしか書けない判定（ヒューリスティック・除外リスト・閾値）
KIND = "example"

# 下段（example）の由来。実際に取り逃した欠陥を1行で書く。
# 「〜が起きそう」は由来にならない。空のまま出荷すると exit 2 で落ちる
ORIGIN = "書きかけの印を消し忘れて出荷しかけた"

# 【2】前提 — これが文書に無ければ、この検出器は測定していない。
# (名前, 正規表現, 最低件数)。1つでも満たさなければ「測定できない」
REQUIRED_MARKERS = []

# 前提を満たさないときの向き。True=NG（既定）。
# 空振りを合格として返さないための配線であり、緩めるなら理由を書き残すこと
REQUIRE_APPLICABLE = True

# 【3】検出する対象。(正規表現, なぜ問題か)
PATTERNS = [
    (re.compile(r"TODO|FIXME"), "書きかけの印。出荷前に消す"),
]

# 人が確認して残すと決めた件数。0 のまま回すと「消せば通る」が最短経路になりうる。
# no_regression.py と併用する
ALLOWED = 0
SHOW = 8                       # 表示する件数
SKIP_PREFIX = ()               # 対象外にする行頭（"#", "|", ">" など）

# 【4】この検出で見ていない範囲。編集した人が限界を引き継ぐために必ず書く
NOT_GUARANTEED = [
    "印が無いことは、書きかけでないことを意味しない（別の言い回しは通る）",
    "消しても満たせる。書き換えたのか削除したのかは判定しない",
]

# ═══════════ 編集点 ここまで ═══════════


def applicable(lines):
    missing = []  # 前提を満たさないマーカー。空なら測定できる
    for name, pat, least in REQUIRED_MARKERS:
        if sum(1 for l in lines if pat.search(l)) < least:
            missing.append(f"{name}（{least}件以上）")
    return missing


def scan(lines):
    hits = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if SKIP_PREFIX and s.startswith(SKIP_PREFIX):
            continue
        for pat, why in PATTERNS:
            if m := pat.search(line):
                hits.append((i, m.group(0), why, s))
                break
    return hits


def main():
    if KIND not in ("spec", "example"):
        print(f"KIND が不正: {KIND!r}")
        return 2
    if KIND == "example" and not ORIGIN.strip():
        print("ORIGIN が空。実例からしか書けない検出器は、由来を書かずに出荷しない")
        return 2
    paths = [Path(a) for a in sys.argv[1:]]
    if not paths:
        print(__doc__)
        return 2

    total = 0
    for p in paths:
        if not p.is_file():
            print(f"{p}: 見つからない")
            return 2
        lines = p.read_text(encoding="utf-8").splitlines()

        if missing := applicable(lines):
            print(f"\n{p.name} — 前提を満たさない: {' / '.join(missing)}。測定できない")
            if REQUIRE_APPLICABLE:
                total += 1
                continue
            print("  ← REQUIRE_APPLICABLE=False のため判定対象外")
            continue

        hits = scan(lines)
        total += max(0, len(hits) - ALLOWED)
        print(f"\n{p.name} — 該当 {len(hits)}件（許容 {ALLOWED}）")
        for i, hit, why, line in hits[:SHOW]:
            print(f"  L{i:<5} {hit}  — {why}")
            print(f"        {line[:70]}")
        if len(hits) > SHOW:
            print(f"  … 他 {len(hits) - SHOW}件")

    print("\n保証しないこと")
    for s in NOT_GUARANTEED:
        print(f"  - {s}")
    print(f"\n判定: {'NG' if total else 'OK'}（{total}件）")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
