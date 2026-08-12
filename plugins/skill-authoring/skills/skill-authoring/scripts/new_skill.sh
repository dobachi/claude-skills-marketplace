#!/bin/bash
# new_skill.sh <name> ["one-line description"] — scaffold a plugin in this marketplace.
#
# Creates the layout, plugin.json, a SKILL.md skeleton, and registers the plugin in
# marketplace.json. README rows are PRINTED rather than inserted: they live in a
# category table and only a human knows which category is right.
#
# 終了コード: 0=作成 / 1=既存 / 2=引数エラー
set -u

NAME="${1:-}"
DESC="${2:-One-line description of what this skill does and when to use it.}"
case "$NAME" in
  "" ) echo "usage: new_skill.sh <name> [\"description\"]" >&2; exit 2 ;;
  *[!a-z0-9-]* ) echo "new_skill: name must be lowercase letters, digits and hyphens: $NAME" >&2; exit 2 ;;
  -*|*- ) echo "new_skill: name must not start or end with a hyphen: $NAME" >&2; exit 2 ;;
  *--* ) echo "new_skill: name must not contain consecutive hyphens: $NAME" >&2; exit 2 ;;
esac
case "$NAME" in *anthropic*|*claude*) echo "new_skill: name contains a reserved word (anthropic/claude)" >&2; exit 2;; esac

# Repo root. Search from the CURRENT DIRECTORY first, then from the script.
# When the skill fires, this script runs from the installed plugin cache
# (~/.claude/plugins/cache/...), which has no marketplace above it — but the
# user is standing in the repo. Script-location-first fails in exactly the
# normal case.
find_repo() {
  local d="$1"
  while [ "$d" != "/" ]; do
    [ -f "$d/.claude-plugin/marketplace.json" ] && { printf '%s' "$d"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}
REPO="$(find_repo "$PWD" || find_repo "$(cd "$(dirname "$0")" && pwd)" || true)"
[ -f "${REPO:-/nonexistent}/.claude-plugin/marketplace.json" ] || {
  echo "new_skill: marketplace.json が見つかりません (探した場所: $PWD と $(dirname "$0"))" >&2
  echo "           マーケットプレイスのリポジトリ内で実行してください" >&2; exit 2; }
cd "$REPO" || exit 2

PLUGIN="plugins/$NAME"
[ -e "$PLUGIN" ] && { echo "new_skill: already exists: $PLUGIN" >&2; exit 1; }
SKILL="$PLUGIN/skills/$NAME"
mkdir -p "$PLUGIN/.claude-plugin" "$SKILL/references" "$SKILL/scripts"

python3 - "$NAME" "$DESC" <<'PY'
import json, sys, pathlib
name, desc = sys.argv[1], sys.argv[2]
p = pathlib.Path("plugins")/name/".claude-plugin"/"plugin.json"
p.write_text(json.dumps({"name": name, "description": desc,
                         "version": "0.1.0", "author": {"name": "dobachi"}},
                        ensure_ascii=False, indent=2)
             .replace('"author": {\n    "name": "dobachi"\n  }', '"author": {"name": "dobachi"}') + "\n")
mp = pathlib.Path(".claude-plugin/marketplace.json")
d = json.loads(mp.read_text())
if not any(x.get("name") == name for x in d["plugins"]):
    d["plugins"].append({"name": name, "source": "./plugins/%s" % name, "description": desc})
    mp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print("  marketplace.json に登録した")
else:
    print("  marketplace.json には既にある")
PY

cat > "$SKILL/SKILL.md" <<EOF
---
name: $NAME
description: $DESC
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# ${NAME}

<!-- 書く前に決めること:
     - このスキルが持つ仕事は何か。既存のどのスキルとも重ならないか
     - 失敗の具体例を1つ。それを直せない案は書かない
     - 何を他スキルに渡すか。description にも書く -->

## When it applies

## Rules

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|

## References
EOF

rmdir "$SKILL/references" "$SKILL/scripts" 2>/dev/null
echo "  作成: $SKILL/SKILL.md"
echo
echo "次にやること"
echo "  1. SKILL.md を書く（references/authoring-best-practices.md）"
echo "  2. 下の行を README.md と README_ja.md のカテゴリ表に貼る"
echo "  3. python3 site/scripts/gen_catalog.py"
echo "  4. $(dirname "$0")/release_check.sh $NAME"
echo
echo "README 用の行:"
echo "| **$NAME** | $DESC |"
