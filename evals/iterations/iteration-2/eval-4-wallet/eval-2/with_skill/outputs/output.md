# Wallet status + session rotation

## Current status
The skill calls `weather_runtime.wallet.status_snapshot(state)`:

```json
{
  "chain": "amoy",
  "address": "0x9F8a0c1d...b2E3",
  "balance_usdc": 47.50,
  "auth": true,
  "session": {
    "valid_until": "2026-08-04T12:00:00Z",
    "remaining_spend_usdc": 8.20,
    "max_spend_usdc": 50
  }
}
```

(For Amoy, the `session` block is omitted — session keys are a mainnet-only concept.)

## When does the session need re-minting?
`weather_runtime.wallet.session_needs_renewal(valid_until, remaining_spend, max_spend)` returns true if EITHER:

- **Expiry trigger**: `valid_until - now < 24h`
- **Spend trigger**: `remaining_spend / max_spend < 0.10` (i.e. <10% of the budget remains)

In the example above, the spend trigger fires (`8.20 / 50 = 16.4%` is still above 10%, so it's the expiry one that would fire if it were within 24h — but here it isn't, so neither fires yet).

## Re-mint flow
1. The user (human) signs a new session payload from the cold wallet.
2. The skill calls `build_session_payload(chain='polygon', max_spend_usdc=50, valid_for_days=7, cold_signature=...)` and submits it to the CLOB.
3. The old session is revoked; the new one is active immediately.
4. `session_valid_until` is updated in `risk.json`; the heartbeat is pushed.

The cold-wallet signature is non-negotiable — there is no programmatic way to extend a session.
