# ADR-009: Cron is hourly + event-driven; not pure hourly, not continuous

## Status
Accepted

## Date
2026-07-28

## Context
The agent needs a schedule. The naive shapes are:
- **Hourly cron.** Simple. Misses forecast updates that land between hours.
- **Continuous (every 1-5 min).** Reacts fast. Overtrades, racks up fees, and gets rate-limited by data sources.
- **Event-driven only.** Misses slow drift in market prices.

Weather forecast cadence: NOAA NWS updates every ~hour (sometimes more often when storms approach). Open-Meteo is on-demand. Market prices on Polymarket move continuously but typically in 1-5% steps every few minutes when active.

## Decision
**Hourly cron + event-driven triggers.**

| Trigger | Fires | Reason |
|---------|-------|--------|
| Hourly cron | Every hour on the hour | Baseline tick. Refreshes forecasts + market state. |
| Forecast update webhook | On new NOAA NWS run | New forecast can flip the blend. Don't wait for the hour. |
| Market price move >5% | On detection during polling | Big price move = information. Re-evaluate. |
| T-24h to market resolution | One-shot per market | Final hour; tighten or close. |
| New market listed | Webhook from Polymarket Gamma API | First-mover on new markets. |

**Debounce:** even with multiple triggers, the agent executes **at most one decision per market per 15 minutes.** This prevents overtrading when many triggers fire in a short window.

**Implementation:** the runtime exposes a small daemon (`runtime/cron.py`) that:
- Runs the hourly tick.
- Polls for events (price move, T-24h, new market) every 5 minutes.
- Debounces per-market to one action per 15 min.

The agent invokes `runtime/cron.py`; the cron invokes the skills in order defined in `docs/ORCHESTRATION.md`.

## Consequences
Positive:
- Forecast updates are picked up within minutes, not hours.
- The hourly tick is the floor; the agent never goes silent.
- The 15-min per-market debounce is the overtrade firewall.
- Cron + event-driven composes: cron fires the tick; events fire additional ticks; debounce keeps both sane.

Negative:
- Two systems to operate (cron + event loop). More moving parts than pure cron.
- The 5-min polling loop is a constant small load. Trivial in practice.
- Debounce window is a parameter; if the user wants faster reaction, they reduce it (at higher fee/slippage cost).

## Alternatives considered
- **Pure hourly.** Rejected. Too slow on fast-moving markets and on forecast updates.
- **Pure continuous (every minute).** Rejected. Overtrades, hits rate limits.
- **Event-driven only, no cron.** Rejected. Misses the "nothing changed but I should still check" case.

## See also
- ADR-003: skill family (which skills fire on each tick)
- `docs/ORCHESTRATION.md` (tick sequence)
