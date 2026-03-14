---
name: github-issues
description: Lists GitHub Issues, aggregates by label, analyzes priorities, and organizes tasks
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# GitHub Issue Review & Organization

Reviews GitHub Issues in this repository and organizes actionable tasks.

## Execution Steps

1. **Check GitHub CLI authentication**
   ```bash
   gh auth status 2>/dev/null || echo "GitHub CLI authentication required: gh auth login"
   ```

2. **List open Issues**
   ```bash
   echo "Open Issues:"
   gh issue list --state open --limit 30 --json number,title,labels,assignees,createdAt --template '{{range .}}#{{.number}}: {{.title}}{{if .labels}} [{{range $i, $e := .labels}}{{if $i}}, {{end}}{{.name}}{{end}}]{{end}}{{if .assignees}} (Assignee: {{range $i, $e := .assignees}}{{if $i}}, {{end}}{{.login}}{{end}}){{end}}{{"\n"}}{{end}}'
   ```

3. **Aggregate Issues by label**
   ```bash
   echo "Issues by label:"
   gh issue list --state open --json labels --jq '[.[] | .labels[].name] | group_by(.) | map({label: .[0], count: length}) | sort_by(.count) | reverse | .[] | "\(.label): \(.count)"' | head -10
   ```

4. **Recent Issues (within 7 days)**
   ```bash
   echo "Recently created Issues (within 7 days):"
   gh issue list --state open --search "created:>$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)" --limit 10 --json number,title,createdAt --template '{{range .}}#{{.number}}: {{.title}} ({{.createdAt | time "2006-01-02"}}){{"\n"}}{{end}}'
   ```

5. **Check high-priority Issues**
   ```bash
   echo "High-priority Issues:"
   gh issue list --state open --label "priority:high,bug,critical" --limit 10 --json number,title,labels --template '{{range .}}#{{.number}}: {{.title}} [{{range $i, $e := .labels}}{{if $i}}, {{end}}{{.name}}{{end}}]{{"\n"}}{{end}}'
   ```

6. **Task organization suggestions**
   Organize and suggest tasks based on the following perspectives:
   - Priority (determined from labels and creation date)
   - Relevance (grouping similar Issues)
   - Implementation order (considering dependencies)
   - Effort estimation

## Usage

```
/github-issues
```

No arguments required. GitHub CLI must be configured.

## Notes

- GitHub CLI authentication is required (`gh auth login`)
- Appropriate permissions are needed for private repositories
- Display is limited for large numbers of Issues (max 10-30 per category)
