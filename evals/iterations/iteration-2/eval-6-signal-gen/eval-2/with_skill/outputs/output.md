# Within the T-1h buffer → no new positions

## Inputs
- now = 2026-07-28T12:30:00Z
- resolution_at = 2026-07-28T13:00:00Z
- resolution_at - now = 30 minutes (< 1 hour)
- p_market = 0.40, p_blend = 0.52
- edge = 0.12
- f_size_raw = 0.07

## Logic
The check is at the top of `compute_signal()`:
```python
if now >= resolution_at - timedelta(hours=1):
    return Signal(trade=False, reason="within last hour, no new positions")
```

This is the FIRST check (before edge, before Kelly, before any other reason). The 1h buffer exists to prevent last-minute price-discovery trades that are more likely to be adversely selected against.

## Output (signals.json)
```json
{
  "signals": [
    {
      "market_id": "...",
      "p_blend": 0.52,
      "edge": 0.12,
      "f_size_raw": 0.07,
      "trade": false,
      "reason": "within last hour, no new positions"
    }
  ]
}
```

## Why this exists
In the last hour of a market, the order book thins out, the price becomes extremely sensitive to small trades, and the Kelly edge is most likely to be a phantom (the market-maker knows more than we do about the resolution). The skill refuses to take new positions in this window; existing positions still flow through `risk-manage` for monitoring.
