---
name: web-frontend-dev
description: Build production web front-ends (SPA and beyond) — component architecture, state management, API data-fetching with caching, forms and data tables, auth/session UI, and accessibility. Turns frontend-design direction into a real, maintainable implementation. Use for building web UIs, SPAs, dashboards, admin panels, フロントエンド実装 that consume an API.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Web Frontend Implementation Expert

You build the actual web front-end: a maintainable, accessible UI that talks to an API.
`frontend-design` sets the aesthetic direction; this skill turns it into a real
application — component structure, state, data-fetching, forms, tables, and auth. It
consumes the API contracts that `web-api-dev` / `archimate-to-impl` produce (OpenAPI).

## Core principles

1. **Separate server state from client state.** Data from the API (server state) and UI
   state (what's open, selected, typed) are different problems with different tools.
   Conflating them is the root of most frontend mess. `references/state-and-data-fetching.md`.
2. **The server is the source of truth; the client caches it.** Fetch, cache, invalidate
   — don't hand-roll a second copy of the backend in global state.
3. **Component boundaries follow the UI, data flow follows ownership.** Lift state to the
   lowest common owner; pass down; avoid prop-drilling with context only where it earns
   its keep. `references/spa-architecture.md`.
4. **Accessibility is not optional.** Semantic HTML, keyboard operability, focus
   management, labels, and contrast are requirements, not polish.
5. **Handle the four states, always.** Every data view has loading / empty / error /
   success — design and build all four, not just the happy path.
6. **Type the boundary.** Generate types/clients from the OpenAPI contract so the UI and
   API cannot silently drift.

## Choosing the rendering approach

| Need | Approach | Notes |
|------|----------|-------|
| app-like, behind auth, highly interactive (dashboard, admin, trading UI) | **SPA** (React/Vue/Svelte) | client renders; API for data |
| SEO / fast first paint / content-heavy | **SSR / SSG** (Next, Nuxt, SvelteKit, Astro) | server-rendered, hydrate |
| mostly content, islands of interactivity | **MPA + islands** (Astro) | least JS shipped |
| existing server-rendered app needing sprinkles | progressive enhancement (htmx / Alpine) | avoid a full SPA |

Default a data-dense, authenticated product UI to an **SPA**; reach for SSR/SSG when
first paint or SEO drives the requirement. Don't ship a framework you don't need.

## The build loop

1. **CONTRACT** — take the API's OpenAPI; generate types/a client so the data shape is
   known and checked.
2. **ARCHITECTURE** — routes, component tree, and where each piece of state lives
   (`spa-architecture.md`).
3. **DATA** — wire server-state fetching with caching/invalidation (React Query / SWR /
   RTK Query / Vue Query); keep client state separate (`state-and-data-fetching.md`).
4. **UI** — build views with all four states; forms with validation; tables with
   sort/filter/paginate.
5. **AUTH** — session/token handling, protected routes, and token refresh at the edge.
6. **A11Y + POLISH** — keyboard, focus, labels, contrast; apply `frontend-design`'s
   direction; verify with `webapp-testing`.

## Forms and tables (where real apps live)

- **Forms:** schema-driven validation (shared with the backend schema when possible),
  inline errors, disabled/pending on submit, optimistic or pending feedback, and never
  lose user input on error.
- **Tables:** server-side sort/filter/paginate for large sets (don't ship 10k rows to
  the client); virtualize long lists; keep sortable columns and empty/error states.

## Deliverables

- A component/route architecture with an explicit state-ownership map.
- A typed API client generated from the contract, with caching/invalidation wired.
- Views implementing loading/empty/error/success, accessible and keyboard-operable.
- Auth/session flow (protected routes, refresh) and form/table behavior defined.

## Boundaries

- **Not** aesthetic direction — that is `frontend-design` (this skill implements it).
- **Not** the API — that is `web-api-dev`; this consumes its contract.
- **Not** claude.ai HTML artifacts — that is the web-artifacts-builder example skill.
- Verify behavior with `webapp-testing` (Playwright) rather than asserting it works.
