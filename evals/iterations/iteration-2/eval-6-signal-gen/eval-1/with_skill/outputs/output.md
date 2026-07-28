# Small edge — no trade

## Inputs
- p_market = 0.50
- sources: noaa=0.52, openmeteo=0.52, paid=0.52
- w_market = 0.3
- best_ask = 0.51

## Math
```
p_blend = w_market * p_market + (1 - w_market) * mean(sources)
        = 0.3 * 0.50 + 0.7 * 0.52
        = 0.15 + 0.364
        = 0.514

edge = p_blend - p_market = 0.014

f_size_raw = 0.25 * kelly(0.514, b = (1 - 0.51) / 0.51 = 0.96)
           = 0.25 * (0.514 * 0.96 - 0.486) / 0.96
           = 0.25 * 0.001
           ≈ 0.0004
```

The edge (0.014) is below the 0.05 threshold. `trade = false`.

## Output (signals.json)
```json
{
  "signals": [
    {
      "market_id": "...",
      "p_blend": 0.514,
      "edge": 0.014,
      "f_size_raw": 0.0004,
      "trade": false,
      "reason": "edge below threshold (0.014 < 0.05)"
    }
  ]
}
```

## Note on source agreement
The three sources all agree on 0.52, which is a tight cluster. The skill also checks for the "all sources returned identical p" reason path — that would be `reason = "all sources returned identical p (no signal)"`. In this case, the blend still produces a tiny positive edge, so the reason is the threshold one. (If the sources had been identical at p=0.50, the edge would be exactly 0 and that other reason would fire.)
