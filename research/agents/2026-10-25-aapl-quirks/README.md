# Why does AAPL decouple? AAPL's quirks since 2020

* **Owner, 2026-10-25:** "Ok let's try explain aapl… there is definitely something happening here." Then: "I think since 2020 it has its own quirks. Let's study it."
* **Builds on:** [2026-10-25-aapl-decoupling](../2026-10-25-aapl-decoupling/), which found that AAPL decoupling does not reliably predict S&P tops.
* **The question here is different:** not what the decoupling predicts, but **what makes AAPL decouple**.

## Setup (pre-registered before any test is computed)
* **Window:** primary 2020-01-02 to 2026-10-23. 2011–2019 is reported alongside as a contrast, to check the claim that this is a 2020s quirk.
* **Market for a stock X:** the S&P with X removed, `r_m = (r_SPX − w·r_X)/(1 − w)`, using approximate fixed weights:

  | Stock | AAPL | MSFT | NVDA | AMZN | GOOGL | META |
  |---|---|---|---|---|---|---|
  | Weight w | 0.065 | 0.06 | 0.05 | 0.035 | 0.035 | 0.025 |

* **Returns, residual, alarm:**
  * Returns are daily log close-to-close.
  * Residual `e = r_X − β·r_m`, with β from the trailing 252 sessions, known the day before.
  * Alarm = the 20-day correlation with the market in the bottom fifth of its trailing 252 days (as before).
* **Peers:** MSFT, AMZN, GOOGL, META, NVDA. A "quirk" means AAPL differs from them.
* **Data:**
  * Yahoo daily: ^GSPC, the mega-caps, SMH, SPY, XLK, XLP, USMV, MTUM.
  * Alpha Vantage earnings dates. All reports are post-market, so the reaction day is the next session.
* **Context, not evidence:**
  * As of Oct 22–23, 2026, AAPL is up about 27% this year against about 13% for the S&P.
  * It has reportedly just overtaken NVDA as the most valuable company.
  * The foldable iPhone went on sale this week, and earnings are expected Nov 2.

## Part 0: descriptive quirk scan (no verdicts)
| # | Measure, AAPL vs peers, 2020–2026 (and AAPL 2011–2019) |
|---|---|
| S1 | Beta and correlation with the market (ex-self) |
| S2 | Downside beta (market-down days) vs upside beta |
| S3 | Share of return earned overnight vs intraday |
| S4 | Lag-1 autocorrelation of the residual |
| S5 | Share of days with 20-day correlation below 0.3 |
| S6 | Mean residual on the market's 20 worst days |

Anatomy of decoupling: `log corr = log β + log σ_m − log σ_X`. For each alarm day, how much of the drop from the stock's 252-day median correlation comes from β falling, market volatility falling, or the stock's own volatility rising?

## Theories and tests (2020-01-02 to 2026-10-23; each judged on its own)
**T1, its own news calendar.** Decoupling is mostly earnings.
* Statistic: P(an earnings reaction day inside the 20-day window | alarm) − P(… | no alarm).
* Null: circular shift of the alarm, 2,000 draws.
* Pass: p < 0.05.

**T2, AI-trade rotation.** Since 2023 the index has been led by an AI/semis factor that AAPL does not share; money rotates between the AI trade and AAPL. With `f = r_SMH − r_SPY`:
* **(a)** On 2023-01-03 to 2026-10-23, AAPL's residual loading on f is below the average loading of the non-semis peers (MSFT, AMZN, GOOGL, META). 20-day block bootstrap p < 0.05.
* **(b)** On 2020–2026, AAPL's 20-day correlation is lower when the S&P (ex-AAPL) moves with f, i.e. when its 20-day correlation with f is high. Spearman < 0, circular-shift p < 0.05.
* Pass: (a) and (b).

**T3, defensive asymmetry.** AAPL behaves like a quality/defensive name in sell-offs.
* Prediction: AAPL downside beta − upside beta < 0 (block bootstrap p < 0.05), and more negative than the peer average (p < 0.05).
* Pass: both.

**T4, buyback bid.** Apple's large repurchases support it, except during blackout.
* Blackout: from 14 calendar days before each fiscal quarter end (last Saturday of Dec/Mar/Jun/Sep) through the earnings reaction day.
* Prediction: downside beta in open windows < downside beta in blackout windows.
* Bootstrap by resampling quarters; pass at p < 0.05.

**T5, forced index flows** (the forced-flow law, applied to AAPL). AAPL is about 7% of the S&P, about 9% of QQQ and a capped weight in XLK. Index rebalances fall on quad-witching days.
* Prediction: AAPL residuals made on quad-witching days are given back more over the next 5 sessions. Regress `e(t+1..t+5)` on `e(t)` with a `e(t) × quad-witching` interaction: coefficient d < 0, block bootstrap p < 0.05.
* Month-end is reported as a secondary.

**"Since 2020" check, descriptive:** for each theory that passes, is the effect larger in 2020–2026 than in 2011–2019?

**Current episode, descriptive (Sep 15 to Oct 23, 2026):** the anatomy, the residual against f, and AAPL vs SMH and the S&P.
