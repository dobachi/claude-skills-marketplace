#!/usr/bin/env python3
"""Cross-layer trace-coverage analysis for an archimate-ea running model.

Where validate_model.py checks *legality* (is this relationship allowed?), this
checks *completeness of the forward trace* — does each upper-layer intent actually
reach a carrier in the layer below? It operationalizes the per-layer Definition of
Done from references/elicitation-playbook.md, which until now lived only in prose.

Two outputs, matching the two ways staged design drops upstream content:

  1. Coverage gaps  — an upper element with NO downstream carrier of the kind its
     DoD requires (a Requirement nothing realizes, an ApplicationComponent no
     technology hosts). This is the "取りこぼし / dropped" failure.

  2. Reach matrix   — per Goal root, how many elements in each lower layer trace
     back to it. Zeros and outliers expose the "偏り / skew" failure, where the
     technology layer clusters on some branches and starves others.

A rule only fires once its counterpart layer is *in play* (has ≥1 element), so the
tool is safe to run at every CHECKPOINT during a staged descent: it checks the
transitions you have reached, not the ones you have not started.

Usage:
    trace_coverage.py MODEL.yaml [--format text|json]

Exit codes: 0 = full coverage, 1 = gaps or empty-layer roots found.
"""

from __future__ import annotations

import argparse
import json
import sys

try:
    import yaml  # noqa: F401  (imported for the shared loader's benefit / clear error)
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

from archimate_metamodel import load as load_metamodel
from validate_model import load_model

# Ordered active layers, motivation (intent) at the top descending to realization.
# composite / connector (junctions) are pass-through — no rank.
LAYER_RANK = {
    "motivation": 0, "strategy": 1, "business": 2,
    "application": 3, "technology": 4, "physical": 5, "implementation": 6,
}
# Downstream columns shown in the reach matrix (motivation is the row source itself).
MATRIX_LAYERS = ["strategy", "business", "application", "technology",
                 "physical", "implementation"]

# Relationships that carry intent down the stack (Association excluded — too generic,
# it would over-connect the reach graph and hide skew).
CARRY_RELS = {"Realization", "Serving", "Assignment", "Aggregation",
              "Composition", "Access", "Triggering", "Flow", "Influence"}

# --- Definition-of-Done rules, one per forward-trace obligation ----------------
# subject : element types this rule constrains
# needs   : list of link-specs; the rule is satisfied if ANY need is met
#           dir "in"  = an edge whose TARGET is the subject (something points at it)
#           dir "out" = an edge whose SOURCE is the subject
#           cp_types / cp_layers = what the counterpart must be
# gate    : set of layers whose presence makes the rule relevant, or None = always.
#           A rule stays silent until its downstream layer is in play.
RULES = [
    {"id": "goal-refined", "subject": {"Goal"}, "gate": None,
     "needs": [{"rel": {"Realization", "Aggregation"}, "dir": "in",
                "cp_types": {"Requirement", "Outcome"}}],
     "msg": "Goal is refined into no Requirement or Outcome — its intent has no carrier."},

    {"id": "req-carried", "subject": {"Requirement"},
     "gate": {"strategy", "business", "application", "technology"},
     "needs": [{"rel": {"Realization"}, "dir": "in",
                "cp_layers": {"strategy", "business", "application", "technology"}}],
     "msg": "Requirement is realized by no downstream element — the intent stops at motivation."},

    {"id": "bizsvc-purpose", "subject": {"BusinessService"}, "gate": None,
     "needs": [{"rel": {"Realization"}, "dir": "out", "cp_types": {"Requirement"}},
               {"rel": {"Serving", "Realization", "Assignment"}, "dir": "out",
                "cp_types": {"Capability"}}],
     "msg": "BusinessService neither realizes a Requirement nor supports a Capability — no traceable purpose."},

    {"id": "bizsvc-realized", "subject": {"BusinessService"}, "gate": None,
     "needs": [{"rel": {"Realization", "Assignment"}, "dir": "in",
                "cp_types": {"BusinessProcess", "BusinessFunction", "BusinessInteraction"}}],
     "msg": "BusinessService is realized by no BusinessProcess/Function — nothing performs it."},

    {"id": "appsvc-anchor", "subject": {"ApplicationService"}, "gate": None,
     "needs": [{"rel": {"Serving"}, "dir": "out", "cp_layers": {"business"}},
               {"rel": {"Realization"}, "dir": "out", "cp_types": {"Requirement"}}],
     "msg": "ApplicationService serves no business behavior and realizes no Requirement — no upstream anchor."},

    {"id": "appcomp-hosted", "subject": {"ApplicationComponent"}, "gate": {"technology"},
     "needs": [{"rel": {"Realization", "Serving", "Assignment"}, "dir": "in",
                "cp_layers": {"technology"}}],
     "msg": "ApplicationComponent is realized/served by no technology element — deployment is undefined."},
]


def _label(el: dict) -> str:
    name = el.get("name")
    if isinstance(name, dict):
        for lang in ("en", "ja"):
            if name.get(lang):
                return str(name[lang])
        if name:
            return str(next(iter(name.values())))
    elif isinstance(name, str) and name.strip():
        return name
    return el.get("id", "?")


def _build_incidence(model):
    """id -> list of (direction, other_id, rel_type); direction is 'out' if the id is
    the source of the edge, 'in' if it is the target."""
    inc: dict[str, list[tuple[str, str, str]]] = {}
    for r in model.relationships:
        if not isinstance(r, dict):
            continue
        s, d, t = r.get("source"), r.get("target"), r.get("type")
        if s is None or d is None:
            continue  # dangling — validate_model.py reports it; ignore here
        inc.setdefault(s, []).append(("out", d, t))
        inc.setdefault(d, []).append(("in", s, t))
    return inc


def _counterparts(eid, rels, direction, inc, elem_by_id, seen):
    """Counterpart elements reached from `eid` over `rels` in `direction`, transparently
    passing THROUGH junctions (a junction AND/ORs edges of one relationship type, so the
    real counterpart is one hop past it)."""
    out = []
    for d, other, rtype in inc.get(eid, []):
        if rtype not in rels or (direction != "any" and d != direction):
            continue
        oe = elem_by_id.get(other)
        if oe is None:
            continue
        if oe.get("type") == "Junction":
            if other not in seen:
                seen.add(other)
                out += _counterparts(other, rels, direction, inc, elem_by_id, seen)
        else:
            out.append(oe)
    return out


def _need_met(eid, need, inc, elem_by_id, mm):
    cps = _counterparts(eid, need["rel"], need["dir"], inc, elem_by_id, set())
    for oe in cps:
        ot = oe.get("type")
        if "cp_types" in need and ot not in need["cp_types"]:
            continue
        if "cp_layers" in need and mm.layer_of(ot) not in need["cp_layers"]:
            continue
        return True
    return False


def find_gaps(model, mm, inc, layers_in_play):
    gaps = []
    for e in model.elements:
        if not isinstance(e, dict):
            continue
        etype = e.get("type")
        for rule in RULES:
            if etype not in rule["subject"]:
                continue
            if rule["gate"] is not None and not (rule["gate"] & layers_in_play):
                continue  # downstream layer not started yet
            if not any(_need_met(e.get("id"), n, inc, elem_by_id=model.element_by_id, mm=mm)
                       for n in rule["needs"]):
                gaps.append({"rule": rule["id"], "id": e.get("id"),
                             "label": _label(e), "type": etype, "message": rule["msg"]})
    return gaps


def _can_step(u_type, v_type, mm):
    """Downward/lateral step for reach traversal: allow moving to a same-or-lower layer.
    Junctions/composite (no rank) are pass-through in both directions."""
    ru = LAYER_RANK.get(mm.layer_of(u_type))
    rv = LAYER_RANK.get(mm.layer_of(v_type))
    if ru is None or rv is None:
        return True
    return rv >= ru


def reach_matrix(model, mm, inc):
    """For each Goal, BFS downward over carrying relationships; tally reached elements
    per layer. Returns (rows, active_cols)."""
    elem_by_id = model.element_by_id
    goals = [e for e in model.elements
             if isinstance(e, dict) and e.get("type") == "Goal"]
    rows = []
    for g in goals:
        gid = g.get("id")
        visited = {gid}
        frontier = [gid]
        per_layer: dict[str, int] = {}
        while frontier:
            nxt = []
            for u in frontier:
                ut = elem_by_id.get(u, {}).get("type")
                for _, other, rtype in inc.get(u, []):
                    if other in visited or other not in elem_by_id:
                        continue
                    ov = elem_by_id[other]
                    ot = ov.get("type")
                    passthrough = ot == "Junction" or mm.layer_of(ot) in (None,) or \
                        mm.aspect_of(ot) == "connector"
                    if rtype not in CARRY_RELS and not passthrough:
                        continue
                    if not _can_step(ut, ot, mm):
                        continue
                    visited.add(other)
                    nxt.append(other)
                    lyr = mm.layer_of(ot)
                    if lyr and lyr != "motivation":
                        per_layer[lyr] = per_layer.get(lyr, 0) + 1
            frontier = nxt
        rows.append({"id": gid, "label": _label(g), "per_layer": per_layer})
    active_cols = [l for l in MATRIX_LAYERS
                   if any(r["per_layer"].get(l) for r in rows)]
    return rows, active_cols


def analyze(model, mm):
    inc = _build_incidence(model)
    layers_in_play = {mm.layer_of(e.get("type")) for e in model.elements
                      if isinstance(e, dict)} - {None}
    gaps = find_gaps(model, mm, inc, layers_in_play)
    rows, cols = reach_matrix(model, mm, inc)
    # Empty-layer roots: a Goal reaching 0 elements in a layer that IS in play.
    empty_roots = []
    for r in rows:
        for l in cols:
            if r["per_layer"].get(l, 0) == 0:
                empty_roots.append({"goal": r["id"], "label": r["label"], "layer": l})
    return {"gaps": gaps, "rows": rows, "cols": cols,
            "empty_roots": empty_roots, "layers_in_play": sorted(layers_in_play)}


def _median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return 0
    m = n // 2
    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2


def render_text(res, path):
    out = [f"{path} — trace coverage ({load_metamodel().spec})"]

    out.append("")
    if res["gaps"]:
        out.append(f"Coverage gaps — upstream intent with no downstream carrier ({len(res['gaps'])}):")
        for g in sorted(res["gaps"], key=lambda x: x["rule"]):
            out.append(f"  [{g['rule']:<14}] {g['id']} ({g['label']}): {g['message']}")
    else:
        out.append("Coverage gaps: none — every element meets its layer's Definition of Done.")

    out.append("")
    if res["rows"] and res["cols"]:
        cols = res["cols"]
        w = max([24] + [len(r["label"]) for r in res["rows"]])
        header = "  " + "Goal".ljust(w) + "".join(c[:11].rjust(13) for c in cols)
        out.append("Downstream reach — elements per layer traced from each Goal:")
        out.append(header)
        for r in res["rows"]:
            cells = "".join(str(r["per_layer"].get(c, 0)).rjust(13) for c in cols)
            flag = ""
            zeros = [c for c in cols if r["per_layer"].get(c, 0) == 0]
            if zeros:
                flag = "   <- 0 in " + ", ".join(zeros)
            out.append("  " + r["label"].ljust(w) + cells + flag)
        # skew note per column
        for c in cols:
            vals = [r["per_layer"].get(c, 0) for r in res["rows"]]
            med = _median(vals)
            starved = [r["label"] for r in res["rows"] if r["per_layer"].get(c, 0) == 0]
            if starved and med > 0:
                out.append(f"  skew [{c}]: median reach {med:g}, but {', '.join(starved)} reach 0.")
    elif res["rows"]:
        out.append("Downstream reach: Goals present but no lower layers populated yet.")
    else:
        out.append("Downstream reach: no Goal roots to trace from (add motivation first).")

    n_gap = len(res["gaps"])
    n_empty = len(res["empty_roots"])
    out.append("")
    out.append(f"  Summary: {n_gap} coverage gap(s), {n_empty} goal/empty-layer pair(s)."
               + ("" if not (n_gap or n_empty) else
                  "  Reconcile each before descending to the next layer."))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Cross-layer trace-coverage analysis.")
    ap.add_argument("model", help="path to the running-model YAML")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args(argv)

    mm = load_metamodel()
    model = load_model(args.model)
    res = analyze(model, mm)

    if args.format == "json":
        print(json.dumps({"model": args.model, **res}, ensure_ascii=False, indent=2))
    else:
        print(render_text(res, args.model))

    return 1 if (res["gaps"] or res["empty_roots"]) else 0


if __name__ == "__main__":
    sys.exit(main())
