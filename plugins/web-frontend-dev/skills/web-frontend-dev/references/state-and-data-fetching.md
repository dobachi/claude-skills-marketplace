# State and data fetching

The highest-leverage idea in modern frontend: **server state and client state are
different problems.** Most frontend complexity comes from managing API data as if it
were local UI state.

## Two kinds of state

| | **Server state** | **Client state** |
|---|---|---|
| Origin | the API (you own a cached copy) | the UI (you own it) |
| Examples | user list, orders, prices | modal open, selected tab, form draft, theme |
| Concerns | fetching, caching, staleness, invalidation, refetch | just set/read |
| Tool | a **data-fetching library** (React Query, SWR, RTK Query, Vue Query) | local state / a small store |

Do **not** put server data in a global client store and hand-manage loading flags and
invalidation — that reimplements a cache badly. Use a query library for server state; use
local/context/store only for client state.

## Server state with a query library

- **Cache by key** (the endpoint + params). Multiple components asking for the same key
  share one request and one cache entry.
- **Stale-while-revalidate:** show cached data instantly, refetch in the background,
  update when it lands — fast and fresh.
- **Invalidate on mutation:** after a write, invalidate the affected query keys so views
  refetch the truth. Prefer invalidation over manually editing the cache.
- **Loading/error are built in:** the library gives you the four states (loading / empty /
  error / success) per query — render all four.
- **Optimistic updates** for snappy mutations: apply the expected result immediately, roll
  back on error. Use where latency hurts UX; keep the rollback correct.

## Client state

- Keep it local until more than one distant component needs it; then lift or put it in a
  small store (Zustand/Pinia/Redux-Toolkit) — scoped, not a dumping ground.
- Put shareable/navigational state in the **URL** (filters, ids, pagination), not a store.
- Form state is client state until submit; see below.

## The API boundary

- **Generate types and/or a client from OpenAPI** (openapi-typescript, orval, openapi-
  generator). The UI then fails to compile when the contract changes — drift caught early.
  This is the join with `web-api-dev` / `archimate-to-impl`.
- Centralize the fetch layer: base URL, auth header injection, error normalization, and
  ret/refresh in one place, not scattered across components.
- Handle auth at the edge: attach the token, refresh on 401, and redirect on refresh
  failure — uniformly.

## Forms

- Use a form library (React Hook Form / Formik / VeeValidate) + a schema validator (Zod /
  Yup) — ideally the **same schema shape** the backend validates, so rules don't diverge.
- Validate on blur/submit, show inline errors, disable submit while pending, and **never
  discard user input** on a failed request.

## Rule of thumb

If you are writing `useState` for `isLoading` next to an API call, reach for a query
library instead. If you are copying API data into a global store, stop — cache it, don't
mirror it.
