# Plugin contract / SDK design

The contract is the platform's real API surface. Every plugin builds to it; changing it
breaks all of them. Design it deliberately and version it from day one.

## What the contract defines

1. **The interface** — the entry points a plugin must implement (e.g. `run(input) →
   output`, plus optional `init`, `describe`, `health`). Keep it small; a wide contract
   is a wide compatibility burden.
2. **The boundary schema** — the exact shape of data in and out, defined in a
   language-neutral schema (JSON Schema / Protobuf / a typed IDL). Data crosses the trust
   boundary **by value**, serialized — never as shared host objects.
3. **The capability model** — what a plugin may *request* (read a dataset, call a named
   host service, use N MB memory). Capabilities are granted explicitly by the host, not
   assumed. This is how you deny ambient authority at the contract level.
4. **Metadata** — name, version, host-API compatibility range, author, declared
   capabilities. The registry reads this (`registry-and-versioning.md`).

## Keep the interface narrow and pure

- Prefer a **pure function** shape: input in, result out, no side effects the host did
  not sanction. Purity makes isolation, testing, and determinism far easier.
- Push variability into **data**, not into new methods. A `describe()` returning
  declared parameters beats ten specialized entry points.
- Version the **schema** alongside the interface — a field added to the boundary type is
  a contract change.

## Versioning and compatibility

- **Semantic versioning of the host API.** Plugins declare a compatible range (e.g.
  `hostApi >=1.2 <2.0`). The registry refuses to serve a plugin to an incompatible host.
- **Backward compatibility rules:** additive changes (new optional field, new optional
  capability) are minor; removing/renaming a field or tightening a type is **major** and
  requires a new host-API major version.
- **Deprecation, not silent breakage:** mark a contract element deprecated, keep it for
  a stated window, then remove at the next major. Communicate via the registry.
- **Capability negotiation:** at load, the host and plugin agree on which optional
  capabilities are available; a plugin needing an ungranted capability fails to load
  (fail closed), it does not run degraded in an undefined way.

## Language reach

- A **language-neutral boundary schema** lets plugins be written in multiple languages.
  If you commit to WASM, the contract is a WASM component interface (e.g. WIT); if to
  subprocess, it is a stdin/stdout or RPC protocol; if in-process (trusted only), it is a
  native interface. Pick the boundary technology together with the isolation mechanism —
  they are the same decision (`sandboxing-strategies.md`).

## Testing the contract

- Ship a **conformance test suite** plugins can self-test against — it defines "valid
  plugin" operationally and catches contract drift.
- Provide a **reference plugin** (trivial but complete) as the template and the
  integration test fixture.
- Validate every plugin against the schema **at load time**, before execution — a
  contract violation is a load failure, not a runtime surprise.
