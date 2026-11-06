# M3 signature test: does a shock's build-up predict how it fades, and whether a second leg comes?

**Status:** pre-registered. This file is committed and pushed before any outcome is computed by class.
**Law:** FOUNDATION.md M3 (signature), with the memory condition from M2.
**Owner's question:** "each move has its own volatility signature, and that controls how long the quiet lasts." Second part: does it predict whether a second leg down comes?
**Cards read in full before designing this test** (memory/papers/):
* Marcaccioli, Bouchaud & Benzaquen 2021
* Sornette, Malevergne & Muzy 2002
* Sornette & Helmstetter 2003

## What the theory predicts
* **Self-made shocks** (built up from many small moves) fade more slowly than shocks from outside news.
  * News shocks hit abruptly; self-made ones show a volatility build-up first (Marcaccioli 2021: minute data on 300 stocks).
  * The literature has not tested this on index-level shocks. Marcaccioli et al. removed market-wide events.
* **Condition** (Sornette & Helmstetter 2003): the gap exists only if market memory is long (power law slower than 1/t after renormalization).
  * With short, exponential-like memory, both kinds fade at the same speed.
  * Our aftershock study measured each index's memory (self-exciting kernel with tail exponent 1 + θ):

    | Index | θ | Fit gain, power law vs exponential (90% CI) | Memory |
    |---|---|---|---|
    | S&P | 1.13 | +2.5 [−2.5, 7.2] | short, unresolved |
    | NDX | 0.67 | +10.5 [2.6, 19.5] | long |
    | SOX | 0.46 | +12.7 [2.2, 26.4] | long |

  * So the gap should show in NDX and SOX more than in the S&P.
* **Second legs:** the literature says nothing about direction. That part is the owner's extension, tested here for the first time.

## Data and definitions (frozen)
* **Prices:** daily closes from Yahoo: ^GSPC from 1950, ^NDX from 1985, ^SOX from 1994. `prep.py` rebuilds them and checks for absurd moves (none above 25%).
* **Shock.** A down day with return ≤ −6 × the trailing 5-year median |return| (shifted one day), with no ±6× day in the previous 21 sessions. This is the same rule as the aftershock study.
  * It reproduces the published S&P set: 54 completed shocks, 28 with a new leg.
  * Complete shocks (those with 89 sessions after them): S&P 54, NDX 30, SOX 18.
  * The 2026-11-05 shock is excluded from the tests and classified as a live forecast.
* **Signature (uses only data before the shock):** B = mean |r| over days −10…−1 ÷ mean |r| over days −70…−11.
  * Within each index, shocks are split into thirds by B:
    * top third: "build-up" (self-made signature);
    * bottom third: "abrupt" (news signature);
    * the middle third is reported but left out of the two-class tests.
* **O1, fade.** E(a..b) = mean |r| over days a…b ÷ the same pre-shock baseline (days −70…−11), minus 1. Persistence P = E(21..60) ÷ E(1..20): the share of the early excess volatility still present a month later. Shocks with E(1..20) ≤ 0 are dropped and counted.
* **O2, second leg.** First-leg low = lowest close on days 0…5. A new leg is any close more than 2% below that low on days 6…89 (84 sessions). Same as the aftershock study.
* **O2x, direction beyond volatility.** For each shock, 2,000 sign-randomized paths for days 6–89: r* = μ + s(r − μ), with s = ±1 and μ = the mean return over the 1,260 days before the shock. This gives the expected new-leg rate given that path's volatility. Excess = actual − expected.
* **O3, pause length** (exploratory): sessions from the first-leg low to the new leg, among shocks that had one.
* **O4, decay exponent** (exploratory; the Sornette, Malevergne & Muzy method): the log-log slope of the class-average cumulative excess |r| over days 1–60, which gives α = 1 − slope.

## Hypotheses and pass criteria (frozen)
* **H1, the M3 law at daily index scale.** Pooled across the three indices, median P is higher after build-up shocks than after abrupt shocks.
  * Test: one-sided permutation (shuffle B within each index, 10,000 times), p < 0.05.
  * Report the difference in medians with a 90% bootstrap interval.
* **H2, the memory condition.** The build-up minus abrupt gap in median P is larger in NDX and SOX than in the S&P.
  * Test: [gap in NDX and SOX] − [gap in S&P] > 0, with a 90% interval excluding 0. Bootstrap over shock dates, since NDX and SOX share shock days.
  * **Expected to be underpowered:** 10 vs 10 shocks for NDX and 6 vs 6 for SOX.
* **H3, the owner's extension.** The new-leg rate is higher after build-up shocks than after abrupt ones, pooled.
  * Test: one-sided permutation, p < 0.05.
  * O2x tells whether any difference is more than volatility (more volatility means more new lows even with random signs). It is two-sided and exploratory.
* **Multiverse of free choices:** shock size {5×, 6×, 8×} × isolation {21, 42 sessions} × build-up window {5, 10, 20 days}, i.e. 18 specifications.
  * Joint p: the mean of the standardized effects across specifications, compared against the same within-index permutations.
  * The primary specification is 6×, 21 sessions, 10 days.
* **Power, stated in advance:** about 34 vs 34 shocks pooled. Only large differences can be detected; for example, a new-leg rate near 35% vs 65%. A miss here does not rule out a smaller effect.
* **Live forecast:** classify the 2026-11-05 shock in each index by B. Log the class-conditional persistence and new-leg rates as the forecast. Score it after day 89, around mid-March 2027.

## Reproduce
```
python prep.py       # data and the shock-set check
python test.py       # everything above -> out/signature.json, out/figure
```

---

## Results (run 2026-11-06 on data to the 2026-11-05 close)
**Deviations from the pre-registration, reported:**
* **S&P has 53 complete shocks, not 54.** The 1955-03-14 shock came only 39 sessions into the usable sample, too early for the 70-session baseline.
* **The joint p across the 18 specifications was miscomputed in `test.py`.** The permutations were not coupled across specifications, so the joint p came out under 0.001, which is too optimistic. `addendum.py` recomputes it with one random rank per shock (index and date), shared by every specification, as the pre-registration intended. **The corrected joint p is the one to use.**

### Verdicts
* **H1 (build-up shocks fade more slowly): passes narrowly.**
  * Median persistence: 0.32 build-up vs 0.15 abrupt. A month later, build-up shocks still carry about a third of their early excess volatility; abrupt shocks about a seventh.
  * One-sided permutation p = 0.049. 90% bootstrap interval of the difference: [−0.14, +0.55].
  * All 18 specifications are positive. Corrected joint p = 0.08.
  * **Dropped shocks:** all 13 shocks removed by the E1 ≤ 0 rule were abrupt shocks whose volatility was back below normal within 20 days (0 of 34 build-up shocks vs 13 of 34 abrupt). These are the fastest fades, so the rule worked against H1. Keeping them as the fastest fades (post-hoc rank test, `sensitivity.py`) gives p < 0.0001.
  * **Caveat:** most of this effect is also what plain volatility clustering predicts (recent high volatility stays high). The part only the theory predicts is H2.
* **H2 (the gap needs long memory): not established, as expected.** The direction matches the theory.

  | | S&P (short memory) | NDX | SOX (longest memory) |
  |---|---|---|---|
  | θ (from the aftershock study) | 1.13 | 0.67 | 0.46 |
  | Gap in persistence (build-up − abrupt) | +0.10 | +0.37 | +0.56 |
  | Decay exponent, build-up vs abrupt (exploratory O4) | 0.33 vs 0.33 | 0.29 vs 0.62 (NDX and SOX pooled) | |

  * The gaps rise in order as memory lengthens.
  * Long-memory gap minus S&P gap: +0.26, 90% CI [−0.39, +1.21].
  * The S&P exponents are identical, as Sornette & Helmstetter predict for short memory. For NDX and SOX the exponent gap has 90% CI [−0.14, +1.20], with an 81% chance of being above zero.
  * The abrupt exponent of 0.62 is close to Marcaccioli's 0.68 for news shocks. The build-up exponent of 0.29–0.33 is close to their 0.40 for self-made shocks and to the 0.3 decay after the 1987 crash.
* **H3 (build-up shocks bring more second legs): fails.**
  * New-leg rate: 50% build-up vs 53% abrupt; p = 0.68.
  * Corrected joint p = 0.87; only 3 of 18 specifications are positive.
  * **Direction beyond volatility (O2x):** second legs came about as often as random signs with the same realized volatility would produce: 50% vs 56% expected (build-up), 53% vs 54% (abrupt).
* **O3 (pause length):** 12 vs 11.5 sessions from the first-leg low to the new leg. No difference.

### Named events
* **9/11 (2001-09-17):** classified as build-up (B 1.24), although it is a textbook news shock. It faded fast (P 0.15). The signature misreads news that arrives in an already-volatile market, as Marcaccioli et al. also found (classification accuracy about 0.72).
* **Tariffs, 2025-04-03:** classified as middle or abrupt in all three indices. Volatility was below normal within two months (P −0.19 to −0.30): the calm after news.

### Live forecast (score after day 89, around mid-March 2027)
* **Class:** the 2026-11-05 shock has a build-up signature in all three indices (B = 1.42 S&P, 1.60 NDX, 1.74 SOX; the build-up cut-off is about 1.2).
* **Forecast 1:** its persistence P will be above the abrupt-class median in each index (0.16 / 0.20 / −0.30). That is, the storm fades slowly.
* **Forecast 2:** second-leg odds about 50%, i.e. no edge from the signature.

### What this means
* **The owner's signature idea is half right.**
  * The build-up before a shock predicts how long the storm lasts (volatility), most clearly in the long-memory markets (NDX, chips), as the physics predicts.
  * It does not predict whether a second leg comes. Given the volatility that follows, the direction is a coin flip (law C1).
* **"Digest, then follow-through"** remains a fair description, since most second legs pause first. But whether the follow-through comes cannot be called from the signature.

### Next for M3
* **More power for H2:** run the same test on the 1-minute bars we already hold (SPY and QQQ, 2020–26). There are many more shocks there, but intraday memory has to be measured first.
* **Separate the theory from plain clustering:** simulate each index's fitted memory model, then check whether the model alone reproduces the class gaps.

### The owner's interpretation (2026-11-06), and how it fits
**Owner:** "A one-off shock is shaken off quickly, while a deeper shock carries volatility as investors keep reassessing."

**How it fits:**
* **It matches the physics.** Sornette's "self-made" shock is the build-up of many small bad news items. That is a deep issue being repriced piece by piece, so the fundamental and physical readings describe one mechanism.
* **It matches the cross-index pattern.** The gap is clearest in Nasdaq-100 and chips, which are concentrated in one theme (AI), so doubt there keeps being repriced. It is weakest in the diversified S&P.
* **One correction to the intuition:** reassessment raises volatility in both directions. Deep shocks did not bring more lower lows (50% vs 53%). They brought bigger swings, including sharp rallies.

**A possible test** (logged, not run): if reassessment drives the slow fade, the gap should be larger for shocks concentrated in one sector or theme than for broad shocks, and volatility should stay elevated on scheduled news days (earnings, CPI) after build-up shocks.
