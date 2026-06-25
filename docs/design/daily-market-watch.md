# daily-market-watch — Design Notes

## Purpose

A single research-driven skill that produces a structured "Daily Market Watch" Markdown report. Default scope: global (US + EU + Asia). Supports region zoom-in (China / Japan / EU / UK / India / HK / Korea / Australia / Singapore / LatAm / ME) and asset-class zoom-in (crypto only / equities only / etc.).

## What it is NOT

- Not a real-time quote system. The skill produces a report; it does not stream.
- Not a single-ticker deep dive. For "tell me about NVDA" use a different tool.
- Not an options-pricing engine. Section D recommends strategies; it doesn't compute greeks.

## Output contract

Every report must contain exactly the canonical template (see SKILL.md "Output Template"):

1. **TL;DR** — 3-5 bullets, lead with the most important takeaway
2. **Section 0: Market Overview** — 11 sub-fields (indices, bonds, commodities, FX, crypto, sentiment, data prints, Fed signals, other CBs, COT positioning, curve & vol)
3. **Section A: Top 5 Value Opportunities** — 5 stocks + 5 ETFs + 5 crypto
4. **Section B: Top 5 Momentum Picks** — 5 stocks + 5 ETFs + 5 crypto
5. **Section C: Portfolio Allocation Insights** — sample alloc + rebalancing + long/short by class
6. **Section D: Options Strategies** — 3-5 strategies with parameters
7. **Section E: Trends / Risks / Upcoming Events**
8. **Sources** — grouped by category
9. **Disclaimer** — verbatim

The template is non-negotiable. Lite mode (TL;DR + Market Overview + Sources + Disclaimer) is the only exception.

## Inputs the user can override

| Input | Default | Override |
|-------|---------|----------|
| Region scope | Global | "China only", "Asia ex-Japan" |
| Asset focus | All | "crypto only", "equities only" |
| Time window | Last 7 days | Specific dates |
| Portfolio lens | Diversified 60/30/10 | "aggressive growth", "income" |
| Granularity | Standard 5 sections | "lite" (TL;DR + MO only) |
| Output format | Markdown | "table only", "bullet only" |

The skill must state the parsed scope at the top of the report under `## Scope` so the user can correct it.

## Region zoom = source zoom (see ADR-002)

When a user zooms into a region, the model MUST scope the source map to that region, not just the content. For "China only", use Caixin / SCMP / PBoC; do not extrapolate from CNBC / WSJ. The Guardrails section operationalises this.

## Source-citation discipline

Every non-trivial number, every named pick, every Fed/CB signal must trace to a URL in the Sources block. If a number is unverifiable, mark `n/a` and explain — never invent.

## How "with-skill" differs from "without-skill"

A model without the skill responding to "give me a daily market watch" might produce:
- A short paragraph with a few ticker mentions
- No screening workings (because the skill spec doesn't require it)
- No sources block
- No disclaimer (or generic one)
- Likely missing the 6-section structure
- Likely miss regional source discipline

The eval results confirm this: with_skill beats baseline on all 3 evals (mean delta +52%).

## See also

- `skills/daily-market-watch/SKILL.md` — full workflow
- `skills/daily-market-watch/references/regional-sources.md` — 12-region source map
- `skills/daily-market-watch/references/fed-signals.md` — how to read CME FedWatch, SOFR futures, COT, etc.
- `skills/daily-market-watch/examples/sample-report.md` — full canonical example
- `skills/daily-market-watch/examples/sample-lite.md` — lite mode example
- `docs/decisions/ADR-002-region-zoom-source-zoom.md`
- `evals/iterations/iteration-1/eval-1-daily/` — eval data
