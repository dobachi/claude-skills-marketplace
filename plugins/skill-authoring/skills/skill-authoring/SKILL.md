---
name: skill-authoring
description: The contract for adding, updating and releasing a skill in THIS marketplace (dobachi-skills) — the repo-specific half that generic skill guidance does not cover. Scaffolds the plugin layout, registers the plugin in marketplace.json and both READMEs, and gates the release on a script rather than on remembering — description length and YAML safety, the four places a description must stay in sync, version bump, site catalog freshness, validator, and any bundled test harness. Also carries the authoring guidance itself (progressive disclosure, reference-file rules, the three-directional test pattern) as references. Use when adding a new skill, editing an existing one, or before committing a skill change — スキルを追加したい, スキルを直したい, プラグインを登録, リリース前チェック. Hands the measuring of a skill (evals, trigger accuracy, A/B between versions) to the official skill-creator plugin rather than duplicating it.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Skill Authoring (this marketplace)

Generic guidance tells you how to write a good `SKILL.md`. This covers the part that is specific to
**this repository** — the layout, the four registration sites, and the checks that are easy to
forget and invisible when forgotten.

**It does not measure skills.** Running evals, tuning trigger accuracy, and A/B-ing two versions
belong to the official `skill-creator` plugin:

```
claude plugin enable skill-creator@claude-plugins-official
```

## Why this exists as a skill and not only as a document

The two references below were repo documents for months, and they were correct. The failures kept
happening anyway — a description over 1024 characters twice in one afternoon, a `": "` that broke
the YAML, a forgotten catalog regeneration, the same consistency check run by hand six times.

A document is read when someone remembers it. A skill loads when the work starts. That difference
is the whole point, and `scripts/release_check.sh` is where it becomes mechanical.

## Layout

```
plugins/<name>/
  .claude-plugin/plugin.json          name, description, version, author
  skills/<name>/
    SKILL.md                          frontmatter + body, under 500 lines
    references/                       optional; over 100 lines needs a ## Contents
    scripts/                          optional; executed, not read into context
    tests/                            optional but expected for bundled scripts
    evals/evals.json                  optional; official format, run by skill-creator
```

The name must be **identical** in four places: the directory, `SKILL.md` frontmatter,
`plugin.json`, and `marketplace.json`.

## Workflow

```
0. DECIDE     What does this skill own that no existing skill owns? Name the sibling
              it hands off to. A skill that overlaps a sibling gets triggered instead of it.
1. SCAFFOLD   scripts/new_skill.sh <name>
              Creates the layout, plugin.json, a SKILL.md skeleton, and registers it
              in marketplace.json. README rows are printed for you to paste.
2. WRITE      references/authoring-best-practices.md — frontmatter rules, progressive
              disclosure, reference-file rules, the three-directional test pattern.
3. TEST       Bundled a script? Ship tests/ with permanent fixtures. Three directions:
              clean → 0, defect-injected → 1, precondition missing → 2.
              Include a fixture shaped UNLIKE this repo's own documents.
4. CHECK      scripts/release_check.sh <name>          ← the gate. Run before committing.
5. INSTALL    ./install.sh   then  /reload-plugins  in a live session.
6. COMMIT     commit-safe. No AI signature — this repo's commits carry none.
7. MEASURE    Optional, and only via skill-creator. Not this skill's job.
```

## The gate

`scripts/release_check.sh <name>` fails on the things that are invisible when they go wrong:

| Check | Why it is here |
|---|---|
| `description` ≤ 1024 chars, parses as YAML, no XML tag | Over-length is rejected by claude.ai; a bare `": "` silently breaks the frontmatter |
| Registered in `plugin.json`, `marketplace.json`, `README.md`, `README_ja.md` | Four places, and missing one is not visible from any other |
| `version` bumped when skill files changed | An unchanged version means installs do not pick the change up |
| `site/skills/_catalog.md` regenerated | Generated from `marketplace.json`; a stale catalog contradicts the README |
| `SKILL.md` under 500 lines; reference files over 100 have a TOC | Official guidance; the loaded body is a recurring token cost |
| `tools/validate_skills.py --only <name> --strict` | Frontmatter against the Agent Skills spec, registration, links |
| `tests/run_tests.sh` if present | A detector that stopped detecting reads exactly like a clean pass |

Exit `0` ready, `1` findings, `2` usage error.

## Rules that keep being broken

1. **`description` must not contain `": "`.** An unquoted YAML scalar ends at the first colon-space.
   The frontmatter still looks fine and the skill silently fails to load.
2. **Descriptions live in four files.** Change one, change all four, then regenerate the catalog.
3. **Bump the version on every shipped change.** `install.sh` compares versions; without a bump the
   change does not reach an installed copy.
4. **Fixtures belong in the repo, not in `/tmp`.** Controls that evaporate with the session are the
   reason a bug survives to the next release.
5. **Test the harness by breaking the code.** Revert a real past bug; if the suite stays green, it
   is not a suite.
6. **Do not overlap a sibling skill.** Say what this one hands off, in the description itself.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| Writing SKILL.md first, testing later | Documents imagined problems; official guidance is evals first | Decide the failing case, then write |
| A description that lists capabilities only | Triggering needs *when*, not just *what* | What it does + when + what it hands off |
| Copying a sibling's whole approach into a new skill | Two skills compete for the same trigger | Own one job; name the handoff |
| Validating only on this repo's own documents | Dogfooding exercises only shapes you already have | A fixture shaped unlike your repo |
| "It passed, ship it" with no defect-injected case | A broken detector and a clean pass are the same output | Three directions |
| Hand-checking the four registration sites | Six manual runs in one afternoon, and one still missed | `release_check.sh` |

## References

- `references/authoring-best-practices.md` — how to write the content: frontmatter rules against the
  Agent Skills spec, progressive disclosure, reference-file rules, the three testing layers
- `references/registration-runbook.md` — the step-by-step registration procedure, including importing
  a packaged `.skill` file
