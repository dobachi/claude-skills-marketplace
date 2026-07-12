#!/usr/bin/env python3
"""Emit Gherkin .feature skeletons from a backlog.yaml.

One feature file per epic (stories with no epic go to `misc.feature`). Each story
becomes a labelled group; each acceptance criterion becomes a Scenario — Given/When/
Then criteria map directly, and rule criteria become a single-assertion scenario to
flesh out. Downstream, disposable output: regenerate it, don't hand-edit.

Usage:
    emit_gherkin.py BACKLOG.yaml [--lang en|ja] [--out DIR]

With --out, writes one .feature per epic into DIR; without it, prints all to stdout
separated by `# file:` markers.
"""

from __future__ import annotations

import argparse
import os
import sys

from backlog_read import as_list, label, load


def _steps(kw, field, ac, lang, lines):
    vals = as_list(ac.get(field))
    for i, v in enumerate(vals):
        lines.append(f"    {kw if i == 0 else 'And'} {label(v, lang)}")


def scenario(ac, lang) -> list:
    lines = []
    if ac.get("rule"):
        rule = label(ac.get("rule"), lang)
        lines.append(f"  Scenario: {rule}")
        lines.append(f"    Then {rule}")
        return lines
    lines.append(f"  Scenario: {ac.get('scenario') or ac.get('id') or 'scenario'}")
    _steps("Given", "given", ac, lang, lines)
    _steps("When", "when", ac, lang, lines)
    _steps("Then", "then", ac, lang, lines)
    return lines


def story_sentence(b, s, lang) -> str:
    want = label(s.get("i_want"), lang)
    if b.is_job_story(s):
        return (f"When {label(s.get('when'), lang)}, I want {want}, "
                f"so I can {label(s.get('so_i_can'), lang)}.")
    persona = b.persona(s)
    who = label(persona.get("name"), lang) if persona else (s.get("persona") or "—")
    so = label(s.get("so_that"), lang)
    return f"As a {who}, I want {want}" + (f", so that {so}." if so else ".")


def feature_for_epic(b, ep, stories, lang) -> str:
    title = label(ep.get("name"), lang) if ep else "Miscellaneous stories"
    lines = [f"Feature: {title}"]
    if ep and ep.get("traces_to"):
        lines.append(f"  # EA traces_to: {', '.join(ep['traces_to'])}")
    if ep and ep.get("description"):
        lines.append(f"  {label(ep.get('description'), lang)}")
    lines.append("")
    for s in stories:
        lines.append(f"  # Story {s.get('id')}: {story_sentence(b, s, lang)}")
        acs = [ac for ac in (s.get("acceptance_criteria") or []) if isinstance(ac, dict)]
        if not acs:
            lines.append("  # (no acceptance criteria yet)")
        for ac in acs:
            lines += scenario(ac, lang)
            lines.append("")
        if not acs:
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Emit Gherkin .feature skeletons from backlog.yaml.")
    ap.add_argument("backlog")
    ap.add_argument("--lang", choices=["en", "ja"], default="en")
    ap.add_argument("--out", help="directory to write one .feature per epic")
    args = ap.parse_args()

    b = load(args.backlog)
    by_epic = {}
    for s in b.stories:
        by_epic.setdefault(s.get("epic"), []).append(s)

    groups = []  # (filename, epic-or-None, stories)
    for ep in b.epics:
        if by_epic.get(ep["id"]):
            groups.append((f"{ep['id']}.feature", ep, by_epic[ep["id"]]))
    if by_epic.get(None):
        groups.append(("misc.feature", None, by_epic[None]))

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        for fname, ep, stories in groups:
            path = os.path.join(args.out, fname)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(feature_for_epic(b, ep, stories, args.lang))
            sys.stderr.write(f"wrote {path}\n")
    else:
        for fname, ep, stories in groups:
            print(f"# file: {fname}")
            print(feature_for_epic(b, ep, stories, args.lang))


if __name__ == "__main__":
    main()
