# Optimization under uncertainty

When inputs are forecasts, a single "optimal" answer to the wrong numbers is fragile.
Choose an uncertainty strategy deliberately — the cheapest that the decision's risk
justifies.

## Decision ladder (cheapest first)

1. **Deterministic + sensitivity.** Solve with expected values, then vary the
   uncertain parameters and watch the solution/objective. Fine when the solution is
   stable and the downside of being wrong is small. This is the baseline — always do
   at least this.
2. **Stochastic programming.** Model uncertainty as scenarios with probabilities and
   optimize expected (or risk-adjusted) objective. Use when recourse matters — you
   decide now, observe, then adjust.
3. **Robust optimization.** Optimize against the worst case within an uncertainty set.
   Use when you need a guarantee and have no distribution, or the cost of violation is
   severe.

## Stochastic programming

- **Two-stage with recourse:** first-stage "here-and-now" decisions (fixed before
  uncertainty resolves) + second-stage "wait-and-see" recourse per scenario. Objective
  = first-stage cost + expected recourse cost.
- **Scenarios** come from `simulation-harness` (scenario generation, seeds) or from
  forecast distributions produced by `data-analyst`. Reduce scenario count with
  scenario reduction / sampling — solve time scales with the number of scenarios.
- **Risk measures:** expected value is risk-neutral. For tail risk, optimize **CVaR**
  (conditional value-at-risk) — it stays linear and is the standard convex tail
  measure. Add a chance constraint when a requirement is "satisfy X with ≥95%
  probability" (note: chance constraints can be nonconvex; use scenario/CVaR
  approximations).

## Robust optimization

- Define an **uncertainty set** (box, ellipsoidal, budget/Γ-robust). The set's shape
  trades conservatism against tractability: box is simplest but most conservative;
  budgeted (Bertsimas–Sim) lets you dial how many parameters may deviate at once.
- The **robust counterpart** of an LP with a well-chosen set is still LP/conic — i.e.
  tractable. Ellipsoidal sets give SOCP counterparts.
- Use robust when you cannot trust a distribution; use stochastic when you can and
  recourse is valuable. **Distributionally robust** optimization sits between the two.

## Validating an under-uncertainty solution

- **Out-of-sample test:** fix the here-and-now decision, then evaluate it on fresh
  scenarios (`simulation-harness`) the model never saw. In-sample optimality that
  collapses out-of-sample means overfitting to the scenario set.
- **Value of information:** compare stochastic solution vs deterministic (VSS, value of
  the stochastic solution) and vs perfect information (EVPI) to justify the added
  modeling cost — sometimes deterministic + sensitivity is genuinely enough.
- Report the risk measure used and the scenario set size/source, not just the objective.
