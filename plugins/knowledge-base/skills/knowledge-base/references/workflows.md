# Workflows

The step-by-step an agent follows when using a knowledge base. Assumes the rules in
[`kb-convention.md`](kb-convention.md). Everything here is plain file operations plus
`grep` — no server, no database.

## When this skill applies

Use it when the user wants to **save, organize, or recall durable knowledge** that should
survive across sessions and be reachable from any agent: decisions, how-tos, research
findings, project context, or a structured catalog of entities.

## Setup: install the adapters (per machine)

If the user asks to "set up the KB adapter(s)", run the bundled installer — do not
hand-write the files:

```bash
python3 <skill-dir>/scripts/install-adapters.py            # default KB home ~/.kb
```

It writes a minimal, always-loaded pointer into `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`,
and `~/.gemini/GEMINI.md` (idempotent, append-only, OS-correct path — see `adapters.md`).
Tell the user to start a new agent session to pick it up.

## 0. Locate the KB(s)

- A KB is any directory containing a `manifest.yaml`. For where KBs live, `kb-convention.md`
  §0 is authoritative; in practice look in `~/.kb/` (personal) and `./kb/` (this project).
- **The adapter is the real source of truth**: check any path it names in its
  `Precedence:` line, in that order — that is what the user actually configured.
- `find ~/.kb ./kb -name manifest.yaml 2>/dev/null` lists them; read each
  `manifest.yaml` for its `kb` id and `format`.
- If the user wants to store cross-project knowledge and no home KB exists yet, offer to
  create one (§1) and to put it under git.

## 1. Create a KB

1. Choose a directory and a `kb` id (letters/digits/hyphen).
2. Write `manifest.yaml` with `kb`, `format` (`prose` or `entities`), `format_version: 1`,
   `index: INDEX.md`.
3. Write `INDEX.md`: a title, a one-line "about", and an empty "Topics" section.
4. For `format: entities`, optionally copy `entities-schema.json` from this skill's
   `references/` into the KB, so the KB carries its own format definition when copied
   elsewhere. (The bundled validator does not read it — see `kb-convention.md` §5.)
5. Run the validator — expect 0 errors. The script path is relative to **this skill's
   directory**, so use its full path:
   `python3 <skill-dir>/scripts/kb-check.py <kb-root>`

## 2. Add a record

**prose**
1. Pick a kb-local-unique `id` (kebab-case).
2. Create `<id>.md` with frontmatter `id:` (required; optional `title`, `tags`, `updated`)
   and a Markdown body.
3. **Add an `INDEX.md` entry with aliases** — synonyms and related terms someone might
   search by. This is stage-0 recall; skipping it is the most common way a record becomes
   unfindable.

**entities**
1. Frontmatter requires `id`, `type`, `name`.
2. Put scalar properties as **top-level fields** (`storage:`, `requires:`, `runtime:`…).
   Put **only record-to-record links** under `relations:`, with values that are an `id`
   (same KB) or `kb/id` (another KB). Do **not** invent a relation to an entity that does
   not exist yet.
3. Add an `INDEX.md` entry with aliases.
4. Run the validator (`python3 <skill-dir>/scripts/kb-check.py <kb-root>`) — it checks the
   required fields and warns on relations that resolve to nothing.

## 3. Recall / answer from a KB

1. **Read `INDEX.md` first.** Use its topics and aliases to find candidate records.
2. If the index is not enough, `grep -rn <term> <kb-root>`.
3. Read the record and answer **only from KB content**. If the KB has no basis, say "not
   in the KB" — do not fill from outside knowledge.
4. Cite the record path or `kb/id`.

## 4. Cross-KB search (federation at query time)

1. **Choose the target set** — which KB directories to include.
2. **Order = precedence** — earlier KBs win on conflict.
3. For each KB: `INDEX.md` → `grep` as in §3.
4. **Merge**: on overlap, take the higher-precedence KB's answer first; note the others as
   "also covered in …". Follow `kb/id` references across KBs as needed.

## 5. Maintain

- **Keep INDEX aliases current** when you add or rename records — stage-0 recall depends on
  it.
- Run `python3 <skill-dir>/scripts/kb-check.py <kb-root>` after edits: it checks the five
  invariants, the `entities` required fields, and dangling relations (warnings, not errors).
- Never add a database, lock file, or binary index **inside** the KB. Never use symlinks.
- Commit / sync the KB as plain files (Git, OneDrive, …) — it needs nothing else.

## 6. When to escalate (deferred, not v0.1)

If, at scale, `grep` gets slow or recall misses concept queries the index does not cover,
consider a **throwaway, git-ignored** local index (BM25, or a vector index as a last
resort), rebuilt per machine, with Markdown remaining the source of truth. This is stage-2
in the search plan and is **out of scope for v0.1** — reach for it only when a real need is
shown, and log that you did.
