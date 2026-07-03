---
name: simulation-harness
description: Build simulation and backtesting harnesses to evaluate algorithms and system behavior — generate scenarios, run discrete-event or time-stepped models, replay history, collect metrics, and compare variants (A/B) reproducibly under fixed seeds. Use for simulation, backtesting, what-if evaluation, シミュレーション / バックテスト of algorithms and services.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Simulation & Backtest Harness Builder

You build the rig that answers "how would this algorithm/service behave?" before it
meets production — by running it against generated scenarios or replayed history,
collecting metrics, and comparing variants. This is how a decision from
`optimization-modeling` or a service design gets **evaluated**, not just asserted.

## Core principles

1. **Reproducible or it is not evidence.** Every run is pinned to a seed and a scenario
   set; the same seed reproduces the same result bit-for-bit. A result you cannot
   reproduce cannot be trusted or compared. `references/metrics-and-reproducibility.md`.
2. **Separate the model, the scenario, and the policy.** The simulated world (model),
   the inputs it runs on (scenarios), and the algorithm under test (policy) are three
   independent pieces — swap any one without touching the others.
3. **Evaluate out-of-sample.** Tune on one scenario set, judge on a fresh one. In-sample
   performance that collapses out-of-sample is overfitting — the failure this harness
   exists to catch.
4. **Compare against a baseline.** A number in isolation means little; report the policy
   against a naive/current baseline on the *same* scenarios and seeds.
5. **Model the mechanism honestly.** Include the frictions that matter (latency, fees,
   partial fills, delays); a simulator that omits them flatters the policy.

## Pick the execution model

| World behaves like | Model | Notes |
|--------------------|-------|-------|
| events at irregular times (arrivals, messages, rounds) | **discrete-event** (SimPy-style) | event queue advances the clock to the next event |
| state advances on a fixed tick | **time-stepped** | simplest; choose Δt small enough to be faithful |
| replay recorded history through the policy | **backtest / trace replay** | data fidelity is everything; no lookahead |
| many interacting decision-makers | **agent-based** | emergent behavior; watch reproducibility |
| estimate a distribution of outcomes | **Monte Carlo** over any of the above | vary seed/scenario, aggregate |

## The harness loop

1. **DEFINE WORLD + POLICY** — the model and the algorithm under test, behind clean
   interfaces so either can be swapped.
2. **GENERATE SCENARIOS** — synthetic (parameterized distributions) and/or historical
   replay; fix seeds. `references/scenario-design.md`.
3. **RUN** — execute the policy over scenarios; a Monte-Carlo sweep for distributions.
4. **MEASURE** — collect metrics (outcome, risk/tail, constraint violations, latency);
   aggregate with dispersion, not just means. `references/metrics-and-reproducibility.md`.
5. **COMPARE** — policy vs baseline vs variants on identical scenarios/seeds; use paired
   comparison (same scenarios) to cut variance.
6. **VALIDATE** — hold out an out-of-sample set for the final verdict; check sensitivity
   to seed and scenario count.

## Backtesting traps (avoid these)

- **Lookahead / future leakage** — the policy sees data it would not have had at decision
  time. The single most common way a backtest lies.
- **Survivorship bias** — replaying only entities that still exist.
- **Overfitting to one history** — one path is one sample; use multiple regimes /
  bootstrap, and report variance.
- **Ignoring frictions** — no fees, instant fills, zero latency inflate results.

## Deliverables

- A harness with model / scenario / policy separated behind interfaces.
- A scenario set (synthetic params and/or replay source) with fixed seeds.
- A metrics report: outcome + risk/tail + violations, with dispersion, policy vs
  baseline on identical scenarios.
- An out-of-sample verdict and a seed/scenario-count sensitivity note.

## Boundaries

- **Not** the algorithm being tested — that is `optimization-modeling` / the dev skills
  (this harness consumes it as the policy, and supplies it scenarios for stochastic
  models).
- **Not** production data analysis / ML training — that is `data-analyst`.
- **Not** load/perf testing of a running service — that is a separate concern.
