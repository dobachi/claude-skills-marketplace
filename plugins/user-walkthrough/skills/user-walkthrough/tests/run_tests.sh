#!/bin/bash
# run_tests.sh — three-direction harness for the bundled scripts
#   clean → 0 / defect-injected → 1 (with the expected message) / precondition missing → 2
#
# Covers check_report.py, audit_walk.py, walk_sandbox.sh (check/exec; skipped with a note
# if bubblewrap is absent) and walk_driver.py's client side. walk_driver.py's server needs
# Playwright and a browser, so it is exercised by the eval walk, not here.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/../scripts"
FX="$HERE/fixtures"
AFX="$FX/audit"
pass=0; fail=0

run() {  # run <want-exit> <label> <pattern|""> -- cmd...
  local want="$1" label="$2" pat="$3" out rc; shift 4
  out=$("$@" 2>&1); rc=$?
  if [ "$rc" -ne "$want" ]; then
    echo "FAIL $label: exit $rc, want $want"; printf '%s\n' "$out" | sed 's/^/     /' | head -8
    fail=$((fail+1)); return
  fi
  if [ -n "$pat" ] && ! printf '%s\n' "$out" | grep -q -- "$pat"; then
    echo "FAIL $label: exit ok but output lacks '$pat'"; printf '%s\n' "$out" | sed 's/^/     /' | head -8
    fail=$((fail+1)); return
  fi
  echo "ok   $label → $rc"; pass=$((pass+1))
}
report() { run "$1" "check_report $(basename "$2")" "${3:-}" -- python3 "$SCRIPTS/check_report.py" "$2"; }
audit() {  # audit <want> <transcript> <pattern> [log-dir]
  run "$1" "audit_walk $(basename "$2")" "$3" -- python3 "$SCRIPTS/audit_walk.py" \
    --policy "$AFX/policy.json" --log "${4:-$AFX/log_empty}" --work /work/walk --transcript "$2"
}

echo "== check_report.py"
report 0 "$FX/clean_ja.md"          "2 finding"
report 0 "$FX/clean_en_none.md"     "0 finding"
report 0 "$FX/clean_en_crlf.md"     "2 finding"
report 0 "$FX/clean_plain_labels.md" "2 finding"
report 1 "$FX/defect_missing_evidence.md"       "missing or empty Evidence"
report 1 "$FX/defect_plain_labels_tool_step.md" "walk_driver.py"
report 1 "$FX/defect_empty_evidence.md"         "missing or empty Evidence"
report 1 "$FX/defect_speculative.md"            "speculative ('might')"
report 1 "$FX/defect_speculative_ja.md"         "speculative ('可能性')"
report 1 "$FX/defect_speculative_ja2.md"        "speculative ('ように見え')"
report 1 "$FX/defect_blocker_static.md"         "Blocker must be observed"
report 1 "$FX/defect_blocker_zero.md"           "Blocker must be observed"
report 1 "$FX/defect_bad_severity.md"           "must start with \[Blocker\]"
report 1 "$FX/defect_no_not_checked.md"         "Not checked"
report 1 "$FX/defect_steps_unnumbered.md"       "no numbered step"
report 1 "$FX/defect_steps_tool_command.md"     "walk_driver.py"
report 1 "$FX/defect_steps_selector.md"         "#cart-remove-1"
report 1 "$FX/defect_expected_equals_actual.md" "identical"
report 1 "$FX/defect_repro_unrecognized.md"     "is not n/m"
report 2 "$FX/missing_findings_section.md"      "not a walkthrough report"
report 2 "$FX/does_not_exist.md"                "no such file"
run 2 "check_report (no args)" "" -- python3 "$SCRIPTS/check_report.py"

echo "== audit_walk.py"
audit 0 "$AFX/clean_claude.jsonl"            "clean — 0 attempt"
audit 0 "$AFX/clean_generic.jsonl"           "clean — 2 attempt"
audit 0 "$AFX/attempt_only_claude.jsonl"     "ATTEMPT   call 8 Bash"
audit 0 "$AFX/clean_claude.jsonl"            "walk_driver refused step 3" "$AFX/log_refused"
audit 1 "$AFX/violation_curl.jsonl"          "URL not reachable by a user"
audit 1 "$AFX/violation_read_source.jsonl"   "Read outside the work directory"
audit 1 "$AFX/violation_term.jsonl"          "internal term 'TodoStore'"
audit 1 "$AFX/violation_raw_browser.jsonl"   "raw browser automation"
audit 1 "$AFX/violation_tool.jsonl"          "tool WebFetch"
audit 1 "$AFX/violation_escape_dotdot.jsonl" "looked outside the work directory"
audit 1 "$AFX/violation_generic.jsonl"       "forbidden path /src/acme"
audit 2 "$AFX/empty_claude.jsonl"            "no tool calls"
audit 2 "$AFX/does_not_exist.jsonl"          "no transcript"
run 2 "audit_walk (no policy)" "no policy file" -- python3 "$SCRIPTS/audit_walk.py" \
  --policy "$AFX/nope.json" --log "$AFX/log_empty" --work /w --transcript "$AFX/clean_claude.jsonl"

echo "== walk_driver.py (client)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
run 2 "walk_driver no server" "no browser session" -- env WALK_SOCK="$TMP/none.sock" python3 "$SCRIPTS/walk_driver.py" look
run 2 "walk_driver unknown verb" "" -- python3 "$SCRIPTS/walk_driver.py" evaluate "1+1"
run 2 "walk_driver no css option" "" -- python3 "$SCRIPTS/walk_driver.py" click --selector "#btn"
run 2 "walk_driver serve, log inside work" "outside the walker" -- python3 "$SCRIPTS/walk_driver.py" serve \
  --policy "$AFX/policy.json" --work "$TMP" --log "$TMP/log"

echo "== walk_sandbox.sh"
mkdir -p "$TMP/work" "$TMP/repo/src"
echo "secret source" > "$TMP/repo/src/app.js"
printf '{"forbidden_paths": ["%s"]}\n' "$TMP/repo" > "$TMP/policy.json"
echo '{}' > "$TMP/nopolicy.json"
SB="$SCRIPTS/walk_sandbox.sh"
run 2 "walk_sandbox no args" "" -- bash "$SB"
# The policy is read only after the bwrap check, so without bwrap this exits 2
# for the other reason and the message differs.
if command -v bwrap >/dev/null 2>&1; then
  run 2 "walk_sandbox no forbidden_paths" "no forbidden_paths" -- bash "$SB" check "$TMP/work" "$TMP/nopolicy.json"
fi
if command -v bwrap >/dev/null 2>&1 && bwrap --ro-bind / / true 2>/dev/null; then
  run 0 "walk_sandbox check ok" "no forbidden path is visible" -- bash "$SB" check "$TMP/work" "$TMP/policy.json"
  run 1 "walk_sandbox WALK_RO exposes repo" "REFUSED" -- env WALK_RO="$TMP" bash "$SB" check "$TMP/work" "$TMP/policy.json"
  run 1 "walk_sandbox WALK_RO inside repo" "REFUSED" -- env WALK_RO="$TMP/repo/src" bash "$SB" check "$TMP/work" "$TMP/policy.json"
  # The real thing: inside the sandbox the repo does not exist, home is empty, / is read-only.
  run 0 "walk_sandbox hides the repo" "hidden" -- bash "$SB" exec "$TMP/work" "$TMP/policy.json" -- \
    sh -c "if cat '$TMP/repo/src/app.js' 2>/dev/null; then echo LEAK; exit 1; fi; echo hidden"
  run 0 "walk_sandbox hides home" "empty-home" -- bash "$SB" exec "$TMP/work" "$TMP/policy.json" -- \
    sh -c '[ -z "$(ls -A "$HOME")" ] && echo empty-home'
  # Nothing but the listed trees exists at /. Catches "--ro-bind / /" style widening,
  # which the /tmp-based repo above would not (a tmpfs covers /tmp either way).
  run 0 "walk_sandbox root holds only the allowed trees" "minimal-root" -- bash "$SB" exec "$TMP/work" "$TMP/policy.json" -- \
    sh -c 'for d in /var /root /srv /mnt /media /boot /snap; do [ -e "$d" ] && { echo "visible: $d"; exit 1; }; done; echo minimal-root'
  run 0 "walk_sandbox system read-only" "ro" -- bash "$SB" exec "$TMP/work" "$TMP/policy.json" -- \
    sh -c 'touch /usr/x 2>/dev/null && exit 1; echo ro'
  run 0 "walk_sandbox work writable" "rw" -- bash "$SB" exec "$TMP/work" "$TMP/policy.json" -- \
    sh -c 'touch ok && echo rw'
elif ! command -v bwrap >/dev/null 2>&1; then
  run 2 "walk_sandbox without bwrap refuses" "bubblewrap" -- bash "$SB" check "$TMP/work" "$TMP/policy.json"
  echo "note bubblewrap missing — sandbox isolation tests skipped"
else
  echo "note bubblewrap present but not permitted here (user namespaces?) — isolation tests skipped"
fi

echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
