# Changelog

All notable changes to this repo are documented here. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `news-rss-watch` — deterministic, agent-agnostic RSS/Atom news watcher skill. 40-feed seed registry (US, China, Singapore, markets, important, arXiv research), per-feed watermark dedup, cross-feed story clustering + importance scoring, per-category budget, nightly digest mode (`--action digest`), Google News search-as-feed (`--action add-search`), arXiv topic watcher (`watch_arxiv.py`). Stdlib-only Python, strict JSON/markdown CLI contract, 27 offline unit tests (`make test-news-rss`).
- `evals/iterations/iteration-1/eval-4-news-rss-watch/` — 3 prompts covering feed polling, regional scope, deduplication, source URLs, importance scores, and the JSON contract.

### Removed
- Retired the automated-trading skill family, installer, architecture docs, and evals; this repo now contains five research skills.

### Fixed
- `run_evals.py` — partial `--eval-set` runs now merge prior benchmark rows instead of truncating the benchmark to the selected set.

## [1.1.0] — 2026-06-30

### Added
- `sg-financial-advisor` — Singapore-licensed FA Rep skill (research-driven). MAS FAA 2001 / LIA / IBF / CMFAS (RES5, CM-LIP, M9A) grounded. Categorises portfolio into Hospitalisation/Death-TPD/CI/ECI/PA/Investment-Legacy buckets; computes LIA gap (×10 Death, ×4 CI, ×1 ECI, ×4 PA); injects RES5/FAA-N16 surrender warning with sunk-cost table before any termination recommendation; runs FAA-N20 Balanced Scorecard; flags ILPs via M9A keyword filter (Link/Flexi/Sub-Funds/Premium Allocation); diagnoses Premium Overhead Inefficiency; integrates National Protection stack (MediShield Life + Integrated Shield + CareShield Life + HPS); optimises CPF (OA vs SA, SA top-up S$8k, emergency fund 3-6/6-12 mo). Output: Sequence-style action checklist (risk-first), grouped sources, verbatim SG-FA disclaimer.
- `evals/iterations/iteration-1/eval-3-sgfa/` — 3 prompts (default 29yo legacy ILP, mid-career 38yo family, lite 45yo no-legacy) with 41 graded assertions total. All 3 evals pass at 100% (41/41); mean delta +80% over baseline.
- `docs/design/sg-financial-advisor.md` — design notes
- `evals/` now runs 15 evals across 5 skills, mean delta +57%
- `Makefile` — new `evals-sg-fa` target

## [1.0.0] — 2026-06-25

### Added
- `smart-money-tracker` — SEC 13F + STOCK Act + House Clerk convergence tracker (script-driven)
- `daily-market-watch` — global finance news report with 6 sections + 12 region zoom-ins (research-driven)
- `thematic-stock-picker` — 5-year policy-anchored thematic stock picker with screening (research-driven)
- `.gitignore` — ignores `test-runs/` working artifacts

### Notes
- Smart Money Tracker upstream sources: SEC EDGAR 13F, InsiderFinance.io, House Clerk FD
- Daily Market Watch region sources: 12 regional news sources catalogued in `references/regional-sources.md`
- Thematic Stock Picker screening criteria: master + 9 per-sector overlays in `references/screening-criteria.md`
