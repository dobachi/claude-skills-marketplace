#!/bin/bash
# release_check.sh <skill-name> — the pre-commit gate for a skill in this marketplace.
#
# Every check here exists because it was forgotten at least once, and because
# forgetting it produces no visible symptom: a description over the limit still
# loads locally, a stale catalog still renders, an unbumped version still installs
# (just not the new content).
#
# 使い方:   ./release_check.sh <skill-name> [--fix-catalog]
# 終了コード: 0=出荷可 / 1=指摘あり / 2=引数エラー
set -u

NAME="${1:-}"
FIX_CATALOG=0
[ "${2:-}" = "--fix-catalog" ] && FIX_CATALOG=1
if [ -z "$NAME" ]; then
  echo "usage: release_check.sh <skill-name> [--fix-catalog]" >&2
  exit 2
fi

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
if [ ! -f "${REPO:-/nonexistent}/.claude-plugin/marketplace.json" ]; then
  echo "release_check: marketplace.json が見つかりません (探した場所: $PWD と $(dirname "$0"))" >&2
  echo "               マーケットプレイスのリポジトリ内で実行してください" >&2
  exit 2
fi
cd "$REPO" || exit 2

PLUGIN="plugins/$NAME"
SKILL="$PLUGIN/skills/$NAME"
if [ ! -d "$PLUGIN" ]; then
  echo "release_check: no such plugin: $PLUGIN" >&2
  exit 2
fi

fail=0
ok()   { printf "  OK   %s\n" "$1"; }
ng()   { printf "  NG   %s\n" "$1"; fail=1; }
note() { printf "  --   %s\n" "$1"; }

echo "release_check: $NAME  ($REPO)"
echo

# ---------------------------------------------------------------- 1. frontmatter
python3 - "$NAME" "$SKILL" <<'PY'
import sys, re, pathlib
name, skill_dir = sys.argv[1], pathlib.Path(sys.argv[2])
md = skill_dir / "SKILL.md"
if not md.is_file():
    print("  NG   SKILL.md がありません: %s" % md); sys.exit(1)
text = md.read_text(encoding="utf-8")
m = re.match(r"(?s)^---\n(.*?)\n---\n", text)
if not m:
    print("  NG   frontmatter がありません"); sys.exit(1)
fm = m.group(1)
dm = re.search(r"(?m)^description:[ \t]*(.*)$", fm)
if not dm:
    print("  NG   description がありません"); sys.exit(1)
desc = dm.group(1)
bad = 0
if len(desc) > 1024:
    print("  NG   description が %d 字 (上限 1024)" % len(desc)); bad = 1
else:
    print("  OK   description %d 字" % len(desc))
if ": " in desc and not (desc.startswith(('"', "'", "|", ">"))):
    print("  NG   description に \": \" があり、YAML が途中で切れます"); bad = 1
else:
    print("  OK   description に YAML を壊す \": \" は無い")
if re.search(r"</?[a-zA-Z][^>]*>", desc):
    print("  NG   description に XML タグがあります (Skills API が拒否)"); bad = 1
body = text[m.end():].splitlines()
if len(body) > 500:
    print("  NG   SKILL.md 本文が %d 行 (公式指針: 500行未満)" % len(body)); bad = 1
else:
    print("  OK   SKILL.md 本文 %d 行" % len(body))
for ref in sorted((skill_dir / "references").glob("*.md")) if (skill_dir/"references").is_dir() else []:
    lines = ref.read_text(encoding="utf-8").splitlines()
    if len(lines) > 100:
        head = "\n".join(lines[:40])
        if not re.search(r"(?im)^#{2,3}\s*(contents|目次|toc)\b", head):
            print("  NG   %s は %d 行だが目次が無い" % (ref.name, len(lines))); bad = 1
        else:
            print("  OK   %s 目次あり (%d 行)" % (ref.name, len(lines)))
sys.exit(bad)
PY
[ $? -eq 0 ] || fail=1

# --------------------------------------------------- 2. registered in four places
# "名前がファイルのどこかに出てくる" では弱すぎる。README には本文リンクとして
# 名前が出ることがあり、表の行を消しても grep は通ってしまう（実際に取り逃した）。
# JSON は name フィールド、README は表の行そのものを見る。
python3 - "$NAME" "$PLUGIN" <<'PY'
import json, pathlib, re, sys
name, plugin = sys.argv[1], sys.argv[2]
bad = 0
def say(okp, msg):
    global bad
    print(("  OK   " if okp else "  NG   ") + msg)
    if not okp: bad = 1

pj = pathlib.Path(plugin)/".claude-plugin"/"plugin.json"
try:
    say(json.loads(pj.read_text()).get("name") == name, "plugin.json の name が一致")
except Exception as e:
    say(False, "plugin.json が読めない (%s)" % e)

mp = pathlib.Path(".claude-plugin/marketplace.json")
try:
    entries = [p for p in json.loads(mp.read_text())["plugins"] if p.get("name") == name]
    say(bool(entries), "marketplace.json に登録あり")
    if entries and entries[0].get("source") != "./plugins/%s" % name:
        say(False, "marketplace.json の source が ./plugins/%s でない" % name)
except Exception as e:
    say(False, "marketplace.json が読めない (%s)" % e)

row = re.compile(r"^\|\s*\*\*%s\*\*\s*\|" % re.escape(name), re.M)
for f in ("README.md", "README_ja.md"):
    say(bool(row.search(pathlib.Path(f).read_text(encoding="utf-8"))),
        "%s のカテゴリ表に行がある" % f)
sys.exit(bad)
PY
[ $? -eq 0 ] || fail=1

# ------------------------------------------------------------- 3. version bumped
if git -C "$REPO" rev-parse HEAD >/dev/null 2>&1; then
  if git -C "$REPO" diff --quiet HEAD -- "$SKILL" && git -C "$REPO" diff --quiet --cached HEAD -- "$SKILL"; then
    note "スキル本体に未コミットの変更なし — バージョンは確認不要"
  else
    now=$(python3 -c "import json;print(json.load(open('$PLUGIN/.claude-plugin/plugin.json')).get('version',''))" 2>/dev/null)
    was=$(git -C "$REPO" show "HEAD:$PLUGIN/.claude-plugin/plugin.json" 2>/dev/null \
          | python3 -c "import json,sys;print(json.load(sys.stdin).get('version',''))" 2>/dev/null)
    if [ -z "$was" ]; then ok "新規プラグイン (version=$now)"
    elif [ "$now" = "$was" ]; then ng "スキルが変わったのに version が $now のまま (install.sh が拾わない)"
    else ok "version $was -> $now"; fi
  fi
fi

# ------------------------------------------------------------ 4. catalog freshness
if [ -f site/scripts/gen_catalog.py ] && [ -f site/skills/_catalog.md ]; then
  before=$(mktemp); cp site/skills/_catalog.md "$before"
  python3 site/scripts/gen_catalog.py >/dev/null 2>&1
  if cmp -s "$before" site/skills/_catalog.md; then
    ok "サイトカタログは最新"
  elif [ "$FIX_CATALOG" = "1" ]; then
    ok "サイトカタログを再生成した (--fix-catalog) — 差分をコミットすること"
  else
    ng "サイトカタログが古い — python3 site/scripts/gen_catalog.py して差分をコミット"
    cp "$before" site/skills/_catalog.md
  fi
  rm -f "$before"
fi

# ---------------------------------------------------------------- 5. validator
if [ -f tools/validate_skills.py ]; then
  out=$(python3 tools/validate_skills.py --only "$NAME" --strict 2>&1); rc=$?
  if [ $rc -eq 0 ]; then ok "validate_skills.py --strict 通過"
  else ng "validate_skills.py --strict"; printf '%s\n' "$out" | sed 's/^/       /' | head -8; fi
fi

# ------------------------------------------------------------- 6. bundled harness
harness=""
[ -f "$SKILL/tests/run_tests.sh" ] && harness="$SKILL/tests/run_tests.sh"
[ -f "$SKILL/detectors/test_detectors.sh" ] && harness="$SKILL/detectors/test_detectors.sh"
if [ -n "$harness" ]; then
  if bash "$harness" >/tmp/rc_harness.$$ 2>&1; then ok "ハーネス通過: $harness"
  else ng "ハーネス失敗: $harness"; tail -5 /tmp/rc_harness.$$ | sed 's/^/       /'; fi
  rm -f /tmp/rc_harness.$$
elif ls "$SKILL"/scripts/*.py "$SKILL"/scripts/*.sh >/dev/null 2>&1; then
  note "スクリプトを同梱しているがテストが無い (tests/run_tests.sh を検討)"
fi

echo
if [ "$fail" -eq 0 ]; then echo "判定: 出荷可"; else echo "判定: 指摘あり"; fi
echo "保証しないこと"
echo "  - 内容の質は見ていない。トリガ精度と出力品質は skill-creator の担当"
echo "  - 4箇所に「名前がある」ことしか見ていない。説明文の中身の一致までは見ない"
exit $fail
