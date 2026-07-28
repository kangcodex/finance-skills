# ADR-003: Polymarket weather-trading uses a 5-skill family on a thin Python runtime

## Status
Accepted

## Date
2026-07-28

## Context
The user wants an agent that trades on Polymarket using weather forecasts as edge. The naive shape is one mega-skill: "be a weather trader." That fails because the workflow has distinct cadences (one-time setup vs hourly tick vs per-tick risk check) and distinct failure domains (wallet key handling vs market data vs signal math vs order routing). Skills that mix cadences produce context-bloat and one-skill-blocks-all bugs.

References:
- `https://github.com/aliaihub/awesome-hermes-usecases/blob/main/usecases/weather-trading-polymarket.md`
- `https://github.com/alteregoeth-ai/weatherbot`
- `https://moonsat.medium.com/hermes-agent-polymarket-how-i-built-self-learning-weather-trading-bot-100-5-000-guide-233fd4a008f2`

## Decision
Adopt a **5-skill family** on a **thin Python runtime**:

| Skill | Cadence | Purpose |
|-------|---------|---------|
| `polymarket-wallet-setup` | One-time | Generate/import wallet, derive Polymarket proxy, fund with USDC, verify CLOB auth. |
| `weather-data-fetch` | Per-tick | Pull forecast sources (NOAA, Open-Meteo, paid APIs) + market-implied probs. Normalize. |
| `signal-gen` | Per-tick | Compute blended probability per market, compare to market price, output edge + size. |
| `trade-execute` | Per-tick (conditional) | Place / amend / cancel orders on Polymarket CLOB. Pre-trade risk gate. |
| `risk-manage` | Per-tick + heartbeat | Track exposure, PnL, Brier, kill-switches, daily drawdown, per-market cap. |

**Runtime = Python scripts in `runtime/` that skills call.** Skills remain instructions; scripts do the deterministic I/O (RPC calls, signing, API fetches). The agent orchestrates which skill fires when.

## Consequences
Positive:
- Each skill stays under 500 lines, scoped to one concern.
- Test/eval per skill is clean (3 assertions each, 15 total).
- `risk-manage` can be invoked independently for portfolio introspection without firing trades.
- Failure in one skill does not cascade: if `weather-data-fetch` is down, `risk-manage` still produces state.

Negative:
- Orchestration logic lives in `ORCHESTRATION.md`, not in any one skill. Drift risk.
- 5 evals to maintain.
- Cross-skill contracts (positions table schema, market ID format) must be enforced.

## Alternatives considered
- **3 skills** (`setup`, `trade`, `risk`). Rejected: `trade` would still bundle data + signal + execution, making per-skill evals noisy.
- **7+ skills** (granular per stage). Rejected: orchestration overhead exceeds the gain. Wallet setup, position sizer, stop-loss, pnl-tracker etc. can be modules inside the 5 skills, not standalone skills.
- **No skills, just a single Python CLI.** Rejected: the user explicitly asked for skills so the agent can reason about *when* to invoke each piece. A CLI loses the trigger-ability.
- **Skills only, no runtime scripts.** Rejected: the agent cannot natively sign Polygon transactions or poll Polymarket CLOB. Some code must exist.

## See also
- ADR-004: skill taxonomy
- ADR-005: Polygon mainnet vs Amoy
- ADR-006: wallet custody model
- `docs/design/weather-trading-system.md`
- `docs/ORCHESTRATION.md`
