# Session Summary — design notes

Design rationale for the `session-summary` plugin: a structured summary of the current AI
working session, richer than the built-in one-line `/recap`.

## The need

Claude Code ships `/recap` (one line), `/insights` (an HTML report across many sessions),
`/export` (the raw conversation) and `/compact` (a summary for the context window, not for a
reader). None of them answers, for one session, the questions a returning reader asks:
do I have to act, where is the work, how far has it got, what comes next and what is in the
way. No skill in anthropics/skills or in this marketplace did either (checked 2026-10-31).

## Sections and why each exists

| Section | Why |
|---|---|
| 一言概要 | Requested. Lets the reader decide whether to read on |
| あなたにお願いしたいこと | Placed second because the most common reason to read a summary is to learn whether the reader is the one blocking. Written as `なし` when empty, so absence is distinguishable from "not checked" |
| 作業場所 | Requested. Path, repository, remote, branch, HEAD and dirty state are what is needed to resume the work elsewhere, and what is most often misremembered |
| ロードマップと現在地 | Requested. Omitted for sessions that only answered questions, so the template does not invent a plan |
| 生成・変更したもの | Requested. Carries a state column (uncommitted / committed / pushed) because "I made X" without the state is the usual source of a lost change |
| 決めたこと | Added. What is lost first on resume is not what was decided but why, and what was rejected; without it the same choice is argued again |
| 確認できていないこと | Added. Separating done from verified keeps the summary from being more optimistic than the evidence |
| 次にやること / 止まっているもの | Requested. Blockers are typed (decision / external / technical) with an unblocker, so it is clear who must move |

## Facts from the repository, not from memory

The workspace section and artifact states are produced by `scripts/workspace_facts.sh` rather
than written from the conversation. A summary written from memory reproduces the agent's
belief about the repository, which is exactly what drifts after compaction, a rebase, or a
change the user made in another terminal. The script prints `key: value` lines only, masks
credentials embedded in remote URLs, treats a non-repository as a normal case (exit 0), and
takes `--since <rev>` so the commits made during the session can be listed.

## Saving only on request

The maintainer chose on-demand saving. The default location is
`~/.claude/session-summaries/`, outside the repository, so a summary is never swept into a
commit. Files are never overwritten, so a series of summaries doubles as a history.

## Hand-offs

- One-line recap → built-in `/recap`
- Meeting, conference or trip records → `debrief-report`
- Summarizing a document → `document-summary`
- Parking a task for a later session → `backlog`
- Reporting progress to a GitHub Issue → `commit-and-report`
