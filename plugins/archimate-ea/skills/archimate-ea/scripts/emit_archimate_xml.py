#!/usr/bin/env python3
"""Emit an Open Group ArchiMate Model Exchange File Format (3.x) XML document.

Generate-forward: the YAML model is upstream; the XML is downstream, for
interchange with the Archi tool (File -> Import -> Open Exchange File). The
schema requires node geometry, so a simple grid layout is written as a
placeholder — run Archi's auto-layout / "format" after import.

Refuses to emit if the model has ERROR-level validation problems.

Usage:
    emit_archimate_xml.py MODEL.yaml -o OUT.xml [--layout grid|none] [--xsd SCHEMA.xsd] [--force]
"""

from __future__ import annotations

import argparse
import re
import sys

from lxml import etree

from archimate_metamodel import load as load_metamodel
from validate_model import load_model, validate, ERROR

ARCHI_NS = "http://www.opengroup.org/xsd/archimate/3.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NSMAP = {None: ARCHI_NS, "xsi": XSI_NS}

_ID_RE = re.compile(r"[^\w.\-]")
GRID_COLS = 5
NW, NH, GAP, MARGIN = 120, 55, 40, 20


def xml_id(raw: str) -> str:
    s = _ID_RE.sub("_", str(raw))
    return s if (s[:1].isalpha() or s[:1] == "_") else "id_" + s


def _set_xsi_type(el, value):
    el.set(f"{{{XSI_NS}}}type", value)


def _add_lang_texts(parent, tag, value):
    """Append one <tag xml:lang="..">text</tag> per language (or a plain <tag> for a string)."""
    if isinstance(value, dict):
        for lang, text in value.items():
            e = etree.SubElement(parent, tag)
            e.set(f"{{{XML_NS}}}lang", str(lang))
            e.text = str(text)
    elif value is not None:
        e = etree.SubElement(parent, tag)
        e.text = str(value)


def build(model, mm) -> etree._Element:
    id_map = {}  # original id -> xml id (elements + relationships)
    for e in model.elements:
        if isinstance(e, dict) and e.get("id"):
            id_map[e["id"]] = xml_id(e["id"])
    for r in model.relationships:
        if isinstance(r, dict) and r.get("id"):
            id_map[r["id"]] = xml_id(r["id"])

    root = etree.Element(f"{{{ARCHI_NS}}}model", nsmap=NSMAP)
    root.set("identifier", xml_id(model.header.get("id", "model")))
    _add_lang_texts(root, "name", model.header.get("name") or model.header.get("id", "model"))
    _add_lang_texts(root, "documentation", model.header.get("documentation"))

    # ---- elements --------------------------------------------------------
    elements_el = etree.SubElement(root, "elements")
    for e in model.elements:
        if not isinstance(e, dict):
            continue
        el = etree.SubElement(elements_el, "element")
        el.set("identifier", id_map[e["id"]])
        _set_xsi_type(el, mm.xsi_type(e.get("type"), e.get("junctionType")))
        _add_lang_texts(el, "name", e.get("name"))
        _add_lang_texts(el, "documentation", e.get("documentation"))
        props = e.get("properties") or {}
        if props:
            props_el = etree.SubElement(el, "properties")
            for key, val in props.items():
                p = etree.SubElement(props_el, "property")
                p.set("propertyDefinitionRef", f"propid-{xml_id(key)}")
                _add_lang_texts(p, "value", {"en": val} if not isinstance(val, dict) else val)

    # ---- relationships ---------------------------------------------------
    rels_el = etree.SubElement(root, "relationships")
    for r in model.relationships:
        if not isinstance(r, dict):
            continue
        rel = etree.SubElement(rels_el, "relationship")
        rel.set("identifier", id_map[r["id"]])
        rel.set("source", id_map.get(r.get("source"), xml_id(r.get("source", ""))))
        rel.set("target", id_map.get(r.get("target"), xml_id(r.get("target", ""))))
        if r.get("type") == "Access" and r.get("accessType"):
            rel.set("accessType", mm.access_type_xml(r["accessType"]))
        if r.get("type") == "Association" and r.get("isDirected"):
            rel.set("isDirected", "true")
        _set_xsi_type(rel, r.get("type"))
        # NOTE: Influence 'strength' is a notation modifier, not a schema attribute;
        # it is kept in YAML (and rendered in PlantUML) but not emitted here.

    # ---- organizations ---------------------------------------------------
    if model.organizations:
        orgs_el = etree.SubElement(root, "organizations")

        def emit_org(parent, org):
            o = etree.SubElement(parent, "organization")
            _add_lang_texts(o, "label", org.get("label"))
            for ref in org.get("items", []) or []:
                if ref in id_map:
                    etree.SubElement(o, "item").set("identifierRef", id_map[ref])
            for child in org.get("children", []) or []:
                emit_org(o, child)

        for org in model.organizations:
            if isinstance(org, dict):
                emit_org(orgs_el, org)

    # ---- propertyDefinitions (schema order: after organizations) ---------
    if model.property_defs:
        pdefs_el = etree.SubElement(root, "propertyDefinitions")
        for pd in model.property_defs:
            if not isinstance(pd, dict):
                continue
            d = etree.SubElement(pdefs_el, "propertyDefinition")
            d.set("identifier", f"propid-{xml_id(pd.get('key', ''))}")
            d.set("type", pd.get("type", "string"))
            _add_lang_texts(d, "name", pd.get("name") or pd.get("key"))

    # ---- views -----------------------------------------------------------
    if model.views:
        diagrams = etree.SubElement(etree.SubElement(root, "views"), "diagrams")
        for v in model.views:
            if not isinstance(v, dict) or not v.get("id"):
                continue
            view = etree.SubElement(diagrams, "view")
            view.set("identifier", xml_id(v["id"]))
            _set_xsi_type(view, "Diagram")
            _add_lang_texts(view, "name", v.get("name"))

            node_id = {}  # element id -> node id (unique per view)
            members = [m for m in (v.get("elements", []) or []) if m in model.element_by_id]
            for i, eid in enumerate(members):
                nid = f"node-{xml_id(v['id'])}-{xml_id(eid)}"
                node_id[eid] = nid
                n = etree.SubElement(view, "node")
                n.set("identifier", nid)
                n.set("elementRef", id_map[eid])
                _set_xsi_type(n, "Element")
                col, row = i % GRID_COLS, i // GRID_COLS
                n.set("x", str(MARGIN + col * (NW + GAP)))
                n.set("y", str(MARGIN + row * (NH + GAP)))
                n.set("w", str(NW))
                n.set("h", str(NH))
            for rid in v.get("relationships", []) or []:
                r = model.rel_by_id.get(rid)
                if not r:
                    continue
                s, t = r.get("source"), r.get("target")
                if s not in node_id or t not in node_id:
                    continue
                c = etree.SubElement(view, "connection")
                c.set("identifier", f"conn-{xml_id(v['id'])}-{xml_id(rid)}")
                c.set("relationshipRef", id_map[rid])
                c.set("source", node_id[s])
                c.set("target", node_id[t])
                _set_xsi_type(c, "Relationship")

    return root


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit Open Group ArchiMate Exchange XML from a running model.")
    ap.add_argument("model")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--layout", choices=["grid", "none"], default="grid",
                    help="node geometry strategy (grid placeholder, or zeros)")
    ap.add_argument("--xsd", help="validate output against the official ArchiMate Exchange XSD")
    ap.add_argument("--force", action="store_true", help="emit even if validation has errors")
    args = ap.parse_args(argv)

    mm = load_metamodel()
    model = load_model(args.model)
    errors = [p for p in validate(model, mm) if p.severity == ERROR]
    if errors and not args.force:
        sys.stderr.write(f"Refusing to emit: {len(errors)} validation error(s). "
                         "Run validate_model.py for details (or pass --force).\n")
        return 2

    if args.layout == "none":
        global MARGIN, NW, NH, GAP
        MARGIN = NW = NH = GAP = 0

    root = build(model, mm)
    tree = etree.ElementTree(root)

    if args.xsd:
        schema = etree.XMLSchema(etree.parse(args.xsd))
        if not schema.validate(root):
            sys.stderr.write("XSD validation FAILED:\n")
            for err in schema.error_log:
                sys.stderr.write(f"  line {err.line}: {err.message}\n")
            return 2
        sys.stderr.write("XSD validation OK\n")

    tree.write(args.out, xml_declaration=True, encoding="UTF-8", pretty_print=True)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
