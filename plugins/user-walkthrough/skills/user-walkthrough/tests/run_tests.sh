#!/bin/bash
# run_tests.sh — three-direction harness for scripts/check_report.py
#   clean → 0 / defect-injected → 1 (with the expected message) / precondition missing → 2
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHK="$HERE/../scripts/check_report.py"
FX="$HERE/fixtures"
pass=0; fail=0

expect() {  # expect <exit> <fixture-or-path> [pattern]
  local want="$1" f="$2" pat="${3:-}" out rc
  out=$(python3 "$CHK" "$f" 2>&1); rc=$?
  if [ "$rc" -ne "$want" ]; then
    echo "FAIL $(basename "$f"): exit $rc, want $want"; printf '%s\n' "$out" | sed 's/^/     /'; fail=$((fail+1)); return
  fi
  if [ -n "$pat" ] && ! printf '%s\n' "$out" | grep -q -- "$pat"; then
    echo "FAIL $(basename "$f"): exit ok but output lacks '$pat'"; printf '%s\n' "$out" | sed 's/^/     /'; fail=$((fail+1)); return
  fi
  echo "ok   $(basename "$f") → $rc"; pass=$((pass+1))
}

# clean → 0
expect 0 "$FX/clean_ja.md"          "2 finding"
expect 0 "$FX/clean_en_none.md"     "0 finding"
expect 0 "$FX/clean_en_crlf.md"     "2 finding"

# defect-injected → 1, and for the right reason
expect 1 "$FX/defect_missing_evidence.md"       "missing or empty Evidence"
expect 1 "$FX/defect_empty_evidence.md"         "missing or empty Evidence"
expect 1 "$FX/defect_speculative.md"            "speculative ('might')"
expect 1 "$FX/defect_speculative_ja.md"         "speculative ('可能性')"
expect 1 "$FX/defect_blocker_static.md"         "Blocker must be observed"
expect 1 "$FX/defect_blocker_zero.md"           "Blocker must be observed"
expect 1 "$FX/defect_bad_severity.md"           "must start with \[Blocker\]"
expect 1 "$FX/defect_no_not_checked.md"         "Not checked"
expect 1 "$FX/defect_steps_unnumbered.md"       "no numbered step"
expect 1 "$FX/defect_expected_equals_actual.md" "identical"
expect 1 "$FX/defect_repro_unrecognized.md"     "is not n/m"

# precondition missing → 2
expect 2 "$FX/missing_findings_section.md"      "not a walkthrough report"
expect 2 "$FX/does_not_exist.md"                "no such file"
out=$(python3 "$CHK" 2>&1); rc=$?
if [ $rc -eq 2 ]; then echo "ok   (no args) → 2"; pass=$((pass+1)); else echo "FAIL (no args): exit $rc"; fail=$((fail+1)); fi

echo "passed $pass, failed $fail"
[ "$fail" -eq 0 ]
