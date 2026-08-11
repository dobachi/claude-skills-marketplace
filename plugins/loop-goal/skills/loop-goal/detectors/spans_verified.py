#!/usr/bin/env python3
"""照合の台帳が、文書の参照を覆っているかを見る。**ゲートに入れる側。**

照合そのもの（ネットワーク）は span_verify.py がループの外で済ませる。
こちらはその結果を読むだけなので、オフラインで秒で終わり、決定的である。

**台帳はループの書き込み範囲の外に置くこと。** 同じ木の中にあると、
最短経路が「台帳に済と書く」になる。検出器を read-only にするのと同じ理由。

使い方:   python3 spans_verified.py <file> <台帳>
終了コード: 0=覆えている  1=不足または不一致あり  2=引数エラー
"""

import re
import sys
from pathlib import Path

# ─────────── 編集点: 文書の書式と、通す判定 ───────────
KIND = "spec"
ROW = re.compile(r"^\|\s*(S-\d+)\s*\|")
REF = re.compile(r"\[(S-\d+)\]")

OK_MARKS = ("済",)          # これだけを合格と見なす
# 取得失敗を合格にしない。すると「ネットを切れば通る」が最短経路になる
BAD_PREFIX = ("不一致", "取得失敗", "URL不明")

# 引用を伴わない出典（言い換えだけで参照されているもの）を NG にするか。
# True にすると、言い換えの参照を全て引用付きに直すまで通らない。
# 既定は False — 言い換えの妥当性は第4層であり、ここで判定するものではない。
# ただし件数は必ず出す（見ていない範囲として残す）
UNQUOTED_IS_NG = False
REQUIRE_APPLICABLE = True   # 文書に参照が1つも無ければ「測定できない」
# ────────────────────────────────────────────────────────


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    doc, led = Path(sys.argv[1]), Path(sys.argv[2])
    for p in (doc, led):
        if not p.is_file():
            print(f"{p}: 見つからない")
            return 2

    lines = doc.read_text(encoding="utf-8").splitlines()
    refs = {m for l in lines for m in REF.findall(l) if not ROW.match(l)}
    print(f"\n{doc.name} — 本文が参照する出典 {len(refs)}種 / 台帳 {led.name}")

    if not refs:
        print("  参照が0件。覆うべき対象が無く、測定できない")
        if REQUIRE_APPLICABLE:
            print("\n判定: NG（測定できない）")
            return 1
        print("  ← REQUIRE_APPLICABLE=False のため判定対象外")

    entries = {}
    for row in led.read_text(encoding="utf-8").splitlines():
        if not row.strip() or row.lstrip().startswith("#"):
            continue                                # 空行と由来コメントは読み飛ばす
        sid, verdict = (row.split("\t") + ["", ""])[:2]
        entries.setdefault(sid, []).append(verdict)

    bad = 0
    for sid in sorted(refs):
        vs = entries.get(sid)
        if not vs:
            print(f"  未照合   {sid}  台帳に無い（引用を伴わない参照）")
            bad += UNQUOTED_IS_NG
            continue
        ng = [v for v in vs if v.startswith(BAD_PREFIX)]
        ok = [v for v in vs if v in OK_MARKS]
        if ng:
            print(f"  NG       {sid}  {' / '.join(sorted(set(ng)))}")
            bad += 1
        elif ok:
            print(f"  済       {sid}  {len(ok)}件の引用が原文と一致")
        else:
            print(f"  不明     {sid}  台帳の判定が読めない: {vs}")
            bad += 1

    unquoted = sum(1 for s in refs if s not in entries)
    print(f"\n  引用を伴わない参照 {unquoted}種"
          + ("（NG 扱い）" if UNQUOTED_IS_NG else "（判定対象外。人か別工程が見る）"))

    print("\n保証しないこと")
    print("  - 台帳が正しいかは見ない。span_verify.py の出力を信じている")
    print("  - 引用が原文にあることは、その引用が主張を支えることを意味しない")
    print("  - 言い換えだけの参照は既定では通す。**そこが見ていない範囲である**")
    print("  - 台帳が古いかは見ない。文書を直したら照合し直すこと")
    print(f"\n判定: {'NG' if bad else 'OK'}（{bad}件）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
