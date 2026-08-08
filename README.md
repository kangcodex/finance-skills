```bash
curl -fsSL https://raw.githubusercontent.com/kangcodex/finance-skills/main/scripts/install.sh | bash
```

# finance-skills

A collection of agent skills for financial markets analysis, portfolio construction, smart-money tracking, Singapore-licensed financial advisory, and **autonomous Polymarket weather trading**. Each skill bundles a workflow, a curated source map, and reference docs so the agent (Claude Code, Codex, OpenCode, Cursor, etc.) can answer finance questions without making things up.

## Skill families

| Family | What it does | Skills |
|--------|--------------|--------|
| **Research** | One-shot analysis skills. The user asks a question, the agent produces a cited Markdown report. | `smart-money-tracker`, `daily-market-watch`, `thematic-stock-picker`, `sg-financial-advisor`, `news-rss-watch` |
| **Weather Trading** | Autonomous Polymarket trading agent. Runs unattended on a cron. The user sets up the wallet once, then the agent ticks. | `polymarket-wallet-setup`, `weather-data-fetch`, `signal-gen`, `risk-manage`, `trade-execute` |

Both families share the same flat-skill convention (`SKILL.md` + `references/` + `examples/`). The weather-trading family additionally depends on a **private** `weather_runtime` Python package (sibling repo, not in this tree). The deterministic math + I/O lives in the private runtime; the public SKILL.md files are pure orchestration instructions.

## Install

This repo follows the [vercel-labs/skills](https://github.com/vercel-labs/skills) install pattern. The `skills` CLI works with **OpenCode, Claude Code, Codex, Cursor**, and [68 other agents](https://github.com/vercel-labs/skills#supported-agents).

### Install all skills

```bash
npx skills add kangcodex/finance-skills
```

### Install a single skill

```bash
npx skills add kangcodex/finance-skills --skill thematic-stock-picker

# Direct subpath (works for any agent that resolves GitHub tree URLs)
npx skills add https://github.com/kangcodex/finance-skills/tree/main/skills/thematic-stock-picker
```

### Install for a specific agent only

```bash
npx skills add kangcodex/finance-skills -a claude-code
npx skills add kangcodex/finance-skills -a opencode
npx skills add kangcodex/finance-skills -a codex
```

### Install globally (across all your projects)

```bash
npx skills add kangcodex/finance-skills -g
```

### Non-interactive (CI / scripts)

```bash
npx skills add kangcodex/finance-skills -a claude-code -y
```

The CLI prompts you to choose between **symlink** (recommended — single source of truth, easy updates) or **copy** (independent copies per agent) on first run. Use `-y` to skip the prompt.

### Manual / local install

If you can't or don't want to use the `npx skills` CLI:

```bash
git clone https://github.com/kangcodex/finance-skills.git
cd finance-skills
mkdir -p ~/.claude/skills
cp -r skills/thematic-stock-picker ~/.claude/skills/thematic-stock-picker
```

## Research skills

All four research skills produce **source-cited Markdown reports** and follow a common contract: each has a `SKILL.md` workflow, a `references/` directory with curated source maps or screening criteria, and an `examples/` directory with a sample output for verification.

| Skill | Folder | What it does |
|-------|--------|--------------|
| `news-rss-watch` | [`skills/news-rss-watch/`](skills/news-rss-watch/) | Deterministic RSS/Atom watcher over a 40-feed seed registry (US, China, Singapore, markets, important, arXiv research). Per-feed watermark dedup, cross-feed story clustering + importance scoring, per-category budget, nightly digest mode, Google News search-as-feed for gaps. 27 offline unit tests. |
| `daily-market-watch` | [`skills/daily-market-watch/`](skills/daily-market-watch/) | Global finance news report — 6 sections (Market Overview, Value, Momentum, Allocation, Options, Trends/Risks/Events), 12 region zoom-ins, Fed signals integration. |
| `thematic-stock-picker` | [`skills/thematic-stock-picker/`](skills/thematic-stock-picker/) | High-conviction 5-year thematic stock picker — 5 distinct policy-anchored themes × 5-8 screened small/mid-cap US/ADR names, with screening workings + sources + DD disclaimer. |
| `sg-financial-advisor` | [`skills/sg-financial-advisor/`](skills/sg-financial-advisor/) | Singapore-licensed FA Rep skill — diagnose an insurance + CPF portfolio, compute the LIA gap, apply RES5 surrender warning + FAA-N20 BSC + M9A ILP filter, prioritise a Sequence-style action checklist, integrate with the National Protection stack. |

### Companion skills (cross-skill orchestration)

| From | To | Use case |
|------|----|----------|
| `smart-money-tracker` | `thematic-stock-picker` | When picking a theme, corroborate the basket against institutional positioning (13F) and congressional trades (STOCK Act). |
| `daily-market-watch` | `thematic-stock-picker` | When picking a theme, ground the macro/policy backdrop in the current market tape (Fed signals, rate path, sentiment). |
| `news-rss-watch` | `daily-market-watch` | Poll feeds first for raw new stories; hand the JSON to daily-market-watch when the user wants a synthesized source-cited report instead of raw items. |
| `thematic-stock-picker` | `smart-money-tracker` | When the convergence report flags a ticker, add it to the watchlist and pull a deeper thematic context. |
| `sg-financial-advisor` | `thematic-stock-picker` | When the LIA gap analysis flags freed-up cashflow (e.g. surrender of legacy plans), direct the surplus to a screened thematic basket. |
| `sg-financial-advisor` | `daily-market-watch` | When the action checklist calls for deploying surplus to investments, ground the entry in current macro/market context. |

See [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) for the full cross-skill playbook (research + weather-trading).

## Weather trading skills

The weather-trading family is **safe to leave running unattended** on Polygon Amoy (testnet). Mainnet is gated behind two env-var flags and a cold-wallet signature.

The agent reads each skill's `SKILL.md` and follows the workflow. The first time the user wants to start trading, they invoke the `polymarket-wallet-setup` skill. After that, the four tick skills run in order on a cron (or event-driven), driven by the user's scheduling layer.

```
weather-data-fetch → signal-gen → risk-manage → trade-execute
                                            ↑ always gates on risk.json.halt
```

The skills reference the `weather_runtime` Python package, which is **not in this repo**. It lives in a private sibling repo (kept out of source control by design — the runtime encodes the strategy alpha and the session-key custody code). To install it:

```bash
# One-shot install (fetches the private runtime tarball + sets up venv)
./scripts/install.sh
```

The script will print the rest. It defaults to `./weather-agent/` as the install path and refuses to overwrite a non-empty directory.

The 5 weather-trading skills each have 3 evals (15 total) — see `evals/iterations/iteration-2/`.

## Eval coverage

Two iteration dirs cover the two skill families. Both are evaluated by the same grader (`evals/run_evals.py`).

**Research skills (iteration-1):** 15/15 evals beat baseline, mean delta +62% (91.9% with-skill pass rate).

**Weather-trading skills (iteration-2):** 15/15 evals at 4/4 (100% with-skill pass rate, mean delta +70%).

| Skill | Eval | with_skill | baseline | delta |
|-------|------|-----------|----------|-------|
| smart-money-tracker | show-me-whales-buying-this-quarter | 4/4 | 1/4 | +75% |
| smart-money-tracker | pelosi-tech-buys | 4/4 | 2/4 | +50% |
| smart-money-tracker | q1-2026-smart-money-report | 3/4 | 2/4 | +25% |
| daily-market-watch | default-global-7day-report | 8/10 | 3/10 | +50% |
| daily-market-watch | china-region-zoom | 4/5 | 0/5 | +80% |
| daily-market-watch | executive-summary-only | 4/4 | 3/4 | +25% |
| thematic-stock-picker | default-5-themes-2031 | 10/12 | 5/12 | +42% |
| thematic-stock-picker | single-theme-ai-infrastructure | 4/5 | 1/5 | +60% |
| thematic-stock-picker | screen-defense-stocks | 4/6 | 2/6 | +33% |
| sg-financial-advisor | default-29yo-legacy-ilp | 16/16 | 3/16 | +81% |
| sg-financial-advisor | mid-career-38yo-family-ilp-cleanup | 15/15 | 3/15 | +80% |
| sg-financial-advisor | lite-portfolio-no-legacy | 10/10 | 2/10 | +80% |
| news-rss-watch | comprehensive-outlook-poll | 6/6 | 1/6 | +83% |
| news-rss-watch | singapore-focus | 5/5 | 1/5 | +80% |
| news-rss-watch | json-contract-poll | 5/5 | 1/5 | +80% |

**Weather-trading skills (iteration-2):**

| Skill | Eval | with_skill | baseline | delta |
|-------|------|-----------|----------|-------|
| polymarket-wallet-setup | set-me-up-on-amoy | 4/4 | 2/4 | +50% |
| polymarket-wallet-setup | mainnet-upgrade-with-cold-wallet | 4/4 | 0/4 | +100% |
| polymarket-wallet-setup | check-status-and-rotate-session | 4/4 | 2/4 | +50% |
| weather-data-fetch | fetch-forecasts-for-3-markets | 4/4 | 1/4 | +75% |
| weather-data-fetch | single-market-one-source-down | 4/4 | 2/4 | +50% |
| weather-data-fetch | all-sources-failed-mark-and-skip | 4/4 | 0/4 | +100% |
| signal-gen | compute-signals-from-forecasts | 4/4 | 0/4 | +100% |
| signal-gen | edge-too-small-no-trade | 4/4 | 2/4 | +50% |
| signal-gen | within-last-hour-skip | 4/4 | 1/4 | +75% |
| risk-manage | decide-halt-on-daily-drawdown | 4/4 | 1/4 | +75% |
| risk-manage | halt-on-consecutive-tx-failures | 4/4 | 1/4 | +75% |
| risk-manage | human-pause-action | 4/4 | 0/4 | +100% |
| trade-execute | execute-skip-when-halt-true | 4/4 | 2/4 | +50% |
| trade-execute | slippage-exceeds-tolerance | 4/4 | 3/4 | +25% |
| trade-execute | idempotent-rerun | 4/4 | 1/4 | +75% |

Run the grader: `make evals` (runs both iterations) or `make evals-weather` (iteration-2 only). See [`evals/`](evals/) and `evals/iterations/iteration-2/benchmark.md`.

## Development

```bash
make help              # list all targets
make evals             # run 12 research evals + 15 weather evals
make evals-weather     # run only the 15 weather-trading evals
make install-runtime   # run scripts/install.sh (private runtime fetch + install)
make verify            # smoke-smart-money + evals (full pre-PR gate)
make clean             # remove __pycache__/, .pytest_cache/, *.pyc
```

### Repo layout

```
finance-skills/
├── README.md
├── Makefile
├── LICENSE
├── skills/                            # all skills live here (flat convention)
│   ├── smart-money-tracker/           # research skill 1
│   ├── daily-market-watch/            # research skill 2
│   ├── thematic-stock-picker/         # research skill 3
│   ├── sg-financial-advisor/          # research skill 4
│   ├── news-rss-watch/                # research skill 5 (deterministic feed watcher)
│   ├── polymarket-wallet-setup/       # weather-trading skill 1
│   ├── weather-data-fetch/            # weather-trading skill 2
│   ├── signal-gen/                    # weather-trading skill 3
│   ├── risk-manage/                   # weather-trading skill 4
│   └── trade-execute/                 # weather-trading skill 5
├── scripts/
│   └── install.sh                     # one-shot installer for the private runtime
├── evals/                             # cross-skill eval infrastructure (research)
└── docs/                              # architecture decisions
    ├── CHANGELOG.md
    ├── ORCHESTRATION.md
    └── decisions/                     # ADRs 001-012 (10 weather-trading + 2 design)
```

The private `weather_runtime` Python package (the deterministic math + I/O that backs the 5 weather-trading skills) lives in a separate, non-public repo. Install it with `./scripts/install.sh` after installing the skills.

## Documentation

- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — version history
- [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) — how all 9 skills work together
- [`docs/decisions/`](docs/decisions/) — architectural decision records
- [`scripts/install.sh`](scripts/install.sh) — one-shot installer for the private runtime
- [`skills/smart-money-tracker/AGENTS.md`](skills/smart-money-tracker/AGENTS.md) — skill testing framework

## Disclaimer

This software is for informational and educational purposes only. It does not constitute financial advice. Always do your own due diligence before making investment decisions. Past performance is not indicative of future results.

The weather-trading family trades real USDC when run on mainnet. Only deploy with funds you can afford to lose, after reading the full risk framework (in the private runtime's documentation).

## License

MIT — see [`LICENSE`](LICENSE).
