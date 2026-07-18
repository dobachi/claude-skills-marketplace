#!/usr/bin/env python3
"""Validate every skill's SKILL.md against the Agent Skills contract.

Single source of truth for skill validation. Called three ways:
  - by hand, as the check step in docs/adding-or-updating-a-skill.md
  - by CI (.github/workflows/validate-skills.yml) on any plugins/** change
  - by tools/pack-desktop.py before it packages anything

Two severities, deliberately distinct:

  ERROR   — malformed or contract-breaking on ANY surface (bad YAML, missing
            field, name/dir mismatch, name not registered). Exit 1.
  DESKTOP — valid in Claude Code but rejected by claude.ai / the Skills API
            (reserved word in name, description over 1024 chars, XML tags).
            Warned, not failed — Claude Code tolerates these, and failing the
            whole repo on them would punish skills that never target claude.ai.
            `--strict` promotes DESKTOP findings to errors (used by the packer).

Field limits are the official ones, verified verbatim against
platform.claude.com/docs Agent Skills (name: max 64, lowercase/digits/hyphens,
no XML tags, no reserved words "anthropic"/"claude"; description: non-empty,
max 1024, no XML tags).

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"

NAME_MAX = 64
DESC_MAX = 1024
NAME_RE = re.compile(r"^[a-z0-9-]+$")
RESERVED = ("anthropic", "claude")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


class Finding:
    __slots__ = ("severity", "skill", "path", "message")

    def __init__(self, severity: str, skill: str, path: Path, message: str):
        self.severity = severity  # "ERROR" | "DESKTOP"
        self.skill = skill
        self.path = path
        self.message = message


def load_registered_names() -> set[str]:
    try:
        data = json.loads(MARKETPLACE.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"error: cannot read {MARKETPLACE}: {exc}")
    return {p.get("name") for p in data.get("plugins", [])}


def has_xml_tag(text: str) -> bool:
    # A crude but sufficient tag detector: <word ...> or </word>. The API rejects
    # any XML tag; we mirror that rather than trying to be clever about intent.
    return re.search(r"</?[a-zA-Z][^>]*>", text) is not None


def plugin_dir_for(skill_md: Path) -> Path:
    # plugins/<plugin>/skills/<skill>/SKILL.md -> plugins/<plugin>
    return skill_md.parent.parent.parent


def validate_skill(skill_md: Path, registered: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    skill_dir = skill_md.parent
    dir_name = skill_dir.name
    rel = skill_md.relative_to(REPO)
    text = skill_md.read_text(encoding="utf-8")

    m = FRONTMATTER_RE.match(text)
    if not m:
        findings.append(Finding("ERROR", dir_name, rel,
                                "no YAML frontmatter (must start with a --- block)"))
        return findings

    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0]
        findings.append(Finding("ERROR", dir_name, rel,
                                f"frontmatter is not valid YAML: {detail}"))
        return findings

    if not isinstance(fm, dict):
        findings.append(Finding("ERROR", dir_name, rel,
                                "frontmatter did not parse to a mapping"))
        return findings

    name = fm.get("name")
    desc = fm.get("description")

    # --- name ---
    if not name or not isinstance(name, str):
        findings.append(Finding("ERROR", dir_name, rel, "missing `name`"))
    else:
        if name != dir_name:
            findings.append(Finding("ERROR", name, rel,
                                    f"`name` ({name!r}) != directory ({dir_name!r})"))
        if len(name) > NAME_MAX:
            findings.append(Finding("DESKTOP", name, rel,
                                    f"`name` is {len(name)} chars (max {NAME_MAX})"))
        if not NAME_RE.match(name):
            findings.append(Finding("DESKTOP", name, rel,
                                    "`name` must be lowercase letters, digits, hyphens only"))
        for word in RESERVED:
            if word in name:
                findings.append(Finding("DESKTOP", name, rel,
                                        f"`name` contains reserved word {word!r} "
                                        "(rejected by claude.ai / Skills API)"))

    # --- registration: the PLUGIN (not each skill) must be in marketplace.json.
    # A plugin may bundle several skills (e.g. agent-delegate), so registration
    # is checked against the plugin's own name, read from its plugin.json. ---
    plugin_json = plugin_dir_for(skill_md) / ".claude-plugin" / "plugin.json"
    plugin_name = None
    if not plugin_json.is_file():
        findings.append(Finding("ERROR", str(name or dir_name), rel,
                                f"no plugin.json at {plugin_json.relative_to(REPO)}"))
    else:
        try:
            plugin_name = json.loads(plugin_json.read_text()).get("name")
        except json.JSONDecodeError as exc:
            findings.append(Finding("ERROR", str(name or dir_name),
                                    plugin_json.relative_to(REPO),
                                    f"plugin.json is not valid JSON: {exc}"))
        else:
            if plugin_name not in registered:
                findings.append(Finding("ERROR", str(name or dir_name), rel,
                                        f"plugin {plugin_name!r} not registered in "
                                        "marketplace.json"))

    # --- description ---
    if not desc or not isinstance(desc, str) or not desc.strip():
        findings.append(Finding("ERROR", str(name or dir_name), rel,
                                "missing or empty `description`"))
    else:
        if len(desc) > DESC_MAX:
            findings.append(Finding("DESKTOP", str(name), rel,
                                    f"`description` is {len(desc)} chars (max {DESC_MAX})"))
        if has_xml_tag(desc):
            findings.append(Finding("DESKTOP", str(name), rel,
                                    "`description` contains an XML tag (rejected by Skills API)"))

    # --- extra frontmatter keys (this repo's convention: name + description only) ---
    extra = set(fm) - {"name", "description"}
    if extra:
        findings.append(Finding("DESKTOP", str(name or dir_name), rel,
                                f"unexpected frontmatter keys: {', '.join(sorted(extra))}"))

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate SKILL.md files.")
    ap.add_argument("--strict", action="store_true",
                    help="treat DESKTOP (claude.ai/API) findings as errors too")
    ap.add_argument("--only", metavar="NAME",
                    help="validate a single skill by name")
    ap.add_argument("--quiet", action="store_true",
                    help="print only findings and the summary line")
    args = ap.parse_args()

    registered = load_registered_names()
    skill_files = sorted((REPO / "plugins").glob("*/skills/*/SKILL.md"))
    if args.only:
        skill_files = [p for p in skill_files if p.parent.name == args.only]
        if not skill_files:
            print(f"error: no skill named {args.only!r}", file=sys.stderr)
            return 2

    all_findings: list[Finding] = []
    for sf in skill_files:
        all_findings.extend(validate_skill(sf, registered))

    errors = [f for f in all_findings if f.severity == "ERROR"]
    desktop = [f for f in all_findings if f.severity == "DESKTOP"]

    for f in errors:
        print(f"ERROR   {f.skill}: {f.message}  [{f.path}]")
    for f in desktop:
        tag = "ERROR  " if args.strict else "desktop"
        print(f"{tag} {f.skill}: {f.message}  [{f.path}]")

    n = len(skill_files)
    if not args.quiet:
        print()
    print(f"checked {n} skill(s): {len(errors)} error(s), {len(desktop)} desktop finding(s)")

    fail = bool(errors) or (args.strict and bool(desktop))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
