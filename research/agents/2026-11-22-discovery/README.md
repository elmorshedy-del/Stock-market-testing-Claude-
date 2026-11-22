# Discovery pass 1: which slow and fast cross-asset variables predict the size and danger of the next S&P moves

**Protocol committed before any result is computed.** System: [DISCOVERY.md](../DISCOVERY.md). **Date:** 2026-11-22.
**Owner's request:** a rigorous system to surface relationships and predictors, including "how fast they moved or how certain variables moved together in certain environments".

## Fixed before running
* **Sampling:** weekly, at the Friday close (or the last trading day of the week).
* **Periods:**
  * discovery and walk-forward: **1990-01 to 2019-12**;
  * **lockbox: 2020-01-01 to the latest data. Sealed.** It is not used, plotted or summarized until the owner has seen the candidate list. It is then opened once.
* **Targets** (S&P 500, from the Friday close):
  1. `vol4`: log of annualized realized volatility over the next 20 trading days;
  2. `mdd13`: worst close-to-close drawdown over the next 65 trading days;
  3. `crash13`: 1 if `mdd13` ≤ −10%, else 0;
  4. `ret4`: log return over the next 20 trading days;
  5. `ret13`: log return over the next 65 trading days.
* **Benchmarks:**
  * `vol4`: the last 20 days' realized volatility (log);
  * `mdd13` and `crash13`: the expanding-window average or base rate;
  * `ret4` and `ret13`: the expanding-window mean.
* **Features:** the systematic library in `features.py` (stage 4 of the system), built from point-in-time data:
  * monthly data lagged one month;
  * NFCI lagged one week;
  * everything else at the Friday close.
* **Screen:** Spearman correlation of each feature with each target, on 1990–2019.
  * p-value from 500 circular shifts of the target (minimum shift 52 weeks);
  * Benjamini–Hochberg at q = 0.10 across all feature × target pairs;
  * stability: the same sign in 1990–99, 2000–09 and 2010–19.
* **Models:** LightGBM per target with fixed, modest settings (300 trees, learning rate 0.03, 15 leaves, minimum 40 rows per leaf, feature fraction 0.5); nothing is tuned.
  * Purged expanding walk-forward: test years 2000–2019; each fit uses data ending `h` weeks before the test year begins (`h` = 4 or 13).
  * Skill: out-of-sample R² against the benchmark for `vol4`, `mdd13`, `ret4` and `ret13`; Brier skill score and AUC for `crash13`.
  * **Null:** the whole walk-forward rerun 40 times with the target circularly shifted against the features. A model counts only if its skill beats the null's 95th percentile.
  * Explanation: SHAP values and SHAP interaction values on the walk-forward models, to name the drivers and the environments in which they matter.
* **Lead and lag:** PCMCI (partial-correlation test, lags 1–4 weeks, α = 0.01) on weekly changes in about ten core variables. A map of who leads whom.

## Expectations written down (my priors)
* `vol4` is predictable well beyond chance, because volatility clusters. The real question is whether anything beats its own past.
* `crash13` and `mdd13` are predictable modestly.
* `ret4` and `ret13` are close to unpredictable. A model that "predicts returns" here is more likely a leak than a finding, and gets audited first.

## Results
To be appended below this line after the run, without editing anything above.

## Pass 1 results (2026-11-22; appended, nothing above edited)
**Audit before results:** the strongest return predictors in the screen were weekly changes in the Chicago Fed NFCI.
* That index is re-estimated every week, so its past values are revised.
* It did not exist before 2011, so earlier values are backcast.
* It therefore fails the point-in-time rule.
* **Deviation:** models were run with all features (ALL) and without NFCI (CLEAN). CLEAN is the valid one.

**Screen** (1,130 feature × target pairs):
* 181 pass FDR at q = 0.10; 148 also keep the same sign in all three decades.
* Most measure the same thing: current stress (VIX level, realized volatility, credit spreads, distance from the 52-week high).
* The crash and drawdown links are carried mostly by the 2000s; in the 1990s the correlations are near zero.

**Models** (CLEAN, out of sample 2000–2019, ~1,030 weeks; skill = 1 − error ÷ benchmark error):
| Target | Model vs pre-registered benchmark | Chance 95th pct | p vs chance | Added benchmark (linear on VIX + 20d and 63d realized vol) vs pre-registered | Model vs added benchmark |
|---|---|---|---|---|---|
| vol4 | +0.108 | −0.201 | 0.024 | **+0.257** | −0.200 |
| mdd13 | −0.450 | +0.026 | 0.78 | **+0.112** | −0.632 |
| crash13 | −0.190 (AUC 0.60) | −0.050 | 0.83 | **+0.076** (AUC 0.58) | −0.287 |
| ret4 | −0.376 | −0.045 | 1.00 | −0.026 | −0.341 |
| ret13 | −0.662 | −0.073 | 0.98 | −0.068 | −0.556 |

* The 182-feature boosted model, untuned by design, is beaten by a three-variable linear model on every target. It overfits: about 1,000 weekly rows with overlapping targets give far fewer independent observations.
* Returns are not predictable by anything here, as expected beforehand.
* The ALL set (with NFCI) did better on vol4 (+0.18), consistent with NFCI's look-ahead.

**Lead and lag** (PCMCI, weekly changes, lags 1–4 weeks, FDR q < 0.01):
* 10 links in 1990–2019, 1 in 1990–2004, 8 in 2005–2019; **none appears in both halves.**
* The strongest (stocks lead the Baa spread by 1–2 weeks; the S&P leads the Nikkei by a week) are likely artifacts: stale compilation of Moody's yields, and trading hours that do not overlap.

## Pass 2 protocol (written after pass 1, before pass 2 runs)
* **Question:** does anything add to the current-stress model?
* **Benchmark S:** linear regression (logistic for crash13) on VIX level and 20-day and 63-day realized volatility, refit in each fold.
* **Targets:** vol4, mdd13, crash13. Returns are dropped; pass 1 settled them.
* **Nested selection, inside each walk-forward fold, on training rows only:**
  1. fit S;
  2. take the residual (for crash13, the outcome minus S's probability);
  3. rank every CLEAN feature by |Spearman| with that residual;
  4. keep the top 10.
* **Two incremental models per fold:**
  1. ridge (or L2 logistic), α = 1.0 on standardized inputs, using S's inputs plus the 10 selected features;
  2. a small LightGBM (4 leaves, at least 80 rows per leaf, 200 trees, learning rate 0.03) on the same 13 inputs, which can capture environment-dependent effects.
* **Skill** against S in the same fold. **Null:** 40 circular shifts of the target; S and the selection are redone under each shift. A model counts only if it beats the null's 95th percentile **and** S.
* **Reported:** how often each feature is selected across the 20 folds, as a measure of stability.

## Pass 2 results (appended)
| Target | Ridge: skill added over S | Chance 95th pct | p | Small trees: skill added over S | Chance 95th pct | p |
|---|---|---|---|---|---|---|
| vol4 | −0.079 | +0.073 | 0.49 | −0.233 | +0.173 | 0.98 |
| mdd13 | −0.323 | −0.027 | 0.54 | −0.307 | +0.124 | 0.85 |
| crash13 | −0.349 | −0.069 | 0.61 | −0.206 | +0.082 | 0.81 |

* **Nothing adds to the current-stress model.** Every incremental model is worse than S out of sample and inside the chance band.
* **Chance alone reaches positive "skill" here** (up to +0.17), because slow variables can fit a slow target by accident. Without the time-shift null, a positive in-sample or even walk-forward number would have looked like a finding.
* **Most-selected variables** (chosen from the past only, in each of 20 folds):
  * vol4: CAPE level (19), oil vs its 3-year range (16), stock–credit correlation (12);
  * mdd13: stock–credit correlation (19), dollar/yen distance from its 52-week high (19);
  * crash13: VIX vs its 3-year range, 252-day realized vol and the VIX 52-week speed (20 each). All three are more stress measures.

## Candidate list for the lockbox
* **One:** the three-variable stress model S (VIX level, 20-day and 63-day realized volatility), predicting 4-week volatility, 13-week drawdown and the odds of a fall of 10% or more.
* No discovered variable survived. **The lockbox stays sealed** until the owner decides whether to spend it on S.

## In the owner's units (1990–2019, weekly; overlapping weeks, so the effective sample is smaller)
| VIX at the Friday close | <13 | 13–16 | 16–20 | 20–25 | 25–30 | 30+ |
|---|---|---|---|---|---|---|
| Weeks followed by a fall of 10%+ within 13 weeks | 2% | 6% | 19% | 22% | 18% | 27% |
| Median realized volatility over the next 4 weeks | 8% | 10% | 13% | 17% | 21% | 30% |

**Files:** `features.py`, `screen.py` → `out/screen.csv`; `model.py` → `out/models.json`, `out/oos_*.csv`; `pass2.py` → `out/pass2.json`;
`leadlag.py` → `out/leadlag.json`; `explain.py` (written, not run: there was no model worth explaining); `figure.py` → `out/discovery.png`.
