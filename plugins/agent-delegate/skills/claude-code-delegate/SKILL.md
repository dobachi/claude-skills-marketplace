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
3. **Apply** — only on approval:
   ```bash
   claude -p "<task>" --permission-mode acceptEdits --add-dir <dir> 2>&1
   ```
   `--dangerously-skip-permissions` may be added **only here**, after the user approved
   the plan — never on an un-planned write.

Two gates protect writes: these instructions (soft) **and** the host's Bash permission
prompt on the actual command (hard).

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

# Write: plan then apply
claude -p "In /home/me/proj, rename function foo() to load_config() everywhere. Show the plan; do not edit." --permission-mode plan 2>&1
# → show plan, get approval →
claude -p "In /home/me/proj, rename function foo() to load_config() everywhere." --permission-mode acceptEdits --add-dir /home/me/proj 2>&1
```
