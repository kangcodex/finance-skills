# finance-skills

A collection of agent skills for financial markets analysis, portfolio construction, smart-money tracking, Singapore-licensed financial advisory, and deterministic news monitoring. Each skill bundles a workflow, a curated source map, and reference docs so the agent (Claude Code, Codex, OpenCode, Cursor, etc.) can answer finance questions without making things up.

## Skill families

| Family | What it does | Skills |
|--------|--------------|--------|
| **Research** | One-shot analysis and monitoring skills. The user asks a question, the agent produces a cited Markdown report or deterministic feed output. | `smart-money-tracker`, `daily-market-watch`, `thematic-stock-picker`, `sg-financial-advisor`, `news-rss-watch` |

All skills share the same flat-skill convention (`SKILL.md` + `references/` + `examples/`) and are independently installable.

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

All five research skills define their workflow in `SKILL.md`; source maps, examples, and deterministic scripts live with the skills that need them.

| Skill | Folder | What it does |
|-------|--------|--------------|
| `smart-money-tracker` | [`skills/smart-money-tracker/`](skills/smart-money-tracker/) | SEC 13F + STOCK Act + House Clerk convergence tracker with source verification and cached data fallbacks. |
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

See [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) for the full cross-skill playbook.

## Eval coverage

The iteration-1 eval set covers all five research skills (15 evals) and is evaluated by `evals/run_evals.py`.

**Research skills:** 15/15 evals beat baseline, mean delta +62% (91.9% with-skill pass rate).

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

Run the grader with `make evals`. See [`evals/`](evals/) and `evals/iterations/iteration-1/`.

## Development

```bash
make help              # list all targets
make evals             # run all 15 research evals
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
│   └── news-rss-watch/                # research skill 5 (deterministic feed watcher)
├── evals/                             # cross-skill eval infrastructure
└── docs/                              # architecture decisions
    ├── CHANGELOG.md
    ├── ORCHESTRATION.md
    └── decisions/                     # ADRs for the research skills
```

## Documentation

- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — version history
- [`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) — how all 5 skills work together
- [`docs/decisions/`](docs/decisions/) — architectural decision records
- [`skills/smart-money-tracker/AGENTS.md`](skills/smart-money-tracker/AGENTS.md) — skill testing framework

## Disclaimer

This software is for informational and educational purposes only. It does not constitute financial advice. Always do your own due diligence before making investment decisions. Past performance is not indicative of future results.

## License

MIT — see [`LICENSE`](LICENSE).
