#!/usr/bin/env python3
"""Validate a requirements-stories backlog.yaml.

Two tiers, styled after archimate-ea's validate_model.py:

  ERROR  structural — broken references or missing required fields. The backlog is
         malformed; fix before emitting.
  WARN   quality — INVEST / EARS / prioritization / anti-pattern smells. The backlog
         is well-formed but a story or requirement could be better. These are
         conversation starters, not blockers.

Usage:
    validate_backlog.py BACKLOG.yaml [--format text|json] [--strict]

Exit codes: 0 = clean, 1 = warnings only, 2 = errors (or warnings with --strict).
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from backlog_read import EARS_PATTERNS, MOSCOW, as_list, label, load

ERROR, WARN = "ERROR", "WARN"

ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
GENERIC_PERSONA = {"user", "ユーザー", "ユーザ", "someone", "利用者"}
# i_want phrasing that signals a technical task rather than user-visible value.
TASK_SMELL = re.compile(
    r"\b(refactor|migrat|database|schema|index|deploy|pipeline|cron|"
    r"リファクタ|スキーマ|マイグレーション|デプロイ|バッチ|インデックス)\b", re.I)
SHALL_WORDS = ("shall", "must", "なければならない", "しなければ", "する必要がある")
# Bilingual keyword hints per EARS pattern: (english, japanese-substrings).
EARS_KW = {
    "event-driven": ("when", ("とき", "た場合", "たら")),
    "state-driven": ("while", ("間", "の状態", "している場合")),
    "unwanted": ("if", ("もし", "場合", "とき")),
    "optional": ("where", ("を含む", "構成では", "の場合")),
}
SMALL_ESTIMATE_MAX = 8    # story points above this suggest a split (INVEST-Small)
MANY_AC = 8               # more acceptance criteria than this also suggests a split


class Problem:
    __slots__ = ("severity", "code", "ref", "message")

    def __init__(self, severity, code, ref, message):
        self.severity, self.code, self.ref, self.message = severity, code, ref, message

    def as_dict(self):
        return {"severity": self.severity, "code": self.code,
                "ref": self.ref, "message": self.message}


def _text_both(field) -> tuple:
    """Return (english-ish, japanese-ish) lowercased text for keyword tests."""
    en = label(field, "en").lower()
    ja = label(field, "ja")
    return en, ja


def check(b) -> list:
    problems = []
    E = lambda *a: problems.append(Problem(ERROR, *a))
    W = lambda *a: problems.append(Problem(WARN, *a))

    # ── backlog header ────────────────────────────────────────────────
    if not b.meta.get("id"):
        E("missing-id", "backlog", "backlog.id is required.")
    if not b.meta.get("name"):
        E("missing-name", "backlog", "backlog.name is required.")

    # ── unique + well-formed ids ──────────────────────────────────────
    seen = {}
    for group in (b.personas, b.epics, b.stories, b.nfrs):
        for e in group:
            if not isinstance(e, dict):
                continue
            eid = e.get("id")
            if not eid:
                E("missing-element-id", "?", "An element has no id.")
                continue
            if eid in seen:
                E("duplicate-id", eid, f"id '{eid}' is used more than once.")
            seen[eid] = e
            if not ID_RE.match(eid):
                W("id-style", eid, f"id '{eid}' should be kebab-case starting with a letter.")

    # ── epics ─────────────────────────────────────────────────────────
    for ep in b.epics:
        pri = ep.get("priority")
        if pri is not None and pri not in MOSCOW:
            E("bad-priority", ep["id"], f"priority '{pri}' is not MoSCoW {MOSCOW}.")

    # ── stories ───────────────────────────────────────────────────────
    n_prioritised, n_must = 0, 0
    for s in b.stories:
        sid = s.get("id", "?")
        job = b.is_job_story(s)

        # references
        if s.get("epic") and s["epic"] not in b.by_id:
            E("dangling-epic", sid, f"epic '{s['epic']}' does not exist.")
        pid = s.get("persona")
        if isinstance(pid, str) and pid.startswith("persona-") and pid not in b.by_id:
            E("dangling-persona", sid, f"persona '{pid}' does not exist.")

        # shape: needs a capability, and either role-form or job-form completeness
        if not s.get("i_want"):
            E("story-no-goal", sid, "story has no i_want (the capability).")
        if job:
            if not s.get("so_i_can"):
                W("invest-valuable", sid, "job story has no 'so_i_can' — the outcome/benefit is missing.")
        else:
            if not s.get("persona"):
                W("story-no-persona", sid, "story has no persona (the 'who'). Add one or use the job-story form.")
            if not s.get("so_that"):
                W("invest-valuable", sid,
                  "story has no 'so_that' — without the benefit you can't prioritize or de-scope it.")

        # generic persona
        if isinstance(pid, str):
            pname = label(b.persona(s).get("name"), "en") if b.persona(s) else pid
            if pname.strip().lower() in GENERIC_PERSONA or pid.strip().lower() in GENERIC_PERSONA:
                W("generic-persona", sid, "persona is generic ('user') — name the real role; it drives design.")

        # testable
        acs = s.get("acceptance_criteria") or []
        if not acs:
            W("invest-testable", sid, "story has no acceptance_criteria — nothing to confirm 'done'.")
        else:
            for i, ac in enumerate(acs):
                if not isinstance(ac, dict):
                    E("bad-ac", sid, f"acceptance_criteria[{i}] is not a mapping.")
                    continue
                is_gwt = any(k in ac for k in ("given", "when", "then"))
                if not is_gwt and not ac.get("rule"):
                    W("empty-ac", ac.get("id", f"{sid}[{i}]"),
                      "acceptance criterion has neither Given/When/Then nor a rule.")
                elif is_gwt and not as_list(ac.get("then")):
                    W("ac-no-then", ac.get("id", f"{sid}[{i}]"),
                      "Given/When/Then criterion has no 'then' — no observable outcome to assert.")
        if len(acs) > MANY_AC:
            W("invest-small", sid, f"{len(acs)} acceptance criteria — the story may be too big; consider splitting.")

        # small
        est = s.get("estimate")
        if isinstance(est, (int, float)) and est > SMALL_ESTIMATE_MAX:
            W("invest-small", sid,
              f"estimate {est} exceeds {SMALL_ESTIMATE_MAX} — too big for one iteration; split it (see SPIDR).")

        # task-not-story smell
        en, ja = _text_both(s.get("i_want"))
        if TASK_SMELL.search(en) or TASK_SMELL.search(ja):
            if not s.get("so_that") and not s.get("so_i_can"):
                W("task-not-story", sid,
                  "i_want reads like a technical task and has no user benefit — is this a task under a story?")

        # priority
        pri = s.get("priority")
        if pri is not None:
            if pri not in MOSCOW:
                E("bad-priority", sid, f"priority '{pri}' is not MoSCoW {MOSCOW}.")
            else:
                n_prioritised += 1
                if pri == "Must":
                    n_must += 1

    if n_prioritised >= 5 and n_must / n_prioritised > 0.6:
        W("moscow-inflation", "backlog",
          f"{n_must}/{n_prioritised} prioritized stories are 'Must' (>60%) — "
          "'Must' should be the protected minimum, not the default.")

    # ── nfrs (EARS) ───────────────────────────────────────────────────
    for nf in b.nfrs:
        nid = nf.get("id", "?")
        pat = nf.get("pattern")
        if pat not in EARS_PATTERNS:
            E("bad-ears-pattern", nid,
              f"pattern '{pat}' is not one of {tuple(EARS_PATTERNS)}.")
        en, ja = _text_both(nf.get("text"))
        both = en + " " + ja
        if not any(w in both for w in SHALL_WORDS):
            W("ears-no-shall", nid,
              "NFR text has no 'shall'/'must'/'なければならない' — EARS requirements use a modal 'shall'.")
        if pat in EARS_KW:
            en_kw, ja_kws = EARS_KW[pat]
            has = (en_kw in en) or any(k in ja for k in ja_kws)
            if not has:
                W("ears-keyword", nid,
                  f"'{pat}' NFR should open with its EARS keyword "
                  f"('{en_kw}'/'{ja_kws[0]}') — the sentence doesn't match its pattern.")
        if not nf.get("metric"):
            W("nfr-unmeasurable", nid,
              "NFR has no 'metric' — an NFR without a measurable threshold can't be tested.")
        for st in nf.get("applies_to", []) or []:
            if st not in b.by_id:
                E("dangling-applies-to", nid, f"applies_to '{st}' is not a defined story.")

    # ── story map refs ────────────────────────────────────────────────
    for sm_id in b.all_story_map_story_ids():
        if sm_id not in b.by_id:
            E("dangling-map-story", "story_map", f"story_map references unknown story '{sm_id}'.")

    return problems


def main():
    ap = argparse.ArgumentParser(description="Validate a requirements-stories backlog.yaml.")
    ap.add_argument("backlog", help="path to backlog.yaml")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    args = ap.parse_args()

    b = load(args.backlog)
    problems = check(b)
    errors = [p for p in problems if p.severity == ERROR]
    warns = [p for p in problems if p.severity == WARN]

    if args.format == "json":
        print(json.dumps({"problems": [p.as_dict() for p in problems],
                          "summary": {"errors": len(errors), "warnings": len(warns)}},
                         ensure_ascii=False, indent=2))
    else:
        print(f"{args.backlog} — backlog validation (requirements-stories)")
        if not problems:
            print("  clean — structure sound, no INVEST/EARS smells.")
        else:
            for p in problems:
                print(f"  [{p.severity}] {p.code}: {p.ref}\n      {p.message}")
            print(f"  Summary: {len(errors)} error(s), {len(warns)} warning(s).")

    if errors:
        sys.exit(2)
    if warns and args.strict:
        sys.exit(2)
    sys.exit(1 if warns else 0)


if __name__ == "__main__":
    main()
