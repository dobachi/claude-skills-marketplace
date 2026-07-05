#!/usr/bin/env bash
#
# install.sh — register this marketplace with Claude Code and install every plugin.
#
# Two ways to run:
#
#   1) From a checkout of this repo:
#        ./install.sh
#
#   2) Directly, without cloning (one-liner):
#        curl -fsSL https://raw.githubusercontent.com/dobachi/claude-skills-marketplace/master/install.sh | bash
#
# In checkout mode it registers the marketplace from the local path and installs every
# plugin discovered under plugins/ (dependency-free). In remote (piped) mode it registers
# the marketplace from the GitHub repo and installs every plugin listed in the remote
# marketplace.json — this parse needs `python3` or `jq`.
#
# Idempotent: re-running refreshes the marketplace, installs new plugins, and updates
# already-installed ones to the latest version (a plain re-install would not). After it
# finishes, run
# /reload-plugins inside a live Claude Code session to apply immediately; new sessions
# load the plugins automatically.

set -uo pipefail

REPO_SLUG="dobachi/claude-skills-marketplace"
RAW_BASE="https://raw.githubusercontent.com/${REPO_SLUG}/master"

if ! command -v claude >/dev/null 2>&1; then
  echo "error: 'claude' (Claude Code CLI) not found in PATH." >&2
  exit 1
fi

# Top-level marketplace "name" from a manifest on stdin (dependency-free).
market_name_from() {
  sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}

# Plugin names from a marketplace.json on stdin (remote mode; needs python3 or jq).
list_plugins() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import sys, json; [print(p['name']) for p in json.load(sys.stdin)['plugins']]"
  else
    jq -r '.plugins[].name'
  fi
}

# Are we running from a checkout, or piped from curl (BASH_SOURCE is not a real file)?
SRC="${BASH_SOURCE[0]:-}"
REPO_DIR=""
if [ -n "$SRC" ] && [ -f "$SRC" ]; then
  REPO_DIR="$(cd "$(dirname "$SRC")" && pwd)"
fi

if [ -n "$REPO_DIR" ] && [ -f "$REPO_DIR/.claude-plugin/marketplace.json" ]; then
  MODE="local"
  MANIFEST="$REPO_DIR/.claude-plugin/marketplace.json"
  ADD_SOURCE="$REPO_DIR"
  MARKET_NAME="$(market_name_from < "$MANIFEST")"
  # Discover plugins from the directory tree, so the list stays in sync as plugins are added.
  get_names() { for d in "$REPO_DIR"/plugins/*/; do [ -f "$d/.claude-plugin/plugin.json" ] && basename "$d"; done; }
else
  MODE="remote"
  ADD_SOURCE="$REPO_SLUG"
  if ! command -v python3 >/dev/null 2>&1 && ! command -v jq >/dev/null 2>&1; then
    echo "error: remote mode needs 'python3' or 'jq' to parse marketplace.json." >&2
    exit 1
  fi
  MANIFEST_CONTENT="$(curl -fsSL "$RAW_BASE/.claude-plugin/marketplace.json")" || {
    echo "error: failed to fetch marketplace.json from $RAW_BASE" >&2
    exit 1
  }
  MARKET_NAME="$(printf '%s' "$MANIFEST_CONTENT" | market_name_from)"
  get_names() { printf '%s' "$MANIFEST_CONTENT" | list_plugins; }
fi
MARKET_NAME="${MARKET_NAME:-dobachi-skills}"

echo "==> [$MODE] Registering marketplace '$MARKET_NAME' from $ADD_SOURCE"
# Add if new; if it already exists, refresh its cached index from the source.
claude plugin marketplace add "$ADD_SOURCE" 2>/dev/null \
  || claude plugin marketplace update "$MARKET_NAME"

echo "==> Installing / updating plugins from '$MARKET_NAME'"
# `claude plugin install` no-ops on an already-installed plugin — it will NOT pick up
# a new version. So for plugins already present we call `claude plugin update`, which
# does apply a version bump from the (refreshed) marketplace source. New plugins are
# installed. Snapshot the installed set once; entries look like `name@marketplace`.
INSTALLED_LIST="$(claude plugin list 2>/dev/null || true)"
is_installed() { printf '%s\n' "$INSTALLED_LIST" | grep -Fq "$1@$MARKET_NAME"; }

installed=0
updated=0
failed=0
while IFS= read -r name; do
  [ -n "$name" ] || continue
  if is_installed "$name"; then
    if claude plugin update "$name@$MARKET_NAME"; then
      updated=$((updated + 1))
    else
      echo "  (update failed: $name)" >&2
      failed=$((failed + 1))
    fi
  else
    if claude plugin install "$name@$MARKET_NAME"; then
      installed=$((installed + 1))
    else
      echo "  (install failed: $name)" >&2
      failed=$((failed + 1))
    fi
  fi
done < <(get_names)

echo
echo "Done: $installed installed, $updated updated, $failed failed."
echo "In a running Claude Code session, run /reload-plugins to apply now."
echo "New sessions load the plugins automatically."
