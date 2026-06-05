#!/usr/bin/env python3
"""Emit one PlantUML (.puml) file per view from an archimate-ea running model.

Generate-forward: the YAML model is upstream; these .puml files are downstream,
disposable render artifacts. Never hand-edit them — edit the YAML and re-emit.
Layout is left to Graphviz (PlantUML's engine); no coordinates are computed.

Refuses to emit if the model has ERROR-level validation problems.

Usage:
    emit_plantuml.py MODEL.yaml -o OUTDIR [--lang auto|en|ja|...] [--force]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from archimate_metamodel import load as load_metamodel
from validate_model import load_model, validate, ERROR

_ALIAS_RE = re.compile(r"\W")


def alias_of(eid: str) -> str:
    a = _ALIAS_RE.sub("_", str(eid))
    return a if a[:1].isalpha() or a[:1] == "_" else "n_" + a


def label_of(node: dict, lang: str) -> str:
    name = node.get("name")
    if isinstance(name, dict):
        if lang != "auto" and lang in name:
            text = name[lang]
        else:
            text = next(iter(name.values()), node.get("id", ""))
    elif isinstance(name, str):
        text = name
    else:
        text = node.get("id", "")
    return str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def _rel_label(rel: dict) -> str:
    if rel.get("type") == "Access" and rel.get("accessType"):
        return {"read": "R", "write": "W", "readWrite": "RW", "none": ""}.get(rel["accessType"], "")
    if rel.get("type") == "Influence" and rel.get("strength"):
        return str(rel["strength"])
    if rel.get("type") == "Association" and rel.get("isDirected"):
        return ""  # directed associations render as plain associations in stdlib
    return ""


def emit_view(view, model, mm, lang) -> str:
    lines = ["@startuml", "!include <archimate/Archimate>", ""]
    title = label_of(view, lang)
    if title:
        lines.append(f'title {title}')
        lines.append("")

    member_ids = list(view.get("elements", []) or [])
    for eid in member_ids:
        e = model.element_by_id.get(eid)
        if not e:
            continue
        a = alias_of(eid)
        if e.get("type") == "Junction":
            lines.append(f"Junction({a})")
            continue
        macro = mm.plantuml_macro(e.get("type"))
        label = label_of(e, lang)
        if macro:
            lines.append(f'{macro}({a}, "{label}")')
        else:
            lines.append(f'rectangle "{label}" as {a}')
    lines.append("")

    member_set = set(member_ids)
    for rid in view.get("relationships", []) or []:
        r = model.rel_by_id.get(rid)
        if not r:
            continue
        src, dst = r.get("source"), r.get("target")
        if src not in member_set or dst not in member_set:
            continue  # endpoint not in view; skip to keep the diagram well-formed
        macro = mm.relationship_macro(r.get("type")) or "Rel_Association"
        lbl = _rel_label(r)
        if lbl:
            lines.append(f'{macro}({alias_of(src)}, {alias_of(dst)}, "{lbl}")')
        else:
            lines.append(f'{macro}({alias_of(src)}, {alias_of(dst)})')

    lines += ["", "@enduml", ""]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit PlantUML views from a running model.")
    ap.add_argument("model")
    ap.add_argument("-o", "--out", required=True, help="output directory")
    ap.add_argument("--lang", default="auto", help="label language (auto = first provided per element)")
    ap.add_argument("--force", action="store_true", help="emit even if validation has errors")
    args = ap.parse_args(argv)

    mm = load_metamodel()
    model = load_model(args.model)
    errors = [p for p in validate(model, mm) if p.severity == ERROR]
    if errors and not args.force:
        sys.stderr.write(f"Refusing to emit: {len(errors)} validation error(s). "
                         "Run validate_model.py for details (or pass --force).\n")
        return 2

    views_dir = os.path.join(args.out, "views")
    os.makedirs(views_dir, exist_ok=True)
    index = []
    for v in model.views:
        if not isinstance(v, dict) or not v.get("id"):
            continue
        path = os.path.join(views_dir, f"{v['id']}.puml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(emit_view(v, model, mm, args.lang))
        index.append((v["id"], label_of(v, args.lang)))
        print(f"wrote {path}")

    with open(os.path.join(views_dir, "_index.md"), "w", encoding="utf-8") as fh:
        fh.write("# Views\n\n" + "\n".join(f"- `{i}.puml` — {t}" for i, t in index) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
