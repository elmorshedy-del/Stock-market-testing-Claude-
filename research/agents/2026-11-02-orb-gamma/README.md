# Does a 5-minute opening-range breakout make money in SPY, and mainly when dealers are short gamma?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02 (intraday, after the close data for Oct 30)
**Started:** 2026-11-02   **Pre-registered at commit:** (the commit that first adds this README)
**Type:** replication (practitioner ORB) + new question (gamma conditioning) + exploratory features and ML with a held-out test
**Verdict:** (filled in at the end)

**Owner's ask (2026-11-02):** "Let's run it, make it simple first, then add any related variables that could sharpen it or tilt the odds, and do ML. Start small so you don't use a lot of quota. The data has to be sorted, audited and diagnosed. A failed test doesn't mean the strategy is wrong; it could be the parameters, the regime or the conditions, so analyze what worked and why, and improvise."

## Question
* Does the opening-range breakout (ORB) of Zarattini & Aziz (SSRN 4416622, 2023: QQQ 2016-23, claimed 33% annual alpha) make money on SPY in 2024-26 after costs?
* Is the edge concentrated where our gamma work says dealers amplify moves, with SPY below its pre-open gamma flip or S&P GEX low?
* Which conditions (gap, opening-range width, opening volume, VIX, 0DTE share, calendar) tilt the odds, and can a small ML model, tested on held-out months, beat the simple rule?

## Prior work
* REPORT §4z at 26a8bce: below the flip, SPY up-bursts are 2.8× as likely (p < 0.001); down-bursts are not raised (0.7×). This is the basis for H2's direction. A long-side tilt below the flip is possible, so long and short results are reported separately.
* flip-wicks at 26a8bce: `out/preopen_levels.csv` gives the daily pre-open SPY flip (including and excluding same-day expiries), GEX and 0DTE share, from prior-close open interest. That makes it known before the open. Used as is, not edited.
* intraday-hours B1 and forced-flow A2 at 26a8bce: no intraday momentum into the US close in 2023-26. That is a prior against the ORB working overall.
* open-fade at 26a8bce: "sell at the open" is not supported; the routine first-hour dip is not a signal.
* hft-papers at fd8ede0 (C1): the source of this idea.

## Hypotheses and pass/fail criteria (frozen before any strategy result)

### Data audit (must pass before any strategy number is computed)
* **D1 completeness:** a regular session has 390 one-minute bars, 09:30-15:59 ET. Days missing more than 5 bars in 09:30-10:00, or more than 20 bars in total, are dropped and counted.
* **D2 accuracy:** daily open, high, low and close rebuilt from the bars vs Yahoo SPY daily (unadjusted). A day is flagged if any of the four differs by more than 0.05%.
* **D3 timestamps:** UTC to ET with DST. The first bar must be 09:30.
* **D4 calendar:** half days (13:00 close) are excluded.
* **Pass:** at least 95% of sessions clean on D1 and D2. If the audit fails, switch the source (ARCX.PILLAR, SPY's primary listing) and log it as an amendment before any strategy run.

### Strategies (frozen)
* **S0, the paper's ORB (primary):**
  * The first 5-minute candle is the 09:30-09:34 bars. Close > open: go long at the 09:35 bar's open. Close < open: go short. Equal: no trade.
  * Stop = the first candle's low for a long, its high for a short. Target = 10R, where R = |entry − stop|. Otherwise exit at the 15:59 bar's close.
  * Stops are checked on each bar's high and low. If a bar opens through the stop, the fill is that bar's open. If the stop and the target are both touched in one bar, the stop is assumed.
* **S1, classic breakout (secondary):**
  * The opening range is the high and low of 09:30-09:34.
  * Enter long on the first trade above the range high + $0.01 (fill at the larger of that level and the bar's open), or short on the first trade below the range low − $0.01. Only the first break counts, and there are no entries after 15:00.
  * Stop at the opposite side of the range; exit at the close.
* **Costs:** $0.01 a share a side, plus $0.01 extra on stop fills. Results are in basis points of the entry price, and in R.
  * Day P&L is 0 on no-trade days.
  * The paper's sizing (1% risk per trade, leverage capped at 4×) is reported as secondary, for comparability only.

### H1 (replication)
* **Statistic:** S0 mean net P&L per day.
* **Null:** a circular shift of the daily direction signal against the days' price paths. Each day's long and short outcomes are both computed, so a shifted signal picks the other outcome. Shifts k run from 20 to N−20; p = the share of shifts with a mean ≥ the actual.
* **Pass:** mean > 0 and p < 0.05. S1 is reported the same way, but S0 decides H1.

### H2 (gamma regime, this study's main question)
* **Regime:** below the flip = SPY's 09:35 price < `flip_incl`. That flip includes the day's expiring options, which are live during the session.
* **Statistic:** mean S0 P&L on below-flip days minus above-flip days, over sessions covered by `preopen_levels.csv` (through 2026-10-12).
* **Null:** a circular shift of the regime series, which keeps how persistent regimes are.
* **Prediction:** the difference is positive. **Pass:** p < 0.05.
* **Secondary regime definitions,** with Holm correction across the three:
  * `flip_excl`;
  * SqueezeMetrics S&P GEX at the prior close in the bottom tercile of its trailing 252 days, vs the top tercile.
* **Falsified if** above-flip days do as well or better.
* Long and short trades are also reported separately, because of the 2.8× long-side prior.

### H3 (exploratory: parameters, the multiverse)
* **Grid:** opening range ∈ {1, 5, 15, 30} minutes × exit ∈ {close, 10R, 2R} × {S0, S1} = 24 variants.
* **Joint p:** the max-t across the grid under the same circular shift.
* Report which variants work and in which regimes. Nothing here is a confirmatory claim.

### Conditioning variables (exploratory; all known by 09:35)
* the overnight gap, its size and direction, and whether the first candle agrees with it;
* opening-range width vs 14-day ATR (Crabel: narrow ranges break better);
* first-5-minute volume vs its 14-day average ("in play");
* VIX at the prior close and its overnight change (Breaking-VIX-at-open);
* the 0DTE share; distance to the flip, scaled;
* day of week; OPEX week; scheduled CPI, FOMC and NFP days;
* the prior day's return; DIX (prior close).

### ML (exploratory, with an untouched test)
* **Target:** an S0 win (net P&L > 0).
* **Features:** the list above.
* **Split by time:**
  * train 2024-01-02 to 2025-06-30;
  * validate 2025-07-01 to 2025-12-31, where the probability threshold is chosen;
  * test 2026-01-02 to 2026-10-30, touched once.
* **Models:** L2 logistic regression; shallow gradient boosting (depth ≤ 3, ≤ 200 trees).
* **Rule:** take S0 only when the predicted P(win) is above the threshold.
* **Compare on test** with unfiltered S0 and with the best simple regime filter from H2.
* **ML "pass":** test-period Sharpe above the unfiltered S0, with a 10-day block-bootstrap 90% CI that excludes 0.
* About 200 test days is small. The result is a lean, not a rule.

### Scope and cost (start small)
* **Stage 1 (this registration):** SPY only, Databento EQUS.MINI `ohlcv-1m`, 2024-01-01 to 2026-10-31. The quote is **$0.227** (20.3 MB). Gamma state from flip-wicks; GEX and DIX from SqueezeMetrics (free); VIX from Yahoo (free).
* **Stage 2 (pre-planned; logged as an amendment before it runs):**
  * extend SPY to 2020-2023 (ARCX.PILLAR, about $0.55) as an out-of-sample check of any Stage-1 regime finding;
  * QQQ, and TSLA on its own flip.

## Method
* `fetch.py` pulls the bars into `data/`, which is gitignored.
* `audit.py` writes `out/audit.json`.
* `orb.py` holds the S0/S1 engine plus H1 and H2.
* `explore.py` runs H3 and the features.
* `ml.py` runs the ML step.
* `figure.py` makes the figures.

## Results
(pending)

## Threats to validity
* **Venue:** EQUS.MINI is not the full consolidated tape. Highs and lows can differ slightly, which D2 checks.
* **Fill realism:** stop fills at bar granularity; there is no queue position.
* **Period:** 2024-26 is mostly a bull market. The regime split shrinks the samples.
* **The flip** is a model level that depends on our convention (classic dealer sign).

## Reproduce
```bash
python fetch.py   # needs DATABENTO_API_KEY in the environment
python audit.py && python orb.py && python explore.py && python ml.py && python figure.py
```
