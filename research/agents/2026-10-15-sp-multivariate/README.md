# Does a stack of signals (macro + options/flow + momentum/RSI + stretch) warn of S&P 500 corrections?

**Agent / session:** Claude (Opus 5.5), claude.ai session for the owner, 2026-10-15
**Started:** 2026-10-15   **Pre-registered at commit:** the first commit that adds this file (pushed before any model was trained)
**Type:** new question (multivariate follow-up to rounds 1 and 2)
**Verdict:** *(filled in at the end)*

## Question

Rounds 1 and 2 tested signals one at a time and found nothing beyond distance-to-the-line and volatility. The owner's
view: a warning should come from a **stack** — slow macro conditions first, then options flow and gamma weeks to
months ahead, with momentum/RSI and how stretched the market is. And the options market changed after 2019
(zero commissions, retail flow, daily 0DTE), so options signals may need their own regime.

**Asset:** the S&P 500 (^GSPC; SPY tracks it). Weekly, as of each Friday close, 1992–2026.

## Outcomes (forward from each Friday close; label windows start the next trading day)

1. **`Y_CORR` (primary): a fall of 10% or more** (daily low vs that Friday's close) within 13 weeks.
2. **`Y_BEAR` (secondary): a fall of 20% or more** within 52 weeks — the 2022-style case.
3. **`Y_CHAN` (secondary): a touch of the lower line** of the 3-year weekly channel (round 2's channel) within 26 weeks,
   weeks with a valid channel only.

## Features (`features_mv.py`; every value as known at that Friday's close)

| Layer | Features |
|---|---|
| **V** volatility (the baseline) | VIX; 20- and 126-day realized vol |
| **M** slow macro | Fed funds 52-week change; 10y 26-week change; 10y−3m curve; dollar 26-week change; M2 growth; CPI; margin debt growth; Fed net liquidity 26-week change; TIPS 26-week change; HYG vs IEF; margin credit; Chicago Fed NFCI and its risk, credit and leverage parts, and NFCI 13-week change |
| **O** options / flow / vol structure | VIX/VIX3M; VIX9D/VIX; VVIX; SKEW; VIX minus 20-day realized vol; Cboe total, equity and index put/call (10-day means; archive to Oct 2019, daily statistics after); S&P dealer gamma (GEX) and dark-pool index (DIX), SqueezeMetrics |
| **R** momentum and RSI | RSI(14) on daily, weekly and monthly bars; 4, 13, 26, 52-week momentum; 12-1 momentum; weekly MACD histogram; distance from the 40-week average; breadth (share of 137 stocks above their 200-day average); bearish RSI divergence (price within 1% of its 26-week high while weekly RSI is 10+ points below its prior 26-week peak) |
| **S** stretch / mean reversion | 3-year weekly channel position and R²; drawdown from the 52-week high; average pairwise correlation of stocks |
| **ERA** regime | zero-commission era (from 2019-10-04); daily-0DTE era (from 2022-05-13) — the eras in `research/microstructure` §4g |

Model inputs: trailing 260-week percentile (centred) for most features; RSI, channel position/R², drawdown and the
binary flags on their natural scale. Features that start late are missing before they exist.

Known limitations stated up front: the NFCI file is today's vintage (revised history; it also ends Apr 2026), so every
model is also run **without NFCI**; Cboe's put/call is Cboe-exchange volume only and its index ratio includes 0DTE
SPXW after 2022; breadth uses survivors only.

## Models and walk-forward (settings fixed here, no tuning on test years)

* **GBM (primary):** `HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05,
  min_samples_leaf=40, l2_regularization=1.0, random_state=0)`, missing values handled natively. It can find stacked
  combinations ("tightening AND low gamma AND stretched").
* **LOGIT (secondary):** L2 logistic regression, C = 0.3; missing → 0 (neutral) plus one missing flag per late feature;
  options-layer features also enter **interacted with the zero-commission era flag**, so their effect can differ after
  2019.
* **Walk-forward:** for each test year Y = 2000 … 2026, train on weeks from 1992 whose outcome window ended before
  Jan 1 of Y (purged), predict every week of Y. Evaluate on resolved weeks.
* **Specifications** (both models): `VOL` = V only (the bar to beat); `FULL` = all layers + ERA; drop-one
  (`FULL−M`, `FULL−O`, `FULL−R`, `FULL−S`); add-one (`V+M`, `V+O`, `V+R`, `V+S`); `FULL_RECENT` = FULL with weeks
  from Oct 2019 on weighted 2× in training; `FULL_NO_NFCI`.

## Frozen pass/fail

**Primary:** `Y_CORR`, GBM, `FULL` vs `VOL`, out of sample 2000–2026. **Pass only if both:**
1. AUC(FULL) − AUC(VOL) ≥ **0.05**, with the 95% interval from resampling **calendar years** (1,000 draws) above zero;
2. Brier skill of FULL relative to VOL > 0 (FULL's probabilities are more accurate).

The same test is reported for LOGIT, `Y_BEAR` and `Y_CHAN` (secondary; a pass there is labelled secondary), for
`FULL_NO_NFCI` (a pass that disappears without NFCI is reported as **NFCI-dependent**), and separately for the old
(2000 – Sep 2019) and new (Oct 2019 – 2026) option regimes.

**Which layer matters** (reported, no pass/fail): ΔAUC of each drop-one and add-one specification vs `VOL` and `FULL`,
with year-block intervals.

**Event counts:** the number of distinct corrections (separate 10% falls) and bear markets inside each test window is
stated next to every result. Fewer than 8 distinct events in a window → labelled underpowered.

## Exploratory (no pass/fail)

* **Stacked rule:** macro composite (≥ half of the macro signals in their bearish third) AND a fast trigger (VIX curve
  inverted-third, GEX bottom third, or equity put/call top third) AND stretched (weekly RSI ≥ 70, channel z ≥ 0.5 or
  distance from the 40-week average in its top third) vs the base rate, with a circular-shift null.
* **SPY's own gamma** (the owner's engine, `research/microstructure/out/td_gamma_SPY.csv`, 2020+): flip distance,
  near-price OI, call/put walls and gamma share expiring within a day, in the weeks before each 2020–2026 correction
  vs other weeks. Too few events to model.
* **Today:** the FULL model's current probabilities.

## Results

*(after the run)*

## Reproduce

```bash
python fetch_mv.py         # SKEW, VVIX, VIX9D, Cboe put/call (archive + daily JSON), Chicago Fed NFCI
python features_mv.py      # weekly feature table + outcomes -> data/features_raw.pkl, data/features_X.pkl
```
(Rounds 1 and 2 must be built first; this study reads their data and outputs.)
