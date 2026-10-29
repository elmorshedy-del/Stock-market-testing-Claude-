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
