#!/usr/bin/env python3
"""本文の出典参照と出典表の対応を検査する。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下のブロックだけ）。

使い方:   python3 refs_integrity.py <file>...
終了コード: 0=整合  1=不整合あり  2=引数エラー
"""

import re
import sys
from collections import Counter
from pathlib import Path

# ─────────── 編集点: 文書の書式に合わせて書き換える ───────────
# 検出器の種類（ARCHITECTURE.md §3）。spec=仕様から書けるので実例は要らない
KIND = "spec"
# 出典表の行。1列目が出典ID
ROW = re.compile(r"^\|\s*(S-\d+)\s*\|")
# 本文中の参照記号
REF = re.compile(r"\[(S-\d+)\]")
# 表にあるが本文から参照されない出典を NG 扱いにするか。
# 参考文献リストを兼ねる文書では False にする
UNUSED_IS_NG = True
# 前提: 出典表も本文参照も0件なら、対応関係を見るものが無い＝何も検査していない。
# True=そのとき NG（既定）。書式の違う文書に当てて素通りする事故を塞ぐ配線であり、
# 緩めるなら「この文書は出典を持たない」と確認した記録を残すこと
REQUIRE_APPLICABLE = True
# ──────────────────────────────────────────────────────────────


def scan(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    table = [m.group(1) for l in lines if (m := ROW.match(l))]
    refs = Counter(s for l in lines if not ROW.match(l) for s in REF.findall(l))
    dup = [s for s, n in Counter(table).items() if n > 1]
    return table, refs, dup


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
        table, refs, dup = scan(p)
        if not table and not refs:
            print(f"\n{p.name} — 出典表0件 / 本文参照0件。測定できない")
            if REQUIRE_APPLICABLE:
                total += 1
                continue
            print("  ← REQUIRE_APPLICABLE=False のため判定対象外")
            continue
        undef = sorted(set(refs) - set(table))
        unused = sorted(set(table) - set(refs))
        bad = len(undef) + len(dup) + (len(unused) if UNUSED_IS_NG else 0)
        total += bad

        print(f"\n{p.name} — 本文{len(refs)}種 {sum(refs.values())}箇所 / 出典表{len(table)}件")
        print(f"  未定義（本文にあるが表に無い）  {len(undef)}件 {undef if undef else ''}")
        print(f"  未使用（表にあるが本文に無い）  {len(unused)}件 {unused if unused else ''}"
              + ("" if UNUSED_IS_NG else "  ← UNUSED_IS_NG=False のため判定対象外"))
        print(f"  ID重複                          {len(dup)}件 {dup if dup else ''}")

    print("\n保証しないこと")
    print("  - 参照先が主張の根拠として妥当かは見ない（対応関係だけを見る）")
    print("  - URL の生死・引用が原文に実在するかは見ない（別工程）")
    print("  - 参照記号が正しい位置に付いているかは見ない（citation_presence.py）")
    print("  - 書式（ROW / REF）が文書と合っているかは見ない。合っていなければ")
    print("    「測定できない」で落とす（REQUIRE_APPLICABLE）が、部分的なズレは拾えない")
    print(f"\n判定: {'NG' if total else 'OK'}（{total}件）")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
