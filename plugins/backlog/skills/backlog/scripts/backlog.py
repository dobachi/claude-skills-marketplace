#!/usr/bin/env python3
"""backlog — a lightweight, persistent "do it later" inbox.

Hybrid storage, resolved from the current working directory:
  * inside a git repo -> <repo-root>/BACKLOG.md   (shared via git)
  * otherwise         -> ~/.claude/backlog.md      (personal inbox)

`list` shows BOTH the current repo's file and the personal inbox so nothing is
ever hidden. Completed items are swept out with `archive`.

stdlib only; cross-agent (works the same under Claude Code, Codex, agy).
Dates come from the local clock; the caller may pass --date to override.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
GLOBAL_FILE = HOME / ".claude" / "backlog.md"
REPO_BASENAME = "BACKLOG.md"
HEADER = "# Backlog\n\n"

ITEM_RE = re.compile(r"^\s*- \[(?P<done>[ xX])\]\s*(?P<date>\d{4}-\d{2}-\d{2})?\s*(?P<text>.*?)\s*$")

_TODAY_OVERRIDE = None


def today() -> str:
    return _TODAY_OVERRIDE or datetime.date.today().isoformat()


def repo_root() -> Path | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=os.getcwd(),
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except Exception:
        pass
    return None


def archive_path(active: Path) -> Path:
    # BACKLOG.md -> BACKLOG.archive.md ; backlog.md -> backlog.archive.md
    return active.with_name(active.stem + ".archive" + active.suffix)


def resolve_single(scope: str) -> tuple[str, Path]:
    """The one store add/done/drop/archive act on."""
    r = repo_root()
    if scope == "global":
        return ("global", GLOBAL_FILE)
    if scope == "repo":
        if not r:
            sys.exit("backlog: not inside a git repository (use -g for the personal inbox)")
        return ("repo", r / REPO_BASENAME)
    return ("repo", r / REPO_BASENAME) if r else ("global", GLOBAL_FILE)


def resolve_many(scope: str) -> list[tuple[str, Path]]:
    """The stores `list`/`find` display: repo (if any) + personal inbox."""
    r = repo_root()
    if scope == "global":
        return [("global", GLOBAL_FILE)]
    if scope == "repo":
        if not r:
            sys.exit("backlog: not inside a git repository (use -g for the personal inbox)")
        return [("repo", r / REPO_BASENAME)]
    stores: list[tuple[str, Path]] = []
    if r:
        stores.append(("repo", r / REPO_BASENAME))
    stores.append(("global", GLOBAL_FILE))
    return stores


def load(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def save(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(lines).rstrip("\n") + "\n"
    if not body.lstrip().startswith("# Backlog"):
        body = HEADER + body
    path.write_text(body, encoding="utf-8")


def parse_item(line: str):
    m = ITEM_RE.match(line)
    if not m:
        return None
    return {
        "done": m.group("done").lower() == "x",
        "date": m.group("date") or "",
        "text": m.group("text").strip(),
    }


def _label(label: str, path: Path, open_count: int) -> str:
    if label == "repo":
        return f"\U0001F4CB このリポジトリ  {path} — 未完了 {open_count}"
    return f"\U0001F310 個人インボックス  {path} — 未完了 {open_count}"


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_add(args) -> int:
    label, store = resolve_single(args.scope)
    text = " ".join(args.text).strip()
    if not text:
        sys.exit("backlog: nothing to add")
    for t in (args.tag or []):
        tag = t if t.startswith("#") else "#" + t
        if tag not in text:
            text += " " + tag
    lines = load(store) or [HEADER.rstrip("\n")]
    item = f"- [ ] {today()} {text}"
    lines.append(item)
    save(store, lines)
    print(f"➕ 追加 ({label}): {store}\n   {item}")
    return 0


def cmd_list(args) -> int:
    stores = resolve_many(args.scope)
    n = 0
    for label, path in stores:
        items = [it for it in (parse_item(l) for l in load(path)) if it]
        open_items = [it for it in items if not it["done"]]
        shown = items if args.all else open_items
        print(_label(label, path, len(open_items)))
        if not shown:
            print("   （なし）")
        for it in shown:
            n += 1
            box = "[x]" if it["done"] else "[ ]"
            print(f"   {n:>2}. {box} {it['date']}  {it['text']}")
        print()
    return 0


def _matches(scope: str, query: str, include_done: bool):
    q = query.lower()
    hits = []
    for label, path in resolve_many(scope):
        lines = load(path)
        for idx, raw in enumerate(lines):
            it = parse_item(raw)
            if not it:
                continue
            if not include_done and it["done"]:
                continue
            if q in it["text"].lower():
                hits.append((label, path, idx, raw, it))
    return hits


def _print_candidates(hits) -> None:
    print("複数一致しました。語をもっと具体的にしてください:", file=sys.stderr)
    for label, path, _idx, _raw, it in hits:
        print(f"   [{label}] {it['text']}", file=sys.stderr)


def cmd_find(args) -> int:
    hits = _matches(args.scope, " ".join(args.query), include_done=True)
    if not hits:
        print("一致なし")
        return 0
    for label, _path, _idx, _raw, it in hits:
        box = "[x]" if it["done"] else "[ ]"
        print(f"[{label}] {box} {it['date']}  {it['text']}")
    return 0


def cmd_done(args) -> int:
    query = " ".join(args.query)
    hits = _matches(args.scope, query, include_done=False)
    if not hits:
        sys.exit(f"一致する未完了項目なし: {query}")
    if len(hits) > 1:
        _print_candidates(hits)
        return 2
    _label_, path, idx, _raw, it = hits[0]
    lines = load(path)
    lines[idx] = f"- [x] {it['date']} {it['text']} (done: {today()})"
    save(path, lines)
    print(f"☑️ 完了: {it['text']}")
    return 0


def cmd_drop(args) -> int:
    query = " ".join(args.query)
    hits = _matches(args.scope, query, include_done=True)
    if not hits:
        sys.exit(f"一致なし: {query}")
    if len(hits) > 1:
        _print_candidates(hits)
        return 2
    _label_, path, idx, raw, it = hits[0]
    if not args.yes:
        # Refuse to delete without confirmation; print the target for a preview.
        print(f"削除対象: {it['text']}")
        print("確認のうえ --yes を付けて再実行してください。", file=sys.stderr)
        return 3
    lines = load(path)
    del lines[idx]
    save(path, lines)
    print(f"\U0001F5D1️ 削除: {it['text']}")
    return 0


def cmd_archive(args) -> int:
    label, store = resolve_single(args.scope)
    lines = load(store)
    done_idx = [i for i, l in enumerate(lines) if (it := parse_item(l)) and it["done"]]
    if not done_idx:
        print(f"済み項目なし ({label}): {store}")
        return 0
    done_lines = [lines[i] for i in done_idx]
    keep = [l for i, l in enumerate(lines) if i not in set(done_idx)]
    save(store, keep)
    if not args.purge:
        apath = archive_path(store)
        alines = load(apath)
        if not alines:
            alines = ["# Backlog — archive", ""]
        alines.append(f"## {today()} archived")
        alines.extend(done_lines)
        alines.append("")
        apath.parent.mkdir(parents=True, exist_ok=True)
        apath.write_text("\n".join(alines).rstrip("\n") + "\n", encoding="utf-8")
        print(f"✅ {len(done_lines)}件を {apath.name} へ退避しました（未完了 {len([l for l in keep if parse_item(l)])}件を残置）")
    else:
        print(f"\U0001F9F9 {len(done_lines)}件を削除しました（--purge、未完了 {len([l for l in keep if parse_item(l)])}件を残置）")
    return 0


def cmd_stale(args) -> int:
    try:
        cutoff = datetime.date.fromisoformat(today()) - datetime.timedelta(days=args.days)
    except ValueError:
        sys.exit("backlog: bad --date")
    found = 0
    for label, path in resolve_many(args.scope):
        for it in (parse_item(l) for l in load(path)):
            if not it or it["done"] or not it["date"]:
                continue
            try:
                d = datetime.date.fromisoformat(it["date"])
            except ValueError:
                continue
            if d <= cutoff:
                found += 1
                print(f"[{label}] {it['date']}  {it['text']}")
    if not found:
        print(f"{args.days}日以上放置の未完了なし")
    return 0


def cmd_path(args) -> int:
    for label, path in resolve_many("auto"):
        print(f"{label}\t{path}\t(archive: {archive_path(path)})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="backlog", description="lightweight persistent do-it-later inbox")
    p.add_argument("--date", help="override today's date (YYYY-MM-DD)")

    def scope_flags(sub):
        sub.add_argument("-g", "--global", dest="scope", action="store_const", const="global",
                         default="auto", help="force the personal inbox")
        sub.add_argument("-r", "--repo", dest="scope", action="store_const", const="repo",
                         help="force this repo's BACKLOG.md")

    sub = p.add_subparsers(dest="cmd", required=False)

    a = sub.add_parser("add", help="append an item")
    scope_flags(a); a.add_argument("--tag", action="append"); a.add_argument("text", nargs="+"); a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="show open items (repo + personal)")
    scope_flags(l); l.add_argument("--all", action="store_true", help="include done items"); l.set_defaults(func=cmd_list)

    f = sub.add_parser("find", help="preview matching items"); scope_flags(f)
    f.add_argument("query", nargs="+"); f.set_defaults(func=cmd_find)

    d = sub.add_parser("done", help="check off a matching item"); scope_flags(d)
    d.add_argument("query", nargs="+"); d.set_defaults(func=cmd_done)

    dr = sub.add_parser("drop", help="delete a matching item (needs --yes)"); scope_flags(dr)
    dr.add_argument("--yes", action="store_true"); dr.add_argument("query", nargs="+"); dr.set_defaults(func=cmd_drop)

    ar = sub.add_parser("archive", help="sweep done items into the archive file"); scope_flags(ar)
    ar.add_argument("--purge", action="store_true", help="delete instead of archiving"); ar.set_defaults(func=cmd_archive)

    st = sub.add_parser("stale", help="list long-untouched open items"); scope_flags(st)
    st.add_argument("--days", type=int, default=30); st.set_defaults(func=cmd_stale)

    pa = sub.add_parser("path", help="print resolved store paths"); pa.set_defaults(func=cmd_path)
    return p


def main(argv=None) -> int:
    global _TODAY_OVERRIDE
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "date", None):
        _TODAY_OVERRIDE = args.date
    if not getattr(args, "cmd", None):
        return cmd_list(argparse.Namespace(scope="auto", all=False))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
