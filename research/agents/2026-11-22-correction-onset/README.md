# Discovery pass 3: predicting the start of a correction inside the post-2009 bull market

**Protocol committed before any result.** System: [DISCOVERY.md](../DISCOVERY.md). **Date:** 2026-11-22.
**Owner's correction of my question:** "this was supposed to be a system that predicts corrections within the rising channel from 2008 bottom. If it works it could have predicted early October to now drop after this year's high that was a top."
**Why passes 1–2 missed it:**
* They asked a different question: danger at any time, 1990–2019.
* Their one predictor, current stress, works once a fall is under way. Corrections start from calm highs.

## The question
* **Weeks studied:** Friday closes from 2011-06 (when the gamma and dark-pool data begin) to the latest week with a complete outcome, **only weeks when the S&P is within 3% of its 52-week high**. These are the moments when a top is possible.
* **Primary target C10:** the S&P falls 10% or more from that Friday close within the next 13 weeks.
* **Secondary target C7:** a fall of 7% or more within 8 weeks. It catches shallower corrections such as July 2024 and January 2026.
* **Benchmark:** the base rate among near-high weeks.

## Candidate variables (fixed now; 16; each with its reason)
| # | Variable | Why it might lead a correction |
|---|---|---|
| 1 | Stretch: distance above the 200-day average ÷ 63-day volatility | overextended rallies |
| 2 | Rally speed: 13-week return ÷ its normal size | too far, too fast |
| 3 | 10-year yield, 8-week change | discount-rate shock (**hindsight risk: I know it preceded October 2026**) |
| 4 | Stock–bond correlation, 63 days | stocks and bonds falling together; diversifiers fail |
| 5 | VIX level | calm before the storm, or stress |
| 6 | VIX 20-day change | volatility rising while price sits at highs |
| 7 | VVIX (volatility of VIX) | demand for crash protection on volatility |
| 8 | SKEW index | demand for tail puts |
| 9 | Credit lag: HYG minus SPY, 8-week return | credit weakening before stocks |
| 10 | Breadth: equal-weight vs cap-weight S&P (RSP/SPY), 13-week change | narrowing leadership |
| 11 | Dealer gamma (GEX), percentile vs its past year | low gamma: amplified moves (our robust result) |
| 12 | GEX percentile, 4-week change | gamma draining away |
| 13 | DIX (dark-pool buying), 5-day average | sell-side absorption |
| 14 | Dollar (DXY), 8-week change | dollar funding squeeze |
| 15 | Gold vs S&P correlation, 63 days | common-holder (leveraged) crowding; **hindsight risk** |
| 16 | Excess earnings yield (1/CAPE − real 10-year) | valuation stretched against rates |

All are point-in-time at the Friday close; CAPE and CPI are lagged one month.

## Method (fixed now)
* **Lens 1, one variable at a time:** AUC of each variable for each target (0.5 = no information).
  * p-value from 1,000 circular shifts of the outcome series (minimum shift 26 weeks), which keeps the clustering of event weeks.
  * Benjamini–Hochberg at q = 0.10 over 16 × 2 = 32 tests.
  * **Episode consistency:** in how many of the correction episodes was the variable, in the weeks before the top, on the side the AUC says, compared with the same year's near-high weeks that were not followed by a correction?
* **Lens 2, combined:** L2 logistic regression (C = 0.5, standardized) on the variables that pass lens 1.
  * If none pass: on the 4 with the highest training AUC, chosen inside each fold, labelled as weak.
  * Two evaluations:
    * (a) leave-one-calendar-year-out, purged of the 13 weeks on each side;
    * (b) walk-forward: train on everything before each test year (minus 13 weeks), test years 2015 to 2026.
  * Metrics: AUC; Brier skill against the base rate.
  * Null: 200 circular shifts of the outcome, with the whole lens rerun.
* **Lens 3, the timeline:** the walk-forward probability, week by week, 2015 to now, with every correction marked.
  * Specifically the value in August–September 2026, before the 6 October top.
  * Alarm threshold: the training 80th percentile in each fold. Reported: hits, misses and false alarms per year.

## Honesty notes, written before the run
* This uses 2020–2026. The lockbox sealed in pass 1 (for the weekly cross-asset question) is therefore spent for these variables; this pass's confirmation must come from the forward log.
* My choice of variables 3 and 15 is contaminated by knowing what happened in 2026. They are reported separately.
* Corrections from near highs since mid-2011 number roughly 10 to 15. That is small; wide uncertainty is expected.

## Results
To be appended below this line after the run, without editing anything above.

## Status: interrupted by the owner (2026-11-22), superseded by `../2026-11-22-vulnerability/`
* Partial lens 1 only (`out/lens1.csv`), with 2026 outcomes labelled where the fall had already happened.
* Breadth (RSP/SPY, 13-week change) was the strongest variable: AUC 0.26 for 10%+ corrections (p 0.006; right in 8 of 9 episodes), but it missed the multiple-testing bar (0.003).
* The combined lens did not finish. Nothing here is used as evidence.
