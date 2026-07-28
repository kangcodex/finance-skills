# Computing per-market signals

## Inputs
- `runtime/state/forecasts.json` — per-source p_yes
- `runtime/state/markets.json` — per-market p_market, best_ask, resolution_at
- `runtime/state/source_weights.json` — per-source weights + w_market

## Math
For each market:
1. `p_blend = w_market * p_market + sum(w_i * p_i)`, clamped to [0, 1]
2. `edge = p_blend - p_market`
3. `f_size_raw = 0.25 * kelly(p_blend, (1 - best_ask) / best_ask)` (fractional Kelly)

`trade = (edge > 0.05) AND (f_size_raw > 0) AND (now < resolution_at - 1h)`

`reason` is one of: `"edge>0.05, f_size>0"`, `"edge below threshold (X < 0.05)"`, `"within last hour, no new positions"`, `"all sources returned identical p (no signal)"`.

## Workflow
1. Read all three inputs via `weather_runtime.state_io.read_state`. If any is missing, abort the tick.
2. Reload `source_weights.json` only if `weights_have_changed_enough(old, new, tol=0.01)`.
3. For each market, call `weather_runtime.signal_gen.compute_signal(market, forecasts_for_market, source_weights, now=now)`.
4. Write `signals.json` atomically.

## Output (signals.json)
```json
{
  "signals": [
    {
      "market_id": "...",
      "p_blend": 0.54,
      "edge": 0.14,
      "f_size_raw": 0.0583,
      "trade": true,
      "reason": "edge>0.05, f_size>0"
    }
  ]
}
```

## Worked example
p_market=0.40, source=0.60, w_market=0.3 → p_blend = 0.3*0.4 + 0.7*0.6 = 0.54 → edge=0.14 → trade=true.
