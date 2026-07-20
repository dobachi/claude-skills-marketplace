# backlog

A lightweight, persistent **do-it-later inbox** for coding agents. Park a task in one line
now, pick it up in a later session.

```
/backlog add egress proxy で SBX_NET=none 対応 #hardening
/backlog                     # 未完了を一覧（repo + 個人インボックスをまとめて）
/backlog done proxy          # チェック
/backlog archive             # 済み項目を BACKLOG.archive.md へ退避（棚卸し）
```

Also fires on natural phrases: 「これ積んでおいて」「あとでやる」「TODOに入れて」「棚卸しして」
"add to backlog" / "what's on my backlog" / "clear out the done items".

## Storage (hybrid, automatic)

| Context | File |
|---|---|
| Inside a git repo | `<repo-root>/BACKLOG.md` (shared via git, reviewable in a PR) |
| Anywhere else | `~/.claude/backlog.md` (personal inbox) |

`list` shows **both** at once so nothing is hidden. Override with `-g` (personal) / `-r`
(this repo). Completed items are swept into a sibling `*.archive.md` by `archive`.

## Why not the session task list?

The session task list is ephemeral — it vanishes when the conversation ends. `backlog`
persists across sessions and across repos, which is what "park this for later" needs.

## Requirements

`python3` on `PATH` (standard library only — no dependencies). Cross-agent: the same
`scripts/backlog.py` works under Claude Code, Codex, and Antigravity (agy).

Design notes: [`docs/backlog-design.md`](../../docs/backlog-design.md).
