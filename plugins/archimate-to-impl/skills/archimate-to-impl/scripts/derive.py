#!/usr/bin/env python3
"""Derive implementation scaffolding from an ArchiMate EA model's Application layer.

Generate-forward: reads ea-model.yaml (read-only) and writes, under an output dir,
  out/traceability.yaml   requirement -> component -> service -> api -> task graph
  out/traceability.md     the same, human-readable, with orphan markers
  out/openapi/<svc>.yaml   an OpenAPI 3.0 skeleton per ApplicationService
  out/entities/<obj>.yaml  an entity stub per DataObject
  out/tasks.md             a per-component implementation task list (recommended skill)

These are disposable downstream artifacts — never hand-edit ea-model.yaml here; edit
the model in archimate-ea and re-derive. Orphans are reported by trace_check.py.

Traversal rules (see references/traceability-schema.md):
  service  -Realization-> requirement        (service realizes requirement)
  function -Realization-> service            (function realizes service)
  component-Assignment-> function            (component runs function)
  component-Assignment-> interface           (component exposes interface)
  function -Access->      dataobject         (function reads/writes data)
  component-Association-> service            (component uses/depends on service)

Usage:
    derive.py MODEL.yaml -o out/
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

from ea_read import (APP_COMPONENT, APP_FUNCTION, APP_SERVICE, APP_INTERFACE,
                     DATA_OBJECT, REQ_TYPES, load, camel, kebab)


def build_graph(m) -> dict:
    services, components, requirements, dataobjects = [], [], [], []

    # --- services -------------------------------------------------------
    for svc in m.of_type(APP_SERVICE):
        sid = svc["id"]
        reqs = [r["target"] for r in m.rels(type="Realization", source=sid)
                if m.is_type(r["target"], *REQ_TYPES)]
        funcs = [r["source"] for r in m.rels(type="Realization", target=sid)
                 if m.is_type(r["source"], APP_FUNCTION)]
        comps = set()
        for f in funcs:  # component -Assignment-> function -Realization-> service
            comps.update(r["source"] for r in m.rels(type="Assignment", target=f)
                         if m.is_type(r["source"], APP_COMPONENT))
        # component -Association-> service (directed use/dependency)
        users = [r["source"] for r in m.rels(type="Association", target=sid)
                 if m.is_type(r["source"], APP_COMPONENT)]
        ifaces = []
        for c in comps:
            ifaces.extend(r["target"] for r in m.rels(type="Assignment", source=c)
                          if m.is_type(r["target"], APP_INTERFACE))
        data = []
        for f in funcs:
            for r in m.rels(type="Access", source=f):
                if m.is_type(r["target"], DATA_OBJECT):
                    data.append({"id": r["target"], "access": r.get("accessType", "readWrite")})
        services.append({
            "id": sid, "name": m.name(sid),
            "realizes_requirements": reqs,
            "implemented_by_functions": funcs,
            "components": sorted(comps),
            "used_by_components": users,
            "interfaces": sorted(set(ifaces)),
            "data": data,
            "api_skeleton": f"openapi/{sid}.yaml",
        })

    # --- components -----------------------------------------------------
    for comp in m.of_type(APP_COMPONENT):
        cid = comp["id"]
        funcs = [r["target"] for r in m.rels(type="Assignment", source=cid)
                 if m.is_type(r["target"], APP_FUNCTION)]
        ifaces = [r["target"] for r in m.rels(type="Assignment", source=cid)
                  if m.is_type(r["target"], APP_INTERFACE)]
        svcs = set()
        for f in funcs:
            svcs.update(r["target"] for r in m.rels(type="Realization", source=f)
                        if m.is_type(r["target"], APP_SERVICE))
        # services this component uses (directed association)
        svcs.update(r["target"] for r in m.rels(type="Association", source=cid)
                    if m.is_type(r["target"], APP_SERVICE))
        reqs = set()
        for s in svcs:
            reqs.update(r["target"] for r in m.rels(type="Realization", source=s)
                        if m.is_type(r["target"], *REQ_TYPES))
        data = []
        for f in funcs:
            for r in m.rels(type="Access", source=f):
                if m.is_type(r["target"], DATA_OBJECT):
                    data.append({"id": r["target"], "access": r.get("accessType", "readWrite")})
        # A component that exposes a service or an interface is an API surface.
        exposes_api = bool(svcs) or bool(ifaces)
        skill = "web-api-dev" if exposes_api else "python-expert"
        components.append({
            "id": cid, "name": m.name(cid),
            "functions": funcs, "interfaces": ifaces,
            "services": sorted(svcs),
            "traces_to_requirements": sorted(reqs),
            "data": data,
            "task": {
                "id": f"TASK-{cid}",
                "title": f"Implement {m.name(cid)}",
                "recommended_skill": skill,
            },
        })

    # --- requirements (coverage) ---------------------------------------
    covered = set()
    for svc in services:
        covered.update(svc["realizes_requirements"])
    for e in m.of_type(*REQ_TYPES):
        rid = e["id"]
        realizers = [s["id"] for s in services if rid in s["realizes_requirements"]]
        requirements.append({
            "id": rid, "type": m.type_of(rid), "name": m.name(rid),
            "realized_by_services": realizers,
            "covered": rid in covered,
        })

    # --- data objects (entity stubs) -----------------------------------
    for obj in m.of_type(DATA_OBJECT):
        oid = obj["id"]
        accessors = []
        for r in m.rels(type="Access", target=oid):
            if m.is_type(r["source"], APP_FUNCTION):
                accessors.append({"function": r["source"], "access": r.get("accessType", "readWrite")})
        dataobjects.append({
            "id": oid, "name": m.name(oid),
            "entity": camel(m.name(oid), oid),
            "accessed_by": accessors,
        })

    return {"requirements": requirements, "services": services,
            "components": components, "dataobjects": dataobjects}


# --- emitters -------------------------------------------------------------

_ACCESS_METHODS = {
    "read": ["get_collection", "get_item"],
    "write": ["post", "put"],
    "readWrite": ["get_collection", "get_item", "post", "put", "delete"],
    "none": [],
}


def openapi_skeleton(m, svc: dict, graph: dict) -> dict:
    paths: dict = {}
    schemas: dict = {}
    entity_by_id = {d["id"]: d for d in graph["dataobjects"]}
    for d in svc["data"]:
        obj = entity_by_id.get(d["id"])
        if not obj:
            continue
        ent = obj["entity"]
        seg = kebab(obj["name"], obj["id"])
        schemas.setdefault(ent, {
            "type": "object",
            "description": f"Stub from DataObject {obj['id']} — fill in fields.",
            "properties": {"id": {"type": "string"}},
        })
        methods = _ACCESS_METHODS.get(d["access"], _ACCESS_METHODS["readWrite"])
        coll, item = f"/{seg}", f"/{seg}/{{id}}"
        # Fresh dict per use so yaml.safe_dump does not emit anchors/aliases.
        def ref():
            return {"$ref": f"#/components/schemas/{ent}"}

        def id_param():
            return [{"name": "id", "in": "path", "required": True,
                     "schema": {"type": "string"}}]
        if "get_collection" in methods:
            paths.setdefault(coll, {})["get"] = {
                "summary": f"List {ent}", "responses": {"200": {
                    "description": "OK", "content": {"application/json": {
                        "schema": {"type": "array", "items": ref()}}}}}}
        if "post" in methods:
            paths.setdefault(coll, {})["post"] = {
                "summary": f"Create {ent}",
                "requestBody": {"content": {"application/json": {"schema": ref()}}},
                "responses": {"201": {"description": "Created"}}}
        if "get_item" in methods:
            paths.setdefault(item, {})["get"] = {
                "summary": f"Get {ent}",
                "parameters": id_param(),
                "responses": {"200": {"description": "OK", "content": {
                    "application/json": {"schema": ref()}}}, "404": {"description": "Not found"}}}
        if "put" in methods:
            paths.setdefault(item, {})["put"] = {
                "summary": f"Replace {ent}",
                "parameters": id_param(),
                "requestBody": {"content": {"application/json": {"schema": ref()}}},
                "responses": {"200": {"description": "OK"}}}
        if "delete" in methods:
            paths.setdefault(item, {})["delete"] = {
                "summary": f"Delete {ent}",
                "parameters": id_param(),
                "responses": {"204": {"description": "Deleted"}}}
    if not paths:  # service accesses no data — leave a single placeholder path
        paths["/todo"] = {"get": {"summary": "TODO: define operations",
                                  "responses": {"200": {"description": "OK"}}}}
    reqs = ", ".join(svc["realizes_requirements"]) or "(none — orphan service)"
    return {
        "openapi": "3.0.3",
        "info": {
            "title": svc["name"], "version": "0.1.0",
            "description": (f"Skeleton generated from ApplicationService {svc['id']}. "
                            f"Realizes requirements: {reqs}. Flesh out with web-api-dev."),
        },
        "paths": paths,
        "components": {"schemas": schemas} if schemas else {},
    }


def entity_stub(obj: dict) -> dict:
    return {
        "entity": obj["entity"],
        "source_dataobject": obj["id"],
        "fields": {"id": {"type": "string", "required": True}},
        "accessed_by": obj["accessed_by"],
        "note": "Stub — derive fields from the domain; keep source_dataobject stable.",
    }


def render_md(graph: dict) -> str:
    out = ["# Traceability: requirement → component → service → api → task\n"]

    out.append("## Requirement coverage\n")
    out.append("| Requirement | Type | Realized by services | Covered |")
    out.append("|---|---|---|---|")
    for r in graph["requirements"]:
        svcs = ", ".join(f"`{s}`" for s in r["realized_by_services"]) or "—"
        mark = "✅" if r["covered"] else "❌ ORPHAN"
        out.append(f"| {r['name']} (`{r['id']}`) | {r['type']} | {svcs} | {mark} |")

    out.append("\n## Services → API\n")
    out.append("| Service | Realizes | Components | Interfaces | Data (access) | API skeleton |")
    out.append("|---|---|---|---|---|---|")
    for s in graph["services"]:
        reqs = ", ".join(f"`{x}`" for x in s["realizes_requirements"]) or "— ORPHAN"
        comps = ", ".join(f"`{x}`" for x in s["components"]) or "— no impl"
        ifs = ", ".join(f"`{x}`" for x in s["interfaces"]) or "—"
        data = ", ".join(f"`{d['id']}`({d['access']})" for d in s["data"]) or "—"
        out.append(f"| {s['name']} (`{s['id']}`) | {reqs} | {comps} | {ifs} | {data} | `{s['api_skeleton']}` |")

    out.append("\n## Components → tasks\n")
    out.append("| Component | Task | Skill | Traces to requirements | Services |")
    out.append("|---|---|---|---|---|")
    for c in graph["components"]:
        reqs = ", ".join(f"`{x}`" for x in c["traces_to_requirements"]) or "— ORPHAN"
        svcs = ", ".join(f"`{x}`" for x in c["services"]) or "—"
        out.append(f"| {c['name']} (`{c['id']}`) | {c['task']['title']} | "
                   f"{c['task']['recommended_skill']} | {reqs} | {svcs} |")
    return "\n".join(out) + "\n"


def render_tasks_md(graph: dict) -> str:
    out = ["# Implementation tasks (per component)\n"]
    for c in graph["components"]:
        out.append(f"## {c['task']['id']}: {c['task']['title']}")
        out.append(f"- Recommended skill: **{c['task']['recommended_skill']}**")
        out.append(f"- Component: `{c['id']}`")
        out.append(f"- Traces to requirements: "
                   + (", ".join(f"`{x}`" for x in c["traces_to_requirements"]) or "⚠️ none (orphan)"))
        out.append(f"- Services to expose: "
                   + (", ".join(f"`{x}`" for x in c["services"]) or "—"))
        if c["data"]:
            out.append("- Data: " + ", ".join(f"`{d['id']}`({d['access']})" for d in c["data"]))
        out.append("")
    return "\n".join(out) + "\n"


def _dump(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)


def main():
    ap = argparse.ArgumentParser(description="Derive implementation scaffolding from an EA model.")
    ap.add_argument("model", help="path to ea-model.yaml")
    ap.add_argument("-o", "--out", default="out", help="output directory (default: out/)")
    args = ap.parse_args()

    m = load(args.model)
    graph = build_graph(m)

    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "openapi"), exist_ok=True)
    os.makedirs(os.path.join(args.out, "entities"), exist_ok=True)

    _dump(os.path.join(args.out, "traceability.yaml"), graph)
    with open(os.path.join(args.out, "traceability.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(graph))
    with open(os.path.join(args.out, "tasks.md"), "w", encoding="utf-8") as fh:
        fh.write(render_tasks_md(graph))
    for svc in graph["services"]:
        _dump(os.path.join(args.out, "openapi", f"{svc['id']}.yaml"),
              openapi_skeleton(m, svc, graph))
    for obj in graph["dataobjects"]:
        _dump(os.path.join(args.out, "entities", f"{obj['id']}.yaml"), entity_stub(obj))

    n_orphan_req = sum(1 for r in graph["requirements"] if not r["covered"])
    print(f"derived: {len(graph['services'])} service(s), {len(graph['components'])} component(s), "
          f"{len(graph['dataobjects'])} data object(s) -> {args.out}/")
    print(f"  traceability.yaml / traceability.md / tasks.md / openapi/ / entities/")
    if n_orphan_req:
        print(f"  note: {n_orphan_req} requirement(s) not covered — run trace_check.py for details")


if __name__ == "__main__":
    main()
