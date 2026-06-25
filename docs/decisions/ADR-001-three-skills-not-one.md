# ADR-001: Three skills, not one

## Status
Accepted

## Date
2026-06-25

## Context

A user prompt that produces a comprehensive finance report can span 4-6 distinct concerns:

1. Current market tape (indices, bonds, FX, commodities, crypto)
2. Fed / central-bank signals (rate path, positioning, vol)
3. Top stock / ETF / crypto picks (value + momentum)
4. Portfolio allocation + rebalancing
5. Options strategies
6. Trends / risks / upcoming events

Plus a separate "smart money" concern (institutional + political positioning) that complements the market read.

The first attempt was a single mega-skill covering all six sections of the user's @crypto_condom-inspired daily market watch prompt. That worked for the daily report but was too narrow for the "what should I own for 5 years" prompt and the "what are Pelosi and the whales doing" prompt.

## Decision

Split into three orthogonal skills, each with a single primary lens:

| Skill | Lens | What it owns |
|-------|------|--------------|
| `smart-money-tracker` | **Who is positioned** (institutions + politicians) | SEC 13F + STOCK Act + House Clerk |
| `daily-market-watch` | **What is moving the tape** (markets + Fed) | Indices, bonds, FX, commodities, crypto, Fed signals, value/momentum picks, allocation, options, trends/risks/events |
| `thematic-stock-picker` | **5-year secular basket** (policy-anchored) | 5 themes × 5-8 screened tickers, screening workings, sources, DD disclaimer |

The three skills share the user-facing **disclaimer + sources + Markdown-report** contract, but each has its own source map, workflow, and example output.

## Consequences

Positive:

- Each skill is **installable independently** via `npx skills add kangcodex/finance-skills --skill X`
- Each skill's `SKILL.md` can stay under 500 lines (the daily-market-watch 6-section skill is the longest at ~320 lines)
- Eval grading is clean: 3 evals per skill, 9 total, each with assertions that are unambiguous
- Users get the right amount of structure for the right question: "what's moving" doesn't need a 5-year thesis; "5-year thesis" doesn't need yesterday's CPI print

Negative:

- A user who wants "everything" has to invoke all three (orchestration playbook in `docs/ORCHESTRATION.md`)
- Some content overlaps (e.g. Fed signals appear in daily-market-watch AND inform thematic-stock-picker)
- The model has to make a routing decision; if it routes wrong, the user has to re-prompt

## Alternatives considered

- **One mega-skill** with all 6 sections + 3 lenses. Rejected: the SKILL.md would exceed 500 lines, evaluation would be muddy, and the install pattern is less flexible.
- **Two skills** (market-watch + picker, fold smart-money into picker). Rejected: smart-money is a different *data source class* (institutional disclosure filings, not market tape or policy) and warrants its own skill.
- **Four skills** (split daily-market-watch into market-data and value-momentum-allocation). Rejected: the 6 sections of the daily report are tightly coupled (Fed signals tie directly to allocation and options); splitting makes the workflow harder to follow.

## See also

- `docs/ORCHESTRATION.md` — how the three skills work together
- `docs/decisions/ADR-002-region-zoom-source-zoom.md` — design principle shared across the research-driven skills
