# Who buys AAPL during the day? And a last-hour exploration

* **Owner, 2026-10-25:** "I like this last hour stuff btw… So while u testing aapl see if u find anything interesting in the data."
* **Builds on:** [2026-10-25-aapl-quirks](../2026-10-25-aapl-quirks/). Since 2020 AAPL earns +30%/yr more intraday than overnight, and Apple's buyback windows no longer explain it. Also on [forced-flow](../2026-10-24-forced-flow/), whose A2 found no last-half-hour momentum in SPY (2023–2026).

## Data
* **Hourly bars:** Yahoo 60-minute bars for 51 tickers, 2023-11-27 to 2026-10-23 (730 sessions). Bars start at :30, and the 15:30 bar ends at the official close, so **it includes the closing auction**. Early-close days are dropped.
* **5-minute bars:** Yahoo, 60 days, for AAPL, MSFT, NVDA, SPY and TSLA. Descriptive use only.
* **Daily segments:**

  | Segment | From | To |
  |---|---|---|
  | overnight | previous official close | 09:30 open |
  | first hour | 09:30 | 10:30 |
  | midday | 10:30 | 15:30 |
  | last half hour | 15:30 | the official close |

* **Peers:** MSFT, AMZN, GOOGL, META, NVDA.
* **Dealer gamma:** daily `gex_classic` for SPY, QQQ, TSLA, MSFT, NVDA and MU (`research/microstructure/out`, through 2026-10-09), taken from the day before.

## Part A, who buys AAPL during the day (pre-registered; all 730 sessions)
**A0, does the quirk hold in this window?** AAPL (intraday − overnight) minus the peer average. 20-day block bootstrap.

**A1, where does it sit?** For each segment: the AAPL mean minus the peer mean, annualized. 20-day block bootstrap, two-sided p.

| Hypothesis | Predicted location of AAPL's excess | Extra test |
|---|---|---|
| **H-gap:** dip buyers after overnight gap-downs | the first hour | **A2:** the first-hour-on-overnight slope is more negative for AAPL than the peer average (p < 0.05) |
| **H-close:** closing flows (passive and index money at the close) push the close up, and it gives back overnight | the last half hour | **A3:** the next-overnight-on-last-half-hour slope is more negative for AAPL than the peer average (p < 0.05) |
| **H-spread:** steady day-long accumulation (VWAP-style) | midday, with neither the first hour nor the last half hour significant | none |

* **Verdict rule:** a hypothesis is supported if its segment's AAPL excess is > 0 with p < 0.05 **and** its extra test passes. H-spread has no extra test.

## Part B, last-hour exploration (owner's request; explore, then confirm on held-out data)
* **Split:**
  * the first 365 sessions (2023-11-27 to about 2025-05) are for **exploration**;
  * the last 365 are **held out** and not examined until the confirmations below are written down and pushed.
* **Fixed menu, scanned on the exploration half** (per ticker and pooled):

  | # | Question |
  |---|---|
  | B1 | Does the open-to-15:30 return predict the last half hour (intraday momentum or reversal)? |
  | B2 | Does the first hour predict the last half hour? |
  | B3 | Does the overnight gap predict the last half hour? |
  | B4 | Does the last half hour predict the next overnight return (closing-pressure reversal)? |
  | B5 | Mean last-half-hour return by weekday, month end, monthly OPEX Friday, quad witching, and the day before a holiday |
  | B6 | Abnormal last-bar volume share vs the last-half-hour return and the next overnight return |
  | B7 | On big market days (SPY at 15:30 more than ±1% from the open), does the last half hour continue or reverse? |
  | B8 | Gamma-conditioned: is the B1 slope different when dealer gamma is below its trailing-252 median? |

  Anything else noticed along the way is flagged as exploratory.
* **Confirmation:**
  * Carry forward **at most 5 findings**, chosen on the exploration half, each with a stated sign.
  * They are written into this README and pushed **before** the held-out half is computed.
  * A finding is confirmed if, on the held-out half, it has the same sign and a Holm-corrected p < 0.05 across the carried findings, using the same statistic and a 20-day block bootstrap.

## Part A results (`part_a.py`; `out/part_a.json`; 722 full sessions)
| Test | Result |
|---|---|
| A0, is the quirk present? | AAPL intraday − overnight **+22%/yr**; peers MSFT −3, AMZN −21, GOOGL −1, META −27, NVDA −66. AAPL minus peers +46, **p 0.006** ✅ |
| A1, where it sits (AAPL minus peers, %/yr) | **overnight −27 (p 0.02); first hour +24 (p 0.014)**; midday −5 (p 0.34); last half hour +0.5 (p 0.94) |
| A2, first hour vs gap (H-gap test) | AAPL −0.10 vs peers about −0.03; difference −0.08, p 0.075 (not significant) |
| A3, next overnight vs last half hour (H-close test) | AAPL −0.08 vs peers −0.17; wrong direction (p 0.62) |

* **By the rule, no hypothesis is supported:**
  * H-gap has its segment but its extra test misses (p 0.075);
  * H-close has neither;
  * H-spread does not apply, because the first hour is significant.
* **Diagnosis:**
  * AAPL's "intraday" premium is a **first-hour** effect. AAPL opens cheap: about 27%/yr less overnight than the peers. It is bought back within the first hour (+24%/yr).
  * Overnight plus the first hour together, AAPL (+19) ≈ peers (+22).
  * So the quirk is **where** the gain lands: AAPL's opening print is depressed and recovers by 10:30. **It is not the close and not closing flows.**
  * It does not depend much on the size of the gap (A2), so it looks less like dip-buying after bad news and more like a systematic weak open.

## Part B exploration results (first 365 sessions, 2023-11-27 to 2025-05-15; `explore.py`; `out/explore.json`)
| # | Result |
|---|---|
| B1 open-to-15:30 → last half hour | ≈ 0 (pooled t 0.2). No intraday momentum, as A2 found in forced-flow |
| **B2 first hour → last half hour** | **positive**: pooled stocks slope +0.022 (t 1.96); 71% of stocks positive; SPY +0.066, QQQ +0.058, XLK +0.073, SMH +0.061 |
| B3 overnight → last half hour | pooled ≈ 0; **AAPL is the most negative of 51 (−0.074)** |
| B4 last half hour → next overnight | nothing pooled (t −0.5) |
| **B5 calendar** | **month end: stocks +17 bp (t 2.0), SPY +14 bp (t 1.4), 19 days.** Weekdays, OPEX, quad witching and pre-holiday show nothing |
| B6 abnormal closing volume | nothing (corr 0.04 / 0.01) |
| B7 big SPY days | slight last-half-hour reversal (t < 0.6) |
| B8 gamma | no consistent pattern across the 6 tickers |
| **Extra: (first hour − overnight) by ticker** | a clear split. **Semis and AI names gap up overnight and fade in the first hour:** AVGO −38, MU −34, NVDA −33, SMH −25, ORCL −24 bp/day. **AAPL (+18), T (+21), UNH, BAC, PG, MMM gap down and recover in the first hour.** The overnight/first-hour split lines up with the AI trade, and AAPL sits on the anti-AI side again |

### Carried forward for confirmation on the held-out 365 sessions (signs fixed now; Holm across these 5)
| # | Finding | Statistic and test |
|---|---|---|
| F1 | The first hour predicts the last half hour | ticker-demeaned pooled slope over the 45 stocks > 0; day-block bootstrap, one-sided |
| F2 | The month-end last half hour is positive | mean of the stock-average last-half-hour return on month-end days > 0; bootstrap over those days, one-sided |
| F3 | AAPL's overnight gap predicts its last half hour negatively | slope < 0; day-block bootstrap, one-sided |
| F4 | A stock's (first hour − overnight) signature is persistent | Spearman across the 51 tickers of the per-ticker mean, exploration vs held-out, > 0; permutation of ticker labels |
| F5 | Semis gap up and fade | mean (first hour − overnight) of the semis (NVDA, AVGO, AMD, MU, AMAT, QCOM, TXN, INTC, SMH; picked by industry, not by rank) minus the rest < 0; day-block bootstrap, one-sided |

* **Contamination note:** Part A used all 730 sessions for the segment means of AAPL and its 5 peers (6 of the 51 tickers in F4/F5) and for the AAPL first-hour slope. F3's AAPL last-half-hour slope was not computed on the held-out half.
