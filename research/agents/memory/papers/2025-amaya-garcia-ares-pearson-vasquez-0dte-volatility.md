# Amaya, Garcia-Ares, Pearson & Vasquez (2025). 0DTE Index Options and Market Volatility: How Large is Their Impact? Working paper, 25 January 2025 (hosted by Cboe)
**Read:** the full main text (sections 1–6) and the appendix in outline; Tables 1–6 through the text, not cell by cell. 2026-11-16. A working paper, not peer reviewed; Cboe supplied the data and hosts the paper.
**Question it serves:** SIZE (how big). Mechanism tag: POS.

## Claim
* **With true market-maker positions, the S&P 500 dealer-gamma effect is real but small.** Market makers are usually long gamma, which lowers volatility slightly. When they are short, volatility is higher, by at most a few points.

## Data
* Every trade in SPX and SPXW options, Jan 2020–June 2023, with the capacity of buyer and seller (customer, market maker, professional customer, firm, broker-dealer): 442.6 million trade records, from Cboe.
* One-minute option quotes (Algoseek); the most active E-mini future for the index.
* Analysis window July 2020–June 2023 (36 months), to let positions opened before 2020 run off.

## Method
* **Position:** cumulate market-maker buys minus sells in each option series from its first trade. No sign assumption is needed.
* **Gamma:** Black–Scholes–Merton with the series' own implied volatility, every minute, summed over all series. In units of 10⁹.
* **Models, estimated month by month on one-minute returns:**
  1. a GARCH model with a daily level, an intraday pattern, and a term that lets variance depend on the last one to five minutes of market-maker gamma;
  2. a linear model of squared returns on lagged squared returns and lagged gamma, with date and time-of-day fixed effects.
* **Impact:** re-simulate returns with the gamma term switched off and compare realized volatility with and without it, per day and per 30 minutes.

## Results
* **Who trades:** 68.7% of volume is a customer against a market maker. Customers buy 0DTE options from market makers about as often as they sell them (15.0% against 14.1% of total volume). 0DTE is 34.8% of volume.
* **Market-maker gamma is usually positive:** the mean of daily means is 341 (s.d. 320). It is negative at some point on at least a quarter of days, and all day on about 1% of days.
* **After Tuesday and Thursday expiries began (May 2022):** mean 234, down from 409; gamma is negative at some point on more than half of days. Daily average gamma is rarely negative before 2022 and often negative from early 2022.
* **Sign of the relation:** variance falls with lagged gamma in every specification. The average likelihood-ratio statistic is about 9 (5% critical value 5.99, 1% 9.21), so the evidence is real but not overwhelming. One lag of gamma is enough.
* **Size, GARCH model, in points of annualized volatility:**

  | | Daily | 30-minute |
  |---|---|---|
  | Mean impact | −0.19 | −0.17 |
  | 90th percentile | positive | positive |
  | 99th percentile | not given | +2.0 |
  | Maximum | +3.3 | +6.4 |

* **For scale:** the day-to-day change in realized volatility has a standard deviation of 4.5 points and exceeds 3 points on about 20% of days. The authors' reading: the largest gamma effect "is not large".
* The linear model gives a larger average damping (about −2 points) and a similar maximum (+7.0 at 30 minutes).

## Caveats
* **The authors':** positions opened before January 2020 are missing for a few long-dated series; the estimate is of the maximum in this sample only.
* **Mine:**
  * **The window (July 2020–June 2023) contains no crash.** The largest gamma-driven increase they can measure is bounded by the worst day in a calm-to-bearish three years. It says nothing about a day like 5 November 2026.
  * The models are fitted month by month with a daily variance level taken out first. Any effect of gamma on the *level* of a day's volatility is absorbed by that daily term; what is left is the within-day part. So the estimate is a lower bound on the total effect.
  * Only Cboe-listed SPX options: no SPY options, no E-mini options, no over-the-counter positions.
  * Cboe has an interest in the answer.

## What it means for us
* **The sign assumption behind public "GEX" is wrong for the S&P at short maturities.** Customers buy and sell 0DTE options in nearly equal amounts. A measure that assumes "dealers long calls, short puts" from open interest is a rough proxy at best. This bears directly on the open item of which gamma measure to trust (N1 in the map): the honest answer is that open-interest proxies carry a large error in sign for short-dated index options.
* **Our own robust result (gamma state forecasts the size of the next move) is larger than this paper's estimate.** Two readings: (a) our proxy picks up something besides hedging, for example that gamma is low after selloffs when volatility is high anyway; (b) their method removes the daily level. Both are probably true. The derivation has to keep "low gamma" and "after a selloff" apart, because they arrive together.
* **Regime date to respect:** May 2022, when daily expiries began. Market-maker gamma is lower and more often negative after it.
* **For "is it priced?":** if the true hedging effect is a fraction of a point on average and a few points at most, then even if the option market ignored it completely, the mispricing available is of that order: a few percent of the option's price in calm states, not tens of percent.

## How we would replicate or extend it on our data
* We cannot build true positions without trade-level capacity data. The Cboe open-close files give them daily. Cost not yet checked.

## Open questions
* How much of the daily *level* of volatility does market-maker gamma at the open explain? That is the number an overnight option buyer needs, and this paper's design removes it.
