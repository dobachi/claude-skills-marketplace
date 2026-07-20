---
name: backlog
description: A lightweight, persistent "do it later" inbox — capture a task in one line and review it in a later session. Use whenever the user wants to defer or park work: "これ(タスクに)積んでおいて", "あとでやる", "TODOに入れて", "バックログに追加", "棚卸しして", "put this on the backlog", "add to my todo", "remind me to … later", "what's on my backlog", "clear out the done items". Hybrid storage: inside a git repo it uses <repo>/BACKLOG.md (shared via git); otherwise ~/.claude/backlog.md (personal inbox). Not for tracking the steps of the task in progress right now — that's the session task list.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Backlog — a persistent do-it-later inbox

Capture deferred work in one line and pick it up in a later session. This is the
cross-session counterpart to the ephemeral session task list: use the **session task
list** for the steps of the job in front of you; use **backlog** for "park this and
remind me later."

All operations go through the bundled helper. The path is relative to **this skill's
directory** — invoke it with the full path:

```bash
python3 <skill-dir>/scripts/backlog.py <subcommand> …
```

## Storage (hybrid, automatic)

The helper picks the store from the current working directory — no need to specify it:

- inside a git repo → `<repo-root>/BACKLOG.md` (travels with the repo, reviewable in a PR)
- otherwise → `~/.claude/backlog.md` (personal inbox)

`list` always shows **both** the current repo's file and the personal inbox, so nothing is
ever hidden. Override the target with `-g` (force personal) or `-r` (force this repo).

## Subcommands

| Intent | Command |
|---|---|
| Park a task | `backlog.py add "<text>" [--tag foo] [-g]` |
| Review (open items, repo + personal) | `backlog.py list` |
| Review incl. done | `backlog.py list --all` |
| Preview what a word matches | `backlog.py find <word>` |
| Mark done | `backlog.py done <word>` |
| Delete | `backlog.py drop <word> --yes` |
| Sweep done items into the archive file | `backlog.py archive` |
| Purge done items (no archive) | `backlog.py archive --purge` |
| Long-untouched open items | `backlog.py stale --days 30` |

`add` is append-only (always safe). `done` toggles `[ ]`→`[x]` and stamps the completion
date. `archive` moves `[x]` items into `BACKLOG.archive.md` (repo) / `backlog.archive.md`
(personal), leaving the working file lean.

## Routing intent → command

- **"これ積んでおいて / あとでやる / add to backlog"** → `add`. Write a self-contained one
  line (what, and enough context to act on it later). Add `#tags` via `--tag` if useful.
- **"バックログ見せて / what's on my backlog"** → `list` (no subcommand also works).
- **"〜done / 終わった"** → `done <word>`. If the word matches several items the helper
  exits non-zero and prints the candidates — re-run with a more specific word.
- **"消して / drop"** → first `find <word>` (or `list`) to show the exact target, get the
  user's go-ahead, then `drop <word> --yes`. Never pass `--yes` before the user has seen
  what will be deleted.
- **"棚卸し / 消し込み / clear out done"** → `archive` (default: keep history in the archive
  file; `--purge` to delete outright).
- **"棚卸しレビュー / groom"** (guided) → run `archive` to sweep done items, then
  `stale --days <N>` to surface long-parked open items, and walk the user through each one
  (keep / `done` / `drop`). This is the interactive "stocktaking" pass.

## Notes

- Dates come from the local clock. Today is known from context; pass `--date YYYY-MM-DD`
  only if you need to override it.
- The file is plain Markdown — the user can also edit it by hand; the helper tolerates that.
- Requires `python3` on `PATH` (standard library only; no dependencies).

## Examples

```bash
# Park a task (auto-routes to the repo's BACKLOG.md when inside a repo)
python3 <skill-dir>/scripts/backlog.py add "egress proxy で SBX_NET=none 対応" --tag hardening

# A personal note even while inside a repo
python3 <skill-dir>/scripts/backlog.py add -g "確定申告の準備"

# Review everything relevant, then close one out
python3 <skill-dir>/scripts/backlog.py list
python3 <skill-dir>/scripts/backlog.py done proxy

# Stocktaking: sweep done items away, then look at what's gone stale
python3 <skill-dir>/scripts/backlog.py archive
python3 <skill-dir>/scripts/backlog.py stale --days 30
```
