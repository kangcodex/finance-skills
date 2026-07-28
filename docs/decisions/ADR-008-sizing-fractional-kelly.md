# ADR-008: Sizing = fractional Kelly + hard caps; no full Kelly, no fixed %

## Status
Accepted

## Date
2026-07-28

## Context
Once a signal has edge, the next decision is **how much** to bet. The risk skill is the one that owns sizing — sizing is a risk decision, not a signal decision. (Signal says "there's edge"; risk says "given the portfolio, how much do we risk on this?")

Common sizing methods:
- **Fixed % of bankroll per trade.** Simple, but ignores edge size.
- **Full Kelly.** Maximizes log-growth given true probability. Maximizes ruin given miscalibrated probability.
- **Fractional Kelly** (e.g. 0.25 Kelly). Industry standard for automated systems.
- **Risk parity / vol-targeted.** Suited to continuous-return assets. Prediction markets have bounded, discrete outcomes; less natural fit.

## Decision
**Fractional Kelly (0.25) with hard caps.** The `risk-manage` skill computes, for each signal:

```
f_raw = (p * b - q) / b           # full Kelly
                                       # where p = p_blend, b = payoff odds, q = 1 - p
f_size = 0.25 * f_raw              # fractional
```

Then clamps:
- `f_size ≤ MAX_PER_TRADE_PCT` of bankroll (default **5%**)
- `f_size ≤ MAX_PER_MARKET_PCT` of bankroll (default **10%**)
- New position does not push `total_exposure > MAX_TOTAL_EXPOSURE_PCT` (default **25%**)
- New position does not push `daily_loss_today > MAX_DAILY_DRAWDOWN_PCT` (default **10%** → halts for the day)
- If `f_raw ≤ 0`, **no trade** (signal-gen already screens for `edge > 5%`, this is a second check)

If any cap binds, the position is sized to the binding cap and the trade proceeds (the cap is not a veto; it is a clamp). The fact that a cap bound is **logged** for review.

## Consequences
Positive:
- Edge is rewarded (bigger edge → bigger size), but bounded — no "all in on a sure thing."
- A miscalibrated `p_blend` cannot blow the account: caps are absolute, not relative.
- Daily drawdown cap turns a bad day into a paused day, not a wiped account.
- The 0.25 fraction is the industry default for automated trading; survives a regime where the agent's edge estimate is half-true.

Negative:
- Under-bets during the agent's best runs (0.25 Kelly is conservative).
- Requires the agent to track **bankroll** (cash + sum of open positions marked to last trade price). If the bankroll feed is wrong, sizing is wrong.

## Alternatives considered
- **Fixed 2% per trade.** Rejected. Ignores edge. Pays the same for a 6% edge and a 30% edge.
- **Full Kelly.** Rejected. Too sensitive to `p_blend` calibration errors; a 5% miscalibration at full Kelly is ruin.
- **Vol-targeted / risk parity.** Rejected. Designed for continuous-return assets. Prediction-market payoffs are bounded [0, 1] per contract.

## See also
- ADR-007: signal blend (where `p_blend` comes from)
- ADR-009: kill switch (daily drawdown is one of the auto-halt conditions)
- `docs/design/risk-framework.md` (full risk envelope)
