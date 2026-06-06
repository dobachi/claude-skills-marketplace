#!/usr/bin/env python3
"""Ingest an Archi-exported Open Group Exchange XML back into the YAML running model.

The round-trip return path: emit YAML -> import into Archi -> edit -> export
(File -> Export -> Open Exchange File) -> ingest here. Edits are merged into the
existing ea-model.yaml (the source of truth), keyed on stable ids, with comments
and formatting preserved (ruamel.yaml round-trip). Non-destructive by default:
items present in YAML but absent from the XML are reported, not deleted (use
--prune). Geometry is not recovered; Influence strength and YAML-only fields
(version, viewpoint, …) are preserved. See references/round-trip.md.

A no-op round-trip (emit then ingest with no Archi edits) makes NO changes.

Usage:
    ingest_archi_xml.py MODEL.yaml --xml IN.xml [--prune] [--dry-run]
                        [--format text|json] [--no-validate]
"""

from __future__ import annotations

import argparse
import json
import sys

from lxml import etree
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from emit_archimate_xml import xml_id, ARCHI_NS, XSI_NS, XML_NS
from archimate_metamodel import load as load_metamodel
from validate_model import load_model, validate, ERROR

NS = {"a": ARCHI_NS}
XSI_TYPE = f"{{{XSI_NS}}}type"
XML_LANG = f"{{{XML_NS}}}lang"

ELEMENT_KEYS = ["id", "type", "name", "documentation", "properties", "junctionType"]
REL_KEYS = ["id", "type", "source", "target", "accessType", "isDirected"]


# ---- XML parsing ----------------------------------------------------------
def read_lang_texts(parent, tag):
    els = parent.findall(f"a:{tag}", NS)
    if not els:
        return None
    if len(els) == 1 and els[0].get(XML_LANG) is None:
        return els[0].text
    return {(e.get(XML_LANG) or "und"): e.text for e in els}


def _unwrap_value(v):
    # emitter wraps a scalar property value as {"en": v}; collapse it back.
    if isinstance(v, dict) and len(v) == 1 and "en" in v:
        return v["en"]
    return v


class Incoming:
    def __init__(self, path, mm):
        root = etree.parse(path).getroot()
        self.root = root
        inv_j = {v: k for k, v in mm.modifiers["junctionXsi"].items()}      # AndJunction->and
        inv_a = {v: k for k, v in mm.modifiers["accessTypeXml"].items()}     # Write->write

        self.model_id = root.get("identifier")
        self.name = read_lang_texts(root, "name")
        self.documentation = read_lang_texts(root, "documentation")

        self.elements = []
        for el in root.findall("a:elements/a:element", NS):
            xt = el.get(XSI_TYPE)
            rec = {"xml_id": el.get("identifier")}
            if xt in inv_j:
                rec["type"], rec["junctionType"] = "Junction", inv_j[xt]
            else:
                rec["type"], rec["junctionType"] = xt, None
            rec["name"] = read_lang_texts(el, "name")
            rec["documentation"] = read_lang_texts(el, "documentation")
            props = {}
            for p in el.findall("a:properties/a:property", NS):
                ref = p.get("propertyDefinitionRef") or ""
                key = ref[len("propid-"):] if ref.startswith("propid-") else ref
                props[key] = _unwrap_value(read_lang_texts(p, "value"))
            rec["properties"] = props
            self.elements.append(rec)

        self.relationships = []
        for rel in root.findall("a:relationships/a:relationship", NS):
            at = rel.get("accessType")
            self.relationships.append({
                "xml_id": rel.get("identifier"),
                "type": rel.get(XSI_TYPE),
                "source": rel.get("source"),
                "target": rel.get("target"),
                "accessType": inv_a.get(at) if at else None,
                "isDirected": rel.get("isDirected") == "true",
            })

        self.property_defs = []
        for pd in root.findall("a:propertyDefinitions/a:propertyDefinition", NS):
            ident = pd.get("identifier") or ""
            self.property_defs.append({
                "key": ident[len("propid-"):] if ident.startswith("propid-") else ident,
                "type": pd.get("type", "string"),
                "name": read_lang_texts(pd, "name"),
            })

        self.organizations = [self._org(o) for o in root.findall("a:organizations/a:organization", NS)]

        self.views = []
        for v in root.findall("a:views/a:diagrams/a:view", NS):
            self.views.append({
                "xml_id": v.get("identifier"),
                "name": read_lang_texts(v, "name"),
                "element_refs": [n.get("elementRef") for n in v.findall(".//a:node", NS) if n.get("elementRef")],
                "rel_refs": [c.get("relationshipRef") for c in v.findall(".//a:connection", NS) if c.get("relationshipRef")],
            })

    def _org(self, o):
        return {
            "label": read_lang_texts(o, "label"),
            "items": [i.get("identifierRef") for i in o.findall("a:item", NS)],
            "children": [self._org(c) for c in o.findall("a:organization", NS)],
        }


# ---- helpers --------------------------------------------------------------
def plain(v):
    if isinstance(v, dict):
        return {k: plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    return v


class Report:
    def __init__(self):
        self.added, self.updated, self.removed = [], [], []
        self.view_changes, self.property_changes, self.warnings = [], [], []

    def to_dict(self):
        return {k: getattr(self, k) for k in
                ("added", "updated", "removed", "view_changes", "property_changes", "warnings")}

    def n_changes(self):
        return sum(len(getattr(self, k)) for k in
                   ("added", "updated", "removed", "view_changes", "property_changes"))


def update_langfield(node, key, incoming, rep, ref):
    """Set node[key] from incoming (str | dict | None), preserving formatting.
    Returns True if changed. Never churns when content is equal."""
    existing = node.get(key)
    if incoming is None:
        if key in node:
            del node[key]
            rep.updated.append({"id": ref, "field": key, "old": plain(existing), "new": None})
            return True
        return False
    if plain(existing) == plain(incoming):
        return False
    if isinstance(incoming, dict) and isinstance(existing, dict):
        for lang, text in incoming.items():
            if existing.get(lang) != text:
                existing[lang] = text
        for lang in [l for l in existing if l not in incoming]:
            del existing[lang]
    else:
        node[key] = CommentedMap(incoming) if isinstance(incoming, dict) else incoming
    rep.updated.append({"id": ref, "field": key, "old": plain(existing), "new": plain(incoming)})
    return True


def set_scalar(node, key, value, rep, ref):
    if value is None:
        return False
    if node.get(key) != value:
        old = node.get(key)
        node[key] = value
        rep.updated.append({"id": ref, "field": key, "old": plain(old), "new": plain(value)})
        return True
    return False


def merge_idlist(node, key, incoming_ids, rep, ref):
    existing = list(node.get(key) or [])
    in_set, ex_set = set(incoming_ids), set(existing)
    if in_set == ex_set:
        return
    kept = [x for x in existing if x in in_set]
    added = [x for x in incoming_ids if x not in ex_set]
    node[key] = kept + added
    rep.view_changes.append({"id": ref, "field": key,
                             "added": sorted(in_set - ex_set), "removed": sorted(ex_set - in_set)})


# ---- merge ----------------------------------------------------------------
def ingest(yaml_path, xml_path, prune, mm):
    rep = Report()
    ymodel = load_model(yaml_path)
    incoming = Incoming(xml_path, mm)

    # inverse id map from THIS model (xml_id is not invertible in general)
    xml_to_yaml, seen = {}, {}
    for coll in (ymodel.elements, ymodel.relationships, ymodel.views):
        for item in coll:
            yid = item.get("id")
            if not yid:
                continue
            x = xml_id(yid)
            if x in xml_to_yaml and xml_to_yaml[x] != yid:
                rep.warnings.append(f"id collision: '{yid}' and '{xml_to_yaml[x]}' both sanitize to '{x}'; "
                                    "skipping ambiguous match — disambiguate the ids.")
                seen.setdefault(x, set()).update({yid, xml_to_yaml[x]})
            else:
                xml_to_yaml[x] = yid
    pdkey = {xml_id(pd["key"]): pd["key"] for pd in ymodel.property_defs if pd.get("key")}

    def resolve(xid):
        return xml_to_yaml.get(xid, xid)   # new items keep their (valid) xml id as yaml id

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096                       # don't wrap long lines on dump
    yaml.indent(mapping=2, sequence=4, offset=2)
    with open(yaml_path, encoding="utf-8") as fh:
        data = yaml.load(fh)

    el_nodes = {e["id"]: e for e in data.get("elements", []) if isinstance(e, dict)}
    rel_nodes = {r["id"]: r for r in data.get("relationships", []) if isinstance(r, dict)}
    view_nodes = {v["id"]: v for v in data.get("views", []) if isinstance(v, dict)}
    pdef_nodes = {p["key"]: p for p in data.get("propertyDefinitions", []) if isinstance(p, dict)}

    # ---- elements --------------------------------------------------------
    for ie in incoming.elements:
        if ie["xml_id"] in seen:
            continue
        yid = xml_to_yaml.get(ie["xml_id"])
        if yid and yid in el_nodes:
            node = el_nodes[yid]
            set_scalar(node, "type", ie["type"], rep, yid)
            if ie["type"] == "Junction":
                set_scalar(node, "junctionType", ie["junctionType"], rep, yid)
            update_langfield(node, "name", ie["name"], rep, yid)
            update_langfield(node, "documentation", ie["documentation"], rep, yid)
            _merge_properties(node, ie["properties"], prune, rep, yid)
        else:
            new = CommentedMap()
            new["id"] = ie["xml_id"]
            new["type"] = ie["type"]
            if ie["type"] == "Junction" and ie["junctionType"]:
                new["junctionType"] = ie["junctionType"]
            if ie["name"] is not None:
                new["name"] = CommentedMap(ie["name"]) if isinstance(ie["name"], dict) else ie["name"]
            if ie["documentation"] is not None:
                new["documentation"] = ie["documentation"]
            if ie["properties"]:
                new["properties"] = CommentedMap(ie["properties"])
            data.setdefault("elements", CommentedSeq()).append(new)
            rep.added.append({"kind": "element", "id": ie["xml_id"], "type": ie["type"]})

    # ---- relationships ---------------------------------------------------
    for ir in incoming.relationships:
        if ir["xml_id"] in seen:
            continue
        src, tgt = resolve(ir["source"]), resolve(ir["target"])
        yid = xml_to_yaml.get(ir["xml_id"])
        if yid and yid in rel_nodes:
            node = rel_nodes[yid]
            set_scalar(node, "type", ir["type"], rep, yid)
            set_scalar(node, "source", src, rep, yid)
            set_scalar(node, "target", tgt, rep, yid)
            if ir["type"] == "Access" and ir["accessType"] is not None:
                set_scalar(node, "accessType", ir["accessType"], rep, yid)
            if ir["type"] == "Association" and ir["isDirected"] and not node.get("isDirected"):
                set_scalar(node, "isDirected", True, rep, yid)
            # Influence 'strength' and any other YAML-only keys are never touched.
        else:
            new = CommentedMap()
            new["id"] = ir["xml_id"]; new["type"] = ir["type"]
            new["source"] = src; new["target"] = tgt
            if ir["type"] == "Access" and ir["accessType"]:
                new["accessType"] = ir["accessType"]
            if ir["type"] == "Association" and ir["isDirected"]:
                new["isDirected"] = True
            data.setdefault("relationships", CommentedSeq()).append(new)
            rep.added.append({"kind": "relationship", "id": ir["xml_id"], "type": ir["type"]})

    # ---- propertyDefinitions --------------------------------------------
    for ipd in incoming.property_defs:
        key = pdkey.get(ipd["key"], ipd["key"])
        if key in pdef_nodes:
            node = pdef_nodes[key]
            set_scalar(node, "type", ipd["type"], rep, key)
            # don't re-introduce a synthesized name (emitter writes name=key when absent)
            if ipd["name"] is not None and plain(ipd["name"]) != key:
                update_langfield(node, "name", ipd["name"], rep, key)
        else:
            new = CommentedMap()
            new["key"] = key; new["type"] = ipd["type"]
            if ipd["name"] is not None:
                new["name"] = CommentedMap(ipd["name"]) if isinstance(ipd["name"], dict) else ipd["name"]
            data.setdefault("propertyDefinitions", CommentedSeq()).append(new)
            rep.added.append({"kind": "propertyDefinition", "id": key})

    # ---- views -----------------------------------------------------------
    for iv in incoming.views:
        yid = xml_to_yaml.get(iv["xml_id"])
        els = [resolve(x) for x in iv["element_refs"]]
        rels = [resolve(x) for x in iv["rel_refs"]]
        if yid and yid in view_nodes:
            node = view_nodes[yid]
            update_langfield(node, "name", iv["name"], rep, yid)
            merge_idlist(node, "elements", els, rep, yid)
            merge_idlist(node, "relationships", rels, rep, yid)
        else:
            new = CommentedMap()
            new["id"] = iv["xml_id"]
            if iv["name"] is not None:
                new["name"] = CommentedMap(iv["name"]) if isinstance(iv["name"], dict) else iv["name"]
            new["elements"] = els
            new["relationships"] = rels
            data.setdefault("views", CommentedSeq()).append(new)
            rep.added.append({"kind": "view", "id": iv["xml_id"]})

    # ---- organizations (best-effort, by label) ---------------------------
    if incoming.organizations and "organizations" in data:
        _merge_orgs(data["organizations"], incoming.organizations, resolve, rep)

    # ---- removals (XML-absent existing items) ----------------------------
    incoming_el = {e["xml_id"] for e in incoming.elements}
    incoming_rel = {r["xml_id"] for r in incoming.relationships}
    _handle_removals(data, ymodel, incoming_el, incoming_rel, prune, rep)

    return data, rep, yaml


def _merge_properties(node, incoming_props, prune, rep, ref):
    existing = node.get("properties")
    if not incoming_props:
        return
    if not isinstance(existing, dict):
        node["properties"] = CommentedMap(incoming_props)
        rep.property_changes.append({"id": ref, "added": list(incoming_props)})
        return
    for k, v in incoming_props.items():
        if str(existing.get(k)) != str(v):
            existing[k] = v
            rep.property_changes.append({"id": ref, "key": k, "new": v})
    if prune:
        for k in [k for k in existing if k not in incoming_props]:
            del existing[k]
            rep.property_changes.append({"id": ref, "removed": k})


def _merge_orgs(existing_orgs, incoming_orgs, resolve, rep):
    by_label = {json.dumps(plain(o.get("label")), sort_keys=True): o
                for o in existing_orgs if isinstance(o, dict)}
    for io in incoming_orgs:
        lbl = json.dumps(plain(io["label"]), sort_keys=True)
        items = [resolve(x) for x in io["items"]]
        if lbl in by_label:
            node = by_label[lbl]
            merge_idlist(node, "items", items, rep, f"org:{plain(io['label'])}")
            if io["children"] and "children" in node:
                _merge_orgs(node["children"], io["children"], resolve, rep)


def _handle_removals(data, ymodel, incoming_el, incoming_rel, prune, rep):
    rm_el = [e["id"] for e in ymodel.elements if xml_id(e["id"]) not in incoming_el]
    rm_rel = [r["id"] for r in ymodel.relationships if xml_id(r["id"]) not in incoming_rel]
    for rid in rm_el:
        rep.removed.append({"kind": "element", "id": rid, "pruned": prune})
    for rid in rm_rel:
        rep.removed.append({"kind": "relationship", "id": rid, "pruned": prune})
    if not prune:
        return
    rm_el_set, rm_rel_set = set(rm_el), set(rm_rel)
    # cascade: relationships touching a pruned element are also pruned
    for r in ymodel.relationships:
        if r.get("source") in rm_el_set or r.get("target") in rm_el_set:
            rm_rel_set.add(r["id"])
    data["elements"] = CommentedSeq([e for e in data.get("elements", []) if e.get("id") not in rm_el_set])
    data["relationships"] = CommentedSeq([r for r in data.get("relationships", []) if r.get("id") not in rm_rel_set])
    for v in data.get("views", []):
        if "elements" in v:
            v["elements"] = [x for x in v["elements"] if x not in rm_el_set]
        if "relationships" in v:
            v["relationships"] = [x for x in v["relationships"] if x not in rm_rel_set]
    gone = rm_el_set | rm_rel_set
    for org in data.get("organizations", []):
        _scrub_org(org, gone)


def _scrub_org(org, gone):
    if "items" in org:
        org["items"] = [x for x in org["items"] if x not in gone]
    for c in org.get("children", []):
        _scrub_org(c, gone)


# ---- CLI ------------------------------------------------------------------
def _render_text(rep, path, dry, pruned):
    out = [f"Ingest {'(dry-run) ' if dry else ''}— {path}"]
    for a in rep.added:
        out.append(f"  ADDED      {a['kind']:<12} {a['id']}" + (f"  ({a.get('type')})" if a.get('type') else ""))
    for u in rep.updated:
        out.append(f"  UPDATED    {u['id']}: {u['field']}  {u['old']!r} -> {u['new']!r}")
    for p in rep.property_changes:
        out.append(f"  PROPERTY   {p}")
    for v in rep.view_changes:
        out.append(f"  VIEW       {v['id']}.{v['field']}  +{v['added']} -{v['removed']}")
    for r in rep.removed:
        tag = "PRUNED" if r["pruned"] else "REMOVED?"
        note = "" if r["pruned"] else "  [report-only; use --prune to delete]"
        out.append(f"  {tag:<10} {r['kind']:<12} {r['id']}{note}")
    for w in rep.warnings:
        out.append(f"  WARNING    {w}")
    out.append(f"  Summary: {rep.n_changes()} change(s)"
               + (f", {sum(1 for r in rep.removed if not r['pruned'])} candidate removal(s) not pruned" if not pruned else ""))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Ingest Archi Open Exchange XML back into the YAML model.")
    ap.add_argument("model")
    ap.add_argument("--xml", required=True, help="Open Exchange XML exported from Archi")
    ap.add_argument("--prune", action="store_true", help="delete items absent from the XML (cascades)")
    ap.add_argument("--dry-run", action="store_true", help="report changes, do not write")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--no-validate", action="store_true", help="skip post-write validation")
    args = ap.parse_args(argv)

    mm = load_metamodel()
    data, rep, yaml = ingest(args.model, args.xml, args.prune, mm)

    if args.format == "json":
        print(json.dumps({"model": args.model, "dry_run": args.dry_run, "pruned": args.prune,
                          "changes": rep.to_dict()}, ensure_ascii=False, indent=2))
    else:
        print(_render_text(rep, args.model, args.dry_run, args.prune))

    if args.dry_run:
        return 1 if any(not r["pruned"] for r in rep.removed) else 0

    # Only write when data actually changed — a no-op ingest leaves the file
    # byte-untouched (report-only removals do not mutate the document).
    dirty = bool(rep.added or rep.updated or rep.property_changes or rep.view_changes
                 or any(r["pruned"] for r in rep.removed))
    if not dirty:
        return 1 if any(not r["pruned"] for r in rep.removed) else 0

    with open(args.model, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)

    if not args.no_validate:
        problems = validate(load_model(args.model), mm)
        errs = [p for p in problems if p.severity == ERROR]
        if errs:
            sys.stderr.write(f"WARNING: {len(errs)} validation error(s) after ingest — "
                             "run validate_model.py for details.\n")
            return 2
    return 1 if any(not r["pruned"] for r in rep.removed) else 0


if __name__ == "__main__":
    sys.exit(main())
