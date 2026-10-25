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
