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

## Results (run 2026-11-05 after the close)

Inputs that are not committed (gitignored `data/`): the FRED monthly series 1999-2026 and DFII10 2003-2026 as fetched on 2026-11-05. The ICE HY OAS series is not stored.

Files: `history.py` → `out/history.json`; `p4.py` → `out/p4.json`; `s1_threshold.py` → `out/s1_threshold.json`; `x1_depth.py` → `out/x1_depth.json`; `figure.py` → `out/history_calendar.png`, `out/deep_change_checklist.png`.

Today: S&P 500 close 7,353.73 on 2026-11-05; record 7,818.93 on 2026-10-06; -5.95% from the record, 22 sessions in.

### Corrections made before first publication
1. **P3 definition.** The first run used a 20% zigzag. That counts rallies inside a bear as new bear starts (six "peaks" in 1930-34 alone), which is not the pre-registered rule. Re-run with the pre-registered rule: peak = last record close before the decline. The zigzag is kept as a sensitivity check. The verdict is the same either way.
2. **P2 finished events.** The first run counted the 2026-03-13 event as finished although its 252-session window is still open. Only events with a full window now count: 20 finished, not 21.
3. **P1.** LAD and the lower envelope were run on the 2009-03-09 and 2023-01-03 starts only. OLS was run on all three starts.
4. **P2 narrow/broad.** The average-stock proxy switches from the NYSE Composite to RSP in 2007-01, not 2004, because a trailing 3-year fit needs three years of RSP history.
5. **P4 data gaps.**
   * HY OAS: FRED now serves only the last three years (ICE licence), so there are no eve values. The latest reading is 3.32 (Nov 4).
   * The 10y TIPS series starts in 2003, so the 2000 eve has only the proxy (10y minus core CPI).
   * VIX3M is missing for the 1999 and 2000 eves.

### Added after pre-registration (exploratory; none of these is a test)
* **P4 control group.** Fixed by date rule before any P4 value was computed: the eve of every ≥10% decline from a record close since 1999 that stopped short of 20%. Those are 1999-07-16, 2015-05-21, 2018-01-26, 2018-09-20 and 2025-02-19.
  * Disclosure: I had already seen the DFII10 and CAPE tables when I set the rule, but the rule uses dates only.
  * Without a control group, "rhymes with a bear eve" means nothing if correction eves rhyme just as well.
  * "Rhymes" = the same third of the indicator's 1999-2026 monthly distribution.
  * AUC = the chance a bear eve reads higher than a correction eve (0.5 = no separation).
* **S1.** Sensitivity of the P2 threshold (on the trailing fit today reads −1.68, just short of −1.75), with base rates for the same outcomes.
* **X1.** Base rate from today's depth: every decline from a record that reached −5.95%, listed individually.

### P1. Retest: robust
| | long channel (2009 / 2010 / 2012 starts; LAD 2009) | short channel (2022-10 / 2023-01 / 2023-06 starts; LAD 2023) | trailing 3y / 15y | vs lower envelope (2009 / 2023) |
|---|---|---|---|---|
| SPX | +0.69 / +0.77 / +0.75; LAD +0.63 | **-2.04 / -1.99 / -1.81; LAD -2.07** | -1.68 / +0.73 | +14.1% / +0.6% |
| QQQ | -0.45 / -0.40 / -0.48; LAD -0.45 | **-2.71 / -2.67 / -2.63; LAD -2.69** | -2.49 / -0.49 | +6.4% / -4.2% |
| SMH | +1.37 / +1.28 / +1.00; LAD +1.71 | **-1.69 / -1.61 / -1.50; LAD -1.51** | -1.45 / +1.02 | +61.2% / +0.9% |
| RSP | -0.18 / +0.04 / +0.31; LAD +0.09 | **+0.20 / +0.14 / +0.01; LAD +0.16** | +0.11 / +0.25 | +4.9% / +7.5% |

* **S&P:** sits on the floor of its 2023 channel by every method (−1.81 to −2.07σ; 0.6% above the 2023 lower envelope). The 2009 channel is intact (about +0.7σ).
* **QQQ:** below its 2023 channel (4.2% under the envelope).
* **SMH:** −1.5 to −1.7σ short-term, but +1.0 to +1.7σ on the long channel.
* **Equal-weight (RSP):** mid-channel on everything (within ±0.31).
* **No look-ahead:** the trailing 3-year fit puts the S&P at −1.68σ, a little milder than the in-sample −1.95.

### P2. History of "short channel broken, long channel intact": H-P2 FAILS
* **Bears:** 7 of 20 finished events (35%) became ≥20% bears within 252 sessions, against my ≤30%.
* **Base rate:** 26.7% of all days were followed by a ≥20% bear within 252 sessions.
* **Narrow vs broad:** narrow 1 of 1 (2022-04-26), broad 5 of 17. The second half of H-P2 fails too, though n = 1 says nothing.
* **10% corrections:** 20 of 20 finished events had a ≥10% drawdown within 252 sessions. For comparison:
  * 67.8% of all days;
  * 67.1% of days that were 2.5-10% off their 252-session high (n 1039). Those same days became bears 17.9% of the time.
* **Events less than 10% down on the signal day:** all 10 finished ones went on to −10% or worse. Six of them were already −9% or worse on the day.
* **Today:** -1.68σ short, +0.73σ long. **Today does not qualify under the pre-registered rule.**

| event | short z | long z | avg-stock z | down on the day | max fall next 252 | fwd 63 / 126 / 252 | sessions to new high | finished |
|---|---|---|---|---|---|---|---|---|
| 1965-05-27 | -1.85 | -0.45 | — | -2.7% | **-11.1%** | -0.8% / +4.8% / -0.9% | 84 | yes |
| 1966-02-24 | -1.88 | -0.61 | — | -3.4% | **-22.2%** | -4.2% / -13.0% / -3.8% | 300 | yes |
| 1973-03-22 | -1.85 | -0.58 | -2.20 | -9.5% | **-24.6%** | -5.2% / -1.9% / -10.6% | 1850 | yes |
| 1977-08-08 | -1.77 | -0.48 | -1.73 | -9.1% | **-19.4%** | -6.5% / -8.7% / +5.7% | 511 | yes |
| 1980-03-26 | -1.75 | -0.18 | -1.96 | -16.7% | **-17.1%** | +18.3% / +32.1% / +38.1% | 75 | yes |
| 1981-08-24 | -1.75 | +1.15 | -1.68 | -10.7% | **-27.1%** | -3.0% / -11.1% / -7.5% | 303 | yes |
| 1984-07-24 | -1.82 | +0.63 | -1.78 | -14.4% | **-13.8%** | +13.2% / +18.7% / +30.3% | 125 | yes |
| 1987-10-15 | -1.85 | +1.80 | -2.08 | -11.5% | **-33.5%** | -15.4% / -12.9% / -7.7% | 449 | yes |
| 1990-08-22 | -1.93 | -0.41 | -1.97 | -14.2% | **-19.9%** | -0.4% / +15.3% / +23.4% | 121 | yes |
| 1997-04-11 | -2.08 | +0.57 | -1.96 | -9.6% | **-10.8%** | +24.3% / +31.6% / +50.4% | 16 | yes |
| 1997-10-27 | -1.90 | +1.59 | -1.64 | -10.8% | **-19.3%** | +11.5% / +24.8% / +21.5% | 28 | yes |
| 1998-08-04 | -1.78 | +1.90 | -2.49 | -9.7% | **-19.3%** | +3.7% / +18.6% / +21.8% | 78 | yes |
| 1999-08-10 | -1.86 | +1.61 | -1.79 | -9.7% | **-12.1%** | +7.5% / +12.5% / +15.7% | 69 | yes |
| 2007-08-15 | -1.92 | -0.62 | -2.90 | -9.4% | **-22.4%** | +5.3% / -4.1% / -8.1% | 36 | yes |
| 2011-08-22 | -1.76 | -0.55 | -2.00 | -17.6% | **-19.4%** | +8.2% / +20.8% / +25.7% | 128 | yes |
| 2014-10-07 | -1.83 | +1.66 | -2.13 | -3.8% | **-12.4%** | +4.7% / +8.1% / +3.1% | 18 | yes |
| 2018-10-11 | -2.36 | +0.89 | -3.06 | -6.9% | **-19.8%** | -5.3% / +6.5% / +8.7% | 131 | yes |
| 2020-03-09 | -3.52 | -0.04 | -4.82 | -18.9% | **-33.9%** | +17.7% / +24.8% / +41.1% | 113 | yes |
| 2022-04-26 | -2.01 | +0.40 | -0.95 | -13.0% | **-25.4%** | -3.6% / -7.6% / -1.0% | 435 | yes |
| 2025-04-03 | -1.77 | -0.58 | -1.31 | -12.2% | **-18.9%** | +15.4% / +24.4% / +22.6% | 58 | yes |
| 2026-03-13 | -1.80 | +0.58 | -0.87 | -5.0% | **-9.1%** | +12.1% / +14.9% / — | 22 | no (open) |

**S1 (threshold sensitivity, exploratory):**

| threshold | events | finished | ≥10% | ≥20% | today qualifies |
|---|---|---|---|---|---|
| -1.5 | 22 | 20 | 19 | 6 | yes |
| -1.65 | 23 | 21 | 20 | 7 | yes |
| -1.75 | 21 | 20 | 20 | 7 | no |
| -2.0 | 18 | 17 | 17 | 7 | no |

The bear share stays at 30-41% for every threshold (6-7 bears among 17-21 finished events). At −1.65, where today qualifies, the only event that stopped above −10% within a year was 2006-06-09 (−7.7%).

### P3. Calendar: H-P3 FAILS (the owner's observation is not supported)
* **Pre-registered rule (declines of ≥20% from a record close, 1928-2026):** 12 bear markets.
  * 3 began in Nov-Dec: 1961-12-12, 1968-11-29, 1980-11-28. That is 25% against 17% by chance, so Nov-Dec starts are not rarer (one-sided binomial p = 0.87).
  * 5 of 12 began in Jan-Jun.
  * Peak months: Jan 1973, 2022; Feb 1966, 2020; Mar 2000; Aug 1956, 1987; Sep 1929; Oct 2007; Nov 1968, 1980; Dec 1961.
* **Calendar spans:** most bears ran across a year-end. Only 1966 (Feb-Oct) and 2022 (Jan-Oct) fit "start of year to end of year".
* **Zigzag sensitivity (first run):** 5 of 27 began in Nov-Dec (p = 0.71). Same verdict.
* **Corrections that began in Sep-Nov, like Oct 6, 2026:**
  * Pre-registered rule (≥10% from a record): 4 of 10 became bears, against 8 of 16 in other months (Fisher p = 0.70).
  * Zigzag: 10 of 36 against 25 of 67 (p = 0.39).
  * The direction matches the owner's intuition, but it is weak and not significant.

### X1. From today's depth (exploratory)
* **All declines:** since 1950, 51 declines from a record reached −5.95% on a close.
  * 27 stopped above −10% (53%).
  * 13 ended between −10% and −20% (25%).
  * 11 became bears (22%).
* **Fast ones:** the 35 that got there at least as fast as now (≤ 22 sessions) split 18 / 10 / 7 the same way.
* **Records set in Oct-Nov:** 9 declines, 6 reached −10%, 3 became bears (1968, 1980, 2007). Small n, but no sign that late-year starts stay shallow.
* **All 51 episodes:** listed in `out/x1_depth.json`.

### P4. Deep-change checklist (descriptive; figure `out/deep_change_checklist.png`)

| gauge | today (record month) / latest | bear eves 2000 / 2007 / 2020 / 2022 | correction eves 1999 / 2015 / Jan-18 / Sep-18 / 2025 | AUC (n) | today rhymes with |
|---|---|---|---|---|---|
| WTI oil y/y (%) | +67.7 / +52.9 | +114.1 / +45.7 / -8.03 / +60.0 | — / -42.0 / +21.3 / +41.0 / -7.40 | 0.81 (4 v 4) | 2000, 2007, 2022 |
| Core CPI y/y (%) | 2.57 (2026-09) / — | 2.45 / 2.16 / 2.37 / 6.05 | 2.08 / 1.75 / 1.89 / 2.20 / 3.14 | 0.80 (4 v 5) | 2000, 2020, 2022 |
| VIX / VIX3M | 0.86 / 1.10 | — / 0.98 / 0.93 / 0.83 | — / 0.84 / 0.82 / 0.85 / 0.88 | 0.75 (3 v 4) | 2022 |
| 2y - fed funds (pp) | 0.86 / 0.70 | 0.68 / -0.79 / -0.25 / 0.90 | 0.56 / 0.49 / 0.62 / 0.82 / -0.12 | 0.45 (4 v 5) | 2000, 2022 |
| 10y real yield, TIPS (%) | 2.78 / 2.64 | — / 2.20 / -0.11 / -0.69 | — / 0.33 / 0.54 / 0.88 / 2.03 | 0.33 (3 v 4) | 2007 |
| 10y - core CPI y/y (pp) | 2.42 (2026-09) / 2.33 | 3.81 / 2.37 / -0.87 / -4.29 | 3.71 / 0.45 / 0.69 / 0.80 / 1.31 | 0.45 (4 v 5) | 2000, 2007 |
| Baa - 10y (pp) | 1.46 / 1.54 | 2.11 / 1.95 / 2.11 / 1.82 | 2.16 / 2.69 / 1.67 / 1.88 / 1.47 | 0.55 (4 v 5) | 2007, 2022 |
| Unemployment - 12-month low (pp) | 0.10 (2026-09) / — | 0.00 / 0.30 / 0.00 / 0.10 | 0.10 / 0.20 / 0.00 / 0.00 / 0.30 | 0.45 (4 v 5) | 2000, 2020, 2022 |
| Shiller CAPE | 40.6 / 38.8 | 43.2 / 27.3 / 30.7 / 36.9 | 43.8 / 26.8 / 33.3 / 32.6 / 37.2 | 0.45 (4 v 5) | 2000, 2020, 2022 |

**Read:**
* **Gauges that leaned bear vs correction.** Only three, in this tiny sample: oil y/y (AUC 0.81), core CPI (0.80) and VIX/VIX3M (0.75).
  * Today is on the bear side of the first two: oil +68% y/y in October (+53% now), core CPI 2.57%.
  * Today is on the calm side of the third at the record (0.86), although the VIX curve is inverted today (1.10).
* **Pressure that rhymes with 2000 and 2022:**
  * hikes priced: 2y 0.86 pp above fed funds in October, 0.70 now;
  * the highest real yield of any eve (TIPS 2.78% in October, 2.64% now; 2007 was 2.20);
  * CAPE 40.6, second only to the 1999-2000 eves.
  * But 2y − fed funds, real yields and CAPE do not separate bear eves from correction eves (AUC 0.33-0.45), so these rhymes carry little weight.
* **No cracks yet:**
  * credit is the calmest of all nine eves (Baa − 10y 1.46 in October, 1.54 now);
  * unemployment is 0.1 pp off its 12-month low.
  * At the eve, the crack gauges did not separate bears from corrections either (AUC 0.45-0.55), so "no cracks yet" does not rule a bear out.

### The owner's question: my judgement (not a test result)
Earlier today I gave 65% (correction within the uptrend) / 30% (full correction via AI) / 5% (2022 route). **Revised:**
* **About 45%: a dip inside the uptrend.** The S&P holds roughly 7,000-7,350 (the 2023 channel floor; SPY's 700-740 put zone) and resumes.
* **About 30%: a full 10-20% correction** (S&P about 6,250-7,000). It breaks the 2023 channel but holds the 2009 one, like 1998, 2018 and 2025.
* **About 25%: a ≥20% bear** (below about 6,250), the 2000/2022-type route: an AI capex unwind with a tight Fed and an oil shock.
* **Why the shallow case was cut:**
  * From −6%, history is about a coin flip to −10% (X1: 24 of 51).
  * This channel setup fell 10%+ within a year in 20 of 20 finished cases, and became a bear in 7 of 20, about twice the rate for similar dips (18%).
  * The two macro gauges that best separated bears from corrections (oil y/y, core CPI) sit on the bear side.
  * The calendar gives no protection.
* **What still argues for the uptrend:**
  * the 2009 channel is intact (+0.7σ);
  * the equal-weight index is mid-channel;
  * credit is calm;
  * jobs have not cracked.
* **Would move me toward the shallow case:**
  * S&P back above about 7,600 with RSP leading;
  * oil y/y falling under about +25%;
  * the 2y back within 0.3 pp of fed funds;
  * the VIX curve back below 0.9.
* **Would move me toward a bear:**
  * closes below SPY 720 (the gap from there to 700 is thin);
  * Baa − 10y above about 1.9 or HY OAS above about 4;
  * unemployment 0.3 pp or more above its 12-month low (Friday's jobs report is the first check);
  * AI capex cuts.

## Addendum (descriptive, after the owner's SMH chart question; not a test)
**Question:** why does the owner's SMH channel leave room to fall when the SPY and QQQ channels look finished?

**Method:** `same_rule.py` → `out/same_rule_lines.png`, `out/same_rule.json`. All three charts use one rule: lines parallel to each 2023 OLS trend, through the 2026 scare low (2026-03-30 close) and through the 2025 crash low (2025-04-08 close).

| | close Nov 5 | line through the 2026 low | line through the 2025 low |
|---|---|---|---|
| S&P | 7,353.73 | 7,076 (−3.8%) | 6,616 (−10.0%) |
| QQQ | 647.05 | 642 (−0.8%) | 597 (−7.8%) |
| SMH | 447.73 | 465 (broken: close is 3.8% below it) | 344 (−23.2%) |

**Read:**
* The owner's SMH lower line matches the line through the 2025 crash low.
* The SPY and QQQ readings ("looks over") match the line through the 2026 low, or the −2σ band.
* Measured by one rule, the three agree:
  * on the 2026 lines, the S&P has about 4% left, QQQ sits on its line and SMH is already through it;
  * on the 2025 lines, all three have room.
* Chips' extra room, about 2.3 times the S&P's, reflects their bigger swings: a trend of +51% a year vs +20%, and a residual SD of 13% vs 4%.
* In both 2025 and 2026, all three bottomed on the same day (Apr 8, 2025 and Mar 30, 2026).

**SMH one-day drops of 9.5% or worse since 2000 (5 before today):**
* Three came within a week of the low: 2002-10-16, 2020-03-12 and 2020-03-16.
* Two were followed by much lower lows: 2002-07-25 (−31% within 60 sessions) and 2025-01-27 (−24% by 2025-04-08).
