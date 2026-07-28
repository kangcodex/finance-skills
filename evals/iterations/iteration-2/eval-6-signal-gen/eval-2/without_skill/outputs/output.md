# Don't trade too close to resolution

If the market resolves in 30 minutes, you should probably not open a new position. Here's why:

1. **Thin order book** — there aren't many counterparties left.
2. **Adverse selection** — the people still trading have information you don't.
3. **Kelly is unreliable** — the formula assumes a stable edge, which doesn't exist in the last hour.

A 12% edge looks attractive, but it might be a phantom. The conservative move is to skip this one and wait for the next market.

In the signals.json you'd record: `{ "trade": false, "reason": "too close to resolution" }`.
