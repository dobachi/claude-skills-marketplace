#!/usr/bin/env python3
"""Check an ArchiMate EA model for implementation-traceability orphans.

Surfaces the gaps that break the requirement -> component -> service -> api -> task
chain, as a problem list styled after archimate-ea's validate_model.py:

  unimplemented-requirement  a Requirement/Constraint no ApplicationService realizes
  service-no-requirement     an ApplicationService realizing no requirement
  service-no-impl            an ApplicationService no function/component implements
  component-no-requirement   an ApplicationComponent tracing to no requirement
  service-no-interface       an ApplicationService whose components expose no interface

All are WARN by default (the model is still valid ArchiMate — these are coverage
gaps, not metamodel errors). --strict promotes any warning to a failing exit.

Usage:
    trace_check.py MODEL.yaml [--format text|json] [--strict]

Exit codes: 0 = clean, 1 = warnings, 2 = warnings with --strict.
"""

from __future__ import annotations

import argparse
import json
import sys

from ea_read import (APP_COMPONENT, APP_FUNCTION, APP_SERVICE, APP_INTERFACE,
                     REQ_TYPES, load)

WARN = "WARN"


class Problem:
    __slots__ = ("severity", "code", "ref", "message")

    def __init__(self, severity, code, ref, message):
        self.severity, self.code, self.ref, self.message = severity, code, ref, message

    def as_dict(self):
        return {"severity": self.severity, "code": self.code,
                "ref": self.ref, "message": self.message}


def check(m) -> list:
    problems = []
    P = lambda *a: problems.append(Problem(WARN, *a))

    services = m.of_type(APP_SERVICE)
    service_ids = {s["id"] for s in services}

    # Which requirements does some ApplicationService realize?
    realized_reqs = set()
    for s in services:
        for r in m.rels(type="Realization", source=s["id"]):
            if m.is_type(r["target"], *REQ_TYPES):
                realized_reqs.add(r["target"])

    # unimplemented-requirement
    for e in m.of_type(*REQ_TYPES):
        if e["id"] not in realized_reqs:
            P("unimplemented-requirement", e["id"],
              f"{m.type_of(e['id'])} '{m.name(e['id'])}' is realized by no ApplicationService "
              f"— no implementation traces to it.")

    # per-service checks
    for s in services:
        sid = s["id"]
        reqs = [r for r in m.rels(type="Realization", source=sid)
                if m.is_type(r["target"], *REQ_TYPES)]
        if not reqs:
            P("service-no-requirement", sid,
              f"ApplicationService '{m.name(sid)}' realizes no Requirement/Constraint "
              f"— it may be dead weight or a missing Realization edge.")
        funcs = [r["source"] for r in m.rels(type="Realization", target=sid)
                 if m.is_type(r["source"], APP_FUNCTION)]
        comps = set()
        for f in funcs:
            comps.update(r["source"] for r in m.rels(type="Assignment", target=f)
                         if m.is_type(r["source"], APP_COMPONENT))
        if not funcs and not comps:
            P("service-no-impl", sid,
              f"ApplicationService '{m.name(sid)}' has no realizing ApplicationFunction "
              f"or ApplicationComponent — nothing implements it.")
        ifaces = []
        for c in comps:
            ifaces.extend(r["target"] for r in m.rels(type="Assignment", source=c)
                          if m.is_type(r["target"], APP_INTERFACE))
        if comps and not ifaces:
            P("service-no-interface", sid,
              f"ApplicationService '{m.name(sid)}' is implemented but its component(s) expose "
              f"no ApplicationInterface — the protocol boundary is undefined.")

    # per-component checks
    for c in m.of_type(APP_COMPONENT):
        cid = c["id"]
        funcs = [r["target"] for r in m.rels(type="Assignment", source=cid)
                 if m.is_type(r["target"], APP_FUNCTION)]
        svcs = set()
        for f in funcs:
            svcs.update(r["target"] for r in m.rels(type="Realization", source=f)
                        if m.is_type(r["target"], APP_SERVICE))
        svcs.update(r["target"] for r in m.rels(type="Association", source=cid)
                    if m.is_type(r["target"], APP_SERVICE))
        reqs = set()
        for s in svcs:
            reqs.update(r["target"] for r in m.rels(type="Realization", source=s)
                        if m.is_type(r["target"], *REQ_TYPES))
        if not reqs:
            P("component-no-requirement", cid,
              f"ApplicationComponent '{m.name(cid)}' traces to no Requirement/Constraint "
              f"— it implements nothing the model asks for.")
    return problems


def main():
    ap = argparse.ArgumentParser(description="Check EA model for traceability orphans.")
    ap.add_argument("model", help="path to ea-model.yaml")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on warnings")
    args = ap.parse_args()

    m = load(args.model)
    problems = check(m)

    if args.format == "json":
        print(json.dumps({"problems": [p.as_dict() for p in problems],
                          "summary": {"warnings": len(problems)}},
                         ensure_ascii=False, indent=2))
    else:
        print(f"{args.model} — traceability check (archimate-to-impl)")
        if not problems:
            print("  clean — every requirement traces to an implementation.")
        else:
            for p in problems:
                print(f"  [{p.severity}] {p.code}: {p.ref}\n      {p.message}")
            print(f"  Summary: {len(problems)} warning(s).")

    if problems and args.strict:
        sys.exit(2)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
