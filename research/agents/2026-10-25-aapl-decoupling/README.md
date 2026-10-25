# Does AAPL decoupling from the S&P warn of pullbacks, and why?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-25
**Type:** follow-up to a post-hoc lead, with four pre-registered tests that could kill it. This file was pushed before any of them ran.
**Builds on:** 2026-10-25-spy-channel-reversion.
* There, AAPL's 20-day return correlation with SPY falling into the bottom fifth of its past year fired before all six 5%+ pullbacks of the 2022–2026 channel.
* When on, a top followed within 30 sessions 36% of the time vs 12% when off (post-hoc circular-shift p 0.024).
* Today the correlation is −0.17, the channel's lowest.

**Verdict:** (after the run)

## The proposed mechanism
* AAPL has been the S&P's largest or second-largest weight since about 2011. It is held by every index fund and most active funds.
* When the biggest constituent stops moving with the index, the index's gains are being carried by a narrower set of names. Leadership is rotating, and the rally rests on fewer shoulders. That is a crack in breadth, seen through the biggest holding.
* **What this predicts:**
  * **(a) Timing:** it should work only once AAPL is a mega-cap (2011+), not in 1990–2010, when AAPL was a small or mid weight.
  * **(b) Generality:** other mega-caps decoupling should warn too.
  * **(c) Robustness:** it should not be AAPL's own earnings-day jumps.
  * **(d) Specificity:** it should add information beyond general stock dispersion.

## Definitions (fixed here)
* **Index:** ^GSPC daily closes (Yahoo, 1990–2026). **Stocks:** Yahoo split-adjusted closes.
* **Signal:** the 20-day correlation of daily log returns, the stock vs ^GSPC.
  * **Alarm** = that correlation's trailing-252-day percentile ≤ 0.20 (the bottom fifth of its past year). Same rule as the channel study.
* **Event:** an S&P **top** is a close at a 252-day high that is followed by a close at least 5% below it before any close above it.
  * Non-reversion days exclude the sessions from each top to its lowest close.
* **Outcome on day t:** a top occurs in sessions t to t+29.
* **Statistic:** P(top within 30 | alarm on) − P(top within 30 | off), over non-reversion days.
  * **Null:** circular shifts of the alarm series, 2,000 draws, minimum shift 60 sessions. One-sided.
* **Evaluation days end 2026-08-14,** so any top within 30 sessions is already known.

## Tests
**H1. Out of sample in time** (the rule was found on 2022-10 to 2026-10):
* **Primary:** 1990-01-02 to 2022-10-12. Pass: difference > 0, p < 0.05.
* **Mechanism (a):** the difference in 2011–2022 is larger than in 1990–2010. Each era is reported with its own p.

**H2. Other mega-caps (generality, mechanism (b)):**
* MSFT, AMZN, GOOGL, META and NVDA, each with the same rule, 2013–2026.
* **Also:** an "average mega-cap" signal, the mean of the six names' 20-day correlations (AAPL included), with the same rule.
* **Pass:** at least 3 of the 5 non-AAPL names show a difference > 0, **and** the average signal's p < 0.05.

**H3. Not the earnings jump (robustness, mechanism (c)):**
* The AAPL–S&P 20-day correlation is recomputed with the 2 days of largest |AAPL − S&P| return gap removed from each window. Earnings reactions are almost always among them.
* **Also:** a Spearman (rank) correlation version.
* **Pass:** the drop-2 version keeps a difference > 0 with p < 0.05 over 2011-01-03 to 2026-08-14.

**H4. Beyond dispersion (specificity, mechanism (d)):**
* **Dispersion signal:** the average pairwise 20-day correlation of a 42-stock large-cap panel (those trading at each date). Alarm when it is in the bottom fifth of its past year.
* **Logistic regression,** 2011–2026, non-reversion days: outcome ~ AAPL alarm + dispersion alarm.
* **Pass:** AAPL's coefficient > 0 with a 20-day block bootstrap p < 0.05.
* **Also:** the dispersion alarm's own difference.

**Overall reading rule:**
* **"Real and explained"** if H1 passes **and** at least two of H2–H4 pass.
* **"AAPL-specific but unexplained"** if H1 passes and H2 fails.
* **"Channel coincidence"** if H1 fails.

**Prediction (written before the run):**
* H1: positive but weak out of sample, stronger after 2011.
* H3: holds.
* H2 and H4: uncertain.
