# Sandboxed delegation — running skip-permissions agents safely

Design note for confining delegated CLI agents (`codex`, `claude`, `agy`) when they must
run non-interactively with their permission prompts disabled. Companion to the
`agent-delegate` plugin. Verified empirically on WSL2 (kernel 6.18, `bwrap`/`docker`/
`systemd-run` present, Landlock in-kernel, unprivileged user namespaces enabled).

## Problem

The `agent-delegate` skills hand a task to another CLI agent in non-interactive mode
(`codex exec`, `claude -p`, `agy -p`). Non-interactive means the agent **cannot pause to
ask** mid-run, so any write-enabled apply step ends up passing a bypass flag
(`--dangerously-skip-permissions`, `--dangerously-bypass-approvals-and-sandbox`). That
flag removes the *approval* gate. If nothing else confines the process, a mistaken or
prompt-injected agent can then touch the whole filesystem, read `~/.ssh` and `~/.aws`,
and reach the network — with no human in the loop. We want an **OS-level boundary** that
holds even when the approval layer is off.

## Two layers of confinement (they are different things)

| Layer | What it is | Removed by the bypass flag? |
|---|---|---|
| **Approval / permission** | The agent pausing to ask before a write or network call | **Yes** — that's what the flag turns off |
| **OS sandbox** | Kernel-enforced FS/network boundary around the process | **No** (except Codex's `--yolo`, which drops both) |

The key realization: **skipping permissions need not mean removing the sandbox.** The two
layers are orthogonal for Codex and Claude Code. The design keeps the OS boundary on
regardless of the approval layer.

### Native (in-agent) sandboxes — first line, but uneven

| | Codex CLI | Claude Code | Antigravity `agy` |
|---|---|---|---|
| Linux primitive | Landlock + seccomp (helper binary) | bubblewrap + socat (+ opt. seccomp) | *reportedly nsjail — unverified* |
| Network default | **off** in `read-only`/`workspace-write` | **off** (proxy allowlist, no domains pre-allowed) | claims blocked; unverified |
| Default read scope | restricted by mode | **whole machine readable** (secrets exposed) | unclear |
| Covers | all model-run commands | **Bash subprocesses only** | shell commands |
| Default on? | always (mode-dependent) | opt-in (`sandbox.enabled`) | **off** (`enableTerminalSandbox:false`) |
| Bypass flag | `--dangerously-bypass-approvals-and-sandbox` / `--yolo` | `--dangerously-skip-permissions` (perms only) | "YOLO" mode |

Takeaways that shape the design:
- **Codex** already runs non-interactively *and* sandboxed with `codex exec --sandbox
  workspace-write` — writes stay in the workspace, network is off, `.git/` stays
  read-only. You rarely need `--yolo` at all; avoid it.
- **Claude Code**'s native sandbox only wraps **Bash**; its Read/Edit/Write tools are
  bounded by `--add-dir`, not the sandbox, and by default the process can *read the whole
  machine* (including `~/.ssh`, `~/.aws`). `--dangerously-skip-permissions` does **not**
  disable the native sandbox — keep `sandbox.enabled:true`.
- **agy**'s native sandbox is under-documented and off by default. **Do not rely on it.**

Because the native sandboxes are uneven (Claude Code reads everything; agy unproven) and
none is a hard isolation boundary, we add an **external OS sandbox** as the uniform layer.

## Decision: layered, with bubblewrap as the uniform external wrapper

Defense in depth:

1. **Use the agent's own non-interactive + sandbox mode** wherever it exists, and prefer
   it over the nuclear bypass. For Codex, `codex exec --sandbox workspace-write` needs no
   bypass flag. For Claude Code, keep `sandbox.enabled:true` even with
   `--dangerously-skip-permissions`.
2. **Wrap the whole CLI in an external `bwrap` jail** whenever a bypass/skip-permissions
   flag is in play — uniformly for all three agents, and the *only* real boundary for
   `agy`.

Why bubblewrap as the default external layer (over the alternatives surveyed):

- **Rootless, no daemon, no image, no config file** — one binary, boundary built from CLI
  flags. Works today on this WSL2 kernel (verified).
- Exact `--bind` / `--ro-bind` control maps directly onto "writable working dir,
  read-only everything else."
- Lighter than rootless Podman/Docker (which need an image + subuid setup) and than
  gVisor (needs root runtime registration and native containerd, not Docker Desktop).
- `firejail` is disqualified: it's **setuid-root** with a CVE history, and its AppArmor
  integration is a no-op on the WSL2 kernel. `systemd-run`'s strong directives need the
  system manager (root) and `systemd=true` in `wsl.conf`. `nsjail` is a fine alternative
  (adds seccomp + rlimits) but isn't installed here.

Escalation ladder (pick the lightest that meets the threat model):

| Threat | Approach |
|---|---|
| Trusted task, just want a guardrail | Native sandbox mode only (`codex exec -s workspace-write`; Claude Code `sandbox.enabled`) |
| Skip-permissions apply step | Native sandbox **+** external `bwrap` wrapper (below) |
| Untrusted/injection-prone, real secrets on box | `bwrap` with HOME masked **+ egress allowlist proxy**, or rootless Podman `--network none`, or gVisor |

## The `bwrap` wrapper (verified on this box)

A reusable launcher. Binds the working dir read-write, mounts the system read-only, masks
`$HOME` (so `~/.ssh`, `~/.aws`, tokens are **not** readable) while re-exposing only the
delegated agent's own config dir, and fixes the WSL2 DNS symlink so the API stays
reachable.

```bash
#!/usr/bin/env bash
# sbx — confine a command: writable $SBX_WORK, read-only system, masked HOME.
# Usage: SBX_WORK=/path SBX_AGENT_CFG=~/.codex sbx codex exec -s workspace-write "..."
set -euo pipefail
WORK="${SBX_WORK:-$PWD}"                 # the only writable real path
NET="${SBX_NET:-share}"                  # share | none  (share = API reachable)
HOME_DIR="${HOME:?}"
RESOLV="$(readlink -f /etc/resolv.conf)" # WSL2: /etc/resolv.conf -> /mnt/wsl/resolv.conf

args=(
  --ro-bind /usr /usr --ro-bind /etc /etc
  --ro-bind-try /bin /bin --ro-bind-try /sbin /sbin
  --ro-bind-try /lib /lib --ro-bind-try /lib64 /lib64
  --ro-bind "$RESOLV" "$RESOLV"          # <-- WSL2 DNS fix; without it name resolution fails
  --proc /proc --dev /dev --tmpfs /tmp
  --tmpfs "$HOME_DIR"                     # HOME becomes empty tmpfs: ~/.ssh, ~/.aws GONE
  --bind "$WORK" "$WORK" --chdir "$WORK"
  --setenv HOME "$HOME_DIR"
  --unshare-user --unshare-pid --unshare-ipc --die-with-parent --new-session
)
# Re-expose only the delegated agent's own config/auth (read-write for session state):
[ -n "${SBX_AGENT_CFG:-}" ] && [ -e "$SBX_AGENT_CFG" ] && args+=(--bind "$SBX_AGENT_CFG" "$SBX_AGENT_CFG")
[ "$NET" = none ] && args+=(--unshare-net)

exec bwrap "${args[@]}" -- "$@"
```

Verified behavior on WSL2 (kernel 6.18): project dir writable, `~/.ssh` secret **not**
readable, system read-only, and with `SBX_NET=share` the provider API is reachable (after
the resolv.conf bind). Anything the agent writes outside `$SBX_WORK` lands on a throwaway
tmpfs and is discarded on exit — it never touches the real filesystem.

Per-agent config dir to pass as `SBX_AGENT_CFG`: Codex `~/.codex`, Claude Code `~/.claude`
(+ `~/.claude.json`), agy `~/.gemini/antigravity-cli`. Bind these read-write only if the
agent needs to persist session state; otherwise `--ro-bind`.

## The network dilemma

The agents **must** reach their provider API, so full network isolation (`--unshare-net`)
breaks them. But none of the filesystem sandboxers filter by hostname — it's all-or-
nothing at the netns level (Landlock is port-only). So:

- **Pragmatic default (`SBX_NET=share`):** keep the host network, rely on FS confinement +
  masked HOME. The residual risk is **exfiltration** — a compromised agent can read what's
  inside `$SBX_WORK` and POST it anywhere. Acceptable when the working dir holds no
  secrets and the task is trusted.
- **Hardened:** give the sandbox a private netns (`--unshare-net`) plus a **pasta/slirp**
  interface, run an **allowlist egress proxy** on the host (only `api.anthropic.com`,
  `api.openai.com`, Google endpoints), and inject `HTTPS_PROXY` into the sandbox. This is
  the only way to bound *where* the agent can talk. Heavier; stand it up once and reuse.

Note both Codex and Claude Code warn their own network layers don't inspect TLS by
default, so a broad domain allowlist (e.g. all of `github.com`) is still an exfil channel.
Keep allowlists tight.

## WSL2-specific caveats (all confirmed here)

- **Keep the working dir on ext4** (`~/…`), never `/mnt/c`. SUID, overlayfs, userns UID
  mapping, and DynamicUser ownership all misbehave on the `drvfs`/9p mount.
- **DNS:** `/etc/resolv.conf` is a symlink into `/mnt/wsl/`; you must `--ro-bind` its real
  target or name resolution fails inside the sandbox (the wrapper does this).
- **systemd options** need `[boot] systemd=true` in `/etc/wsl.conf` + `wsl --shutdown`
  first. The user manager here is offline, so `systemd-run --user` can't apply the strong
  `Protect*`/`DynamicUser` directives — another reason to prefer `bwrap`.
- **Docker present (v29.6.1, rootless seccomp profile)** — viable for the hardened image
  route; but Docker Desktop's WSL backend overrides `daemon.json` runtimes, so gVisor
  (`runsc`) would need a native `containerd` in the distro instead.

## Honest threat-model limits

- `bwrap` and both native sandboxes are **process-level OS sandboxes, not VMs.** They
  reduce risk; they are not a hard boundary against a kernel exploit. For genuinely
  untrusted code, escalate to rootless Podman `--network none` or gVisor.
- With `SBX_NET=share`, FS confinement does **not** stop exfiltration of whatever is
  inside the writable dir. Masking HOME closes the "read my SSH key" hole but not "read
  the repo I'm editing and POST it."
- Claude Code's native sandbox covers Bash only and reads the whole machine by default —
  the external `bwrap` masked-HOME layer is what actually closes its secret-read hole.

## Integration with the `agent-delegate` skills

The existing preview→confirm→apply gate stays. The change is only at the **apply** step:
wrap the write-enabled, skip-permissions command in `sbx` (or the native sandbox mode),
so the boundary holds even though the approval layer is off.

```bash
# Codex — no bypass flag needed; native sandbox already confines the apply:
SBX_WORK=/home/me/proj SBX_AGENT_CFG=~/.codex \
  sbx codex exec -s workspace-write --skip-git-repo-check "<approved task>" 2>&1

# Claude Code — skip prompts but keep the OS boundary (native sandbox + external bwrap):
SBX_WORK=/home/me/proj SBX_AGENT_CFG=~/.claude \
  sbx claude -p "<approved task>" --permission-mode acceptEdits --add-dir /home/me/proj 2>&1

# agy — native sandbox unproven, so the external bwrap IS the boundary:
SBX_WORK=/home/me/proj SBX_AGENT_CFG=~/.gemini/antigravity-cli \
  sbx agy -p "<approved task>" --mode accept-edits --add-dir /home/me/proj --print-timeout 5m0s 2>&1
```

Prefer the least-privilege native mode over the nuclear bypass every time; reserve
`--dangerously-*` for cases where the native mode genuinely can't complete the task, and
even then keep the `sbx` wrapper on.
