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

## Results (run 2026-11-05)
Files:
* `physics.py` → `out/physics.json`, `out/surrogates.npz` (T1-T3);
* `a1_first_passage.py` → `out/a1.json`;
* `s2_surrogate_p2.py` → `out/s2.json`;
* `figure.py` → `out/physics_tests.png`.

### T1. Variance ratios: H-T1 FAILS (no restoring force)
| index | VR 1m / 3m / 6m / 1y / 2y / 3y | 3y random-walk 2.5 / 50 / 97.5 | p (3y below) |
|---|---|---|---|
| S&P 500 (1950-) | 0.92 / 0.86 / 0.91 / 0.94 / 0.87 / 0.77 | 0.53 / 0.93 / 1.59 | 0.24 |
| Nasdaq-100 (1985-) | 0.85 / 0.88 / 0.90 / 1.00 / 1.08 / 1.00 | 0.42 / 0.85 / 1.98 | 0.65 |
| SOX (1994-) | 0.81 / 0.84 / 0.89 / 0.90 / 0.68 / 0.64 | 0.35 / 0.81 / 1.91 | 0.29 |

* Holm p = S&P 500 0.73, Nasdaq-100 0.73, SOX 0.73.
* **Against my prediction:** VR(756) landed in my 0.6-0.95 range for the S&P (0.77) and SOX (0.64), but not for NDX (1.00). None cleared the surrogates.

### T2. Channel force: H-T2 FAILS (position in the channel predicts nothing)
| index | β 21d / 63d / 252d (forward log return per 1σ of z) | 63d random-walk 95% band | p (below) 21 / 63 / 252 |
|---|---|---|---|
| S&P 500 | +0.0009 / +0.0038 / +0.0068 | -0.0064 to +0.0060 | 0.80 / 0.90 / 0.76 |
| Nasdaq-100 | +0.0018 / +0.0050 / +0.0145 | -0.0140 to +0.0143 | 0.77 / 0.77 / 0.77 |
| SOX | +0.0030 / +0.0080 / -0.0088 | -0.0233 to +0.0226 | 0.78 / 0.77 / 0.43 |

* All 9 cells sit inside the random-walk bands; Holm p = 1.0 everywhere.
* **My prediction had the wrong sign.** I predicted a slightly negative β. Eight of the 9 are slightly positive, which is weak momentum, the opposite of a pull back to the line. None is significant.

### T3. How tight is each current channel (descriptive)
| | residual SD of the 2023 channel | random-walk median | ratio | percentile among random walks |
|---|---|---|---|---|
| S&P 500 | 3.92% | 6.65% | 0.59 | 3.5 |
| QQQ | 5.72% | 9.07% | 0.63 | 4.5 |
| SMH | 13.23% | 16.1% | 0.82 | 23.2 |

* The S&P and QQQ channels since 2023 are smoother than about 96% of random walks built from the same daily moves. SMH's is ordinary.
* The window was picked after the fact, starting at the 2022 low. That is the look-elsewhere effect, and T2 shows past smoothness did not predict anything.

### A1. Volatility first-passage model: H-A1 FAILS on the strict bar; H-A2 HOLDS
Fit on 1990-2007: k = 0.812 (prediction 0.75-0.85, correct); drift 14.9% a year. Out of sample, 2008-2026:

| cell | Brier skill vs climatology | 90% CI | mean predicted | observed |
|---|---|---|---|---|
| -5% within 21 sessions | +0.049 | -0.054 to +0.125 | 0.188 | 0.179 |
| -5% within 63 sessions | -0.016 | -0.145 to +0.076 | 0.341 | 0.333 |
| -10% within 21 sessions | +0.085 | -0.067 to +0.189 | 0.034 | 0.049 |
| -10% within 63 sessions | +0.004 | -0.152 to +0.141 | 0.113 | 0.155 |

* **H-A1 fails.** No cell has a CI lower bound above 0. My prediction (pass in all 4) was wrong; skill was higher at 21 sessions than at 63, as predicted.
* **Reliability shows how it fails, and both ways are physical:**
  * At high VIX the model over-predicts falls, because fear decays (an aftershock-like fade in volatility).
  * At low VIX it under-predicts them (falls from calm; fat tails).
  * Overall, real 10% falls came about 1.4 times as often as the model said.
  * Both point to the same missing ingredient: self-exciting, mean-reverting volatility with jumps.
* **Nasdaq-100 / VXN (descriptive):** k = 0.767; BSS -5% within 21 +0.09, -5% within 63 +0.05, -10% within 21 +0.11, -10% within 63 +0.08. The CI clears 0 for both 21-session cells.
* **H-A2 holds.** Adding the trailing channel position changes out-of-sample log loss by -0.10%, +0.11%, -0.40%, -0.10%, so the drawn channel adds nothing beyond volatility.

### S2 (exploratory). The channels-deep P2 rule on random walks
* **On random walks:** the same channel-break rule gives a median 16 events per path. A median 86% of them fell 10%+ within a year (5-95%: 69-100%), and 38% became bears (19-57%).
* **Actual:** 100% and 35%. 63% of random walks had at least the actual bear share, and 8.6% had at least the actual 10%+ share.
* **So** P2's elevated risk is what volatility clustering produces. The channel itself carried no information.

### Today's odds from the A1 model
The lines rise with each trend, so the model uses drift minus trend. The deeper odds are floors, because of fat tails.
* S&P 500 line through the 2026 low (7,076.2): 24% within 5 sessions, 58% within 21, 76% within 63 (implied vol 28.18).
* S&P 500 line through the 2025 low (6,616.1): 0% within 5 sessions, 12% within 21, 39% within 63 (implied vol 28.18).
* QQQ (Nasdaq-100 model, VXN) line through the 2026 low (641.6): 85% within 5 sessions, 94% within 21, 97% within 63 (implied vol 38.26).
* QQQ (Nasdaq-100 model, VXN) line through the 2025 low (596.8): 6% within 5 sessions, 40% within 21, 67% within 63 (implied vol 38.26).

### Conclusion
* **Drawn channels fail.** Tested against a random walk that keeps every real daily move, they show no restoring force and no predictive power. Their one real signal, more risk after a break, is volatility clustering.
* **The physics that survives is volatility.** A two-constant Brownian first-passage model is right on average. It fails exactly where physics says a Gaussian diffusion fails: it misses decaying fear and jumps from calm.
* **Next models:**
  1. Self-exciting volatility: Hawkes and aftershock (Omori) decay, from 5-minute data.
  2. Forced flows plus the square-root impact law, for where a low forms.
  3. Earnings × multiple, for a channel's slope.
