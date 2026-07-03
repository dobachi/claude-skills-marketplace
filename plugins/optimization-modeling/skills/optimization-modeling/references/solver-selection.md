# Solver and modeling-layer selection

Two decisions: the **modeling layer** (how you express the model in code) and the
**solver** (what actually optimizes). Choose the layer for ergonomics and the solver
for the problem class.

## Modeling layers (Python)

| Layer | Best for | Notes |
|-------|----------|-------|
| **PuLP** | quick LP/MILP | simple, CBC bundled; limited to linear |
| **Pyomo** | large/structured LP/MILP/NLP | solver-agnostic, supports NLP via IPOPT; good for real models |
| **OR-Tools** | CP-SAT, routing, scheduling | best-in-class CP-SAT; also an LP/MILP wrapper |
| **CVXPY** | convex (LP/QP/SOCP/SDP) | you write convex math; it verifies convexity and picks a conic solver |
| **JuMP** (Julia) | performance-critical / research | if the stack allows Julia |
| **linprog / milp (SciPy)** | tiny embedded LP/MILP | dependency-light; HiGHS under the hood |

**Guidance:** CVXPY when the problem is convex and you want convexity *checked*; Pyomo
for large or nonlinear models needing solver choice; OR-Tools CP-SAT for combinatorial,
scheduling, and feasibility-heavy problems; PuLP/SciPy for small linear cases.

## Solvers by class

| Class | Open source | Commercial |
|-------|-------------|------------|
| LP | **HiGHS**, CBC, GLPK | Gurobi, CPLEX, Mosek |
| MILP | **HiGHS**, CBC, **OR-Tools CP-SAT** | Gurobi, CPLEX |
| QP / convex | OSQP, ECOS, **Clarabel**, SCS | Mosek, Gurobi |
| SOCP / SDP | ECOS, SCS, Clarabel | Mosek |
| NLP (local) | **IPOPT** | Knitro |
| Global nonconvex | Couenne, SCIP*, BARON‑like | BARON, Gurobi (nonconvex QP) |
| CP / scheduling | **OR-Tools CP-SAT** | CP Optimizer |

\* SCIP is free for academic/non-commercial; check licensing for production.

**Defaults that rarely disappoint:** HiGHS for LP/MILP, CP-SAT for combinatorial,
Clarabel/ECOS via CVXPY for convex, IPOPT for smooth nonlinear.

## When to reach for a commercial solver

- MILP that HiGHS/CBC cannot close within the time budget (large, weak relaxation).
- Need for features: indicator constraints, lazy constraints/callbacks, nonconvex QP,
  proven performance on your instances. Benchmark on *your* data before committing —
  the gap is problem-dependent.

## Driving the solve

- **Set limits:** wall-clock time limit and MIP relative gap (e.g. 1%). Report which
  one stopped the solve.
- **Read the status:** optimal / feasible (gap > 0) / infeasible / unbounded /
  time-limit. Never present a feasible-but-not-optimal result as optimal.
- **Warm-start** MILPs from a known good solution when re-solving similar instances.
- **Presolve** on by default; turn off only to debug a suspected presolve issue.
- **Reproducibility:** fix the seed and thread count if you need bit-stable results
  (parallel MIP is otherwise nondeterministic).

## Scale tactics (when it is too big/slow)

- Tighten formulations (smaller big-M, stronger cuts) before buying a bigger solver.
- **Decomposition:** Benders (complicating constraints), Dantzig-Wolfe / column
  generation (many variables), Lagrangian relaxation (coupling constraints).
- Aggregate/rolling-horizon for time-indexed models.
- For stochastic models, control the scenario count (see
  `references/stochastic-and-robust.md`) — solve time scales with scenarios.
