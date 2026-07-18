# Cross-agent adapters

A KB is just files, so any agent can read it. An **adapter** is a thin pointer you drop
into your project (or your home config) that tells a given agent *where the KB is* and
*how to use it*. It is a few dozen lines of text — not code, not a server.

## Adapter vs. this skill — read this first

They are different things, and **the adapter is the load-bearing one**:

| | Adapter (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`) | This skill |
|---|---|---|
| What it does | Tells the agent the KB exists, where it is, and the basic procedure | Supplies the conventions, workflows, and validator |
| When it applies | **Every session, automatically** | Only when the request matches the skill's description |
| Which agents | **All of them** (Claude Code, Codex, agy, …) | **Claude Code only** — it is a plugin |

Consequences you must not miss:

- **Installing this skill alone does not make an agent use your KB.** Without an adapter,
  an ordinary question never causes the agent to look in the KB. The adapter is what makes
  KB use *implicit*.
- **Codex and `agy` cannot install this skill at all** (plugins are a Claude Code
  mechanism). For them the adapter is the only mechanism — which is precisely how the
  "works from any agent" property is delivered.
- Recall alone works with just an adapter; the skill mainly earns its keep when *creating
  and validating* KBs.

So setup is two steps: **place an adapter** (this file), and — on Claude Code — install
the skill.

## The adapter body

The body is the same for every agent; only the filename each agent auto-loads differs.
Fill the placeholders `<KB_PATH>` (e.g. `~/.kb` or `./kb`) and the precedence list.

## The shared adapter body

```markdown
# Knowledge base

This project's durable knowledge lives in one or more knowledge bases (KBs) under
`<KB_PATH>`. Each KB is a directory with `manifest.yaml` + `INDEX.md` + records.

To answer from the KB, use ONLY what is in `<KB_PATH>` — do not fill gaps from outside
knowledge or guesses:

1. Read each KB's `INDEX.md` first (`<KB_PATH>/*/INDEX.md`). Use its topics and aliases
   to locate the right records.
2. If the index is not enough, `grep -rn <term> <KB_PATH>` for full text.
3. Read the record (Markdown) and answer from it. If the KB has no basis for something,
   say "not in the KB" rather than inventing it.

Cross-KB references use `kb/id`. When several KBs cover the same topic, the KB listed
earlier wins:

- Precedence: <kb-a>, <kb-b>, ...
```

## Where to put it: project vs user level

An adapter works at either scope, and both are verified:

- **Project level** — at the repo root, so the KB applies to that project only.
- **User level (global)** — applies in every directory, so a personal KB at `~/.kb` is
  always reachable. Verified 2026-07-19 from an empty neutral directory (no local
  convention file): all three agents auto-loaded the user-level adapter and reached the KB.

| Agent | User-level (global) path | Project-level path |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `./CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` | `./AGENTS.md` |
| Antigravity (`agy`) | `~/.gemini/GEMINI.md` | `./AGENTS.md` |

If a user-level file already exists, **append** the adapter body — do not overwrite it.

## Per-agent placement

### Claude Code — `CLAUDE.md`  ✅ verified

Put the adapter body in `CLAUDE.md` at the project root (or `./.claude/CLAUDE.md`).
Claude Code auto-loads it at session start.

To keep one shared source, put the body in a separate file and import it:

```markdown
@./kb-adapter.md
```

(`@path` imports are expanded into context at launch; up to 4 hops deep.)

**Verified 2026-07-18**: a fresh `claude -p` in the project dir auto-loaded `CLAUDE.md`
and reached the KB from a bare question, with no pointer in the prompt.

### Codex — `AGENTS.md`  ✅ verified

Put the adapter body in `AGENTS.md` at the project root. Codex reads `AGENTS.md` before
starting work (nearest file wins in a monorepo; files concatenate root→cwd).

**Verified 2026-07-18**: `codex exec` auto-read `AGENTS.md` and followed its procedure
(INDEX first) from a bare question, with no pointer in the prompt.

### Antigravity (`agy`) — `AGENTS.md`  ✅ verified

Antigravity CLI auto-reads `AGENTS.md`, so the same `AGENTS.md` you write for Codex also
serves `agy` — no extra config.

**Verified 2026-07-18**: `agy -p` auto-read `AGENTS.md` ("following the instructions in
AGENTS.md…") and reached the KB from a bare question, no pointer in the prompt. (`agy`
needs the workspace granted with `--add-dir` in headless mode; that is an `agy` sandbox
detail, not a KB requirement.)

### Gemini CLI (standalone) — `GEMINI.md` or `context.fileName`  ⚠️ not verified here

If you use the standalone `gemini` CLI instead of `agy`: it auto-loads `GEMINI.md` by
default. To make it also read `AGENTS.md`, set in `settings.json`:

```json
{ "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
```

Auto-load via `context.fileName` was **not verified** in the development environment
(`gemini` binary absent). Verify where `gemini` is installed.

## Sharing one body across agents

**At project level** the files sit side by side, so one file can serve all three:

1. Write the adapter body once in `AGENTS.md` — serves **Codex** and **Antigravity (`agy`)**
   directly (both auto-read it).
2. `CLAUDE.md` → `@./AGENTS.md` (import it) — or copy the body — for **Claude Code**.
3. Only if you use the standalone `gemini` CLI: `settings.json` →
   `context.fileName: ["AGENTS.md", "GEMINI.md"]`.

**At user level this recipe does not work as written.** The three files live in different
directories (`~/.claude/`, `~/.codex/`, `~/.gemini/`), so a relative `@./AGENTS.md` import
resolves to nothing. Place a **copy** of the body in each of the three paths instead, and
re-copy when you change it.

Do **not** wire these with symbolic links in either case (they break on Windows/OneDrive
sync); use an import (same directory only) or a copy.

**Verified 2026-07-18** on the three agents in this project's workflow — Claude Code
(`CLAUDE.md`), Codex (`AGENTS.md`), and Antigravity `agy` (`AGENTS.md`): each auto-loads
the adapter and answers a KB-dependent question with no pointer in the prompt.

## Pointing at multiple KBs

List every KB directory an agent should consider, in precedence order, in the adapter's
`Precedence:` line. The agent searches each (INDEX → grep) and, on overlap, prefers the
earlier one. This is the whole of "federation" — no index server, just an ordered set the
agent walks at query time.
