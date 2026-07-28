---
name: weather-data-fetch
description: >-
  Pulls weather forecasts from N sources and the Polymarket book for every
  tracked market, normalizes to `p_yes in [0, 1]`, and writes
  `forecasts.json` + `markets.json` atomically. v1 sources: NOAA NWS (US,
  free, station-id-keyed), Open-Meteo (global, free, ensemble), and one
  paid source (Tomorrow.io or Visual Crossing, configurable). A single
  source failure does not block the others; if ALL sources fail for a
  market, the entry is flagged `all_sources_failed: true` so `risk-manage`
  can auto-halt after the 1h threshold. Use this skill on every per-tick
  cycle BEFORE `signal-gen` reads `forecasts.json`. Triggers on "fetch
  forecasts", "pull the weather data", "refresh market X", or any
  data-layer step in the weather-trading pipeline.
---

# weather-data-fetch

The data layer of the weather-trading agent. Pulls forecasts and market
state, normalizes to a common shape, writes atomically. Strategy lives
in `signal-gen`; this skill is the producer it consumes.

## When to use

- **Per-tick** (hourly cron + event-driven triggers): pull for every
  market in `runtime/state/tracked_markets.json`.
- **Per-market refresh** (e.g. a price-move event triggers a single
  market refresh): call `weather_runtime.adapters.fetch_all` with the
  one market.

Do not call this skill on a market that is not in `tracked_markets.json`.
The signal-gen skill reads only the forecasts in this skill's output.

## Inputs (read-only)

| File / env | Purpose |
|------------|---------|
| `runtime/state/tracked_markets.json` | Markets to fetch. Each entry has `market_id`, `question`, `station_id` (for NOAA), `lat`, `lon`. |
| `RUNTIME_PAID_PROVIDER` | `tomorrow.io` or `visualcrossing`. Required if the paid source is enabled. |
| `RUNTIME_PAID_API_KEY` | API key for the paid source. If unset, the paid source is silently skipped (not failed). |

## Output (written)

| File | Purpose | Permissions |
|------|---------|-------------|
| `runtime/state/forecasts.json` | `{market_id: {source_name: p_yes, "p_market": float, "all_sources_failed": bool}}`. | normal |
| `runtime/state/markets.json` | Snapshot of Polymarket market state: `{market_id: {question, side_yes_best_ask, side_no_best_ask, ...}}`. | normal |

## Source adapters (v1)

| Class | Endpoint | Free | Coverage |
|-------|----------|------|----------|
| `NoaaAdapter` | `api.weather.gov/stations/{station_id}` | yes | US only |
| `OpenMeteoAdapter` | `ensemble-api.open-meteo.com/v1/ensemble` | yes | global |
| `PaidSourceAdapter(provider="tomorrow.io")` | `api.tomorrow.io/v4/timelines` | no | global |
| `PaidSourceAdapter(provider="visualcrossing")` | `weather.visualcrossing.com/...` | no | global |

Adding a new source = implement the `ForecastSource` protocol (`name`,
`p_yes(market) -> float`) and add an instance to the `sources` list. No
changes to this skill's body.

## Workflow

1. **Read `tracked_markets.json`.** Abort with a clear reason if missing.
2. **Build the source list** from env:
   - `NoaaAdapter(client, station_id=market.station_id)` — one per market.
   - `OpenMeteoAdapter(client)` — one shared.
   - `PaidSourceAdapter(client, provider=RUNTIME_PAID_PROVIDER)` if
     `RUNTIME_PAID_API_KEY` is set, else skipped.
3. **For each market**:
   1. Pull the CLOB book via `client.get_book(market_id)`. Synthesize
      `p_market = best_ask` on the YES side.
   2. For each source, call `src.p_yes(market)`. On any exception, log
      a warning, leave that source out of the entry, and continue.
   3. If every source failed, set `all_sources_failed = true`.
4. **Normalize** every `p_yes` to [0, 1] via
   `adapters.normalize_p_yes(value)`. Out-of-range values are clamped
   to the boundary, NaN raises.
5. **Write** `forecasts.json` and `markets.json` atomically (tmp +
   fsync + `os.replace`).

## Failure handling

- **Single source failure**: log, skip that source's row, do not fail
  the skill. The other sources cover the gap.
- **All sources failed for one market**: set
  `all_sources_failed = true` and keep `p_market`. `signal-gen` will
  produce a no-signal for that market.
- **All sources failed for every market**: emit a hard-anomaly via
  `db.append_alert(severity="hard", kind="data_source_failures", ...)`.
  `risk-manage` auto-halts after the 1h threshold.
- **HTTP 429**: back off exponentially per source. Skill is idempotent
  on retry because each call is independent.
- **NaN or out-of-range p_yes**: `normalize_p_yes` rejects NaN outright
  and clamps out-of-range. Loudly, not silently.

## Guardrails

- **Never** write a probability outside [0, 1] to `forecasts.json`.
  `signal-gen` assumes the contract; an out-of-range value would
  silently corrupt the blend.
- **Never** modify `tracked_markets.json` from this skill. That file
  is maintained out-of-band.
- **Never** place orders. This skill is read-only against the CLOB
  (best-ask reads only).
- **Strategy and config are fixed.** The mapping
  `precipitation_probability → p_yes` is the simplest sensible default
  for a precipitation market. Do not propose new mappings as strategy
  changes — they are adapter-internal.

## Runtime reference

`weather_runtime.adapters` — module that implements everything above.
