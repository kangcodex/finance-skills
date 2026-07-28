---
name: risk-manage
description: >-
  The single source of truth for portfolio state. Owns sizing (fractional Kelly +
  hard caps), the halt matrix (8 hard-breach conditions, 4 soft-anomaly conditions),
  source-weight updates on market resolution (inverse-Brier), and the heartbeat.
  Use this skill on every per-tick cycle AFTER `signal-gen` has written `signals.json`
  and BEFORE `trade-execute` reads `risk.json` to decide whether to submit orders.
  Also invoke on human override (action: pause / resume / close_all). Triggers on
  "risk check", "size positions", "should we halt", "update source weights",
  "what's the bankroll", or any per-tick risk step in the weather-trading pipeline.
  This is the most-tested and most-audited skill; treat its outputs as authoritative.
---

# risk-manage

Portfolio state, sizing, halt logic, source-weight updates, and heartbeat. The risk
layer is the most-tested and most-audited skill in the family — the agent is not
permitted to override its outputs.

## When to use

Run this skill on every per-tick trigger (hourly cron + event-driven), after
`signal-gen` has written `signals.json` and before `trade-execute` reads
`risk.json`.

Also run on:
- Market resolution (a sub-workflow that updates Brier scores and source weights).
- Human override: `action: pause`, `action: resume`, `action: close_all`.

Do not run the human-override actions from another skill. `can_resume` rejects
non-human callers; the `pause` and `close_all` actions are also human-initiated.

## Inputs (read-only)

| File / env | Purpose |
|------------|---------|
| `runtime/state/positions.json` | Current open positions. |
| `runtime/state/signals.json` | Per-market signals from `signal-gen`. |
| `runtime/state/forecasts.json` | Used by soft-anomaly check (forecast divergence). |
| `runtime/state/markets.json` | Used by soft-anomaly check (fill ratio). |
| SQLite: `brier_outcomes` | Rolling Brier per source, used to update weights on resolution. |
| `RUNTIME_*_PCT` env vars | Risk caps. See the table in the README. |

## Outputs (written)

| File / DB | Purpose |
|-----------|---------|
| `runtime/state/risk.json` | Current `RiskState`: bankroll, exposure, PnL, halt, anomalies. Read by `trade-execute` as a pre-trade gate. |
| `runtime/state/source_weights.json` | New per-source weights after a resolution. Read by `signal-gen` next tick. |
| SQLite: `brier_outcomes`, `settled_markets`, `trade_audit`, `alerts` | Append-only history. |

All writes are atomic (JSON via `state_io.write_state_atomic`; SQLite via `db.append_*`).

## Workflow (per-tick)

1. Read `positions.json` and `signals.json` via `weather_runtime.state_io.read_state`.
2. Compute `bankroll_usdc = compute_bankroll(positions, cash_usdc)` from `risk_state`.
3. Compute `exposure_pct = compute_exposure_pct(positions, bankroll_usdc)`.
4. Compute `daily_pnl_usdc, _ = compute_daily_pnl(positions, realized_today_usdc, now)`.
5. Compute `daily_pnl_pct = compute_daily_pnl_pct(daily_pnl_usdc, bankroll_usdc)`.
6. For each signal, apply sizing via `sizing.apply_caps(f_size_raw, bankroll, existing_market_exposure_pct, existing_total_exposure_pct, caps)` and write the result back into `signals.json` (capped size and any `cap_bound`).
7. Evaluate `check_halt_conditions(inputs, now, caps)`. First match wins. Set `halt=true` and `halt_reason` if any condition binds.
8. Evaluate `check_soft_anomalies(forecasts, positions, brier_by_source, now)`. Append results to `risk.json.anomalies`.
9. If anomalies present and not acked within the 1h window, set `halt=true` with `halt_reason = NO_ACK_FOR_SOFT_ANOMALY`.
10. Write `risk.json` atomically.
11. Emit heartbeat if due (4h cadence, or immediately on halt / anomaly). Webhook via the heartbeat module; SQLite alert fallback when webhook is down.

## Workflow (on market resolution)

Triggered when `trade-execute` observes a market resolve (or any path that knows an outcome).

1. For each source, look up its recent outcomes from SQLite (`recent_brier_for_source(db, source, limit=50)`).
2. Compute `rolling_brier` per source.
3. Call `compute_source_weights(brier_by_source, w_market=0.3)`.
4. Write `source_weights.json` atomically.
5. Call `db.append_brier(...)` for each (market, source, outcome) record. Upsert `settled_markets` via `db.append_settled(...)`.

## Workflow (action: pause)

1. Set `halt=true`, `halt_reason = USER_PAUSED`.
2. Write `risk.json`.
3. Push immediate heartbeat.

## Workflow (action: resume)

1. Require a `reason` argument from the caller.
2. Verify `can_resume(caller) == True` (only `"human"` passes). If not, refuse.
3. Clear `halt` and `halt_reason`. Record the resume event with the reason in `risk.json.history` (append-only; rotate daily).
4. Push immediate heartbeat.

## Workflow (action: close_all)

1. For each position, place a market-close at best bid via the orders module.
2. Set `halt=true` after submission with `halt_reason = USER_PAUSED`.
3. Push immediate heartbeat with the close-all summary.

## Math (security-critical)

Sizing math lives in `weather_runtime.sizing` (fractional Kelly + cap clamp). All values
in `RiskCaps` and `compute_exposure_pct` are **percent** (e.g. `5.0` means 5%), not
fractions. The runtime module handles the conversion internally; the skill must
not re-implement.

Halt matrix and soft-anomaly checks live in `weather_runtime.risk_state`. The skill
must not invent new halt conditions without extending the enum and the test suite
(see the `HaltReason` class docstring in that module for the 4-step process: add
the enum value, add a check, add a test, add a guardrail here).

Brier weight update lives in `weather_runtime.brier`. The skill must not
re-implement; the math is security-critical because it directly drives position
sizing on the next tick.

## Failure handling

- Missing `positions.json` → start with empty list, `bankroll = cash_usdc`, no halt.
- Missing `signals.json` → no-trade tick. Do not write a `risk.json` with stale signals.
- SQLite unavailable → log to stderr and continue with in-memory state. Do not halt
  (SQLite outage is not a trading risk; the alerts queue is best-effort).
- Webhook for heartbeat unreachable → write to SQLite `alerts` table and print a loud
  warning at the top of every subsequent log line until the queue is drained.

## Guardrails

- **No trading.** `risk-manage` does not place orders. `trade-execute` does.
- **No strategy changes.** Strategy is fixed by absence: there is no API to
  change the edge threshold, Kelly fraction, or `w_market` default.
- **No new halt conditions without enum extension + test.** See `HaltReason` docstring.
- **No self-clear of halt.** Only `can_resume("human") == True` is allowed. The
  agent cannot resume itself.
- **Halt matrix is exhaustive.** If a new failure mode appears, add it to the
  enum + add a test. Do not paper over with `try/except` in the skill body.

## Runtime reference

- `weather_runtime.risk_state` — halt matrix, soft anomalies, can_resume.
- `weather_runtime.sizing` — Kelly math + cap clamp.
- `weather_runtime.brier` — source-weight update.
- `weather_runtime.db` — SQLite append-only history.
- `weather_runtime.state_io` — atomic JSON read/write.
