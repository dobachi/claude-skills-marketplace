# Backlog — design notes

Design rationale for the `backlog` plugin: a lightweight, persistent "do it later" inbox
that a coding agent can capture into with one line and review in a later session.

## The need

The recurring request is "これ(タスクに)積んでおいて" / "add this to the backlog" —
park a piece of work now, act on it later. Nothing in the existing toolbox fits:

- **The session task list** (the agent's in-conversation todos) is **ephemeral** — it
  disappears when the conversation ends. It tracks the steps of the job in front of you,
  not things deferred to a future session.
- **github-issues / commit-and-report** assume GitHub and are heavyweight for a one-line
  "remember this."
- **The knowledge base (`~/.kb`)** stores *knowledge*, which has a different lifecycle
  from *actions* — mixing open tasks into it muddies both.

So `backlog` is the missing piece: a cross-session, cross-repo capture inbox that stays
out of the way.

## Storage: hybrid, resolved from context

The store is chosen automatically from the current working directory:

| Context | File | Why |
|---|---|---|
| Inside a git repo | `<repo-root>/BACKLOG.md` | Task belongs to that codebase; travels with it, reviewable in a PR, shared with the team |
| Anywhere else | `~/.claude/backlog.md` | Personal, project-agnostic inbox |

Resolution uses `git rev-parse --show-toplevel`, so any subdirectory of a repo maps to the
same `BACKLOG.md`. `-g` forces the personal inbox even inside a repo; `-r` forces the repo
file. This keeps the common case zero-config while leaving an explicit override.

**Why not one global file with project tags?** A repo-local file is git-trackable and
reviewable alongside the code it concerns, which is where most deferred *dev* work belongs.
The personal inbox catches everything else. The cost — items live in more than one file —
is paid back by the merged `list` (below).

## `list` shows both, so nothing hides

Because `add` routes by context, a naive "show the current file" would hide the personal
inbox whenever you're inside a repo ("where did the item I just parked go?"). So `list`
**always renders both** the current repo's file *and* the personal inbox, in labelled
sections with continuous numbering. Outside a repo the two coincide and only one section
shows. Default view is open items; `--all` includes completed ones.

## Lifecycle: capture → done → archive

Two-stage cleanup keeps the working file honest without losing history:

1. `done <word>` toggles `[ ]`→`[x]` and stamps `(done: YYYY-MM-DD)`. The item stays in
   place — visible, satisfying, still undoable.
2. `archive` sweeps all `[x]` items into a sibling `BACKLOG.archive.md` (or
   `backlog.archive.md`) under a dated `## YYYY-MM-DD archived` heading, leaving the
   working file with only open items. `archive --purge` deletes instead, for those who
   don't want a history trail.

`groom` is the interactive "stocktaking" pass: run `archive` to clear the done pile, then
`stale --days N` to surface long-parked open items, and walk the user through each
(keep / `done` / `drop`). The mechanical parts (`archive`, `stale`) are deterministic in
the helper; the judgement calls stay with the user.

## Safety

- `add` is append-only — never rewrites existing content.
- `done` / `drop` match by substring; if a word matches several items the helper prints
  the candidates and exits non-zero rather than guessing.
- `drop` refuses to delete without `--yes`; the skill previews the target (`find` / `list`)
  and gets the user's go-ahead first.
- The store is plain Markdown the user can hand-edit; the parser tolerates manual edits.

## File format

```markdown
# Backlog

- [ ] 2026-07-20 egress proxy で SBX_NET=none 対応  #hardening
- [x] 2026-07-19 書き込みを bwrap で隔離 (done: 2026-07-20)
```

One item per line: a checkbox, the capture date, free text, and optional `#tags`. Human
-readable and diff-friendly by design.

## Implementation

A single stdlib-only `scripts/backlog.py` (no dependencies), so the same skill runs
unchanged under Claude Code, Codex, and Antigravity (agy) — matching the repo's cross-agent
convention (cf. knowledge-base's `kb-check.py`). The `SKILL.md` is self-contained so it
survives being symlinked/copied into another agent's flat `skills/` directory.

## Future extensions (not built yet)

- **Promote to a GitHub Issue** — bridge a backlog item into `github-issues` /
  `commit-and-report` when it graduates from "someday" to "tracked work."
- **Priority / due hints** — an optional `!` priority or `@YYYY-MM-DD` due marker, sorted
  in `list`.
- **`list --all-stores`** — scan every known repo BACKLOG.md, not just the current one.
