# When the price has moved

If the market has moved against you (slippage), you have a few choices:

1. **Accept the slippage and place the order anyway** — you're paying more than expected but still getting a position.
2. **Wait for the price to come back** — markets are mean-reverting in the short term.
3. **Cancel the trade** — sometimes the right answer is no trade.

In this case, a 4% slippage on a 0.50 reference is significant. I'd probably wait for the price to come back. If you really want the position, you could place a limit order at 0.51 instead of 0.52.

The orders.json would record: `{ "status": "skipped", "reason": "slippage too high" }`.
