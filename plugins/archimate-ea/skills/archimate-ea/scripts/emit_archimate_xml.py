#!/usr/bin/env python3
"""Emit an Open Group ArchiMate Model Exchange File Format (3.x) XML document.

Generate-forward: the YAML model is upstream; the XML is downstream, for
interchange with the Archi tool (File -> Import -> Open Exchange File). The
schema requires node geometry. The default `layered` layout reflects the model's
logical structure — ArchiMate layers become stacked horizontal bands (motivation
at top down to technology/implementation) and nodes within a band are ordered by
a barycenter heuristic to reduce edge crossings — so the imported view reads
top-down instead of as an arbitrary grid. `grid` (the old placeholder) and `none`
remain for when you intend to re-run Archi's own auto-layout after import.

Refuses to emit if the model has ERROR-level validation problems.

Usage:
    emit_archimate_xml.py MODEL.yaml -o OUT.xml [--layout layered|grid|none] [--xsd SCHEMA.xsd] [--force]
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
BAND_GAP = 70          # vertical space between layer bands in the layered layout
JW, JH = 14, 14        # junction / connector node size (small, like Archi's dots)

# ArchiMate layers top-to-bottom; connector (junctions) and composite (Grouping,
# Location) have no band and are slotted between their neighbours by barycenter.
LAYER_BANDS = ["motivation", "strategy", "business",
               "application", "technology", "physical", "implementation"]


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


def compute_layout(members, edges, node_layer, strategy):
    """Return {eid: (x, y, w, h)} for the nodes of one view.

    strategy 'layered' places elements in horizontal bands by ArchiMate layer and
    orders each band with a barycenter sweep so related elements line up vertically;
    'grid' is the legacy row-major placeholder; 'none' emits zero geometry (defer to
    Archi's own auto-layout)."""
    if strategy == "none":
        return {eid: (0, 0, 0, 0) for eid in members}
    if strategy == "grid":
        pos = {}
        for i, eid in enumerate(members):
            col, row = i % GRID_COLS, i // GRID_COLS
            pos[eid] = (MARGIN + col * (NW + GAP), MARGIN + row * (NH + GAP), NW, NH)
        return pos
    return _layered_layout(members, edges, node_layer)


def _layered_layout(members, edges, node_layer):
    band_rank = {name: i for i, name in enumerate(LAYER_BANDS)}
    mset = set(members)
    adj = {m: set() for m in members}
    for s, t in edges:
        if s in mset and t in mset and s != t:
            adj[s].add(t)
            adj[t].add(s)

    # 1. band per node; connector/composite (no rank) inherit their neighbours' mean.
    raw = {m: band_rank.get(node_layer.get(m)) for m in members}
    for _ in range(3):
        for m in members:
            if raw[m] is None:
                nb = [raw[n] for n in adj[m] if raw[n] is not None]
                if nb:
                    raw[m] = int(round(sum(nb) / len(nb)))
    for m in members:
        if raw[m] is None:
            raw[m] = 0

    # 2. compress to consecutive rows; seed each band in stable membership order.
    rows = {b: i for i, b in enumerate(sorted(set(raw.values())))}
    bands = [[] for _ in rows]
    for m in members:               # members is already in view order -> stable
        bands[rows[raw[m]]].append(m)

    # 3. barycenter crossing reduction: alternate down/up sweeps.
    pos = {m: i for band in bands for i, m in enumerate(band)}
    for sweep in range(4):
        order = range(1, len(bands)) if sweep % 2 == 0 else range(len(bands) - 2, -1, -1)
        for bi in order:
            band = bands[bi]
            band.sort(key=lambda m: (
                sum(pos[n] for n in adj[m]) / len(adj[m]) if adj[m] else pos[m], pos[m]))
            for i, m in enumerate(band):
                pos[m] = i

    # 4. coordinates: bands stacked vertically, each centred on the widest band.
    def size(m):
        return (JW, JH) if node_layer.get(m) not in band_rank else (NW, NH)
    span = [sum(size(m)[0] + GAP for m in band) for band in bands]
    widest = max(span) if span else 0
    coords = {}
    y = MARGIN
    for bi, band in enumerate(bands):
        x = MARGIN + max(0, (widest - span[bi]) // 2)
        for m in band:
            w, h = size(m)
            coords[m] = (x, y + (NH - h) // 2, w, h)
            x += w + GAP
        y += NH + BAND_GAP
    return coords


def build(model, mm, layout="layered") -> etree._Element:
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
        _set_xsi_type(rel, r.get("type"))
        # NOTE: Influence 'strength' AND Association 'isDirected' are notation modifiers,
        # not Open Exchange 3.0 schema attributes (isDirected arrived in 3.1). They are
        # kept in YAML (and rendered in PlantUML) but not emitted here — emitting
        # isDirected fails Archi import with cvc-complex-type ("attribute not allowed").

    # ---- organizations ---------------------------------------------------
    if model.organizations:
        orgs_el = etree.SubElement(root, "organizations")

        def emit_org(parent, org):
            # Open Exchange 3.0: organizations contain <item> (label-only folder or
            # identifierRef leaf); there is no <organization> element. Nested folders
            # are <item> with a <label>. (Previously emitted <organization>, which is
            # not in the XSD and fails Archi import with cvc-complex-type.2.4.a.)
            o = etree.SubElement(parent, "item")
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
            member_set = set(members)
            edges = [(r.get("source"), r.get("target"))
                     for rid in (v.get("relationships", []) or [])
                     for r in [model.rel_by_id.get(rid)] if r
                     and r.get("source") in member_set and r.get("target") in member_set]
            node_layer = {m: mm.layer_of(model.element_by_id[m].get("type")) for m in members}
            coords = compute_layout(members, edges, node_layer, layout)
            for eid in members:
                nid = f"node-{xml_id(v['id'])}-{xml_id(eid)}"
                node_id[eid] = nid
                n = etree.SubElement(view, "node")
                n.set("identifier", nid)
                n.set("elementRef", id_map[eid])
                _set_xsi_type(n, "Element")
                x, y, w, h = coords[eid]
                n.set("x", str(x))
                n.set("y", str(y))
                n.set("w", str(w))
                n.set("h", str(h))
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
    ap.add_argument("--layout", choices=["layered", "grid", "none"], default="layered",
                    help="node geometry: 'layered' = structure-aware bands by ArchiMate "
                         "layer (default); 'grid' = row-major placeholder; 'none' = zeros "
                         "(defer to Archi auto-layout)")
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

    root = build(model, mm, layout=args.layout)
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
