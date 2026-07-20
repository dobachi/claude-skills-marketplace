# Cross-agent adapters

A KB is just files, so any agent can read it. An **adapter** is a thin pointer you drop
into your project (or your home config) that tells a given agent *where the KB is* and
*how to use it*. It is a few dozen lines of text — not code, not a server.

## Adapter vs. this skill — read this first

They are different things, and **the adapter is the load-bearing one**:

| | Adapter (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`) | This skill |
|---|---|---|
| What it does | Tells the agent the KB exists, where it is, and the basic procedure | Supplies the conventions, workflows, and validator |
| When it applies | **Every session, automatically** | **Only when the request matches the skill's description** (trigger-activated) |
| Which agents | All of them (Claude Code, Codex, Gemini CLI, agy, …) | All of them too — each scans a skills directory (Claude Code via its plugin marketplace; Codex/agy via `~/.agents/skills`; Gemini CLI via `~/.gemini/skills`) |

Consequences you must not miss:

- **Installing this skill alone does not make an agent use your KB.** Without an adapter,
  an ordinary question never causes the agent to look in the KB. The adapter is what makes
  KB use *implicit*.
- **The reason is timing, not availability.** The skill is reachable on every agent, but a
  skill is *trigger-activated* — it fires only when the request matches its description. An
  adapter is loaded *every session*. So implicit recall on ordinary questions relies on the
  adapter, on every agent — not on the skill.
- Recall alone works with just an adapter; the skill mainly earns its keep when *creating
  and validating* KBs.

So setup is two steps: **place an adapter** (this file), and **install the skill** into
whichever agents you use.

## Install it with the script (recommended)

Do not hand-write the adapter. Run the bundled installer — it writes the body into each
agent's config file, **appending inside markers** (idempotent; it never clobbers existing
content), and it resolves the KB path for the current OS so Windows gets a Windows path
automatically:

```bash
python3 <skill-dir>/scripts/install-adapters.py            # default KB home: ~/.kb
python3 <skill-dir>/scripts/install-adapters.py --kb <path> --also ./kb --dry-run
```

It targets `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`. On a fresh
machine, this is the whole of adapter setup. (Or just ask the agent to "set up the KB
adapters" — the skill runs the script.)

## The adapter body (what the script writes)

Keep it minimal: an always-loaded pointer, nothing more. Detail lives in this skill and is
loaded only when you create or manage a KB — so the always-loaded footprint stays tiny.
Verified 2026-07-20 on Claude Code, Codex, and agy: this minimal body is enough for implicit
recall from a bare question.

Two clauses keep it from misfiring: **skip** the KB when the task already carries the
material it needs (or is unrelated to stored knowledge), and **fail open** — if the KB is
unreadable or access is denied (e.g. a headless agent with no file permission), the agent
says so and continues instead of halting. Without the fail-open clause an agent that dutifully
tries to read the KB and is denied will stop mid-task.

```markdown
# ナレッジベース（KB）

永続知識は <KB_PATH> にある（作業中プロジェクトの `./kb/` も）。一般知識で答える前に必ずKBを確認する:
各 `INDEX.md` を読み、必要なら grep。KB内の記述だけで答え、無ければ「KBに記載なし」と言う。
ただし、課題に必要な資料が既に与えられている・KBと無関係な作業ならKB参照は不要。KBが読めない/アクセス拒否のときは、その旨を一言添えて停止せず作業を続ける。
KBの作成・編集・検証は knowledge-base スキルに従う。
```

English equivalent:

```markdown
# Knowledge base

Durable knowledge lives in <KB_PATH> (and a project's `./kb/`). Before answering from
general knowledge, always check the KB: read each `INDEX.md`, grep if needed, answer only
from KB content, and say "not in the KB" when there is no basis.
Skip the KB when the task already includes the material it needs or is unrelated to stored
knowledge. If the KB is unreadable or access is denied, say so briefly and continue — do not stop.
For creating, editing, or validating a KB, follow the knowledge-base skill.
```

Everything else — the `kb/id` reference rule, precedence across many KBs, how to add a
record with aliases, portability rules — is **not** in the adapter; it is in
`kb-convention.md` / `workflows.md`, which the agent reads via the skill when it actually
manages a KB.

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
