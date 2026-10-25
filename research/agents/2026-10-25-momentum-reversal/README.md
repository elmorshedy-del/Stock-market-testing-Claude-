# Momentum and mean reversion, split by regime, trend and stock phase

* **Owner, 2026-10-25:** "But momentum reversion being a main quant strategy why we didn't derive anything useful from it. That mathematician founded his whole fund based upon it. Can u research it deeply and try some tests on it. And test per regimes and stock phases and trends, don't lump data analysis together."
* **Builds on:**
  * [sp-multivariate](../2026-10-15-sp-multivariate/): momentum/RSI was the one family that predicted S&P 10% corrections (AUC 0.68);
  * [technical-indicators](../2026-10-16-technical-indicators/): mostly null;
  * [forced-flow](../2026-10-24-forced-flow/): reversal of forced moves;
  * [intraday-hours](../2026-10-25-intraday-hours/): the "open personality" persists.

## Part 1: what is known (research map)
| Horizon | Effect | Evidence | Where it works and where it fails |
|---|---|---|---|
| Intraday | **Same-hour persistence:** a stock's return in a given half-hour repeats at the same time on later days | Heston, Korajczyk & Sadka (2010, *JF*) | Driven by recurring flows, such as trading at fixed times |
| 1 day to 1 week | **Short-term reversal:** last week's losers beat last week's winners | Lehmann (1990, *QJE*); Jegadeesh (1990, *JF*); Lo & MacKinlay (1990, *RFS*) | It is a **liquidity-provision** premium, so it is **largest when volatility is high and liquidity scarce** (Nagel 2012, *RFS*, "Evaporating liquidity"). It dies after costs in calm, liquid markets |
| 1 month | 1-month reversal | Jegadeesh (1990) | As above |
| 3–12 months | **Cross-sectional momentum:** past winners beat past losers | Jegadeesh & Titman (1993, *JF*); Carhart (1997); near-52-week-high stocks keep winning: George & Hwang (2004, *JF*) | **Crashes** in "panic" states: after bear markets, when volatility is high and the market rebounds, losers rip (Daniel & Moskowitz 2016, *JFE*). Scaling by volatility helps (Barroso & Santa-Clara 2015, *JFE*) |
| 1–12 months, own past | **Time-series momentum (trend-following):** an asset's own past-year return predicts its next month | Moskowitz, Ooi & Pedersen (2012, *JFE*); Hurst, Ooi & Pedersen (2017, a century of trend-following) | Works best in long trends and as "crisis alpha" in drawn-out bear markets. Whipsaws in choppy, range-bound markets |
| Multi-year | Long-term reversal | De Bondt & Thaler (1985, *JF*) | Weak in modern large caps |

**Renaissance / Jim Simons:**
* Public accounts (Zuckerman 2019, *The Man Who Solved the Market*) describe many weak, short-horizon price signals: reversion over hours to days, plus some trend. They are combined across thousands of instruments, run with very low trading costs, high turnover and leverage.
* The edge comes from **breadth of signals and execution**, not from one big pattern. Their exact methods are not public.
* A daily-bar test on 81 large caps can find **whether the raw effects exist and in which regimes**. It cannot reproduce Medallion.

## Part 2: tests (pre-registered here, before any computation)
**Data:**
* ^GSPC daily since 1928.
* 41 large caps (daily, from listing, back to 1970 for many).
* 40 more large caps from 2019, making 81.
* Yahoo hourly bars for 51 tickers (2023-11 to 2026-10).
* All are today's large caps, so the sample is **survivorship-biased**. That biases cross-sectional momentum down (dead losers are missing) and reversal up. It is noted wherever relevant.

**Regimes**, all known at the time of the signal:

| Regime | Definition |
|---|---|
| Market trend | S&P above or below its 200-day average (10-month average for monthly tests) |
| Market state | **bull** if the S&P's 24-month return > 0, otherwise **bear** (Daniel–Moskowitz) |
| Rebound | bear state **and** the S&P up over the signal month: the momentum-crash condition |
| Volatility | S&P 63-day realized volatility as a percentile of its trailing 10 years, in thirds (low / mid / high) |
| Era | 1928–49, 1950–79, 1980–99, 2000–22, and **the channel 2022-10 to 2026** |
| Stock phase (per stock, daily) | **uptrend** = close > 50-day > 200-day; **downtrend** = close < 50-day < 200-day; **mixed** = otherwise. Separately: **near high** (≥ 95% of its 252-day high) vs **far** (< 80%) |

**Tests**, each with a **primary** statistic (Holm-corrected across the five) and **regime cells** (reported with denominators and block-bootstrap 90% intervals):

| Test | Design | Primary prediction | Regime contrasts (each with a predicted sign) |
|---|---|---|---|
| **M1 Time-series momentum, S&P 1928–2026, monthly** | sign of the past 12-month return; next month's return when long minus when short. Secondary: 1- and 3-month lookbacks | > 0 | the edge is larger in **high volatility** and in **bear states** (crisis alpha) |
| **M2 Cross-sectional momentum, large caps 1990–2026, monthly** | rank by the return from t−12 to t−1 months; next-month return of the top third minus the bottom third, equal weight | > 0 | lower in **bear states**; **negative in rebound months** (crash) |
| **M3 Short-term reversal, large caps 1990–2026, weekly** | rank by the past 5-day return; next-5-day return of the bottom third minus the top third. Gross, and net of 10 bp per leg per week | gross > 0 | **larger in high volatility** (Nagel); larger below the 200-day |
| **M4 Own-stock autocorrelation by phase, large caps 1990–2026, daily** | slope of the next-5-day z-return on the past-5-day z-return, pooled within stock (z = return ÷ trailing 20-day volatility) | < 0 (weekly reversal) | **weaker reversal / more continuation in uptrends and near highs** (George–Hwang) than in downtrends and far from highs |
| **M5 Same-hour persistence, 51 tickers, hourly, 2023-11 to 2026-10** | each day and hour slot (7 slots), rank stocks by their mean return in that slot over the previous 20 days; today's slot return of the top third minus the bottom third | > 0 | by slot (first hour, midday, last half hour); by volatility third |

**Null:** block bootstrap (12-month blocks for monthly tests, 20-day blocks for daily and weekly), 4,000 draws. Primary p-values are one-sided in the predicted direction.

**Pass:** a primary passes if Holm-adjusted p < 0.05. A regime contrast is "supported" if it has the predicted sign with bootstrap p < 0.05. All cells are reported regardless.

**Today:** the current regime on each axis, and which effects are "on" or "off" under it.
