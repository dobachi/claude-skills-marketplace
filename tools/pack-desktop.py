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

Flow:  validate (strict) -> select from manifest -> zip -> checklist + ledger

Output: dist/desktop/<skill>.zip, UPLOAD.md, .manifest.json

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


def write_checklist(dest_dir: Path, packed: list[dict], prev: dict) -> None:
    lines = [
        "# Claude Desktop — skill upload checklist",
        "",
        "One zip per skill; upload is manual (there is no bulk path and no sync",
        "from Claude Code). Work top to bottom.",
        "",
        "## Prerequisites",
        "",
        "- A plan that allows custom-skill upload (Pro / Max / Team / Enterprise;",
        "  **not** Free).",
        "- **Code execution / file creation** enabled in settings — skills do not",
        "  run without it.",
        "- The upload entry point in the Claude app. The docs disagree on the exact",
        "  label (\"Customize > Skills\", \"Settings > Features\", \"Settings >",
        "  Capabilities > Skills\") — find the one your build shows; it is where you",
        "  \"Upload a skill\" / \"Create skill\" and pick a .zip.",
        "",
        "## Upload",
        "",
    ]
    for i, item in enumerate(packed, 1):
        n = item["name"]
        prior = prev.get("skills", {}).get(n, {}).get("content")
        if prior is None:
            tag = "NEW"
        elif prior != item["content"]:
            tag = "CHANGED — re-upload (replace existing)"
        else:
            tag = "unchanged since last pack"
        flag = "  *(experimental — verify it runs)*" if item["experimental"] else ""
        lines.append(f"- [ ] **{n}** — `{n}.zip`  ·  {tag}{flag}")
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Package skills as zips for Claude Desktop.")
    ap.add_argument("--experimental", action="store_true",
                    help="also package skills marked experimental in the manifest")
    ap.add_argument("--only", metavar="NAME", action="append",
                    help="package just this skill (repeatable); ignores manifest buckets "
                         "but still validates")
    ap.add_argument("--out", type=Path, default=OUT_DIR,
                    help=f"output dir (default {OUT_DIR.relative_to(REPO)})")
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
        packed.append({
            "name": n,
            "zip": zpath.name,
            "content": chash,
            "zip_sha256": zhash,
            "experimental": n in exp_set,
        })
        print(f"packed {n} -> {zpath.relative_to(REPO)}")

    write_checklist(out, packed, prev)

    ledger = {"skills": {p["name"]: p for p in packed}}
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")

    changed = sum(
        1 for p in packed
        if prev.get("skills", {}).get(p["name"], {}).get("content") != p["content"]
    )
    print(f"\n{len(packed)} zip(s) in {out.relative_to(REPO)}  "
          f"({changed} new/changed).  Checklist: {(out / 'UPLOAD.md').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
