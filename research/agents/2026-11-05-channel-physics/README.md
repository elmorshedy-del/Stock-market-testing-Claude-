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
