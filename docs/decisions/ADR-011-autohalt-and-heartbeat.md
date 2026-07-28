# ADR-011: Auto-halt on objective breaches + heartbeat to human; no silent operation

## Status
Accepted

## Date
2026-07-28

## Context
The agent trades real money. Three classes of failure:
1. **Hard breach**: daily drawdown exceeded, key-compromise signal, API storm, session key expired, all sources return errors for >1h.
2. **Soft anomaly**: unusual PnL pattern, single-source divergence, repeated rejected orders.
3. **Normal operation**: no breach, no anomaly.

The question is: which conditions auto-halt, which escalate to the human, and which pass silently?

## Decision

| Condition | Action | Reason |
|-----------|--------|--------|
| **Hard breach** (any of: daily loss >10% of bankroll; session key expired/revoked; >3 consecutive failed tx; all data sources failed for >1h) | **Auto-halt.** `risk-manage` sets `halt=true` in `runtime/state/risk.json`. `trade-execute` refuses to submit any order while `halt=true`. Push notification to user. | These are unambiguous. Don't ask, act. |
| **Soft anomaly** (any of: per-source forecast divergence >2σ; single market fill ratio <30% over 5 attempts; Brier score of best source worsened >20% week-over-week) | **Heartbeat to human.** Push notification: "Anomaly X detected. Continuing to trade. Ack or I pause next tick." If no ack within 1h, auto-pause. | Anomalies need human judgment, but the agent shouldn't keep trading silently. |
| **Normal operation** | **Heartbeat to human every 4h with summary.** "Bankroll $X, exposure Y%, N positions, PnL today +/-$Z." | The user is always in the loop, even when nothing is wrong. |

**Heartbeat channel**: configurable. Default = a local log file + a webhook (Discord/Telegram/Slack). The skill does not implement the channel; the runtime daemon does.

**Halt-clear**: only the human clears `halt=true` (via the `risk-manage` skill with an explicit "resume" action). The agent cannot clear its own halt.

## Consequences
Positive:
- Hard breaches cannot drain the account. They are objective and unambiguous.
- The human is never surprised. Heartbeat on every state, not just on failure.
- Anomaly escalation has a bounded response time (1h) — the agent does not stall indefinitely waiting for a human who is asleep.
- Auto-clear of halt is impossible. The user is always in control of re-entry.

Negative:
- The 1h ack window means the user can wake up to a paused agent. Better than waking up to an empty wallet.
- The heartbeat is a dependency (the webhook must work). If the webhook is down, the runtime falls back to a loud log line + a local SQLite alert table that the user checks on next login.
- More moving parts than "just halt everything" — but that would block trading on minor blips.

## Alternatives considered
- **Manual halt only.** Rejected. The user is asleep / on a plane / on a date. The agent must defend itself.
- **Auto-halt on everything including soft anomalies.** Rejected. Stops trading during routine forecast volatility.
- **No heartbeat, silent operation.** Rejected. The user must be able to know what the agent did without asking.

## See also
- ADR-006: session key revocation path
- ADR-008: daily drawdown cap (one of the hard breach inputs)
- `docs/design/risk-framework.md` (full halt matrix)
