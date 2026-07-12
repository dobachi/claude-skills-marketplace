#!/usr/bin/env python3
"""Shared reader/helpers for a requirements-stories backlog.yaml.

Kept small and dependency-light (PyYAML only). validate_backlog.py, trace_check.py,
emit_backlog_md.py and emit_gherkin.py all import this so they share one parser and
one label/traversal convention. See references/backlog-schema.md for the schema.
"""

from __future__ import annotations

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install -r scripts/requirements.txt\n")
    sys.exit(3)

MOSCOW = ("Must", "Should", "Could", "Won't")

# EARS patterns and the keyword each requires (case-insensitive substring test).
EARS_PATTERNS = {
    "ubiquitous": None,            # no leading keyword; always active
    "event-driven": "when",
    "state-driven": "while",
    "unwanted": "if",             # "If <cond>, then …"
    "optional": "where",
}


def label(value, lang: str = "en") -> str:
    """Resolve a str or {ja,en} label to one string, preferring `lang`."""
    if value is None:
        return ""
    if isinstance(value, dict):
        if lang in value:
            return str(value[lang])
        for k in ("en", "ja"):
            if k in value:
                return str(value[k])
        return str(next(iter(value.values()), "")) if value else ""
    return str(value)


def as_list(value) -> list:
    """Normalise a scalar-or-list field (given/when/then) to a list."""
    if value is None:
        return []
    return list(value) if isinstance(value, list) else [value]


class Backlog:
    def __init__(self, raw: dict, path: str = ""):
        self.raw = raw or {}
        self.path = path
        self.meta = self.raw.get("backlog") or {}
        self.personas = self.raw.get("personas") or []
        self.epics = self.raw.get("epics") or []
        self.stories = self.raw.get("stories") or []
        self.nfrs = self.raw.get("nfrs") or []
        self.story_map = self.raw.get("story_map") or {}
        self.dor = self.raw.get("definition_of_ready") or []
        self.dod = self.raw.get("definition_of_done") or []
        self.by_id = {}
        for group in (self.personas, self.epics, self.stories, self.nfrs):
            for e in group:
                if isinstance(e, dict) and "id" in e:
                    self.by_id.setdefault(e["id"], e)

    # --- lookups ----------------------------------------------------------
    def persona(self, story: dict):
        pid = story.get("persona")
        return self.by_id.get(pid) if isinstance(pid, str) else None

    def epic_of(self, story: dict):
        return self.by_id.get(story.get("epic"))

    def is_job_story(self, story: dict) -> bool:
        return "when" in story and "so_i_can" in story

    def effective_traces(self, el: dict) -> list:
        """A story/epic's traces_to, inheriting the parent epic's when the story omits it."""
        own = el.get("traces_to")
        if own:
            return list(own)
        epic = self.epic_of(el) if el in self.stories else None
        return list(epic.get("traces_to")) if epic and epic.get("traces_to") else []

    def wsjf(self, story: dict):
        w = story.get("wsjf")
        if not isinstance(w, dict):
            return None
        try:
            cod = float(w.get("business_value", 0)) + float(w.get("time_criticality", 0)) \
                + float(w.get("risk_reduction", 0))
            size = float(w.get("job_size", 0))
            return cod / size if size else None
        except (TypeError, ValueError):
            return None

    def all_story_map_story_ids(self) -> list:
        out = []
        for act in self.story_map.get("backbone", []) or []:
            for step in act.get("steps", []) or []:
                out.extend(step.get("stories", []) or [])
        for rel in self.story_map.get("releases", []) or []:
            out.extend(rel.get("stories", []) or [])
        return out

    def ea_model_path(self):
        """Absolute path to the referenced ea-model.yaml, or None."""
        rel = self.meta.get("ea_model")
        if not rel:
            return None
        base = os.path.dirname(os.path.abspath(self.path)) if self.path else os.getcwd()
        return os.path.normpath(os.path.join(base, rel))


def load(path: str) -> Backlog:
    with open(path, encoding="utf-8") as fh:
        return Backlog(yaml.safe_load(fh), path=path)
