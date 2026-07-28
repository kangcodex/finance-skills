# When the edge is too small

If the edge is small (e.g. 0.014), you generally shouldn't trade. The minimum edge I use is 5% — anything below that and the transaction costs + Kelly fraction will eat into your returns.

In this case:
- Market says 50% chance of rain.
- Forecasts say 52% chance.
- That's a 2% edge, which is too small.

You'd want to either:
1. Wait for the edge to grow as the event approaches.
2. Look for other markets with bigger edges.
3. Use a smaller bankroll on this market if you really want to trade.

Signals.json would record: `{ "trade": false, "reason": "edge too small" }`.
