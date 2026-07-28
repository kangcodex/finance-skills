# Polymarket wallet setup — Polygon Amoy

## Step 1. Environment
Set the env vars. Amoy is the testnet default, no mainnet flag needed.

```bash
export RUNTIME_CHAIN=amoy
export RUNTIME_BANKROLL_USDC=100
# leave RUNTIME_ALLOW_MAINNET unset — mainnet is gated
```

## Step 2. Run the wallet setup
Invoke the polymarket-wallet-setup skill. The skill will:
1. Call `wallet.generate_keypair()` to create a new EOA on Amoy.
2. Call `wallet.save_key()` to write the keypair to `runtime/secrets/wallet.amoy.json` with `chmod 600`.
3. Call `wallet.poll_usdc_balance()` until the faucet transfer is seen (>0 USDC).
4. Call `wallet.derive_and_save_clob_creds()` to derive L2 API creds, persisted to `runtime/secrets/clob.amoy.json` with `chmod 600`.
5. Call `wallet.run_test_order()` to place then cancel a tiny order — proves the full CLOB path works.

## Step 3. Verify
The skill returns a `status_snapshot` showing chain=amoy, address, balance, and auth=true. Total elapsed: under 2 minutes.

## What's next
Tick skills (weather-data-fetch → signal-gen → risk-manage → trade-execute) can now be wired up to a cron.
