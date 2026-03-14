---
name: github-issues
description: GitHub Issueを確認してやるべきことを整理するスキル
---

# GitHub Issue確認・整理

このリポジトリのGitHub Issueを確認し、やるべきタスクを整理します。

## 実行内容

1. **GitHub CLI認証確認**
   ```bash
   gh auth status 2>/dev/null || echo "GitHub CLIの認証が必要です: gh auth login"
   ```

2. **オープンなIssue一覧取得**
   ```bash
   echo "オープンなIssue一覧:"
   gh issue list --state open --limit 30 --json number,title,labels,assignees,createdAt --template '{{range .}}#{{.number}}: {{.title}}{{if .labels}} [{{range $i, $e := .labels}}{{if $i}}, {{end}}{{.name}}{{end}}]{{end}}{{if .assignees}} (担当: {{range $i, $e := .assignees}}{{if $i}}, {{end}}{{.login}}{{end}}){{end}}{{"\n"}}{{end}}'
   ```

3. **ラベル別Issue集計**
   ```bash
   echo "ラベル別集計:"
   gh issue list --state open --json labels --jq '[.[] | .labels[].name] | group_by(.) | map({label: .[0], count: length}) | sort_by(.count) | reverse | .[] | "\(.label): \(.count)件"' | head -10
   ```

4. **最近のIssue（7日以内）**
   ```bash
   echo "最近作成されたIssue（7日以内）:"
   gh issue list --state open --search "created:>$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)" --limit 10 --json number,title,createdAt --template '{{range .}}#{{.number}}: {{.title}} ({{.createdAt | time "2006-01-02"}}){{"\n"}}{{end}}'
   ```

5. **高優先度Issue確認**
   ```bash
   echo "高優先度Issue:"
   gh issue list --state open --label "priority:high,bug,critical" --limit 10 --json number,title,labels --template '{{range .}}#{{.number}}: {{.title}} [{{range $i, $e := .labels}}{{if $i}}, {{end}}{{.name}}{{end}}]{{"\n"}}{{end}}'
   ```

6. **タスク整理提案**
   以下の観点でタスクを整理・提案します：
   - 優先度（ラベル、作成日時から判断）
   - 関連性（類似Issueのグループ化）
   - 実装順序（依存関係を考慮）
   - 作業量の見積もり

## 使用方法

```
/github-issues
```

引数は不要です。GitHub CLIが設定されている必要があります。

## 注意事項

- GitHub CLIの認証が必要です（`gh auth login`）
- プライベートリポジトリの場合は適切な権限が必要です
- Issue数が多い場合は表示を制限しています（各カテゴリ最大10-30件）
