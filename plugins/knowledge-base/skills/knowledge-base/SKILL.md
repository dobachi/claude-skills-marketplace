---
name: knowledge-base
description: A minimal, portable, cross-agent persistent knowledge base. Stores knowledge as plain Markdown, where one KB is one directory that works by copying the folder — no server, no database — syncable via Git or OneDrive. Supports multiple KBs, each declaring its own format (prose or entities, with room for more). Use when the user wants to save, recall, or organize durable knowledge that survives across sessions and works from any agent.
---

# Knowledge Base

A persistent knowledge base that any AI agent can use in common — **minimal, portable,
cross-agent, and multi-KB**. Knowledge is plain Markdown; one KB is one directory that
works by copying the folder, with no server and no database.

**Where KBs live**: conventionally `~/.kb/` (personal, one KB per subdirectory) and
`./kb/` (this project). The user's adapter names the authoritative set — see below.

> **Prerequisite — this skill alone is not enough.** An agent only consults a KB
> *implicitly* when an **adapter** is in place. Read
> [`references/adapters.md`](references/adapters.md) for what an adapter is, how it
> differs from this skill, and where to put it.

**The full, self-contained rules are in [`references/kb-convention.md`](references/kb-convention.md).**
Read it before creating or editing a KB. Summary of the contract:

- **One KB = one directory** with `manifest.yaml` + `INDEX.md` + records.
- **Formats**: `prose` (narrative Markdown) and `entities` (typed entities + relations;
  the format is stated in [`references/entities-schema.json`](references/entities-schema.json)).
  Reserved for later: `ossie` (metrics/semantic layer), only if a warehouse-backed KB is
  needed.
- **Five invariants** every format keeps: text files · a manifest · an INDEX · `kb/id`
  addressing · grep works. New formats add nothing to the core.
- **Search is staged**: curated INDEX (aliases absorb vocabulary gaps) → grep → a
  throwaway git-ignored index only if proven necessary.
- **Multiple KBs**: separate by default, federate at query time by choosing a target set
  and precedence order. IDs are KB-local; cross-KB refs are `kb/id`.
- **Portable**: no symlinks, no DB/lock files inside the KB; Git/OneDrive-safe.

## Wiring an agent to a KB

Adapters — and where each agent auto-loads them — are in
[`references/adapters.md`](references/adapters.md). Verified: **Claude Code**
(`CLAUDE.md`), **Codex** (`AGENTS.md`), and **Antigravity `agy`** (`AGENTS.md`; user-level
`~/.gemini/GEMINI.md`). Not verified: the standalone `gemini` CLI's `context.fileName`.
One body serves all of them — share it with an import (same directory) or a copy, never a
symlink.

## How to operate a KB

**Read [`references/workflows.md`](references/workflows.md) before creating, adding to, or
recalling from a KB.** It has the step-by-step: locate, create, add a record, recall,
cross-KB search, maintain. In short — read `INDEX.md` first, fall back to `grep`, answer
only from KB content, and keep the index's aliases current.

## Validating a KB

`scripts/kb-check.py` (stdlib only) checks the five invariants, the `entities` required
fields, and whether `relations` resolve to real records. The path is relative to **this
skill's directory**, so invoke it with the full path:

```bash
python3 <skill-dir>/scripts/kb-check.py <kb-root>
```

