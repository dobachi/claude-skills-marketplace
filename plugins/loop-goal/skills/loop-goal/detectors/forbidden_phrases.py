#!/usr/bin/env python3
"""禁止語の混入を検出する。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下の FORBIDDEN だけ）。

使い方:   python3 forbidden_phrases.py <file>...
終了コード: 0=検出なし  1=検出あり  2=引数エラー
           ループの停止条件にそのまま使える。
"""

import re
import sys
from pathlib import Path

# ─────────── 編集点: プロジェクトごとに書き換える ───────────
# (正規表現, なぜ禁止か)
FORBIDDEN = [
    (r"【訂正】|【訂正・重要】", "訂正注記。経緯ではなく結論を書く"),
    (r"初版|前版|旧版", "執筆経緯。本文には残さない"),
    (r"としていたが|と書いたが|と記載したが", "執筆経緯の言い回し"),
]

# 対象外にするパス（部分一致）。
# 執筆経緯そのものを主題にする文書は、同じ語を正当に含む。
# 上の FORBIDDEN は「調査報告書」向けの設定であり、万能ではない。
SKIP_PATHS = ["design-implications", "HANDOVER", "fact-check-report"]
# ──────────────────────────────────────────────────────────


def scan(path):
    hits = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for pat, why in FORBIDDEN:
            if m := re.search(pat, line):
                hits.append((i, m.group(0), why, line.strip()))
                break
    return hits


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
        if any(s in str(p) for s in SKIP_PATHS):
            print(f"\n{p.name} — 対象外（SKIP_PATHS）")
            continue
        hits = scan(p)
        total += len(hits)
        print(f"\n{p.name} — 禁止語 {len(hits)}件")
        for ln, word, why, text in hits:
            print(f"  L{ln:<5} 「{word}」  {why}")
            print(f"         {text[:68]}")

    print("\n保証しないこと")
    print("  - 語が無いことは、経緯が書かれていないことを意味しない（別の言い回しは通る）")
    print("  - 消しても満たせる。書き換えたのか削除したのかは判定しない")
    print(f"\n判定: {'NG' if total else 'OK'}（{total}件）")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
