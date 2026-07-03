#!/usr/bin/env python3
"""Shared read/traversal helpers for archimate-to-impl over an ea-model.yaml.

Kept intentionally small and dependency-light (PyYAML only). derive.py and
trace_check.py import this so they share one parser and one set of traversal rules.
It never writes the model — this skill treats ea-model.yaml as read-only upstream.
"""

from __future__ import annotations

import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

# ArchiMate types this skill cares about, grouped for readability.
APP_COMPONENT = "ApplicationComponent"
APP_FUNCTION = "ApplicationFunction"
APP_SERVICE = "ApplicationService"
APP_INTERFACE = "ApplicationInterface"
DATA_OBJECT = "DataObject"
REQ_TYPES = ("Requirement", "Constraint")


class Model:
    def __init__(self, raw: dict):
        self.raw = raw or {}
        self.elements = self.raw.get("elements") or []
        self.relationships = self.raw.get("relationships") or []
        self.by_id = {e["id"]: e for e in self.elements
                      if isinstance(e, dict) and "id" in e}

    def of_type(self, *types) -> list:
        return [e for e in self.elements
                if isinstance(e, dict) and e.get("type") in types]

    def type_of(self, eid: str):
        e = self.by_id.get(eid)
        return e.get("type") if e else None

    def is_type(self, eid: str, *types) -> bool:
        return self.type_of(eid) in types

    def rels(self, type=None, source=None, target=None) -> list:
        out = []
        for r in self.relationships:
            if not isinstance(r, dict):
                continue
            if type is not None and r.get("type") != type:
                continue
            if source is not None and r.get("source") != source:
                continue
            if target is not None and r.get("target") != target:
                continue
            out.append(r)
        return out

    def name(self, eid: str) -> str:
        e = self.by_id.get(eid)
        if not e:
            return eid
        n = e.get("name")
        if isinstance(n, dict):
            for k in ("en", "ja"):
                if k in n:
                    return str(n[k])
            return str(next(iter(n.values()), eid)) if n else eid
        return str(n) if n else eid


def load(path: str) -> Model:
    with open(path, encoding="utf-8") as fh:
        return Model(yaml.safe_load(fh))


# --- naming helpers -------------------------------------------------------

def _ascii_words(name: str) -> list:
    """Split a label into ascii word tokens; drops non-ascii (e.g. Japanese)."""
    import re
    tokens = re.findall(r"[A-Za-z0-9]+", name)
    return tokens


def camel(name: str, fallback: str) -> str:
    """CamelCase identifier from a label, falling back to an id-derived name."""
    words = _ascii_words(name)
    if not words:
        words = _ascii_words(fallback.replace("-", " "))
    if not words:
        return "Entity"
    return "".join(w[:1].upper() + w[1:] for w in words)


def kebab(name: str, fallback: str) -> str:
    """kebab-case path segment from a label, falling back to an id-derived name."""
    words = _ascii_words(name)
    if not words:
        words = _ascii_words(fallback.replace("-", " "))
    if not words:
        return "resource"
    return "-".join(w.lower() for w in words)
