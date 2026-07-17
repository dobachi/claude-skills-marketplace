# Adapter: source code

Applies the essence test to code — modules, classes, functions, branches, parameters,
abstractions, config. Use with the five-question test in `SKILL.md`.

**Division of labor:** this skill decides, at the design/scope level, *which* capability or
abstraction is inessential and safe to remove. The actual edit — and bug-hunting — belongs
to **/simplify** and **/code-review**. Deliver the scope decision; hand them the change.

## What "purpose" and "load-bearing" mean here

- **Purpose** = the behavior the code must exhibit for its callers — its external contract.
- **Load-bearing** = code some tested/observable behavior depends on. This is Brooks's
  essential complexity: the part inherent to the problem. **Accidental complexity** — the
  contingent by-product of how it was built — is what's removable *without changing the
  contract*.

## The invariant: behavior is held fixed

Distilling code is **behavior-preserving except for capabilities the user agrees to drop.**
There are two distinct moves; keep them separate:

1. **Accidental-complexity removal** — same behavior, less code (dead code, redundant
   layers, over-abstraction collapsed). Safe once verified. → `/simplify`.
2. **Scope reduction** — a *capability* judged inessential to the purpose is removed, which
   *does* change behavior. Requires explicit user confirmation; name what stops working.

Never blur (2) into (1). Silently dropping a capability under the banner of "simplifying" is
exactly the failure mode this skill's propose-first invariant exists to prevent.

## Code-specific cruft (smells → category)

| Category | Smell |
|---|---|
| Dead / redundant | Unreachable code, unused functions/params/vars, commented-out blocks, duplicate helpers. |
| Speculative generality | Abstractions/interfaces/hooks/flags with a single caller; `TODO: future`, parameters never varied; a strategy pattern for one strategy. |
| Accidental complexity | Needless indirection, a layer that only forwards, config for values that never change, a framework for a 10-line job. |
| Gold-plating | Handling inputs that can't occur; options no user asked for; premature caching/pooling with no measured need. |
| Premature optimization | Hand-rolled complexity for performance that isn't a stated requirement or measured bottleneck. |
| Decoration | Noise comments restating the code; ceremonial boilerplate. |

## Chesterton's Fence is sharpest here

A branch, flag, or `try/except` that "looks pointless" is the classic fence: it may guard a
race, a legacy client, a platform quirk, or a bug someone already paid for. **Before
proposing removal, establish why it exists** — git blame, tests, callers, issue links. If
its reason can't be established → **flag, don't cut.**

## Keep, even when it looks removable

- Error handling and input validation on a real trust boundary.
- A test that pins a subtle contract (even if it looks redundant with another).
- An abstraction with two or more genuinely different callers — that's essential, not
  speculative. (One caller = speculative; two similar = maybe; two different = keep.)
- Code required by a domain mandate (security, compliance, accessibility).

## Verify before recommending a cut

Prefer evidence over eyeballing: coverage/reachability, "find usages", a compile/test run,
git history. A cut recommended without checking callers is a guess. Note in the ledger how
each cut was verified (e.g. "no callers in repo; grep + LSP references empty").

## Handoffs

- Apply the same-behavior cleanup → **/simplify**.
- Hunt for correctness bugs the cut might touch → **/code-review**.
- The "cut" is really a rename/reorg with no removal → normal refactoring, not this skill.
