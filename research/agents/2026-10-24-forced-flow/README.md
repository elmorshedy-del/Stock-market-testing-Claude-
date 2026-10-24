# Forced flow: is price predictable only where someone must trade?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-24
**Type:** a theory with pre-registered falsification tests, then diagnosis and follow-up tests, each pre-registered before it runs. This file was pushed before any test ran.
**Builds on:**
* dealer-sign (call gamma damps the next-day range);
* the full setup (§4w, edge_lab);
* spy-channel (S&P gamma rungs, VIX × gamma);
* the failures of shape, macro and candle-model forecasts (2026-10-24 analogs, Kronos).

**Verdict:** (after the run)

## The theory
* **Discretionary flow is arbitraged away;** forced flow is not.
* **Price behaviour is therefore predictable only where an actor must trade by rule regardless of price.**
* **The predictable part is mostly the size and path of moves, not their direction,** and it scales with the forced flow relative to liquidity.
* **Each test below names a forced actor,** derives a prediction no news story would produce, and states what result kills it.

## Data
* Yahoo daily bars (repository copies, outcomes to 2026-10-14).
* SqueezeMetrics `DIX.csv` (S&P dealer gamma, 2011–2026).
* `td_gamma_<sym>.csv` (own dealer gamma for TSLA, MSFT, NVDA, SPY, QQQ, MU; 2020–2026).
* The private SPY 1-minute option files: parity spot, 2023-01-03 to 2026-10-15. These stay outside the repository, and only derived daily numbers are written here.
* The macro panel's FINRA margin debt (monthly, 1998–2026). It is used with a 2-month lag, because FINRA publishes about three weeks after month end.
* ^GSPC daily since 1928.

## A. Dealers (the core): sign flip and size law
* **Forced actor:** option dealers hedging delta.
  * Long gamma, they sell rallies and buy dips, so returns mean-revert.
  * Short gamma, they chase, so returns continue.
* **Size law:** the effect grows with hedge flow relative to liquidity: H = dealer gamma ($ per 1% move) ÷ 20-day average dollar volume.

**A1 (daily, S&P):**
* **Data:** SqueezeMetrics GEX ÷ SPY 20-day dollar volume, 2011–2026.
* **Bins:** H's trailing-252-day percentile, in quintiles (point in time).
* **Statistic:** in each quintile, the slope β of the next-day return on today's return.
* **Prediction:**
  * β falls monotonically from quintile 1 (lowest gamma) to quintile 5;
  * β(Q1) > 0 (continuation) and β(Q5) < 0 (reversal).
* **Pass:** β(Q1) − β(Q5) > 0 with a 20-day block bootstrap p < 0.05 (one-sided, 2,000 draws), **and** a Spearman correlation between β and quintile rank below −0.7.
* **Also:** the 6 single names with their own gamma (`td_gamma`, gex_classic ÷ own dollar volume), 2020–2026, pooled within ticker. Reported; for single names the pass is the same Q1 − Q5 test.

**A2 (intraday, SPY, 2023–2026):**
* **Returns:** r_rest = log(S at 15:30 ÷ prior close); r_last = log(S at 16:00 ÷ S at 15:30). S is the 1-minute parity spot.
* **Statistic:** the slope of r_last on r_rest by quintile of SPY's own H (`td_gamma_SPY` gex_classic ÷ SPY dollar volume, trailing percentile), and by the sign of gex_classic.
* **Prediction:** a positive slope (last-half-hour continuation) when gamma is negative or low, falling toward zero or below when it is high.
* **Pass:** slope(low-H half) − slope(high-H half) > 0 with a block bootstrap p < 0.05.

**Kill for A:** no ordering by H, in daily or intraday data. Then the dealer mechanism is not what drives our gamma results.

## B. Expiry release
* **Forced actor:** dealers' hedges unwind when options expire.
* **Prediction:** the larger the share of gamma that expires at a monthly expiry, the more realized volatility rises from the week before to the week after.
* **Data:** 6 tickers, 2020–2026.
  * x = `gamma_share_1d` on the session before the monthly expiry;
  * y = log(mean |daily return| over the 5 sessions after ÷ the 5 sessions before).
* **Statistic:** the within-ticker slope of y on x.
* **Null:** permute x across expiries within ticker, 2,000 draws.
* **Pass:** slope > 0 with p < 0.05.
* **Kill:** slope ≤ 0.

## C. Volatility-target funds: the window drop-out echo
* **Forced actor:** funds that size positions by trailing realized volatility (often a 1-month window), a large strategy since about 2008.
* **Mechanical prediction:** when a big move drops out of the trailing 21-session window, measured volatility falls by construction, so these funds buy. No news is involved.
  * **Event:** a session whose |return| ≥ 2.5× the prior 20-day standard deviation, and is the largest |return| in its 21-session window.
  * **Outcome:** the S&P return over sessions s+21 to s+23, in excess of the mean 3-session return.
* **Prediction:** positive excess in 2008–2026; about zero in 1960–2007, before the strategy existed at scale.
* **Pass:** post-2008 excess > 0 (bootstrap p < 0.05) **and** greater than the pre-2008 excess.
* **Also reported:** the 63-session (3-month window) echo.

## D. Leverage as fuel
* **Forced actor:** leveraged holders hit by margin calls and risk limits.
* **Prediction:** after a volatility shock, the S&P's drawdown over the next 20 sessions is deeper when margin debt grew fast over the prior year. Average returns over all days do **not** differ by leverage growth.
* **Events, 1998–2026:** VIX 5-day change ≥ +40%, events at least 40 sessions apart.
* **Statistics:**
  * the event's 20-session max drawdown from its close, regressed on margin-debt year-on-year growth (2-month lag);
  * the mean drawdown, top vs bottom half of leverage growth.
* **Null:** permute leverage across events, 5,000 draws.
* **Pass:** drawdown deeper with higher leverage growth, p < 0.05.
* **Control:** the next-20-session mean return over all days, top vs bottom half of leverage growth. The prediction is no difference.

## Predictions (written before the run)
* **A1 and A2:** expected to pass. The literature finds gamma-dependent autocorrelation and last-half-hour momentum.
* **B:** uncertain.
* **C:** uncertain, and weaker, because many funds smooth their windows.
* **D:** low power with about 30 events, so likely inconclusive.

## Then
Each result gets a diagnosis: era and ticker splits, alternative explanations, and what it implies. Any follow-up test is written here as an amendment and pushed before it runs.
