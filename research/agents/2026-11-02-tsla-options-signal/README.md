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

## Results (`options_signal.py` → `out/signals.csv`, `out/results.json`; `figure.py` → `out/options_signal.png`; $0, ThetaData Value tier)
**Sample:** 1,592 days (2020-07-01 → 2026-10-30), 82 monthly end-of-day chain files.

| Signal | Next 10 sessions, % per sd (beyond momentum + gamma) [95% CI] | p | Holm | R1 / R2 slope | Top vs bottom third, next 10 sessions | OOS R² 2023–26 (with / controls only) | Now (Oct 30) |
|---|---|---|---|---|---|---|---|
| O1 IV spread (calls vs puts) | +0.51 [−0.34, +1.58] | 0.24 | 0.95 | −0.48 / +0.74 | +1.09% vs −0.06% | −1.18% / −1.12% | **0th pct** (puts rich vs calls) |
| O2 put skew | +1.01 [−1.27, +2.93] (sign opposite to Xing et al.) | 0.30 | 0.95 | +0.88 / +0.14 | +2.36% vs −0.47% | −3.60% / −3.41% | 88th pct (steep) |
| O3 put/call volume | +0.54 [−1.25, +2.82] | 0.43 | 0.95 | +0.71 / +0.52 | +1.12% vs +0.24% | −1.83% / −1.12% | 94th pct (put-heavy) |
| O4 put/call OI | +0.99 [−1.86, +2.32] | 0.52 | 0.95 | +2.28 / −1.53 | +0.76% vs −0.89% | −5.25% / −1.12% | 28th pct |

* **Verdict: no option-pricing or put/call signal forecasts TSLA's next 10 sessions beyond momentum and our gamma state.**
  * None passes (Holm 0.95), and none improves the 2023–26 out-of-sample forecasts.
  * The literature's single-stock effects do not show up in a time-series test on TSLA alone.
* **Leans (descriptive, not proof):**
  * The IV spread points the Cremers–Weinbaum way (calls rich → slightly better).
  * Put skew, volume and OI all lean *contrarian*: fear → slightly better, opposite to Xing et al.
* **Named tops (descriptive, n 8):** put skew was at or below its 10th percentile at 4 tops (Feb 2023 10th, Jul 2023 2nd, Jul 2024 2nd, Dec 2024 4th): no one was hedging. The other 4 were at the 24th–65th. A candidate top-warning ("flat skew after a run") to pre-register and test on all tops.
* **Named bursts (day before):** no pattern in O1 or O2 (percentiles spread from 1st to 98th).
* **Data-quality note:**
  * The Databento 1-minute TSLA close (single venue, publisher 2) differs from Yahoo's close on some days (Oct 29 2026: 403.2 vs 397.45).
  * Because the IV spread is a put-call-parity measure, a stock-price error biases it.
  * Oct 30's reading uses a close on which both sources agree (399.83 vs 399.81).
* **Answer to the owner:** no, this is not already in gamma.
  * Gamma maps *where and how fast* (hedging levels); option pricing is a *fear/complacency gauge*.
  * For TSLA the gauge adds no tested forecasting power; its leans are contrarian.
  * Today's mix is fear-heavy: puts priced over calls (lowest in a year), skew 88th pct, put volume 94th pct. That is unlike the flat-skew complacency seen at 4 past tops.
