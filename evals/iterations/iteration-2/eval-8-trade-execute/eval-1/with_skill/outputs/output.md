# Slippage > tolerance → skip

## Inputs
- reference_price = 0.50 (the price the signal-gen step assumed)
- best_ask = 0.52 (current CLOB top of book)
- slippage = (0.52 - 0.50) / 0.50 = 0.04 = 4%

## Pre-trade gate (6 conditions, first-fail-wins)
1. `risk.halt == false` — passes
2. `session_valid_until > now + 1h` — passes
3. `session_remaining_spend > notional` — passes
4. `now < resolution_at - 1h` — passes
5. **`best_ask <= reference_price * 1.02`** (2% slippage cap) — 0.52 > 0.50 * 1.02 = 0.51 — **FAILS** ✓

The condition fires because 0.52 > 0.51. Slippage (4.0%) exceeds the 2.0% tolerance.

## Result
The order is **skipped** with `reason="slippage 4.0% > tolerance 2.0%"`. No order is placed on the CLOB.

`runtime/state/orders.json`:
```json
{
  "attempts": [
    {
      "ts": "...",
      "market_id": "...",
      "side": "YES",
      "status": "skipped",
      "reason": "slippage 4.0% > tolerance 2.0%",
      "order_id": null
    }
  ]
}
```

A `trade_audit` row is also appended to the SQLite history.

## Why this matters
A 4% slippage on a 0.50 quote means the fill is at 0.52, which:
- Eats ~half the expected edge (0.014 → 0.006 after slippage).
- Makes the Kelly fraction positive but tiny — not worth the risk.

The next tick will re-check; if the best_ask comes back down to ≤0.51, the order can go through.
