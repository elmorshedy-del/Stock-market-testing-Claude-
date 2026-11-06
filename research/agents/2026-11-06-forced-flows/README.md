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

## Results (run 2026-11-06, before the open)
Files:
* `ff_fetch.py` → `data/` (gitignored: leveraged-ETF quotes, daily and 5-minute bars);
* `ff_test.py` → `out/ff.json`;
* `figure.py` → `out/physics_next.png` (shared with the aftershocks study).

### Data correction before any result was read
* **The first run hit two data problems:**
  * Yahoo's daily closes for SOXX on 2026-11-02 to 11-04 came back about 3 times too high (453–465, against 150–155 in the 5-minute bars). That produced a fake −70.7% semis day.
  * A 20-session warm-up gap dropped 20 sessions from each index complex.
* **Fixes:**
  * Daily closes are overwritten by each day's last 5-minute close. That matches the official close wherever both exist (0 mismatches over 1% for SPY, QQQ and every stock).
  * Rolling windows need only 15 of 20 sessions.
* The first-run numbers are not results. The final sample is 660 observations: 11 underlyings × 60 sessions.

### H-FF1 FAILS: out-of-sample correlation of the flow predictor with the 15:30→close move = -0.09 (90% CI -0.30 to +0.11, one-sided p 0.76)
### H-FF2 FAILS: out-of-sample R² flow -0.043 vs momentum -0.028 (ΔR² -0.014, p 0.67); neither beats zero
### H-FF3 FAILS: Spearman ρ between leveraged intensity ψ and end-of-day momentum = +0.12 (direction as predicted), permutation p 0.36, 11 underlyings

| underlying | ψ = ΣL(L−1)A / daily $ volume | end-of-day momentum slope | corr(R, r) |
|---|---|---|---|
| SEMIS | 2.65 | +0.031 | +0.20 |
| NDX | 1.10 | +0.011 | +0.07 |
| MSTR | 0.99 | +0.017 | +0.13 |
| COIN | 0.89 | -0.015 | -0.10 |
| TSLA | 0.79 | -0.033 | -0.23 |
| MU | 0.55 | +0.051 | +0.29 |
| NVDA | 0.46 | +0.014 | +0.07 |
| PLTR | 0.36 | -0.002 | -0.01 |
| AMD | 0.31 | +0.033 | +0.20 |
| SPX | 0.24 | -0.021 | -0.15 |
| AVGO | 0.16 | +0.014 | +0.07 |

* **Constant-asset sensitivity:** same verdicts (correlation -0.09, ΔR² -0.014).
* **Fitted impact constant:** Y = 0.188 in-sample and 0.077 on all sessions. The textbook value is about 0.5–1.
* **My prediction was wrong:** I expected H-FF1 to pass.

### Descriptive: the Nov 5 close
| complex | full-day move | forced close rebalancing | % of a normal day's $ volume | actual 15:30→close |
|---|---|---|---|---|
| SEMIS | -12.3% | $27.93bn | 21.8% | -1.46% |
| NDX | -6.5% | $18.83bn | 6.1% | -0.66% |
| SPX | -4.4% | $4.97bn | 1.0% | -0.30% |
| MU | -17.5% | $1.63bn | 6.7% | -2.97% |
| TSLA | -10.8% | $1.18bn | 8.2% | +0.27% |
| NVDA | -9.3% | $0.88bn | 4.0% | -0.82% |
| AMD | -17.3% | $0.46bn | 3.6% | -2.34% |
| MSTR | -9.2% | $0.22bn | 8.5% | -0.05% |
| PLTR | -9.7% | $0.15bn | 2.9% | +0.08% |
| AVGO | -10.5% | $0.11bn | 1.5% | -1.24% |
| COIN | -9.7% | $0.10bn | 6.8% | -0.80% |

* The semis figure assumes Yahoo's net assets are from after the Nov 5 drop. If they predate it, the forced selling is about $21bn, or 17% of a normal day's volume, instead of $28bn.

### Exploratory (not pre-registered)
* **The textbook constant Y = 1 on big days** (|move by 15:30| ≥ 2.5%):
  * 230 observations on 56 days;
  * correlation 0.08, same sign 52%;
  * average continuation +0.04% actual vs +0.66% predicted.
* **Single days:** Nov 5 fit for semis (−1.49% predicted, −1.46% actual). Oct 30 went the other way (−1.33% predicted, +1.10% actual).
* **Next-morning reversal:** the correlation of the flow predictor with the next day's first 5 minutes is +0.03. No transient impact is measurable.

### Reading
* **The identity is exact and the flows are big, but the price doesn't move when the flow hits.** The likeliest reasons:
  * the flow is public arithmetic, so anticipating traders and liquidity providers position earlier;
  * swap dealers hedge through the day.
* **So where a low forms** probably depends on forced selling nobody can compute in advance: margin calls, volatility-target and CTA deleveraging, redemptions. Scheduled flows are priced early.
* **Direct measurement** would need closing-auction imbalance data. Databento cost quotes from 2026-11-06, nothing purchased:
  * Nasdaq imbalance for the 10 Nasdaq-listed names, last 60 sessions: $0.53; Jan 2024 to now: $6.29.
  * SPY imbalance on NYSE Arca, Jan 2024 to now: $9.38.
  * 1-minute bars, Jan 2024 to now: $3.62 for the 10 names plus $0.41 for SPY.
  * Full extension: about $19.70.

## Erratum (2026-11-06, after the literature review)
The interpretation "scheduled flows are priced early" (above, and in the INDEX row) is probably wrong.
* **Contrary evidence.**
  * Hartzmark & Solomon (2025, American Economic Review) find that predictable dividend-reinvestment flows still move the whole market on the day they are paid, with a multiplier of about 1.9.
  * Garcia-Ares, Vasquez, Pearson & Amaya (2026, SSRN 7330098) find that unwinding the hedges of expiring index options moves the last 30 minutes: about 6 bp per one standard deviation of dealers' 3:30 pm delta.
* **Likelier explanations for our null.**
  * Our flows were estimated from a formula, not observed.
  * Leveraged-ETF rebalancing may be executed by swap dealers before 15:30.
  * Closing liquidity is very deep.
* **Status.** The test result (H-FF1/2/3 fail) stands; only the explanation changes. Closing-auction imbalance data would measure the flow directly. See FOUNDATION.md, law S2.
