# Idempotent re-run after a crash

## Scenario
1. trade-execute processes 3 signals, places 1, writes orders.json.
2. Mid-write, the orchestrator crashes. The atomic write is either fully-written or not-yet-written; there is no partial state.
3. The orchestrator restarts and the per-tick cron re-runs trade-execute on the same signals.json.

## What happens on re-run
The orchestrator (in `weather_runtime.orders.execute`) does this:

```python
# Load existing attempts
existing = read_state(orders_log_path) or {"attempts": []}
attempted_markets = {a["market_id"] for a in existing["attempts"]}

for signal in signals:
    if signal["market_id"] in attempted_markets:
        # Already processed this market in a previous run.
        # Re-write the same row (idempotent — no second CLOB call).
        continue
    # ... pre_trade_check + place_one ...
```

The `market_id` is the dedup key. Any market that already has an entry in `orders.json` is skipped on re-run — no second CLOB call, no double-place.

## Atomic write guarantees
`write_state_atomic` (in `weather_runtime.state_io`) does:
1. Write to `.{name}.tmp`.
2. `fsync` the tmp file.
3. `os.replace` the tmp to the real path (POSIX-atomic on the same filesystem).

So the crash mid-write cannot leave a half-written orders.json. The worst case is:
- The pre-replace write fails → tmp is cleaned up, orders.json is unchanged (old version).
- The post-replace succeeds → orders.json is the new version.

Either way, the file is consistent.

## What gets re-run
The pre-trade check IS re-run for the new market (if any). For an already-attempted market, no re-run — the existing row is the source of truth.

## Recovery
If you want to retry a market (e.g. it was skipped on a stale slippage check), you must either:
- Wait for the next tick with a fresh signal (signal-gen will re-emit `trade=true` if the edge is still there), OR
- Manually delete the row from orders.json (operator action; not exposed in any skill).
