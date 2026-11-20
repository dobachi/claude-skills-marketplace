---
name: session-map
description: Lists every Claude Code session running on this machine and says what each one is doing — laid out along the tmux structure (session, window, pane), then terminals outside tmux, Remote Control children and background sessions. A bundled script reads the facts Claude Code already writes (~/.claude/sessions, the transcripts, ps, tmux list-panes), flags what needs the user (waiting for input, stopped with Ctrl-Z, idle for days, duplicate names, two claude in one pane, no transcript), and with --summarize has a cheap model (haiku) turn each transcript into five lines — purpose, now, state, waiting on, next — cached by transcript mtime so unchanged sessions cost nothing. Use when the user asks "動いているセッションを一覧して", "セッションのまとめ", "tmux で何が動いてる？", "どのセッションが返事待ち？", "放置しているセッションは？", "what sessions are running", "session overview". Not for summarizing the current session in depth (session-summary), saving or restoring tmux layouts (tmux-revive), or sessions on other machines and in the cloud (ListAgents).
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Session Map

Answer two questions about this machine, cheaply: **what is running where**, and **what each
session is doing — especially which ones are waiting on the user.**

Claude Code's own `claude agents --json` and the ListAgents tool already list sessions, but
not as a tmux tree, not whether a process is stopped with Ctrl-Z, and not what the session is
about. The script adds those; you add the overview.

## Step 1 — run the script

```bash
python3 <skill-dir>/scripts/session_map.py --summarize
```

| Option | Use |
|---|---|
| (none) | Structure, flags, AI title and last ask only. No model call. Use when the user only wants the layout |
| `--summarize` | Adds a five-line summary per session from a cheap model. **The default for "まとめ"**. A session in `waiting` status is summarized from the deeper excerpt plus its tmux screen, because the question it waits on is what a short excerpt misses |
| `--session Q` | Only sessions matching a pid, a sessionId prefix, part of a name, or a pane id like `%61` |
| `--session Q --deep` | One session in depth: more of the transcript, the current tmux screen, a longer summary |
| `--model M` | Summary model (default `haiku`, or `$SESSION_MAP_MODEL`) |
| `--stale-days N` | Days without an update before the "更新なし" flag (default 7) |
| `--no-cache` / `--json` | Force fresh summaries / machine-readable output |

Exit `0` = listed, `1` = listed but some summaries failed (each failure is shown in place),
`2` = no `~/.claude/sessions` here, no match for `--session`, or a usage error.

Cost, measured on 20 sessions: about $0.01 and 25 seconds for the first run; repeated runs
only pay for sessions whose transcript changed. Summaries are cached in
`~/.cache/session-map/` (mode 700).

The script holds the model to the format (the five lines, in order; a missing line reads
`（要約に無し）`), and a second process on the same conversation points at the first instead of
repeating its summary.

Show the user the script's output as it is (it is already a tree). Then write Step 2 under it.

## Step 2 — write the overview

Under the tree, in this order. Headings follow the user's language.

```markdown
## あなたの返事を待っているもの
- <session label>（<tmux 位置 or 場所>）— <what it waits for, from 待ち: or the 入力待ち flag>
（なければ「なし」）

## 進行中
- <label> — <one line from いま:>

## 片付け候補
- <label> — <reason: N日更新なし / 会話ログなし / 一時停止中 / 同名が複数>
```

## Rules

1. **Only what the script printed.** The summaries come from a cheap model reading an excerpt;
   do not add facts to them, and keep any 「らしい」 they carry.
2. **"Waiting" has two sources — use both.** The `入力待ち` flag (Claude Code's own status,
   e.g. a permission prompt) and a `待ち:` line that is not 「なし」 (the session asked the user
   a question and stopped). A session can be idle and still be waiting on the user.
3. **Locate every session the way the user would reach it**: `tmux 8:2.0`, `tmux の外 pts/10`,
   `Remote Control`. Not by pid alone.
4. **Cleanup candidates are suggestions, never actions.** Do not kill, stop, `claude rm` or
   detach anything unless the user asks for that specific session.
5. **Two processes on one conversation in one pane** (one usually stopped with Ctrl-Z) is
   worth naming: resuming the stopped one later would fork the conversation.
6. **Drill down only on request, one session at a time** with `--session Q --deep`. It reads
   more transcript and the tmux screen, so it costs more than the overview.
7. **Other machines and cloud sessions are out of scope.** If the user asks about them, call
   ListAgents; it lists Remote Control sessions on other machines and cloud sessions, without
   summaries.

## Anti-patterns

| Anti-pattern | Instead |
|---|---|
| Reading each transcript yourself to find out what a session does | `--summarize`; the excerpt and the cheap model are the point |
| Summarizing with `--deep` for every session | Overview first; `--deep` for the one the user picks |
| Treating `idle` as "nothing needed" | Check `待ち:` too (Rule 2) |
| Listing pids without tmux positions | `tmux <session>:<window>.<pane>` from the tree |
| Cleaning up stale sessions because they look abandoned | List them; the user decides |
