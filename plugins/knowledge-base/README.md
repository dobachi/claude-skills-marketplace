# knowledge-base

A persistent knowledge base your AI agent can use across sessions — and across
different agents. It is built to stay small, to travel anywhere, and to let you keep
several separate knowledge bases at once.

## What you get

- **Knowledge that survives sessions.** Save a fact, a decision, or a how-to once; your
  agent can recall it later instead of you re-explaining it every time.
- **Files you own, in plain Markdown.** Your knowledge is plain text on your disk — no
  database, no server, no lock-in. Open it in any editor, read it with your own eyes,
  edit it by hand.
- **Carry it anywhere.** A knowledge base is just a folder. Copy it to a USB stick, sync
  it through Git, Dropbox, or OneDrive — it keeps working. Nothing to install on the
  other side, nothing to start up.
- **Works from any agent.** The same knowledge is reachable from Claude Code, Codex, and
  Antigravity (`agy`) — verified — and from anything else that can read files, because
  underneath it is only files.
- **Keep several knowledge bases.** A work KB and a personal KB. A prose KB and a
  structured KB. They stay separate by default; you choose which ones to search together
  when you want to.

## How it works

### A knowledge base is a folder

```
my-knowledge/
├── manifest.yaml     # this KB's name and format
├── INDEX.md          # the table of contents your agent reads first
├── decisions/        # your notes, as Markdown files
│   └── db-choice.md
└── ...
```

Creating a KB is making a folder. Sharing it is copying the folder. Deleting it is
deleting the folder. There is no separate app to run.

### Where your knowledge lives

Your knowledge is yours and lives separately from the skill:

- **Personal, cross-project knowledge** goes in a home folder — conventionally `~/.kb/`,
  with one KB per subfolder, kept under git. To keep it somewhere else (a OneDrive or
  Dropbox folder, say), put it there and write that path into your adapter; nothing in the
  format depends on the location.
- **Project-specific knowledge** goes in `./kb/` inside that project, so it travels with
  the project's repo.

The skill (installed via the marketplace) never holds your knowledge — so updating or
reinstalling it never touches your KBs.

### Two kinds of knowledge (more later)

- **prose** — ordinary notes: memos, how-tos, decisions, meeting notes.
- **entities** — structured things and their relationships: people, terms, products,
  and how they connect.

Each KB says which kind it is in its `manifest.yaml`. Future kinds can be added without
changing anything you already have.

### Finding things

Your agent reads a short **index** first (a curated table of contents you and the agent
keep up to date), then falls back to plain text search across the files. You do not need
to run or maintain any search engine. If a knowledge base ever grows large enough to need
a faster index, that index is built locally and is disposable — your Markdown files
always remain the real source, so nothing is lost if the index is deleted.

### Using it from your agent

Setup is two steps: **place an adapter**, and — on Claude Code — **install this skill**.

The adapter is a short text file, placed where your agent already looks, that says where
the KB is and how to use it. It is what makes the agent consult the KB *without being
asked* — which the skill alone does not do, because a skill fires only when a request
matches its description, whereas the adapter is loaded every session. (The skill itself
runs on all of these agents, not just Claude Code.)

- **Claude Code** — `CLAUDE.md` (project) or `~/.claude/CLAUDE.md` (all projects). Verified.
- **Codex** — `AGENTS.md` (project) or `~/.codex/AGENTS.md`. Verified.
- **Antigravity (`agy`)** — the same `AGENTS.md`, or `~/.gemini/GEMINI.md`. Verified.
- **Standalone `gemini` CLI** — a `context.fileName` setting. Not yet verified.

## Portability notes (please read before syncing)

- **Git / OneDrive / Dropbox all work** because everything is text. Conflicts, when they
  happen, are ordinary text conflicts you can read and resolve.
- **On Windows + OneDrive**, avoid case-only filename differences (`Notes.md` vs
  `notes.md`) — the sync layer treats them as the same file.
- **No symbolic links** are used, on purpose, so sync tools that do not follow symlinks
  (notably Dropbox on Windows) will not break your KB.

## Status & roadmap

Version 0.1.0. The convention, both formats, the recall/creation workflow, the adapters,
and a validator are in place; the adapters are verified on three agents. A throwaway local
index for very large KBs is deliberately out of scope for this release.

The design rationale — why there is no vector database, why the KB never contains a
database, and how the adapter/skill split delivers cross-agent use — is in
[knowledge-base — Concept and Design](https://github.com/dobachi/claude-skills-marketplace/blob/main/docs/knowledge-base-design.md).
