# All sources failed

## Scenario
NOAA returns 503, Open-Meteo returns empty body, paid source returns 401 (key expired).

## fetch_all behavior
```python
result["markets"]["m1"] = {
    "noaa": None,
    "openmeteo": None,
    "paid": None,
    "all_sources_failed": True,
}
```

Each adapter bumps its `consecutive_failures` and records `last_error`:
- NOAA: `"HTTP 503 Service Unavailable"`, failures=1
- Open-Meteo: `"empty response"`, failures=1
- Paid: `"HTTP 401 Unauthorized"`, failures=1

## Downstream

1. **signal-gen** still runs. With all source p_yes = null, `blend_probability` cannot compute a meaningful blend — only `p_market` is known. The signal ends up as `p_blend = w_market * p_market + (1 - w_market) * p_market = p_market` (using the market as its own source). `edge = 0` and `reason = "all sources returned identical p (no signal)"`. **`trade = false`**.

2. **risk-manage** runs `check_soft_anomalies()` which contains an `all_sources_failed` check. If this persists for >1h, the soft anomaly fires; the user is expected to ack within the window. If not acked, the `NO_ACK_FOR_SOFT_ANOMALY` halt fires.

3. The risk-manage skill also writes `risk.json` with `halt = false` (the halt matrix's `ALL_SOURCES_FAILED` is a >1h threshold check), but the soft-anomaly state is recorded.

## Recovery
- Diagnose: are all sources really down, or is the failure local (network, key)?
- Re-test each source manually.
- The next tick will re-run; if sources recover, the `consecutive_failures` counter resets on first success.
