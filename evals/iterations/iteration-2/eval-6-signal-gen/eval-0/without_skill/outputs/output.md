# Computing trading signals

To compute a trading signal from forecasts, you would:

1. Read the forecast data (which gives you a probability of the event happening).
2. Compare it to the market's implied probability.
3. If the forecast probability is much higher than the market probability, that's an "edge" — the market is underpricing the event.
4. If the edge is large enough (typically >5%), it's worth taking a position.
5. The position size depends on your bankroll and how confident you are. Kelly criterion is the standard formula: f* = (bp - q) / b, where b is the payoff odds, p is your probability, q = 1-p.

The output should include the blended probability, the edge, the suggested position size, and a buy/sell decision.
