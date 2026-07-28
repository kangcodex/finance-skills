---
name: signal-gen
description: >-
  Compute the agent's blended probability `p_blend` and per-market edge from forecast
  sources and the market-implied probability. Pure math; no I/O. Use this skill on
  every per-tick cycle AFTER `weather-data-fetch` has written `forecasts.json` and
  `markets.json`, and BEFORE `risk-manage` decides whether to size and place orders.
  Triggers on "compute signals", "blend the forecasts", "what's the edge on market
  X", or any per-tick invocation in the weather-trading pipeline. Do NOT use for
  one-shot manual analysis outside the cron — there is no point blending one market's
  forecasts in isolation; the value is in doing it systematically across all tracked
  markets every tick.
---

# signal-gen

Per-tick signal computation for the Polymarket weather-trading agent. Pure math; no
network calls, no wallet, no order placement. The skill reads inputs from disk,
calls into the `weather_runtime.signal_gen` module, and writes the result.

## When to use

Run this skill on every per-tick trigger (hourly cron + event-driven), immediately
after `weather-data-fetch` has written the latest `forecasts.json` and
`markets.json`, and immediately before `risk-manage` reads the resulting signals.

Do not run standalone for one-off analysis. The blending is the system; a single
market in isolation has no useful edge estimate.

## Inputs (read-only)

| File | Purpose |
|------|---------|
| `runtime/state/forecasts.json` | `p_yes` per source per market. Written by `weather-data-fetch`. |
| `runtime/state/markets.json` | `p_market`, `best_ask`, `resolution_at` per market. Written by `weather-data-fetch`. |
| `runtime/state/source_weights.json` | Per-source weights + `w_market`. Written by `risk-manage` on resolution. |

## Output (written)

| File | Purpose |
|------|---------|
| `runtime/state/signals.json` | One entry per market: `p_blend`, `edge`, `f_size_raw`, `trade`, `reason`. |

Write is atomic (tmp + fsync + os.replace) via `weather_runtime.state_io.write_state_atomic`.

## Workflow

1. Read the three input files via `weather_runtime.state_io.read_state`. If any are
   missing or malformed, abort the tick with a clear log line — do not emit a partial
   signal file. `risk-manage` is the consumer and a missing `signals.json` is a
   no-trade tick, which is safer than a corrupt one.
2. Reload `source_weights.json` only if `weights_have_changed_enough(old, new)` is
   true (tolerance 0.01). Otherwise reuse the in-process copy. This keeps the loop
   cheap without missing real weight updates.
3. For each market in `markets.json`:
   - Build `forecasts_for_market = {"p_market": m["p_market"], **per_source_p_yes}`.
   - Call `compute_signal(market, forecasts_for_market, source_weights, now=now)`.
   - Append to the output list.
4. Write `signals.json` atomically.
5. Log a one-line summary: `signals=N, trade=M, no_trade=N-M` where `M` is the
   count of `trade=True`.

## Math (security-critical)

`p_blend = w_market * p_market + sum_i(w_i * p_i)`, clamped to [0, 1].

`edge = p_blend - p_market`.

`f_size_raw = 0.25 * kelly(p_blend, (1 - best_ask) / best_ask)` from
`weather_runtime.sizing.fractional_kelly`.

`trade = (edge > 0.05) AND (f_size_raw > 0) AND (now < resolution_at - 1h)`.

The math lives in `weather_runtime.signal_gen` and is unit-tested. The skill must
not re-implement the math — it calls the module.

## Failure handling

- Missing/malformed input file → abort tick, log, do not write output.
- One market has malformed `resolution_at` → skip that market, log, continue with the rest.
- All `weights_have_changed_enough` evaluations return false → no-op weight reload (intended).

## Guardrails

- **No I/O beyond the three input files and one output file.** No network, no signing.
- **No sizing decisions beyond `f_size_raw`.** Cap application and bankroll-based notional
  calculation are `risk-manage`'s job.
- **No order placement.** That is `trade-execute`.
- **Strategy is fixed.** The skill must not propose changes to the edge
  threshold, Kelly fraction, or `w_market` default. Only `risk-manage` updates source
  weights, and only on resolution.

## Runtime reference

- `weather_runtime.signal_gen` — the math (compute_signal, blend_probability, compute_edge).
- `weather_runtime.sizing` — fractional Kelly.
- `weather_runtime.state_io` — atomic read/write.
