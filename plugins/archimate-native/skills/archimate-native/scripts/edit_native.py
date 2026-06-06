#!/usr/bin/env python3
"""Surgically edit an Archi-native .archimate model in place (round-trip-safe).

Mutates ONLY the targeted nodes; every untouched node, id, bound, and bendpoint is
preserved byte-for-byte. Always preview with --dry-run (prints a unified diff)
before applying. Relationship additions are validated against the ArchiMate 3.2
metamodel. Deletes cascade-clean relationships and diagram objects/connections.
See references/operations.md.

Subcommands: add-concept, add-rel, rename, set-property, remove-property,
set-doc, add-to-view, delete-concept.
"""

from __future__ import annotations

import argparse
import difflib
import sys

from lxml import etree

from native_model import NativeModel, XSI_TYPE

DEFAULT_FILL = "#ffffb5"
NW, NH = 120, 55


# ---- minimal-diff tree helpers -------------------------------------------
def _depth(el):
    d, p = 0, el.getparent()
    while p is not None:
        d += 1
        p = p.getparent()
    return d


def _append(parent, new_el, child_depth):
    indent = "\n" + "  " * child_depth
    children = list(parent)
    if children:
        new_el.tail = children[-1].tail   # inherit the close-tag indent
        children[-1].tail = indent
    else:
        new_el.tail = parent.text
        parent.text = indent
    parent.append(new_el)


def _indent_subtree(el, depth):
    children = list(el)
    if not children:
        return
    el.text = "\n" + "  " * (depth + 1)
    for i, ch in enumerate(children):
        _indent_subtree(ch, depth + 1)
        ch.tail = ("\n" + "  " * (depth + 1)) if i < len(children) - 1 else ("\n" + "  " * depth)


def _remove(el):
    parent = el.getparent()
    prev = el.getprevious()
    if prev is not None:
        prev.tail = el.tail
    else:
        parent.text = el.tail
    parent.remove(el)


def _set_xsi(el, native_type):
    el.set(XSI_TYPE, f"archimate:{native_type}")


def _folder_by_type(model, ftype):
    for f in model.folders:
        if f.type == ftype and f.parent is None:
            return f
    return None


# ---- operations -----------------------------------------------------------
def op_add_concept(model, args):
    canon = args.type
    if not model.mm.is_element_type(canon):
        sys.stderr.write(f"unknown element type: {canon}\n"); return None
    layer = model.mm.layer_of(canon)
    folder = (next((f for f in model.folders if f.name == args.folder), None)
              if args.folder else model.folder_for_layer(layer))
    if folder is None:
        sys.stderr.write(f"no folder for layer '{layer}'; pass --folder NAME of an existing folder.\n")
        return None
    el = etree.Element("element")
    _set_xsi(el, model.to_native(canon, "concept"))
    el.set("id", model.new_id())
    el.set("name", args.name)
    if args.doc:
        d = etree.SubElement(el, "documentation"); d.text = args.doc
    _append(folder.el, el, _depth(folder.el) + 1)
    _indent_subtree(el, _depth(folder.el) + 1)
    return f"added {canon} '{args.name}' (id {el.get('id')}) to folder '{folder.name}'"


def op_add_rel(model, args):
    canon = args.type
    if not model.mm.is_relationship_type(canon):
        sys.stderr.write(f"unknown relationship type: {canon}\n"); return None
    src, dst = model.concepts.get(args.source), model.concepts.get(args.target)
    if not src or not dst:
        sys.stderr.write("source/target must be existing concept ids.\n"); return None
    if not model.mm.relationship_allowed(canon, src.canonical_type, dst.canonical_type):
        allowed = model.mm.allowed_relationships(src.canonical_type, dst.canonical_type) or ["Association"]
        sys.stderr.write(f"REFUSED: {canon} from {src.canonical_type} to {dst.canonical_type} "
                         f"is not allowed. Permitted: {', '.join(allowed)}.\n")
        return None
    folder = _folder_by_type(model, "relations")
    if folder is None:
        sys.stderr.write("no 'relations' folder found.\n"); return None
    el = etree.Element("element")
    _set_xsi(el, model.to_native(canon, "relationship"))
    el.set("id", model.new_id())
    el.set("source", args.source); el.set("target", args.target)
    if args.name:
        el.set("name", args.name)
    _append(folder.el, el, _depth(folder.el) + 1)
    return f"added {canon} {src.name} → {dst.name} (id {el.get('id')})"


def op_rename(model, args):
    c = model.concepts.get(args.id) or model.relationships.get(args.id)
    if not c:
        sys.stderr.write(f"no concept/relationship with id {args.id}\n"); return None
    old = c.el.get("name") or ""
    c.el.set("name", args.name)
    return f"renamed {args.id}: '{old}' → '{args.name}'"


def op_set_property(model, args):
    c = model.concepts.get(args.id)
    if not c:
        sys.stderr.write(f"no concept with id {args.id}\n"); return None
    for p in c.el.findall("property"):
        if p.get("key") == args.key:
            p.set("value", args.value or "")
            return f"updated property {args.key} on {args.id}"
    p = etree.Element("property"); p.set("key", args.key); p.set("value", args.value or "")
    _append(c.el, p, _depth(c.el) + 1)
    return f"added property {args.key}={args.value} on {args.id}"


def op_remove_property(model, args):
    c = model.concepts.get(args.id)
    if not c:
        sys.stderr.write(f"no concept with id {args.id}\n"); return None
    for p in c.el.findall("property"):
        if p.get("key") == args.key:
            _remove(p)
            return f"removed property {args.key} on {args.id}"
    sys.stderr.write(f"property {args.key} not found on {args.id}\n"); return None


def op_set_doc(model, args):
    c = model.concepts.get(args.id)
    if not c:
        sys.stderr.write(f"no concept with id {args.id}\n"); return None
    d = c.el.find("documentation")
    if d is not None:
        d.text = args.text
        return f"updated documentation on {args.id}"
    d = etree.Element("documentation"); d.text = args.text
    # documentation must precede property children if present
    first_prop = c.el.find("property")
    if first_prop is not None:
        first_prop.addprevious(d); d.tail = first_prop.tail
        _reindent_children(c.el, _depth(c.el))
    else:
        _append(c.el, d, _depth(c.el) + 1)
    return f"added documentation on {args.id}"


def _reindent_children(el, depth):
    children = list(el)
    if not children:
        return
    el.text = "\n" + "  " * (depth + 1)
    for i, ch in enumerate(children):
        ch.tail = ("\n" + "  " * (depth + 1)) if i < len(children) - 1 else ("\n" + "  " * depth)


def op_add_to_view(model, args):
    view = model.diagrams.get(args.view) or next(
        (d for d in model.diagrams.values() if d.name == args.view), None)
    if not view:
        sys.stderr.write(f"view not found: {args.view}\n"); return None
    concept = model.concepts.get(args.concept)
    if not concept:
        sys.stderr.write(f"concept not found: {args.concept}\n"); return None
    # placement — never disturb existing objects
    x, y = 24, 24
    if args.near:
        near = next((o for o in view.objects.values() if o.concept_id == args.near), None)
        if near and near.bounds():
            b = near.bounds(); x, y = b["x"] + b["width"] + 40, b["y"]
    else:
        max_y = -1
        for o in view.objects.values():
            b = o.bounds()
            if b and o.el.getparent() is view.el:
                max_y = max(max_y, b["y"] + b["height"])
        if max_y >= 0:
            x, y = 24, max_y + 40
    child = etree.Element("child")
    _set_xsi(child, "DiagramObject")
    child.set("id", model.new_id())
    child.set("textAlignment", "2"); child.set("fillColor", DEFAULT_FILL)
    child.set("archimateElement", concept.id)
    b = etree.SubElement(child, "bounds")
    b.set("x", str(x)); b.set("y", str(y)); b.set("width", str(NW)); b.set("height", str(NH))
    _append(view.el, child, _depth(view.el) + 1)
    _indent_subtree(child, _depth(view.el) + 1)
    return f"added '{concept.name}' to view '{view.name}' at ({x},{y})"


def op_delete_concept(model, args):
    c = model.concepts.get(args.id)
    if not c:
        sys.stderr.write(f"no concept with id {args.id}\n"); return None
    rels = model.rels_of(args.id, "both")
    rel_ids = {r.id for r in rels}
    diagobj_ids = {o.id for o in model.diagobjs_by_concept.get(args.id, [])}
    # connections to remove: those of a removed relationship, or touching a removed object
    conn_to_remove = []
    for d in model.diagrams.values():
        for conn in d.connections.values():
            if conn.relationship_id in rel_ids or conn.source in diagobj_ids or conn.target in diagobj_ids:
                conn_to_remove.append(conn)
    removed_conn_ids = {conn.id for conn in conn_to_remove}
    # strip removed connection ids from any targetConnections attr
    for d in model.diagrams.values():
        for o in d.objects.values():
            tc = o.el.get("targetConnections")
            if tc:
                kept = [i for i in tc.split() if i not in removed_conn_ids]
                if kept:
                    o.el.set("targetConnections", " ".join(kept))
                else:
                    del o.el.attrib["targetConnections"]
    for conn in conn_to_remove:
        _remove(conn.el)
    for o in model.diagobjs_by_concept.get(args.id, []):
        _remove(o.el)
    for r in rels:
        _remove(r.el)
    _remove(c.el)
    return (f"deleted concept '{c.name}' (id {args.id}); cascaded "
            f"{len(rels)} relationship(s), {len(diagobj_ids)} diagram object(s), "
            f"{len(conn_to_remove)} connection(s)")


def _assert_no_new_dangling(new_bytes):
    """Load the post-edit bytes and fail if any dangling concept/relationship refs exist."""
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".archimate"); os.close(fd)
    try:
        with open(tmp, "wb") as fh:
            fh.write(new_bytes)
        m = NativeModel(tmp)
        bad = []
        for r in m.relationships.values():
            if r.source not in m.concepts:
                bad.append(f"rel {r.id} → missing source {r.source}")
            if r.target not in m.concepts:
                bad.append(f"rel {r.id} → missing target {r.target}")
        for d in m.diagrams.values():
            for o in d.objects.values():
                if o.concept_id not in m.concepts:
                    bad.append(f"view {d.id} object → missing concept {o.concept_id}")
        return bad
    finally:
        os.unlink(tmp)


OPS = {
    "add-concept": op_add_concept, "add-rel": op_add_rel, "rename": op_rename,
    "set-property": op_set_property, "remove-property": op_remove_property,
    "set-doc": op_set_doc, "add-to-view": op_add_to_view, "delete-concept": op_delete_concept,
}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Surgically edit an Archi-native .archimate model.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("model")
        p.add_argument("--dry-run", action="store_true", help="print a unified diff, do not write")

    p = sub.add_parser("add-concept"); common(p)
    p.add_argument("--type", required=True); p.add_argument("--name", required=True)
    p.add_argument("--folder"); p.add_argument("--doc")
    p = sub.add_parser("add-rel"); common(p)
    p.add_argument("--type", required=True); p.add_argument("--source", required=True)
    p.add_argument("--target", required=True); p.add_argument("--name")
    p = sub.add_parser("rename"); common(p); p.add_argument("--id", required=True); p.add_argument("--name", required=True)
    p = sub.add_parser("set-property"); common(p)
    p.add_argument("--id", required=True); p.add_argument("--key", required=True); p.add_argument("--value")
    p = sub.add_parser("remove-property"); common(p); p.add_argument("--id", required=True); p.add_argument("--key", required=True)
    p = sub.add_parser("set-doc"); common(p); p.add_argument("--id", required=True); p.add_argument("--text", required=True)
    p = sub.add_parser("add-to-view"); common(p)
    p.add_argument("--view", required=True); p.add_argument("--concept", required=True); p.add_argument("--near")
    p = sub.add_parser("delete-concept"); common(p)
    p.add_argument("--id", required=True); p.add_argument("--yes", action="store_true", help="confirm cascade delete")

    args = ap.parse_args(argv)
    if args.cmd == "delete-concept" and not args.yes and not args.dry_run:
        sys.stderr.write("delete-concept cascades; re-run with --dry-run to preview, then --yes to apply.\n")
        return 2

    model = NativeModel(args.model)
    original = open(args.model, "rb").read()
    msg = OPS[args.cmd](model, args)
    if msg is None:
        return 2
    new_bytes = model.serialize()

    dangling = _assert_no_new_dangling(new_bytes)
    if dangling:
        sys.stderr.write("ABORT: edit would leave dangling references:\n  " + "\n  ".join(dangling) + "\n")
        return 2

    if args.dry_run:
        diff = difflib.unified_diff(
            original.decode("utf-8").splitlines(True), new_bytes.decode("utf-8").splitlines(True),
            fromfile=args.model, tofile=args.model + " (proposed)")
        sys.stdout.writelines(diff)
        print(f"\n# DRY RUN: {msg}")
        return 0

    with open(args.model, "wb") as fh:
        fh.write(new_bytes)
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
