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

## Round 1 results (`quirks.py`; `out/quirks.json`, `out/daily.csv`)
**Bug fixed before reporting:** quarters not yet reported (Sep 2026) had been left out of the blackout calendar. They now run to the last day of data. T4's verdict is unchanged.

| Theory | Result | Verdict |
|---|---|---|
| T1 earnings calendar | 2020–2026: alarm windows contain earnings 31% vs 32% of the time (p 0.44). **2011–2019: 63% vs 24% (p < 0.001)** | fail. Decoupling *used to be* an earnings event; since 2020 it is not |
| T2 AI-trade rotation | (a) since 2023, AAPL's residual loads **−0.12** on SMH−SPY vs about −0.03 for MSFT/AMZN/GOOGL/META (difference −0.09, **p 0.015**); 2011–2022 it was +0.22, above peers. (b) AI leadership does not line up with AAPL's coupling over time (Spearman +0.05, p 0.55) | fail (only (a) passes). Since 2023 AAPL is the mega-cap that is short the AI trade, but that does not explain *when* it decouples |
| T3 defensive asymmetry | down − up beta −0.03 (p 0.37); vs peers −0.06 (p 0.20) | fail |
| T4 buyback windows | downside beta open 1.15 vs blackout 1.12 (p 0.62) | fail |
| T5 forced index flows (quad witching) | d −0.21, p 0.41 (27 days). Month end +0.08 | fail |

### Part 0 scan (descriptive)
| 2020–2026 | AAPL | MSFT | NVDA | AMZN | GOOGL | META | AAPL 2011–19 |
|---|---|---|---|---|---|---|---|
| Beta / corr vs market ex-self | 1.09 / 0.70 | 1.08 / 0.72 | 1.66 / 0.63 | 1.07 / 0.61 | 1.09 / 0.68 | 1.27 / 0.57 | 0.88 / 0.49 |
| **Overnight / intraday log return, %** | **−24 / +180** | +66 / +55 | +274 / +84 | +119 / −20 | +38 / +119 | +39 / +75 | +175 / +10 |
| Residual lag-1 autocorrelation | **0.081** | 0.026 | −0.048 | 0.026 | 0.034 | 0.026 | 0.048 |
| Share of days with corr < 0.3 | 16% | 12% | 15% | 12% | 12% | 10% | 29% |

* **By year, AAPL's overnight return is negative in 2022, 2023, 2024 and 2025 (−37, −7, −2, −14%),** while intraday is +5, +46, +29, +22%.
* SPY's overnight return is positive in every year except 2022. MSFT shows no such pattern.
* The largest single overnight gaps (all under 14%) cannot account for this; dividends are worth about −0.5% a year.

**Anatomy of decoupling (2020–2026), relative to normal (1 = normal):** on alarm days, the 20-day beta falls to 0.61, market volatility to 0.73 and AAPL's own volatility to 0.89, while idiosyncratic volatility rises to 1.17. The peers show the same pattern, so a typical decoupling is "a calm market plus stock-specific news." **Today is different:**
* AAPL's 20-day beta is **negative** (−0.97 × normal), while its idiosyncratic volatility is *below* normal (0.83).
* That is a calm, steady move against the market, i.e. rotation rather than news.
* Current episode (Sep 15 to Oct 23): AAPL +4.3%, S&P ex-AAPL −0.2%, SMH − SPY −2.6%. AAPL's residual is +4.2% and correlates **−0.34** with the AI factor.

## Amendment 1 (round 2): the quirks round 1 found. Pre-registered before computing.
**R2a, the overnight/intraday quirk (in-sample check of a pattern already seen):**
* Mean daily (intraday − overnight) for AAPL, 2020-01-02 to 2026-10-23.
* Two comparisons: (i) above the peer average; (ii) above AAPL in 2011–2019.
* 20-day block bootstrap; pass if both have p < 0.05.

**R2b, buyback execution (mechanism, not yet looked at):**
* Rule 10b-18 keeps buybacks out of the opening print and the last minutes of trading, so buybacks push prices during the day.
* Prediction: AAPL's mean (intraday − overnight) is larger in open windows than in blackout windows (T4 calendar).
* Quarter bootstrap; pass at p < 0.05.
* 2013–2019 is reported as a contrast (buybacks were also large then).

**R2c, residual persistence (in-sample):**
* Sum of AAPL's residual autocorrelations at lags 1–5, 2020–2026, above the peer average.
* Block bootstrap; pass at p < 0.05.

**R2d, the trader's question: after a rotation-type run-up, does AAPL's excess stick or fade?**
* Signal: AAPL's 20-day residual sum is in the top tenth of its trailing 252 days (no look-ahead).
* Outcome: the next 20-day residual sum.
* Statistic: mean outcome on signal days − mean on all days, 2020–2026. 20-day block bootstrap, two-sided p.
* Same for the peers pooled, as a contrast.
* No pass/fail direction; reported as stick (> 0), fade (< 0) or neither (p ≥ 0.05).
