# ADR-005: Default to Polygon Amoy testnet; mainnet is flag-gated

## Status
Accepted

## Date
2026-07-28

## Context
Polymarket runs on Polygon. Polygon has mainnet (real USDC, real money) and Amoy (testnet, no value, real flow). An agent that trades autonomously and has access to a real private key can drain a wallet in minutes through bad logic, bad data, or a bug. The moonsat writeup describes going from $100 to $5,000 — that trajectory has the inverse risk.

The question is: do we ship the agent pointing at mainnet by default and rely on the user to test first, or default to a no-value environment?

## Decision
- **Default = Amoy testnet.** `RUNTIME_CHAIN=amoy` is the env-var default.
- **Mainnet requires an explicit flag** (`RUNTIME_CHAIN=polygon` AND `RUNTIME_ALLOW_MAINNET=1`). If only the first is set, the runtime aborts with a clear error: "mainnet requires RUNTIME_ALLOW_MAINNET=1; refusing to start."
- **USDC source on mainnet must be from a wallet that has been pre-funded by the user**; the agent does not move USDC from a CEX.
- **Skill descriptions must call out the chain explicitly.** "polymarket-wallet-setup" sets up on the chain in `RUNTIME_CHAIN`; "trade-execute" refuses to submit if mainnet is active and `RUNTIME_ALLOW_MAINNET != 1`.

## Consequences
Positive:
- First-run experience is safe. New users can run the full pipeline end-to-end on Amoy with no value at risk.
- The two-flag gate (chain + allow) makes "I forgot this was real money" mistakes nearly impossible.
- Amoy has the same CLOB contract addresses, same API surface, same SDK. No code branches.

Negative:
- Users who want to go live have to read the docs and set two env vars. Friction by design.
- Some market data (volume, liquidity) on Amoy is fake or sparse; signal-gen must not optimize against Amoy-thin books.

## Alternatives considered
- **Mainnet by default.** Rejected. The cost of an accidental live order is the user's money.
- **Amoy only forever.** Rejected. The user explicitly wants to trade real money eventually.
- **Single flag, no second gate.** Rejected. One env var is too easy to set by accident when copying `.env` examples.

## See also
- ADR-006: wallet custody model (mainnet key handling)
- `docs/design/weather-trading-system.md` (chain configuration)
