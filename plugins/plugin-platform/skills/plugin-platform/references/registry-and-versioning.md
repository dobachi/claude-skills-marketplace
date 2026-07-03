# Registry, versioning, and provenance

The registry is the catalog that makes a plugin **discoverable, versioned, and
trustable**. For a marketplace of third-party units it is also where trust and
supply-chain safety are enforced.

## Registry metadata (per plugin version)

```yaml
name: bid-optimizer
version: 1.4.2                 # semver of the plugin itself
host_api: ">=1.2 <2.0"        # compatible host contract range
entry: bid_optimizer.wasm      # artifact + isolation kind (wasm/container/...)
capabilities: [read:market-data]   # requested capabilities (host grants/denies)
publisher: acme                # identity
signature: <sig>               # provenance (see below)
digest: sha256:...             # content hash for pinning/integrity
deprecated: false
```

The **host_api range** is what the registry uses to refuse serving an incompatible
plugin (`plugin-contract.md`). The **digest** is what lets consumers pin an exact
artifact and detect tampering.

## Versioning policy

- **Semver the plugin** and **semver the host API** independently. A plugin update
  within the same host-API major is a drop-in; a host-API major may require plugins to
  re-publish.
- **Immutable published versions.** Never mutate `1.4.2` in place — publish `1.4.3`.
  Immutability is what makes pinning and reproducibility real.
- **Resolution:** consumers pin an exact version (or a digest) for reproducibility, or a
  compatible range for auto-update. Default production posture: **pin**, update
  deliberately.

## Discovery

- Searchable metadata (name, tags, capability, publisher, compatibility).
- Surface **compatibility with the caller's host version** in results — a plugin the
  caller cannot run should be marked, not hidden silently.
- Show provenance/trust signals (signed? publisher reputation?) alongside function.

## Provenance and supply-chain safety

- **Sign artifacts;** verify the signature at install/load. An unsigned or
  signature-mismatched artifact fails closed.
- **Pin by digest** so a malicious or accidental re-publish cannot silently change what
  runs (defends the "malicious update" threat from `sandboxing-strategies.md`).
- **Review/scan on submission** for a marketplace: automated checks + `security-review`
  before a third-party plugin is admitted; re-review on capability escalation.
- **Publisher identity** and a revocation path (yank a compromised version; the registry
  stops serving it, consumers pinned to it get warned).

## Deprecation and lifecycle in the registry

- Mark deprecated with a reason and a sunset date; keep serving through the window so
  consumers can migrate.
- **Yank** (security) vs **deprecate** (soft): a yanked version is refused for new
  installs immediately; a deprecated one still resolves but warns.
- Track which host-API versions a plugin version supports so a host upgrade can report
  exactly which plugins will stop working.

## Minimal viable registry

Start with: an immutable content-addressed store (artifact + digest), a metadata index
with host-API compatibility and capabilities, signature verification at load, and a
yank path. Add search, reputation, and automated scanning as the marketplace grows.
