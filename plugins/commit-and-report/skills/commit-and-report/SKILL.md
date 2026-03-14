---
name: commit-and-report
description: Commit, push, and report progress to GitHub Issues in one step
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Commit, Push & Issue Report

Commits changes, pushes to remote, and reports progress to the specified Issue. Can also close the Issue when work is complete.

## Usage

```
/commit-and-report "commit message" [issue number]
```

## Execution Steps

1. **Check changes, stage, and commit**
   ```bash
   git status
   git add .
   git commit -m "$ARGUMENTS"
   ```

   Note: `git add .` only targets files under the current directory.
   To target the entire project, run from the project root or
   specify files explicitly.

2. **Push to remote**
   ```bash
   git push
   ```

3. **Report to Issue** (when issue number is provided)
   ```bash
   if echo "$ARGUMENTS" | grep -q " "; then
     ISSUE_NUM=$(echo "$ARGUMENTS" | awk '{print $NF}')
     COMMIT_MSG=$(echo "$ARGUMENTS" | sed 's/ [0-9]*$//')
     gh issue comment "$ISSUE_NUM" --body "$COMMIT_MSG"
   fi
   ```

## Examples

```
/commit-and-report "feat: implement custom commands"
/commit-and-report "fix: bug fix" 123
```

When an issue number is provided, progress is automatically reported to that Issue.
