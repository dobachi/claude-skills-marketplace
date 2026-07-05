#!/usr/bin/env python3
"""Validate an archimate-ea running-model YAML against the ArchiMate 3.2 metamodel.

Loads the model, runs structural + metamodel checks, and prints a human-readable
(or JSON) problem list designed to drive the facilitation dialogue. ERROR-level
problems block emit; WARN-level do not.

Also exposes load_model() and validate(), imported by the emitters so they share
one parser and refuse to emit an invalid model.

Usage:
    validate_model.py MODEL.yaml [--format text|json] [--strict]

Exit codes: 0 = clean, 1 = warnings only, 2 = errors (or warnings with --strict).
"""

from __future__ import annotations

import argparse
import json
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

from archimate_metamodel import load as load_metamodel

ERROR = "ERROR"
WARN = "WARN"

# NCName-ish: valid xsd:ID lexical form (used verbatim as XML identifier on emit).
_ID_RE = re.compile(r"^[A-Za-z_][\w.\-]*$")

# BCP-47-ish language subtag, used as the key of a multilingual name/documentation
# map. A key that is not a plausible language tag is almost always the artifact of
# a broken YAML flow mapping — e.g. `name: { en: Establish a fair, reliable market }`
# parses to `{en: "Establish a fair", "reliable market": null}` because the unquoted
# comma splits the flow entry. Emitters would then write it verbatim as
# `<name xml:lang="reliable market">None</name>`, so we catch it here instead.
_LANG_RE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")


class Problem:
    __slots__ = ("severity", "code", "ref", "message")

    def __init__(self, severity, code, ref, message):
        self.severity = severity
        self.code = code
        self.ref = ref
        self.message = message

    def as_dict(self):
        return {"severity": self.severity, "code": self.code,
                "ref": self.ref, "message": self.message}


class Model:
    """Parsed running model with id indexes. Shared by validator and emitters."""

    def __init__(self, raw: dict):
        self.raw = raw or {}
        self.header = self.raw.get("model", {}) or {}
        self.property_defs = self.raw.get("propertyDefinitions", []) or []
        self.elements = self.raw.get("elements", []) or []
        self.relationships = self.raw.get("relationships", []) or []
        self.organizations = self.raw.get("organizations", []) or []
        self.views = self.raw.get("views", []) or []
        self.element_by_id = {e.get("id"): e for e in self.elements if isinstance(e, dict)}
        self.rel_by_id = {r.get("id"): r for r in self.relationships if isinstance(r, dict)}
        self.property_keys = {p.get("key") for p in self.property_defs if isinstance(p, dict)}


def load_model(path: str) -> Model:
    with open(path, encoding="utf-8") as fh:
        return Model(yaml.safe_load(fh))


def _truthy_bool(v) -> bool:
    return isinstance(v, bool)


def _check_langmap(P, kind, ref, field, value):
    """Flag a multilingual name/documentation/label map whose keys are not plausible
    language tags, or whose values are null/empty. Both are the tell-tale signature of
    a YAML flow mapping split by an unquoted comma or colon inside the text."""
    if not isinstance(value, dict):
        return  # plain string (or absent) — nothing to check
    for lang, text in value.items():
        if not isinstance(lang, str) or not _LANG_RE.match(lang):
            P(ERROR, "bad-lang-key", ref,
              f"{kind} '{ref}' {field} has key {lang!r}, which is not a language code. "
              "This usually means an unquoted comma/colon split a YAML flow mapping "
              f"(e.g. `{field}: {{ en: A, B }}` parses as two keys); quote the text "
              "(`en: \"A, B\"`) or write the map in block style.")
        if text is None or (isinstance(text, str) and not text.strip()):
            P(ERROR, "empty-lang-text", ref,
              f"{kind} '{ref}' {field}[{lang!r}] has no text; a split flow mapping "
              "often leaves the tail key with a null value. Check the source line for "
              "an unquoted comma or colon.")


def validate(model: Model, mm) -> list[Problem]:
    problems: list[Problem] = []
    P = lambda *a: problems.append(Problem(*a))

    # ---- 1. structure & id uniqueness ------------------------------------
    if not model.header.get("id"):
        P(ERROR, "missing-key", "model", "model.id is required (becomes the XML model identifier).")

    seen_ids: dict[str, str] = {}
    def register(kind, oid):
        if oid is None:
            P(ERROR, "missing-key", kind, f"{kind} entry is missing an 'id'.")
            return
        if oid in seen_ids:
            P(ERROR, "duplicate-id", oid,
              f"id '{oid}' is used by both a {seen_ids[oid]} and a {kind}; ids must be unique.")
        else:
            seen_ids[oid] = kind
            if not _ID_RE.match(str(oid)):
                P(WARN, "bad-id", oid,
                  f"id '{oid}' is not a valid XML identifier (letter/underscore start, "
                  "then letters/digits/.-_); it will be sanitized on XML emit.")

    for e in model.elements:
        if not isinstance(e, dict):
            P(ERROR, "shape", "elements", f"element entry is not a mapping: {e!r}")
            continue
        register("element", e.get("id"))
    for r in model.relationships:
        if not isinstance(r, dict):
            P(ERROR, "shape", "relationships", f"relationship entry is not a mapping: {r!r}")
            continue
        register("relationship", r.get("id"))
    for v in model.views:
        if isinstance(v, dict):
            register("view", v.get("id"))

    # ---- 1b. multilingual name/documentation/label maps -----------------
    # Catch flow-mapping corruption (unquoted comma/colon) before it reaches emit.
    _check_langmap(P, "model", model.header.get("id", "model"), "name", model.header.get("name"))
    _check_langmap(P, "model", model.header.get("id", "model"), "documentation", model.header.get("documentation"))
    for e in model.elements:
        if isinstance(e, dict):
            _check_langmap(P, "element", e.get("id"), "name", e.get("name"))
            _check_langmap(P, "element", e.get("id"), "documentation", e.get("documentation"))
    for pd in model.property_defs:
        if isinstance(pd, dict):
            _check_langmap(P, "propertyDefinition", pd.get("key"), "name", pd.get("name"))
    for v in model.views:
        if isinstance(v, dict):
            _check_langmap(P, "view", v.get("id"), "name", v.get("name"))
    def _walk_org_labels(org):
        if not isinstance(org, dict):
            return
        _check_langmap(P, "organization", org.get("label"), "label", org.get("label"))
        for child in org.get("children", []) or []:
            _walk_org_labels(child)
    for org in model.organizations:
        _walk_org_labels(org)

    # ---- 2/6. elements: type + modifiers + properties --------------------
    for e in model.elements:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        etype = e.get("type")
        if not mm.is_element_type(etype):
            P(ERROR, "unknown-type", eid,
              f"element '{eid}' has unknown type '{etype}'. Not an ArchiMate 3.2 element.")
        if etype == "Junction":
            jt = e.get("junctionType", "or")
            if jt not in mm.modifiers["junctionType"]:
                P(ERROR, "bad-modifier", eid,
                  f"junction '{eid}' junctionType '{jt}' must be one of {mm.modifiers['junctionType']}.")
        elif "junctionType" in e:
            P(WARN, "bad-modifier", eid, f"junctionType on non-Junction element '{eid}' is ignored.")
        for key in (e.get("properties") or {}):
            if key not in model.property_keys:
                P(WARN, "undeclared-property", eid,
                  f"property '{key}' on '{eid}' is not declared in propertyDefinitions; "
                  "add a definition (XML requires declare-before-use).")

    # ---- 3/4/5. relationships: type, endpoints, legality, modifiers ------
    junction_edges: dict[str, list[tuple[str, str]]] = {}  # junction id -> [(relId, relType)]
    for r in model.relationships:
        if not isinstance(r, dict):
            continue
        rid = r.get("id")
        rtype = r.get("type")
        src = r.get("source")
        dst = r.get("target")
        known_rel = mm.is_relationship_type(rtype)
        if not known_rel:
            P(ERROR, "unknown-relationship", rid,
              f"relationship '{rid}' has unknown type '{rtype}'.")
        src_e = model.element_by_id.get(src)
        dst_e = model.element_by_id.get(dst)
        if src_e is None:
            P(ERROR, "dangling-source", rid,
              f"relationship '{rid}' source '{src}' is not a defined element.")
        if dst_e is None:
            P(ERROR, "dangling-target", rid,
              f"relationship '{rid}' target '{dst}' is not a defined element.")

        # track junction incidence
        if src_e is not None and src_e.get("type") == "Junction":
            junction_edges.setdefault(src, []).append((rid, rtype))
        if dst_e is not None and dst_e.get("type") == "Junction":
            junction_edges.setdefault(dst, []).append((rid, rtype))

        # legality (only when both endpoints + types are known)
        if known_rel and src_e is not None and dst_e is not None:
            st, dt = src_e.get("type"), dst_e.get("type")
            if mm.is_element_type(st) and mm.is_element_type(dt):
                if not mm.relationship_allowed(rtype, st, dt):
                    allowed = mm.allowed_relationships(st, dt) or ["Association"]
                    P(ERROR, "illegal-relationship", rid,
                      f"{rtype} from {st}({src}) to {dt}({dst}) is not allowed. "
                      f"{st}→{dt} permits: {', '.join(allowed)}.")

        # modifier placement / values
        if "accessType" in r:
            if rtype != "Access":
                P(WARN, "bad-modifier", rid, f"accessType on non-Access relationship '{rid}' is ignored.")
            elif r["accessType"] not in mm.modifiers["accessType"]:
                P(ERROR, "bad-modifier", rid,
                  f"accessType '{r['accessType']}' on '{rid}' must be one of {mm.modifiers['accessType']}.")
        if "isDirected" in r:
            if rtype != "Association":
                P(WARN, "bad-modifier", rid, f"isDirected on non-Association relationship '{rid}' is ignored.")
            elif not _truthy_bool(r["isDirected"]):
                P(ERROR, "bad-modifier", rid, f"isDirected on '{rid}' must be a boolean.")
        if "strength" in r and rtype != "Influence":
            P(WARN, "bad-modifier", rid, f"strength on non-Influence relationship '{rid}' is ignored.")

    # ---- junction consistency: incident edges must share one rel type ----
    for jid, edges in junction_edges.items():
        types = {t for _, t in edges}
        if len(types) > 1:
            P(ERROR, "junction-inconsistent", jid,
              f"junction '{jid}' joins relationships of differing types {sorted(types)}; "
              "all edges through a junction must be the same relationship type.")

    # ---- 8. views -------------------------------------------------------
    for v in model.views:
        if not isinstance(v, dict):
            continue
        vid = v.get("id")
        members = set(v.get("elements", []) or [])
        for ref in v.get("elements", []) or []:
            if ref not in model.element_by_id:
                P(ERROR, "view-bad-ref", vid, f"view '{vid}' lists element '{ref}' which does not exist.")
        for ref in v.get("relationships", []) or []:
            r = model.rel_by_id.get(ref)
            if r is None:
                P(ERROR, "view-bad-ref", vid, f"view '{vid}' lists relationship '{ref}' which does not exist.")
                continue
            for endpoint in (r.get("source"), r.get("target")):
                if endpoint not in members:
                    P(WARN, "view-dangling-edge", vid,
                      f"view '{vid}': relationship '{ref}' endpoint '{endpoint}' is not in the view's elements; "
                      "the connection would dangle.")

    # ---- 9. organizations ------------------------------------------------
    def walk_org(org):
        for ref in org.get("items", []) or []:
            if ref not in model.element_by_id and ref not in model.rel_by_id:
                P(WARN, "org-bad-ref", org.get("label"), f"organization item '{ref}' does not exist.")
        for child in org.get("children", []) or []:
            walk_org(child)
    for org in model.organizations:
        if isinstance(org, dict):
            walk_org(org)

    return problems


# --------------------------------------------------------------------------
def _render_text(problems, path):
    lines = [f"{path} — validation ({load_metamodel().spec})"]
    if not problems:
        lines.append("  clean — no problems found.")
    order = {ERROR: 0, WARN: 1}
    for p in sorted(problems, key=lambda x: order.get(x.severity, 9)):
        lines.append(f"  {p.severity:<5} [{p.code}]  {p.ref}: {p.message}")
    n_err = sum(1 for p in problems if p.severity == ERROR)
    n_warn = sum(1 for p in problems if p.severity == WARN)
    lines.append(f"  Summary: {n_err} error(s), {n_warn} warning(s)."
                 + ("  Emit blocked until errors resolved." if n_err else ""))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate an archimate-ea running model.")
    ap.add_argument("model", help="path to the running-model YAML")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args(argv)

    mm = load_metamodel()
    model = load_model(args.model)
    problems = validate(model, mm)

    n_err = sum(1 for p in problems if p.severity == ERROR)
    n_warn = sum(1 for p in problems if p.severity == WARN)

    if args.format == "json":
        print(json.dumps({"model": args.model,
                          "errors": n_err, "warnings": n_warn,
                          "problems": [p.as_dict() for p in problems]},
                         ensure_ascii=False, indent=2))
    else:
        print(_render_text(problems, args.model))

    if n_err:
        return 2
    if n_warn:
        return 2 if args.strict else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
