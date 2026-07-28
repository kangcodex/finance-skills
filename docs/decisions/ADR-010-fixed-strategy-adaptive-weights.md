# ADR-010: Strategy is fixed; only data-source weights adapt (Brier-tracked)

## Status
Accepted

## Date
2026-07-28

## Context
"AI trading bot" usually means "the model rewrites its own strategy." That is dangerous. A reinforcement-learning agent that edits its own reward function, position-sizing formula, or signal blend is one prompt-injection away from "trade the entire bankroll on a 99.99% signal that turns out to be a stale-data error."

The moonsat writeup describes a bot that "learns" — but on inspection, the learning is scoped to **which data sources are accurate**, not the strategy itself.

## Decision
**The strategy is fixed. Only data-source weights adapt.**

| Layer | Mutable by the agent? | How it changes |
|-------|-----------------------|----------------|
| Which markets to consider (universe filter) | No | Hardcoded in `signal-gen` SKILL.md. |
| How to form `p_blend` (Bayesian formula) | No | Hardcoded. |
| Edge threshold (5%) | No | Hardcoded. |
| Kelly fraction (0.25) | No | Hardcoded. |
| Hard caps (5% / 10% / 25% / 10%) | No | Hardcoded. |
| `w_market` (market prior weight, 0.3) | No | Hardcoded. |
| Per-source weights `w_i` | **Yes** | Updated by `risk-manage` after each market resolution, based on rolling Brier score. |

`risk-manage` writes the new weights to `runtime/state/source_weights.json`. `signal-gen` reads them on the next tick.

**The agent cannot:**
- Add new forecast sources without a code change to `weather-data-fetch`.
- Change the Kelly fraction.
- Change the edge threshold.
- Disable any risk cap.

If the user wants to change any of these, they edit the skill, not the agent. The agent is not allowed to "discover" that a 1.0 Kelly fraction would have made more on the last 20 trades.

## Consequences
Positive:
- The blast radius of a prompt injection is bounded: even if the agent is fully compromised, it cannot increase the Kelly fraction or disable the daily drawdown cap.
- The "learning" stays at the right altitude: at the data layer, where the moonsat approach demonstrably works.
- Backtests are reproducible: a given sequence of market outcomes produces a deterministic sequence of weights.

Negative:
- Misses some adaptation opportunities (e.g. "we should trade less in summer because volatility is lower"). The user can add these as new hardcoded rules later.
- The fixed strategy may be wrong in regimes the user hasn't thought of. The right response is to revise the skill, not to let the agent improvise.

## Alternatives considered
- **Full RL, agent rewrites everything.** Rejected. Unbounded blast radius; no reproducibility; can drift into ruin.
- **No learning at all.** Rejected. The whole edge is "we blend sources better than the market." Without per-source weighting, all sources are equal, which is wrong.
- **Agent tunes thresholds within hard bounds.** Rejected. Even bounded self-tuning creates a slow drift toward "0.24... 0.25... 0.26..." that the user can't audit.

## See also
- ADR-007: signal blend
- ADR-008: sizing
- `docs/design/risk-framework.md` (what is and isn't mutable)
