#!/usr/bin/env python3
"""Quarto pre-render step: generate the full skill catalog table from marketplace.json.

Reads `.claude-plugin/marketplace.json` at the repo root and writes a Markdown table to
`site/skills/_catalog.md`, which `site/skills/index.qmd` includes. Runs at every render
so the catalog never drifts from the marketplace manifest. Stdlib only — no deps.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
OUT = Path(__file__).resolve().parents[1] / "skills" / "_catalog.md"

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
    plugins = sorted(data.get("plugins", []), key=lambda p: p.get("name", ""))

    lines = [
        f"*{len(plugins)} プラグイン（`marketplace.json` から自動生成）*",
        "",
        "| プラグイン | 説明 |",
        "|---|---|",
    ]
    for p in plugins:
        name = p.get("name", "")
        cell = f"[**{name}**]({EA_PAGES[name]})" if name in EA_PAGES else f"**{name}**"
        lines.append(f"| {cell} | {esc(p.get('description', ''))} |")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"gen_catalog: wrote {OUT.relative_to(REPO_ROOT)} ({len(plugins)} plugins)")


if __name__ == "__main__":
    main()
