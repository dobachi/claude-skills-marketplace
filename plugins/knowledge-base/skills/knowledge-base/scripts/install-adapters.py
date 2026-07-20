#!/usr/bin/env python3
"""KBアダプタを各エージェントの設定ファイルへ設置する（最小・stdlibのみ）。

想起（読む）を暗黙に効かせるための薄いアダプタを、各エージェントが毎セッション
自動で読むファイルに追記する。作成・管理の詳細は knowledge-base スキルに委譲する。

- 追記であって上書きではない。マーカーで囲み、既にあれば中身だけ差し替える（冪等）。
- KBホームは絶対パスに解決して本文へ埋める（Windows/macOS/Linux でパスが自動で合う）。

使い方:
  python3 install-adapters.py                 # 既定: ~/.kb を指すアダプタを3ファイルへ
  python3 install-adapters.py --kb ~/work/kb  # KBホームを指定
  python3 install-adapters.py --kb C:/Users/me/.kb --also ./kb   # 追加のKBも Precedence に
  python3 install-adapters.py --dry-run       # 書かずに内容だけ表示

対象ファイル（既定）:
  ~/.claude/CLAUDE.md   (Claude Code)
  ~/.codex/AGENTS.md    (Codex, Antigravity/agy)
  ~/.gemini/GEMINI.md   (Gemini CLI, Antigravity/agy)
"""
import argparse
import os
import sys

START = "<!-- kb-adapter:start -->"
END = "<!-- kb-adapter:end -->"

TARGETS = [
    ("~/.claude/CLAUDE.md", "Claude Code"),
    ("~/.codex/AGENTS.md", "Codex / agy"),
    ("~/.gemini/GEMINI.md", "Gemini CLI / agy"),
]


def build_body(kb_paths):
    locs = " と ".join(f"`{p}`" for p in kb_paths)
    return (
        f"{START}\n"
        f"# ナレッジベース（KB）\n\n"
        f"永続知識は {locs} にある（作業中プロジェクトの `./kb/` も）。"
        f"一般知識で答える前に必ずKBを確認する:\n"
        f"各 `INDEX.md` を読み、必要なら grep。KB内の記述だけで答え、"
        f"無ければ「KBに記載なし」と言う。\n"
        f"KBの作成・編集・検証は knowledge-base スキルに従う。\n"
        f"{END}"
    )


def upsert(path, body, dry_run):
    """マーカー区間を追記 or 差し替え。既存内容は保持。返り値: created|updated|unchanged"""
    existing = ""
    exists = os.path.isfile(path)
    if exists:
        with open(path, encoding="utf-8") as f:
            existing = f.read()

    if START in existing and END in existing:
        pre = existing[: existing.index(START)]
        post = existing[existing.index(END) + len(END):]
        new = pre + body + post
        status = "unchanged" if new == existing else "updated"
    else:
        sep = "" if existing == "" or existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
        new = existing + sep + body + "\n"
        status = "created" if not exists else "updated"

    if not dry_run and status != "unchanged":
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return status


def main():
    ap = argparse.ArgumentParser(description="Install KB adapters into agent config files.")
    ap.add_argument("--kb", default="~/.kb", help="KB home (default: ~/.kb)")
    ap.add_argument("--also", action="append", default=[], help="extra KB path to include in precedence (repeatable)")
    ap.add_argument("--targets", nargs="*", help="override target files (default: the three agent configs)")
    ap.add_argument("--dry-run", action="store_true", help="print what would change; write nothing")
    args = ap.parse_args()

    kb_home = os.path.abspath(os.path.expanduser(args.kb))
    kb_paths = [kb_home] + [os.path.expanduser(p) for p in args.also]
    body = build_body(kb_paths)

    if args.dry_run:
        print("=== adapter body (dry-run) ===")
        print(body)
        print("=== targets ===")

    targets = args.targets if args.targets else [t[0] for t in TARGETS]
    labels = {t[0]: t[1] for t in TARGETS}
    for raw in targets:
        path = os.path.abspath(os.path.expanduser(raw))
        status = upsert(path, body, args.dry_run)
        label = labels.get(raw, "")
        print(f"  [{status:9}] {path}" + (f"  ({label})" if label else ""))

    if not args.dry_run:
        print("\nKB adapters installed. Start a new agent session to pick them up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
