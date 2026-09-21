#!/usr/bin/env python3
"""audit_walk.py — did the walker stay within what a user can touch and know?

Reads, after the walk:
  <log>/transcript.jsonl   the walker's tool calls. Claude Code `--output-format
                           stream-json`, or a generic JSONL of {"tool": ..., "input": {...},
                           "denied": bool} for other agents
  <log>/actions.jsonl      walk_driver.py's own record (optional)
  policy.json              start_url, allowed_urls, allowed_commands, forbidden_paths,
                           forbidden_terms (internal names the UI never shows)

VIOLATION (exit 1) — something outside a user's reach was actually done:
  - a command other than walk_driver.py / allowed_commands / read-only look-around
    (ls, pwd, cat/head/tail/wc of relative paths) ran
  - a tool other than Bash/Read/Write/Edit/Glob/Grep/TodoWrite ran
  - a file path outside the work directory was read or written
  - a URL outside allowed_urls was fetched by a command (curl, wget, python …)
  - raw browser automation appeared (evaluate, force=True, page.content, CSS locator …)
  - a forbidden path or forbidden term appears in anything the walker sent — it knew
    something a user could not (the walk is not blind)
ATTEMPT (reported, exit 0) — the same, but the harness denied it (permission layer
  or walk_driver refusal). The walk stayed clean; the attempts say where it pushed.

Exit codes: 0 clean / 1 violations / 2 missing or unreadable input
"""
import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path

OK_TOOLS = {"Bash", "Read", "Write", "Edit", "Glob", "Grep", "TodoWrite"}
LOOK_AROUND = {"ls", "pwd", "cat", "head", "tail", "wc", "echo", "file"}
RAW_BROWSER = re.compile(
    r"\bevaluate\s*\(|force\s*=\s*True|\bpage\.content\s*\(|\.inner_html\s*\(|query_selector|"
    r"\blocator\s*\(\s*['\"][#.\[/]|\bpage\.\$|document\.|localStorage|sessionStorage|"
    r"sync_playwright|chromium\.launch", re.I)
URL = re.compile(r"https?://[^\s'\"<>)]+")
DENIED = re.compile(r"permission|denied|not allowed|don't ask|haven't granted", re.I)
SEGMENT_SPLIT = re.compile(r"\s*(?:&&|\|\||;|\|)\s*")


def load_transcript(path):
    """Yield (tool, input, denied, result_text) for every tool call."""
    calls, results = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if not isinstance(r, dict):
            continue
        if "tool" in r and "input" in r:                      # generic format
            calls.append((r["tool"], r["input"], bool(r.get("denied")), ""))
            continue
        msg = r.get("message") if isinstance(r, dict) else None
        msg = msg if isinstance(msg, dict) else {}
        content = msg.get("content") if isinstance(msg.get("content"), list) else []
        for c in content:
            if c.get("type") == "tool_use":
                calls.append((c.get("name"), c.get("input") or {}, c.get("id"), None))
            elif c.get("type") == "tool_result":
                t = c.get("content")
                t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
                results[c.get("tool_use_id")] = (bool(c.get("is_error")), t)
    out = []
    for tool, inp, ident, res in calls:
        if res is None:                                       # claude: resolve by id
            is_err, text = results.get(ident, (False, ""))
            denied = is_err and bool(DENIED.search(text[:300]))
            out.append((tool, inp, denied, text))
        else:
            out.append((tool, inp, ident, res))
    return out


def url_allowed(url, policy):
    url = url.rstrip(".,")
    for entry in policy.get("allowed_urls", []) + [policy.get("start_url", "")]:
        if not entry:
            continue
        if entry.endswith("*") and url.startswith(entry[:-1]):
            return True
        if url == entry:
            return True
    return False


def inside(path, work):
    """Lexically inside the work directory (after resolving . and ..)."""
    w = str(work)
    p = os.path.normpath(path if os.path.isabs(path) else os.path.join(w, path))
    return p == w or p.startswith(w.rstrip("/") + "/")


def check_command(cmd, policy, work):
    """Return a list of problems for one Bash command string."""
    problems = []
    allowed_cmds = [c.strip() for c in policy.get("allowed_commands", []) if c.strip()]
    if RAW_BROWSER.search(cmd):
        problems.append("raw browser automation: %r" % RAW_BROWSER.search(cmd).group(0))
    for u in URL.findall(cmd):
        if not url_allowed(u, policy):
            problems.append("URL not reachable by a user: %s" % u)
    if "$(" in cmd or "`" in cmd:
        problems.append("command substitution — cannot tell what ran")
    for seg in SEGMENT_SPLIT.split(cmd.strip()):
        if not seg:
            continue
        if re.match(r"^\s*(for|while|if|do|done|then|fi)\b", seg):
            problems.append("shell control flow — use one walk_driver.py call per action")
            continue
        try:
            words = shlex.split(seg)
        except ValueError:
            words = seg.split()
        if not words:
            continue
        head = words[0]
        if words[:2] in (["python3", "walk_driver.py"], ["python3", "./walk_driver.py"]):
            continue
        if any(seg.strip() == c or seg.strip().startswith(c + " ") for c in allowed_cmds):
            continue
        if head in LOOK_AROUND:
            outside = [w for w in words[1:] if not w.startswith("-") and not inside(w, work)]
            if outside:
                problems.append("looked outside the work directory: %s" % " ".join(outside))
            continue
        problems.append("not a user action: %s" % seg[:80])
    return problems


def main(argv):
    ap = argparse.ArgumentParser(prog="audit_walk.py")
    ap.add_argument("--policy", required=True, type=Path)
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--transcript", type=Path, help="default: <log>/transcript.jsonl")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    tpath = a.transcript or a.log / "transcript.jsonl"
    if not a.policy.is_file():
        print("audit_walk: no policy file %s" % a.policy, file=sys.stderr); return 2
    if not tpath.is_file():
        print("audit_walk: no transcript %s — cannot audit a walk with no record" % tpath,
              file=sys.stderr); return 2
    try:
        policy = json.loads(a.policy.read_text(encoding="utf-8"))
    except ValueError as e:
        print("audit_walk: policy is not JSON: %s" % e, file=sys.stderr); return 2
    work = Path(os.path.realpath(a.work))
    calls = load_transcript(tpath)
    if not calls:
        print("audit_walk: transcript has no tool calls — wrong file or wrong format", file=sys.stderr)
        return 2

    forbidden = [f for f in policy.get("forbidden_paths", []) if f]
    terms = [t for t in policy.get("forbidden_terms", []) if t]
    violations, attempts = [], []
    for i, (tool, inp, denied, _text) in enumerate(calls, 1):
        blob = json.dumps(inp, ensure_ascii=False)
        found = []
        if tool not in OK_TOOLS:
            found.append("tool %s is not a user's" % tool)
        if tool == "Bash":
            found += check_command(inp.get("command", ""), policy, work)
        elif tool in ("Read", "Write", "Edit"):
            p = inp.get("file_path", "")
            if p and not inside(p, work):
                found.append("%s outside the work directory: %s" % (tool, p))
            if tool in ("Write", "Edit") and RAW_BROWSER.search(blob):
                found.append("wrote raw browser automation: %r" % RAW_BROWSER.search(blob).group(0))
        elif tool in ("Glob", "Grep"):
            p = inp.get("path")
            if p and not inside(p, work):
                found.append("%s outside the work directory: %s" % (tool, p))
        for f in forbidden:
            if f in blob:
                found.append("mentions forbidden path %s — not blind" % f)
        for t in terms:
            if t in blob:
                found.append("uses internal term %r that the UI does not show — not blind" % t)
        for p in dict.fromkeys(found):                      # de-duplicate, keep order
            (attempts if denied else violations).append("call %d %s: %s" % (i, tool, p))

    refused = []
    acts = a.log / "actions.jsonl"
    if acts.is_file():
        for line in acts.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("result") == "refused":
                refused.append("step %s: %s" % (r.get("step"), json.dumps(r.get("request"), ensure_ascii=False)))

    print("audit_walk: %d tool call(s) checked" % len(calls))
    for v in violations:
        print("VIOLATION " + v)
    for t in attempts:
        print("ATTEMPT   " + t + " (denied)")
    for r in refused:
        print("ATTEMPT   walk_driver refused " + r)
    if violations:
        print("audit_walk: the walk left a user's reach — report it as `walker: separate agent "
              "(not blind)` and treat findings that depend on it as unverified")
        return 1
    print("audit_walk: clean — %d attempt(s) denied, none executed" % (len(attempts) + len(refused)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
