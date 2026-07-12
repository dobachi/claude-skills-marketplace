#!/usr/bin/env python3
"""Render a backlog.yaml to a human-readable Markdown backlog.

Downstream, disposable output — regenerate it, never hand-edit it (fix backlog.yaml
and re-emit). Groups stories under their epics, renders each as a story sentence with
its acceptance criteria and NFRs, then a prioritized view, a WSJF ranking (when
present), and the story map.

Usage:
    emit_backlog_md.py BACKLOG.yaml [--lang en|ja] [--out FILE]
"""

from __future__ import annotations

import argparse
import sys

from backlog_read import MOSCOW, as_list, label, load


def story_sentence(b, s, lang) -> str:
    want = label(s.get("i_want"), lang)
    if b.is_job_story(s):
        return (f"**When** {label(s.get('when'), lang)}, **I want** {want}, "
                f"**so I can** {label(s.get('so_i_can'), lang)}.")
    persona = b.persona(s)
    who = label(persona.get("name"), lang) if persona else (s.get("persona") or "—")
    so = label(s.get("so_that"), lang)
    tail = f", **so that** {so}" if so else ""
    return f"**As a** {who}, **I want** {want}{tail}."


def render_ac(ac, lang, out):
    if ac.get("rule"):
        out.append(f"  - _Rule:_ {label(ac.get('rule'), lang)}")
        return
    title = ac.get("scenario") or ac.get("id") or "scenario"
    out.append(f"  - _Scenario: {title}_")
    out.append("    ```gherkin")
    for kw, field in (("Given", "given"), ("When", "when"), ("Then", "then")):
        vals = as_list(ac.get(field))
        for i, v in enumerate(vals):
            lead = kw if i == 0 else "And"
            out.append(f"    {lead} {label(v, lang)}")
    out.append("    ```")


def nfrs_for(b, story_id):
    return [nf for nf in b.nfrs if story_id in (nf.get("applies_to") or [])]


def render(b, lang) -> str:
    out = [f"# {label(b.meta.get('name'), lang)}", ""]
    if b.meta.get("goal"):
        out += [f"**Goal:** {label(b.meta.get('goal'), lang)}", ""]
    if b.meta.get("ea_model"):
        out += [f"_Traces into EA model:_ `{b.meta['ea_model']}`", ""]

    # Personas
    if b.personas:
        out += ["## Personas", ""]
        for p in b.personas:
            trace = f" — traces to `{', '.join(p['traces_to'])}`" if p.get("traces_to") else ""
            desc = f": {label(p.get('description'), lang)}" if p.get("description") else ""
            out.append(f"- **{label(p.get('name'), lang)}** (`{p['id']}`){desc}{trace}")
        out.append("")

    # Epics → stories
    out += ["## Epics & stories", ""]
    by_epic = {}
    for s in b.stories:
        by_epic.setdefault(s.get("epic"), []).append(s)
    epic_order = list(b.epics) + [None]  # None = stories with no epic, rendered last
    for ep in epic_order:
        ep_id = ep["id"] if ep else None
        stories = by_epic.get(ep_id, [])
        if ep is None and not stories:
            continue
        if ep is not None:
            pri = f" · _{ep.get('priority')}_" if ep.get("priority") else ""
            trace = f" · traces to `{', '.join(ep['traces_to'])}`" if ep.get("traces_to") else ""
            out += [f"### {label(ep.get('name'), lang)} (`{ep['id']}`){pri}{trace}", ""]
            if ep.get("description"):
                out += [label(ep.get("description"), lang), ""]
        else:
            out += ["### (no epic)", ""]
        for s in stories:
            meta_bits = []
            if s.get("priority"):
                meta_bits.append(s["priority"])
            if s.get("estimate") is not None:
                meta_bits.append(f"{s['estimate']} pts")
            if s.get("status"):
                meta_bits.append(s["status"])
            meta = f"  \n  _{' · '.join(meta_bits)}_" if meta_bits else ""
            out.append(f"- **`{s.get('id')}`** {story_sentence(b, s, lang)}{meta}")
            for ac in s.get("acceptance_criteria") or []:
                if isinstance(ac, dict):
                    render_ac(ac, lang, out)
            for nf in nfrs_for(b, s.get("id")):
                m = f" — _{nf['metric']}_" if nf.get("metric") else ""
                out.append(f"  - _NFR ({nf.get('quality', nf.get('pattern'))}):_ "
                           f"{label(nf.get('text'), lang)}{m}")
            out.append("")

    # Cross-cutting NFRs (not attached to a single story)
    loose = [nf for nf in b.nfrs if not nf.get("applies_to")]
    if loose:
        out += ["## Cross-cutting non-functional requirements", ""]
        for nf in loose:
            m = f" — _{nf['metric']}_" if nf.get("metric") else ""
            out.append(f"- **`{nf['id']}`** ({nf.get('quality', nf.get('pattern'))}) "
                       f"{label(nf.get('text'), lang)}{m}")
        out.append("")

    # Prioritized view (MoSCoW)
    buckets = {k: [] for k in MOSCOW}
    for s in b.stories:
        if s.get("priority") in buckets:
            buckets[s["priority"]].append(s)
    if any(buckets.values()):
        out += ["## Prioritized (MoSCoW)", ""]
        for k in MOSCOW:
            if buckets[k]:
                ids = ", ".join(f"`{s['id']}`" for s in buckets[k])
                out.append(f"- **{k}:** {ids}")
        out.append("")

    # WSJF ranking
    ranked = sorted((s for s in b.stories if b.wsjf(s) is not None),
                    key=lambda s: b.wsjf(s), reverse=True)
    if ranked:
        out += ["## WSJF ranking (highest first)", "",
                "| Story | WSJF |", "|---|---|"]
        for s in ranked:
            out.append(f"| `{s['id']}` | {b.wsjf(s):.2f} |")
        out.append("")

    # Story map
    sm = b.story_map
    if sm.get("backbone"):
        out += ["## Story map", ""]
        for act in sm["backbone"]:
            out.append(f"- **{label(act.get('activity'), lang)}**")
            for step in act.get("steps", []) or []:
                ids = ", ".join(f"`{x}`" for x in step.get("stories", []) or [])
                out.append(f"  - {label(step.get('step'), lang)}: {ids}")
        out.append("")
        if sm.get("releases"):
            out += ["**Releases:**", ""]
            for rel in sm["releases"]:
                ids = ", ".join(f"`{x}`" for x in rel.get("stories", []) or [])
                out.append(f"- _{rel.get('name')}_: {ids}")
            out.append("")

    if b.dor:
        out += ["## Definition of Ready", ""] + [f"- {label(x, lang)}" for x in b.dor] + [""]
    if b.dod:
        out += ["## Definition of Done", ""] + [f"- {label(x, lang)}" for x in b.dod] + [""]

    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Render backlog.yaml to Markdown.")
    ap.add_argument("backlog")
    ap.add_argument("--lang", choices=["en", "ja"], default="en")
    ap.add_argument("--out", help="write to FILE instead of stdout")
    args = ap.parse_args()

    md = render(load(args.backlog), args.lang)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md)
        sys.stderr.write(f"wrote {args.out}\n")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
