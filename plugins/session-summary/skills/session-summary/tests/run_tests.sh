#!/bin/bash
# run_tests.sh — tests for scripts/workspace_facts.sh.
# Repositories are built fresh from the steps below on every run, so the fixtures are
# this file itself; nothing depends on the caller's git config or working directory.
# 終了コード: 0=全件成功 / 1=失敗あり
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/workspace_facts.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com
export GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); }
ng()   { FAIL=$((FAIL+1)); echo "FAIL: $1"; [ -n "${2:-}" ] && printf '%s\n' "$2" | sed 's/^/    /'; }
run()  { OUT="$(bash "$SCRIPT" "$@" 2>&1)"; RC=$?; }
has()  { printf '%s\n' "$OUT" | grep -qF -- "$1"; }
expect_rc()  { [ "$RC" -eq "$1" ] && ok || ng "$2: exit $RC (want $1)" "$OUT"; }
expect_has() { has "$1" && ok || ng "$2: missing '$1'" "$OUT"; }
expect_not() { has "$1" && ng "$2: unexpected '$1'" "$OUT" || ok; }

mkrepo() { git init -q -b main "$1" && git -C "$1" commit -q --allow-empty -m "$2"; }

# 1. Not a git repository: facts still printed, exit 0.
mkdir "$WORK/plain"
run --dir "$WORK/plain"
expect_rc 0 "non-git"
expect_has "git: none" "non-git"
expect_has "cwd: $(cd "$WORK/plain" && pwd -P)" "non-git"

# 2. Clean repository, no remote, no upstream.
mkrepo "$WORK/clean" "first commit"
run --dir "$WORK/clean"
expect_rc 0 "clean"
expect_has "branch: main" "clean"
expect_has "worktree: main" "clean"
expect_has "remote: none" "clean"
expect_has "upstream: none" "clean"
expect_has "first commit" "clean"
expect_has "worktree_state: staged 0, modified 0, untracked 0" "clean"

# 3. Dirty: staged, modified and untracked are counted separately.
R="$WORK/dirty"; mkrepo "$R" "base"
echo a > "$R/tracked"; git -C "$R" add tracked; git -C "$R" commit -q -m "add tracked"
echo b >> "$R/tracked"                       # modified, unstaged
echo c > "$R/new-staged"; git -C "$R" add new-staged
echo d > "$R/loose"                          # untracked
run --dir "$R"
expect_has "worktree_state: staged 1, modified 1, untracked 1" "dirty"
expect_has "?? loose" "dirty"

# 4. Credentials in a remote URL are masked; upstream ahead/behind is reported.
R="$WORK/remote"; mkrepo "$WORK/origin-src" "root"
git clone -q "$WORK/origin-src" "$R"
git -C "$R" remote add secret "https://user:tok3n@example.com/o/r.git"
git -C "$R" commit -q --allow-empty -m "local only"
run --dir "$R"
expect_has "remote.secret: https://***@example.com/o/r.git" "remote"
expect_not "tok3n" "remote"
expect_has "upstream: origin/main (ahead 1, behind 0)" "remote"

# 5. Linked worktree is identified with its main repository.
git -C "$WORK/clean" worktree add -q -b side "$WORK/wt"
run --dir "$WORK/wt"
expect_has "worktree: linked (main: $(cd "$WORK/clean" && pwd -P))" "worktree"
expect_has "branch: side" "worktree"

# 6. Detached HEAD.
R="$WORK/detached"; mkrepo "$R" "one"; git -C "$R" commit -q --allow-empty -m "two"
git -C "$R" checkout -q --detach HEAD~1
run --dir "$R"
expect_has "branch: (detached)" "detached"

# 7. Repository with no commits yet.
git init -q -b main "$WORK/empty"
run --dir "$WORK/empty"
expect_rc 0 "empty"
expect_has "head: (no commits)" "empty"

# 8. --since lists the commits made after the given revision.
R="$WORK/since"; mkrepo "$R" "start"; BASE="$(git -C "$R" rev-parse --short HEAD)"
git -C "$R" commit -q --allow-empty -m "session work 1"
git -C "$R" commit -q --allow-empty -m "session work 2"
run --dir "$R" --since "$BASE"
expect_rc 0 "since"
expect_has "commits_since $BASE: 2" "since"
expect_has "session work 2" "since"
expect_not "  $BASE start" "since"

# 9. Usage errors exit 2.
run --dir "$R" --since no-such-rev;   expect_rc 2 "bad --since"
run --since;                          expect_rc 2 "--since without value"
run --dir "$WORK/missing";            expect_rc 2 "missing --dir"
run --bogus;                          expect_rc 2 "unknown arg"

echo "passed $PASS, failed $FAIL"
[ "$FAIL" -eq 0 ]
