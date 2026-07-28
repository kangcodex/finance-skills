# Handling a single-source failure

If NOAA is rate-limiting you, you have a few options:

1. **Wait and retry** — NOAA's rate limits usually reset after a few minutes.
2. **Use Open-Meteo instead** — it's a free global weather API and covers most US locations.
3. **Switch to a paid source** — tomorrow.io or visualcrossing will give you better reliability.

For a single market, I'd just rely on Open-Meteo. You don't need multiple sources for a one-off query.

The forecasts.json should look like:
```json
{
  "markets": {
    "nyc-rain-jul4": {
      "openmeteo": 0.32
    }
  }
}
```
