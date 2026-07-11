---
name: codex-delegate
description: Delegate a task from the current coding agent to OpenAI Codex CLI (`codex exec`), running it non-interactively and using only its final output. Explicit-invocation only — trigger when the user says "codexに投げて", "codexで調べて/やって", "delegate this to codex", "ask codex", "use codex to …", or otherwise explicitly asks to hand work to Codex. Read tasks run directly in a read-only sandbox; any write goes through a preview→confirm→apply gate. Not for auto-delegation.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Delegate to Codex CLI

Hand a self-contained task to **OpenAI Codex CLI** in non-interactive mode
(`codex exec`), capture its stdout, and use only the final deliverable.

## When to use

**Only on explicit request.** Delegate when the user asks to hand work to Codex
("codexに投げて", "codexでやって", "ask codex", "delegate to codex"). Do **not**
auto-delegate — reaching for another agent is the user's call.

Good fits: a second-opinion review, an isolated refactor that would bloat your context,
a task where you specifically want Codex's model/behavior.

## Preconditions

- `codex` is on `PATH` (`command -v codex`). If missing, tell the user and stop.
- Codex reads its prompt as the argument to `codex exec`. It starts with **zero
  context** — the prompt must be complete on its own (absolute paths, exact task,
  desired output shape, boundaries).
- `codex exec` expects a git repo by default; add `--skip-git-repo-check` for non-git
  directories.

## Read / analyze / search → run directly (read-only)

```bash
codex exec -s read-only "<self-contained prompt>" 2>&1
# options: -m <model>   -C <working-dir>   --json   -o <last-message-file>
#          --skip-git-repo-check   timeout 5m codex exec ...   (OS timeout)
```

`-s read-only` sandboxes Codex so it cannot write. Safe to run after the normal Bash
permission prompt; no extra confirmation needed.

## Write (edits / file creation / side effects) → preview → confirm → apply

Codex in `exec` mode cannot pause to ask you mid-run, so insert the confirmation
**before** the write:

1. **Preview** — run read-only and have Codex emit the proposed change as a diff:
   ```bash
   codex exec -s read-only "<task>. Do not write files; output the full unified diff of the change you propose." 2>&1
   ```
2. **Confirm** — show the diff to the user and get an explicit go/no-go.
3. **Apply** — only on approval, either:
   ```bash
   codex apply                       # apply the diff Codex just produced, or
   codex exec -s workspace-write --add-dir <dir> "<task>" 2>&1
   ```
   `--dangerously-bypass-approvals-and-sandbox` may be added **only here**, after the
   user approved the previewed change — never on an un-previewed write.

Two gates protect writes: these instructions (soft) **and** the host's Bash permission
prompt on the actual command (hard).

## Prompt construction

- Absolute file paths; state the exact task and the **required output shape**.
- Set boundaries: "do not modify anything outside `<dir>`".
- For machine-readable results, add `--json` (JSONL events) or `-o <file>` (final
  message to a file) and parse that.

## Output handling

Append `2>&1`. Surface Codex's final deliverable; don't replay its intermediate
reasoning. Report failures (non-zero exit, timeout) verbatim.

## Continue a prior delegation

```bash
codex exec resume --last "<follow-up prompt>" 2>&1
```

## Examples

```bash
# Read: second-opinion review
codex exec -s read-only "Review /home/me/proj/src/auth.py for security bugs. List findings as a numbered markdown list; no code changes." 2>&1

# Write: preview then apply
codex exec -s read-only "In /home/me/proj, add input validation to create_user(). Output the unified diff only; do not write." 2>&1
# → show diff, get approval →
codex apply
```
