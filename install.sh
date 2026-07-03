#!/usr/bin/env bash
#
# install.sh — register this marketplace with Claude Code and install every plugin.
#
# Usage (from a checkout of this repo, on any machine with the `claude` CLI):
#   ./install.sh
#
# It registers this marketplace from the local checkout (or refreshes it if already
# registered — local marketplaces are cached at add-time, so a refresh is needed to
# pick up newly added plugins), then installs every plugin under plugins/. The plugin
# list is discovered from the directory tree, so it stays in sync as plugins are added.
#
# Idempotent: re-running refreshes and re-installs. After it finishes, run
# /reload-plugins inside a live Claude Code session to apply immediately; new sessions
# load the plugins automatically.

set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$REPO_DIR/.claude-plugin/marketplace.json"

if ! command -v claude >/dev/null 2>&1; then
  echo "error: 'claude' (Claude Code CLI) not found in PATH." >&2
  exit 1
fi
if [ ! -f "$MANIFEST" ]; then
  echo "error: $MANIFEST not found — run this from a checkout of the marketplace repo." >&2
  exit 1
fi

# Marketplace name = the top-level "name" in the manifest (fallback: dobachi-skills).
MARKET_NAME="$(sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$MANIFEST" | head -1)"
MARKET_NAME="${MARKET_NAME:-dobachi-skills}"

echo "==> Registering marketplace '$MARKET_NAME' from $REPO_DIR"
# Add if new; if it already exists, refresh its cached index from disk.
claude plugin marketplace add "$REPO_DIR" 2>/dev/null \
  || claude plugin marketplace update "$MARKET_NAME"

echo "==> Installing plugins from '$MARKET_NAME'"
installed=0
failed=0
for dir in "$REPO_DIR"/plugins/*/; do
  [ -f "$dir/.claude-plugin/plugin.json" ] || continue
  name="$(basename "$dir")"
  if claude plugin install "$name@$MARKET_NAME"; then
    installed=$((installed + 1))
  else
    echo "  (failed: $name)" >&2
    failed=$((failed + 1))
  fi
done

echo
echo "Done: $installed installed, $failed failed."
echo "In a running Claude Code session, run /reload-plugins to apply now."
echo "New sessions load the plugins automatically."
