# Are price channels real? Random-walk null test: variance ratios and the "channel force"

**Agent / session:** Claude, for the owner, 2026-11-05 after the close.
**Pre-registered at commit:** the commit that first adds this README. No result had been computed when it was written.

**Owner:** "Is there a microstructure way or rigorous quantitative way where a mathematical model would fit them and it can be scientifically validated … like physicists … derived from fundamental principles rather than just mathematically fit … The most inferior method is what we're doing, just subjectively trying to fit it."

## Why this test comes first
A drawn channel is only physics if a restoring force pulls price back toward a trend. Without one, any price path shows "channels" in hindsight and touching a line carries no information. The null is a random walk with drift whose volatility clusters exactly like the real market. So the first job is to test for the restoring force against a null that keeps everything else real markets have.

## Two models
* **M0, no force.** log price = drift × time + a random walk whose daily moves cluster exactly as observed.
  * Built from sign-randomized surrogates: r*ₜ = μ + sₜ(rₜ − μ), with sₜ = ±1 at random.
  * This keeps every day's absolute move (volatility clustering, fat tails, crash days) and destroys any predictability of direction.
* **M1, restoring force.** log price = trend + an Ornstein–Uhlenbeck deviation with speed κ. It predicts:
  * (a) variance ratios below 1 at horizons around 1/κ;
  * (b) a negative slope of future returns on today's channel position;
  * (c) channel width set by σ/√(2κ), rather than drawn by hand.

## Data
Daily closes from Yahoo, as log returns:
* S&P 500 (^GSPC), 1950–2026;
* Nasdaq-100 (^NDX), 1985–2026;
* PHLX Semiconductor (^SOX), 1994–2026.

## Tests
All tests use 2,000 surrogates per index. One-sided p = the share of surrogates at or beyond the observed value.

* **T1, variance ratio.** VR(q) = Var(overlapping q-day log return) ÷ (q × Var(1-day log return)), for q = 21, 63, 126, 252, 504, 756.
  * **H-T1:** VR(756) is below the M0 surrogates (p < 0.05, Holm over the 3 indices) on at least 2 of the 3 indices.
* **T2, channel force.**
  * zₜ = position in the trailing 756-session log-linear channel (no look-ahead; same as channels-deep P2).
  * β_h = OLS slope of the forward h-session log return on zₜ, for h = 21, 63, 252.
  * **H-T2:** β_63 is below the M0 surrogates (p < 0.05, Holm over the 3 indices) on at least 2 of the 3 indices.
  * Secondary: all 9 cells (3 indices × 3 horizons), Holm over 9.
* **T3, descriptive.** How tight is each current channel compared with chance? Take the residual SD of the 2023-01-03→today in-sample channel for ^GSPC, QQQ and SMH (the owner's charts) and report its percentile among sign-randomized versions of the same returns.

## My predictions (stated before running)
* **T1:** weak mean reversion, with VR(756) between 0.6 and 0.95 on all three. I expect the S&P not to clear the surrogates (p > 0.05). NDX and SOX might clear it, driven by 2000–02. H-T1 is a coin flip.
* **T2:** β_63 slightly negative but not significant. H-T2 fails.
* **If both fail:** drawn channels are mostly hindsight, and the models worth building are volatility and flow models (see Next).
* **If both pass:** M1 is supported, and channel width and the odds of reaching a line can be derived from (σ, κ) instead of drawn.

## Interpretation note
A negative β could also come from a time-varying risk premium (expected returns rise after falls). Either one is a restoring force in prices, and this test cannot tell them apart.

## Next (not part of this pre-registration)
* **Mechanistic route:** a forced-flow model with an impact law.
  * Flows: leveraged-ETF rebalancing, which is an identity, ΔExposure = L(L−1) × AUM × daily return; vol-target deleveraging; dealer gamma hedging.
  * Impact: the square-root law.
* **Self-excitation:** a Hawkes branching ratio and Omori aftershock decay, estimated on 5-minute data.

## Amendment A1: a model derived from first principles, the volatility first-passage model
**Pre-registered at the commit that first adds this section.** T1-T3 had been run; A1 had not.

**Motivation.** T1 and T2 found no restoring force (see the results, added later). If channels carry no direction, the physics left is volatility. A random walk's chance of falling a given distance has a closed form (the reflection principle, i.e. Brownian first passage) with one measured input: volatility. That gives "how much further, how likely" from first principles, with nothing drawn.

**Model.**
* log price is a Brownian motion with drift μ and per-session volatility σₜ = k × VIXₜ/100/√252.
* P(the close falls by a = −ln(1 − x) within T sessions) = Φ((−a − μT)/(σₜ√T)) + exp(−2μa/σₜ²) Φ((−a + μT)/(σₜ√T)).
* Two parameters, shared by every cell:
  * k, the implied-to-realized volatility scale (it also absorbs daily-close monitoring);
  * μ, the drift.

**Data.** S&P 500 (^GSPC) closes and VIX (^VIX), 1990-01-02 to today. Secondary: Nasdaq-100 (^NDX) with VXN (^VXN, 2001 on).

**Cells.** x = 5% and 10%; T = 21 and 63 sessions. Outcome = 1 if any close within T sessions is ≤ today's close × (1 − x).

**Fit and test.**
* Fit k and μ by maximum likelihood on 1990–2007 (all 4 cells jointly).
* Test out of sample on 2008-01-01 to the last complete window.
* Metric: Brier skill score (BSS) against climatology, where climatology = the in-sample base rate for each cell.
* 90% CI from a block bootstrap with 252-session blocks.

**Hypotheses.**
* **H-A1 (primary):** S&P out-of-sample BSS > 0, with the 90% CI lower bound > 0, in at least 3 of 4 cells.
* **H-A2 (secondary):** adding the trailing 756-session channel position z as a logistic covariate does not improve out-of-sample log loss by more than 0.5%. In other words, the drawn channel adds nothing beyond volatility.
* **Descriptive:**
  * NDX/VXN, with the same k and μ re-fitted on 2001–2007;
  * reliability table (10 bins);
  * today's touch probabilities for the same-rule lines (S&P 7,076 and 6,616; QQQ 642 and 597).

**My predictions (stated before running).**
* k ≈ 0.75–0.85, because implied volatility exceeds realized.
* H-A1 passes in all 4 cells, with more skill at 21 sessions than at 63.
* H-A2 holds: the channel adds nothing.

**Also exploratory (not a test), added with A1:** S2 re-runs the channels-deep P2 event rule on the M0 surrogates. It asks whether "short channel broken → 10%+ fall within a year" is more than volatility clustering would produce.
