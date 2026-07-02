#!/usr/bin/env python3
"""Write a tech-selection decision back into an archimate-ea running model.

Sets `selected-product`, `decision-adr`, and `evaluated-on` as `properties` on a
Technology-layer target element (SystemSoftware / Node / TechnologyService), adding
the three `propertyDefinitions` if absent. Uses ruamel round-trip so comments,
quoting, and key order in ea-model.yaml are preserved.

With --validate it runs the archimate-ea validator as a subprocess after writing and
refuses to leave the model in an ERROR state (restoring the original on failure).

Usage:
    writeback.py --model ea-model.yaml --target syssw-db \
        --product "PostgreSQL 16" --adr ADR-0003 [--date 2026-07-03] \
        [--dry-run] [--validate [--validator PATH]]

Exit codes: 0 = written (and valid if --validate), 2 = bad input / target,
            4 = validation failed after write.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
from datetime import date

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap
except ImportError:
    sys.stderr.write("ruamel.yaml is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

PROP_DEFS = [
    {"key": "selected-product", "type": "string", "name": {"en": "Selected product"}},
    {"key": "decision-adr", "type": "string", "name": {"en": "Decision ADR"}},
    {"key": "evaluated-on", "type": "date", "name": {"en": "Evaluated on"}},
]
TECH_TYPES = {"SystemSoftware", "Node", "TechnologyService"}


def _fail(msg: str, code: int = 2):
    sys.stderr.write(f"error: {msg}\n")
    sys.exit(code)


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def ensure_property_defs(data) -> list:
    """Add any of the three property definitions that the model lacks. Returns added keys."""
    defs = data.get("propertyDefinitions")
    if defs is None:
        from ruamel.yaml.comments import CommentedSeq
        defs = CommentedSeq()
        data["propertyDefinitions"] = defs
    existing = {d.get("key") for d in defs if isinstance(d, dict)}
    added = []
    for pd in PROP_DEFS:
        if pd["key"] not in existing:
            m = CommentedMap()
            m["key"] = pd["key"]
            m["type"] = pd["type"]
            m["name"] = CommentedMap(pd["name"])
            defs.append(m)
            added.append(pd["key"])
    return added


def apply_decision(data, target_id, product, adr, evaluated_on):
    elements = data.get("elements") or []
    el = next((e for e in elements if isinstance(e, dict) and e.get("id") == target_id), None)
    if el is None:
        _fail(f"target element '{target_id}' not found in model")
    etype = el.get("type")
    if etype not in TECH_TYPES:
        _fail(f"target '{target_id}' is type {etype}; expected one of "
              f"{', '.join(sorted(TECH_TYPES))}")
    props = el.get("properties")
    if props is None:
        props = CommentedMap()
        el["properties"] = props
    props["selected-product"] = product
    props["decision-adr"] = adr
    props["evaluated-on"] = evaluated_on
    return el


def dump_str(y: YAML, data) -> str:
    buf = io.StringIO()
    y.dump(data, buf)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description="Write a tech-selection decision into the EA model.")
    ap.add_argument("--model", required=True, help="path to ea-model.yaml")
    ap.add_argument("--target", required=True, help="id of the Technology element to fill")
    ap.add_argument("--product", required=True, help="chosen product, e.g. 'PostgreSQL 16'")
    ap.add_argument("--adr", required=True, help="ADR reference, e.g. ADR-0003")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="evaluated-on date (ISO); defaults to today")
    ap.add_argument("--dry-run", action="store_true", help="print the change, do not write")
    ap.add_argument("--validate", action="store_true",
                    help="run the archimate-ea validator after writing")
    ap.add_argument("--validator", default=None,
                    help="path to validate_model.py (required with --validate unless discoverable)")
    args = ap.parse_args()

    y = _yaml()
    with open(args.model, encoding="utf-8") as fh:
        original = fh.read()
    data = y.load(io.StringIO(original))

    added = ensure_property_defs(data)
    el = apply_decision(data, args.target, args.product, args.adr, args.date)

    rendered = dump_str(y, data)

    if args.dry_run:
        sys.stderr.write(
            f"[dry-run] would set on '{args.target}' ({el.get('type')}): "
            f"selected-product={args.product!r}, decision-adr={args.adr!r}, "
            f"evaluated-on={args.date}\n")
        if added:
            sys.stderr.write(f"[dry-run] would add propertyDefinitions: {', '.join(added)}\n")
        sys.stdout.write(rendered)
        return

    with open(args.model, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    sys.stderr.write(
        f"wrote decision to '{args.target}': {args.product} (ADR {args.adr}, {args.date})\n")
    if added:
        sys.stderr.write(f"added propertyDefinitions: {', '.join(added)}\n")

    if args.validate:
        if not args.validator:
            _fail("--validate requires --validator PATH to validate_model.py")
        proc = subprocess.run(
            [sys.executable, args.validator, args.model, "--format", "text"],
            capture_output=True, text=True)
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        if proc.returncode >= 2:  # 2 = ERROR-level problems
            with open(args.model, "w", encoding="utf-8") as fh:
                fh.write(original)  # roll back so the model is never left invalid
            _fail("validation failed after write; model restored to previous state", code=4)


if __name__ == "__main__":
    main()
