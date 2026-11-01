# SPY RSI across frames, was Friday's selling expiring gamma, and post-2020 precedents for this week

* **Owner, 2026-11-01:** "For spy what does rsi point to on different significant frames. And what was this hard selling a result of gamma expiring all day. And is there a precedent to a week like this (a rotation week / deep selling / and Tesla holding like this) and what happened after. Only search after 2020 for this."
* **Builds on:**
  * [technical-indicators](../2026-10-16-technical-indicators/): RSI level and divergence don't tell true lows from false ones; a 1-ATR bounce off a 20-day closing low is the filter.
  * [sp-multivariate](../2026-10-15-sp-multivariate/): for the S&P, weak weekly RSI / momentum means a broken trend and more correction risk; high RSI means lower risk.
  * [dealer-sign](../2026-10-16-dealer-sign/): the classic convention holds for SPY.
  * [week-review](../2026-10-31-week-review/).
* **Written and pushed before computing.**

## Part R: RSI (descriptive)
* **Indicator:** RSI(14), Wilder, on SPY at 1-hour, 4-hour (from 1-hour bars), daily, weekly and monthly frames, each with its trailing percentile.
* **Rules applied:**
  * The sp-multivariate reading: weekly RSI in its weakest third had a 37% chance of a 10% fall within 13 weeks vs 8% in its strongest third.
  * The 1-ATR bounce trigger level: the first close ≥ 1 ATR(14) above the latest 20-session closing low.
  * Daily bullish divergence state.

## Part M: Friday's dealer hedge flow (descriptive mechanics, no pass bar)
* **Instrument:** SPY options only.
* **Convention:** classic (dealers long calls, short puts), supported for SPY by dealer-sign.
* **Positions:** OI dated Oct 30 (the Oct 29 close). Friday's own 0DTE opening trades are **not** in any OI file.
* **IVs:** the Oct 30 closing-chain smile (engine `chain_day`), scaled each 5 minutes by VIX(t) / VIX(close).
* **Delta:** Black–Scholes, with time to 16:00 on each expiry date.
* **Path:** SPY 1-minute closes, 09:30–16:00, sampled every 5 minutes.
* **Dealer hedge trade per step** = −(change in dealer delta), split into three parts:
  * **gamma:** price moves at fixed time and vol;
  * **charm:** time passes at fixed price and vol;
  * **vanna:** vol changes at fixed price and time.
* **Expiry split:** the Oct 30 expiry vs all later expiries.
* **Scale:** cumulative hedge dollars vs SPY's traded dollar volume (Yahoo 1-minute volume × price).
* **Answers:**
  * (i) how much selling hedging added;
  * (ii) whether it came from the expiring contracts;
  * (iii) whether charm pushed selling or buying;
  * (iv) whether the 14:52 low and the rebound line up with the 0DTE hedges unwinding.
* **Threats, stated now:**
  * The convention.
  * One-day-stale positions; same-day 0DTE positions are invisible.
  * SPX and futures options are not included.
  * IV scaling is uniform across strikes.

## Part D3: precedents since 2020 (descriptive analogs)
* **Weeks:** calendar weeks ending Friday. Return = Friday close / prior Friday close − 1. Sample: weeks ending 2020-01-03 to 2026-10-23 (forward outcomes needed).
* **Primary analog:** QQQ week ≤ −1.5% **and** RSP − QQQ ≥ +2.0 pts **and** TSLA − QQQ ≥ +5.0 pts.
  * This week: QQQ −1.97%, RSP − QQQ +2.79, TSLA − QQQ +9.4.
* **Secondary sets:**
  * **S1 rotation weeks:** QQQ ≤ −1.5% and RSP − QQQ ≥ +2.0.
  * **S2 TSLA holds in a tech-selloff week:** QQQ ≤ −1.5% and TSLA − QQQ ≥ +5.
  * **S3 daily:** QQQ ≤ −3% on the day and TSLA ≥ −1% on the day. Friday: QQQ −3.47%, TSLA −0.87%.
* **Outcomes:**
  * From the week's Friday close: SPY, QQQ, TSLA at +1, +2 and +4 weeks, and SPY's worst drawdown within 4 weeks.
  * S3 from the day's close: +5, +10 and +20 sessions.
* **Base:** all weeks (all days for S3) in the same sample.
* **Spacing:** qualifying weeks within 4 weeks of an earlier one are kept in the list but excluded from the averages (no overlap).
* **Reporting:** every match is listed with its date. n will be small, so: counts, means and medians vs base, no significance claims.
* **Prediction (low confidence):**
  * Rotation weeks are followed by S&P results near base (D2 found no edge).
  * TSLA's relative strength persists a little over 1–2 weeks (momentum).
