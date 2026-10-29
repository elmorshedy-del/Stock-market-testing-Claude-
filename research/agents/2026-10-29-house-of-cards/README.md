# House of cards: do forced rallies unwind faster, and does that tell you when to exit? (pre-registration)

* **Owner, 2026-10-29:**
  * "The days before [Sept 2, 2020] including the gap up weren't driven by the kind of price discovery that tends to last… the same mechanism that led the violent move up was forced inflows… going up in a relative vacuum. Once that hit some exhaustion it all collapsed in itself just as quickly. A house of cards."
  * The goal is exits on short-term calls: rules, not hand-drawn lines. See [OWNER_NOTES](../OWNER_NOTES.md).
* **Mechanism:**
  * When customers buy upside calls in size, dealers who sell them must buy stock to hedge, and more as price rises (short gamma).
  * The price rise is then partly mechanical, and the demand for convexity lifts implied volatility *with* price: "spot up, vol up". An ordinary rally lowers implied vol.
  * When the buying stops or the calls are sold, the hedges unwind the other way.
* **Prediction:**
  * Forced (vol-up) rallies give back more of their gain, and faster, than genuine (vol-down) rallies of the same size.
  * Gap-ups at the end of forced runs fade more within the day, so an exit at the open beats holding to the close.
* **Builds on:**
  * [forced-flow](../2026-10-24-forced-flow/): moves on low dealer-gamma days are given back.
  * [gap-teardown](../2026-10-28-gap-teardown/) and [calendar-mechanics](../2026-10-29-calendar-mechanics/): the earnings-morning fade.
* **The only prior look:** the descriptive Sept 2020 numbers in OWNER_NOTES (S&P +4.0% and VIX +4.6 over the 10 sessions to Sept 1, 2020; this combination is on 3.7% of days since 1990). No run, give-back or gap outcome has been computed.

## The forced-run signature (fixed)
* **Run window:** the 10 sessions ending at the close before the decision (the run's end for index runs, the session before the gap for gap-ups).
* **Forced (primary, binary):** the price rose over the run AND implied vol rose over the run.
  * Implied vol is VIX for the S&P, VXN for the Nasdaq-100, and for single names the 30-day at-the-money implied vol from local end-of-day chains: the expiry nearest 30 days (20–45), strikes within ±3% of the parity spot.
* **Options-led (secondary, single names):** call contracts traded × 100 / shares traded, 10-session mean over the prior 60-session mean, top tercile within stock.

## Tests (Holm across H1–H6; pass at Holm p < 0.05; two-sided bootstrap p)
**Index runs, 1990–2025** (S&P/VIX). A run end is a session whose 10-session return is at or above the 90th percentile of all 10-session returns and is the highest close of its 10 sessions. Events are taken in order with at least 10 sessions between them.
* **H1, give-back:**
  * The worst fraction of the run given back within the next 10 sessions: (close − lowest close in t+1..t+10) / (close − close 10 sessions earlier). Forced minus genuine.
  * **Stratified by VIX tercile at the run's start**, so vol-up runs in high-vol regimes are not compared with calm ones. Event bootstrap.
  * Prediction: > 0.
* **H2, the cliff:**
  * The share of runs giving back ≥ 50% within 10 sessions, forced minus genuine, same stratification.
  * Prediction: > 0.
* **H3, replication:** H1 on the Nasdaq-100 with VXN, 2001–2025. Prediction: > 0.

**Single names: gap-ups ≥ 0.5σ** (the labeled set) for TSLA, NVDA, QQQ, MSFT and MU, 2020-02 – 2026-10-14 (local chains). Stock-demeaned; date-block bootstrap.
* **H4:** forced run into the gap vs not; Y1 (open → 10:30, σ). Prediction: lower.
* **H5:** forced run into the gap vs not; the gap day's open → close return (σ, Yahoo daily), the "sell at the open vs hold to the close" decision. Prediction: lower.
* **H6:** options-led run (top tercile) vs not; open → close (σ). Prediction: lower.

## Also reported (descriptive, no test)
* The time to give back half the run (sessions, censored at 10), forced vs genuine.
* **The exit translated to an option:** for H5's two groups, the open → close move priced through a 7-day at-the-money call. Black-Scholes at the prior close's implied vol, held constant; the stated simplification ignores the intraday vol change.
* **Profiles:** Sept 2, 2020 (S&P, QQQ, NVDA), and the current state of TSLA, NVDA, QQQ and SPY as of the latest data.

## Limits stated in advance
* VIX measures index options; single-name implied vol is from end-of-day quotes, so it is noisy.
* A rising implied vol can also mean fear of a fall (put buying), not call demand. The signature cannot separate the two; the call-volume measure (H6) is the partial check.
* Single-name tests cover 2020 onward only.

---

# Results (written after the run; pre-registered @ bab7db6)

**Deviation:** for H6, windows spanning a stock split were dropped, because option contract counts jump at a split and Yahoo share volume is split-adjusted.

## Tests (Holm across H1–H6: nothing passes; lowest Holm p 0.20)
| | n (forced / genuine) | forced minus genuine [95% CI] | raw p | Holm |
|---|---|---|---|---|
| H1 S&P give-back (fraction of run, VIX-stratified) | 12 / 170 | +0.08 [−0.19, +0.52] | 0.43 | 1.0 |
| H2 S&P cliff (≥ 50% given back in 10 sessions) | 12 / 170 | +0.00 [−0.21, +0.48] | 0.73 | 1.0 |
| H3 Nasdaq-100 give-back (VXN-stratified) | 9 / 119 | +0.08 [−0.28, +0.41] | 0.62 | 1.0 |
| H4 gap-up after a forced run, open → 10:30 (σ) | 429 / 1,138 | −0.05 [−0.12, +0.03] | 0.20 | 1.0 |
| **H5 gap-up after a forced run, open → close (σ)** | 429 / 1,138 | **−0.13 [−0.25, −0.01]** | **0.033** | 0.20 |
| H6 gap-up after an options-led run, open → close (σ) | 487 / 970 | +0.01 [−0.12, +0.13] | 0.92 | 1.0 |

## Descriptive
* **Index runs** (top-decile 10-day rallies):
  * Forced runs are rare: 12 of 182 S&P runs, 9 of 128 Nasdaq-100 runs.
  * Share giving back half within 10 sessions: S&P 33% forced vs 26% genuine; Nasdaq-100 **56% vs 29%**. Median give-back on the Nasdaq-100: 0.56 vs 0.23 of the run.
  * The median forced path sags to 0.86 of the run by session 5, while the genuine path keeps rising (about 1.08).
  * **Aug 28, 2020 was a forced S&P run:** it gave back 130% of the run, half of it within 5 sessions.
* **Gap-ups:**
  * Forced runs precede 27% of gap-ups.
  * Gap day open → close: median −0.04% vs +0.19%. Violent first hour **18% vs 13%**.
* **The exit in option terms** (7-day ATM call bought at the open, marked at the close, prior-close IV held constant):
  * Median **−2.8%** after a forced run vs **+3.7%** after a genuine run.
  * A loss of 25% or more: 30% vs 25%.
  * Sept 2, 2020: NVDA (forced run, VF) −39%; QQQ (forced, VF) −7%; MU (forced, but SC) +60%.
* **Current state:**
  * TSLA's 10 sessions to Oct 27: +8.6% with its 30-day ATM implied vol **down** 4.5 points (0.425 → 0.380). A genuine run by this signature.
  * S&P Oct 13–27: −1.1% with VIX +2.2, which is not a rally.

## Verdict
* **The owner's thesis points the right way, but it is not proven.**
  * Every forced-vs-genuine contrast leans as predicted except H6: index give-backs, cliffs, gap-day open→close, the violent-fade rate and the option P&L.
  * Only the gap-day open→close is individually significant (raw p 0.03), and nothing survives Holm.
  * At the index level forced rallies are too rare (21 events in 35 years) to settle it.
* **For exits, the practical reading:**
  * After a run where price and implied vol rose together, the edge in holding a short-dated call from the gap's open to the close disappears: median −2.8% vs +3.7%.
  * Selling into the open is favoured there; after a genuine run (vol falling), holding is.
  * This is a tilt, not a rule. Treat it as a forward check before sizing on it.
* **Options-led volume** (call volume up relative to shares) did not separate anything; implied vol carried what signal there was.
