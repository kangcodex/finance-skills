# Restarting after a crash

If the trade-execute step crashes mid-run, the easiest fix is:

1. Check the orders.json to see which orders actually went through.
2. Identify which signals haven't been processed yet.
3. Re-run trade-execute on the remaining signals only.

To prevent double-placing, you can:
- Add a unique ID to each order and check it before placing.
- Use a database transaction.
- Wrap the order placement in a try/except and only mark the order as "placed" after the CLOB confirms.

Most production systems use idempotency keys — a unique string per order attempt that the CLOB uses to dedupe requests. If the CLOB sees the same idempotency key twice, it returns the original order without placing a new one.
