# ADR-007: Signal blends N forecast sources with market-implied prob as Bayesian prior

## Status
Accepted

## Date
2026-07-28

## Context
The edge in weather trading on Polymarket comes from **forecasting better than the market**. The naive approach is to pick one forecast source (e.g. NOAA) and trade against it. The moonsat approach (per the Medium writeup) is to **learn** which sources are reliable by tracking accuracy over time.

The design question: how does the agent form its belief about the true probability of an event?

## Decision
- **Belief = Bayesian blend of N forecast sources, with the market-implied probability as the prior.**
- N ≥ 3 sources for v1: **NOAA NWS** (free, public, US-only), **Open-Meteo** (free, global, ensemble), **one paid source** (Tomorrow.io or Visual Crossing) as the tie-breaker.
- For each market:
  1. Pull the deterministic forecast from each source.
  2. Convert to a probability of the market's resolution (e.g. "Will max temp in NYC on 2026-08-01 exceed 32°C?" → use forecast distribution from each source).
  3. Pull the market's `lastTradePrice` from Polymarket CLOB. Treat as `p_market`.
  4. Update:
     `p_blend = w_market * p_market + sum(w_i * p_i)` where `w_market = 0.3` and `w_i ∝ recent Brier accuracy of source i` (re-normalized).
  5. **Edge = p_blend − p_market** (in price units).
- **Minimum edge to trade = 5% (price units)** below this, no trade (fees + slippage eat the edge).
- **Brier tracking per source** is maintained by `risk-manage` and updated on each market resolution. `signal-gen` reads the latest weights.

## Consequences
Positive:
- The agent is **not** betting on a single forecast model. If NOAA is wrong, the blend is not.
- The market price acts as a strong prior — prevents the agent from trading on garbage forecasts when the market is well-calibrated.
- Brier-weighted adaptation is the "self-learning" piece, scoped to data weights, not strategy.

Negative:
- Requires ground truth to update Brier. That's only available on resolution. So the first 20-50 markets have flat weights. Acceptable.
- The paid source is a recurring cost. Mitigated by starting on free sources and adding the paid one only when free-source accuracy plateaus.
- Bayesian math is one more thing to get right; tests must cover the math separately from the wiring.

## Alternatives considered
- **Single source (NOAA).** Rejected. Single point of failure; no "self-learning."
- **Equal-weight average.** Rejected. Treats a 90%-accurate source the same as a 60%-accurate one.
- **ML model on top of forecasts.** Rejected for v1. Needs labeled data, hyperparameter care, and would obscure the reasoning. Can be added as another source later.
- **Pure market price (no forecast).** Rejected. Then there's no edge.

## See also
- ADR-008: position sizing (edge feeds into size)
- `docs/design/weather-trading-system.md` (signal pipeline)
