# Changelog

All notable changes to this repo are documented here. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `docs/ORCHESTRATION.md` — cross-skill playbook
- `docs/decisions/ADR-001-three-skills-not-one.md`
- `docs/decisions/ADR-002-region-zoom-source-zoom.md`
- `docs/api/Fed-signals.md` — canonical source map for Fed/CME/EDGAR
- `docs/design/daily-market-watch.md`
- `docs/design/thematic-stock-picker.md`
- `evals/` infrastructure: 9 evals, programmatic grader, benchmark
- `Makefile` with `evals`, `smoke-smart-money`, `verify` targets
- `README.md` (top-level)
- `examples/` directories in all 3 skills

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
