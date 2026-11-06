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
