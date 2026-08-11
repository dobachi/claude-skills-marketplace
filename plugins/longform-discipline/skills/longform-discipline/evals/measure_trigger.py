#!/usr/bin/env python3
"""Trigger measurement that does not bail on the first non-Skill tool call.

run_eval.py returns False as soon as the first tool_use is not Skill/Read. In a
repo whose CLAUDE.md mandates a knowledge-base check, the first call is Bash and
every query scores 0 — including the ones that should score 0, so the result
reads like a clean pass in both directions and carries no information.

This scans the whole stream for a Skill invocation naming the target, and
measures the REAL installed skill rather than a synthetic command file.
"""
import json, os, subprocess, sys, concurrent.futures as cf

REPO = "/home/dobachi/Sources/claude-skills-marketplace"
TARGET = "longform-discipline"

def run(query, timeout=180):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    p = subprocess.run(
        ["claude", "-p", query, "--output-format", "stream-json",
         "--verbose", "--include-partial-messages"],
        cwd=REPO, env=env, capture_output=True, timeout=timeout)
    tools, fired, pending = [], False, False
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        try: e = json.loads(line)
        except Exception: continue
        if e.get("type") != "stream_event":
            continue
        se = e["event"]; t = se.get("type")
        if t == "content_block_start":
            cb = se.get("content_block", {})
            if cb.get("type") == "tool_use":
                tools.append(cb.get("name"))
                pending = cb.get("name") in ("Skill", "Task")
        elif t == "content_block_delta" and pending:
            d = se.get("delta", {})
            if d.get("type") == "input_json_delta" and TARGET in d.get("partial_json", ""):
                fired = True
    return fired, tools[:6]

CASES = json.load(open(sys.argv[1]))
with cf.ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(run, c["query"]): c for c in CASES}
    rows = []
    for f in cf.as_completed(futs):
        c = futs[f]
        try: fired, tools = f.result()
        except Exception as e: fired, tools = None, [f"ERROR {e}"]
        ok = (fired == c["should_trigger"]) if fired is not None else None
        rows.append((ok, c["should_trigger"], fired, c["query"], tools))
for ok, want, got, q, tools in sorted(rows, key=lambda r: (not r[1], r[0] is not False)):
    print("  %-4s want=%-5s got=%-5s %-46s %s"
          % ("PASS" if ok else "FAIL", want, got, q[:46], tools[:4]))
n_ok = sum(1 for r in rows if r[0])
print("\n合計 %d/%d" % (n_ok, len(rows)))
