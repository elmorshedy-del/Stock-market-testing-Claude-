# Data sources

Coverage below is what was actually pulled and checked, not what the vendor advertises.

**Keys:** set them as environment variables (e.g. `THETADATA_API_KEY`) for the session. Never put them in a file, a commit or a script.

| Source | What we use | Coverage we have | Cost and limits | Fetched by |
|---|---|---|---|---|
| **ThetaData**, Value tier | End-of-day option quotes and open interest per contract; same-day OI | 2020-01 → today, TSLA MSFT SPY QQQ NVDA MU (MU not refreshed after Oct 9 2026) | $40/month. 2 concurrent requests. Same-day OI only one expiration at a time. Free tier: about 1 year of quotes and no OI (not enough). | `engines/gamma/td_pull.py`, `live_check.py` |
| **SqueezeMetrics** | Published S&P dealer gamma (GEX) and dark-pool index (DIX), daily | 2011-05 → today | Free CSV | `research/microstructure/fetch.py --index` |
| **FINRA** Reg SHO daily short-volume files | Per-stock dark-pool buying proxy: short volume ÷ off-exchange volume, 5-day mean | 2018-08 → today (one file per day) | Free | `research/microstructure/finra_dpi.py fetch` |
| **Yahoo Finance** (unofficial) | Daily bars; live option chains with today's volume | ^GSPC 1970+, SPY 1993+, TSLA 2010+, about 45 tickers; chains are a live snapshot only | Free. Option chains need a cookie and crumb. No OI history. Can change without notice. | `research/microstructure/fetch.py` |
| **Alpha Vantage** | Tried for live quotes and single-stock gamma | Not usable | Rate-limited; real-time and options endpoints not on our key | none |
| **Databento** | OPRA trades with quotes, one day (2025-03-28), used to calibrate trade signing | One day | Free credit used. Per-contract OI quoted at $140–445 per ticker for 2023–26 (not bought). | one-off |
| **Cboe Open-Close** sample | Signed volume by contract, one day | 2025-03-28 | Free sample | one-off |
| **DoltHub** options database | Free option chains around TSLA earnings | 18 reports, 2021–2025 | Free | `research/microstructure/earnings_implied.py` |
| **HistoricalData.net** sample | End-of-day chains with OI and IV, TSLA/SPY/SPX | Jul–Dec 2022 | Free sample, licensed: not committed | one-off (validated the GEX method: 0.96 vs SqueezeMetrics) |

**Local layout:** each study keeps its downloads in its own `data/`, which is gitignored. Raw ThetaData chains for six tickers from 2020 take about 860 MB.
