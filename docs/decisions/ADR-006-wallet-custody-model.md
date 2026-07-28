# ADR-006: Amoy = test key; mainnet = session key with per-tx caps

## Status
Accepted

## Date
2026-07-28

## Context
The agent must sign Polymarket orders. That requires a Polygon private key. The question is: where does that key live, and what can it do?

Three models:
1. **Self-custody long-lived key**: agent owns the key, signs everything, no limits. Maximum autonomy, maximum blast radius.
2. **Delegated session key**: main wallet owner issues a session key with a spending cap and a TTL; the agent uses only the session key.
3. **Custodial relayer / builder**: agent calls a hosted service (e.g. Polymarket builder relayer) that holds the key and signs on behalf. Agent never touches the key.

## Decision
- **Amoy (testnet):** self-custody of a generated test key is acceptable. The setup skill creates a fresh key, saves it to `runtime/secrets/wallet.amoy.json` with `chmod 600`. This is throwaway.
- **Mainnet:** **session key only.** The user runs `polymarket-wallet-setup` on mainnet which:
  1. Imports the user's main wallet as a cold signer (read-only at runtime, never loaded into the agent process).
  2. Mints a **session key** with: `validUntil` (e.g. 7 days), `maxSpendUSDC` (e.g. $50), and `allowedContracts` (only the Polymarket CTF Exchange + Conditional Tokens contracts).
  3. Writes the session key to `runtime/secrets/wallet.polygon.json`. The cold key never touches disk in the runtime directory.
- **Auto-rotation:** the setup skill re-mints the session key when `validUntil < 24h` OR after a configurable spend threshold. The agent cannot extend its own session.
- **Revocation:** the user can revoke the session key from their main wallet at any time; the agent's next signing attempt will fail.

## Consequences
Positive:
- Even if the agent is fully compromised (prompt injection, malicious data), the session key caps the damage at `maxSpendUSDC` per window.
- The cold key is never loaded into the runtime; it only exists in the user's wallet (hardware or browser extension).
- Revocation is one transaction away.

Negative:
- The user has to perform the one-time delegation transaction themselves. Friction by design.
- Session key flow requires EIP-7715 or a Polymarket-specific delegation. If neither is available, fall back to a plain hot key with hard caps in the runtime (degraded mode, clearly flagged).

## Alternatives considered
- **Hot key on mainnet.** Rejected. One bug, one prompt injection, one typo, full wallet.
- **Builder relayer only.** Rejected. Adds counterparty risk; not all markets are available through the relayer; user wanted local control.
- **HSM / Vault.** Rejected for v1. Out of scope; the user is an individual trader, not a fund.

## See also
- ADR-005: chain gating
- ADR-009: kill switch
- `docs/design/risk-framework.md` (spend caps as risk control)
