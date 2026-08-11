#!/usr/bin/env python3
"""数字を含む断定文に、引用も出典参照も付いていない箇所を挙げる。

ヒューリスティック。断定か否かの機械判定は不可能なので、候補を出すだけで
確定はしない。ヘッジを削るときに根拠まで一緒に落とす事故（設計への示唆 §1）を
拾うのが目的。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下のブロックだけ）。

使い方:   python3 citation_presence.py <file>...
終了コード: 0=候補が許容数以下  1=超過  2=引数エラー
"""

import re
import sys
from pathlib import Path

# ─────────── 編集点: 文書の書式に合わせて書き換える ───────────
QUOTE = re.compile(r"^>")                  # 引用行。この直後にあれば根拠付きと見なす
REF = re.compile(r"\[S-\d+\]")             # 文中の出典参照
NUM = re.compile(r"[0-9０-９]")             # 数字を含む文だけを対象にする（参照記号は除く）
SKIP_PREFIX = ("#", "|", "-", "*", "`", ">")   # 見出し・表・箇条書きは対象外
SKIP_MARK = ("【推】",)                     # 推測と明示した文は対象外
MIN_LEN = 25                               # これより短い行は見出し断片とみなす

# 事実を報告せず、方法や書式を説明する節。見出しに含まれる文字列で指定する。
# ここを広げるほど検出は緩む。緩めた範囲は「見ていない範囲」として残る
SKIP_SECTIONS = ("Source Register", "検証方法と限界", "この文書の読み方")

# 人が確認して残すと決めた候補数。ループの停止条件にするならここを基準にする。
# 0 のまま回すと「消せば通る」が最短経路になりうる。no_regression.py と併用する
# 参照が付いているために候補から外れた行を数えるか。
# ゲートが実際に要求した参照の量が分かる。実測: 要求5行に対し43箇所付いた（§7.9）
COUNT_SUPPRESSED = True
ALLOWED = 0
SHOW = 8                                   # 表示する件数
# ──────────────────────────────────────────────────────────────


def scan(lines):
    out, suppressed, fence, skip_level = [], [], False, 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if s.startswith("#"):
            level = len(s) - len(s.lstrip("#"))
            if skip_level and level <= skip_level:      # 同レベル以上の見出しで解除
                skip_level = 0
            if not skip_level and any(k in s for k in SKIP_SECTIONS):
                skip_level = level                      # 下位の見出しごと対象外
        if fence or skip_level:
            continue
        if not s or s.startswith(SKIP_PREFIX) or any(m in s for m in SKIP_MARK):
            continue
        bare = REF.sub("", s)                       # 参照記号 [S-09] の数字を
        if len(bare) < MIN_LEN or not NUM.search(bare):   # 「断定の数字」と数えない
            continue
        j = i + 1                                   # 空行を挟んで引用が続くか
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and QUOTE.match(lines[j].strip()):
            continue                                # 引用で足りている。参照の有無は無関係
        if REF.search(s):
            suppressed.append(i + 1)                # 参照が無ければ候補になった行
            continue
        out.append((i + 1, s))
    return out, suppressed


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
        hits, suppressed = scan(lines)
        total += len(hits)
        print(f"\n{p.name} — 引用の欠落候補 {len(hits)}件（許容 {ALLOWED}）")
        for ln, s in hits[:SHOW]:
            print(f"  ?    L{ln:<5} {s[:60]}")
        if len(hits) > SHOW:
            print(f"       … 他 {len(hits) - SHOW}件")
        if COUNT_SUPPRESSED:
            refs = sum(len(REF.findall(l)) for l in lines)
            print(f"  この検査が実際に要求した参照: {len(suppressed)}行分"
                  f" / 文書中の参照 {refs}件")
            if len(suppressed) < refs:
                print(f"    → 差の {refs - len(suppressed)}件はこの検査が要求していない。"
                      "多いことが悪いとは限らないが、人が読む")

    print("\n保証しないこと")
    print("  - 断定か否かの機械判定は不可能。ここに出ないことは根拠があることを意味しない")
    print("  - 直後に引用があることは、その引用が当の主張を支えることを意味しない")
    print("  - 文を消しても数は減る。書き換えたのか削除したのかは判定しない")
    print("  - 参照が多すぎることは検出しない。要求した行数を出すだけで、判定はしない")
    print(f"  - SKIP_SECTIONS{list(SKIP_SECTIONS)} の節は見ていない")
    print(f"\n判定: {'NG' if total > ALLOWED else 'OK'}（{total}件 / 許容 {ALLOWED}）")
    return 1 if total > ALLOWED else 0


if __name__ == "__main__":
    sys.exit(main())
