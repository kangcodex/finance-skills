# Canonical Data Sources — Fed / CME / SEC

This document is the canonical source map for the Fed, central-bank, and SEC data referenced by `daily-market-watch` and `thematic-stock-picker`. Each skill also embeds the relevant subset in its own `references/` directory; this top-level map is the source of truth for the repo.

## Federal Reserve

| Source | URL | Cadence | What you get |
|--------|-----|---------|--------------|
| Federal Reserve main | https://www.federalreserve.gov/ | Continuous | Statements, minutes, speeches, H.4.1, Z.1 |
| FOMC calendar | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | Scheduled | Meeting dates, statement release times |
| H.4.1 (factors) | https://www.federalreserve.gov/releases/h41/ | Weekly (Thu) | Fed balance sheet |
| Z.1 (Financial Accounts) | https://www.federalreserve.gov/releases/z1/ | Quarterly | Sectoral balance sheets |
| Selected interest rates | https://www.federalreserve.gov/releases/h15/ | Daily | SOFR, fed funds, T-bill yields |
| NY Fed rates | https://www.newyorkfed.org/markets/reference-rates/sofr | Daily | SOFR fixings |
| Atlanta Fed GDPNow | https://www.atlantafed.org/research/economicforecasting | Real-time | Nowcast |
| Beige Book | https://www.federalreserve.gov/monetarypolicy/beigebook202X.htm | 8x/year | Regional economic conditions |
| Fed speeches | https://www.federalreserve.gov/newsevents/speeches.htm | Daily | Calendar + transcripts |

## CME / Fed Funds / SOFR

| Source | URL | What you get |
|--------|-----|--------------|
| CME FedWatch | https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html | Implied probabilities of rate moves at upcoming FOMC meetings |
| CME SOFR futures | https://www.cmegroup.com/markets/interest-rates/stir/sofr.html | Implied SOFR for the next 3 months, 1Y, 2Y |
| CME Fed Funds futures (ZQ) | https://www.cmegroup.com/markets/interest-rates/stir/fed-funds.html | Implied effective fed funds for each contract month |
| CME economic calendar | https://www.cmegroup.com/tools-information/calendars/economic-calendar.html | All CME-tracked economic releases |
| Cboe VIX | https://www.cboe.com/tradable_products/vix/ | 30-day implied SPX vol |
| Cboe VVIX | https://www.cboe.com/us/indices/dashboard/vvix/ | Vol of VIX |
| Cboe SKEW | https://www.cboe.com/us/indices/dashboard/skew/ | Tail-risk pricing |

## SEC

| Source | URL | What you get |
|--------|-----|--------------|
| EDGAR full-text search | https://www.sec.gov/edgar/search/ | All filings (10-K, 10-Q, 8-K, DEF 14A, 13F, Form 4) |
| EDGAR 13F | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=13F | Institutional holdings (quarterly) |
| EDGAR Form 4 | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=4 | Insider transactions |
| EDGAR filings RSS | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=10-K&dateb=&owner=include&count=40 | New 10-K filings feed |
| EDGAR Reg-SHO | https://www.sec.gov/data/sho.html | Daily short interest |

## Treasury

| Source | URL | What you get |
|--------|-----|--------------|
| Treasury yield curve | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/ | Daily par yield curve |
| Treasury auctions | https://home.treasury.gov/policy-issues/financing-the-government/quarterly-refunding | Quarterly refunding, auction schedule |
| Treasury statements | https://home.treasury.gov/news/press-releases | Press releases |

## Other central banks (for region zoom)

| CB | URL |
|----|-----|
| ECB | https://www.ecb.europa.eu/ |
| BoE | https://www.bankofengland.co.uk/ |
| BoJ | https://www.boj.or.jp/en/ |
| PBoC | http://www.pbc.gov.cn/ |
| SNB | https://www.snb.ch/ |
| BoC | https://www.bankofcanada.ca/ |
| RBA | https://www.rba.gov.au/ |
| RBNZ | https://www.rbnz.govt.nz/ |
| RBI | https://www.rbi.org.in/ |
| MAS | https://www.mas.gov.sg/ |
| BoK | https://www.bok.or.kr/ |

## CFTC positioning

| Source | URL | Cadence |
|--------|-----|---------|
| COT report | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | Weekly (Fri, for prior Tue) |
| Bank participation report | https://www.cftc.gov/MarketReports/BankParticipationReport/index.htm | Weekly |
| Traders in financial futures | https://www.cftc.gov/MarketReports/CommitmentsofTraders/DealerIntermediaryActivity/index.htm | Weekly |

## BLS / BEA / economic data

| Source | URL | Coverage |
|--------|-----|----------|
| BLS | https://www.bls.gov/ | CPI, PPI, NFP, JOLTS, ECI, productivity |
| BEA | https://www.bea.gov/ | GDP, PCE, personal income/spending, trade balance |
| EIA | https://www.eia.gov/ | Energy (oil, gas, coal, electricity) |
| Census | https://www.census.gov/ | Retail sales, housing starts, new home sales |
| NAREIT | https://www.reit.com/data-research | REIT sector data |
| ISM | https://www.ismworld.org/ | Manufacturing / services PMI |

## See also

- `daily-market-watch/references/fed-signals.md` — how to interpret these sources
- `daily-market-watch/references/regional-sources.md` — region-specific sources (CN, JP, EU, etc.)
