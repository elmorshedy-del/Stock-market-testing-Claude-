# Three positioning claims, tested: TSLA's strike crossing, correlation × gamma, put monetization

* **Owner, 2026-10-26:**
  * "was this particular level it opened at some kind of resistance by some positioning and once it opened above it it caused a forced buy";
  * "we want to formalize this correlation thing mentioned in the letter by testing and also that large put sell since these can be confusing or just noise."
* **The letter** (a SpotGamma-style newsletter the owner pasted):
  * "if COR1M starts to creep higher with SPX < 7,700, then we want to start positioning for a broader selloff";
  * "One trader bought nearly 110K QQQ October 30 $700 puts for an estimated $111 million… closed for a 193% gain."
* **Prior evidence that matters:** [dealer-sign](../2026-10-16-dealer-sign/) Part B. **Dealers are net long calls in TSLA:** call gamma damps the next-day range (−0.070, p < 0.001). Put gamma is inconclusive in TSLA.

## P1. Did TSLA's gap cross a positioning level, and does crossing one force buying?
* **Today, descriptive:**
  * the call open interest at the strikes TSLA gapped over (375, 380), from OI dated Oct 26 (positions at Friday's close);
  * the dealer delta change from $372.22 to $391.62 under the classic convention (dealers long calls, short puts) and under the all-short convention, in shares, compared with Monday's TSLA volume.
* **Historical test (TSLA, 2020 to 2026-10-14):**
  * For each day, find the largest call-OI strike within 0–10% above the prior close, expiring within 45 days, from OI dated that day (known before the open).
  * Events: up-gaps ≥ 2% whose **open is above that strike** (crossed overnight), vs up-gaps ≥ 2% that did not cross it.
  * Outcomes: open-to-close return (does the day continue?); the next 5 sessions' return from the close; the same-day gap-fill rate.
* **Competing predictions:**
  * owner: crossing forces buying, so continuation is **higher**;
  * dealer-sign (dealers long calls): dealers sell above the strike, so continuation is **lower**.
* Two-sided; bootstrap by event.

## P2. Correlation × gamma: does rising correlation while dealers are short gamma lead to a broader selloff?
* **Correlation:** realized 10-day average pairwise correlation of daily returns.
  * 41 large caps from 1990; 81 from 2020.
  * The letter's COR1M (implied) is not available here, which is a stated limitation.
* **"Rising":** the 5-session change in correlation is in the top third of its trailing-252 distribution.
* **Gamma state:**
  * **primary:** SqueezeMetrics GEX < 0 (2011–2026);
  * secondary: SPY below its flip, from the engine (2020–2026).
* **Outcomes:** the S&P's next-10-session return, and P(a close ≥ 5% below the 252-day high within the next 20 sessions, given the S&P was within 5% at the signal).
* **Primary contrast:** (GEX < 0 and rising) minus (GEX < 0 and not rising): next-10-day return **< 0** and drawdown probability **> 0**. 20-day block bootstrap, one-sided.
* All four cells are reported, plus the same contrast when GEX > 0.

## P3. Large put closes: a bottom signal or noise?
* **Verify the letter's trade:** OI of QQQ 2026-10-30 $700 puts, Oct 1–23 (ThetaData; licensed, only aggregates written).
* **Systematic, SPY and QQQ 2020 to 2026-10-14:**
  * **Large put close:** a single put contract (expiring in 3–60 days, strike within 15% of spot) whose OI falls by ≥ 40,000 contracts from the prior day.
  * Same-day expiries are excluded, so expiry roll-off is not counted.
  * **In a selloff:** the ETF is down ≥ 3% over the prior 10 sessions.
  * **Statistic:** mean next 5/10/20-session ETF return after selloff days **with** a large put close minus selloff days **without** one. Events are de-duplicated: one per 5 sessions per ETF.
  * Bootstrap by event; two-sided (the letter implies > 0).
* **Reading:** a positive difference means monetization marks short-term lows; otherwise it is noise.
