# Does Kronos (a foundation model for price candles) help on TSLA?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-24
**Type:** zero-shot model check, pre-registered here before any scored run. A smoke run only checked that the model loads and produces a forecast from the latest close.
**Builds on:** microstructure §4ab (TimesFM 2.5 zero-shot: no help on direction, volatility below the options' implied vol). The design copies §4ab so the two results compare directly.
**Verdict:** (after the run)

## The model
* **Kronos** ([shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos), [arXiv 2508.02739](https://arxiv.org/abs/2508.02739), AAAI 2026) is a decoder-only transformer pre-trained on candle data (open, high, low, close, volume) from more than 45 exchanges. It tokenizes candles and samples future candles autoregressively.
* **Weights used:** `NeoQuasar/Kronos-small` (24.7M parameters) as the primary model and `NeoQuasar/Kronos-base` (102.3M) as the secondary, both with `Kronos-Tokenizer-base`. Context limit 512.
* Run on CPU. Sampling uses the README defaults (T = 1.0, top_p = 0.9).

## Leakage guard
* The paper went up on 2025-08-02, so the pre-training data ends before that.
* Only origins from **2025-10-01** onward are scored, so no outcome could be in the training data. This is the same cut-off as §4ab.

## Design
* **Data:** TSLA daily bars from Yahoo (10 years, fresh through 2026-10-23).
* **Inputs at each origin day t:** the last 400 bars through t (open, high, low, close, volume; the predictor's default `amount` = volume × mean price).
* **Origins:** every trading day from 2025-10-01 to 2026-10-09, the last day with 10 sessions of outcome. That is about 255 origins.
* **Paths:** K = 8 sampled 10-session paths per origin.
  * Kronos-small runs on every origin.
  * Kronos-base runs on every 5th origin (CPU time). Its results are reported as secondary and descriptive.

### Job 1: direction (primary: 10 sessions)
* **Prediction:** log(mean across paths of the close at t+h) − log(close at t), for h = 5 and 10.
* **Scores:** correlation with the realized log return, hit rate, and MAE.
* **Baselines:**
  * hit rate against "always long" (the share of up windows);
  * MAE against a zero-change forecast.
* **Null:** circular shift of the prediction series against the outcomes, 1,000 shifts, minimum shift 20 origins. The p-value is one-sided.
* **Pass (Kronos-small, h = 10):** correlation p < 0.05 **and** hit rate above always-long.

### Job 2: volatility over the next 10 sessions
* **Prediction:** mean across paths of the mean |daily log return| along the path. The first step is from the close at t.
* **Realized:** mean |daily log return| over t+1 to t+10.
* **Baselines:**
  * the last 22 days' mean |return|;
  * a 1/5/22-day blend;
  * **the options' own 30-day ATM implied vol** (`td_gamma_TSLA.csv`, converted to an expected mean |daily return| as IV·√(2/π)/√252).
* **Scores:** correlation and MAE.
* **Pass:** Kronos-small's correlation beats the option-IV correlation, with a 20-day block bootstrap p < 0.05.

### Job 3 (secondary): next-day range
* **Prediction:** mean across paths of the first step's log(high/low).
* **Baseline:** the last 22 days' mean log(high/low).
* **Score:** correlation with the realized range.

### Also reported (descriptive, not a test)
* Both models' 10-session forecast from the **2026-10-23 close**: median path and 10–90% band.

## Prediction (written before the run)
* No usable direction skill: hit rate near always-long, correlation within the shift null.
* Volatility worse than the options' implied vol, as with TimesFM.
* The edges in this repository come from positioning (open interest, gamma, expiry), which a candle-only model cannot see.

## Threats to validity
* About 255 overlapping 10-day windows hold only about 25 independent outcomes. The shift null keeps the serial dependence but has limited power.
* K = 8 paths make the mean forecast noisy, which works against Kronos. The 5-day horizon and the base model act as checks.
* Yahoo prices are split-adjusted. The input is normalized per window, as the predictor does.
