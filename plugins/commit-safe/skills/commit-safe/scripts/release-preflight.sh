#!/bin/bash
# Read-only release preflight for the commit-safe skill.
# リリース前状態の点検（読み取り専用 / no writes, no network mutations）
#
# Usage: release-preflight.sh [--tag vX.Y.Z]
# Exit:  0 = no blockers, 1 = blockers found, 2 = usage / not a git repo

set -u

# --- minimal i18n (Japanese if locale starts with ja, else English) ---
_lang="en"
case "${LC_ALL:-${LC_MESSAGES:-${LANG:-}}}" in
    ja*|ja_*) _lang="ja" ;;
esac
msg() { if [ "$_lang" = "ja" ]; then printf '%s' "$2"; else printf '%s' "$1"; fi; }

BLOCKERS=0
WARNINGS=0
blocker() { echo "  ❌ BLOCKER: $1"; BLOCKERS=$((BLOCKERS + 1)); }
warn()    { echo "  ⚠️  WARN: $1";  WARNINGS=$((WARNINGS + 1)); }
ok()      { echo "  ✅ $1"; }
info()    { echo "     $1"; }
section() { echo; echo "── $1"; }

WANT_TAG=""
while [ $# -gt 0 ]; do
    case "$1" in
        --tag)
            [ $# -ge 2 ] || { echo "$(msg "--tag needs a value" "--tag には値が必要です")" >&2; exit 2; }
            WANT_TAG="$2"; shift 2 ;;
        --tag=*) WANT_TAG="${1#--tag=}"; shift ;;
        -h|--help)
            echo "Usage: $0 [--tag vX.Y.Z]"; exit 0 ;;
        *)
            echo "$(msg "Unknown option" "不明なオプション"): $1" >&2; exit 2 ;;
    esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ $(msg "Not a git repository" "gitリポジトリではありません")"
    exit 2
fi
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT" || exit 2

echo "═══ $(msg "Release preflight" "リリース前点検") ═══"
info "$(msg "repo" "リポジトリ"): $ROOT"

# ── repository / branch ────────────────────────────────────────────────
section "$(msg "Branch & remote" "ブランチとリモート")"
BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")
if [ -z "$BRANCH" ]; then
    blocker "$(msg "detached HEAD — checkout a branch before releasing" "detached HEAD — リリース前にブランチへ切り替えてください")"
else
    info "$(msg "branch" "ブランチ"): $BRANCH"
fi

UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo "")
if [ -n "$UPSTREAM" ]; then
    info "upstream: $UPSTREAM"
else
    warn "$(msg "no upstream configured (push will need -u)" "upstream 未設定（push 時に -u が必要）")"
fi

REMOTE=$(git remote 2>/dev/null | head -1)
if [ -n "$REMOTE" ]; then
    info "remote: $REMOTE -> $(git remote get-url "$REMOTE" 2>/dev/null)"
else
    warn "$(msg "no git remote configured" "git リモートが未設定")"
fi

# ── working tree ───────────────────────────────────────────────────────
section "$(msg "Working tree" "作業ツリー")"
DIRTY=$(git status --porcelain 2>/dev/null)
if [ -n "$DIRTY" ]; then
    blocker "$(msg "working tree is not clean" "作業ツリーが未コミットの変更を含んでいます")"
    echo "$DIRTY" | head -20 | sed 's/^/       /'
    [ "$(echo "$DIRTY" | wc -l)" -gt 20 ] && info "... ($(echo "$DIRTY" | wc -l) $(msg "entries total" "件"))"
else
    ok "$(msg "clean" "クリーン")"
fi

# ── sync with upstream ─────────────────────────────────────────────────
if [ -n "$UPSTREAM" ]; then
    section "$(msg "Sync with upstream" "upstream との同期")"
    info "$(msg "(remote state is as of the last fetch; not fetched here)" "（リモート情報は最後の fetch 時点。ここでは fetch しません）")"
    COUNTS=$(git rev-list --left-right --count "$UPSTREAM"...HEAD 2>/dev/null || echo "")
    if [ -n "$COUNTS" ]; then
        BEHIND=$(echo "$COUNTS" | awk '{print $1}')
        AHEAD=$(echo "$COUNTS" | awk '{print $2}')
        info "$(msg "ahead" "先行"): $AHEAD / $(msg "behind" "遅れ"): $BEHIND"
        [ "$BEHIND" -gt 0 ] && blocker "$(msg "local branch is behind upstream — pull/rebase first" "ローカルが upstream より遅れています — 先に pull/rebase してください")"
        [ "$AHEAD" -gt 0 ] && info "$(msg "unpushed commits:" "未 push のコミット:")" && git log --oneline "$UPSTREAM"..HEAD | head -10 | sed 's/^/       /'
    fi
fi

# ── tags ───────────────────────────────────────────────────────────────
section "$(msg "Tags" "タグ")"
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    info "$(msg "latest tag" "直近のタグ"): $LAST_TAG"
    N=$(git rev-list --count "$LAST_TAG"..HEAD 2>/dev/null || echo "?")
    info "$(msg "commits since" "それ以降のコミット数"): $N"
else
    info "$(msg "no tags yet" "タグはまだありません")"
fi

if [ -n "$WANT_TAG" ]; then
    if git rev-parse -q --verify "refs/tags/$WANT_TAG" >/dev/null 2>&1; then
        blocker "$(msg "tag already exists locally" "タグがローカルに既に存在します"): $WANT_TAG"
    else
        ok "$(msg "tag is free (local)" "タグは未使用（ローカル）"): $WANT_TAG"
    fi
    if [ -n "$REMOTE" ] && git ls-remote --tags "$REMOTE" "refs/tags/$WANT_TAG" 2>/dev/null | grep -q .; then
        blocker "$(msg "tag already exists on remote" "タグがリモートに既に存在します"): $WANT_TAG"
    fi
fi

# ── version-bearing files ──────────────────────────────────────────────
section "$(msg "Version files" "バージョン記載ファイル")"
FOUND_VERSION=0
show_version() { # show_version <file> <extracted-or-empty>
    FOUND_VERSION=1
    if [ -n "$2" ]; then info "$1: $2"; else info "$1: ($(msg "version not parsed" "版数を解析できず"))"; fi
}

json_version() { grep -m1 '"version"[[:space:]]*:' "$1" 2>/dev/null | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/'; }
toml_version() { grep -m1 '^[[:space:]]*version[[:space:]]*=' "$1" 2>/dev/null | sed 's/.*=[[:space:]]*["'"'"']\([^"'"'"']*\)["'"'"'].*/\1/'; }

for f in package.json .claude-plugin/plugin.json composer.json; do
    [ -f "$f" ] && show_version "$f" "$(json_version "$f")"
done
for f in pyproject.toml Cargo.toml; do
    [ -f "$f" ] && show_version "$f" "$(toml_version "$f")"
done
[ -f VERSION ] && show_version "VERSION" "$(head -1 VERSION | tr -d '[:space:]')"
[ -f gradle.properties ] && grep -q '^version' gradle.properties 2>/dev/null && \
    show_version "gradle.properties" "$(grep -m1 '^version' gradle.properties | cut -d= -f2- | tr -d '[:space:]')"

# plugin.json files nested under plugins/ (marketplace-style repos)
NESTED=$(git ls-files '*/.claude-plugin/plugin.json' 2>/dev/null | head -30)
if [ -n "$NESTED" ]; then
    info "$(msg "nested plugin manifests" "配下の plugin.json"): $(echo "$NESTED" | wc -l) $(msg "file(s)" "件")"
    FOUND_VERSION=1
fi

# __version__ = "..." in Python sources
PYVER=$(git grep -l -E '^__version__[[:space:]]*=' -- '*.py' 2>/dev/null | head -5)
if [ -n "$PYVER" ]; then
    echo "$PYVER" | while read -r f; do
        info "$f: $(grep -m1 -E '^__version__[[:space:]]*=' "$f" | sed 's/.*=[[:space:]]*["'"'"']\([^"'"'"']*\)["'"'"'].*/\1/')"
    done
    FOUND_VERSION=1
fi

[ "$FOUND_VERSION" -eq 0 ] && info "$(msg "no version file detected — tag-only release?" "バージョン記載ファイルを検出できず — タグのみのリリース？")"

# ── changelog ──────────────────────────────────────────────────────────
section "CHANGELOG"
CL=$(ls CHANGELOG.md CHANGELOG CHANGES.md HISTORY.md docs/CHANGELOG.md 2>/dev/null | head -1)
if [ -n "$CL" ]; then
    ok "$CL"
    info "$(msg "top of file" "冒頭"): $(grep -m1 '^#' "$CL" 2>/dev/null)"
else
    warn "$(msg "no CHANGELOG found — consider creating one" "CHANGELOG が見つかりません — 作成を検討")"
fi

# ── publish targets ────────────────────────────────────────────────────
section "$(msg "Publish targets" "公開先")"
PUB=0
if [ -f package.json ]; then
    PUB=1
    NAME=$(grep -m1 '"name"[[:space:]]*:' package.json | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    if grep -q '"private"[[:space:]]*:[[:space:]]*true' package.json; then
        info "npm: $NAME ($(msg "private — publish disabled" "private のため公開不可"))"
    else
        info "npm: $NAME — npm publish --dry-run"
    fi
fi
if [ -f pyproject.toml ] || [ -f setup.py ]; then
    PUB=1
    info "PyPI: python -m build && twine check dist/*"
fi
if [ -f Cargo.toml ]; then
    PUB=1
    if grep -q '^[[:space:]]*publish[[:space:]]*=[[:space:]]*false' Cargo.toml; then
        info "crates.io: ($(msg "publish = false" "publish = false のため公開不可"))"
    else
        info "crates.io: cargo publish --dry-run"
    fi
fi
[ -f go.mod ] && { PUB=1; info "Go: $(msg "module released by tag only" "タグのみでリリース")"; }
[ "$PUB" -eq 0 ] && info "$(msg "no package manifest — repository/tag release only" "パッケージ定義なし — リポジトリ/タグのリリースのみ")"

# ── tooling ────────────────────────────────────────────────────────────
section "$(msg "Tooling" "ツール")"
if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        ok "gh: $(msg "installed and authenticated" "インストール済み・認証済み")"
    else
        warn "gh: $(msg "installed but NOT authenticated — GitHub Release step will fail" "インストール済みだが未認証 — GitHub Release は実行できません")"
    fi
else
    warn "gh: $(msg "not installed — GitHub Release must be created manually" "未インストール — GitHub Release は手動作成が必要")"
fi

# ── summary ────────────────────────────────────────────────────────────
echo
echo "═══ $(msg "Summary" "まとめ") ═══"
echo "  BLOCKER: $BLOCKERS / WARN: $WARNINGS"
if [ "$BLOCKERS" -gt 0 ]; then
    echo "  ⛔ $(msg "Resolve blockers before releasing." "BLOCKER を解消するまでリリースへ進まないでください。")"
    exit 1
fi
echo "  ✅ $(msg "No blockers. Proceed step by step, with approval at each gate." "BLOCKER なし。各ゲートで承認を得ながら進めてください。")"
exit 0
