# When all weather sources fail

If all three forecast sources are returning errors, you have a bigger problem. This is rare but it does happen.

Steps to take:
1. Check your internet connection.
2. Check the status pages of each service (NOAA, Open-Meteo, your paid source).
3. If the paid source is the only one failing, it might be a billing issue — check your account.
4. Wait a few minutes and try again.

In the meantime, the agent should mark the market as "unknown" and skip trading it. The signal generation will be skipped too because there's no forecast data to work with.

Most weather APIs are reliable, so this should be a temporary issue. If it persists for more than an hour, you should probably halt the agent and investigate.
