#!/usr/bin/env bash
# walk_sandbox.sh — run the walker where the source code does not exist.
#
# The walker sees: a read-only OS (/usr /etc /bin /sbin /lib /lib64), its own work
# directory (read-write), and nothing else. HOME is an empty tmpfs, so ~/src, the repo,
# ~/.ssh, ~/.claude/projects (past transcripts that quote the source) are simply not
# there. /opt, /srv, /mnt, /media, /tmp of the host are not mounted.
#
# Usage:
#   walk_sandbox.sh check  <work> <policy.json>              visibility check only
#   walk_sandbox.sh exec   <work> <policy.json> -- cmd ...   run any command inside
#   walk_sandbox.sh claude <work> <policy.json> <log-dir>    run a Claude Code walker
#
# policy.json fields used here:
#   forbidden_paths   paths that must be invisible (the repo, design docs, …). REQUIRED
#   allowed_commands  product commands the walker may run, e.g. ["acme"] (CLI products)
# The walker's prompt is <work>/briefing.md. The transcript (stream-json) goes to
# <log-dir>/transcript.jsonl, which the walker cannot see.
#
# Env:
#   WALK_RO     extra read-only paths, ':'-separated (checked against forbidden_paths)
#   WALK_MODEL  model for the claude walker (optional)
#
# What this does NOT stop: the network is shared (the agent must reach its API, and
# the product lives on localhost), so a walker that ignores its tool allowlist could
# fetch raw HTML from the app. That layer is the allowlist (claude mode) plus
# audit_walk.py afterwards — not the OS.
#
# Exit codes: 0 ok / 1 refused (a forbidden path would be visible) / 2 usage or
# precondition (no bwrap, missing files) / otherwise the walker's own exit code.
set -u

usage() { sed -n '2,/^set -u/p' "$0" | sed 's/^# \{0,1\}//; /^set -u/d' >&2; exit 2; }
MODE="${1:-}"; WORK="${2:-}"; POLICY="${3:-}"
[ -n "$MODE" ] && [ -n "$WORK" ] && [ -n "$POLICY" ] || usage
case "$MODE" in check|exec|claude) ;; *) usage ;; esac
[ -d "$WORK" ] || { echo "walk_sandbox: no work directory: $WORK" >&2; exit 2; }
[ -f "$POLICY" ] || { echo "walk_sandbox: no policy file: $POLICY" >&2; exit 2; }
command -v bwrap >/dev/null 2>&1 || {
  echo "walk_sandbox: bubblewrap (bwrap) not found — cannot hide the source by OS." >&2
  echo "walk_sandbox: walk without it only if the user accepts, and say so in the report header." >&2
  exit 2; }
WORK="$(cd "$WORK" && pwd -P)"
HOME_DIR="${HOME:?walk_sandbox: HOME is not set}"

# Resolve what will be visible, then refuse if any forbidden path is among it.
SYS_RO=(/usr /etc /bin /sbin /lib /lib64)
EXTRA_RO=()
IFS=':' read -r -a _ro <<< "${WALK_RO:-}"
for d in "${_ro[@]}"; do [ -n "$d" ] && EXTRA_RO+=("$(readlink -f "$d")"); done
CLAUDE_BIN_DIR=""
if [ "$MODE" = claude ]; then
  command -v claude >/dev/null 2>&1 || { echo "walk_sandbox: claude not on PATH" >&2; exit 2; }
  CLAUDE_BIN_DIR="$(dirname "$(readlink -f "$(command -v claude)")")"
  EXTRA_RO+=("$CLAUDE_BIN_DIR")
fi

python3 - "$POLICY" "$WORK" "${SYS_RO[@]}" -- "${EXTRA_RO[@]}" <<'PY'
import json, os, sys
policy_path, work = sys.argv[1], sys.argv[2]
rest = sys.argv[3:]
sep = rest.index("--")
visible = [work] + rest[:sep] + rest[sep + 1:]
try:
    policy = json.load(open(policy_path, encoding="utf-8"))
except ValueError as e:
    print("walk_sandbox: policy is not JSON: %s" % e, file=sys.stderr); sys.exit(2)
forbidden = policy.get("forbidden_paths")
if not forbidden:
    print("walk_sandbox: policy has no forbidden_paths — say what the walker must not see "
          "(at least the repository)", file=sys.stderr); sys.exit(2)
bad = 0
for f in forbidden:
    f = os.path.realpath(os.path.expanduser(f))
    for v in visible:
        v = os.path.realpath(v)
        if f == v or f.startswith(v.rstrip("/") + "/"):
            print("walk_sandbox: REFUSED — forbidden %s would be visible via %s" % (f, v)); bad = 1
        elif v.startswith(f.rstrip("/") + "/"):
            print("walk_sandbox: REFUSED — visible %s is inside forbidden %s" % (v, f)); bad = 1
sys.exit(bad)
PY
rc=$?
[ $rc -eq 0 ] || exit $rc
if [ "$MODE" = check ]; then echo "walk_sandbox: ok — no forbidden path is visible"; exit 0; fi

RESOLV="$(readlink -f /etc/resolv.conf 2>/dev/null || echo /etc/resolv.conf)"
args=(--proc /proc --dev /dev --tmpfs /tmp --tmpfs "$HOME_DIR" --tmpfs /opt
      --ro-bind-try "$RESOLV" "$RESOLV"
      --bind "$WORK" "$WORK" --chdir "$WORK"
      --setenv HOME "$HOME_DIR"
      --unshare-user --unshare-pid --unshare-ipc --die-with-parent --new-session)
for d in "${SYS_RO[@]}"; do args=(--ro-bind-try "$d" "$d" "${args[@]}"); done
for d in "${EXTRA_RO[@]}"; do args+=(--ro-bind-try "$d" "$d"); done

if [ "$MODE" = exec ]; then
  shift 3
  [ "${1:-}" = "--" ] && shift
  [ $# -gt 0 ] || usage
  exec bwrap "${args[@]}" -- "$@"
fi

# ---- claude walker
LOG="${4:-}"
[ -n "$LOG" ] || usage
mkdir -p "$LOG"; LOG="$(cd "$LOG" && pwd -P)"
case "$LOG/" in "$WORK"/*) echo "walk_sandbox: log dir must be outside the work dir" >&2; exit 2;; esac
[ -f "$WORK/briefing.md" ] || { echo "walk_sandbox: $WORK/briefing.md is missing" >&2; exit 2; }
[ -f "$HOME_DIR/.claude/.credentials.json" ] || [ -n "${ANTHROPIC_API_KEY:-}" ] || {
  echo "walk_sandbox: no Claude credentials (~/.claude/.credentials.json or ANTHROPIC_API_KEY)" >&2; exit 2; }

# A config dir holding ONLY the credentials — not ~/.claude, whose projects/ keeps
# past transcripts of this very repository.
CFG="$(mktemp -d "${TMPDIR:-/tmp}/walk-cfg.XXXXXX")"
trap 'rm -rf "$CFG"' EXIT
[ -f "$HOME_DIR/.claude/.credentials.json" ] && install -m 600 "$HOME_DIR/.claude/.credentials.json" "$CFG/"
args+=(--bind "$CFG" "$CFG" --setenv CLAUDE_CONFIG_DIR "$CFG" --setenv PATH "$CLAUDE_BIN_DIR:/usr/bin:/bin")
[ -n "${ANTHROPIC_API_KEY:-}" ] && args+=(--setenv ANTHROPIC_API_KEY "$ANTHROPIC_API_KEY")

allowed=("Bash(python3 walk_driver.py:*)" "Read" "Write" "Glob")
while IFS= read -r c; do
  [ -n "$c" ] && allowed+=("Bash($c:*)" "Bash($c)")
done < <(python3 -c 'import json,sys; [print(c) for c in json.load(open(sys.argv[1])).get("allowed_commands", [])]' "$POLICY")

model=(); [ -n "${WALK_MODEL:-}" ] && model=(--model "$WALK_MODEL")
echo "walk_sandbox: walker starting (transcript: $LOG/transcript.jsonl)" >&2
bwrap "${args[@]}" -- "$CLAUDE_BIN_DIR/$(basename "$(readlink -f "$(command -v claude)")")" \
  -p "$(cat "$WORK/briefing.md")" \
  --output-format stream-json --verbose \
  --permission-mode dontAsk \
  --allowedTools "${allowed[@]}" \
  --disallowedTools WebFetch WebSearch Task Agent \
  --strict-mcp-config \
  "${model[@]}" \
  > "$LOG/transcript.jsonl" 2> "$LOG/walker.stderr"
rc=$?
echo "walk_sandbox: walker exited $rc" >&2
exit $rc
