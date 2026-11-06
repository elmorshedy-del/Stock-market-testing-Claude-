# Forced flows: do leveraged-ETF rebalancing and the square-root impact law explain the last 30 minutes?

**Agent / session:** Claude, for the owner, 2026-11-06.
**Pre-registered at commit:** the commit that first adds this README. No result had been computed when it was written.

**Owner:** "Yes do both." This is the second of the two next models from channel-physics. The idea: the low forms where forced selling runs out. This study tests the cleanest forced flow, because it is an exact identity.

## Physics
* **The identity.** A daily-reset leveraged ETF with leverage L and net assets A must trade ΔX = L(L−1)·A·r in the underlying at the close, where r is the underlying's return that day.
  * L(L−1) > 0 for every L except 0 and 1. So long and inverse funds alike always trade in the direction of the day's move: they sell into down days.
  * Summing over every fund on an underlying gives the forced flow F = Σᵢ Lᵢ(Lᵢ−1)·Aᵢ·r.
* **The impact law.** The square-root law is empirically near-universal and derived from latent-liquidity models. Executing Q against daily volume V moves price by about Y·σ·√(Q/V), with Y of order 1.
* **Prediction.**
  * From 15:30 to the official close, price should continue in the direction of the day's move. The move should be about Y·σᵤ·sign(F)·√(|F|/Vᵤ).
  * This is strongest where leveraged assets are large relative to liquidity (semis, single stocks) and tiny for the S&P.

## Data
* **Window:** the last 60 sessions (2026-08-13 → 2026-11-05) of Yahoo 5-minute bars, plus official daily closes.
* **Underlyings and their leveraged ETFs.** Leverage is checked against each fund's name.
  * **S&P 500 (SPY):** UPRO, SPXL, SSO, SPXU, SPXS, SDS, SH.
  * **Nasdaq-100 (QQQ):** TQQQ, QLD, SQQQ, QID, PSQ.
  * **Semis (SOXX):** SOXL, SOXS, USD, SSG.
  * **Single stocks:** NVDA, TSLA, AMD, AVGO, MU, PLTR, MSTR, COIN, each with its single-stock leveraged ETFs, where Yahoo reports net assets.
* **Net assets.** The current Yahoo netAssets, scaled back by each fund's price path. This assumes constant shares, ignoring creations and redemptions; a sensitivity run holds assets fixed instead.
* **Liquidity Vᵤ.** The 20-session average daily dollar volume, lagged.
  * Single stocks: the stock's own volume.
  * S&P: all S&P 500 constituents.
  * Nasdaq-100: its constituents.
  * Semis: the main US-listed semiconductor names.
* **Volatility σᵤ.** The 20-session daily-return SD, lagged.
* **Variables.**
  * R = previous official close → 15:30, the "move so far".
  * r = 15:30 → official close, which includes the closing auction.
  * The forced-flow predictor uses R as the information available at 15:30.

## Tests (fit sessions 1-30, test sessions 31-60)
* **H-FF1 (primary).** Out of sample, the flow predictor x = σ·sign(F)·√(|F|/V) correlates positively with r, pooled over underlyings. Block bootstrap by day, one-sided p < 0.05.
* **H-FF2.** The flow model (r = Y·x) beats generic intraday momentum (r = β·R, one β for all underlyings) in out-of-sample R². Bootstrap p < 0.05.
* **H-FF3 (the physics signature, all 60 sessions).** Each underlying's end-of-day momentum slope (r on R) rises with its leveraged intensity ψᵤ = Σ L(L−1)·A/V. Spearman correlation > 0, permutation p < 0.05.
* **Descriptive:**
  * the Nov 5 decomposition: estimated close rebalancing in dollars for each complex, as a percent of V, and the predicted vs actual last-30-minute move;
  * today's 15:30 rule for each underlying.

## My predictions (stated before running)
* H-FF1 passes, because end-of-day momentum is well documented.
* H-FF2 is a coin flip, because flow and momentum are collinear within an underlying.
* H-FF3 is a coin flip with about 13 underlyings, but I expect a positive rank correlation.

## Confounds (not modelled)
* Dealer gamma hedging, which also trades into the close.
* Volatility-target and CTA deleveraging, for which there is no asset data.
* News near the close.

## Better data, cost to be quoted and approved first
Closing-auction imbalance messages (Databento `imbalance` schema) would measure the forced flow directly instead of inferring it.
