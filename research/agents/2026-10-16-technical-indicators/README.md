# Do classic technical indicators (RSI, momentum, ATR, MACD, ...) on daily, weekly and monthly bars give TSLA and MSFT entries or exits, and do they add to our setups?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Started:** 2026-10-16   **Pre-registered at commit:** (the first commit of this README, pushed before any outcome was computed)
**Type:** new question (extension)
**Verdict:** _to be filled in after the run_

## Question

The owner's view: standard technical indicators, read on monthly, weekly and daily bars, should give at least an additional entry or exit signal.

* **Part A, the indicators on their own:** does an indicator's state predict TSLA's or MSFT's next move? Three kinds of prediction:
  * **direction**
  * **an entry** (a big up move)
  * **an exit** (a big down move)
* **Part B, added to our setups:** within days when a setup is on, does the indicator change the odds?
  * TSLA: freed and below its own gamma flip (microstructure §4w/§4ad).
  * MSFT: the release setup, MSFT leading SPY while S&P dealer gamma is low (§4aa).

## Prior work
* `research/agents/2026-10-15-sp-multivariate` @ ecd5c43 found that weekly momentum/RSI warns of **S&P 500** corrections. The warning came from a broken trend: high RSI meant *lower* risk. That covers one index, one outcome (a 10% fall) and two indicator types.
* Not yet tested anywhere here:
  * single stocks
  * entries
  * ATR, MACD, Bollinger, stochastic and ADX
  * daily and monthly bars
  * whether any indicator adds to the options setups
* Setups from `research/microstructure` @ 58b9d1d: `burst_gamma.state`, `stock_gamma.frame` (TSLA) and `held_back` (MSFT release), imported unchanged.

## Data
* Yahoo daily OHLC with dividend-adjusted closes:
  * **TSLA:** 2010-06-29 to 2026-10-15
  * **MSFT:** 1986-03-13 to 2026-10-15
* High, low and open are scaled by adjclose/close.
* Weekly bars end on Friday; monthly bars end at month-end. The last bar of each is used only once complete.

## Indicators (standard parameters, the same bar counts on every timeframe)

| | Definition |
|---|---|
| RSI | RSI(14), Wilder smoothing |
| Momentum | rate of change over 12 bars (12 days, 12 weeks, or the classic 12 months) |
| ATR% | ATR(14) ÷ close |
| MACD | MACD(12, 26, 9) histogram ÷ close |
| Bollinger %B | (close − lower band) ÷ (upper − lower), 20 bars, 2 sd |
| Stochastic | slow %K(14, 3) |
| ADX | ADX(14), Wilder |
| Trend distance | close ÷ SMA − 1: SMA(200) daily, SMA(40) weekly, SMA(10) monthly (each about 200 trading days) |

**States:**
* Each indicator becomes a percentile against its own trailing window: 252 bars for daily (min 120), 52 for weekly (min 26), 60 for monthly (min 36). Monthly uses a longer window because 12 points cannot form thirds.
* **low** = bottom third; **high** = top third.
* Sensitivity check, outside the family: the classic fixed thresholds RSI > 70 / < 30 and stochastic > 80 / < 20.

## Outcomes (strictly after the bar's close)
| Timeframe | Horizon H | Forward return R |
|---|---|---|
| daily | 10 sessions | log return, close t to close t+10 |
| weekly | 4 weeks | close of week w to week w+4 |
| monthly | 3 months | month m to m+3 |

* **Entry outcome (UP):** R in that asset-timeframe's top 20%.
* **Exit outcome (DOWN):** R in its bottom 20%.

## Part A: statistics, null and pass/fail (fixed now)
* **Three statistics** for each asset × timeframe × indicator:
  * **S1, direction:** mean R when the indicator is high, minus when it is low.
  * **S2, entry:** P(UP | high) − P(UP | low).
  * **S3, exit:** P(DOWN | high) − P(DOWN | low).
* **Families:** each asset × timeframe is one family of 24 statistics (8 indicators × 3). There are 6 families.
* **Null:**
  * Shift all of a family's indicator series together, circularly, against the outcomes.
  * Daily uses 1,000 random offsets of at least 60 bars; weekly every offset of at least 13; monthly every offset of at least 6.
  * Each statistic becomes a z-score against its own null.
  * The **family-wise p** is the share of shifts whose largest |z| in the family is at least the real largest |z|. Each statistic's own two-sided p is reported too.
* **Survivor:** a statistic whose step-down family-wise p is < **0.0083** (0.05 over the 6 families).
* **Robust survivor:** also has the same sign in 1986/2010–2020 and in 2021–2026.
* **Smallest possible p, checked before the run** (bar counts only, no outcomes): daily 0.001; TSLA weekly ≈ 0.0013, monthly ≈ 0.0073; MSFT weekly < 0.001, monthly ≈ 0.0022. All are below 0.0083, so every family can pass.

## Part B: added to the setups (fixed now)
* **TSLA**, 2021+, days in the full setup (freed and below its flip):
  * up-burst within 3 sessions
  * down-burst within 3 sessions
* **MSFT**, 2012+, days in the release setup (20-day lead over SPY in its top third, S&P gamma in its bottom third):
  * up-leg starts within 10 sessions
  * down-leg starts within 10 sessions
  * (Both as in `held_back.outcomes`.)
* **Indicators tested:**
  * A fixed a-priori trio, chosen now: daily RSI, daily ATR% and weekly momentum.
  * Plus every robust Part A survivor for that asset, reported separately.
  * Weekly and monthly values reach the daily setup as the last completed bar.
* **Statistic:** within setup days, P(outcome | indicator high) − P(outcome | indicator low).
* **Null:** shift the indicator series alone against the fixed setup and outcomes, with 1,000 random offsets of at least 60 sessions; two-sided.
* **Pass:** p < **0.0042** (0.05 over the 3 indicators × 2 outcomes × 2 assets). Days and episodes are reported.
* **Power, stated now:** with about 60 setup episodes, an edge needs roughly +17 points to be seen (§4ad). A Part B null means "no large addition", not "no addition".

## What would prove the idea wrong
* **Part A:** no survivor in any family, or survivors that flip sign between eras.
* **Part B:** no indicator passes, and none shows a difference the sample could detect.

## Results
_to be filled in after the run_

## Threats to validity
_to be filled in after the run_

## Reproduce
```bash
OMP_NUM_THREADS=1 python indicators.py      # Part A + Part B + today's readings -> out/
```
