# Metrics and reproducibility

## Reproducibility — the non-negotiable

A simulation result is evidence only if someone can reproduce it. Pin everything that
affects the outcome:

- **Seed(s).** One explicit seed per run; derive per-stream seeds from it (do not reuse
  one global RNG across independent streams — that couples them). Record the seed with
  the result.
- **Scenario set version** (params or replay source + seed) — `scenario-design.md`.
- **Policy version** (the algorithm under test) and harness/model version.
- **Environment** where numerics matter: library versions, and beware nondeterminism from
  parallelism, hashing (`PYTHONHASHSEED`), and float reduction order. If you parallelize,
  make results order-independent or fix the reduction.

Litmus test: same seed + same scenario set + same policy ⇒ identical metrics. If not,
there is uncontrolled randomness — find it before trusting any comparison.

## Choosing metrics

Report a **vector**, not one number:

- **Outcome** — the primary objective (profit, throughput, cost, fill rate).
- **Risk / tail** — variance, worst case, CVaR / percentiles. A good mean with a fat tail
  is often a bad policy.
- **Constraint violations** — how often and how badly the policy breaks limits it should
  respect (feasibility under uncertainty).
- **Operational** — latency, decision time, resource use, if relevant.

Always report **dispersion** (std, IQR, percentiles) alongside the mean — a mean over
scenarios without spread hides the risk the simulation was meant to reveal.

## Comparing variants fairly

- **Paired / common random numbers:** run each variant on the **same** scenarios and
  seeds. Paired differences cancel scenario noise and need far fewer runs to separate
  variants. This is the highest-leverage trick in simulation comparison.
- **Baseline first:** always include a naive/current baseline; report the delta.
- **Significance:** with Monte-Carlo runs, quote confidence intervals on the difference,
  not just point estimates — a 1% edge inside the noise band is not an edge.
- **Multiple comparisons:** testing many variants inflates false positives; correct for
  it or validate the winner out-of-sample.

## The final verdict

- Decide on the **out-of-sample** set the design never touched.
- Include a **sensitivity note:** does the ranking hold as seed and scenario count vary?
  A conclusion that flips with the seed is not a conclusion (same spirit as
  `tech-selector`'s fragility check).
- Report result **with** its seed, scenario-set version, and baseline — never a bare
  number.
