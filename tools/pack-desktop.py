#!/usr/bin/env python3
"""Package skills into per-skill zips for manual upload to Claude Desktop / claude.ai.

Claude Desktop has no bulk-install path and no sync from Claude Code — every
custom skill is a separate manual zip upload (verified against Anthropic docs,
2026-07). This tool removes the error-prone half of that: it produces correctly
shaped zips (one top-level <skill>/ folder containing SKILL.md), validated
against the claude.ai/API contract, plus an ordered upload checklist.

It does NOT upload. Upload stays manual by design — the only programmatic path
is the Skills API, whose store is separate from claude.ai and does not surface
there, so it wouldn't help.

Flow:  validate (strict) -> select from manifest -> zip -> order -> checklist,
       index + ledger

Output: dist/desktop/<skill>.zip, UPLOAD.md (ordered checklist), INDEX.md (what
each package is), .manifest.json

Standard library only (plus PyYAML, already a repo dependency).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tools" / "desktop-manifest.yaml"
VALIDATOR = REPO / "tools" / "validate_skills.py"
OUT_DIR = REPO / "dist" / "desktop"

# Files/dirs never worth shipping inside a skill zip.
SKIP_NAMES = {"__pycache__", ".DS_Store", ".git"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".bak"}


def rel(p: Path) -> Path:
    """Display path: repo-relative inside the repo, absolute outside it.

    --out can legitimately point outside the repo (packing straight into a
    Windows-side directory so the Claude Desktop file picker can reach it), and
    Path.relative_to raises there.
    """
    try:
        return p.relative_to(REPO)
    except ValueError:
        return p


def skill_dir(name: str) -> Path:
    hits = list((REPO / "plugins").glob(f"*/skills/{name}"))
    if not hits:
        raise SystemExit(f"error: no skill directory for {name!r}")
    if len(hits) > 1:
        raise SystemExit(f"error: {name!r} is ambiguous: {hits}")
    return hits[0]


def load_manifest() -> dict:
    data = yaml.safe_load(MANIFEST.read_text())
    viable = list(data.get("viable") or [])
    experimental = list(data.get("experimental") or [])
    excluded = [e["name"] for e in (data.get("excluded") or [])]
    return {"viable": viable, "experimental": experimental, "excluded": excluded}


def check_manifest_covers_all(man: dict) -> list[str]:
    """Every skill on disk must appear in exactly one manifest bucket."""
    on_disk = {p.parent.name for p in (REPO / "plugins").glob("*/skills/*/SKILL.md")}
    listed = man["viable"] + man["experimental"] + man["excluded"]
    problems = []
    seen = set()
    for n in listed:
        if n in seen:
            problems.append(f"listed twice in manifest: {n}")
        seen.add(n)
    for n in sorted(on_disk - seen):
        problems.append(f"skill on disk but not in manifest: {n}")
    for n in sorted(seen - on_disk):
        problems.append(f"in manifest but not on disk: {n}")
    return problems


def run_validator(names: list[str]) -> tuple[bool, str]:
    """Validate the selected skills in --strict mode (claude.ai/API contract).

    Runs one skill at a time so a single bad skill doesn't block the rest from
    being reported. Returns (all_ok, combined_output).
    """
    out_lines = []
    ok = True
    for n in names:
        r = subprocess.run(
            [sys.executable, str(VALIDATOR), "--strict", "--only", n, "--quiet"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            ok = False
            # Only surface output from skills that actually failed; a clean run
            # of 38 skills should not print 38 "0 errors" lines.
            out_lines.append(r.stdout.strip())
    if ok:
        return True, f"validated {len(names)} skill(s): all pass (strict)"
    return ok, "\n".join(l for l in out_lines if l)


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        if any(part in SKIP_NAMES for part in p.parts):
            continue
        if p.suffix in SKIP_SUFFIXES:
            continue
        yield p


def zip_skill(name: str, dest_dir: Path) -> tuple[Path, str]:
    """Zip a skill so its single top-level entry is <name>/. Returns (zip_path, sha256)."""
    src = skill_dir(name)
    if not (src / "SKILL.md").is_file():
        raise SystemExit(f"error: {name} has no SKILL.md")
    zpath = dest_dir / f"{name}.zip"
    # Deterministic: fixed member order, fixed timestamps, so an unchanged skill
    # hashes identically across runs (the ledger relies on this).
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in iter_files(src):
            arcname = Path(name) / f.relative_to(src)
            zi = zipfile.ZipInfo(str(arcname), date_time=(2020, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, f.read_bytes())
    return zpath, sha256_of(zpath)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def content_hash(name: str) -> str:
    """Hash a skill's source tree (not the zip) so we can tell what changed."""
    h = hashlib.sha256()
    for f in iter_files(skill_dir(name)):
        h.update(str(f.relative_to(skill_dir(name))).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def git_dates(name: str) -> tuple[str, str]:
    """(added, updated) as YYYY-MM-DD for the skill directory, or ('—', '—').

    Both dates come from the skill directory — the exact tree that goes into the
    zip — so "updated" means "the packaged content changed", not "something
    elsewhere in the plugin changed".
    """
    src = skill_dir(name)
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "log", "--format=%cs", "--",
             str(src.relative_to(REPO))],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "—", "—"
    dates = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    if not dates:
        return "—", "—"
    return dates[-1], dates[0]  # git log is newest-first


ORDERS = ("updated", "added", "manifest")


def order_packed(packed: list[dict], how: str) -> list[dict]:
    """Newest first for the date orders; manifest order is left untouched."""
    if how == "manifest":
        return packed
    key = "updated" if how == "updated" else "added"
    # '—' (no git history) sorts last, not first.
    return sorted(packed, key=lambda p: (p.get(key) or "—") != "—" and p[key] or "",
                  reverse=True)


def summary_of(name: str) -> str:
    """First sentence of the skill's frontmatter description, for the index."""
    text = (skill_dir(name) / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    try:
        meta = yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return ""
    desc = " ".join(str(meta.get("description", "")).split())
    if not desc:
        return ""
    # Cut at the first sentence end, but only if that leaves something readable.
    # Descriptions are full of abbreviations and dotted filenames ("e.g.", ".pptx"),
    # so a naive ". " split produces fragments like "pluggable units (e.g.".
    abbrevs = ("e.g.", "i.e.", "etc.", "cf.", "vs.", "approx.", "resp.", "al.")
    for i, ch in enumerate(desc):
        if ch == "。":
            if 40 <= i <= 240:
                return desc[: i + 1]
            break
        if ch != "." or not desc[i + 1: i + 2].isspace():
            continue
        head = desc[: i + 1]
        initial = len(head) >= 2 and head[-2].isupper() and (len(head) == 2 or head[-3].isspace())
        if head.endswith(abbrevs) or initial:
            continue  # abbreviation or a single-letter initial — not a sentence end
        if 40 <= i <= 240:
            return head
        if i > 240:
            break
    return desc if len(desc) <= 240 else desc[:237].rstrip() + "…"


def status_of(item: dict, prev: dict) -> str:
    """NEW / CHANGED / unchanged, judged against the previous pack's ledger."""
    prior = prev.get("skills", {}).get(item["name"], {}).get("content")
    if prior is None:
        return "NEW"
    if prior != item["content"]:
        return "CHANGED"
    return "unchanged"


def write_checklist(dest_dir: Path, packed: list[dict], prev: dict, order: str) -> None:
    ordering = {
        "updated": "newest first (most recently changed skill at the top)",
        "added": "newest first (most recently added skill at the top)",
        "manifest": "manifest order",
    }[order]
    lines = [
        "# Claude Desktop — skill upload checklist",
        "",
        "One zip per skill; upload is manual (there is no bulk path and no sync",
        f"from Claude Code). Ordered {ordering} —",
        "work top to bottom, so stopping halfway still leaves you with the newest.",
        "",
        "See `INDEX.md` for what each skill does.",
        "",
        "## Prerequisites",
        "",
        "- A plan that allows custom-skill upload (Pro / Max / Team / Enterprise;",
        "  **not** Free).",
        "- **Code execution** enabled under Settings > Capabilities — skills do not",
        "  run without it.",
        "",
        "Upload at **Customize > Skills > +**, then pick the .zip. Uploaded skills",
        "are private to your account; toggle them on and off under",
        "Settings > Capabilities > Skills.",
        "",
        "## Upload",
        "",
    ]
    tags = {
        "NEW": "NEW",
        "CHANGED": "CHANGED — re-upload (replace existing)",
        "unchanged": "unchanged since last pack",
    }
    for item in packed:
        n = item["name"]
        tag = tags[status_of(item, prev)]
        flag = "  *(experimental — verify it runs)*" if item["experimental"] else ""
        upd = item.get("updated", "—")
        lines.append(f"- [ ] **{n}** — `{n}.zip`  ·  updated {upd}  ·  {tag}{flag}")
    lines += [
        "",
        "## After uploading",
        "",
        "- Confirm each skill appears in your skill list and toggles on.",
        "- For experimental skills, run one real task and check the bundled",
        "  scripts actually execute in the sandbox (network access is",
        "  settings-dependent; Node/Puppeteer skills may not work).",
        "",
    ]
    (dest_dir / "UPLOAD.md").write_text("\n".join(lines), encoding="utf-8")


def write_index(dest_dir: Path, packed: list[dict], prev: dict, order: str) -> None:
    """A table of what is in this pack: same order as the checklist, plus what each skill does."""
    sorted_by = {
        "updated": "last change to the packaged skill (newest first)",
        "added": "date the skill first appeared (newest first)",
        "manifest": "manifest order",
    }[order]
    lines = [
        "# Claude Desktop skill packages — index",
        "",
        f"{len(packed)} zip(s) in this directory, sorted by {sorted_by}.",
        "Upload order and status live in `UPLOAD.md`; this file is what each one is for.",
        "",
        "| # | Skill | Zip | Added | Updated | Status | Kind | What it does |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, item in enumerate(packed, 1):
        n = item["name"]
        kind = "experimental" if item["experimental"] else "stable"
        desc = summary_of(n).replace("|", "\\|")
        lines.append(
            f"| {i} | **{n}** | `{n}.zip` | {item.get('added', '—')} | "
            f"{item.get('updated', '—')} | {status_of(item, prev)} | {kind} | {desc} |"
        )
    lines += [
        "",
        "**Status** is against the previous pack in this directory: `NEW` was not packed",
        "before, `CHANGED` differs from what you last uploaded, `unchanged` is already",
        "current if you uploaded it last time.",
        "",
        "**Kind**: `experimental` skills bundle scripts or assume tools that may not exist",
        "in the claude.ai sandbox — upload them, then run one real task to check.",
        "",
    ]
    (dest_dir / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Package skills as zips for Claude Desktop.")
    ap.add_argument("--experimental", action="store_true",
                    help="also package skills marked experimental in the manifest")
    ap.add_argument("--only", metavar="NAME", action="append",
                    help="package just this skill (repeatable); ignores manifest buckets "
                         "but still validates")
    ap.add_argument("--out", type=Path, default=OUT_DIR,
                    help=f"output dir (default {OUT_DIR.relative_to(REPO)})")
    ap.add_argument("--order", choices=ORDERS, default="updated",
                    help="order of the checklist and index: 'updated' (default) and "
                         "'added' list newest first; 'manifest' keeps the manifest's order")
    args = ap.parse_args()

    man = load_manifest()

    problems = check_manifest_covers_all(man)
    if problems:
        print("manifest coverage problems (every skill must be classified):",
              file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2

    if args.only:
        selected = args.only
        exp_set = set(man["experimental"])
        for n in selected:
            if n in set(e for e in man["excluded"]):
                print(f"warning: {n} is marked excluded in the manifest; packaging anyway "
                      "because --only was given", file=sys.stderr)
    else:
        selected = list(man["viable"])
        if args.experimental:
            selected += man["experimental"]
        exp_set = set(man["experimental"])

    # Validate against the claude.ai/API contract before packaging anything.
    ok, report = run_validator(selected)
    if report:
        print(report)
    if not ok:
        print("\nrefusing to package: fix the validation errors above.", file=sys.stderr)
        return 1

    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    ledger_path = out / ".manifest.json"
    prev = {}
    if ledger_path.is_file():
        try:
            prev = json.loads(ledger_path.read_text())
        except json.JSONDecodeError:
            prev = {}

    packed = []
    for n in selected:
        chash = content_hash(n)
        zpath, zhash = zip_skill(n, out)
        added, updated = git_dates(n)
        packed.append({
            "name": n,
            "zip": zpath.name,
            "content": chash,
            "zip_sha256": zhash,
            "experimental": n in exp_set,
            "added": added,
            "updated": updated,
        })
        print(f"packed {n} -> {rel(zpath)}")

    packed = order_packed(packed, args.order)
    write_checklist(out, packed, prev, args.order)
    write_index(out, packed, prev, args.order)

    # Merge, never replace. A subset run (--only, or a run without --experimental
    # after one with it) packs a few skills; replacing the ledger would drop every
    # other skill's entry, and the next full pack would report all of them NEW —
    # losing exactly the "what do I need to re-upload" signal the ledger exists for.
    ledger = {"skills": {**prev.get("skills", {}), **{p["name"]: p for p in packed}}}
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")

    changed = sum(
        1 for p in packed
        if prev.get("skills", {}).get(p["name"], {}).get("content") != p["content"]
    )
    print(f"\n{len(packed)} zip(s) in {rel(out)}  "
          f"({changed} new/changed).  Checklist: {rel(out / 'UPLOAD.md')}  "
          f"Index: {rel(out / 'INDEX.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
