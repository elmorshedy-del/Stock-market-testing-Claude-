# Kyle & Obizhaeva (2016). Market microstructure invariance: empirical hypotheses. Econometrica 84(4), 1345–1404. doi:10.3982/ecta10486
**Read:** the full published text (60 pages), Sections 0–7 and the Supplemental Material (Tables A.I–A.V and the list of follow-up research), 2026-11-06. Verified: Crossref (2026-11-06-literature-laws/out/).
**Laws:** M1 (business time and invariance), F1 (impact shape: linear vs square root), F7 (spread), S4 (the crash law is built on this paper's constants).

## Claim
Two hypotheses about "bets" (a trader's decision to change a position; close to a metaorder):
1. **Invariance of bets.** The dollar risk a bet transfers per unit of business time, I = P·Q·σ/√γ, has the same distribution in every asset and period. Here γ is bets per day, i.e. the speed of business time.
2. **Invariance of transaction costs.** The dollar cost of a bet is the same function of I everywhere.

**Implications from volume and volatility alone,** with W = P·V·σ ("trading activity"):
* bets per day γ ∝ W^(2/3);
* bet size as a fraction of volume ∝ W^(−2/3);
* percentage spread ∝ σ·W^(−1/3);
* illiquidity 1/L ∝ (σ²/(P·V))^(1/3).

**Invariance does not fix the shape of impact.** Linear and square-root impact are both allowed.

## Data
* 2,552 portfolio transitions, 2001–05, from one vendor that handled over 30% of US outsourced transitions.
* 439,765 orders (201,401 buys, 238,364 sells) in NYSE, AMEX and NASDAQ common stocks.
* V is the prior month's average volume. σ is a log-ARIMA forecast; prior-month realized volatility gives similar results.
* Benchmark stock: $40, 1m shares/day, σ = 2%/day (W* = 40e6 × 0.02).
* Trading activity spans a factor of about 150 between the lowest and highest volume groups.
* Execution: about 60% of orders finish on day 1. By dollars, 41/23/15/7/5% is done on days 1–5.

## Method
* **Bet sizes:** regress ln(X/V) on ln(W/W*); invariance predicts slope −2/3. Errors are clustered by week × 17 industries.
* **Costs:** implementation shortfall against the prior close. They control for the market return on day 1, scale by σ, then fit a nonlinear regression:
  cost = κ₀·(W/W*)^α₁ + κ_I·(W/W*)^α₂·(φI/0.01)^z,
  where φI = (W/W*)^(2/3)·X/V is the bet size in invariant units. Invariance predicts α₁ = α₂ = −1/3.
* **Shape-free check:** 1,000 dummies (10 volume groups × 100 size bins).

## Results
* **Bet sizes:**
  * slope −0.62 (s.e. 0.009); quantiles −0.61 to −0.65. Statistically rejected against −2/3, economically close.
  * Restricted fit: ln(X/V) = −5.71 − (2/3)·ln(W/W*) + √2.53·Z.
    * The median benchmark order is 0.33% of daily volume; one standard deviation is a factor of 4.9.
    * Across 15 groups: means −6.03 to −5.41, variances 2.23–2.90, kurtosis 2.73–3.38 (log-normal fits well; a KS test rejects exact equality).
    * Top-1% boundary for the benchmark stock: 12.9% of daily volume (Table A.I).
  * Bets per day: γ = 85·(W/W*)^(2/3).
* **Concentration (if impact is linear):**
  * the largest 5.4% of bets make 50% of volume;
  * **the largest 0.07% of bets make 50% of return variance;**
  * benchmark stock: of 21,420 bets a year, **the 15 largest produce half of the year's variance.**
* **Costs:**
  * Free fit: **z = 0.57 (s.e. 0.039)**, i.e. close to square root; linear (z = 1) is about 11 standard errors away. With α restricted, z = 0.56; with 12 free parameters, z = 0.58 (0.041). Sub-samples give 0.44–0.63.
  * α₂ = −0.32 (0.015), as invariance predicts.
  * Calibrations (Table V), cost of 1% of daily volume in the benchmark stock:

    | Model | Impact | Spread | R² |
    |---|---|---|---|
    | Linear | 2.50 bp (0.19) | 8.21 bp | 0.0991 |
    | Square root | 12.08 bp (0.74) | 2.08 bp | 0.1007 (better) |

    * The market return alone gives R² = 0.0847, so the cost models add only 1–2 points.
  * KO2023's crash constant k = 5.00 (0.38) is exactly 2 × 2.50 (0.19). Under linear execution the price move is twice the average cost.
  * Buys cost more than sells: 12.08 vs 9.56 bp (NYSE).
* **The only evidence for linear at the top:** the two curves cross near the largest-1% bin. "For the largest 1% of orders in the highest-volume group", the dummy fits linear better. That is one coefficient, in the group the authors call the noisiest.
* **Spreads:** slope −0.35 (0.003), R² 0.47. Transition managers pay 71% of the quoted half-spread.
* **Follow-up evidence they cite** (Supplement): TAQ print sizes fit invariance in the 1990s but broke after 2001 (decimal ticks, order-splitting algorithms). News-article counts and buy-sell switch counts scale as W^(2/3).

## Caveats
* **The authors':**
  * invariance is statistically rejected in most tests but economically close;
  * ζ (volume multiplier), ψ (share of variance from bets) and δ (transition order vs bet size) are assumed constant and are unidentified;
  * it should hold best with a small tick, competitive market makers and low fees;
  * fast execution may cost more than the formula, since the general cost could depend on the horizon in business time;
  * the invariants are nominal dollars and should drift with finance wages.
* **Mine, for the crash law:**
  1. **Scope.** The theory assumes "a bet transfers only idiosyncratic risk about a single asset, not market risk". The cost regressions remove the market return, which "understates transaction costs" if orders move the whole market. **The whole-market crash law (KO2023) is outside what this paper derived or tested.**
  2. **Shape.** The bulk of the data is concave (z ≈ 0.57). The crash law needs linear, and the only support is one top bin.
     * The two calibrated curves cross at φI ≈ 18% of benchmark daily volume.
     * Crash-sized bets (KO2023: 6.0–6.2 standard deviations) sit at φI ≈ 50, more than 10× beyond the single largest order in the data and about 400× beyond the top-1% bin.
     * **The linear vs square-root choice for crashes is pure extrapolation from this paper.**
  3. **Under square root, invariance stops amplifying impact.** The W^(1/3) factor cancels: "the square root is the only function for which … impact … depends only on Q/V". So the crash law's business-time amplification exists only if impact is linear at huge size.
  4. **Data:** 2001–05 only, one vendor, US stocks only; futures and index products were not tested.

## What it means for us
* **For the crash law (S4, test #4):**
  * Report three predictions for every event:
    * Inv-LIN: KO2023, k = 5, with W^(1/3) amplification;
    * Inv-SQRT: 1.5 × 12.08 bp × (σ/0.02) × √(Q/(0.01·V)); the peak of a square-root ramp is 1.5× its average cost;
    * conventional: Q/market cap.
  * The data cannot pick the shape at crash size. Our events can add evidence on that, which is the real scientific value of #4.
* **The tail statement is the deep idea** (the largest 0.07% of bets make half the variance). It ties F1, M2 and S4 together: big moves come from rare giant bets, not many small ones. Testable on our data as "how much of a year's variance comes from its few largest flow days".
* **For M1:** γ ∝ W^(2/3) has independent support (news counts, switch counts, E-mini minutes). Business time is the best-supported part of the framework. The cost constants are less reliable.
* **For F7:** spread ∝ σ·W^(−1/3) (slope −0.35) is the same law as "spread ∝ volatility per trade" from the physics side.

## How we would replicate or extend it on our data
1. **Bets per day ∝ W^(2/3)** cannot be tested without metaorder data. The trade-level 3/2 law can (see the Benzaquen 2016 card).
2. **Spread law** on our symbols: regress ln(spread/(P·σ)) on ln(W/W*); expect −1/3. Needs quotes (ThetaData or Databento).
3. **Concentration law:** share of each year's S&P variance from its top 0.1%, 1% and 5% of days, vs a log-normal bet model. Free with daily data. This only shows days, not bets, so it is weaker.
4. **Test #4:** the three predictions above, for events with documented forced selling.

## Open questions
* Does impact at whole-market crash size follow linear or square root? Bucci, Benzaquen, Lillo & Bouchaud (2019, PRL), "Crossover from linear to square-root market impact", is the key physics paper on when impact is linear. **Read before #4.**
* Is the invariant cost constant across markets at the bet level? Bucci et al. (2020), "Are trading invariants really invariant?". **Read before #4.**
