# Delegation Core — shared design for the `agent-delegate` skills

This is the **canonical design source** for the three delegation skills
(`codex-delegate`, `agy-delegate`, `claude-code-delegate`). Each skill's `SKILL.md`
is intentionally **self-contained** (so it works after being symlinked into another
agent's flat `skills/` directory, where this plugin-level file is *not* distributed).
When you change the shared policy below, update all three `SKILL.md` files to match.

## What these skills are

Wrappers that let the *current* coding agent hand a task to *another* CLI coding
agent running in **non-interactive (`-p` / `exec`) mode**, capture its stdout, and use
only the final result. The point is to borrow another agent's strengths (different
model, exclusive tools, a second opinion) or to offload heavy work that would burn the
current context window.

## Non-negotiable policies (identical across all three skills)

### 1. Explicit invocation only
Do **not** auto-delegate. Delegate only when the user explicitly asks for it
("codexに投げて", "agyで調べて", "別のclaudeにやらせて", "delegate this to …").
The decision to reach for another agent is the user's, not the model's.

### 2. Read-first routing
- **Read / analyze / search tasks** → run the delegate in its read-only mode. Safe to
  run after the normal tool-permission prompt; no extra gate needed.
- **Write tasks (edits, file creation, commands with side effects)** → never let the
  delegate write on the first shot. Use the preview→confirm→apply gate (policy 3).
- **Headless read that must touch local files or the KB** → route to a delegate whose
  read-only mode actually *permits reads*: `codex -s read-only` and `claude
  --permission-mode plan` allow reads (including the KB) with writes blocked, no bypass
  flag needed. `agy -p` has **no read-only auto-approve** (its only auto-approve is the
  nuclear `--dangerously-skip-permissions`), so it is a poor fit here — prefer codex/claude,
  or make the task self-contained by embedding the material in the prompt.

### 3. Preview → confirm → apply (for every write)
Non-interactive mode means the delegate **cannot pause to ask** mid-run (it would hang
or, with a skip-permissions flag, write blindly). So the confirmation must happen at
*our* boundary, before the write-enabled call:

1. Run the delegate in a **preview mode that produces a plan/diff but writes nothing**.
2. Show the plan/diff to the user and get an explicit go/no-go.
3. Only on approval, run the write-enabled command.

Two independent gates back this up:
- **Soft:** these SKILL.md instructions tell the model to preview-and-confirm.
- **Hard:** the host agent's own Bash-tool permission prompt fires when the command
  actually runs — the user must approve the command line regardless.

A skip-permissions flag (`--dangerously-skip-permissions` /
`--dangerously-bypass-approvals-and-sandbox`) is used **only on the apply step, after a
human has already approved the previewed change** — never on an un-previewed write.

### 4. Self-contained prompts
The delegate starts with **zero context**. Every prompt must be complete on its own:
absolute file paths, the exact task, the required output shape, and explicit
boundaries ("do not touch anything outside <dir>"). Prefer imperative verbs.

### 5. Output handling
Capture stdout (append `2>&1`). Surface the delegate's final deliverable; do not replay
its intermediate reasoning. If the delegate emits structured output (JSON), request it
explicitly and parse it.

### 6. Sandbox the apply step (OS boundary)
Skipping the approval prompt is **not** the same as removing the OS sandbox — keep the OS
boundary on regardless. Every write/apply command runs inside the bundled `scripts/sbx`
wrapper (bubblewrap): only the approved working dir is writable, the system is read-only,
and `$HOME` is masked so `~/.ssh` / `~/.aws` / tokens are unreadable. This holds even when
the agent's own guards are off — verified by running real `codex` and `claude` with their
native sandboxes disabled: neither could write outside the workspace, read the planted
secret canaries, or touch the real filesystem (0 leaks under an authoritative marker grep).

- **codex / claude** also keep their *own* native sandbox on at apply (double boundary):
  codex via `-s workspace-write` (never `--dangerously-bypass-approvals-and-sandbox`,
  which disables it); claude via `sandbox.enabled: true` (survives skip-permissions).
- **agy** has no proven native sandbox, so `sbx` is the *only* boundary and is mandatory.
- `sbx` fails closed: if `bwrap` is absent it exits 127 rather than running unsandboxed.
- Network defaults to `SBX_NET=share` (the model API must be reachable). This protects the
  filesystem and secrets but does **not** stop exfiltration of the workspace's contents;
  the hardened option is an allow-list egress proxy with `SBX_NET=none`.
- `scripts/sbx` is **duplicated identically** in each of the three skills (like the
  SKILL.md files) so each stays self-contained after symlinking. Keep the copies in sync.

Full rationale, threat model, and the WSL2 caveats: `docs/sandboxed-delegation-design.md`.

### 7. Never escalate a denied read into a bypass
If a delegate's sandbox denies a benign, read-only operation (e.g. a headless agent that
can't read the KB), do **not** add a skip-permissions / bypass flag to force it through —
that trades a read for full write+network access, and the host's safety classifier will
(correctly) block such a command anyway. Instead: re-route to a delegate whose read-only
mode permits the read (policy 2), return the degraded result, or surface the limitation to
the user.

## Per-tool command matrix (verified against installed binaries)

| Concern | codex (`codex-cli` ≥0.144) | agy (Antigravity ≥1.1) | claude (Claude Code ≥2.1) |
|---|---|---|---|
| Non-interactive | `codex exec "P"` | `agy -p "P"` | `claude -p "P"` |
| Model | `-m <model>` | `--model <m>` | `--model <m>` |
| Read-only mode | `-s read-only` | (no `--add-dir`; `--sandbox`) | `--permission-mode plan` |
| Write preview | `-s read-only` → emits diff | `--mode plan` | `--permission-mode plan` |
| Write apply | `-s workspace-write --add-dir <d>` | `--mode accept-edits --add-dir <d>` | `--permission-mode acceptEdits --add-dir <d>` |
| Apply prior diff | `codex apply` | (re-run with accept-edits) | (re-run with acceptEdits) |
| Skip perms (post-approval) | `--dangerously-bypass-approvals-and-sandbox` | `--dangerously-skip-permissions` | `--dangerously-skip-permissions` |
| Sandboxed apply (`scripts/sbx`) | `SBX_CFG=~/.codex` `SBX_RO=~/.local:~/.nvm` | `SBX_CFG=~/.gemini` `SBX_RO=~/.local:~/Applications` | `SBX_CFG=~/.claude:~/.claude.json` `SBX_RO=~/.local:~/.nvm` |
| Structured output | `--json` / `-o <file>` | (plain text only) | `--output-format json` |
| Timeout | OS `timeout <dur> …` | `--print-timeout 5m0s` | OS `timeout <dur> …` |
| Continue last | `codex exec resume --last` | `-c` | `-c` |
| Working dir | `-C <dir>` (`--skip-git-repo-check` if non-git) | `--add-dir <dir>` | (cwd) |

## Recursion guard (claude→claude especially)

When delegating to the same kind of agent you are, avoid infinite nesting: give the
sub-agent a **narrow, terminal task**, never "keep delegating". Consider a distinct
model so the second opinion is actually different.
