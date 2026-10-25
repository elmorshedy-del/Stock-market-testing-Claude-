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

## Round 1 results (`decoupling.py`; `out/decoupling.json`, `out/daily.csv`)
| Test | Result | Verdict |
|---|---|---|
| **H1, 1990–2022 pooled (primary)** (44 tops) | 23.2% vs 23.0%, difference +0.2 points, p 0.48 | **fail** |
| H1, 1990–2010 (28 tops) | 19% vs 25%, −6 points | no signal, as mechanism (a) predicted |
| H1, 2011–2022 (16 tops, out of sample) | **30% vs 20%, +10 points, p 0.098** | positive, not significant |
| discovery channel 2022–2026 (6 tops) | 40% vs 13%, +27 points, p 0.027 | (in sample) |
| H2 other mega-caps, 2013–2026 | MSFT +4, AMZN +4, GOOGL +5, META +10, NVDA +5 points (none significant); AAPL +11 (p 0.039); mega-cap average +7 (p 0.16) | **fail** (5 of 5 positive, but the average p is 0.16) |
| **H3 not the earnings jump**, 2011–2026 | drop-2 version 34% vs 18%, +16 points, **p 0.0015** (plain +15, p 0.006; rank correlation +10, p 0.066) | **pass** |
| **H4 beyond dispersion**, 2011–2026 | AAPL coefficient +0.89, **p 0.001**, with the dispersion alarm in the model (dispersion −0.14). Dispersion alone +5 points, p 0.20. The two alarms correlate 0.48 | **pass** |

* **Pre-registered overall verdict: "channel coincidence,"** because H1's pooled primary fails.
* **Diagnosis:**
  * The pooled test mixes an era in which the mechanism says nothing should happen (AAPL was a small weight in 1990–2010) with the era in which it should. The failure is concentrated in the earlier era, and the mechanism-era out-of-sample is positive (+10 points) but not significant (16 tops).
  * The signal is not earnings jumps, and it is not general dispersion.
  * Other mega-caps lean the same way, weakly.
* **Status:** a plausible, partly supported lead that has **not** passed a strict out-of-sample test.

## Amendment 1 (round 2): is it a "narrowing rally"? Pre-registered before running.
* **The mechanism says the warning is about the index rising without its biggest name.** So its power should be concentrated on alarm days when the S&P's 20-day return is > 0 **and** AAPL's 20-day return is below the S&P's (AAPL lagging while the index rises).
* **Test (2011–2022 only, so the discovery period stays out):**
  * P(top within 30 | narrowing-rally alarm) − P(top within 30 | no alarm), circular-shift p;
  * the same for the other alarm days.
* **Pass:** the narrowing-rally difference > 0 with p < 0.05, **and** it is larger than the other-alarm difference.

## Amendment 1 results (`round2.py`; `out/round2.json`): **fail**, and the mechanism was the wrong way round
| 2011–2022 | P(top within 30) | Difference vs no-alarm days (19.8%) | p |
|---|---|---|---|
| Narrowing-rally alarm days (S&P up, AAPL lagging), 112 days | 22.3% | +2.5 points | 0.39 |
| All other alarm days, 409 days | 32.0% | **+12.2 points** | 0.057 |

* "The index rising without its biggest name" is **not** where the signal sits.

### Post hoc diagnosis (`posthoc2.py`; `out/posthoc2.json`; descriptive, no test)
| Alarm days, 2011–2022, split by cell | Alarm days | P(top within 30): alarm | P(top within 30): no alarm, same cell |
|---|---|---|---|
| S&P up, AAPL lags | 112 | 22% | 20% |
| **S&P up, AAPL leads** | 367 | **34%** | 26% |
| S&P down, AAPL holds up | 26 | 23% | 12% |
| S&P down, AAPL falls more | 16 | 0% | 5% |

* **Possible confound:** alarm days sit closer to the S&P's 252-day high (median −0.45%, vs −1.24% on other days).
* Tops are defined **at** 252-day highs, so being near the high mechanically raises P(top within 30).
* Low single-stock correlation is also typical of calm, grinding markets near highs.
* The round-1 differences may therefore be a "near the high" artifact. This must be controlled before the signal means anything.

## Amendment 2 (round 3): the "near the high" control, and a fresh out-of-sample test abroad. Pre-registered before computing or downloading anything.
* **Statistic: the distance-adjusted difference.**
  * Cut distance to the 252-day high into quintiles (edges from that market's full window).
  * Within each quintile, compute P(top within 30 | alarm) − P(top within 30 | no alarm).
  * Average across quintiles, weighted by alarm days; use only quintiles that have both alarm and no-alarm days.
* **R3a, US control (diagnostic; the data have been used before):**
  * the distance-adjusted difference for AAPL on 2011-01-03 to 2026-08-14;
  * circular-shift p, 2,000 draws;
  * pass at p < 0.05.
  * Also reported: 2011–2022 alone, the discovery channel, and a logistic regression `ahead ~ AAPL alarm + distance quintile dummies + dispersion alarm`.
* **R3b, fresh out-of-sample:** does "the largest stock decoupling from its own index" warn of that index's tops in other markets?
  * Windows run from 2000-01-01 (or the first date with 252 days of both series) to 2026-08-14.
  * Same definitions throughout: 20-day correlation, alarm at the bottom fifth of the trailing 252 days, a top at a 252-day high followed by a close ≥5% below it, a 30-session horizon, and days inside a decline excluded.
  * Markets and names, fixed now (the largest or longest-largest index weight):

    | Index | Name |
    |---|---|
    | ^KS11 | Samsung 005930.KS |
    | ^TWII | TSMC 2330.TW |
    | ^SSMI | Nestlé NESN.SW |
    | ^AEX | ASML ASML.AS |
    | ^GDAXI | SAP SAP.DE |
    | ^FCHI | LVMH MC.PA |
    | ^HSI | Tencent 0700.HK |
    | ^NSEI | Reliance RELIANCE.NS |
    | ^AXJO | CBA CBA.AX |
    | ^GSPTSE | RBC RY.TO |
    | ^N225 | Fast Retailing 9983.T |
    | ^FTSE | AstraZeneca AZN.L |

  * Any pair that Yahoo cannot serve is dropped and listed; no replacements.
  * **Primary:** the equal-weight average across markets of the distance-adjusted difference > 0, with p < 0.05.
  * **Null:** one common circular shift of every market's alarm on a shared weekday calendar, 2,000 draws. This keeps the cross-market clustering of tops.
  * **Secondary:** the count of markets with a positive difference; the plain (unadjusted) average.
* **Overall rule:**
  * R3b pass → "**the decoupling warning is real and general**";
  * R3b fail and R3a pass → "**US/AAPL-only, unconfirmed**";
  * R3a fail and R3b fail → "**near-the-high artifact**".

## Amendment 2 results (`round3.py`; `out/r3a.json`, `out/r3b.json`, `out/r3b_markets.csv`, `out/r3_overall.json`)
**R3a, US near-the-high control: pass (narrowly), but the pass comes from the discovery era.**

| Window | Distance-adjusted difference | Raw difference | p (shift) |
|---|---|---|---|
| **2011–2026 (R3a primary)** | **+10.1 points** | +15.3 | **0.044** |
| 2011–2022 (out of sample) | +4.6 | +10.1 | 0.26 |
| channel 2022–2026 (discovery) | +22.9 | +27.1 | 0.031 |
| 1990–2022 | −2.8 | +0.2 | 0.72 |
| 1990–2010 | −7.5 | −5.9 | 0.90 |

* Logistic regression, 2011–2026: `ahead ~ AAPL alarm + distance quintiles + dispersion alarm`. AAPL coefficient +0.74, block-bootstrap p 0.0085.
* About half the raw out-of-sample edge was the "near the high" effect.

**R3b, 12 other markets (largest stock vs its own index, 2000–2026, 348 tops): fail.**
* Average distance-adjusted difference **−3.2 points**, p 0.98 (common shift).
* 5 of 12 markets positive; plain average −0.7 points (p 0.67).
* No market has p < 0.05 in the positive direction. Samsung/KOSPI is the most negative (−17 points).
* None of the 12 pairs was dropped.

**Pre-registered overall verdict (round 3): "US/AAPL-only, unconfirmed."**

### Post hoc (`posthoc3.py`; `out/posthoc3.json`; descriptive): today's question
**Setup:** the S&P is 2.5% below its 252-day high with the AAPL alarm on. How often does a 1.5–3.5% dip reach −5% before a new high?

| Window | Alarm on | Alarm off |
|---|---|---|
| 1990–2026 | 36% (182 episodes) | 39% (498) |
| 2011–2026 | 45% (82) | 39% (224) |
| channel | 36% (29) | 33% (49) |

* No material difference: the base rate is about 40% either way.

## Verdict across all three rounds
1. **What survives:**
   * In the US since 2011, AAPL's decoupling has gone with more S&P tops.
   * This is not earnings jumps (H3) and not general dispersion (H4).
   * It partly survives the near-the-high control.
2. **What fails:**
   * The pre-registered out-of-sample test (H1, 1990–2022). After the near-the-high control, 2011–2022 is +4.6 points, p 0.26.
   * The proposed mechanism ("a narrowing rally": round 2).
   * Generalization: "the largest stock decoupling" does nothing in 12 other markets.
3. **Reading:**
   * Most of the evidence comes from the channel in which it was noticed (2022–2026).
   * There is no mechanism that survived testing, and no out-of-sample confirmation.
   * By the protocol this is an **unconfirmed lead, most likely a feature of this one regime, not a law**.
4. **Today (Oct 23):**
   * AAPL's correlation is −0.17 (drop-2 −0.14): the alarm is on and robust.
   * The S&P is −2.5% from its high, and the alarm did not change the odds that a dip like this extends to −5%.
   * Treat it as context, not a trade signal.
