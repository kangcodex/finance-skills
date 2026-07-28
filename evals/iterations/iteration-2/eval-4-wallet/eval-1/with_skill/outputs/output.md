# Mainnet upgrade from Amoy

## Pre-flight
Mainnet is gated. The skill will refuse to proceed until ALL of the following are set:

```bash
export RUNTIME_CHAIN=polygon
export RUNTIME_ALLOW_MAINNET=1
export RUNTIME_COLD_WALLET_ADDRESS=0xAbC...123
export RUNTIME_SESSION_MAX_SPEND=50
export RUNTIME_BANKROLL_USDC=50
```

## What happens next
1. The skill calls `wallet.build_session_payload(chain='polygon', max_spend_usdc=50, valid_for_days=7, cold_signature=...)` — **the cold signature is required** for any mainnet session payload. Without it, the skill raises `ColdSignatureRequired` and aborts.
2. The signed session payload is sent to the CLOB; the CLOB derives the L2 session key, scoped to the cold wallet, capped at the requested spend.
3. `valid_until = now + 7 days`.
4. The wallet setup is identical to Amoy from here (save_key, derive_and_save_clob_creds, run_test_order) but the resulting secrets are tagged `wallet.polygon.json` and `clob.polygon.json` (chmod 600).

## Auto-renewal
- **Expiry trigger**: if `valid_until - now < 24h`, the skill flags the session for re-mint. The user re-signs a new session payload from the cold wallet.
- **Spend trigger**: if `session_remaining_spend < 10%` of `RUNTIME_SESSION_MAX_SPEND`, the skill flags for re-mint.
- Either trigger causes a halt + heartbeat push; the user must re-sign to resume.

## What is NOT done
- The session key cannot exceed `RUNTIME_SESSION_MAX_SPEND` (default $50).
- The session key cannot live past 7 days without re-signing.
- The agent cannot self-renew — only a cold-wallet signature counts.
