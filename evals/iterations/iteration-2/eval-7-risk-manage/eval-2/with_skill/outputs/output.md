# User pause action

## Workflow
1. User invokes `risk-manage` with `action: pause`.
2. The skill:
   - Sets `halt = true` in the in-memory `RiskState`.
   - Sets `halt_reason = HaltReason.USER_PAUSED`.
   - Writes `runtime/state/risk.json` atomically.
   - Pushes an immediate heartbeat (if `RUNTIME_HEARTBEAT_URL` is set; otherwise writes a row to the SQLite `alerts` table with severity=hard).
   - Logs the pause event in the in-memory history.

## risk.json after pause
```json
{
  "bankroll_usdc": 50,
  "exposure_pct": 12.0,
  "daily_pnl_usdc": -1.5,
  "daily_pnl_pct": -3.0,
  "halt": true,
  "halt_reason": "USER_PAUSED",
  "consecutive_tx_failures": 0
}
```

## Effect on trade-execute (next tick)
The pre-trade gate's first condition is `risk.halt == false` — this fails immediately for every signal. All attempts are skipped with `reason="halt=true"`. `orders.json` records each skip.

## What the user sees
- The agent enters read-only mode: signals are still computed, risk state is still updated, but no orders are placed.
- The heartbeat webhook (if set) is pushed immediately with the pause notification.
- Existing positions are NOT closed — that's a separate `action: close_all` call.

## Resuming
The user must invoke `risk-manage` with `action: resume` and a reason. `can_resume("human")` returns True; the agent cannot self-resume.
