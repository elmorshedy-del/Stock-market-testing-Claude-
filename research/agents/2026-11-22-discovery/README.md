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
