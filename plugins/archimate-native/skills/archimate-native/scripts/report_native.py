#!/usr/bin/env python3
"""Generate a Markdown report from an Archi-native .archimate model (read-only).

Header + purpose, per-layer concept tables, relationship inventory, folder tree,
view inventory, and a review-findings appendix (so the report doubles as a quality
audit). Reuses review_native's checks.

Usage: report_native.py MODEL.archimate [-o report.md]
"""

from __future__ import annotations

import argparse
import sys

from native_model import NativeModel
from review_native import collect_violations, collect_orphans

LAYER_ORDER = ["motivation", "strategy", "business", "application",
               "technology", "physical", "implementation", "composite", "unknown"]


def build_report(model) -> str:
    lines = [f"# {model.name}", ""]
    lines.append(f"- Archi file version: `{model.version}` (era: {model.era})")
    lines.append(f"- Concepts: {len(model.concepts)} · Relationships: {len(model.relationships)} · Views: {len(model.diagrams)}")
    if model.purpose:
        lines += ["", "## Purpose", "", model.purpose]

    # concepts by layer
    by_layer = {}
    for c in model.concepts.values():
        layer = model.mm.layer_of(c.canonical_type) if c.canonical_type else "unknown"
        by_layer.setdefault(layer, []).append(c)
    lines += ["", "## Concepts by layer", ""]
    for layer in LAYER_ORDER:
        items = by_layer.get(layer)
        if not items:
            continue
        lines.append(f"### {layer.capitalize()} ({len(items)})")
        lines.append("")
        lines.append("| id | type | name |")
        lines.append("|----|------|------|")
        for c in sorted(items, key=lambda x: x.canonical_type or ""):
            lines.append(f"| `{c.id}` | {c.canonical_type or c.native_type} | {c.name} |")
        lines.append("")

    # relationship inventory
    rel_by_type = {}
    for r in model.relationships.values():
        rel_by_type.setdefault(r.canonical_type or r.native_type, []).append(r)
    lines += ["## Relationships", ""]
    for rtype in sorted(rel_by_type):
        lines.append(f"- **{rtype}** ({len(rel_by_type[rtype])})")
        for r in rel_by_type[rtype]:
            lines.append(f"  - {model.label(r.source)} → {model.label(r.target)}")
    lines.append("")

    # views
    lines += ["## Views", ""]
    for d in model.diagrams.values():
        vp = f" · viewpoint {d.viewpoint}" if d.viewpoint else ""
        lines.append(f"- **{d.name or d.id}** — {len(d.objects)} object(s), {len(d.connections)} connection(s){vp}")
    lines.append("")

    # review appendix
    viol = collect_violations(model)
    no_rels, unrealized = collect_orphans(model)
    lines += ["## Review findings", ""]
    if not viol and not no_rels and not unrealized:
        lines.append("No issues found.")
    else:
        for p in viol:
            lines.append(f"- **{p['severity']}** [{p['code']}] `{p['ref']}` — {p['message']}")
        for c in no_rels:
            lines.append(f"- **WARN** [orphan] `{c.id}` — {c.name} has no relationships.")
        for c in unrealized:
            lines.append(f"- **WARN** [unrealized] `{c.id}` — {c.name} ({c.canonical_type}) is not realized/influenced.")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Markdown report from an Archi-native model.")
    ap.add_argument("model")
    ap.add_argument("-o", "--out")
    args = ap.parse_args(argv)
    text = build_report(NativeModel(args.model))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
