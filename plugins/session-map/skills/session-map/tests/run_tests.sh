#!/bin/bash
# run_tests.sh — tests for scripts/session_map.py.
# Fixtures (tests/fixtures/) stand in for ~/.claude, ps and tmux, and the summarizer is a
# shell stub, so nothing here depends on the caller's machine or calls a model.
# The fixture is shaped unlike a typical setup on purpose: a tmux session name with ':' and
# '.', a Japanese cwd, two processes on one conversation in one pane (one stopped), a
# compacted transcript with a broken line, a dead pid and an unreadable registry file.
# 終了コード: 0=全件成功 / 1=失敗あり
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/session_map.py"
FX="$HERE/fixtures"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); }
ng()   { FAIL=$((FAIL+1)); echo "FAIL: $1"; [ -n "${2:-}" ] && printf '%s\n' "$2" | sed 's/^/    /'; }
run()  { OUT="$(python3 "$SCRIPT" --claude-dir "$FX/claude" --ps-file "$FX/ps.txt" --tmux-file "$FX/tmux.txt" \
                --now 1791000000 --cache-dir "$WORK/cache" --screen-file "$FX/screen.txt" "$@" 2>&1)"; RC=$?; }
has()  { printf '%s\n' "$OUT" | grep -qF -- "$1"; }
expect_rc()  { [ "$RC" -eq "$1" ] && ok || ng "$2: exit $RC (want $1)" "$OUT"; }
expect_has() { has "$1" && ok || ng "$2: missing '$1'" "$OUT"; }
expect_not() { has "$1" && ng "$2: unexpected '$1'" "$OUT" || ok; }

# 1. Plain listing: tmux tree, placement outside tmux, flags, stale records.
run
expect_rc 0 "list"
expect_has "動いている claude 4（remote-control 1 / terminal 1 / tmux 2）  終了済みの記録 1" "list"
expect_has "tmux work: main.1  (接続中 1、claude 以外のペイン 1)" "list: session name with ':' and '.'"
expect_has "  work: main.1:2.0  editor  %7" "list: pane line"
expect_has "! 入力待ち（approve Bash）" "list: waiting"
expect_has "一時停止中（Ctrl-Z）" "list: stopped process"
expect_has "同じペインに claude が2個" "list: two claude in one pane"
expect_has "同じ会話を2個のプロセスが開いている" "list: same sessionId twice"
expect_has "tmux の外の端末" "list: terminal group"
expect_has "Remote Control から起動" "list: remote-control group"
expect_has "57日更新なし / 会話ログなし" "list: idle and no transcript"
expect_has "題名: 第3章の改訂" "list: title from transcript"
expect_has "直近の指示: サーバの証明書の期限を確認して" "list: last ask when no last-prompt record"
expect_has "終了済み（記録だけ残っている）: gone(pid 105)" "list: dead pid"
expect_not "pid 999" "list: non-claude process"
# The waiting process sorts before the stopped one in the same pane.
first="$(printf '%s\n' "$OUT" | grep -n '報告書の改訂  \[' | head -1 | cut -d: -f1)"
second="$(printf '%s\n' "$OUT" | grep -n '報告書の改訂-old' | head -1 | cut -d: -f1)"
[ -n "$first" ] && [ -n "$second" ] && [ "$first" -lt "$second" ] && ok || ng "list: running before stopped" "$OUT"

# 2. Summaries: material reaches the summarizer, noise does not, one call per conversation.
CALLS="$WORK/calls"; DUMP="$WORK/material"
# The stub misbehaves like a real cheap model: a preamble, markdown bold, a missing line.
export SESSION_MAP_SUMMARIZER="cat >> '$DUMP'; echo x >> '$CALLS'; printf '前置きの一文です。\\n目的: stub-summary\\n**いま**: working\\n待ち: なし\\n'"
run --summarize
expect_rc 0 "summarize"
expect_has "目的: stub-summary" "summarize"
expect_has "いま: working" "summarize: bold key normalized"
expect_has "状態: （要約に無し）" "summarize: missing line filled"
expect_not "前置きの一文" "summarize: preamble dropped"
expect_has "（pid 101 と同じ会話。要約はそちら）" "summarize: second process points at the first"
[ "$(printf '%s\n' "$OUT" | grep -c 'stub-summary')" -eq 2 ] && ok || ng "summarize: want 2 summaries shown" "$OUT"
[ "$(wc -l < "$CALLS")" -eq 2 ] && ok || ng "summarize: want 2 calls (one per conversation), got $(wc -l < "$CALLS")"
M="$(cat "$DUMP")"
for want in "第3章の報告書を改訂して" "図4もお願い" "図4を差し替え、コミットしてプッシュしました。" \
            "/srv/work/レポート/ch3.md" "git commit -m 'ch3: 図を差し替え' && git push"; do
  printf '%s' "$M" | grep -qF -- "$want" && ok || ng "material: missing '$want'" "$M"
done
# The waiting session gets its screen and the end of a long reply (where the question is).
for want in "SCREEN-MARK" "QUESTION-AT-END どちらで進めますか？"; do
  printf '%s' "$M" | grep -qF -- "$want" && ok || ng "material: missing '$want'" "$(printf '%s' "$M" | tail -c 600)"
done
[ "$(printf '%s' "$M" | grep -cF 'SCREEN-MARK')" -eq 1 ] && ok || ng "material: screen only for the waiting session"
for bad in "SECRET-COMPACT" "SECRET-PREFIX" "SIDECHAIN-ASK" "tool_result"; do
  printf '%s' "$M" | grep -qF -- "$bad" && ng "material: leaked '$bad'" "$M" || ok
done

# 3. Cache: a second run with unchanged transcripts makes no call.
: > "$CALLS"
run --summarize
expect_rc 0 "cache"
expect_has "目的: stub-summary" "cache"
[ ! -s "$CALLS" ] && ok || ng "cache: summarizer called again"
[ "$(stat -c %a "$WORK/cache")" = "700" ] && ok || ng "cache: dir mode $(stat -c %a "$WORK/cache")"
# An entry cached in an older format is normalized on read, without a new call.
for c in "$WORK"/cache/*.json; do
  python3 -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["summary"]="(前置き)\n"+d["summary"]; json.dump(d,open(p,"w"),ensure_ascii=False)' "$c"
done
run --summarize
expect_not "(前置き)" "cache: old entry normalized"
[ ! -s "$CALLS" ] && ok || ng "cache: normalization caused a call"

# 4. A failing summarizer is reported per session and makes the exit code 1.
export SESSION_MAP_SUMMARIZER="echo boom >&2; exit 3"
run --summarize --no-cache
expect_rc 1 "summarizer failure"
expect_has "(要約に失敗 (exit 3): boom)" "summarizer failure"

# 4b. Output that ignores the format entirely is an error, not a summary.
export SESSION_MAP_SUMMARIZER="echo 'I cannot help with that.'"
run --summarize --no-cache
expect_rc 1 "unformatted output"
expect_has "要約の形式が崩れている: I cannot help with that." "unformatted output"

# 5. JSON output and --session selection by name, pid and pane.
unset SESSION_MAP_SUMMARIZER
run --json --session ops-check
expect_rc 0 "json"
printf '%s' "$OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert [s["pid"] for s in d["live"]]==[103]'  2>/dev/null \
  && ok || ng "json: --session by name" "$OUT"
run --json --session %7
printf '%s' "$OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert sorted(s["pid"] for s in d["live"])==[101,102]'  2>/dev/null \
  && ok || ng "json: --session by pane" "$OUT"

# 6. Preconditions and usage.
OUT="$(python3 "$SCRIPT" --claude-dir "$WORK/nowhere" 2>&1)"; RC=$?
expect_rc 2 "no sessions directory"
expect_has "sessions がありません" "no sessions directory"
run --session no-such-session
expect_rc 2 "no match"
run --deep
expect_rc 2 "--deep without --session"

echo "session-map tests: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
