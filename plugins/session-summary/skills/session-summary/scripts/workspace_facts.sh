#!/bin/bash
# workspace_facts.sh [--since <rev>] [--dir <path>] — print where the work happened.
#
# Prints facts only, one "key: value" per line, so the summary is written from the
# repository rather than from memory of the conversation. Credentials embedded in
# remote URLs are masked.
#
# 終了コード: 0=出力した（gitでない場所も0） / 2=引数エラー・--since が解決できない
set -u

SINCE=""
DIR="$PWD"
while [ $# -gt 0 ]; do
  case "$1" in
    --since) [ $# -ge 2 ] || { echo "workspace_facts: --since needs a revision" >&2; exit 2; }
             SINCE="$2"; shift 2 ;;
    --dir)   [ $# -ge 2 ] || { echo "workspace_facts: --dir needs a path" >&2; exit 2; }
             DIR="$2"; shift 2 ;;
    -h|--help) echo "usage: workspace_facts.sh [--since <rev>] [--dir <path>]"; exit 0 ;;
    *) echo "workspace_facts: unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -d "$DIR" ] || { echo "workspace_facts: not a directory: $DIR" >&2; exit 2; }
cd "$DIR" || exit 2

echo "cwd: $(pwd -P)"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "git: none"
  exit 0
fi

mask() { sed -E 's#(://)[^/@]+@#\1***@#'; }

ROOT="$(git rev-parse --show-toplevel)"
echo "repo_root: $ROOT"
COMMON="$(cd "$ROOT" && cd "$(git rev-parse --git-common-dir)" && pwd -P)"
GITDIR="$(cd "$(git rev-parse --git-dir)" && pwd -P)"
if [ "$COMMON" != "$GITDIR" ]; then
  echo "worktree: linked (main: $(dirname "$COMMON"))"
else
  echo "worktree: main"
fi

REMOTES="$(git remote)"
if [ -z "$REMOTES" ]; then
  echo "remote: none"
else
  for r in $REMOTES; do
    echo "remote.$r: $(git remote get-url "$r" 2>/dev/null | mask)"
  done
fi

if BR="$(git symbolic-ref --short -q HEAD)"; then
  echo "branch: $BR"
else
  echo "branch: (detached)"
fi

if HEADSHA="$(git rev-parse --short HEAD 2>/dev/null)"; then
  echo "head: $HEADSHA $(git log -1 --format=%s HEAD)"
  if UP="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null)"; then
    set -- $(git rev-list --left-right --count "HEAD...@{u}")
    echo "upstream: $UP (ahead $1, behind $2)"
  else
    echo "upstream: none"
  fi
else
  echo "head: (no commits)"
fi

STATUS="$(git status --porcelain=v1)"
STAGED=$(printf '%s\n' "$STATUS" | grep -c '^[MADRC]')
MODIFIED=$(printf '%s\n' "$STATUS" | grep -c '^.[MD]')
UNTRACKED=$(printf '%s\n' "$STATUS" | grep -c '^??')
echo "worktree_state: staged $STAGED, modified $MODIFIED, untracked $UNTRACKED"
[ -n "$STATUS" ] && printf '%s\n' "$STATUS" | sed 's/^/  /'

if [ -n "$SINCE" ]; then
  git rev-parse --verify -q "$SINCE^{commit}" >/dev/null || {
    echo "workspace_facts: --since does not resolve to a commit: $SINCE" >&2; exit 2; }
  N=$(git rev-list --count "$SINCE..HEAD")
  echo "commits_since $SINCE: $N"
  [ "$N" -gt 0 ] && git log --format='  %h %s' "$SINCE..HEAD"
fi
exit 0
