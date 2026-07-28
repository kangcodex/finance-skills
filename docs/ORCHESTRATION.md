# Orchestration — How the Finance Skills Work Together

This repo has two skill families (9 skills total). Each can be used standalone, but they're designed to compose. This document describes the canonical playbooks for cross-skill workflows.

## Skill roles at a glance

| Skill | Primary lens | Time horizon | Output type | Read/write pattern |
|-------|-------------|-------------|-------------|---------------------|
| `smart-money-tracker` | Institutional + political positioning | T+0 (now), historical 13F quarters | Markdown report + data files | **Read** upstream APIs, **write** `reports/` |
| `daily-market-watch` | Market tape + Fed signals | T-7 to T+0 (trailing week) | Markdown report | **Read** web sources, **write** to user-facing report |
| `thematic-stock-picker` | 5-year policy-anchored baskets | T+0 to T+5y (5-year secular) | Markdown report with basket + screening | **Read** policy + data, **write** basket + sources |

The patterns below show how to combine them.

## Pattern 1 — "Give me a high-conviction watchlist for the next 5 years"

This is the canonical user request that motivated the repo. Use all three research skills.

```
Step 1 (smart-money-tracker):
  Run the convergence report to find tickers where institutional
  whales and politicians are aligned.
  → produces convergence-signal tickers

Step 2 (daily-market-watch):
  For each convergence ticker, pull the trailing-7-day tape to
  understand current momentum, Fed sensitivity, sector rotation.
  → produces context for each ticker

Step 3 (thematic-stock-picker):
  Plug the convergence tickers as candidate names into a thematic
  basket. Run the screening funnel to filter to 5-8 small/mid-cap
  names. Show the screening workings (how the universe was reduced
  to the basket). Cross-reference the 13F + congress positioning
  in the rationale for each pick.
  → produces final basket with rationale
```

## Pattern 2 — "Should I rotate from value to momentum this week?"

```
Step 1 (daily-market-watch):
  Run a global market watch to see sector rotation, sentiment
  indicators, Fed cut pricing, COT positioning.
  → produces current regime read

Step 2 (smart-money-tracker):
  Check what whales are buying vs selling this quarter.
  Compare to last quarter's 13F changes.
  → produces institutional positioning delta

Step 3 (thematic-stock-picker):
  If the regime has changed (e.g. defensive → risk-on), re-run the
  theme selection and rebalance. The screening criteria stay the
  same; only the universe is rescoped.
  → produces a rebalanced basket
```

## Pattern 3 — "What's moving China markets this week?"

```
Step 1 (daily-market-watch with region zoom = China):
  Pull China-specific market data (CSI 300, HSI, PBoC, USD/CNY)
  using Caixin, SCMP, PBoC sources.
  → produces China-only market report

Step 2 (smart-money-tracker):
  Filter congress to anyone with China exposure (Pelosi, etc.).
  If any China-related 13F moves are reported, flag them.
  → produces positioning overlay

Step 3 (thematic-stock-picker):
  Plug China themes (semis reshoring, critical minerals, defense)
  into a China-weighted basket. Note that this is a smaller basket
  because of ADR-only constraint.
  → produces China basket
```

## Pattern 4 — "Quick answer only"

For a one-shot question (e.g. "did Pelosi buy any tech stocks recently?"), skip the orchestration and just invoke the one skill:

| Question shape | Use this skill |
|----------------|---------------|
| "What's in the [Fed / market / sector] news this week?" | `daily-market-watch` |
| "What are [whales / Pelosi / politicians] doing?" | `smart-money-tracker` |
| "5-year stock picks for [theme]?" | `thematic-stock-picker` |

## Cross-skill data sharing

The research skills do NOT share state (no shared DB, no shared cache). They each bring their own data sources. This is intentional — each skill is self-contained for `npx skills add` install.

If a user wants a single combined report, the model is expected to invoke each skill sequentially, capture the salient points, and synthesize. The `Companion Skills` section of each SKILL.md names which other skills complement it.

## Failure modes

| Failure | Recovery |
|---------|----------|
| One skill times out on web fetch | Use the others; mark the missing piece as "n/a — [skill] timed out" |
| Smart-money says "no data" (e.g. InsiderFinance.io 404) | Falls back to cached `data/congress/congress-trades.json`; still runs 13F + House Clerk |
| Daily-market-watch region source unreachable | Falls back to the next-tier regional source from `references/regional-sources.md` |
| Thematic picker can't find a name with the required metric | Drops the name from the basket; notes the drop in the report |

See each skill's `## Guardrails` section for the full failure protocol.

---

# Weather Trading Skill Family — Orchestration

This repo also ships a second skill family for **autonomous Polymarket weather trading**. Unlike the three research skills above, these are designed to run unattended on a cron, not in response to a one-shot user prompt.

The skills reference the `weather_runtime` Python package, which is **not in this repo** (private sibling repo). Install with `./scripts/install.sh`.

## Family at a glance

| Skill | Cadence | Purpose |
|-------|---------|---------|
| `polymarket-wallet-setup` | One-time | Wallet + session key bootstrap. |
| `weather-data-fetch` | Per-tick | Pull forecasts + market state. |
| `signal-gen` | Per-tick | Blend sources, compute edge. |
| `trade-execute` | Per-tick (conditional) | Place orders (gated by risk). |
| `risk-manage` | Per-tick + heartbeat | Sizing, caps, halt, Brier tracking. |

Full design lives in the private runtime's documentation. The skills' `## Workflow` sections are the canonical reference for the public surface.

## Tick sequence

Every trigger (hourly cron, NWS update webhook, market price move >5%, T-24h, new market) fans out to this sequence. The dispatcher enforces **at most one decision per market per 15 minutes** (debounce).

```
weather-data-fetch                          ── write forecasts.json, markets.json
    │                                        ── append alerts(severity=info) on each source pull
    │
    ▼
signal-gen                                  ── read forecasts + markets + source_weights
    │                                        ── write signals.json
    │
    ▼
risk-manage (sizing + halt decision)        ── write risk.json (bankroll, exposure, halt, f_size_capped)
    │                                        ── append trade_audit on any size decisions
    │
    ▼
   IF halt == false AND any signal.trade == true:
        trade-execute                       ── pre-trade risk check
                                            ── place orders on Polymarket CLOB
                                            ── append trade_audit on every order attempt
                                            ── write positions.json
    │
    ▼
risk-manage (post-trade, on every tick)     ── update Brier for resolved markets
                                            ── update daily PnL, exposure
                                            ── check halt conditions
                                            ── append alerts on any halt / soft anomaly
                                            ── update source_weights.json on resolution
                                            ── emit heartbeat (webhook + SQLite alerts table)
    │
    ▼
   On market resolution (detected by trade-execute polling Gamma):
        risk-manage                         ── append brier_outcomes (one row per source)
                                            ── append settled_markets (upsert)
```

## Cross-skill contracts

Two layers, by access pattern.

**Current-tick state (JSON files, atomic replace):**

| From | To | File |
|------|-----|------|
| `weather-data-fetch` | `signal-gen` | `forecasts.json`, `markets.json` |
| `signal-gen` | `risk-manage`, `trade-execute` | `signals.json` |
| `risk-manage` | `trade-execute` | `risk.json` (read; idempotent pre-trade check) |
| `trade-execute` | `risk-manage` | `positions.json` |
| `risk-manage` | (all) | `source_weights.json` (re-read by `signal-gen` next tick) |

**Append-only history (SQLite, WAL mode):**

| Written by | Table | Why |
|------------|-------|-----|
| `weather-data-fetch` | `alerts` (severity=info) | Source health history |
| `risk-manage` | `alerts` (severity=soft/hard) | Halt + anomaly queue |
| `risk-manage` | `brier_outcomes` | Per-source per-resolution record → source weight update |
| `risk-manage` | `settled_markets` | Backtest source |
| `trade-execute` | `trade_audit` | Every order attempt, for debugging + reconciliation |
| Heartbeat daemon | `alerts` (severity=info) | Heartbeat fallback when webhook is down |

## Failure handling

| Failure | Recovery |
|---------|----------|
| `weather-data-fetch` returns empty | Skip `signal-gen` for affected markets; soft anomaly. |
| `signal-gen` produces zero signals | End tick. |
| `trade-execute` order rejected (slippage, no liquidity) | Log reason; try again next debounce window if signal persists. |
| `risk-manage` sets `halt=true` | All subsequent ticks skip `trade-execute` until human resumes. |
| Skill timeout (>2 min) | Runtime kills skill, sets soft anomaly, continues. |

## Human override

At any time the user can:
- Invoke `risk-manage` with `action: pause` → halts trading (read-only mode).
- Invoke `risk-manage` with `action: resume` → clears halt, with required reason.
- Invoke `risk-manage` with `action: close_all` → market-close every position at best bid, then halt.

These are the only ways the user interacts with the running agent outside of the heartbeat.

## See also

- ADR-003 through ADR-012 (in `docs/decisions/`)
- The private runtime's documentation (installed via `./scripts/install.sh`)
