---
name: agy-delegate
description: Delegate a task from the current coding agent to Google Antigravity CLI (`agy -p`), running it non-interactively and using only its final output. Explicit-invocation only — trigger when the user says "agyに投げて", "antigravityで調べて/やって", "delegate this to agy/antigravity", "ask agy", "use agy to …", or otherwise explicitly asks to hand work to Antigravity. Read tasks run directly; any write goes through a plan→confirm→apply gate. Also the way to reach agy-only tools (Google Search grounding, image generation, science databases). Not for auto-delegation.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Delegate to Antigravity CLI (agy)

Hand a self-contained task to **Google Antigravity CLI** in non-interactive print mode
(`agy -p`), capture its stdout, and use only the final deliverable.

## When to use

**Only on explicit request.** Delegate when the user asks to hand work to agy/Antigravity
("agyに投げて", "antigravityでやって", "ask agy", "delegate to antigravity"). Do **not**
auto-delegate.

Especially useful for agy-exclusive capabilities the current agent lacks — Google
Search grounding, image generation, Chrome DevTools, 40+ scientific databases.

## Preconditions

- `agy` is on `PATH` (`command -v agy`). If missing, tell the user and stop.
- agy starts with **zero context** — the prompt (argument to `-p`) must be complete on
  its own (absolute paths, exact task, desired output shape, boundaries).
- Output is plain text (no JSON mode). Default print timeout is 5m; override with
  `--print-timeout`.

## Read / analyze / search → run directly

```bash
agy -p "<self-contained prompt>" --print-timeout 5m0s 2>&1
# options: --model <m>   --sandbox   -c (continue last conversation)
```

Do **not** pass `--add-dir` and do **not** use an edit mode for read tasks, so agy has
nothing to write into. Safe after the normal Bash permission prompt.

## Write (edits / file creation / side effects) → plan → confirm → apply

`agy -p` cannot pause to ask mid-run, so insert the confirmation **before** the write:

1. **Plan** — run in plan mode; agy produces a plan and writes nothing:
   ```bash
   agy -p "<task>" --mode plan --print-timeout 5m0s 2>&1
   ```
2. **Confirm** — show the plan to the user and get an explicit go/no-go.
3. **Apply** — only on approval:
   ```bash
   agy -p "<task>" --mode accept-edits --add-dir <dir> --print-timeout 5m0s 2>&1
   ```
   `--dangerously-skip-permissions` may be added **only here**, after the user approved
   the plan — never on an un-planned write.

Two gates protect writes: these instructions (soft) **and** the host's Bash permission
prompt on the actual command (hard).

## Prompt construction

- Absolute file paths; state the exact task and the **required output shape**.
- Set boundaries: "do not modify anything outside `<dir>`".
- For agy-only tools, name them: "use Google Search to …", "generate an image of …".

## Output handling

Append `2>&1`. Surface agy's final deliverable; don't replay intermediate reasoning.
Report failures (non-zero exit, timeout) verbatim.

## Continue a prior delegation

```bash
agy -c -p "<follow-up prompt>" --print-timeout 5m0s 2>&1
```

## Examples

```bash
# Read: web-grounded research (agy-only capability)
agy -p "Use Google Search to find the 3 most-cited papers on retrieval-augmented generation since 2024. Output title, authors, year, and a one-line summary each." --print-timeout 5m0s 2>&1

# Write: plan then apply
agy -p "In /home/me/proj, split utils.py into utils/ package by concern." --mode plan --print-timeout 5m0s 2>&1
# → show plan, get approval →
agy -p "In /home/me/proj, split utils.py into utils/ package by concern." --mode accept-edits --add-dir /home/me/proj --print-timeout 5m0s 2>&1
```
