---
name: trade-execute
description: >-
  Pre-trade gate + idempotent order placement for Polymarket CLOB. Consumes
  `signals.json` (where `trade = true`) and `risk.json`; refuses when halted,
  session key is within 1h of expiry, session remaining spend ≤ notional,
  within T-1h of resolution, slippage > 2%, or duplicate position. Re-running
  on the same signals is idempotent. Use this skill on every per-tick cycle
  AFTER `risk-manage` writes `risk.json` and BEFORE the next tick reads
  `positions.json`. Triggers on "execute the trades", "place the orders",
  "submit signals", or any per-tick order step in the weather-trading pipeline.
  Never runs without a green `risk.json`; this is the last gate before real
  money moves.
---

# trade-execute

For each `signal` where `trade = true`, place a limit order on the Polymarket
CLOB after passing a six-condition pre-trade gate. The gate is enforced by
`weather_runtime.orders.pre_trade_check`. The order is sized already — this
skill never re-runs Kelly.

## When to use

Run this skill on every per-tick trigger (hourly cron + event-driven), after
`risk-manage` has written `risk.json` and the green/halt state is known.

Do NOT run if `risk.json` says `halt = true`. The pre-trade check enforces
this; the skill is a no-op in that case.

## Inputs (read-only)

| File | Purpose |
|------|---------|
| `runtime/state/signals.json` | Per-market signals from `signal-gen`. Only `trade = true` are acted on. |
| `runtime/state/risk.json` | Risk envelope. `halt`, `bankroll_usdc`, `session_valid_until`, `session_remaining_spend`. |
| `runtime/state/positions.json` | Open positions. Used to enforce the no-duplicate-position check. |

## Output (written)

| File | Purpose | Permissions |
|------|---------|-------------|
| `runtime/state/orders.json` | Per-attempt log: `{ts, market_id, side, status, reason, order_id}`. Appended atomically. | `chmod 600` |
| `runtime/state/history.db` (SQLite) | One row per attempt in `trade_audit`. | normal |

## Workflow

1. **Read state.** `signals.json`, `risk.json`, `positions.json`. If any
   file is missing or malformed, abort with a clear reason — do not trade
   blind.
2. **For each signal** with `trade = true`:
   1. **Pre-trade check** via
      `orders.pre_trade_check(signal, risk, book, positions, now)`. Six
      conditions, first-fail-wins:
      - `risk.halt == false`
      - `session_valid_until > now + 1h`
      - `session_remaining_spend > signal.notional`
      - `now < resolution_at - 1h`
      - `best_ask <= reference_price * 1.02` (2% slippage cap)
      - No existing position on the same market+side
   2. **If blocked**: log a `skipped` entry to `orders.json` and append
      a `trade_audit` row with `status='skipped'`. Continue to the next
      signal.
   3. **If passed**: place via `orders.place_one(signal, book, client)`.
      Price is `max(best_ask, reference_price * 1.01)`. Qty is
      `notional / price`.
   4. **On fill**: the orchestrator updates `positions.json` (out of
      scope for this skill — left to the scheduler). The order id is
      recorded in both `orders.json` and `trade_audit`.
3. **Write `orders.json` atomically** via the same `tmp+fsync+os.replace`
   pattern used elsewhere in the runtime.
4. **Idempotency**: re-running on the same `signals.json` is a no-op for
   any market already in `orders.json` with `status = placed`.

## Failure handling

- **Order rejected by CLOB**: log `status='error'`, do not retry this tick.
  The next debounce window (per the per-tick trigger cadence) will pick the
  signal up again if it still says `trade = true`.
- **HTTP 5xx**: retry 3× with exponential backoff. The CLOB client is
  responsible for this; the orchestrator just sees a final result.
- **Session key error**: do NOT swallow. Append a `trade_audit` row with
  `status='session_error'`, set `risk.halt = true`, and exit. The next
  tick's `risk-manage` will see the halt.
- **Partial fill**: log fill ratio. If < 30% over 5 attempts, the
  `risk-manage` soft-anomaly check (`low_fill_ratio`) fires.

## Guardrails

- **Never** override `risk.halt`. The pre-trade check is the last line of
  defence; a no-op on halt is non-negotiable.
- **Never** re-size a signal. The notional comes from `signal-gen`; this
  skill is the executor, not the strategist.
- **Never** place an order when the session key is within 1h of expiry.
  This is the safest fail-mode for the session-key custody model.
- **Strategy is fixed**: the slippage cap (2%), the price formula
  (`max(ask, ref*1.01)`), the qty formula (`notional/price`), and the
  pre-trade conditions are all config-free. Do not introduce knobs.

## Runtime reference

- `weather_runtime.orders` — module that implements everything above.
- `weather_runtime.state_io` — atomic JSON read/write.
- `weather_runtime.db` — SQLite `trade_audit` append.
