# Packaging skills for Claude Desktop / claude.ai

How to get skills from this repo into the Claude Desktop app (or claude.ai web).
For writing skills, see [skill-authoring-best-practices.md](./skill-authoring-best-practices.md);
for registering them in the Claude Code marketplace, see
[adding-or-updating-a-skill.md](./adding-or-updating-a-skill.md).

## What's possible, and what isn't

Custom skills **do not sync across surfaces**. A skill in Claude Code's
`~/.claude/skills` (or this marketplace) is not visible in claude.ai or the
Desktop app, and vice versa — Anthropic's docs state this explicitly and tell
you to "implement your own synchronization process." The Skills API
(`POST /v1/skills`) is a *separate* store again: skills uploaded there are not
available on claude.ai, so it isn't a backdoor either.

That leaves two real paths, both **manual, one zip per skill**:

| Path | Reaches | Where | Plans |
|---|---|---|---|
| Personal upload | Just you | Skills settings → upload a `.zip` | Pro / Max / Team / Enterprise (**not** Free) |
| Org provisioning | Everyone in the org | Organization settings → Skills → Add `.zip` | Team / Enterprise only |

There is no bulk-upload API and no CLI (`anthropics/claude-code` issue #25771,
"programmatic skill deployment", was closed *not planned*). So this tooling
automates the half that *can* be automated — **packaging and validation** — and
leaves the upload to you, with a checklist.

## The two tools

### `tools/validate_skills.py` — the skill contract

Checks every `SKILL.md` against the Agent Skills contract. Two severities:

- **ERROR** — broken on any surface: invalid YAML frontmatter, missing
  `name`/`description`, `name` ≠ directory, plugin not in `marketplace.json`.
  Exit 1.
- **desktop** — valid in Claude Code but rejected by claude.ai / the Skills API:
  reserved word (`anthropic`/`claude`) in `name`, `description` over 1024 chars,
  XML tags. Warned by default (Claude Code tolerates these); `--strict` promotes
  them to errors.

```bash
python3 tools/validate_skills.py              # all skills, ERRORs fail
python3 tools/validate_skills.py --strict     # also fail on claude.ai/API findings
python3 tools/validate_skills.py --only doc-review
```

This runs in CI on every `plugins/**` change
([`.github/workflows/validate-skills.yml`](../.github/workflows/validate-skills.yml)),
so a malformed frontmatter can no longer merge unnoticed. It is also the check
step for [adding-or-updating-a-skill.md](./adding-or-updating-a-skill.md).

### `tools/pack-desktop.py` — the zips

Validates (in `--strict` mode), then writes correctly shaped per-skill zips —
one top-level `<skill>/` folder with `SKILL.md` inside — plus an upload
checklist and a hash ledger.

```bash
python3 tools/pack-desktop.py                 # the 'viable' set
python3 tools/pack-desktop.py --experimental  # also the script-bearing ones
python3 tools/pack-desktop.py --only fact-checker
```

Output lands in `dist/desktop/` (git-ignored):

```
dist/desktop/
  <skill>.zip …
  UPLOAD.md        # ordered checklist; NEW / CHANGED / unchanged per skill
  .manifest.json   # content hashes, so a re-pack tells you what to re-upload
```

Zips are deterministic — an unchanged skill hashes identically across runs, so
`UPLOAD.md` can flag exactly which skills changed and need re-uploading.

## What gets packaged: `tools/desktop-manifest.yaml`

"Does this skill work on Desktop?" is a judgement, not something to detect, so
it's written down. Every skill on disk must appear in exactly one bucket, or the
packer refuses to run (this is how a newly added skill gets noticed):

- **viable** — prose / reasoning skills with no runtime dependency on scripts,
  subagents, or an external CLI. They already are pure-instruction skills.
- **experimental** — bundle scripts or assume tools that may not exist in the
  claude.ai sandbox (Node, Puppeteer, python-pptx, the Task tool). Packaged only
  with `--experimental`. **Upload and test before trusting.**
- **excluded** — can't work by construction: CLI-delegation skills (shell out to
  `claude`/`agy`/`codex`), repo/environment skills (act on a local git repo or
  the Claude Code install), and the EA toolchain (local model files). Each entry
  records why.

## Uploading

1. `python3 tools/pack-desktop.py` (add `--experimental` if you want those too).
2. Open `dist/desktop/UPLOAD.md` and work down the list.
3. In the Claude app, upload each `.zip` at the skills entry point.

## Open questions to confirm on first real upload

Two things the docs don't settle — resolve them empirically, don't guess:

1. **Do experimental skills actually run?** claude.ai's sandbox has
   settings-dependent network access, so `fact-checker` (Puppeteer) and
   `literature-search` (Node + external APIs) may not work. `fact-checker` also
   uses the Task tool for parallel verification, which claude.ai doesn't have —
   so even if it loads, that path won't fan out. Upload one, run it, see.
2. **The upload UI path.** Official sources disagree on the label — "Customize >
   Skills", "Settings > Features", "Settings > Capabilities > Skills". Find the
   one your build shows and update `UPLOAD.md`'s prerequisites if useful.
