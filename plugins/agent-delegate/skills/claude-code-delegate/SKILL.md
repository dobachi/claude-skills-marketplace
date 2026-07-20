---
name: claude-code-delegate
description: Delegate a task from the current coding agent to another Claude Code instance (`claude -p`), running it non-interactively and using only its final output. Explicit-invocation only — trigger when the user says "別のclaudeに投げて", "claude codeでやって", "delegate this to claude", "sub-claudeにやらせて", "use a fresh claude to …", or otherwise explicitly asks to hand work to a separate Claude Code. Read tasks run in plan mode; any write goes through a plan→confirm→apply gate. Useful for isolated context or a different model. Not for auto-delegation.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Delegate to another Claude Code

Hand a self-contained task to a **separate Claude Code instance** in non-interactive
print mode (`claude -p`), capture its stdout, and use only the final deliverable.

## When to use

**Only on explicit request.** Delegate when the user asks to spin up a separate Claude
("別のclaudeに投げて", "fresh claudeでやって", "delegate to claude"). Do **not**
auto-delegate.

Good fits: isolating a big subtask in its own context window, running a step under a
**different model**, or a clean-room second attempt.

## Preconditions

- `claude` is on `PATH` (`command -v claude`). If missing, tell the user and stop.
- The sub-instance starts fresh — the prompt (argument to `-p`) must be complete on its
  own (absolute paths, exact task, desired output shape, boundaries).
- **Recursion guard:** give the sub-instance a narrow, terminal task. Never instruct it
  to delegate further. Prefer a distinct `--model` so the second run genuinely differs.
- For the write/apply step, `bwrap` (bubblewrap) must be on `PATH` — the bundled
  `scripts/sbx` wrapper uses it to sandbox the write (see "Sandboxing the apply").

## Read / analyze / search → run in plan mode

```bash
claude -p "<self-contained prompt>" --permission-mode plan --output-format text 2>&1
# options: --model <m>   --add-dir <dir>   --output-format json   -c (continue)
```

`--permission-mode plan` lets the sub-instance read and reason but not edit. Safe after
the normal Bash permission prompt.

## Write (edits / file creation / side effects) → plan → confirm → apply

`claude -p` runs to completion without pausing for approval, so insert the confirmation
**before** the write:

1. **Plan** — run in plan mode; the sub-instance proposes changes but writes nothing:
   ```bash
   claude -p "<task>. Produce a plan / diff of the intended changes; do not edit." --permission-mode plan 2>&1
   ```
2. **Confirm** — show the plan to the user and get an explicit go/no-go.
3. **Apply** — only on approval, run the write **inside the `sbx` sandbox** (see below).
   Keep the sub-instance's own Bash sandbox on too (`sandbox.enabled: true`); it survives
   `--dangerously-skip-permissions`, which only removes the approval prompts:
   ```bash
   SBX_WORK=<dir> SBX_CFG="$HOME/.claude:$HOME/.claude.json" SBX_RO="$HOME/.local:$HOME/.nvm" \
     <skill-dir>/scripts/sbx claude -p "<task>" --permission-mode acceptEdits --add-dir <dir> --dangerously-skip-permissions 2>&1
   ```

Three gates protect writes: these instructions (soft), the host's Bash permission prompt
(hard), **and** the `sbx` OS sandbox that confines the write even if the first two are
bypassed.

### Sandboxing the apply (required)

The apply runs with writes enabled and no interactive approval, so confine it with the
bundled `scripts/sbx` wrapper (bubblewrap). It makes only `SBX_WORK` writable, mounts the
system read-only, and masks `$HOME`. This matters doubly here: Claude Code's native
sandbox wraps only Bash and by default can **read the whole machine** (including
`~/.ssh` / `~/.aws`) — `sbx`'s masked HOME is what actually hides those secrets. Verified:
even with permissions skipped, the sub-instance cannot escape it.

- `<skill-dir>/scripts/sbx` — path is relative to **this skill's directory**; invoke with
  the full path. If `bwrap` is missing, `sbx` refuses (exit 127); install bubblewrap or
  keep `sandbox.enabled: true` and tell the user the HOME-masking layer is unavailable.
- `SBX_WORK` = the approved writable dir. `SBX_CFG` = `~/.claude` + `~/.claude.json`
  (auth/session, read-write). `SBX_RO` = launch dependencies (`~/.local`, node).
- Network defaults to `SBX_NET=share` so the API is reachable. This protects the
  filesystem and secrets but does **not** stop exfiltration of the workspace's contents;
  to bound egress, run an allow-list proxy and set `SBX_NET=none`.

## Prompt construction

- Absolute file paths; state the exact task and the **required output shape**.
- Set boundaries: "do not modify anything outside `<dir>`".
- For machine-readable results, add `--output-format json` and parse `.result`.

## Output handling

Append `2>&1`. Surface the sub-instance's final deliverable; don't replay its
intermediate reasoning. Report failures (non-zero exit) verbatim.

## Continue a prior delegation

```bash
claude -c -p "<follow-up prompt>" 2>&1   # continues the most recent conversation in cwd
```

## Examples

```bash
# Read: isolated analysis under a different model
claude -p "Summarize the architecture of /home/me/proj/src into a bullet list of modules and their responsibilities. Read-only." --permission-mode plan --model claude-sonnet-5 2>&1

# Write: plan then apply (apply is sandboxed)
claude -p "In /home/me/proj, rename function foo() to load_config() everywhere. Show the plan; do not edit." --permission-mode plan 2>&1
# → show plan, get approval →
SBX_WORK=/home/me/proj SBX_CFG="$HOME/.claude:$HOME/.claude.json" SBX_RO="$HOME/.local:$HOME/.nvm" \
  <skill-dir>/scripts/sbx claude -p "In /home/me/proj, rename function foo() to load_config() everywhere." --permission-mode acceptEdits --add-dir /home/me/proj --dangerously-skip-permissions 2>&1
```
