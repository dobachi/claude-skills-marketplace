#!/usr/bin/env python3
"""編集の前後を比べ、根拠の量が減っていないことを確かめる。

他の検出器はどれも「消せば満たせる」。ループの停止条件にするなら、
最短経路が削除にならないように下限を添える必要がある（HANDOVER §2.4-3）。

2026-08-08 の実験では削除は起きなかった。維持する根拠は「予測」ではなく
「比較がタダだから」であり、易しいケースで発火しないのは正常。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下のブロックだけ）。

使い方:   python3 no_regression.py <編集前> <編集後>
終了コード: 0=減っていない  1=減った  2=引数エラー
"""

import re
import sys
from pathlib import Path

# ─────────── 編集点: 文書の書式と、許す目減りを書き換える ───────────
QUOTE = re.compile(r"^>")
SPAN = re.compile(r"「[^」]*」")
ROW = re.compile(r"^\|\s*(S-\d+)\s*\|")
REF = re.compile(r"\[(S-\d+)\]")

# (項目名, 数え方). 「根拠の量」を代理する指標だけを置く
METRICS = [
    ("行数", lambda ls: len(ls)),
    ("引用行", lambda ls: sum(1 for l in ls if QUOTE.match(l))),
    ("引用スパン", lambda ls: sum(len(SPAN.findall(l)) for l in ls if QUOTE.match(l))),
    ("出典参照", lambda ls: sum(len(REF.findall(l)) for l in ls if not ROW.match(l))),
    ("出典表", lambda ls: sum(1 for l in ls if ROW.match(l))),
]

# 許容する減少量。整理で正当に減ることはあるので、項目ごとに緩められる
TOLERANCE = {"行数": 0, "引用行": 0, "引用スパン": 0, "出典参照": 0, "出典表": 0}

# 前提: 編集前**または編集後**に、ここに挙げた指標が1つでも1以上あること。
# 前後とも全部ゼロなら「行数」しか見ていない状態で、下限として機能していない。
# 編集前がゼロでも編集後に増えていれば比較は成立する（出典を新設する課題がこれ）。
# 書式が合っていれば、行数を保って中身を空にする書き換えは検出できる
# （実測: 引用スパン 90→0 / 出典参照 87→4 で NG）。塞ぐのは書式が合わない場合（§7.2）
SUBSTANCE = ["引用行", "引用スパン", "出典参照", "出典表"]

# そのうち「根拠の実体」。残り（出典参照・出典表）は追跡可能性の形式でしかない。
# 実測: 形式だけ増やして実体が 0→0 のまま、同じゲートを通った版がある（§7.11）
EVIDENCE = ["引用行", "引用スパン"]
REQUIRE_APPLICABLE = True
# ────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    before, after = Path(sys.argv[1]), Path(sys.argv[2])
    for p in (before, after):
        if not p.is_file():
            print(f"{p}: 見つからない")
            return 2

    b = before.read_text(encoding="utf-8").splitlines()
    a = after.read_text(encoding="utf-8").splitlines()

    print(f"\n{before.name} → {after.name}")
    bad = 0
    if not any(c(b) or c(a) for lbl, c in METRICS if lbl in SUBSTANCE):
        print(f"  編集前にも編集後にも {' / '.join(SUBSTANCE)} が1件も無い。"
              "行数しか見ておらず、下限として機能していない")
        if REQUIRE_APPLICABLE:
            print("\n判定: NG（測定できない）")
            return 1
        print("  ← REQUIRE_APPLICABLE=False のため続行")
    for label, count in METRICS:
        nb, na = count(b), count(a)
        allowed = TOLERANCE.get(label, 0)
        over = (nb - na) > allowed
        bad += over
        mark = "NG" if over else "OK"
        print(f"  {mark:<4} {label:<12} {nb:>5} → {na:<5} ({na - nb:+d})"
              + (f"  ← {allowed}件までしか許さない" if over else ""))

    # 「減っていないこと」の裏返し。増えていないことは咎めないが、黙ってもいない。
    # 実測: 根拠を5件足した版と1件も足していない版が、同じゲートを両方通った（§7.11）
    grew = {lbl: c(a) - c(b) for lbl, c in METRICS if lbl in EVIDENCE}
    if grew and max(grew.values()) <= 0:
        print("  ※ 根拠の実体は増えていない（" +
              " / ".join(f"{k} {v:+d}" for k, v in grew.items()) + "）。"
              "増えたのは追跡可能性の形式だけである")
        print("    この検査は減っていないことしか見ない。増えていないことは NG にしない")

    print("\n保証しないこと")
    print("  - 数が保たれることは、中身が保たれることを意味しない")
    print("    （引用を別の引用に差し替えても、水増ししても通る）")
    print("  - 増えたことは改善を意味しない。逆に増えていなくても NG にはしない")
    print("  - 何を「根拠の量」と見なすかは METRICS の設計しだい")
    print(f"\n判定: {'NG' if bad else 'OK'}（目減り {bad}項目）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
