#!/usr/bin/env python3
"""Check bidirectional traceability between a backlog.yaml and an ArchiMate ea-model.yaml.

This is the EA bridge. The EA model is read-only upstream (this skill never edits it);
the backlog references it by id via `traces_to`. Two directions, mirroring
archimate-to-impl's orphan philosophy — orphans ARE the product:

  FORWARD   is every EA requirement realized by the backlog?
    uncovered-requirement  a Requirement/Constraint no epic/story/NFR traces to
                           → a gap: is it out of scope, or a missing story?
    goal-not-addressed     a Goal/Outcome nothing in the backlog traces to (softer)

  BACKWARD  does every backlog item point back to the model?
    untraced-story         a story (and its epic) with no traces_to at all
                           → scope creep, or a new requirement to push up into the EA model
    dangling-trace         a traces_to id that does not exist in the EA model
    persona-trace-type     a persona tracing to a non-actor element

If the backlog has no `ea_model` (and none is given with --ea), there is nothing to
check and the run is a clean no-op — the skill works standalone.

Usage:
    trace_check.py BACKLOG.yaml [--ea EA-MODEL.yaml] [--format text|json] [--strict]

Exit codes: 0 = clean/not-linked, 1 = warnings, 2 = warnings with --strict.
"""

from __future__ import annotations

import argparse
import json
import sys

import yaml

from backlog_read import label as blabel
from backlog_read import load as load_backlog

WARN = "WARN"
REQ_TYPES = ("Requirement", "Constraint")
GOAL_TYPES = ("Goal", "Outcome")
ACTOR_TYPES = ("Stakeholder", "BusinessActor", "BusinessRole")


class Problem:
    __slots__ = ("severity", "code", "ref", "message")

    def __init__(self, code, ref, message):
        self.severity, self.code, self.ref, self.message = WARN, code, ref, message

    def as_dict(self):
        return {"severity": self.severity, "code": self.code,
                "ref": self.ref, "message": self.message}


# Contribution relationships followed forward (source realizes/contributes-to target)
# when deciding whether a referenced requirement transitively serves a goal. ArchiMate
# lets a chain of these be derived into one, so req →(Realization)→ junction →(Realization)→
# goal means the requirement serves that goal.
CONTRIB_TYPES = ("Realization", "Influence", "Serving")


class EAModel:
    """Minimal read-only view of an ea-model.yaml (id/type/name/relationships)."""

    def __init__(self, raw: dict):
        self.elements = (raw or {}).get("elements") or []
        self.relationships = (raw or {}).get("relationships") or []
        self.by_id = {e["id"]: e for e in self.elements
                      if isinstance(e, dict) and "id" in e}
        # forward adjacency over contribution edges: source -> [targets]
        self._fwd = {}
        for r in self.relationships:
            if isinstance(r, dict) and r.get("type") in CONTRIB_TYPES:
                self._fwd.setdefault(r.get("source"), []).append(r.get("target"))

    def type_of(self, eid):
        e = self.by_id.get(eid)
        return e.get("type") if e else None

    def name(self, eid):
        e = self.by_id.get(eid)
        return blabel(e.get("name"), "en") if e else eid

    def of_type(self, *types):
        return [e for e in self.elements
                if isinstance(e, dict) and e.get("type") in types]

    def forward_reachable(self, starts) -> set:
        """Ids reachable from `starts` by following contribution edges source->target."""
        seen, stack = set(), list(starts)
        while stack:
            for t in self._fwd.get(stack.pop(), ()):
                if t not in seen:
                    seen.add(t)
                    stack.append(t)
        return seen


def check(b, ea) -> list:
    problems = []
    P = lambda *a: problems.append(Problem(*a))

    # Gather every EA id the backlog references, per source, for both directions.
    referenced = set()

    def collect(el, kind):
        for eid in el.get("traces_to", []) or []:
            referenced.add(eid)
            if eid not in ea.by_id:
                P("dangling-trace", el.get("id", kind),
                  f"{kind} traces_to '{eid}', which is not in the EA model.")

    for p in b.personas:
        collect(p, "persona")
        for eid in p.get("traces_to", []) or []:
            if eid in ea.by_id and ea.type_of(eid) not in ACTOR_TYPES:
                P("persona-trace-type", p.get("id", "persona"),
                  f"persona traces to '{eid}' ({ea.type_of(eid)}); expected a "
                  f"Stakeholder/BusinessActor/BusinessRole.")
    for ep in b.epics:
        collect(ep, "epic")
    for nf in b.nfrs:
        collect(nf, "nfr")

    # Stories: backward untraced check uses inherited (epic) traces, but the epic's
    # own id is still counted toward forward coverage via the epics loop above.
    for s in b.stories:
        collect(s, "story")
        if not b.effective_traces(s):
            P("untraced-story", s.get("id", "story"),
              "story traces to no EA element (directly or via its epic) — scope creep, "
              "or a requirement to push up into the EA model.")

    # FORWARD coverage.
    # Requirements need a story of their OWN — coverage is strictly direct reference.
    for e in ea.of_type(*REQ_TYPES):
        if e["id"] not in referenced:
            P("uncovered-requirement", e["id"],
              f"{ea.type_of(e['id'])} '{ea.name(e['id'])}' is realized by no epic/story/NFR "
              f"— a gap: out of scope, or a missing story?")
    # Goals are served transitively: a goal is addressed if a referenced requirement
    # reaches it over contribution edges (req → … → goal).
    served = referenced | ea.forward_reachable(referenced)
    for e in ea.of_type(*GOAL_TYPES):
        if e["id"] not in served:
            P("goal-not-addressed", e["id"],
              f"{ea.type_of(e['id'])} '{ea.name(e['id'])}' is addressed by nothing in the backlog "
              f"(no traced requirement contributes to it).")

    return problems


# --- gap disposition ledger (closes the feedback loop) --------------------

GAP_STATUSES = ("open", "out-of-scope", "promoted", "fixed")


def _gap_key(code, ref):
    return f"{code}:{ref}"


def merge_gaps(problems, path):
    """Merge detected orphans into a `gaps.yaml` disposition ledger at `path`.

    Each orphan is keyed "<code>:<ref>" and carries a human-controlled status:
    open | out-of-scope | promoted | fixed (+ a free-text note). Re-running preserves
    existing dispositions, adds new orphans as `open`, and flips a still-`open` gap to
    `fixed` once it is no longer detected. `promoted` marks an orphan the team decided
    to push up into the EA model (the promotion list). Returns (gaps, open_detected):
    open_detected = currently-detected orphans still `open` — what a gate checks.
    """
    import os
    existing, order = {}, []
    if os.path.exists(path):
        raw = yaml.safe_load(open(path, encoding="utf-8")) or {}
        for g in (raw.get("gaps") or []):
            if isinstance(g, dict) and g.get("id"):
                existing[g["id"]] = g
                order.append(g["id"])
    current = {_gap_key(p.code, p.ref): p for p in problems}

    merged, new_order = {}, []
    for key in order:                          # preserve existing entries & order
        g = existing[key]
        if key in current:
            g["message"] = current[key].message
            g.setdefault("status", "open")
            g.setdefault("note", "")
        elif g.get("status", "open") == "open":
            g["status"] = "fixed"              # was open, now gone → resolved
        merged[key] = g
        new_order.append(key)
    for key, p in current.items():             # add newly-detected orphans
        if key not in merged:
            merged[key] = {"id": key, "code": p.code, "ref": p.ref,
                           "message": p.message, "status": "open", "note": ""}
            new_order.append(key)

    gaps = [merged[k] for k in new_order]
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump({"gaps": gaps}, fh, allow_unicode=True, sort_keys=False)
    open_detected = sum(1 for k in current if merged[k].get("status", "open") == "open")
    return gaps, open_detected


def _gap_counts(gaps):
    counts = {s: 0 for s in GAP_STATUSES}
    for g in gaps:
        st = g.get("status", "open")
        counts[st] = counts.get(st, 0) + 1
    return counts


def main():
    ap = argparse.ArgumentParser(description="Check backlog↔EA-model traceability.")
    ap.add_argument("backlog", help="path to backlog.yaml")
    ap.add_argument("--ea", help="path to ea-model.yaml (overrides backlog.ea_model)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on warnings")
    ap.add_argument("--gaps", metavar="FILE",
                    help="read/write a gaps.yaml disposition ledger for the orphans")
    ap.add_argument("--require-disposition", action="store_true",
                    help="with --gaps: exit non-zero if any detected orphan is still 'open'")
    args = ap.parse_args()

    b = load_backlog(args.backlog)
    ea_path = args.ea or b.ea_model_path()
    if not ea_path:
        msg = "no EA model linked (backlog.ea_model unset and --ea not given) — nothing to trace."
        print(json.dumps({"problems": [], "summary": {"linked": False}}) if args.format == "json"
              else f"{args.backlog} — {msg}")
        sys.exit(0)

    try:
        with open(ea_path, encoding="utf-8") as fh:
            ea = EAModel(yaml.safe_load(fh))
    except OSError as e:
        sys.stderr.write(f"cannot read EA model '{ea_path}': {e}\n")
        sys.exit(3)

    problems = check(b, ea)

    gaps, gap_open = ([], 0)
    if args.gaps:
        gaps, gap_open = merge_gaps(problems, args.gaps)

    if args.format == "json":
        out = {"problems": [p.as_dict() for p in problems],
               "summary": {"linked": True, "warnings": len(problems)}}
        if args.gaps:
            out["gaps"] = gaps
            out["summary"]["open_undispositioned"] = gap_open
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"{args.backlog} ↔ {ea_path} — traceability check (requirements-stories)")
        if not problems:
            print("  clean — every requirement is covered and every story traces back.")
        else:
            for p in problems:
                print(f"  [{p.severity}] {p.code}: {p.ref}\n      {p.message}")
            print(f"  Summary: {len(problems)} warning(s).")
        if args.gaps:
            c = _gap_counts(gaps)
            print(f"  Gaps ledger: {args.gaps} — open {c['open']}, out-of-scope "
                  f"{c['out-of-scope']}, promoted {c['promoted']}, fixed {c['fixed']}")
            if gap_open:
                print(f"  {gap_open} orphan(s) still undispositioned (status: open) — "
                      f"decide out-of-scope / promoted, or resolve.")

    if args.require_disposition:               # gate mode: pass iff every orphan is dispositioned
        sys.exit(2 if gap_open else 0)
    if problems and args.strict:
        sys.exit(2)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
