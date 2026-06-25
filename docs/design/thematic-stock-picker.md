# thematic-stock-picker — Design Notes

## Purpose

A single research-driven skill that produces a "5-Year Thematic Stock Picks" Markdown report. Generates 5 distinct policy-anchored themes and a **screened** basket of 5-8 US-listed or ADR small/mid-cap names per theme. Always shows the **screening workings** (universe → filters → survivors) and **cites sources** for every pick and every policy claim.

## What it is NOT

- Not a price-target call. The skill produces a thesis + watchlist, not "PT $X".
- Not a long-term hold recommendation. The skill is a starting point for further research; the user must do their own DD.
- Not a backtest. The picks are forward-looking thesis-driven, not historically optimised.
- Not a single-theme skill. The default is 5 themes; the user can ask for 1, 3, or 7.

## Output contract

Every report must contain exactly the canonical template (see SKILL.md "Output Template"):

1. **Scope** — horizon, universe, mcap range, theme count, basket size
2. **Section 0: Macro & Policy Backdrop** — 5-8 numbered policy drivers, each with a URL
3. **Section 1: Screening Workings** — master screen + per-theme overlay + funnel counts
4. **Section 2: 5 Thematic Predictions** — 5 themes × (2-3 sentence thesis + 5-8 tickers with 4 bullets each)
5. **Section 3: Top 2-3 Convictions + Cross-Cutting Risks**
6. **Section 4: Sources** — grouped by category
7. **DD Disclaimer** — verbatim "Always do your own DD — this is not financial advice."

## The 4-bullet format per ticker

For each ticker in a basket, the skill produces exactly 4 sub-bullets:

- **(a) Thesis fit** — 1 line: why this company fits the theme
- **(b) Catalyst** — 1 line: the specific 12-24 month event
- **(c) Valuation / risk** — 1 line: current valuation + key risk
- **(d) Edge + 5-year conviction** — 1 line: why this isn't priced in + conviction tier (Med/High/Very High)

Tight, not bloated. Most picks should be Med/High; Very High is rare (≤1 in 5).

## Screening discipline

The screening workings section is the load-bearing piece. Every pick must survive:

1. **Master screen** — mcap, $ volume, revenue, growth, gross margin, leverage, insider ownership, OCF
2. **Per-theme overlay** — revenue exposure to the theme's sector, regulatory status, jurisdiction, etc.

The report must show:

- Initial universe size (named screener)
- After master screen count
- After theme overlay count
- Final basket count

If a pick was added off-screen (e.g. from a 13F cluster buy), the skill must say so in the per-ticker rationale. The screen is the floor, not the ceiling — but off-screen picks must justify themselves.

## Conviction tier system

| Tier | Meaning | % of picks |
|------|---------|-----------|
| Very High | Would put real money behind; 3+ bagger potential | <10% |
| High | Strong thesis, 2x+ expected; < 30% downside | ~40% |
| Med-High | Solid setup, identifiable catalyst | ~30% |
| Med | Worth watching; not enough edge to be a basket core | ~20% |
| Low | Mention only; thesis is weak or risks dominate | 0% (don't include) |

## Voice

Channel `@crypto_condom` on X (high-conviction thematic investor, policy-obsessed, multi-year horizon, willing to be early and contrarian):

- Punchy, declarative, no fluff
- Policy-anchored every time
- Asymmetric ("3-bagger or it goes to zero" register)
- No memes, no pumps
- Source every claim

## Guardrails (from SKILL.md)

- No fabricated numbers. `n/a` if not verifiable.
- No price targets. Thesis language only ("watchlist idea", "high-conviction long").
- No "buy/sell" imperative. Use "thesis", "watchlist", "high-conviction long".
- Conviction must be honest. Very High is rare.
- Minimal ticker overlap across themes.
- Always end with the verbatim DD disclaimer.

## How "with-skill" differs from "without-skill"

A model without the skill responding to "5 thematic stock predictions for 2031" might produce:
- A short list of tickers with one-line rationales
- No policy anchoring
- No screening workings
- No sources
- No conviction tier
- No DD disclaimer
- High overlap with the user's pre-existing knowledge (no value-add)

The eval results confirm: with_skill beats baseline on all 3 evals (mean delta +45%).

## See also

- `skills/thematic-stock-picker/SKILL.md` — full workflow + voice guide
- `skills/thematic-stock-picker/references/screening-criteria.md` — master screen + 9 per-sector overlays
- `skills/thematic-stock-picker/references/sector-themes.md` — 2026-2031 policy-anchored theme catalog
- `skills/thematic-stock-picker/examples/sample-report.md` — full 5-theme canonical example
- `skills/thematic-stock-picker/examples/sample-ai-infra.md` — single-theme example
- `evals/iterations/iteration-1/eval-2-thematic/` — eval data
