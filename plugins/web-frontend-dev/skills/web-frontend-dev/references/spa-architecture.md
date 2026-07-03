# SPA architecture

Structure a front-end so it stays maintainable as it grows. The recurring failure is
tangled state and god-components; the antidote is clear ownership and boundaries.

## Component structure

- **Compose small, single-purpose components.** A component that both fetches data,
  holds form state, and renders a table is three components.
- **Presentational vs container** (loosely): components that render from props vs
  components that own data/state. You don't need a strict split, but keep data-owning
  logic out of deeply reusable leaf components.
- **Co-locate** a component with its styles, tests, and local hooks; group by feature,
  not by file type, once the app is non-trivial.

## State ownership — the central decision

Put each piece of state at the **lowest common owner** of the components that need it:

| Scope | Where it lives |
|-------|----------------|
| one component | local state |
| a subtree | lift to the nearest common parent; pass down |
| cross-cutting UI (theme, current user, locale) | context / a small store |
| server data | a data-fetching cache, **not** global UI state (`state-and-data-fetching.md`) |

Avoid a giant global store holding everything — it couples the whole app and makes
change risky. Reach for global state only for genuinely cross-cutting **client** state.

## Routing

- Define routes as data; lazy-load route bundles (code-splitting) so initial load stays
  small.
- Keep shareable state in the **URL** (filters, selected id, pagination) — it makes views
  linkable, back-button-correct, and reload-safe. The URL is underused app state.
- Guard protected routes at the router; redirect unauthenticated users and preserve the
  intended destination.

## Data flow

- **Down via props, up via callbacks/events.** Predictable and debuggable.
- Use context for a *few* cross-cutting values; do not use it as a general event bus or
  to dodge thinking about ownership (context re-renders its whole subtree).
- Derive, don't duplicate: compute values from source state rather than storing copies
  that can drift.

## Performance (only where it matters)

- **Code-split** by route; lazy-load heavy components (charts, editors).
- **Virtualize** long lists/tables instead of rendering thousands of nodes.
- Memoize expensive renders/derivations deliberately — measure first; premature memo is
  its own complexity.
- Keep bundles honest: watch what each dependency costs; a data-dense dashboard does not
  need a 3D engine.

## Project conventions

- One way to fetch, one way to handle forms, one way to show errors — consistency beats
  cleverness across a team.
- Type everything at the API boundary and at component props; let the compiler catch
  drift before users do.
