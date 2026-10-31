#!/bin/bash
# run_tests.sh — three-direction tests for scripts/review_sheet.py.
# Fixtures: tests/fixtures/ (pandoc-built deck.pptx, report.docx, report-ja.docx with Japanese
# Word style ids, notes.md, not-a-doc.txt). Sheets are generated into a temp dir at run time.
# 終了コード: 0=全件成功 / 1=失敗あり
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
RS="$HERE/../scripts/review_sheet.py"
FX="$HERE/fixtures"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK" || exit 1

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); }
ng()   { FAIL=$((FAIL+1)); echo "FAIL: $1"; [ -n "${2:-}" ] && printf '%s\n' "$2" | sed 's/^/    /'; }
run()  { OUT="$(python3 -I "$RS" "$@" 2>&1)"; RC=$?; }
has()  { printf '%s\n' "$OUT" | grep -qF -- "$1"; }
fhas() { grep -qF -- "$2" "$1"; }
expect_rc()   { [ "$RC" -eq "$1" ] && ok || ng "$2: exit $RC (want $1)" "$OUT"; }
expect_has()  { has "$1" && ok || ng "$2: missing '$1'" "$OUT"; }
expect_not()  { has "$1" && ng "$2: unexpected '$1'" "$OUT" || ok; }
expect_fhas() { fhas "$1" "$2" && ok || ng "$3: file lacks '$2'" "$(cat "$1")"; }
expect_fnot() { fhas "$1" "$2" && ng "$3: file has '$2'" "$(cat "$1")" || ok; }

cp "$FX/deck.pptx" "$FX/report.docx" "$FX/report-ja.docx" "$FX/notes.md" "$FX/not-a-doc.txt" .

# ---- new: one artifact per kind ------------------------------------------------------
run new deck.pptx --out s-pptx.md
expect_rc 0 "new pptx"
expect_fhas s-pptx.md "<!-- loc: G -->" "pptx: global section"
expect_fhas s-pptx.md "## p.2 要旨 <!-- loc: S2 -->" "pptx: slide title as location"
expect_fhas s-pptx.md "> 設計 | 完了" "pptx: table row in excerpt"
expect_fhas s-pptx.md "units: 4" "pptx: unit count"

run new report.docx --out s-docx.md
expect_rc 0 "new docx (pandoc ids)"
expect_fhas s-docx.md "1. エグゼクティブサマリ <!-- loc: H" "docx: level-1 heading is a location"
expect_fhas s-docx.md "> - 1.1 結論" "docx: level-2 heading folded into excerpt"
grep -c '<!-- loc: H' s-docx.md | grep -qx 3 && ok || ng "docx: want 3 heading locations" "$(grep 'loc: H' s-docx.md)"

run new report-ja.docx --out s-docx-ja.md
expect_rc 0 "new docx (Japanese Word style ids)"
diff <(grep 'loc: ' s-docx.md) <(grep 'loc: ' s-docx-ja.md) >/dev/null && ok || ng "docx-ja: locations differ from pandoc-id version" "$(grep 'loc: ' s-docx-ja.md)"

run new report.docx --out s-docx-d2.md --depth 2
grep -c '<!-- loc: H' s-docx-d2.md | grep -qx 5 && ok || ng "docx --depth 2: want 5 locations" "$(grep 'loc: H' s-docx-d2.md)"

run new notes.md --out s-md.md
expect_rc 0 "new md"
expect_fhas s-md.md "冒頭（表紙・目次） <!-- loc: H0 -->" "md: text before first heading"
expect_fnot s-md.md "これは見出しではない <!-- loc" "md: heading inside a code fence ignored"
expect_fhas s-md.md "## 方針 <!-- loc: H2 -->" "md: headings numbered in order"

run new deck.pptx notes.md --out s-multi.md --header "情報区分: 社外秘" --lang en
expect_rc 0 "new multi"
expect_fhas s-multi.md "## A1. deck.pptx <!-- art: A1 -->" "multi: artifact section"
expect_fhas s-multi.md "<!-- loc: A2.H1 -->" "multi: prefixed location ids"
expect_fhas s-multi.md "情報区分: 社外秘" "multi: header line kept"
expect_fhas s-multi.md "# Review sheet (round 1)" "multi: --lang en"

run new deck.pptx --out s-pptx.md;                 expect_rc 1 "new: refuses to overwrite without --force"
run new deck.pptx --out s-pptx.md --force;         expect_rc 0 "new: --force overwrites"

# ---- new: preconditions -----------------------------------------------------------------
run new not-a-doc.txt --out x.md;   expect_rc 2 "new: unsupported type";   expect_has "unsupported artifact type" "new txt"
run new missing.pptx --out x.md;    expect_rc 2 "new: missing file"
cp not-a-doc.txt fake.pptx; run new fake.pptx --out x.md; expect_rc 2 "new: txt renamed to .pptx is rejected"
run check notes.md;                 expect_rc 2 "check: a plain markdown file is not a sheet"
run check s-pptx.md extra;          expect_rc 2 "check: usage error"
run resolve s-pptx.md S1-1;         expect_rc 2 "resolve: --status required"

# ---- check / ingest on a clean sheet ------------------------------------------------------
run check s-pptx.md
expect_rc 0 "check: fresh sheet is clean"
expect_has "open 0, applied 0, declined 0, question 0, blank 5" "check: counts"
run ingest s-pptx.md
expect_rc 0 "ingest: empty sheet"
expect_has "ids assigned: 0" "ingest: nothing to assign"
expect_not "結論、構成、量" "ingest: the italic hint is not a comment"

# ---- reviewer writes comments: checkbox, continuation, bare line, bare list item ----------
python3 - <<'PY'
import pathlib
p = pathlib.Path("s-pptx.md"); s = p.read_text()
s = s.replace("<!-- loc: G -->\n\n*", "<!-- loc: G -->\n\n- [ ] 全体に長い。半分に。\n\n*", 1)
s = s.replace("<!-- loc: S2 -->\n\n> 結論: 計画どおり\n> お願い: 予算の前倒し\n\n- [ ] ",
              "<!-- loc: S2 -->\n\n> 結論: 計画どおり\n> お願い: 予算の前倒し\n\n- [ ] 結論を一文で。\n  理由も添える。\n予算の根拠が弱い\n")
s = s.replace("<!-- loc: S4 -->\n\n> 来月までに検証を終える。\n\n- [ ] ",
              "<!-- loc: S4 -->\n\n> 来月までに検証を終える。\n\n- 日付を入れる\n- [ ] ")
p.write_text(s)
PY
run check s-pptx.md
expect_rc 1 "check: bare lines are findings"
expect_has "comment without a checkbox" "check: bare line finding"
run ingest s-pptx.md
expect_rc 0 "ingest: assigns ids"
expect_has "ids assigned: 4" "ingest: four comments get ids"
expect_has "- G-1: 全体に長い。半分に。" "ingest: global comment listed first"
expect_has "- S2-1: 結論を一文で。 理由も添える。" "ingest: continuation line joined"
expect_has "- S2-2: 予算の根拠が弱い" "ingest: bare paragraph became a comment"
expect_has "- S4-1: 日付を入れる" "ingest: bare list item became a comment"
expect_fhas s-pptx.md "- [ ] S2-2: 予算の根拠が弱い" "ingest: bare line normalized in the sheet"
expect_fhas s-pptx.md "  理由も添える。" "ingest: reviewer text untouched"
run check s-pptx.md;  expect_rc 0 "check: clean after ingest"
run ingest s-pptx.md; expect_has "ids assigned: 0" "ingest: idempotent"
run ingest s-pptx.md --json
expect_rc 0 "ingest --json"
python3 -c 'import json,sys; d=json.loads(sys.stdin.read()); assert d["locations"]["S2"]["items"][0]["id"]=="S2-1"; assert len(d["global"])==1' <<<"$OUT" && ok || ng "ingest --json: structure" "$OUT"

# ---- resolve: mark, reply, log -----------------------------------------------------------
run resolve s-pptx.md S2-1 --status applied --note "p.2 を一文にした" --by worker-a
expect_rc 0 "resolve applied"
expect_fhas s-pptx.md "- [x] S2-1: 結論を一文で。" "resolve: mark rewritten"
expect_fhas s-pptx.md "  - ↳ r1 worker-a: p.2 を一文にした" "resolve: reply line"
expect_fhas review-log.md "| S2-1 | S2 | 結論を一文で。 理由も添える。 | applied | p.2 を一文にした |" "resolve: log row"
run resolve s-pptx.md S2-2 --status question --note "根拠は 3 案ある"
expect_fhas s-pptx.md "- [?] S2-2: 予算の根拠が弱い" "resolve question"
run resolve s-pptx.md G-1 --status declined --note "量は指定どおり"
run resolve s-pptx.md NOPE-1 --status applied
expect_rc 1 "resolve: unknown id is a finding"
# the reply line is placed after the continuation line, not between them
python3 - <<'PY' && echo ORDER_OK
import pathlib,sys
L = pathlib.Path("s-pptx.md").read_text().splitlines()
i = next(k for k,l in enumerate(L) if l.startswith("- [x] S2-1"))
sys.exit(0 if L[i+1] == "  理由も添える。" and L[i+2].startswith("  - ↳") else 1)
PY
[ "${PIPESTATUS[0]}" -eq 0 ] && ok || ng "resolve: reply placed after continuation"
grep -c '^| 2' review-log.md | grep -qx 3 && ok || ng "log: 3 rows" "$(cat review-log.md)"
run check s-pptx.md
expect_has "open 1, applied 1, declined 1, question 1" "check: counts after resolve"

# ---- defect injection: duplicate id, id under the wrong location ---------------------------
sed 's/^- \[ \] S4-1: 日付を入れる/- [ ] S2-1: 日付を入れる/' s-pptx.md > s-dup.md
run check s-dup.md
expect_rc 1 "check: duplicate id"
expect_has "duplicate id S2-1" "check: duplicate reported"
expect_has "sits under location S4" "check: wrong location reported"

# ---- stale artifact ------------------------------------------------------------------------
printf 'x' >> deck.pptx
run check s-pptx.md
expect_rc 1 "check: artifact changed"
expect_has "stale sheet" "check: stale reported"
run ingest s-pptx.md
expect_has "stale:" "ingest: stale warned"

# ---- carry into the next round -------------------------------------------------------------
run new deck.pptx --carry s-pptx.md --out s-r2.md
expect_rc 0 "new --carry"
expect_has "carried from" "carry: reported"
expect_fhas s-r2.md "round: 2" "carry: round incremented"
expect_fhas s-r2.md "- [?] S2-2: 予算の根拠が弱い" "carry: question carried"
expect_fhas s-r2.md "  - ↳ r1: 根拠は 3 案ある" "carry: its reply carried"
expect_fhas s-r2.md "  - ↳ 第1回から持ち越し" "carry: marked"
expect_fhas s-r2.md "- [ ] S4-1: 日付を入れる" "carry: open carried"
expect_fnot s-r2.md "S2-1:" "carry: applied not carried"
expect_fnot s-r2.md "G-1:" "carry: declined not carried"
run check s-r2.md; expect_rc 0 "carry: new sheet is clean"
# a carried comment whose location vanished lands in the global section
run new notes.md --carry s-pptx.md --out s-r2b.md
expect_fhas s-r2b.md "（前回 S2） 予算の根拠が弱い" "carry: orphan goes to global"
python3 - <<'PY' && ok || ng "carry: orphan sits inside the global section"
import pathlib,sys
L = pathlib.Path("s-r2b.md").read_text().splitlines()
g = next(k for k,l in enumerate(L) if "loc: G" in l); h = next(k for k,l in enumerate(L) if k>g and l.startswith("#"))
sys.exit(0 if any("前回 S2" in l for l in L[g:h]) else 1)
PY

# ---- where --------------------------------------------------------------------------------
run where s-r2.md --url-template 'https://{addr}:3000/?file={relpath}'
expect_rc 0 "where"
expect_has "- host: $(hostname)" "where: host"
expect_has "- sheet: $WORK/s-r2.md" "where: absolute sheet path"
expect_has "fude-cli here $WORK/s-r2.md" "where: open command"
expect_has "?file=s-r2.md" "where: url template"
run where s-r2.md --url-template 'https://x/?token={token}'
expect_rc 2 "where: refuses a token in the template"
run where s-pptx.md
expect_has "changed after the sheet" "where: stale flag"

echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
