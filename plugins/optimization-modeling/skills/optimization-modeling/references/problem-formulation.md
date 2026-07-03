# Problem formulation patterns and pitfalls

Translating a decision into a correct, tractable model is where most of the value —
and most of the errors — live. Keep the formulation reviewable **independent of code**.

## The three questions

1. **Decision variables** — what does the solver get to choose? Give each a symbol, a
   domain (continuous ≥0, integer, binary), and units. If you cannot name the
   variables, you cannot model the problem yet.
2. **Objective** — one scalar to maximize/minimize. Multiple goals → weight them (and
   check the weights the way `tech-selector` does), or optimize one and constrain the
   rest (ε-constraint).
3. **Constraints** — every rule that limits the choice. Each should reference data or
   another variable, not a hidden assumption.

## Keep it linear/convex when you can

Linearity and convexity are the difference between "solved in milliseconds" and
"maybe solved". Reach for integers only when the decision is genuinely discrete.

| You need | Linear/convex-friendly formulation |
|----------|-----------------------------------|
| "at most one of" / logical choice | binary vars + linking constraints |
| fixed cost when active | binary `y` + `x ≤ M·y` (big-M) or an indicator constraint |
| `|x|` in objective (minimizing) | `t ≥ x`, `t ≥ −x`, minimize `t` |
| max/min of terms | epigraph var `t` with `t ≥`/`t ≤` each term |
| product of two binaries `x=ab` | `x ≤ a`, `x ≤ b`, `x ≥ a+b−1` |
| product var·binary | McCormick envelopes / big-M linearization |
| piecewise-linear cost | SOS2 or segment binaries |

## Big-M and indicator constraints

- **Big-M** couples a binary to a continuous bound (`x ≤ M·y`). Pick M as **tight as
  correct** — an inflated M wrecks the LP relaxation and the solve time. If you cannot
  bound M, prefer a solver **indicator constraint** (Gurobi/CPLEX/CP-SAT) instead.
- Document why each M is valid; a wrong M silently cuts off feasible solutions.

## Common pitfalls

- **Unbounded objective** — a maximization with a missing upper limit. Bound every
  variable that should be bounded; an "unbounded" status is a modeling bug, not a win.
- **Infeasible by over-constraining** — when infeasible, relax to find the culprit:
  add slack variables with a penalty, or use the solver's IIS (irreducible infeasible
  subsystem) to locate the conflicting constraints.
- **Equality where inequality is meant** — `=` removes slack the solver needs; use `≤`
  / `≥` unless the balance is truly exact.
- **Scaling** — coefficients spanning many orders of magnitude cause numerical
  trouble. Rescale units so coefficients sit within a few orders of magnitude.
- **Modeling data into the structure** — keep parameters in data, not baked into the
  constraint code, so the same model runs on new numbers (and on scenarios).

## Sanity checks before trusting a result

- Re-solve a tiny hand-computable instance and match the known answer.
- Check the solution against each constraint in code (feasibility within tolerance).
- Flip a binding constraint's RHS slightly and confirm the objective moves the
  expected direction and amount (matches the dual).
