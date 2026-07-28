# Single market, NOAA rate-limiting

## Scenario
- market_id = "nyc-rain-jul4"
- NOAA NWS returns HTTP 429
- Open-Meteo returns a clean response

## fetch_all behavior
```python
result = adapters.fetch_all(markets, sources, client)
# result["markets"]["nyc-rain-jul4"] = {
#     "noaa": None,                # adapter caught the 429, bumped failures
#     "openmeteo": 0.32,           # clean response, normalized to [0,1]
#     "paid": None,                # not configured
#     "all_sources_failed": False  # because openmeteo returned a value
# }
```

The NOAA adapter bumps `consecutive_failures` from 0 to 1 and records `last_error = "HTTP 429"`. Per the contract, after 3 consecutive failures the adapter is treated as down for soft-anomaly purposes (the `risk-manage` skill will surface this as a `forecast_divergence` or `all_sources_failed` check downstream).

## Output (forecasts.json, atomically written)
```json
{
  "markets": {
    "nyc-rain-jul4": {
      "noaa": null,
      "openmeteo": 0.32,
      "paid": null,
      "all_sources_failed": false
    }
  }
}
```

## Important
`all_sources_failed` is `false` because at least one source (Open-Meteo) returned a value. The signal-gen step will blend with what it has; the Brier score for the failing source will be 0 at next resolution and bump its failure count further.
