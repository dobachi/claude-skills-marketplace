#!/usr/bin/env python3
"""Quarto pre-render step: generate the full skill catalog table from marketplace.json.

Reads `.claude-plugin/marketplace.json` at the repo root and writes a Markdown table to
`site/skills/_catalog.md`, which `site/skills/index.qmd` includes. Runs at every render
so the catalog never drifts from the marketplace manifest. Stdlib only — no deps.

Each row also carries the plugin's current version (from its plugin.json) and the date it
was last changed (from git). CI must check out full history (fetch-depth: 0) for the dates
to be real; on a shallow clone the date falls back to "—".
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
OUT = Path(__file__).resolve().parents[1] / "skills" / "_catalog.md"


def plugin_version(name: str) -> str:
    pj = REPO_ROOT / "plugins" / name / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(pj.read_text(encoding="utf-8")).get("version", "—")
    except (OSError, json.JSONDecodeError):
        return "—"


def last_updated(name: str) -> str:
    """Author date (YYYY-MM-DD) of the last commit touching this plugin, or '—'."""
    path = REPO_ROOT / "plugins" / name
    if not path.exists():
        return "—"
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "log", "-1", "--format=%cs", "--", f"plugins/{name}"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "—"
    date = out.stdout.strip()
    return date or "—"

# Plugins documented in depth under the EA section — link the name to its page.
EA_PAGES = {
    "archimate-ea": "../ea/archimate-ea.qmd",
    "archimate-native": "../ea/archimate-native.qmd",
    "requirements-stories": "../ea/requirements-stories.qmd",
    "tech-selector": "../ea/tech-selector.qmd",
    "archimate-to-impl": "../ea/archimate-to-impl.qmd",
    "ea-delivery": "../ea/ea-delivery.qmd",
}


def esc(text: str) -> str:
    """Escape pipes so a description never breaks the Markdown table."""
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    plugins = data.get("plugins", [])

    # Enrich once, reuse for both the "recent" list and the table.
    for p in plugins:
        name = p.get("name", "")
        p["_version"] = plugin_version(name)
        p["_updated"] = last_updated(name)

    by_name = sorted(plugins, key=lambda p: p.get("name", ""))
    # Most-recently-updated first; unknown dates ("—") sort last.
    by_date = sorted(plugins, key=lambda p: (p["_updated"] != "—", p["_updated"]), reverse=True)

    lines = [
        f"*{len(plugins)} プラグイン（`marketplace.json` から自動生成）*",
        "",
    ]

    recent = [p for p in by_date if p["_updated"] != "—"][:8]
    if recent:
        badges = "、".join(f"**{p['name']}** ({p['_updated']})" for p in recent)
        lines += [f"最近更新: {badges}", ""]

    lines += [
        "| プラグイン | 更新日 | 版 | 説明 |",
        "|---|---|---|---|",
    ]
    for p in by_name:
        name = p.get("name", "")
        cell = f"[**{name}**]({EA_PAGES[name]})" if name in EA_PAGES else f"**{name}**"
        lines.append(
            f"| {cell} | {p['_updated']} | {p['_version']} | {esc(p.get('description', ''))} |"
        )
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"gen_catalog: wrote {OUT.relative_to(REPO_ROOT)} ({len(plugins)} plugins)")


if __name__ == "__main__":
    main()
