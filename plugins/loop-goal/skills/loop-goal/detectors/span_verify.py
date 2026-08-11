#!/usr/bin/env python3
"""引用スパンが出典の原文に実在するかを照合する。**ループの外で回す。**

ネットワークに触るので、遅く・非決定的で・失敗しうる。ゲートに入れると
「全部走らせても秒で終わる」前提が崩れ、取得失敗の扱いが fail-open か
「ネットが落ちたら止まる」の二択になる。だから照合はここで済ませ、
結果を台帳に落とす。ゲートは台帳を見る（spans_verified.py）。

**台帳はループの書き込み範囲の外に置く。** 満たす側が「済」と書けてはいけない。
見るのは引用の忠実さであって事実の正しさではない。言い換えだけの参照は
照合する断片が無いので対象外になる（件数は出す）。

使い方:   python3 span_verify.py <file> [台帳の出力先]
終了コード: 0=全て照合できた  1=照合できない引用がある  2=引数エラー
"""

import html
import re
import sys
import urllib.request
from pathlib import Path

# ─────────── 編集点: 文書の書式と、取得の設定 ───────────
KIND = "spec"
ROW = re.compile(r"^\|\s*(S-\d+)\s*\|")        # 出典表の行
REF = re.compile(r"\[(S-\d+)\]")               # 参照記号
QUOTE = re.compile(r"^>\s?(.*)")               # 引用行。group(1) が中身
URL = re.compile(r"https?://[^\s)\]<>「」]+")   # 出典の URL

MIN_SPAN = 12          # これより短い引用は一致しても意味を持たない
HEAD, TIMEOUT = 400_000, 20    # 取得する最大バイト数 / 秒
UA = "Mozilla/5.0 (span_verify)"
TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S | re.I)
WS = re.compile(r"[\s　]+")
# ──────────────────────────────────────────────────────────


def normalize(s):
    # エンティティを戻さないと `Data &amp; Privacy` が逐語一致でも不一致になる（実測）
    return WS.sub("", html.unescape(TAG.sub(" ", s)))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read(HEAD)
    return normalize(raw.decode("utf-8", "replace"))


def collect(lines):
    """(出典ID, 引用スパン) を集める。直前の参照記号を出典とみなす。"""
    urls, spans, last = {}, [], None
    for line in lines:
        if m := ROW.match(line):
            if u := URL.search(line):
                urls[m.group(1)] = u.group(0)
        if r := REF.findall(line):
            last = r[-1]
        if (q := QUOTE.match(line.strip())) and last:
            if len((s := q.group(1).strip())) >= MIN_SPAN:
                spans.append((last, s))
        if (u := URL.search(line)) and last:        # 直前の参照記号に結び付ける
            urls.setdefault(last, u.group(0))
    return urls, spans


def main():
    if not (1 <= len(sys.argv) - 1 <= 2):
        print(__doc__)
        return 2
    doc = Path(sys.argv[1])
    if not doc.is_file():
        print(f"{doc}: 見つからない")
        return 2
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else doc.with_suffix(".verified")

    lines = doc.read_text(encoding="utf-8").splitlines()
    urls, spans = collect(lines)
    refs = {m for l in lines for m in REF.findall(l) if not ROW.match(l)}
    print(f"\n{doc.name} — 参照 {len(refs)}種 / 引用スパン {len(spans)}件 / URL {len(urls)}件")
    if without := len(refs) - len({s for s, _ in spans}):
        print(f"  引用を伴わない出典 {without}種。**照合できない。**")
        print("  参照先が主張を支えるかは人か別工程が見る（第4層と同じ扱い）")

    cache, ledger, bad = {}, [], 0
    for sid, span in spans:
        if not (u := urls.get(sid)):
            v = "URL不明"
        else:
            if u not in cache:
                try:
                    cache[u] = fetch(u)
                except Exception as e:                       # noqa: BLE001
                    cache[u] = f"__FETCH_FAIL__{type(e).__name__}"
            body = cache[u]
            if body.startswith("__FETCH_FAIL__"):
                v = f"取得失敗({body[14:]})"
            elif normalize(span) in body:
                v = "済"
            else:
                v = "不一致"
        if v not in ("済",):
            bad += 1                                # 照合できていないものを OK にしない
        print(f"  {v:<16} {sid}  {span[:44]}")
        ledger.append(f"{sid}\t{v}\t{span[:60]}")

    out.write_text("\n".join(ledger) + "\n", encoding="utf-8")
    print(f"\n台帳: {out}（{len(ledger)}行）")
    print("\n保証しないこと")
    print("  - 引用が原文にあることは、その引用が当の主張を支えることを意味しない")
    print("  - 翻訳された引用は原文と一致しない。日本語訳は「不一致」になる")
    print("  - 一致は文字列の一致でしかない。文脈を無視した切り出しは検出しない")
    print("  - 取得失敗は「済」にしない。ページが変われば結果も変わる")
    print("  - PDF は読めない（HTML のみ）。URL不明・取得失敗は「済」にしない")
    print(f"\n判定: {'NG' if bad else 'OK'}（照合できていない引用 {bad}件 / 全{len(spans)}件）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
