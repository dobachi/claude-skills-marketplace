#!/usr/bin/env python3
"""Read & review an Archi-native .archimate model (read-only).

Subcommands: summary, list, trace, orphans, violations, interpret-view.
Findings reuse the canonical ArchiMate 3.2 metamodel (allowed-relationship matrix)
by normalizing native types to canonical. Output is compact text or JSON, designed
to drive the facilitation dialogue. See references/review-checks.md.

Usage:
    review_native.py summary       MODEL.archimate
    review_native.py list          MODEL.archimate [--layer L] [--type T] [--folder F]
    review_native.py trace         MODEL.archimate --concept ID|NAME [--direction in|out|both] [--depth N] [--rel TYPE]
    review_native.py orphans       MODEL.archimate
    review_native.py violations    MODEL.archimate [--format text|json]
    review_native.py interpret-view MODEL.archimate --view ID|NAME
"""

from __future__ import annotations

import argparse
import json
import sys

from native_model import NativeModel

ERROR, WARN = "ERROR", "WARN"
MOTIVATION_REALIZED = {"Goal", "Requirement", "Outcome"}


def _ctype(model, cid):
    c = model.concepts.get(cid)
    return c.canonical_type if c else None


# ---- checks (shared by summary/violations) -------------------------------
def collect_violations(model):
    problems = []
    def P(sev, code, ref, msg):
        problems.append({"severity": sev, "code": code, "ref": ref, "message": msg})

    for c in model.concepts.values():
        if c.canonical_type is None:
            P(ERROR, "unknown-type", c.id,
              f"concept '{c.name or c.id}' has native type '{c.native_type}' with no canonical mapping.")

    for r in model.relationships.values():
        src, dst = model.concepts.get(r.source), model.concepts.get(r.target)
        if src is None:
            P(ERROR, "dangling-source", r.id, f"relationship '{r.id}' source '{r.source}' is not a concept.")
        if dst is None:
            P(ERROR, "dangling-target", r.id, f"relationship '{r.id}' target '{r.target}' is not a concept.")
        if r.canonical_type is None:
            P(ERROR, "unknown-relationship", r.id, f"relationship '{r.id}' native type '{r.native_type}' unmapped.")
        if src and dst and r.canonical_type and src.canonical_type and dst.canonical_type:
            if not model.mm.relationship_allowed(r.canonical_type, src.canonical_type, dst.canonical_type):
                allowed = model.mm.allowed_relationships(src.canonical_type, dst.canonical_type) or ["Association"]
                P(ERROR, "illegal-relationship", r.id,
                  f"{r.canonical_type} from {src.canonical_type}({src.name or src.id}) to "
                  f"{dst.canonical_type}({dst.name or dst.id}) is not allowed. Permitted: {', '.join(allowed)}.")

    # dangling diagram references (pre-existing corruption)
    for d in model.diagrams.values():
        for do in d.objects.values():
            if do.concept_id not in model.concepts:
                P(WARN, "dangling-diagram-object", do.id,
                  f"view '{d.name or d.id}': object references missing concept '{do.concept_id}'.")
        for conn in d.connections.values():
            if conn.relationship_id and conn.relationship_id not in model.relationships:
                P(WARN, "dangling-connection", conn.id,
                  f"view '{d.name or d.id}': connection references missing relationship '{conn.relationship_id}'.")
    return problems


def collect_orphans(model):
    no_rels, unrealized = [], []
    for c in model.concepts.values():
        if not model.rels_of(c.id, "both"):
            no_rels.append(c)
        elif c.canonical_type in MOTIVATION_REALIZED:
            incoming = [r for r in model.rels_of(c.id, "in")
                        if r.canonical_type in ("Realization", "Influence")]
            if not incoming:
                unrealized.append(c)
    return no_rels, unrealized


# ---- subcommands ----------------------------------------------------------
def cmd_summary(model, args):
    by_layer, by_folder = {}, {}
    for c in model.concepts.values():
        layer = model.mm.layer_of(c.canonical_type) if c.canonical_type else "unknown"
        by_layer[layer] = by_layer.get(layer, 0) + 1
        fname = c.folder.name if c.folder else "?"
        by_folder[fname] = by_folder.get(fname, 0) + 1
    viol = collect_violations(model)
    no_rels, unrealized = collect_orphans(model)
    print(f"{model.name}  (version {model.version}, era={model.era})")
    if model.purpose:
        print(f"  purpose: {model.purpose}")
    print(f"  concepts={len(model.concepts)}  relationships={len(model.relationships)}  views={len(model.diagrams)}")
    print("  by layer:   " + ", ".join(f"{k}={v}" for k, v in sorted(by_layer.items())))
    print("  by folder:  " + ", ".join(f"{k}={v}" for k, v in sorted(by_folder.items())))
    errs = sum(1 for p in viol if p["severity"] == ERROR)
    print(f"  red flags:  {errs} metamodel error(s), {len(no_rels)} orphan(s), {len(unrealized)} unrealized goal/requirement(s)")


def cmd_list(model, args):
    rows = []
    for c in model.concepts.values():
        layer = model.mm.layer_of(c.canonical_type) if c.canonical_type else "unknown"
        if args.layer and layer != args.layer:
            continue
        if args.type and c.canonical_type != args.type:
            continue
        if args.folder and (not c.folder or c.folder.name != args.folder):
            continue
        rows.append((c.id, c.canonical_type or c.native_type, c.name, c.folder.name if c.folder else "?"))
    for cid, t, name, folder in sorted(rows, key=lambda r: (r[3], r[1])):
        print(f"  {cid:<12} {t:<24} {name}   [{folder}]")
    print(f"  ({len(rows)} concept(s))")


def cmd_trace(model, args):
    start = model.find_concept(args.concept)
    if not start:
        sys.stderr.write(f"concept not found: {args.concept}\n"); return 1
    seen = {start.id}
    frontier = [(start.id, 0)]
    print(f"trace from {start.name or start.id} (depth {args.depth}, {args.direction}):")
    while frontier:
        cid, depth = frontier.pop(0)
        if depth >= args.depth:
            continue
        for r in model.rels_of(cid, args.direction):
            if args.rel and r.canonical_type != args.rel:
                continue
            other = r.target if r.source == cid else r.source
            arrow = "->" if r.source == cid else "<-"
            print(f"  {'  '*depth}{model.label(cid)} {arrow}[{r.canonical_type}] {model.label(other)}")
            if other not in seen:
                seen.add(other); frontier.append((other, depth + 1))
    return 0


def cmd_orphans(model, args):
    no_rels, unrealized = collect_orphans(model)
    print("orphans (no relationships):")
    for c in no_rels:
        print(f"  {c.id:<12} {c.canonical_type or c.native_type:<20} {c.name}")
    print("unrealized goals/requirements (nothing realizes/influences them):")
    for c in unrealized:
        print(f"  {c.id:<12} {c.canonical_type:<20} {c.name}")
    if not no_rels and not unrealized:
        print("  none.")


def cmd_violations(model, args):
    problems = collect_violations(model)
    if args.format == "json":
        n_err = sum(1 for p in problems if p["severity"] == ERROR)
        print(json.dumps({"model": model.path, "errors": n_err,
                          "problems": problems}, ensure_ascii=False, indent=2))
    else:
        print(f"{model.path} — review")
        for p in sorted(problems, key=lambda x: 0 if x["severity"] == ERROR else 1):
            print(f"  {p['severity']:<5} [{p['code']}]  {p['ref']}: {p['message']}")
        if not problems:
            print("  clean — no violations.")
        n_err = sum(1 for p in problems if p["severity"] == ERROR)
        print(f"  Summary: {n_err} error(s), {len(problems) - n_err} warning(s).")
    return 2 if any(p["severity"] == ERROR for p in problems) else 0


def cmd_interpret_view(model, args):
    view = model.diagrams.get(args.view) or next(
        (d for d in model.diagrams.values() if d.name == args.view), None)
    if not view:
        sys.stderr.write(f"view not found: {args.view}\n"); return 1
    print(f"View: {view.name or view.id}" + (f"  (viewpoint {view.viewpoint})" if view.viewpoint else ""))
    layers = set()
    print("  shows:")
    for do in view.objects.values():
        c = model.concepts.get(do.concept_id)
        if c:
            layer = model.mm.layer_of(c.canonical_type) if c.canonical_type else "?"
            layers.add(layer)
            print(f"    - {c.name}  ({c.canonical_type}, {layer})")
    print("  connections:")
    for conn in view.connections.values():
        r = model.relationships.get(conn.relationship_id)
        if r:
            print(f"    - {model.label(r.source)} —{r.canonical_type}→ {model.label(r.target)}")
    print(f"  spans layers: {', '.join(sorted(layers)) or '(none)'}; "
          f"{len(view.objects)} object(s), {len(view.connections)} connection(s).")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read & review an Archi-native .archimate model.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("summary", "orphans"):
        s = sub.add_parser(name); s.add_argument("model")
    s = sub.add_parser("list"); s.add_argument("model")
    s.add_argument("--layer"); s.add_argument("--type"); s.add_argument("--folder")
    s = sub.add_parser("trace"); s.add_argument("model")
    s.add_argument("--concept", required=True); s.add_argument("--direction", default="both",
                   choices=["in", "out", "both"]); s.add_argument("--depth", type=int, default=2)
    s.add_argument("--rel")
    s = sub.add_parser("violations"); s.add_argument("model")
    s.add_argument("--format", choices=["text", "json"], default="text")
    s = sub.add_parser("interpret-view"); s.add_argument("model"); s.add_argument("--view", required=True)
    args = ap.parse_args(argv)

    model = NativeModel(args.model)
    return {
        "summary": cmd_summary, "list": cmd_list, "trace": cmd_trace,
        "orphans": cmd_orphans, "violations": cmd_violations, "interpret-view": cmd_interpret_view,
    }[args.cmd](model, args) or 0


if __name__ == "__main__":
    sys.exit(main())
