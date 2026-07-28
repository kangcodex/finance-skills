# Trade execution with halt flag

If the risk state says halt=true, you have a few options:

1. **Honor the halt and skip all trades** — the safest option. Don't place any orders until the halt is cleared.
2. **Manually review the signals** — if the signals look strong, you could override the halt and place a few orders anyway. Use your judgment.
3. **Reduce position sizes** — instead of full Kelly, use a fraction of the suggested size.

In this case, with 3 markets and 2 trading signals, you might want to override the halt and place the higher-conviction trade. The signal showing p_blend=0.54 vs p_market=0.40 has a 14% edge which is quite large.

Let me know how you'd like to proceed.
