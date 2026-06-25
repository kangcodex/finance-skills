# Orchestration — How the Three Finance Skills Work Together

This repo has three finance skills. Each can be used standalone, but they're designed to compose. This document describes the canonical playbooks for cross-skill workflows.

## Skill roles at a glance

| Skill | Primary lens | Time horizon | Output type | Read/write pattern |
|-------|-------------|-------------|-------------|---------------------|
| `smart-money-tracker` | Institutional + political positioning | T+0 (now), historical 13F quarters | Markdown report + data files | **Read** upstream APIs, **write** `reports/` |
| `daily-market-watch` | Market tape + Fed signals | T-7 to T+0 (trailing week) | Markdown report | **Read** web sources, **write** to user-facing report |
| `thematic-stock-picker` | 5-year policy-anchored baskets | T+0 to T+5y (5-year secular) | Markdown report with basket + screening | **Read** policy + data, **write** basket + sources |

The patterns below show how to combine them.

## Pattern 1 — "Give me a high-conviction watchlist for the next 5 years"

This is the canonical user request that motivated the repo. Use all three skills.

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

The three skills do NOT share state (no shared DB, no shared cache). They each bring their own data sources. This is intentional — each skill is self-contained for `npx skills add` install.

If a user wants a single combined report, the model is expected to invoke each skill sequentially, capture the salient points, and synthesize. The `Companion Skills` section of each SKILL.md names which other skills complement it.

## Failure modes

| Failure | Recovery |
|---------|----------|
| One skill times out on web fetch | Use the others; mark the missing piece as "n/a — [skill] timed out" |
| Smart-money says "no data" (e.g. InsiderFinance.io 404) | Falls back to cached `data/congress/congress-trades.json`; still runs 13F + House Clerk |
| Daily-market-watch region source unreachable | Falls back to the next-tier regional source from `references/regional-sources.md` |
| Thematic picker can't find a name with the required metric | Drops the name from the basket; notes the drop in the report |

See each skill's `## Guardrails` section for the full failure protocol.
