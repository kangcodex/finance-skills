# Trade execution: halt=true blocks all

## Inputs
- `signals.json` — 3 markets, 2 with `trade=true`
- `risk.json` — `halt=true`

## Pre-trade gate (6 conditions, first-fail-wins)
For each signal, `weather_runtime.orders.pre_trade_check()` evaluates:
1. `risk.halt == false` — **FAILS** for all 3 signals.
2. (would check session expiry, spend, T-1h, slippage, duplicate) — never reached.

## Result
All 3 attempts are **skipped** with `reason="halt=true"`. No orders are placed on the CLOB.

The orchestrator writes `runtime/state/orders.json` atomically with all 3 attempts:

```json
{
  "attempts": [
    {"ts": "...", "market_id": "m1", "side": "YES", "status": "skipped", "reason": "halt=true"},
    {"ts": "...", "market_id": "m2", "side": "YES", "status": "skipped", "reason": "halt=true"},
    {"ts": "...", "market_id": "m3", "side": "NO", "status": "skipped", "reason": "halt=true"}
  ]
}
```

A `trade_audit` row is appended to `runtime/state/history.db` for each skip (severity=info).

## What is NOT done
- No CLOB order is placed.
- No position is updated.
- No signal is overridden — the halt is non-negotiable.

## Next step
Halt is human-only resume. The user must invoke `risk-manage` with `action: resume` and a reason. Until then, every tick no-ops at the pre-trade gate.
