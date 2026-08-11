#!/usr/bin/env python3
"""測定日つきの文書が、決めた間隔より古くなっていないかを見る。

`references/vendor-matrix.md` のような**腐る資料**が対象。
「使う前に再測定すること」と書いてあっても、書いてあるだけでは守られない。
実測: ベンダーのループ機構は前回測定から**1日で3行動いた**。

見るのは日付だけである。中身が実態と合っているかは見ない。

設計方針: 1目的 / 標準ライブラリのみ / 設定ファイルなし。

使い方:   python3 matrix_freshness.py <file>...
終了コード: 0=新しい  1=古い / 測定日が無い  2=引数エラー
"""

import re
import sys
from datetime import date
from pathlib import Path

# ─────────── 編集点: 期限と、測定日の書き方 ───────────
KIND = "spec"                                    # 日付の比較。実例は要らない
DATE = re.compile(r"測定日[:：]\s*(\d{4})-(\d{2})-(\d{2})")

# 再測定の約束。**推定ではなく約束である**。
# 「N日ごとに測り直す」と決めた数であって、N日なら正しいという意味ではない。
# 短くするほど再測定の手間が増える。伸ばすなら、伸ばした理由を文書に書き残すこと
MAX_AGE_DAYS = 14
# ──────────────────────────────────────────────────────


def main():
    paths = [Path(a) for a in sys.argv[1:]]
    if not paths:
        print(__doc__)
        return 2

    today, bad = date.today(), 0
    for p in paths:
        if not p.is_file():
            print(f"{p}: 見つからない")
            return 2
        if not (m := DATE.search(p.read_text(encoding="utf-8"))):
            print(f"\n{p.name} — 測定日が書かれていない。いつのものか分からない")
            bad += 1
            continue
        measured = date(*(int(g) for g in m.groups()))
        age = (today - measured).days
        over = age > MAX_AGE_DAYS
        bad += over
        print(f"\n{p.name} — 測定日 {measured}（{age}日前 / 期限 {MAX_AGE_DAYS}日）"
              + ("  ← 再測定すること" if over else ""))

    print("\n保証しないこと")
    print("  - 新しいことは、正しいことを意味しない。測定日を書き換えるだけで通る")
    print("  - 中身が実態と合っているかは見ない。日付しか見ていない")
    print("  - MAX_AGE_DAYS に客観的な根拠は無い。再測定の約束を数にしただけである")
    print(f"\n判定: {'NG' if bad else 'OK'}（{bad}件）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
