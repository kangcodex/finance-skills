# ADR-002: Region zoom-in = source zoom-in

## Status
Accepted

## Date
2026-06-25

## Context

A user might ask any of:

- "Give me a daily market watch for this week" → default: global
- "Zoom into China markets this week" → region zoom: China + HK
- "What's moving Japan markets this week" → region zoom: Japan
- "EU market outlook" → region zoom: EU

The naive interpretation of "zoom into China markets" is to scope the *content* to China (e.g. only show CSI 300, Hang Seng, USD/CNY, China-specific news). The more useful interpretation is to also scope the *sources* to Chinese-language and China-focused outlets.

The second interpretation is what users want: a "zoom into China" report should not pull coverage from English-language US outlets (CNBC, WSJ) about China. The report should read like a Chinese-speaking sell-side analyst wrote it for a domestic audience.

## Decision

When `daily-market-watch` is invoked with a region zoom, **both** the content and the source map are scoped to that region:

| Region | Source pool (top tier) |
|--------|----------------------|
| China | Reuters China, Bloomberg China, SCMP, Caixin Global, Caixin (中文), 21st Century Business Herald, Yicai, Eastmoney |
| Japan | Nikkei Asia, Reuters Japan, BoJ, METI, Ministry of Finance, Japan Times |
| EU | ECB, Eurostat, Bundesbank, Reuters Europe, FT, Handelsblatt, Les Echos |
| US | Fed, Treasury, SEC, BLS, BEA, CFTC, Reuters US, Bloomberg US, WSJ, CNBC, MarketWatch |

The skill's `references/regional-sources.md` is the canonical source map. The skill's `## Guardrails` section explicitly states this rule:

> **Region-zoom = source-zoom.** For "China only", use Chinese-language or China-focused sources (Caixin, SCMP, PBoC). For "Japan only", use Nikkei, BoJ, METI. Do not extrapolate from US/English-language coverage of a non-US market.

## Consequences

Positive:

- Reports read like authentic regional coverage
- The model can't fall back to "China news from US perspective" — a known failure mode
- The user gets the same answer a regional analyst would give

Negative:

- The model needs the regional source map loaded as a reference; SKILL.md alone is not enough. The skill's workflow has a hard dependency on `references/regional-sources.md`.
- If the regional source is unreachable (e.g. SCMP paywall), the model has to fall back to a next-tier regional source, not a US/English source. The Guardrails section documents this fallback.

## Alternatives considered

- **Region content-only, global sources**: cheaper, but produces a "China viewed from New York" report. Rejected.
- **Per-region skill variants** (daily-market-watch-china, daily-market-watch-japan): would solve the source scoping at install time but triples the maintenance burden. Rejected.
- **Auto-translation of Chinese sources**: introduces a translation layer the user didn't ask for. Rejected.

## See also

- `daily-market-watch/SKILL.md` — the Guardrails section that operationalises this rule
- `daily-market-watch/references/regional-sources.md` — the canonical source map
