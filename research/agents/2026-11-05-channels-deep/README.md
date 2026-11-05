# Correction inside the uptrend or the start of a bear market? Channels retested, history and calendar, deep-change checklist

**Agent / session:** Claude, for the owner, 2026-11-05 after the close. **Pre-registered at commit:** the commit that first adds this README. P0 was drawn before it.

**Owner:**
* "This correction is done within the rising channel since 2023 … the only question now: does the market merit a full blown correction or just a correction within its uptrend."
* "Redraw these channels, retest the data and deepen the analysis."
* "Keep in mind November and how bear markets unfold by calendar … they usually start start of year to end, not break all of a sudden by end of year."

## P0. Observation (done; `draw.py` → `out/channels_redrawn.png`)
Log-price OLS channels, in-sample. z is today's distance from the midline in σ.

| | 2009 channel | 2023 channel |
|---|---|---|
| S&P | z +0.68 (−2σ band 5,971) | **z −1.95 (−2σ band 7,340; close 7,354)** |
| QQQ | z −0.46 | **z −2.64 (below its −2σ band, 671)** |
| SMH | z +1.37 | z −1.59 |
| RSP | z −0.18 | z +0.16 |

## P1. Retest of today's readings (descriptive)
* **Start date:** long channel from 2009-03-09, 2010-01-04 or 2012-01-03; short from 2022-10-12, 2023-01-03 or 2023-06-01.
* **Method:**
  * OLS;
  * median (LAD) regression;
  * lower envelope (OLS fitted to rolling 63-session lows).
* **No look-ahead:** a trailing 3-year (756 sessions) and trailing 15-year (3,780 sessions) fit ending today.
* **Report** today's z for each variant, for SPX, QQQ, SMH and RSP.

## P2. History: "short channel broken, long channel intact" (S&P 1950→2026, trailing fits only)
* **Daily trailing channels:**
  * short = trailing 756-session log-linear OLS;
  * long = trailing 3,780 sessions;
  * z = today's residual ÷ the window's residual SD.
* **Event:** short z ≤ −1.75 and long z > −1.0, on the first day after ≥ 120 sessions without the condition.
  * −1.75 is chosen so that today (−1.95 in-sample) qualifies; this is stated, not hidden.
* **Per event, listed individually:**
  * the drawdown from the prior 252-session high at the event;
  * the maximum drawdown over the next 252 sessions (≥ 10% = full correction, ≥ 20% = bear);
  * forward 63 / 126 / 252-session returns;
  * sessions until a new high.
* **Split "narrow" vs "broad":** the average stock's own short-channel z is > −1.0 (narrow) or ≤ −1.0 (broad), at the same date. NYSE Composite for 1966–2003, RSP from 2004.
* **H-P2 (my view, stated in advance):** ≤ 30% of events became ≥ 20% bears within 252 sessions, and narrow events turned into bears less often than broad ones.
* **Base rate:** the share of all days from which a ≥ 20% bear began within the next 252 sessions.

## P3. Calendar (the owner's observation), S&P 1928→2026
* **Episodes:** every ≥ 20% close-to-close bear market (peak = last record close before the decline; trough = the lowest close before a new record) and every ≥ 10% correction, with peak and trough dates.
* **H-P3 (owner):** bear-market peaks in Nov–Dec are rarer than chance (share < 2/12). One-sided binomial test.
* **Descriptive:**
  * peak-month distribution;
  * calendar spans;
  * corrections whose peak came in Sep–Nov (like Oct 6, 2026): the share that became ≥ 20% bears, vs corrections peaking in other months.

## P4. Deep-change checklist (descriptive)
* **Today vs the eve of the 2000, 2007, 2020 and 2022 bear markets** (the month of each peak) on:
  * credit (Baa − 10y; HY OAS where available);
  * the 2y yield minus fed funds;
  * the 10y real yield (DFII10, 2003–);
  * unemployment vs its 12-month low;
  * core CPI y/y;
  * oil y/y;
  * VIX ÷ VIX3M (2008–);
  * Shiller CAPE (multpl.com).
* Read as "rhymes" or "differs" with each eve. No pass/fail.
