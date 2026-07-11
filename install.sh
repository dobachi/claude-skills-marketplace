#!/usr/bin/env bash
#
# install.sh — install this skill marketplace for Claude Code AND other coding agents
# (OpenAI Codex CLI, Gemini CLI, Google Antigravity, …) from a single on-disk source.
#
# Two ways to run:
#
#   1) From a checkout of this repo:
#        ./install.sh
#
#   2) Directly, without cloning (one-liner):
#        curl -fsSL https://raw.githubusercontent.com/dobachi/claude-skills-marketplace/master/install.sh | bash
#
# WHY A SINGLE SOURCE OF TRUTH (SRC_DIR)
# --------------------------------------
# Every skill in this repo already IS a standard Agent Skill directory
# (skills/<name>/SKILL.md + scripts/ + references/), which the current generation of
# coding agents discovers from their own paths:
#   - Claude Code : via this marketplace (source: directory)
#   - Codex CLI   : ~/.agents/skills/<name>                       (OpenAI docs)
#   - Gemini CLI  : ~/.gemini/skills/<name>                       (Google docs; ~/.agents/skills alias too)
#   - Antigravity : ~/.gemini/antigravity-cli/skills/<name> (CLI) or ~/.gemini/config/skills (IDE) — opt-in
# So "porting" is not a format conversion — it is pointing every agent at ONE copy of
# the skills. This script resolves that one copy (SRC_DIR) and makes Claude Code read
# it AND symlinks it into the other agents' skill dirs, so a single `git pull` updates
# all of them.
#
# SRC_DIR resolution:
#   - checkout mode : SRC_DIR = the checkout you ran ./install.sh from
#   - one-liner mode: SRC_DIR = a neutral clone at
#                     ${XDG_DATA_HOME:-~/.local/share}/agent-skills/dobachi-skills
#     (NOT Claude's private plugin cache — so other agents don't couple to it and the
#      links survive removing the Claude plugin).
#
# SAFE RE-REGISTRATION (no silent last-writer-wins):
#   `claude plugin marketplace add` on an existing name overwrites its source and leaves
#   the old clone behind as <name>.bak. Running checkout mode and one-liner mode at
#   different times would silently flip which copy every agent reads, and drift them.
#   To avoid that, this script DETECTS the currently registered source and:
#     - same as SRC_DIR                -> no-op (idempotent)
#     - a GitHub source                -> upgrades it to the directory SRC_DIR (safe)
#     - a DIFFERENT healthy directory  -> RECONCILES: keeps the existing one and points
#                                         the agents there too (warns; use --force to
#                                         switch, or answer the prompt on a TTY)
#     - a broken/missing source        -> migrates to SRC_DIR
#   `--force` always switches to this run's SRC_DIR and cleans up the stale copy.
#
# Flags:
#   --status        show what every agent currently points at, then exit (no changes)
#   --force         switch all agents to THIS run's SRC_DIR, overriding a different
#                   existing source; clean up stale .bak clones and stale symlinks
#   --no-agents     only (re)register the Claude Code marketplace; skip other agents
#   --extra-dir DIR link the skills into an ADDITIONAL discovery dir too (repeatable).
#                   For agents not covered by the defaults, e.g. the Antigravity IDE:
#                   --extra-dir ~/.gemini/config/skills
#   --unlink        remove the symlinks this script created from other agents, then exit
#   -h, --help      this help
#
# Idempotent. Needs: claude (for the Claude side), git (one-liner mode), and python3 or
# jq (to read the existing registration; without them, detection is skipped and the run
# behaves like --force with a warning).

set -uo pipefail

REPO_SLUG="dobachi/claude-skills-marketplace"
REPO_URL="https://github.com/${REPO_SLUG}.git"
MARKET_NAME="dobachi-skills"   # fixed key = marketplace.json "name"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
KM_JSON="$CLAUDE_DIR/plugins/known_marketplaces.json"
MARKETPLACES_DIR="$CLAUDE_DIR/plugins/marketplaces"
NEUTRAL_SRC="${XDG_DATA_HOME:-$HOME/.local/share}/agent-skills/dobachi-skills"

# Where other agents discover GLOBAL skills. Two dirs cover every agent we know of, so
# no agent is special-cased — we just link both by default (paths per official docs,
# cross-checked against installed code on this machine):
#   - ~/.agents/skills : Codex CLI (OpenAI docs), Gemini CLI (alias), Antigravity CLI 1.0.x
#                        (verified empirically with `agy` -> reads ~/.agents/skills)
#   - ~/.gemini/skills : Gemini CLI native path (Google docs; GEMINI_DIR=".gemini")
# Agents that read a *different* dir (e.g. the Antigravity IDE at ~/.gemini/config/skills)
# are handled uniformly via --extra-dir, not a per-agent flag.
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
GEMINI_SKILLS_DIR="$HOME/.gemini/skills"
DEFAULT_BASES=("$AGENTS_SKILLS_DIR" "$GEMINI_SKILLS_DIR")

FORCE=0
DO_STATUS=0
LINK_AGENTS=1
DO_UNLINK=0
EXTRA_DIRS=()

# ---- tiny helpers ----------------------------------------------------------
c_bold=$'\033[1m'; c_dim=$'\033[2m'; c_red=$'\033[31m'; c_yel=$'\033[33m'; c_grn=$'\033[32m'; c_off=$'\033[0m'
[ -t 1 ] || { c_bold=""; c_dim=""; c_red=""; c_yel=""; c_grn=""; c_off=""; }
log()  { printf '%s\n' "$*"; }
info() { printf '==> %s\n' "$*"; }
warn() { printf '%swarn:%s %s\n' "$c_yel" "$c_off" "$*" >&2; }
err()  { printf '%serror:%s %s\n' "$c_red" "$c_off" "$*" >&2; }
die()  { err "$*"; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

# Print the leading comment block (everything from line 2 up to the first non-# line).
usage() { awk 'NR==1{next} /^#/{sub(/^# ?/,"");print;next} {exit}' "$0"; }

# ---- flag parsing ----------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --status)      DO_STATUS=1 ;;
    --force)       FORCE=1 ;;
    --no-agents)   LINK_AGENTS=0 ;;
    --extra-dir)   shift; [ $# -gt 0 ] || die "--extra-dir needs a path"; EXTRA_DIRS+=("$1") ;;
    --extra-dir=*) EXTRA_DIRS+=("${1#*=}") ;;
    --unlink)      DO_UNLINK=1 ;;
    -h|--help)     usage; exit 0 ;;
    *)             die "unknown option: $1 (try --help)" ;;
  esac
  shift
done

# All agent discovery dirs this run manages: the defaults plus any --extra-dir.
ALL_BASES=("${DEFAULT_BASES[@]}" ${EXTRA_DIRS[@]+"${EXTRA_DIRS[@]}"})

have claude || die "'claude' (Claude Code CLI) not found in PATH."

# ---- discover the checkout we might be running from ------------------------
# In one-liner mode BASH_SOURCE[0] is not a real file, so this stays empty.
CHECKOUT_DIR=""
SRC="${BASH_SOURCE[0]:-}"
if [ -n "$SRC" ] && [ -f "$SRC" ]; then
  d="$(cd "$(dirname "$SRC")" && pwd)"
  [ -f "$d/.claude-plugin/marketplace.json" ] && CHECKOUT_DIR="$d"
fi

# A directory is a usable skill source if it carries the marketplace manifest and at
# least one skill.
dir_is_healthy_src() {
  local d="$1"
  [ -n "$d" ] && [ -f "$d/.claude-plugin/marketplace.json" ] || return 1
  local first
  first="$(find "$d/plugins" -name SKILL.md -print -quit 2>/dev/null)"
  [ -n "$first" ]
}

# Read the directory path Claude currently has registered for MARKET_NAME.
# Prints the path for a `directory` source; prints "github:<installLocation>" for a
# github source; prints nothing if unregistered or undetectable.
read_registered_source() {
  [ -f "$KM_JSON" ] || return 0
  if have python3; then
    python3 - "$KM_JSON" "$MARKET_NAME" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
e = d.get(sys.argv[2]) or {}
s = e.get("source", {})
kind = s.get("source")
if kind == "directory":
    print(s.get("path", ""))
elif kind == "github":
    print("github:" + (e.get("installLocation", "")))
PY
  elif have jq; then
    jq -r --arg n "$MARKET_NAME" '
      (.[$n] // empty) as $e
      | ($e.source // {}) as $s
      | if $s.source=="directory" then ($s.path // "")
        elif $s.source=="github" then "github:"+($e.installLocation // "")
        else empty end' "$KM_JSON" 2>/dev/null
  fi
}

# List of our skill names (basenames of skills/<name>) for a given source dir.
skill_names_in() {
  local d="$1"
  [ -d "$d/plugins" ] || return 0
  for s in "$d"/plugins/*/skills/*/; do
    [ -f "$s/SKILL.md" ] && basename "${s%/}"
  done
}

# ---- --unlink: remove our symlinks, then exit ------------------------------
unlink_all() {
  local src="${CHECKOUT_DIR:-$NEUTRAL_SRC}" removed=0
  # Names come from whatever source we can see; fall back to "any symlink in the agent
  # dir that resolves into a *claude-skills-marketplace* / neutral / checkout tree".
  local -a names=()
  if dir_is_healthy_src "$src"; then
    while IFS= read -r n; do names+=("$n"); done < <(skill_names_in "$src")
  fi
  for base in "${ALL_BASES[@]}"; do
    [ -d "$base" ] || continue
    for dst in "$base"/*; do
      [ -L "$dst" ] || continue
      local tgt; tgt="$(readlink -f "$dst" 2>/dev/null || true)"
      case "$tgt" in
        *"/claude-skills-marketplace/"*|"$NEUTRAL_SRC"/*|"${CHECKOUT_DIR:-__none__}"/*)
          rm -f "$dst"; info "unlinked $dst"; removed=$((removed+1)) ;;
      esac
    done
  done
  log "Removed $removed symlink(s). (Claude Code marketplace left intact; remove with: claude plugin marketplace remove $MARKET_NAME)"
}

if [ "$DO_UNLINK" = 1 ]; then
  unlink_all
  exit 0
fi

# ---- --status: report, then exit -------------------------------------------
print_status() {
  local reg; reg="$(read_registered_source)"
  log "${c_bold}Marketplace:${c_off} $MARKET_NAME"
  if [ -z "$reg" ]; then
    log "  Claude Code source : ${c_dim}(not registered)${c_off}"
  elif [ "${reg#github:}" != "$reg" ]; then
    log "  Claude Code source : github clone -> ${reg#github:}"
  else
    log "  Claude Code source : directory -> $reg"
    dir_is_healthy_src "$reg" || warn "  registered directory is missing/empty"
  fi
  local src="$reg"; [ "${src#github:}" != "$src" ] && src="${src#github:}"
  dir_is_healthy_src "$src" || src="${CHECKOUT_DIR:-$NEUTRAL_SRC}"
  local total; total="$(skill_names_in "$src" | wc -l | tr -d ' ')"
  log "  Skill source (SRC_DIR guess): $src  (${total} skills)"
  for base in "${ALL_BASES[@]}"; do
    local ok=0 other=0 miss=0
    while IFS= read -r n; do
      [ -n "$n" ] || continue
      local dst="$base/$n"
      if [ -L "$dst" ]; then
        if [ "$(readlink -f "$dst" 2>/dev/null)" = "$(readlink -f "$src/plugins/$n/skills/$n" 2>/dev/null)" ]; then ok=$((ok+1)); else other=$((other+1)); fi
      else
        miss=$((miss+1))
      fi
    done < <(skill_names_in "$src")
    log "  $base : ${c_grn}${ok} linked${c_off}, ${other} elsewhere, ${miss} missing"
  done
  # Orphan .bak clones Claude left behind.
  if [ -d "$MARKETPLACES_DIR" ]; then
    for b in "$MARKETPLACES_DIR"/${MARKET_NAME}.bak; do
      [ -e "$b" ] && warn "orphan clone (safe to delete): $b"
    done
  fi
}

if [ "$DO_STATUS" = 1 ]; then
  print_status
  exit 0
fi

# ---- resolve SRC_DIR (the single source of truth) --------------------------
# desired_dir = what THIS run would install: the checkout, or the neutral clone.
desired_dir="${CHECKOUT_DIR:-$NEUTRAL_SRC}"
registered="$(read_registered_source)"
detect_ok=1; { have python3 || have jq; } || detect_ok=0

SRC_DIR=""
migrate_reason=""

decide_src() {
  # No detection tool: behave like --force with a warning.
  if [ "$detect_ok" = 0 ] && [ -z "$registered" ]; then
    warn "cannot read existing registration (need python3 or jq); proceeding as if new."
    SRC_DIR="$desired_dir"; migrate_reason="fresh (undetectable)"; return
  fi
  # Nothing registered yet.
  if [ -z "$registered" ]; then
    SRC_DIR="$desired_dir"; migrate_reason="new registration"; return
  fi
  # Registered as a GitHub source (old style / Claude's private cache): upgrade to the
  # directory SRC_DIR. Strictly better, non-destructive to user data.
  if [ "${registered#github:}" != "$registered" ]; then
    SRC_DIR="$desired_dir"; migrate_reason="upgrading github source to directory"; return
  fi
  # Registered as a directory.
  local reg_path="$registered"
  if [ "$reg_path" = "$desired_dir" ]; then
    SRC_DIR="$desired_dir"; migrate_reason="";  return           # identical -> no-op
  fi
  # Different directory already registered.
  if [ "$FORCE" = 1 ]; then
    SRC_DIR="$desired_dir"; migrate_reason="--force: switching from $reg_path"; return
  fi
  if dir_is_healthy_src "$reg_path"; then
    # Reconcile by default: keep the existing healthy source; point agents there too.
    if [ -t 0 ] && [ -e /dev/tty ]; then
      log "A different skill source is already registered:"
      log "    existing : $reg_path"
      log "    this run : $desired_dir"
      printf 'Switch every agent to THIS run (%s)? [y/N] ' "$desired_dir" >/dev/tty
      local ans=""; read -r ans </dev/tty || ans=""
      case "$ans" in
        y|Y|yes|YES) SRC_DIR="$desired_dir"; migrate_reason="user chose to switch from $reg_path" ;;
        *)           SRC_DIR="$reg_path";    migrate_reason="user kept existing source" ;;
      esac
    else
      SRC_DIR="$reg_path"
      warn "keeping existing source: $reg_path"
      warn "  (this run's $desired_dir was NOT registered; re-run with --force to switch)"
      migrate_reason="reconciled to existing source"
    fi
    return
  fi
  # Existing directory is broken/empty -> migrate to desired.
  SRC_DIR="$desired_dir"; migrate_reason="existing source is broken ($reg_path); migrating"
}
decide_src

# ---- make sure SRC_DIR physically exists -----------------------------------
if [ "$SRC_DIR" = "$NEUTRAL_SRC" ] && [ -z "$CHECKOUT_DIR" ]; then
  have git || die "one-liner mode needs 'git' to create the neutral clone at $NEUTRAL_SRC"
  if [ -d "$NEUTRAL_SRC/.git" ]; then
    info "Updating neutral clone: $NEUTRAL_SRC"
    git -C "$NEUTRAL_SRC" pull --ff-only --quiet || warn "git pull failed; using existing clone as-is"
  else
    info "Cloning into neutral source: $NEUTRAL_SRC"
    mkdir -p "$(dirname "$NEUTRAL_SRC")"
    git clone --depth 1 --quiet "$REPO_URL" "$NEUTRAL_SRC" || die "git clone failed"
  fi
fi
dir_is_healthy_src "$SRC_DIR" || die "resolved skill source is not usable: $SRC_DIR"
[ -n "$migrate_reason" ] && info "Source: $SRC_DIR ${c_dim}($migrate_reason)${c_off}" || info "Source: $SRC_DIR"

# ---- (re)register the Claude Code marketplace from SRC_DIR ------------------
info "Registering marketplace '$MARKET_NAME' with Claude Code from $SRC_DIR"
# add succeeds and replaces the source when re-run; if the CLI refuses (already present
# with same source), fall back to a plain index refresh.
claude plugin marketplace add "$SRC_DIR" 2>/dev/null \
  || claude plugin marketplace update "$MARKET_NAME" 2>/dev/null \
  || warn "could not (re)register marketplace; is Claude Code healthy?"

# Clean the stale clone Claude leaves behind after a source switch.
if [ -n "$migrate_reason" ] && [ -d "$MARKETPLACES_DIR/${MARKET_NAME}.bak" ]; then
  rm -rf "$MARKETPLACES_DIR/${MARKET_NAME}.bak" && info "removed stale clone ${MARKET_NAME}.bak"
fi

# ---- install / update every plugin -----------------------------------------
info "Installing / updating plugins from '$MARKET_NAME'"
INSTALLED_LIST="$(claude plugin list 2>/dev/null || true)"
is_installed() { printf '%s\n' "$INSTALLED_LIST" | grep -Fq "$1@$MARKET_NAME"; }
get_names() { for d in "$SRC_DIR"/plugins/*/; do [ -f "$d/.claude-plugin/plugin.json" ] && basename "$d"; done; }

installed=0; updated=0; failed=0
while IFS= read -r name; do
  [ -n "$name" ] || continue
  if is_installed "$name"; then
    if claude plugin update "$name@$MARKET_NAME"; then updated=$((updated+1)); else warn "update failed: $name"; failed=$((failed+1)); fi
  else
    if claude plugin install "$name@$MARKET_NAME"; then installed=$((installed+1)); else warn "install failed: $name"; failed=$((failed+1)); fi
  fi
done < <(get_names)
log "Claude Code: $installed installed, $updated updated, $failed failed."

# ---- link SRC_DIR into the other agents ------------------------------------
# Non-destructive: only ever creates/repoints symlinks we manage; never touches real
# files/dirs already sitting in an agent's skills folder (e.g. ~/.agents/skills/find-skills).
link_one() {
  local target="${1%/}" dst="$2"
  if [ -L "$dst" ]; then
    [ "$(readlink -f "$dst" 2>/dev/null)" = "$(readlink -f "$target")" ] && { LN_OK=$((LN_OK+1)); return; }
    ln -sfn "$target" "$dst"; LN_RELINK=$((LN_RELINK+1))
  elif [ -e "$dst" ]; then
    warn "skip (exists, not our symlink): $dst"; LN_SKIP=$((LN_SKIP+1))
  else
    ln -s "$target" "$dst"; LN_NEW=$((LN_NEW+1))
  fi
}

link_into() {
  local base="$1"
  mkdir -p "$base" || { warn "cannot create $base"; return; }
  LN_NEW=0; LN_RELINK=0; LN_OK=0; LN_SKIP=0
  local n
  while IFS= read -r n; do
    [ -n "$n" ] || continue
    link_one "$SRC_DIR/plugins/$n/skills/$n" "$base/$n"
  done < <(skill_names_in "$SRC_DIR")
  log "  $base : ${c_grn}${LN_NEW} new${c_off}, ${LN_RELINK} repointed, ${LN_OK} already-ok, ${LN_SKIP} skipped"
}

if [ "$LINK_AGENTS" = 1 ]; then
  info "Linking skills into other agents' discovery dirs"
  for base in "${ALL_BASES[@]}"; do link_into "$base"; done
else
  log "  (--no-agents: other agents not linked)"
fi

# ---- final word ------------------------------------------------------------
log ""
log "${c_bold}Done.${c_off} All agents point at: $SRC_DIR"
log "  Claude Code : run /reload-plugins in a live session (new sessions auto-load)."
log "  Codex / Gemini CLI : skills available from ~/.agents/skills (restart the agent if it caches)."
log "  Inspect anytime : ./install.sh --status"
