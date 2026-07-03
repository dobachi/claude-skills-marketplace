# Scenario design

Scenarios are the inputs the policy runs on. Their realism and coverage decide whether a
simulation means anything.

## Two sources

| Source | What it is | Strength / risk |
|--------|-----------|-----------------|
| **Synthetic** | sampled from parameterized distributions / a generative model | full control, covers rare/extreme cases; risk = unrealistic if mis-parameterized |
| **Historical replay** | recorded traces fed through the policy | real dynamics; risk = one path, survivorship, lookahead |

Use **both**: replay to stay grounded, synthetic to stress regimes history did not
contain. Feed distributions/forecasts from `data-analyst` when parameterizing.

## Designing synthetic scenarios

- **Parameterize the drivers** (arrival rate, volatility, demand, failure rate) and vary
  them across a grid or by sampling. Document each parameter and its range.
- **Cover regimes, not just the average:** normal, stress, and adversarial/edge cases.
  The average case rarely breaks a policy; the tail does.
- **Correlations matter.** Independently sampling correlated drivers produces impossible
  worlds. Preserve the joint structure (copulas, historical covariance, block bootstrap).
- **Fix the seed** per scenario so it is reproducible and nameable.

## Historical replay done right

- **No lookahead:** at each step the policy sees only data available at that point in
  time. Enforce it structurally (feed a growing prefix), do not rely on discipline.
- **Point-in-time data:** use values as they were known then, not later-revised numbers.
- **Multiple windows / regimes:** one history is one sample. Evaluate across several
  periods (calm, volatile, shock) and report per-regime, not just pooled.
- **Bootstrap / block-resample** to turn one path into a distribution while preserving
  short-range structure.

## Coverage and scenario count

- More scenarios cut estimator variance but cost solve/sim time (and, for stochastic
  optimization, scale the model — see `optimization-modeling`). Pick the count from a
  variance target, and report it.
- **Scenario reduction:** cluster/importance-sample to keep a small representative set
  when downstream (e.g. a stochastic program) is expensive.
- Split into **train / validation / out-of-sample** sets up front; never let the
  out-of-sample set influence design.

## Making scenarios first-class

- Store a scenario as (generator params **or** replay source) + seed + version — enough
  to regenerate it exactly. Name and version scenario sets so results reference them.
- A result is only interpretable next to the scenario set and seed that produced it; keep
  them together (`metrics-and-reproducibility.md`).
