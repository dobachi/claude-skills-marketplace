---
name: session-summary
description: Writes a structured summary of the current AI working session — a one-line overview, what the user must decide or do, where the work happened (paths, repository, remote, branch, HEAD, uncommitted state), the roadmap with the current position, what was created or changed, decisions with their reasons and rejected options, what is done but unverified, and the next step together with what is blocking it and who must act. Workspace facts come from a bundled script run against the repository, not from memory of the conversation. Saves to a file only when asked. Use when the user wants a recap richer than one line — "セッションをまとめて", "今の状況を整理して", "進捗サマリ", "どこまで進んだ？", "引き継ぎ用にまとめて", "summarize this session", "where are we", "status summary", "handoff note". Not for the built-in one-line `/recap`, meeting or trip reports (debrief-report), summarizing a document (document-summary), parking tasks for later (backlog), or posting progress to GitHub Issues (commit-and-report).
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Session Summary

Summarize the session so that a reader who returns to it cold can tell, from the top down:
whether they must act, where the work lives, how far it has got, and what comes next.

## Step 1 — collect the workspace facts

Run the bundled script from the working directory of the session:

```bash
bash <skill-dir>/scripts/workspace_facts.sh [--since <rev>] [--dir <path>]
```

- `--since <rev>`: the HEAD at the start of the session, when known (the git status snapshot
  at the top of the conversation, or the first commit you made). It lists the commits made
  since then.
- `--dir <path>`: run once per additional repository the session worked in.
- Exit `0` = facts printed (a directory that is not a git repository prints `git: none`);
  `2` = bad argument or an unresolvable `--since`.

Files written outside a repository (scratchpad, `~/.claude/...`, generated reports):
confirm each one still exists with `ls` before listing it.

## Step 2 — reconstruct the session from the conversation

Identify: the goal, the steps taken or planned, decisions and their reasons, what was
verified and how, and what is waiting. Where earlier parts of the conversation are only
available as a compaction summary, mark claims drawn from them as `（圧縮前の要約に基づく）`
/ `(from pre-compaction summary)` rather than stating them as observed.

## Step 3 — write the summary

Use this order. Headings follow the user's language; the Japanese form is shown.

```markdown
## 一言概要
<one or two sentences: the goal, what was done, where it stands>

## あなたにお願いしたいこと
- [判断] <decision needed> — 推奨: <option>（<reason>）
- [作業] <something only the user can do, e.g. an interactive login>
（なければ「なし」）

## 作業場所
- ディレクトリ: <absolute cwd>
- リポジトリ: <repo_root>（<main | linked worktree, main: …>）
- リモート: <name> <url>
- ブランチ / HEAD: <branch> @ <short sha> <subject>
- upstream: <name>（ahead N, behind M） / なし
- 未コミット: staged N, modified N, untracked N

## ロードマップと現在地
1. ✅ <done step>
2. ▶ <current step — concrete progress, e.g. 3/5 tests passing>
3. ⬜ <remaining step>

## 生成・変更したもの
| 対象 | 種別 | 状態 |
|---|---|---|
| <absolute or repo-relative path / commit sha> | 新規 / 変更 / 削除 / コミット | 未コミット / コミット済み / push済み |

## 決めたこと
- <decision> — 理由: <why>。却下: <alternative and why not>

## 確認できていないこと・リスク
- <done but not verified, and what verifying it would take>

## 次にやること / 止まっているもの
- 次: <the single next action>
- 停止中: [判断待ち | 外部待ち | 技術] <what> — <who or what unblocks it>
```

## Rules

1. **The ask comes second, right after the overview.** Write `なし` / `none` when there is
   nothing; an absent section reads as "not checked".
2. **Workspace and artifact states come from Step 1 output.** Never write a path, branch,
   commit or "pushed" from memory. If the script was not run, the section says so.
3. **Done and verified are separate.** An item is verified only if a test, a run, or a
   direct inspection in this session showed it working; otherwise it goes under
   確認できていないこと.
4. **Every blocker has a type and an unblocker.** `[判断待ち]` = the user must choose,
   `[外部待ち]` = CI, a review, another person, `[技術]` = an unsolved problem.
5. **Decisions carry the reason and the rejected option.** A decision without the why gets
   re-argued in the next session.
6. **No invented roadmap.** A session that only answered questions gets no roadmap section;
   drop empty structural sections (roadmap, decisions) rather than padding them.
7. **Paths are absolute or repo-relative, never a bare filename.**
8. **Fit on roughly one screen.** List the five most important artifacts and give a count for
   the rest instead of repeating the whole `git status` list.

## Saving

Only when the user asks ("保存して", "save it", "引き継ぎファイルにして"):

- Default path: `~/.claude/session-summaries/<repo-name or dir-name>-<YYYYMMDD-HHMM>.md`
  — outside the repository, so it is never committed by accident.
- Use the path the user names if they name one. Never overwrite an existing file; add a
  suffix instead.
- Report the absolute path of the saved file.

## Anti-patterns

| Anti-pattern | Instead |
|---|---|
| A chronological replay of the conversation | Organize by the sections above; the roadmap carries the order |
| "Tests pass" with no test run in this session | Put it under 確認できていないこと |
| "Waiting" with no type or owner | `[外部待ち] CI on PR #12 — rerun after the fix lands` |
| Listing every file in a 40-file change | Top five plus "and 35 more (see `git status`)" |
| Filling the roadmap for a Q&A session | Omit the section |
