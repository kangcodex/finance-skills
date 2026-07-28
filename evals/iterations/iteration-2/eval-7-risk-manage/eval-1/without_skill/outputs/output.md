# When transactions are failing

If 3 orders in a row are failing, there's clearly a problem. Common causes:

1. **Insufficient gas** — top up your wallet with MATIC.
2. **Stale session key** — rotate the session key.
3. **CLOB outage** — wait and retry.

You should:
1. Pause trading immediately.
2. Investigate the error logs.
3. Fix the underlying issue.
4. Manually place a test order to confirm the system works.
5. Resume trading.

The risk system should automatically pause on consecutive failures, but you should also manually pause to be safe.
