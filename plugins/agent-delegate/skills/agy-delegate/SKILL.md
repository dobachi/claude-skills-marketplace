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
- For the write/apply step, `bwrap` (bubblewrap) must be on `PATH` — the bundled
  `scripts/sbx` wrapper uses it to sandbox the write (see "Sandboxing the apply"). agy's
  own sandbox is off by default and under-documented, so **`sbx` is the real boundary**.

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
3. **Apply** — only on approval, run the write **inside the `sbx` sandbox** (see below):
   ```bash
   SBX_WORK=<dir> SBX_CFG="$HOME/.gemini" SBX_RO="$HOME/.local:$HOME/Applications" \
     <skill-dir>/scripts/sbx agy -p "<task>" --mode accept-edits --add-dir <dir> --print-timeout 5m0s 2>&1
   ```
   `--dangerously-skip-permissions` may be added **only here**, after the user approved
   the plan — never on an un-planned write. Because agy has no reliable native sandbox,
   the `sbx` boundary is not optional for a write.

Three gates protect writes: these instructions (soft), the host's Bash permission prompt
(hard), **and** the `sbx` OS sandbox that confines the write even if the first two are
bypassed.

### Sandboxing the apply (required)

agy has no proven native sandbox, so the bundled `scripts/sbx` wrapper (bubblewrap) is the
boundary. It makes only `SBX_WORK` writable, mounts the system read-only, and masks `$HOME`
so `~/.ssh` / `~/.aws` / tokens are unreadable.

- `<skill-dir>/scripts/sbx` — path is relative to **this skill's directory**; invoke with
  the full path. If `bwrap` is missing, `sbx` refuses (exit 127); install bubblewrap
  before letting agy write, or stop and tell the user.
- `SBX_WORK` = the approved writable dir. `SBX_CFG="$HOME/.gemini"` = agy's config/auth
  (read-write). `SBX_RO="$HOME/.local:$HOME/Applications"` re-exposes the agy binary — it
  resolves `~/.local/bin/agy` → `/etc/alternatives/agy` → `~/Applications/antigravity-cli/`,
  so both `~/.local` and `~/Applications` must be readable inside the jail.
- Network defaults to `SBX_NET=share` so the API is reachable. This protects the
  filesystem and secrets but does **not** stop exfiltration of the workspace's contents;
  to bound egress, run an allow-list proxy and set `SBX_NET=none`.

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

# Write: plan then apply (apply is sandboxed)
agy -p "In /home/me/proj, split utils.py into utils/ package by concern." --mode plan --print-timeout 5m0s 2>&1
# → show plan, get approval →
SBX_WORK=/home/me/proj SBX_CFG="$HOME/.gemini" SBX_RO="$HOME/.local:$HOME/Applications" \
  <skill-dir>/scripts/sbx agy -p "In /home/me/proj, split utils.py into utils/ package by concern." --mode accept-edits --add-dir /home/me/proj --print-timeout 5m0s 2>&1
```
