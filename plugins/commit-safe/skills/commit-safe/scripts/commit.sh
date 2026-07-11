#!/bin/bash

# Clean commit tool without AI messages / AIメッセージを含まないクリーンなコミット
# Self-contained: no external dependencies (bundled with the commit-safe skill).

# --- minimal i18n (Japanese if locale starts with ja, else English) ---
_lang="en"
case "${LC_ALL:-${LC_MESSAGES:-${LANG:-}}}" in
    ja*|ja_*) _lang="ja" ;;
esac
msg() { # msg "<english>" "<japanese>"
    if [ "$_lang" = "ja" ]; then printf '%s' "$2"; else printf '%s' "$1"; fi
}

# --- argument check ---
if [ $# -eq 0 ]; then
    echo "$(msg "Usage" "使用方法"): $0 \"$(msg "commit message" "コミットメッセージ")\""
    echo "$(msg "Example" "例"): $0 \"$(msg "feat: Add new feature" "feat: 新機能を追加")\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# --- commit only what is already staged ---
if ! git diff --cached --quiet; then
    echo "📝 $(msg "Committing staged changes..." "ステージングエリアの変更をコミット中...")"

    git commit -m "$COMMIT_MESSAGE"

    if [ $? -eq 0 ]; then
        echo "✅ $(msg "Commit completed!" "コミット完了!")"
        git log -1 --oneline
    else
        echo "❌ $(msg "Commit failed" "コミットに失敗しました")"
        exit 1
    fi
else
    echo "⚠️  $(msg "No changes in staging area" "ステージングエリアに変更がありません")"
    echo "$(msg "Please stage changes with 'git add' first" "先に 'git add' で変更をステージしてください")"
    exit 1
fi
