# Sornette & Helmstetter (2003). Endogeneous versus exogeneous shocks in systems with memory. Physica A 318, 577. arXiv:cond-mat/0206047
**Read:** full text, with figures 1–3, on 2026-11-06. **Verified:** arXiv. **Laws:** M3, M2.

## Claim
Whether a self-made shock recovers more slowly than an outside shock depends on the shape of the system's memory.
* With exponential memory, both recover at the same speed, so the origin cannot be told from the recovery.
* With long, power-law memory, self-made shocks recover more slowly.
* Self-made shocks are preceded by a build-up that mirrors their recovery.

## Model
* Activity: A(t) = ∫ η(τ) K(t−τ) dτ, where η is the noise ("news") and K is the memory kernel, i.e. the response to one past input.
* **Outside shock:** E[A(t)] = A₀·K(t) plus the background. Recovery is the kernel itself.
* **Self-made shock**, conditioned on a big burst with no external input: E[A(t)] ∝ A₀ ∫ K(t+u) K(u) du.
* **Build-up before a self-made shock.** The expected noise path before it grows like K(−t). The activity before the shock follows the same curve as the recovery after it, i.e. it is time-symmetric.

## Classification by memory shape (the key result)
**Short times:**
* **Exponential memory:** outside and self-made recover at the same speed.
* **Faster than exponential:** outside shocks recover more slowly than self-made ones.
* **Slower than exponential** (stretched exponential or power law): outside shocks recover faster, self-made more slowly.

**Long times:**
* **Memory decaying faster than 1/t** (K ∝ 1/t^(1+θ)): asymptotically there is no qualitative difference; both decay as 1/t^(1+θ).
* **Memory decaying slower than 1/t** (K ∝ 1/t^(1−θ), which a near-critical self-exciting process with power-law memory produces): self-made shocks decay as 1/t^(1−2θ), clearly slower than outside shocks at 1/t^(1−θ).

**Boundaries:** exponential memory (at short times) and 1/t memory (at long times) are the "blind" kernels, where recovery shape cannot reveal the origin.

## Simulation
A self-exciting cascade with power-law memory φ ∝ 1/(t+c)^(1+θ) behaves, near criticality, as memory 1/(t+c)^(1−θ).
* With θ = 0.1–0.2 and 50 runs averaged, outside shocks decay as 1/t^(1−θ). Self-made shocks decay as 1/t^(1−2θ) both before and after the peak.
* A single run is very noisy (about 100 events); averaging is needed.

## Financial example
Log-volatility memory K ∝ 1/√t (θ = 1/2), the multifractal random walk. This gives the 9/11 and Gorbachev-coup versus 1987 contrast in Sornette, Malevergne & Muzy (2002).

## Caveats (mine)
* **Linear response.** The model is linear (presented as coarse-grained). The finite-variance result is generalised in a cited follow-up.
* **The finance evidence** is that of Sornette, Malevergne & Muzy (2002): very few labelled events.
* **Time symmetry is a model property.** Marcaccioli et al. (2021) found self-made shocks only mildly asymmetric.

## What it means for us (important)
**This turns M3 into a law with a condition we can measure:** the self-made vs news difference should appear only where market memory is long, not exponential.

**Our aftershock study already measured the memory shape:**

| Index | Power law vs exponential (fit gain) | Reading |
|---|---|---|
| S&P | +2.5, CI [−2.5, 7.2] | not resolved |
| NDX | +10.5 | power law wins |
| SOX | +12.7 | power law wins |

Averaged mainshock responses fitted best as exponential, with τ ≈ 120 sessions.

**Pre-registrable prediction:** self-made shocks recover more slowly than news shocks in NDX and SOX, but little or not at all in the S&P. One measured constant (the memory shape) predicts another observable (whether the classes differ).

**For the owner's idea** ("each move's signature sets how long the quiet lasts"): this is true only in markets or eras with long memory. That is a refinement, not a contradiction.

**The build-up before a shock should mirror the recovery after it.** That gives a real-time test: measure the build-up, then forecast the recovery.

## How we would replicate or extend it on our data
1. Reuse the aftershock study's memory estimates per index (fit gain of power law vs exponential, with bootstrap intervals).
2. Classify shocks into self-made and news, and measure the recovery exponent for each class.
3. Test whether the recovery gap (self-made slower) grows with how much the power law beats the exponential, across S&P, NDX, SOX and eras (pre- vs post-2008, where our power-law evidence differed).

## Open questions
* Is our exponential fit on the S&P real or a power-of-test problem? Daily big-day counts are small.
* Do intraday data (1-minute, where memory is longer) show the gap more clearly than daily data?
