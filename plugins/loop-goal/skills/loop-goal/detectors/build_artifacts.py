#!/usr/bin/env python3
"""ビルド生成物の実体を見る。終了コードとファイル数だけでは通ってしまう欠陥を拾う。

このリポジトリの `make check` は `hexo generate` の終了コードしか見ないため、
1117ファイル全部が0バイトでも「✅ ビルド成功」と表示する（KB: verification-not-exit-code）。
数えるのはファイル名ではなく中身。

設計方針: 1目的 / 標準ライブラリのみ / 読み切れる長さ / 設定ファイルなし。
定数を書き換えて使うことを前提にしている（編集点は下のブロックだけ）。

使い方:   python3 build_artifacts.py [生成ディレクトリ]
終了コード: 0=実体あり  1=欠陥あり  2=引数エラー
"""

import sys
from pathlib import Path

# ─────────── 編集点: プロジェクトごとに書き換える ───────────
OUT_DIR = "public"          # 既定の生成ディレクトリ
MIN_FILES = 100             # これを下回るなら生成が途中で死んでいる
MAX_EMPTY = 0               # 0バイトファイルの許容数
MIN_BYTES = 512             # 必須ファイルがこれ未満なら中身が無いとみなす

# 必ず生成され、かつ中身を持つべきファイル（生成ディレクトリからの相対パス）
REQUIRED = ["index.html"]

# 陽性対照。ここに出ない語を探しても意味がないことを先に確かめる。
# (ファイル, 含まれるべき文字列)
EXPECT = [("index.html", "<title")]
# ──────────────────────────────────────────────────────────


def check(root):
    files = [p for p in root.rglob("*") if p.is_file()]
    empty = [p for p in files if p.stat().st_size == 0]
    ng = []

    print(f"\n{root} — ファイル {len(files)}件 / 0バイト {len(empty)}件")
    if len(files) < MIN_FILES:
        ng.append(f"ファイル数 {len(files)} < {MIN_FILES}")
    if len(empty) > MAX_EMPTY:
        ng.append(f"0バイト {len(empty)}件 > 許容 {MAX_EMPTY}")
        for p in empty[:5]:
            print(f"       空: {p.relative_to(root)}")
        if len(empty) > 5:
            print(f"       … 他 {len(empty) - 5}件")

    for rel in REQUIRED:
        p = root / rel
        if not p.is_file():
            ng.append(f"{rel} が無い")
        elif p.stat().st_size < MIN_BYTES:
            ng.append(f"{rel} が {p.stat().st_size}バイト < {MIN_BYTES}")

    for rel, needle in EXPECT:
        p = root / rel
        if not p.is_file():
            ng.append(f"{rel} が無く、陽性対照 '{needle}' を確かめられない")
        elif needle not in p.read_text(encoding="utf-8", errors="replace"):
            ng.append(f"{rel} に陽性対照 '{needle}' が無い")

    for m in ng:
        print(f"  NG   {m}")
    if not ng:
        print("  OK   ファイル数・0バイト・必須ファイル・陽性対照 すべて充足")
    return len(ng)


def main():
    args = sys.argv[1:]
    if len(args) > 1:
        print(__doc__)
        return 2
    root = Path(args[0] if args else OUT_DIR)
    if not root.is_dir():
        print(f"{root}: ディレクトリが無い。ビルドが走っていない可能性がある")
        return 1

    bad = check(root)

    print("\n保証しないこと")
    print("  - 中身が正しいことは見ない。空でないこと・語が在ることまで")
    print("  - 古い生成物が残っていても通る。`clean` してから走らせること")
    print("  - EXPECT に挙げた語しか確かめない。挙げ忘れた壊れ方は素通りする")
    print(f"\n判定: {'NG' if bad else 'OK'}（{bad}件）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
