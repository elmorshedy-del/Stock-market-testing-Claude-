# Do gaps and premarket moves stop at option walls, and does the gamma regime decide whether a gap runs or gets dragged back?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Started:** 2026-10-16   **Pre-registered at commit:** (the first commit of this README, pushed before any outcome was computed)
**Type:** new question (the owner's observation)
**Verdict:** _to be filled in after the run_

## Question
The owner's observations:
* Gaps open, and premarket moves stop, exactly at certain levels: the walls.
* The options regime decides whether the price rushes on or is dragged back.
* Premarket volume plays a role.

Today's example (Oct 16): TSLA gapped about +4% on news, peaked premarket at 382.19 just above the 380 strike (the largest open interest expiring today near the price), then slipped back to about 374.

**The confound to beat:** strikes sit on round numbers, and prices cluster at round numbers with or without options. The question is whether the extremes land on the **high-open-interest** strikes more than on **equally round** strikes with less open interest.

## Data
* TSLA open interest per strike from ThetaData: the daily file, where OI dated t is the positions going into session t, known before the open.
* Yahoo daily OHLC from 2020 on, converted to raw (pre-split) prices with the ratio of the option-implied spot to Yahoo's close.
* Yahoo 5-minute pre/post bars: the last ~60 sessions only.
* Dealer gamma flip: `research/microstructure/out/td_gamma_TSLA.csv`, read from the row before day t. MSFT, SPY and QQQ come from their own files.

## G1: walls (pre-registered)
* **Walls on day t:** the 3 strikes with the most total OI (calls + puts, expiries ≤ 45 days) within ±10% of the prior close.
* **A hit:** a price within **one tenth of the local strike spacing** of a wall (for example $0.50 when strikes are $5 apart). That is the resolution of the strike grid, not a market rule of thumb.
* **Events:**
  * (a) the regular-session open
  * (b) the day's high and the day's low, pooled
  * (c) the premarket high and low, 04:00–09:30 (Yahoo, last ~60 sessions)
* **Null, roundness-matched:**
  * Each strike gets a roundness class: the largest of 100, 50, 25, 10, 5, 2.5 or 1 that divides it.
  * Each day's 3 walls are replaced by 3 random strikes from the same window with the same mix of classes.
  * 2,000 replications give the distribution of total hits.
* **Statistic:** observed hits minus the null's mean; one-sided p = share of replications with at least as many hits.
* **Pass:** p < **0.0167** (0.05 over the 3 events).
* **Also reported:** a second null that keeps today's strikes but takes each strike's OI from a day 20+ sessions away. Event (a) is repeated on gap days only (see G2).

## G2: the gamma regime at the open (pre-registered)
* **Gap days:** |open ÷ prior close − 1| in the top fifth of its own trailing 252 days (2020+).
* **State at the open:** is the open above or below the dealer gamma flip from the prior day's row? That flip uses only OI and quotes known before the open.
* **Outcome, continuation:** the session's move (close − open) has the same sign as the gap.
* **Statistic:** P(continuation | open below the flip) − P(continuation | open above the flip).
* **Hypothesis:** positive. Below the flip, dealers amplify, so the gap runs; above it, they dampen, so the gap gets dragged back.
* **Null:** circular shift of the above/below sequence across the gap days, every offset of at least 10 gap days.
* **Pass:** TSLA p < **0.05** with a positive difference.
* **Secondary, descriptive:**
  * MSFT, SPY and QQQ on their own data, each with its own p.
  * The 2 × 2 table of gap up/down × above/below the flip.
  * Gap fill (the close back beyond the prior close) by state.

## G3: premarket volume (not run; no data)
* Yahoo reports zero volume for premarket bars, and Alpha Vantage's extended-hours bars are a paid endpoint.
* Planned test, once 1-minute premarket bars with volume are available: the share of premarket volume vs its own trailing 20 sessions, on gap days, against continuation (the same null as G2).

## Prediction written now
* **G1:** the day's highs and lows land on walls a little more than chance; the open does not. Pass is unlikely for (a), possible for (b). (c) is underpowered at about 60 days.
* **G2:** the difference leans positive but does not pass for TSLA.

## Results
_to be filled in after the run_

## Reproduce
```bash
OMP_NUM_THREADS=1 python gaps_walls.py
```
