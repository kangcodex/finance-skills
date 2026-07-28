# ADR-004: Skill taxonomy is 5 skills with the 3+2 cadence split

## Status
Accepted

## Date
2026-07-28

## Context
ADR-003 chose a 5-skill family. The remaining question is the taxonomy itself: where do the seams between skills live? The driver is **cadence** — skills that fire at the same cadence can share state, while skills that fire at different cadences need clean contracts.

Workflow cadences:
- **One-time**: wallet bootstrap, first fund, smoke test.
- **Per-tick (hourly + event-driven)**: data fetch → signal → execute.
- **Per-tick + heartbeat**: risk monitoring runs on every tick AND emits a heartbeat to the human; kill-switch runs continuously.

A monolithic "trade" skill would force all three cadences into one context. The seams chosen here are at the I/O boundaries: each skill's output is the next skill's input, persisted to disk in between (JSON files in `runtime/state/`).

## Decision

| Skill | Cadence | Reads | Writes | Trigger |
|-------|---------|-------|--------|---------|
| `polymarket-wallet-setup` | One-time | `runtime/secrets/wallet.json` (or env) | same | `setup` / `bootstrap` / first run |
| `weather-data-fetch` | Per-tick | source APIs | `runtime/state/forecasts.json`, `runtime/state/markets.json` | tick + on event (new NWS run, market price move >5%) |
| `signal-gen` | Per-tick | forecasts + markets | `runtime/state/signals.json` | tick |
| `trade-execute` | Per-tick (conditional on signal) | signals + positions | `runtime/state/positions.json`, CLOB orders | tick IF signal has positive expected value |
| `risk-manage` | Per-tick + heartbeat | positions + market prices + pnl | `runtime/state/risk.json`, kill-switch flag, push notif | every tick + on threshold breach |

**Contract between skills = JSON files in `runtime/state/`.** No direct in-memory coupling. Skills are independently testable.

## Consequences
Positive:
- Clean eval boundaries: 5 skills × 3 evals = 15, each with assertions on the produced JSON.
- `risk-manage` can run in dry-run mode while `trade-execute` is off.
- Skills can be re-invoked in isolation during debugging.

Negative:
- JSON-on-disk coupling is slower than in-memory; tick latency is bounded by file I/O (~ms, irrelevant vs network).
- Schema drift: any change to `signals.json` shape ripples to `trade-execute`. Mitigated by version field in each file.

## Alternatives considered
- **3 skills** (setup, trade, risk). Rejected: `trade` collapses three distinct concerns.
- **7 skills** (split trade into signal + size + execute, split risk into limits + pnl + heartbeat). Rejected: too thin; the orchestration doc becomes the largest artifact.
- **2 skills** (one-time setup, runtime loop). Rejected: hides the data→signal→execute pipeline behind a black box.

## See also
- ADR-003: family on thin runtime
- ADR-007: event-driven cron
- `docs/ORCHESTRATION.md`
