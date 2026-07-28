# 3 consecutive tx failures → halt

## Inputs
- consecutive_tx_failures = 3
- (everything else within bounds)

## Halt matrix
1. DAILY_DRAWDOWN: -3% (not at -10% threshold)
2. SESSION_KEY_EXPIRED: not expired
3. **CONSECUTIVE_TX_FAILURES**: `consecutive_tx_failures >= 3` — **TRIGGERED** ✓
4-8. Not relevant; first-match-wins.

## Result
`halt = true`, `halt_reason = HaltReason.CONSECUTIVE_TX_FAILURES`.

`runtime/state/risk.json`:
```json
{
  "bankroll_usdc": 50,
  "exposure_pct": 12.0,
  "daily_pnl_usdc": -1.5,
  "daily_pnl_pct": -3.0,
  "halt": true,
  "halt_reason": "CONSECUTIVE_TX_FAILURES",
  "consecutive_tx_failures": 3
}
```

The risk-manage skill also pushes an immediate heartbeat (if `RUNTIME_HEARTBEAT_URL` is set) and appends a row to the SQLite `alerts` table with severity=hard.

## What trade-execute sees on the next tick
`risk.json.halt == true` → pre-trade check fails on condition #1 → all signals skipped with `reason="halt=true"`.

## Recovery
The user must:
1. Investigate the 3 failed tx (most likely: insufficient gas, RPC drift, or session key revoked).
2. Invoke `risk-manage` with `action: resume` and a reason (e.g. "session key rotated, gas topped up").
3. `can_resume(caller="human") == True` → halt cleared.

The agent cannot self-resume; `can_resume(caller="agent") == False`.
