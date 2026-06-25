# finance-skills

A collection of agent skills for financial markets analysis, portfolio construction, and smart-money tracking. Each skill bundles a workflow, a curated source map, and reference docs so the agent (Claude Code, Codex, OpenCode, Cursor, etc.) can answer finance questions without making things up.

## Skills in this repo

| Skill | Folder | What it does |
|-------|--------|--------------|
| `smart-money-tracker` | [`smart-money-tracker/`](smart-money-tracker/) | Track SEC 13F institutional holdings + congressional STOCK Act trades + House Clerk disclosures. Convergence analysis between whales, politicians, retail flows. |
| `daily-market-watch` | [`daily-market-watch/`](daily-market-watch/) | Global finance news report — 6 sections (Market Overview, Value, Momentum, Allocation, Options, Trends/Risks/Events), 12 region zoom-ins, Fed signals integration. |
| `thematic-stock-picker` | [`thematic-stock-picker/`](thematic-stock-picker/) | High-conviction 5-year thematic stock picker — 5 distinct policy-anchored themes × 5-8 screened small/mid-cap US/ADR names, with screening workings + sources + DD disclaimer. |

All three skills produce **source-cited Markdown reports** and follow a common contract: each has a `SKILL.md` workflow, a `references/` directory with curated source maps or screening criteria, and an `examples/` directory with a sample output for verification.

## Companion skills (cross-skill orchestration)

| From | To | Use case |
|------|----|----------|
| `smart-money-tracker` | `thematic-stock-picker` | When picking a theme, corroborate the basket against institutional positioning (13F) and congressional trades (STOCK Act). |
| `daily-market-watch` | `thematic-stock-picker` | When picking a theme, ground the macro/policy backdrop in the current market tape (Fed signals, rate path, sentiment). |
| `thematic-stock-picker` | `smart-money-tracker` | When the convergence report flags a ticker, add it to the watchlist and pull a deeper thematic context. |

See [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) for the full cross-skill playbook.

## Eval coverage

All three skills are evaluated against a 9-prompt test suite with a programmatic grader (`evals/run_evals.py`). Current state: **9/9 evals beat baseline, mean delta +43%**.

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

Run the grader: `make evals`. See [`evals/`](evals/) and [`evals/iterations/benchmark.md`](evals/iterations/benchmark.md).

## Install

This repo follows the [vercel-labs/skills](https://github.com/vercel-labs/skills) install pattern. The `skills` CLI works with **OpenCode, Claude Code, Codex, Cursor**, and [68 other agents](https://github.com/vercel-labs/skills#supported-agents).

### Install all skills from this repo

```bash
npx skills add kangcodex/finance-skills
```

### Install a single skill

```bash
# Specific skill
npx skills add kangcodex/finance-skills --skill thematic-stock-picker

# Direct subpath (works for any agent that resolves GitHub tree URLs)
npx skills add https://github.com/kangcodex/finance-skills/tree/main/thematic-stock-picker
```

### Install for a specific agent only

```bash
# Claude Code
npx skills add kangcodex/finance-skills -a claude-code

# OpenCode
npx skills add kangcodex/finance-skills -a opencode

# Codex
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

## Manual / local install

If you can't or don't want to use the `npx skills` CLI:

```bash
# Clone the repo
git clone https://github.com/kangcodex/finance-skills.git
cd finance-skills

# Copy the skill into your agent's skills directory
mkdir -p ~/.claude/skills
cp -r thematic-stock-picker ~/.claude/skills/thematic-stock-picker
```

## Development

This repo uses a Makefile for common tasks. See [`Makefile`](Makefile) for the full list.

```bash
make help       # list all targets
make evals      # run all 9 evals against the canonical examples
make verify     # evals + smoke-test the smart-money-tracker scripts
```

### Repo layout

```
finance-skills/
├── README.md
├── Makefile
├── LICENSE
├── smart-money-tracker/      # skill 1 (script-driven)
│   ├── SKILL.md
│   ├── scripts/               # 4 thin entrypoint wrappers
│   ├── src/smart_money_tracker/  # importable package
│   ├── references/            # (none — scripts embed the workflow)
│   ├── examples/              # canonical output structure
│   ├── data/, reports/        # runtime caches and outputs
│   └── tests/                 # skill-level tests
├── daily-market-watch/        # skill 2 (research-driven)
│   ├── SKILL.md
│   ├── references/regional-sources.md
│   ├── references/fed-signals.md
│   └── examples/              # sample-report.md, sample-lite.md
├── thematic-stock-picker/     # skill 3 (research-driven)
│   ├── SKILL.md
│   ├── references/screening-criteria.md
│   ├── references/sector-themes.md
│   └── examples/              # sample-report.md, sample-ai-infra.md
├── evals/                     # cross-skill eval infrastructure
│   ├── run_evals.py           # programmatic grader
│   └── iterations/            # per-iteration benchmark data
└── docs/                      # architecture decisions, design notes
    ├── CHANGELOG.md
    ├── ORCHESTRATION.md
    ├── decisions/             # ADRs
    └── api/                   # canonical source maps
```

## Documentation

- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — version history of the repo
- [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) — how the three skills work together
- [`docs/decisions/`](docs/decisions/) — architectural decision records (ADRs)
- [`docs/api/`](docs/api/) — canonical source maps (Fed/CME/EDGAR/regional news)
- [`smart-money-tracker/AGENTS.md`](smart-money-tracker/AGENTS.md) — skill testing framework

## Disclaimer

This software is for informational and educational purposes only. It does not constitute financial advice. Always do your own due diligence before making investment decisions. Past performance is not indicative of future results.

## License

MIT — see [`LICENSE`](LICENSE).
