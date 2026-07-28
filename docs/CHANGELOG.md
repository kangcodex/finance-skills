# Changelog

All notable changes to this repo are documented here. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- 5 weather-trading skills (orchestration-only, no executable code): `polymarket-wallet-setup`, `weather-data-fetch`, `signal-gen`, `risk-manage`, `trade-execute`. Each is a flat `SKILL.md` that references the `weather_runtime` Python package.
- `scripts/install.sh` — one-shot installer for the **private** runtime. Fetches the runtime tarball, runs `uv sync` + editable install, drops a `.env` from `.env.example`, and prints the next-step commands. Env-overridable: `INSTALL_DIR`, `RUNTIME_REPO` (default `kangcodex/weather-runtime`), `RUNTIME_REF` (default `main`).
- `docs/decisions/ADR-003` through `ADR-012` — 10 ADRs covering the 5-skill family, taxonomy, Amoy-default, custody, signal blend, sizing, cron, fixed strategy, autohalt, docs structure.
- `Makefile` — `install-runtime` target wraps `scripts/install.sh`. `verify` no longer runs the runtime tests (those belong to the private runtime repo). New `help` text reflects the public/private split.

### Architecture
- **Public/private split.** The deterministic math + I/O (sizing, signal blend, halt matrix, wallet setup, orders, adapters) used to live in `runtime/` inside this repo. It has been moved to a separate private repo to keep the strategy alpha and the session-key custody code out of source control. The public repo now ships only the 9 SKILL.md files + the design/decision docs + the install script.

### Removed
- `runtime/` (Python package) — moved to private repo. Reinstall via `./scripts/install.sh`.
- `docs/design/` — gitignored, the inline rationale now lives in each SKILL.md.
- `docs/issues/`, `docs/prds/`, `docs/api/` — gitignored, not part of the public scope.

### Test counts
- Research-skill evals: 12/12 passing, mean delta +57% (unchanged from v1.1.0).
- Runtime tests: 201/201 (run from the private runtime repo after install).

## [1.1.0] — 2026-06-30

### Added
- `sg-financial-advisor` — Singapore-licensed FA Rep skill (research-driven). MAS FAA 2001 / LIA / IBF / CMFAS (RES5, CM-LIP, M9A) grounded. Categorises portfolio into Hospitalisation/Death-TPD/CI/ECI/PA/Investment-Legacy buckets; computes LIA gap (×10 Death, ×4 CI, ×1 ECI, ×4 PA); injects RES5/FAA-N16 surrender warning with sunk-cost table before any termination recommendation; runs FAA-N20 Balanced Scorecard; flags ILPs via M9A keyword filter (Link/Flexi/Sub-Funds/Premium Allocation); diagnoses Premium Overhead Inefficiency; integrates National Protection stack (MediShield Life + Integrated Shield + CareShield Life + HPS); optimises CPF (OA vs SA, SA top-up S$8k, emergency fund 3-6/6-12 mo). Output: Sequence-style action checklist (risk-first), grouped sources, verbatim SG-FA disclaimer.
- `evals/iterations/iteration-1/eval-3-sgfa/` — 3 prompts (default 29yo legacy ILP, mid-career 38yo family, lite 45yo no-legacy) with 41 graded assertions total. All 3 evals pass at 100% (41/41); mean delta +80% over baseline.
- `docs/design/sg-financial-advisor.md` — design notes
- `evals/` now runs 12 evals across 4 skills, mean delta +57%
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
