# Benchmark — iteration-2

| Skill | Eval | with_skill | without_skill | delta |
| --- | --- | --- | --- | --- |
| polymarket-wallet-setup | set-me-up-on-amoy | 4/4 | 2/4 | +50% |
| polymarket-wallet-setup | mainnet-upgrade-with-cold-wallet | 4/4 | 0/4 | +100% |
| polymarket-wallet-setup | check-status-and-rotate-session | 4/4 | 2/4 | +50% |
| weather-data-fetch | fetch-forecasts-for-3-markets | 4/4 | 1/4 | +75% |
| weather-data-fetch | single-market-one-source-down | 4/4 | 2/4 | +50% |
| weather-data-fetch | all-sources-failed-mark-and-skip | 4/4 | 0/4 | +100% |
| signal-gen | compute-signals-from-forecasts | 4/4 | 0/4 | +100% |
| signal-gen | edge-too-small-no-trade | 4/4 | 2/4 | +50% |
| signal-gen | within-last-hour-skip | 4/4 | 1/4 | +75% |
| risk-manage | decide-halt-on-daily-drawdown | 4/4 | 1/4 | +75% |
| risk-manage | halt-on-consecutive-tx-failures | 4/4 | 1/4 | +75% |
| risk-manage | human-pause-action | 4/4 | 0/4 | +100% |
| trade-execute | execute-skip-when-halt-true | 4/4 | 2/4 | +50% |
| trade-execute | slippage-exceeds-tolerance | 4/4 | 3/4 | +25% |
| trade-execute | idempotent-rerun | 4/4 | 1/4 | +75% |
