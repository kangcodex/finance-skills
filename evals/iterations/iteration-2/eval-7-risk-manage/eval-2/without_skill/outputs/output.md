# Pausing the trading agent

To pause the agent, you can:

1. Set the environment variable `RUNTIME_HALT=1` and restart.
2. Use the agent's "pause" command if it has one.
3. Manually revoke the session key from the Polymarket UI.

When the agent is paused, it should:
- Stop placing new orders.
- Keep monitoring the market.
- Send a notification that it's been paused.

To resume, unset the environment variable (or use the agent's "resume" command) and restart the trading loop.

Most agents also let you close all positions as part of the pause command.
