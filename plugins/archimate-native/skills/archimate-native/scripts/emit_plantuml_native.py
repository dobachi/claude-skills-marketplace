#!/usr/bin/env python3
"""Emit PlantUML from an Archi-native .archimate model for quick visual review
without opening Archi.

Each concept/relationship is normalized to canonical and rendered via the SAME
ArchiMate-stdlib macro map used by the archimate-ea skill (archimate_metamodel.json).
Native geometry is intentionally ignored — PlantUML is a review render; the
.archimate keeps the real layout. Layout is left to Graphviz.

Usage: emit_plantuml_native.py MODEL.archimate -o OUTDIR [--view ID|NAME]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from native_model import NativeModel

_ALIAS = re.compile(r"\W")


def alias(cid):
    a = _ALIAS.sub("_", str(cid))
    return a if (a[:1].isalpha() or a[:1] == "_") else "n_" + a


def esc(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def emit(model, concept_ids, rel_ids) -> str:
    out = ["@startuml", "!include <archimate/Archimate>", ""]
    for cid in concept_ids:
        c = model.concepts.get(cid)
        if not c:
            continue
        if c.canonical_type == "Junction":
            out.append(f"Junction({alias(cid)})"); continue
        macro = model.mm.plantuml_macro(c.canonical_type) if c.canonical_type else None
        if macro:
            out.append(f'{macro}({alias(cid)}, "{esc(c.name)}")')
        else:
            out.append(f'rectangle "{esc(c.name)}" as {alias(cid)}')
    out.append("")
    member = set(concept_ids)
    for rid in rel_ids:
        r = model.relationships.get(rid)
        if not r or r.source not in member or r.target not in member:
            continue
        macro = model.mm.relationship_macro(r.canonical_type) or "Rel_Association"
        out.append(f"{macro}({alias(r.source)}, {alias(r.target)})")
    out += ["", "@enduml", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="PlantUML from an Archi-native model.")
    ap.add_argument("model")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--view", help="emit a single view (id or name); default = whole model")
    args = ap.parse_args(argv)

    model = NativeModel(args.model)
    os.makedirs(args.out, exist_ok=True)

    if args.view:
        view = model.diagrams.get(args.view) or next(
            (d for d in model.diagrams.values() if d.name == args.view), None)
        if not view:
            sys.stderr.write(f"view not found: {args.view}\n"); return 1
        cids = [o.concept_id for o in view.objects.values()]
        rids = [c.relationship_id for c in view.connections.values()]
        path = os.path.join(args.out, f"{view.id}.puml")
        targets = [(path, cids, rids)]
    else:
        cids = list(model.concepts)
        rids = list(model.relationships)
        targets = [(os.path.join(args.out, "model.puml"), cids, rids)]

    for path, cids, rids in targets:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(emit(model, cids, rids))
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
