#!/usr/bin/env python3
"""文書が自分で申告している件数と、実測値の一致を検査する。

集計を書いたあとに本文を編集すると、申告値だけが古くなる。
実際に「86→90」のずれを出荷しかけた（設計への示唆 §4）。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下のブロックだけ）。

使い方:   python3 declared_counts.py <file>...
終了コード: 0=一致  1=不一致あり  2=引数エラー
"""

import re
import sys
from pathlib import Path

# ─────────── 編集点: 文書の書式に合わせて書き換える ───────────
KIND = "spec"                                  # ARCHITECTURE.md §3。仕様から書ける
# 前提: 申告が1つも見つからなければ、一致を検査する相手が無い＝何も見ていない。
# True=そのとき NG（既定）。「集計節ごと消せば黙って通る」を塞ぐ配線
REQUIRE_APPLICABLE = True
QUOTE = re.compile(r"^>")                      # 引用行
SPAN = re.compile(r"「[^」]*」")                # 引用スパン
ROW = re.compile(r"^\|\s*(S-\d+)\s*\|")        # 出典表の行
FETCH_FAIL = "⚠️"                              # 出典表で取得不能を示す印

# (項目名, 申告値を拾う正規表現, 実測する関数)
# 実測できない申告（FOUND 件数など）はここに入れない。入れると嘘になる
CHECKS = [
    ("本文中の引用",
     re.compile(r"本文中の引用\s*\|\s*\*{0,2}(\d+)\*{0,2}"),
     lambda ls: sum(len(SPAN.findall(l)) for l in ls if QUOTE.match(l))),
    ("取得不能(FETCH-FAIL)",
     re.compile(r"取得不能.*?\|\s*\*{0,2}(\d+)\*{0,2}"),
     lambda ls: sum(1 for l in ls if ROW.match(l) and FETCH_FAIL in l)),
]
# ──────────────────────────────────────────────────────────────


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
        lines = p.read_text(encoding="utf-8").splitlines()
        print(f"\n{p.name}")
        found = 0
        for label, pat, measure in CHECKS:
            actual = measure(lines)
            hit = [m.group(1) for l in lines if (m := pat.search(l))]
            if not hit:
                print(f"  --   {label:<22} 申告が見つからない（実測 {actual}）")
                continue
            found += 1
            declared = int(hit[-1])
            ok = declared == actual
            total += 0 if ok else 1
            print(f"  {'OK' if ok else 'NG':<4} {label:<22} 申告 {declared} / 実測 {actual}"
                  + ("" if ok else "  ← 不一致")
                  + ("  ← 0 申告。一致するが何も数えていない" if ok and declared == 0 else ""))
        if not found:
            print("  申告が1つも見つからない。一致を検査する相手が無く、測定できない")
            if REQUIRE_APPLICABLE:
                total += 1
            else:
                print("  ← REQUIRE_APPLICABLE=False のため判定対象外")

    print("\n保証しないこと")
    print("  - 実測側の数え方が正しいかは保証しない（SPAN の定義しだいで動く）")
    print("  - 申告が見つからないことは合格ではない。REQUIRE_APPLICABLE で落とすが、")
    print("    CHECKS の一部だけ消した場合は残りの項目で通ってしまう")
    print("  - 引用が原文に実在するか・出典が妥当かは見ない（別工程）")
    print("  - **0 と申告すれば実測0と一致して通る。** 数字は出すが NG にはしない")
    print("    （0 が妥当な文書もあるため。実測: 上限を迫った条件でこの経路が選ばれた）")
    print(f"\n判定: {'NG' if total else 'OK'}（{total}件）")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
