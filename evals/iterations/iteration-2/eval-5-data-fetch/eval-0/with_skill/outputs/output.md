# Fetching forecasts + market state (per-tick)

## Workflow
1. Read `runtime/state/markets.json` (previous tick's known market set) and the CLOB order book for current `best_ask` per market.
2. For each market, call `weather_runtime.adapters.fetch_all(markets, sources, client)`:
   - **NOAAAdapter** — pulls the NWS station gridpoint, maps `probabilityOfPrecipitation/100` → p_yes.
   - **OpenMeteoAdapter** — pulls the ensemble-api `precipitation_probability_max/100` → p_yes.
   - **PaidSourceAdapter** (only if `RUNTIME_PAID_SOURCE` is set) — tomorrow.io or visualcrossing.
3. Each adapter result is run through `normalize_p_yes(value)` which clamps to [0, 1] and rejects NaN. Out-of-range values never reach the JSON.
4. **Failure path**: if a source's HTTP call raises or returns malformed data, the adapter bumps `consecutive_failures` and returns `None`. If ALL sources return None for a given market, set `all_sources_failed=true` on that market's entry in `forecasts.json`.
5. Write both `runtime/state/forecasts.json` and `runtime/state/markets.json` atomically (tmp + fsync + os.replace) via `state_io.write_state_atomic`.

## Output shape (forecasts.json)
```json
{
  "markets": {
    "<market_id>": {
      "noaa": 0.42,
      "openmeteo": 0.48,
      "paid": 0.45,
      "all_sources_failed": false
    }
  }
}
```

## Output shape (markets.json)
```json
{
  "markets": {
    "<market_id>": {
      "p_market": 0.40,
      "best_ask": 0.42,
      "resolution_at": "2026-08-15T00:00:00Z"
    }
  }
}
```
