# KB Convention (v0.1)

The rules that define a knowledge base for this skill. Self-contained: everything a
person or agent needs to create, read, and search a KB by hand, with no external tools.

## 0. Where a KB lives

A KB is separate from this skill. The skill is installed and updated under the plugin
directory; your knowledge must **not** live there (it would be overwritten and cannot be
synced). Put KBs where you own and sync them:

- **Personal / cross-project knowledge** → a home directory, conventionally **`~/.kb/`**,
  where each subdirectory that has a `manifest.yaml` is one KB. Keep it under git (or any
  file-sync tool) to carry it between machines.
- **Project-specific knowledge** → `./kb/` inside that project's repo, so it travels with
  the project.

To keep a home somewhere else (a OneDrive/Dropbox folder, another disk), just put it
there and **write that path into your adapter** — nothing in the format depends on the
location, and everything is plain text, so any sync tool works.

An agent is pointed at these by an adapter (`AGENTS.md` / `CLAUDE.md`); see
`adapters.md`. Absolute paths like `~/.kb` live only in the machine-local
adapter, never inside a KB's records (records reference each other by `kb/id`).

## 1. A KB is a directory

One KB = one directory. Create it with `mkdir`, share it by copying, delete it with
`rm -r`. Minimum contents:

```
<kb-dir>/
├── manifest.yaml     # required — the KB's self-description
├── INDEX.md          # required — the table of contents an agent reads first
└── <records...>      # records; layout depends on the format (§4, §5)
```

The directory name is free; the KB's identifier is `kb:` in the manifest, not the folder
name.

## 2. manifest.yaml (required)

```yaml
kb: architecture-notes        # this KB's id (letters/digits/hyphen); left side of kb/id refs
format: prose                 # prose | entities  (future: ossie, ...)
format_version: 1             # the format's version; the core ignores it, format tools read it
index: INDEX.md               # index filename (default INDEX.md)
title: Architecture notes     # optional, human-facing
description: Design decisions  # optional
```

`kb`, `format`, `format_version` are required. Do **not** mix formats in one directory;
use separate KBs instead.

## 3. INDEX.md (required) — the curated index

The first thing an agent reads. It need not list every record; it captures *where things
are* and, crucially, **aliases / related terms** so a query worded differently still finds
the record. Writing the synonyms here is how vocabulary gaps are handled without embeddings.

```markdown
# Architecture notes (INDEX)

## Topics
- [Storage format decision](decisions/storage-format.md) — aka: on-disk format, storage, Markdown vs DB
- [Search staging](decisions/search-staging.md) — aka: grep, vector search, recall
```

## 4. `prose` format

Narrative knowledge. One record = one Markdown file. Frontmatter is minimal.

```markdown
---
id: storage-format          # unique within the KB; referenced as architecture-notes/storage-format
title: Storage format decision
tags: [storage, format]     # optional
updated: 2026-07-18         # optional, ISO 8601
---

Body — free Markdown.
```

Only `id` is required. Subfolders are free; `id` must be unique within the KB.

## 5. `entities` format

Typed entities and relationships (a light knowledge graph). One record = one entity = one
Markdown file.

```markdown
---
id: grounded-research
type: skill
name: Grounded Research
storage: markdown           # attributes: plain top-level fields
requires: [web-search]
relations:                  # relations: links to OTHER records only
  alternative_to: [deep-research]
  authored_by: [dobachi]
tags: [research]
---

Body — free Markdown describing this entity.
```

Required frontmatter: `id`, `type`, `name`.

`entities-schema.json` (this directory) is the machine-readable statement of that format —
use it with any JSON Schema tool, or ship a copy inside the KB so the KB documents its own
format when copied elsewhere. Note that `scripts/kb-check.py` does **not** read that file;
it applies the same required-field and id-pattern checks internally, so editing the schema
does not change what the bundled validator enforces.

**Keep relations and attributes separate** (learned in dogfooding):

- `relations` values MUST be another record's `id` (same KB) or `kb/id` (another KB).
- Scalar properties (`storage: markdown`) and concept-level dependencies
  (`requires: [vector-db]`, where `vector-db` is not a record) are **top-level fields**,
  not relations. Putting a concept in `relations` produces a link that resolves to nothing.
- If the entity a relation should point to does not exist yet, **do not invent the
  relation** — leave it out until that entity exists.

## 6. IDs and references

- Record ids are **KB-local**. There is no global unique id.
- Same-KB reference: `id` (e.g. `storage-format`).
- Cross-KB reference: `kb/id` (e.g. `skills-catalog/grounded-research`), where the left
  part is the target's `manifest.kb`.
- An unresolved reference is treated like a search returning nothing — **it is not a fatal
  error**. Copying one KB alone must not break it.

## 7. Multiple KBs: separate by default, federate at query time

The core does not merge stores. To search across KBs, do it as an explicit operation:

1. **Choose the target set** — list the KB directories to include.
2. **Order = precedence** — earlier KBs win.
3. **Search each** — read each KB's `INDEX.md`, then `grep -rn <term> <kb-dir>` if needed.
4. **Merge** — when the same topic appears in several KBs, take the higher-precedence one
   first and note the others.

Build a helper script for this only once the by-hand procedure proves insufficient.

## 8. Invariants every format must satisfy

The core relies only on these five. Check them whenever a new format is added.

1. It is text files (copy-portable; syncs and diffs via Git / OneDrive).
2. There is a `manifest.yaml` (declaring `format` and `format_version`).
3. There is an `INDEX` (`manifest.index`).
4. Records are addressable as `kb/id` (no global unique ids).
5. `grep` works (a format-agnostic full-text floor).

Format-specific structure stays inside the KB, opaque to the core. Format-aware search
(e.g. querying metrics) layers on top as a format tool — never in the core.

## 9. Search, staged

Do not reach for a vector DB first. Add capability only when a real need is shown.

- **Stage 0 (default):** the curated `INDEX.md` (§3). Aliases absorb vocabulary gaps.
- **Stage 1:** `grep` / `ripgrep` for full-text. Zero extra dependencies.
- **Stage 2 (only if proven necessary):** a throwaway, git-ignored local index (BM25, or a
  vector index as a last resort), rebuilt per machine. The Markdown stays the source of truth.

## 10. Portability rules

- Everything is text, so Git / OneDrive / Dropbox all work and conflicts are readable.
- **No symbolic links** (they break on Windows/OneDrive sync).
- On Windows + OneDrive, avoid case-only filename differences (`Notes.md` vs `notes.md`).
- Never put a database or lock file inside the KB; a rebuildable index (stage 2) lives
  outside sync.

## Minimal example

`my-kb/manifest.yaml`:
```yaml
kb: my-kb
format: prose
format_version: 1
```

`my-kb/INDEX.md`:
```markdown
# my-kb (INDEX)
## Topics
- (add entries here)
```

Add `my-kb/*.md` files with an `id`, and you can `grep -rn <term> my-kb/` and carry the
folder anywhere.
