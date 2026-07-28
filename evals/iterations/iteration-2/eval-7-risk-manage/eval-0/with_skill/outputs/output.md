# Risk decision: 8.5% daily drawdown

## Inputs
- bankroll_usdc = 50
- exposure_pct = 18
- daily_pnl_pct = -8.5
- no soft anomalies

## Halt matrix (8 conditions, first match wins)
1. **DAILY_DRAWDOWN**: halt if `daily_pnl_pct <= -RUNTIME_MAX_DAILY_DRAWDOWN_PCT` (default -10). At -8.5%, **not triggered**.
2. **SESSION_KEY_EXPIRED** / **REVOKED**: not triggered.
3. **CONSECUTIVE_TX_FAILURES** (>=3 in a row): not triggered.
4. **ALL_SOURCES_FAILED** for >1h: not triggered.
5. **BANKROLL_RECONCILIATION** drift >1%: not triggered.
6. **CLOB_UNREACHABLE** for >30min: not triggered.
7. **INVARIANT_VIOLATION**: not triggered.
8. **USER_PAUSED**: not triggered.

## Result
`halt = false`, `halt_reason = None`. The risk-manage skill writes `runtime/state/risk.json` atomically:

```json
{
  "bankroll_usdc": 50,
  "exposure_pct": 18.0,
  "daily_pnl_usdc": -4.25,
  "daily_pnl_pct": -8.5,
  "halt": false,
  "halt_reason": null,
  "consecutive_tx_failures": 0
}
```

## Next step
`trade-execute` reads `risk.json`, sees `halt=false`, and may place orders from `signals.json` (subject to the 6-condition pre-trade gate).
