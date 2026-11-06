# Sornette, Malevergne & Muzy (2002). Volatility fingerprints of large shocks: endogeneous versus exogeneous. arXiv:cond-mat/0204626
Published in *Risk* (2003) and in *The Application of Econophysics* (Springer, 2004).
**Read:** full text, including Appendices A–D, on 2026-11-06. **Verified:** arXiv. **Laws:** M3, M2.

## Claim
**Outside shocks.** After an external shock (one piece of big news), excess volatility decays as 1/√t. The exponent of 1/2 is universal: it does not depend on the shock's size.

**Self-made shocks.** An endogenous shock comes from many small bad news items adding up through the market's long volatility memory. It decays as 1/t^α(s), where the exponent depends on the shock's size: the bigger the shock, the smaller α and the slower the decay. A specific build-up comes first.

## Data
* **Exogenous examples:** the Aug 19, 1991 coup against Gorbachev (Nikkei, S&P 500, FTSE 100) and Sep 11, 2001 (CAC 40, S&P 500), on daily data.
* **Endogenous example:** the Oct 19, 1987 crash (S&P 500).
* **Shock hierarchy:** S&P 100 5-minute data, Apr 1997 – Dec 2001, de-seasonalized and aggregated to 40-minute and daily scales.
* **Daily indices:** "17 years of daily returns of various indices" (French, German, Canadian, Japanese) are said to give the same results. **No details are shown.**

## Method
* **Model: the multifractal random walk.**
  * Log-volatility is driven by an information flow through a memory kernel K(τ) ~ √(λ²T/τ).
  * Its covariance decays as the logarithm of the lag, with λ² ≈ 0.02 and T ≈ 1 year. The fitted value is λ² = 0.018.
* **Exogenous response:** the linear response to one large input, E[σ²|ω₀] − σ̄² ∝ 1/√t.
  * **Measured as cumulative excess volatility**, which grows as √t (slope 1/2 on a log-log plot). This is a robust way to measure it.
* **Endogenous response:** the expected volatility conditional on a burst e^{2s}σ̄² with no external input.
  * This gives t^−α(s) with α(s) = 2s / ln(T·e^{3/2}/Δt). The exponent is linear in the burst size s.
  * Before the shock, the expected news flow grows like K(−t) ~ 1/√(−t): an accelerating build-up.
* **Exponents measured** as a function of s, with 95% intervals from 500 simulated paths.

## Results
* **Exogenous:** the 1991 coup and 9/11 follow the √t cumulative law in several indices.
* **Endogenous:** after the 1987 crash, volatility decays as about 1/t^0.3 (citing Lillo & Mantegna). That is clearly slower than 1/2, so 1987 is classified as endogenous.
* **Shock hierarchy:** α(s) is linear in s, at both the 40-minute and daily scales, and the exponent rises from fine to coarse scales. It agrees with the model without fitted parameters for α ≥ 0. Estimates are noisy for volatility dips below normal.
* **Against linear models:** models that are linear in volatility, such as FIGARCH, predict the same exponent for every size. The size-dependence favours the log-volatility model.

## Caveats
* **Mine: very few labelled events.** The exogenous evidence rests on two events (seen in several indices) and the endogenous evidence on one (1987). The shock hierarchy is conditioned on volatility level, not on news labels.
* **Mine: the daily-index claim is not shown.**
* **Theirs:** "endogenous" is a misnomer, since all volatility is driven by news. The difference is many small items versus one big one.
* **Disagreement with Marcaccioli et al. 2021,** which fits a self-exciting model:

  | | Decay exponent (outside shock) | Decay exponent (self-made shock) |
  |---|---|---|
  | This paper | 1/2 | depends on shock size |
  | Marcaccioli et al. 2021 | 1 − θ ≈ 0.7 | 1 − 2θ ≈ 0.4, fixed |

  Both agree that self-made shocks decay more slowly.

## What it means for us
* This is a second theory for M3, with a sharper test.
  * **For outside shocks:** the decay exponent is the same regardless of size.
  * **For self-made shocks:** the exponent shrinks as the shock grows, so the biggest self-made shocks stay volatile longest.
* **For the owner's question** (does this decline continue?):
  * A large self-made shock (no single news item, with a build-up) should keep volatility elevated much longer.
  * An outside shock should fade on a fixed √t schedule.
* **The build-up shape before a self-made shock is a usable warning sign:** it should accelerate roughly as 1/√ of the time left to the shock.

## How we would replicate or extend it on our data
1. Use daily S&P 500 data from 1950. Measure the cumulative excess squared return after each shock, over 1–60 sessions. Fit the log-log slope to get 1 − α.
2. Label shocks as outside shocks (a scheduled macro release or a documented one-off event) or self-made.
3. **Pre-registered predictions:**
   * outside shocks have a cumulative slope of about 1/2, i.e. α ≈ 0.5;
   * self-made shocks have α < 0.5;
   * among self-made shocks, α falls as shock size rises; among outside shocks, it does not.
4. Compare with Marcaccioli et al.'s fixed exponents (0.4 / 0.7). Our data can tell the two theories apart.

## Open questions
* Can 1987 still be called a self-made shock once program trading and portfolio insurance are seen as forced flows (S2, S4)? "Self-made" may mean "driven by forced flows", which ties M3 to Kyle & Obizhaeva's crash law.
