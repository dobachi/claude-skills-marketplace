#!/usr/bin/env python3
"""Rebuild the binary fixtures with pandoc. Run once; the outputs are committed.
deck.pptx    — 4 slides, one with a table (pandoc's title placeholders)
report.docx  — nested headings H1..H3, a table, pandoc style ids (Heading1 …)
report-ja.docx — the same document with Japanese Word style ids ("1", name "見出し 1"):
                 the shape this repo never produces itself
"""
import re, shutil, subprocess, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = """\
% 四半期レビュー

# 要旨

- 結論: 計画どおり
- お願い: 予算の前倒し

# 進捗

| 項目 | 状態 |
|---|---|
| 設計 | 完了 |
| 実装 | 進行中 |

# 次の一手

来月までに検証を終える。
"""
REPORT = """\
---
title: 実施報告
---

表紙の文。

# 1. エグゼクティブサマリ

結論の段落。

## 1.1 結論

細部。

## 1.2 目的と結果

細部その2。

# 2. 当社の活動

活動の段落。

### 2.0.1 深い見出し

深い本文。

| # | 内容 |
|---|---|
| A1 | 論文化 |
"""


def run(*a):
    subprocess.run(a, check=True)


def main():
    assert shutil.which("pandoc"), "pandoc required"
    (HERE / "deck.md").write_text(DECK, encoding="utf-8")
    (HERE / "report.md").write_text(REPORT, encoding="utf-8")
    run("pandoc", str(HERE / "deck.md"), "-o", str(HERE / "deck.pptx"))
    run("pandoc", str(HERE / "report.md"), "-o", str(HERE / "report.docx"))
    # Japanese Word shape: style ids 1..9, names 見出し N
    src, dst = HERE / "report.docx", HERE / "report-ja.docx"
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename in ("word/document.xml", "word/styles.xml"):
                s = data.decode("utf-8")
                s = re.sub(r'w:styleId="Heading(\d)"', r'w:styleId="\1"', s)
                s = re.sub(r'w:val="Heading(\d)"', r'w:val="\1"', s)
                s = re.sub(r'<w:name w:val="heading (\d)"', r'<w:name w:val="見出し \1"', s)
                data = s.encode("utf-8")
            zo.writestr(item, data)
    (HERE / "deck.md").unlink()
    print("fixtures rebuilt")


if __name__ == "__main__":
    main()
