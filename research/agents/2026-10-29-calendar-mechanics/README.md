# Calendar mechanics: tracing seasonal weakness to the forced flow behind it (pre-registration)

* **Owner, 2026-10-29:**
  * "There is underlying weakness (and strength) that patterns with particular times or conditions… September wouldn't be consistently one of the weakest months… somewhere out there is able to trace it back to its origin… the generalized rule that controls the mechanics."
  * Then: "Do it, and if there are any earlier tests we delayed that go well with these, do them too."
* **The working rule:**
  * Equity markets are inelastic (Gabaix-Koijen 2021). So prices drift when a large, scheduled, price-insensitive flow meets a temporary absence of the marginal buyer. The calendar schedules both.
  * Related: Hartzmark-Solomon (predictable price pressure from dividend reinvestment), Etula et al. 2020 (month-end cash needs), Lou 2012 (flow-induced trading).
* **The motivating fact** (descriptive, written up before this pre-registration, S&P 500 1950–2025):
  * September's weakness is all after the third Friday: +0.24% before vs −0.97% after (t −3.3, 38% of years up).
  * The 5 sessions after a quarterly expiry average −0.14% (39% up) vs +0.11% (58% up) after monthly expiries.
  * This came from trading lore, so it may be data-mined. **The 1950–2025 S&P late-September result is not re-tested here.** Every test below uses other years, other markets, or the timing differences between candidate causes.
* **Builds on:** [forced-flow](../2026-10-24-forced-flow/) (month-end and Russell moves are given back; the expiry-size *volatility* law failed), [gap-context](../2026-10-29-gap-context/) (the earnings-gap fade lead), and TODO items E1, E2, N4.

## Candidate mechanisms and their clocks
| Mechanism | Clock | Exists since |
|---|---|---|
| Index-option expiry hedges (support into expiry, released after; quarterly is largest) | 3rd Friday (moves between the 15th and 21st) | US index futures 1982, options 1983 |
| Buyback blackout (the largest net buyer steps away) | about 2 weeks before quarter-end, a fixed date about the 16th | SEC Rule 10b-18, Nov 1982 |
| Corporate tax date (cash drained from the system) | the 15th of Mar/Apr/Jun/Sep/Dec | always |
| Pension and balanced-fund quarter-end rebalancing | last days of the quarter | grows after 1980s |
| Japan's index expiry (SQ) | 2nd Friday | Nikkei futures 1988 |

## Part A: index tests (daily log returns; Holm across A1–A8; date-block or year-block bootstrap, 10,000; two-sided p; pass at Holm p < 0.05)
* **A1, pre-1950 out of sample** (S&P 500, 1928–1949; no derivatives, no buybacks):
  * Mean daily return in September sessions after the 3rd Friday, minus all other sessions.
  * Prediction: none for the sign. If negative, the late-September weakness predates expiry and buybacks.
* **A2, other markets** (DAX 1988–2025, FTSE 1984–2025, Nikkei 1970–2025; pooled, year-block bootstrap):
  * The same late-September contrast.
  * Prediction: negative (replication of existence).
* **A3, the era test** (S&P):
  * The late-September contrast in 1983–2025 minus the same in 1950–1982.
  * Prediction: negative if expiry or buybacks (both born 1982–83) are the origin.
* **A4, quarterly vs monthly expiry × era** (S&P):
  * (Mean of the 5 sessions after a quarterly 3rd Friday − mean after a monthly one), in 1983–2025 minus in 1950–1982 (placebo era, when the 3rd Friday meant nothing).
  * Prediction: negative.
* **A5, the clock race** (S&P 1983–2025, quarterly months):
  * Sessions on or after the 16th but on or before the 3rd Friday ("blackout and tax date have started, expiry has not") vs sessions after the 3rd Friday to quarter-end.
  * Statistic: mean(between) − mean(after). Expiry origin predicts > 0 (support persists until expiry); fixed-date origins predict ≈ 0.
* **A6, Japan's clock** (Nikkei 225, 1989–2025, quarterly months):
  * The mean of the 5 Tokyo sessions after the US 3rd Friday, minus the 5 after Japan's own SQ (2nd Friday).
  * Local-expiry origin predicts > 0 (weakness after the local SQ); US-flow origin predicts < 0.
  * Two-sided; the sign tells which.
* **A7, dose** (SqueezeMetrics, 2011–2025, all monthly expiries):
  * Spearman of the GEX change from the session before expiry to the session after (gamma rolled off) with the next-5-session S&P return.
  * Prediction: ρ > 0 (a bigger roll-off means a weaker week). Note: the forced-flow study's volatility version of this failed.
* **A8, liquidity drain** (Treasury daily cash balance, 2009–2025):
  * Spearman of the weekly change in the Treasury General Account with the same week's S&P return, non-overlapping Wednesday-to-Wednesday weeks.
  * Prediction: ρ < 0 (cash pulled out of the banking system weakens stocks).

## Part B: back to single names (Holm across B1–B5)
* **Events:** gap-ups ≥ 0.5σ (gap-teardown definitions, labels and outcomes Y1/Y2), extended to all 13 names by fetching the 9 parked names' first-hour bars (Databento, about $0.2). AVGO and ORCL earnings dates permitting.
* **B1, post-quarterly-expiry window:**
  * Gap-ups in the 5 sessions after a quarterly 3rd Friday vs all others.
  * Prediction: Y1 lower. All 13 names.
* **B2, the earnings-gap fade, out of sample:**
  * The gap-context C7 contrast (earnings-reaction gap-up vs other gap-ups) on the 9 parked names only.
  * Prediction: Y1 lower (now directional, from the 4-name lead).
* **B3, the call-wall cap, out of sample:**
  * Gap-context C1 on MSFT and MU (the parked names with local chains).
  * Prediction: Y1 lower. Low power, stated.
* **B4, the earnings fade mechanism (E1):**
  * Earnings-reaction gap-ups with local chains (TSLA, NVDA, MSFT, MU, 2020–2026).
  * Spearman of "unwind pressure" with Y1. Unwind pressure = near-the-money call OI (strikes from the prior close to +10%, ≤ 45 days, OI dated the reaction day) per 20-day average share volume × the ATM implied-vol drop (report-day close to reaction-day close).
  * Prediction: ρ < 0. Explanatory, not predictive (the vol drop is known only after).
* **B5, pre-earnings selling into the close (N4):**
  * Stocks with a report after that day's close: the 15:30–16:00 return on the report day vs the same stock's other days (stock-demeaned). 12 stocks, Yahoo 60-minute bars, Nov 2023 – Oct 2026.
  * Prediction: lower.

## Data
* **Indices:** S&P 500 daily from 1927 (Yahoo); DAX, FTSE and Nikkei daily (Yahoo).
* **Positioning and cash:** SqueezeMetrics DIX.csv; Treasury Daily Treasury Statement operating cash balance (fiscaldata.treasury.gov). The account was called "Federal Reserve Account" until 2021-09, then "TGA".
* **Earnings:** dates and timing from Alpha Vantage.
  * Every company here reports after the close. Alpha Vantage's few "pre-market" flags for these names (for example MSFT July 2021/22/23) are treated as after the close.
* **Gaps and chains:** gap labels from the Databento first-hour bars; local ThetaData chains.
* **Spend:** about $0.2 of Databento.

## Limits stated in advance
* Calendar windows overlap (quarter-end, expiry, blackout, tax date), so A5 and A6 are the discriminating tests and A1–A4 establish existence and era.
* There are about 76 Septembers per index, so power is modest.
* Japan's SQ also aligns with Japan's own fiscal calendar, so A6 separates local from US timing, not expiry from every local factor.
