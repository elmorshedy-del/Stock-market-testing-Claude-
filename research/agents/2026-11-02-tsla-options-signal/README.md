# Do TSLA's calls and puts tell us about coming rallies, rebounds and tops, beyond what gamma already says?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02
**Type:** pre-registered test. Written and pushed before any signal was computed; the option-history download started at the same time.
**Owner's ask:** "What about calls and puts, are they more informing about expected rebounds, expected rallies, expected tops? Or do we already have this version in gamma?"

## Why this is not already in gamma
* **Our gamma engine** uses *positions* (open interest) and an *assumed dealer side* to map where hedging damps or amplifies moves: walls, flip, pockets. It is about **where and how fast**, not **which way**.
* **Option *prices* carry what buyers are willing to pay for each direction.** The published single-stock evidence:
  * **IV spread** (call IV − put IV at the same strike and expiry): a positive spread predicts higher returns next week/month (Cremers & Weinbaum 2010, *JFQA*).
  * **Skew** (OTM put IV − ATM call IV): steep put skew predicts lower returns (Xing, Zhang & Zhao 2010, *JFQA*).
  * **Signed opening volume** (Pan & Poteshman 2006): we cannot sign volume (our minute signing failed), so only unsigned volume is tested here.

## Signals (TSLA, daily, from end-of-day option quotes; 2020-07 → 2026-10)
* **Inputs:**
  * TSLA's 16:00 stock close (Databento 1-minute bars);
  * the 3-month T-bill (^IRX) as the rate;
  * Black–Scholes IVs from each contract's own mid (American early-exercise ignored; small for near-money, short-dated puts).
* **O1 IVS:** the equal-weighted mean of (IV_call − IV_put) over same-strike pairs with expiries 10–60 days, |ln K/S| ≤ 0.10, both mids ≥ $0.05. Prediction: **positive** slope.
* **O2 SKEW:** at the expiry nearest 30 days, the IV of the put nearest K/S = 0.90 minus the IV of the call nearest K/S = 1.00. Prediction: **negative** slope.
* **O3 PCV:** log(put volume / call volume), expiries ≤ 60 days, summed over the trailing 5 sessions. Prediction: none (unsigned volume mixes buyers and sellers).
* **O4 PCOI:** log(put OI / call OI) from `td_gamma_TSLA.csv`. Prediction: none.

## Test
* **Outcome:** TSLA log return from the **next** session's close (so the signal is known in time) to +5, **+10** and +20 sessions.
* **Model:** the forward return regressed on the standardised signal, with controls:
  * past 5- and 20-session returns;
  * gamma state from our engine (spot vs flip %, and the gex_classic z-score vs the trailing year).
  * So the slope measures **information beyond gamma and momentum**.
* **Inference:** 60-session block bootstrap (2,000). **Primary: 10 sessions, Holm across O1–O4.**
* **Out of sample:** fit 2020-07 → 2022-12, predict 2023-01 → 2026-10 (expanding); OOS R² vs the historical mean.
* **Era split:** R1 2020–21 vs R2 2022+.
* **Practical form:** next-10-session return when the signal is in its top vs bottom third (trailing 1 year).
* **For the owner (descriptive):**
  * the percentile of O1 and O2 on the day before each of the 11 named bursts (rallies) and at the 8 named-move tops;
  * today's readings.

## Limits stated now
* One stock; about 1,550 overlapping days, roughly 155 independent 10-session windows. A modest real effect may not reach significance.
* End-of-day quotes on TSLA's very liquid near-money options are reliable. Far OTM puts are noisier.
* The Cremers–Weinbaum and Xing et al. results are cross-sectional (many stocks); a time-series test on one stock is a harder test.
