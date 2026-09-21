#!/usr/bin/env python3
"""check_report.py <report.md> — check a user-walkthrough report for completeness.

What it checks (structure only — it cannot tell whether a finding is TRUE):
  - every finding heading is `### [Blocker|Major|Minor] title` (JA: 致命/重大/軽微)
  - every finding has Where, Steps (with at least one numbered step), Expected,
    Actual, Evidence, Reproduced — none empty
  - Actual is not speculation ("might", "probably", 「可能性」「かもしれ」...; quoted text is exempt)
  - Expected and Actual are not the same text
  - Reproduced is `n/m`, `not run (static)`, or `observed by user`
  - a Blocker is observed (not `0/m`, not a static guess)
  - the report has a Not checked (未確認) section

Exit codes: 0 complete / 1 findings / 2 file missing or not a walkthrough report
"""
import re
import sys
from pathlib import Path

SEVERITY = {"blocker": "Blocker", "major": "Major", "minor": "Minor",
            "致命": "Blocker", "重大": "Major", "軽微": "Minor"}
FIELDS = {
    "where": "where", "場所": "where",
    "steps": "steps", "手順": "steps", "再現手順": "steps",
    "expected": "expected", "期待": "expected", "期待結果": "expected",
    "actual": "actual", "実際": "actual", "実際の結果": "actual",
    "evidence": "evidence", "証拠": "evidence",
    "reproduced": "reproduced", "再現": "reproduced", "再現性": "reproduced",
}
REQUIRED = ["where", "steps", "expected", "actual", "evidence", "reproduced"]
FINDINGS_H = re.compile(r"^##\s+(findings|指摘)", re.I)
NOT_CHECKED_H = re.compile(r"^##\s+(not checked|未確認)", re.I)
H2 = re.compile(r"^##\s+")
H3 = re.compile(r"^###\s+(.*)$")
SEV_H = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
FIELD = re.compile(r"^\s*[-*]\s*\*\*\s*([^*:：]+?)\s*[:：]?\s*\*\*\s*[:：]?\s*(.*)$")
NUMBERED = re.compile(r"(^|\s)\d+[.)]\s+\S")
SPECULATION = re.compile(
    r"\b(might|probably|possibly|likely|perhaps|could(?!\s*(?:not|n't)))\b"
    r"|可能性|かもしれ|と思われ|おそらく|だろう",
    re.I)
# Quoted text is the product speaking (a verbatim message), not the reporter guessing.
QUOTED = re.compile(r'"[^"]*"|“[^”]*”|「[^」]*」|`[^`]*`')
REPRO_COUNT = re.compile(r"^(\d+)\s*/\s*(\d+)")
REPRO_STATIC = re.compile(r"not run|static|未実行|静的", re.I)
REPRO_USER = re.compile(r"observed by user|ユーザー確認|利用者確認", re.I)


def parse(lines):
    """Return (has_findings_section, has_not_checked, findings list)."""
    in_fence = False
    section = None
    has_findings = has_not_checked = False
    findings, cur, field = [], None, None
    for raw in lines:
        line = raw.rstrip("\n")
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            if cur is not None and field:
                cur["fields"][field] += "\n" + line
            continue
        if not in_fence and H2.match(line) and not line.startswith("###"):
            section = "other"
            if FINDINGS_H.match(line):
                section, has_findings = "findings", True
            elif NOT_CHECKED_H.match(line):
                has_not_checked = True
            cur, field = None, None
            continue
        if section != "findings":
            continue
        m = None if in_fence else H3.match(line)
        if m:
            cur = {"heading": m.group(1).strip(), "fields": {}}
            findings.append(cur)
            field = None
            continue
        if cur is None:
            continue
        fm = None if in_fence else FIELD.match(line)
        if fm and fm.group(1).strip().lower() in FIELDS:
            field = FIELDS[fm.group(1).strip().lower()]
            cur["fields"][field] = fm.group(2).strip()
        elif field:
            cur["fields"][field] += "\n" + line
    return has_findings, has_not_checked, findings


def check(findings):
    problems = []
    for i, f in enumerate(findings, 1):
        tag = "F%d %r" % (i, f["heading"][:50])
        sm = SEV_H.match(f["heading"])
        sev = SEVERITY.get(sm.group(1).strip().lower()) if sm else None
        if sev is None:
            problems.append("%s: heading must start with [Blocker], [Major] or [Minor]" % tag)
        vals = {k: v.strip() for k, v in f["fields"].items()}
        for k in REQUIRED:
            if not vals.get(k):
                problems.append("%s: missing or empty %s" % (tag, k.capitalize()))
        if vals.get("steps") and not NUMBERED.search(vals["steps"]):
            problems.append("%s: Steps has no numbered step (1. ...)" % tag)
        spec = SPECULATION.search(QUOTED.sub("", vals.get("actual", "")))
        if spec:
            problems.append("%s: Actual is speculative (%r) — report what was observed"
                            % (tag, spec.group(0)))
        if vals.get("expected") and vals.get("actual") and \
                " ".join(vals["expected"].split()) == " ".join(vals["actual"].split()):
            problems.append("%s: Expected and Actual are identical" % tag)
        r = vals.get("reproduced", "")
        if r:
            cm = REPRO_COUNT.match(r)
            observed = (cm and int(cm.group(1)) > 0) or bool(REPRO_USER.search(r))
            if not (cm or REPRO_STATIC.search(r) or REPRO_USER.search(r)):
                problems.append("%s: Reproduced %r is not n/m, 'not run (static)' or "
                                "'observed by user'" % (tag, r.splitlines()[0]))
            elif cm and int(cm.group(1)) > int(cm.group(2)):
                problems.append("%s: Reproduced %r — more successes than attempts" % (tag, r))
            elif sev == "Blocker" and not observed:
                problems.append("%s: a Blocker must be observed (Reproduced %r)"
                                % (tag, r.splitlines()[0]))
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: check_report.py <report.md>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print("check_report: no such file: %s" % path, file=sys.stderr)
        return 2
    has_findings, has_not_checked, findings = parse(
        path.read_text(encoding="utf-8").splitlines())
    if not has_findings:
        print("check_report: %s has no '## Findings' / '## 指摘' section — "
              "not a walkthrough report, nothing checked" % path, file=sys.stderr)
        return 2
    problems = check(findings)
    if not has_not_checked:
        problems.append("report: no '## Not checked' / '## 未確認' section — "
                        "say what was not covered")
    for p in problems:
        print("%s: %s" % (path, p))
    if problems:
        print("check_report: %d problem(s) in %d finding(s)" % (len(problems), len(findings)))
        return 1
    print("check_report: OK — %d finding(s), all complete" % len(findings))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
