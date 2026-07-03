# Sandboxing strategies

Running someone else's code safely is the hard core of a plugin platform. The goal:
the plugin computes on the inputs you give it and returns a result, and can do
**nothing else** — no host filesystem, network, environment, processes, or unbounded
resource use — unless you explicitly granted it.

## Isolation mechanisms, strongest trade-offs

| Mechanism | Isolation | Perf / startup | Language reach | Use when |
|-----------|-----------|----------------|----------------|----------|
| In-process, language sandbox (e.g. restricted interpreter) | **weak** — shared memory/GC; escapes are common | fastest | host language only | first-party trusted code only |
| Subprocess + OS limits (rlimits, seccomp-bpf, namespaces, no-net) | medium–strong | low overhead | any native lang | semi-trusted; you control the OS |
| **WASM** (Wasmtime/Wasmer, WASI) | strong — memory-safe, capability-based, no syscalls by default | fast startup, near-native | languages compiling to WASM | semi/untrusted; deterministic sandbox |
| Container (with seccomp/AppArmor, no-net, ro-fs) | strong (kernel-shared) | moderate | any | untrusted; existing container infra |
| microVM / gVisor (Firecracker, gVisor) | **strongest** — separate/kernel-intercepted | heaviest per-call | any | untrusted marketplace, hostile code |

**Rule of thumb:** never run untrusted marketplace code in-process. Default to **WASM**
(great isolation-to-performance ratio, deterministic) or **microVM/gVisor** (maximum
isolation) depending on language reach and per-call cost tolerance.

## Deny ambient authority (capability-based)

The plugin starts with **nothing** and receives only what you pass:

- **Filesystem:** none by default. If needed, mount a read-only, plugin-scoped dir or
  pass data by value. WASI grants dirs explicitly (preopens); containers use read-only
  mounts.
- **Network:** off by default (`--net=none`, no WASI socket cap). Grant a specific
  egress only if a capability was requested and approved.
- **Environment/secrets:** never inherit host env. Pass an explicit, minimal input.
- **Processes/syscalls:** seccomp allowlist (subprocess/container); WASM exposes no
  syscalls except granted WASI functions.

## Bound every resource

| Resource | How |
|----------|-----|
| CPU time | cgroups CPU quota; WASM fuel/epoch interruption; subprocess CPU rlimit |
| Wall-clock | host-side hard timeout that kills/cancels the sandbox |
| Memory | cgroups memory limit; WASM max memory; `RLIMIT_AS` |
| Output size | cap serialized result bytes; truncate/reject over limit |
| Concurrency | pool + per-tenant quota so one plugin cannot starve others |

A timeout must be enforced **by the host**, not trusted to the plugin — WASM
epoch/fuel and cgroups make this reliable; a cooperative timeout inside the plugin does
not count.

## Threats to model at the boundary

- **Resource exhaustion / DoS** — infinite loop, memory bomb, huge output. Covered by
  the limits above; verify they actually fire (test with a hostile fixture).
- **Data exfiltration** — plugin tries to reach network/filesystem. Covered by
  ambient-authority denial; audit granted capabilities.
- **Supply chain** — a malicious *update* to a previously-good plugin. Covered by
  signing/provenance and pinning versions (`registry-and-versioning.md`).
- **Side channels / info leak** — shared caches, timing. Relevant for microVM-grade
  multi-tenant isolation; usually accept-and-document unless the data is sensitive.
- **Host-call abuse** — if you expose host functions to the sandbox, each is new attack
  surface: validate arguments, rate-limit, and keep them capability-gated.

## Verify the sandbox

Escape-test it deliberately: a fixture plugin that tries to read `/etc/passwd`, open a
socket, spawn a process, allocate 100 GB, and loop forever — each must be denied or
killed within limits. An untested sandbox is an assumed sandbox. Pair with
`security-review` before admitting third-party code.
