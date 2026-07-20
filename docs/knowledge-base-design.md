# knowledge-base — Concept and Design

Why the `knowledge-base` skill is built the way it is, and why it deliberately does *not*
reach for the thing most agent-memory projects reach for first.

This document is the rationale, and is self-contained. The skill itself lives in
[`plugins/knowledge-base/skills/knowledge-base/`](../plugins/knowledge-base/skills/knowledge-base/),
whose `references/` carry the convention, the workflows, and the adapters in full.

## The problem

An agent forgets everything between sessions. The obvious fix — bolt on a memory service —
is what most projects build: a vector database, an embedding pipeline, a server process.
That works, and it costs you the two properties that matter most for *personal* knowledge:

- **You stop owning your knowledge.** It lives in a database you cannot read, diff, or
  hand-edit.
- **It stops travelling.** You cannot copy it to a USB stick, sync it through OneDrive, or
  hand one KB to a colleague without exporting.

And it buys a third problem: it ties your knowledge to *one agent*. A Claude Code plugin
cannot be installed into Codex or Antigravity.

## The design

**A knowledge base is a directory of plain Markdown. That is the whole storage layer.**

```
<kb>/
├── manifest.yaml     # kb id, format, format_version
├── INDEX.md          # curated table of contents WITH ALIASES
└── <records>.md      # frontmatter + body
```

Five invariants hold for every format, and the skill relies on nothing else: it is **text
files**, there is a **manifest**, there is an **INDEX**, records are addressable as
**`kb/id`**, and **grep works**. Anything format-specific stays inside the KB, opaque to
the core — so a new format is a new `format:` value plus a schema, never a change to the
core.

### Why no vector database

Retrieval is staged, cheapest first:

0. the curated `INDEX.md` — **aliases in the index absorb vocabulary mismatch**, which is
   the job embeddings are usually hired for;
1. `grep` / `ripgrep`;
2. only if a real need is demonstrated, a **throwaway, git-ignored** local index, with
   Markdown still the source of truth.

Stage 2 is deliberately out of scope for 0.1.0. The evidence for stages 0–1 being enough is
real but bounded, and the skill says so rather than overclaiming: measured comparisons show
lexical search beating dense retrieval in some agent harnesses and losing in others, and the
paper most often cited for "grep is enough" explicitly refuses to generalize. So the design
starts minimal and escalates on evidence, instead of paying the vector-DB cost up front.

### Why the KB never contains a database

SQLite's own documentation warns that its locking has misbehaved on network filesystems and
that this has caused corruption; sync tools resolve conflicts by duplicating whole files.
A KB that is only text therefore survives Git, OneDrive, and Dropbox alike, and its
conflicts are readable. For the same reason the skill uses **no symbolic links** — Dropbox
on Windows does not sync them.

### Why multiple KBs, separate by default

Different knowledge has different structure, and forcing it into one store is what makes
knowledge bases rot. So: **one KB is one directory**, IDs are **KB-local** (no global id
namespace), and cross-KB references are `kb/id`. Federation happens **at query time** — the
agent walks an ordered set of KBs and prefers the earlier one — rather than by merging
stores. Prior art does one or the other; doing both is the point of this design.

### Why an adapter, and why it is not the skill

The skill runs on every agent that scans a skills directory — Claude Code (via its plugin
marketplace), Codex and Antigravity `agy` (via `~/.agents/skills`), Gemini CLI (via
`~/.gemini/skills`). But a skill is *trigger-activated*: it fires only when a request
matches its description. So the skill is **not** the mechanism that makes an agent consult
your KB on an *ordinary* question. An **adapter** is: a few lines of text in the file each
agent already auto-loads *every session* (`CLAUDE.md`, `AGENTS.md`, `~/.gemini/GEMINI.md`),
naming the KB locations and the procedure. That always-loaded pointer is what makes KB use
implicit, and it is what delivers "works from any agent". The skill supplies the
conventions, workflows, and validator on top, and is invoked when you actually create or
manage a KB.

This split is the single most important thing for a user to understand, so
`references/adapters.md` states it first.

## What this skill deliberately does NOT do

- No vector database, no embedding pipeline, no server or MCP process as a requirement.
- No custom storage format, no binary index, no lock files inside the KB.
- No global unique IDs, and no implicit single "the" KB at a hardcoded path.
- No sync or history mechanism of its own — that is Git's (or your sync tool's) job.

## Validation

The design was dogfooded and measured rather than asserted:

- **Convention**: two real KBs (`prose` and `entities`, 15 records) were built to the spec.
  Doing so exposed a real defect — attributes had been modelled as `relations`, producing
  links that resolved to nothing — which is why the convention now separates record-to-record
  `relations` from top-level attribute fields.
- **Cross-KB references** resolve in practice (`kb/id` from one KB into another).
- **Adapters**: from a neutral empty directory, with the adapter only at user level and no
  pointer in the prompt, **Claude Code, Codex, and Antigravity (`agy`) each auto-loaded the
  adapter, found the KB, read `INDEX.md`, and answered from the records**. Recall via the
  curated index alone (no grep) was observed, as was grep fallback.
- Not verified: the standalone `gemini` CLI's `context.fileName`. The skill says so.

## Cost

Effectively zero at rest: the KB is text on disk, and recall is one index read plus, at
most, a `grep`. The validator (`scripts/kb-check.py`) is stdlib-only Python. There is no
service to run, nothing to pay for, and nothing to keep warm.
