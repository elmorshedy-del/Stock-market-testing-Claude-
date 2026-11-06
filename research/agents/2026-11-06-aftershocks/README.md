# Aftershocks: is market fear a self-exciting process with an Omori-law memory?

**Agent / session:** Claude, for the owner, 2026-11-06 (after the Nov 5 close, before the jobs report).
**Pre-registered at commit:** the commit that first adds this README. No result had been computed when it was written.

**Owner:** "Yes do both." This is the first of the two next models from channel-physics. That study found the Brownian first-passage model with VIX misses in two physical ways: it predicts too many falls when VIX is high (fear fades) and too few from calm (jumps). Both point to self-exciting, decaying volatility.

## Physics
* **Earthquakes.** Aftershock rates decay as Omori's law, λ(t) ∝ (t + c)^−p, and each quake can trigger others (a branching, or Hawkes, process).
* **Markets.** If big days trigger big days with a power-law memory, the same model should forecast big-move days better than:
  * a short-memory (exponential) version;
  * a constant rate.
* **Branching ratio n.** The share of big days triggered by earlier big days rather than by news. n near 1 means near-critical, cascade-prone.

## Data
* **Primary:** daily closes, S&P 500 (^GSPC), 1950 to 2026-11-05.
* **Replications:** Nasdaq-100 (^NDX, 1985–) and SOX (^SOX, 1994–).
* **Scale:** sₜ = the median |daily log return| over the previous 1,260 sessions (5 years, lagged). The scale moves slowly, so it doesn't absorb the clusters being measured.
* **Event:** a day with |r| ≥ 3·sₜ (about 1.5% for the S&P today).
* **Mainshock:** a day with |r| ≥ 8·sₜ and no such day in the previous 63 sessions.

## Models
1. **Discrete Hawkes (all events).**
   * P(event on day t | past) = μ + n·Σⱼ₌₁..₂₅₂ k(j)·x₍ₜ₋ⱼ₎, with the kernel k normalized to sum to 1.
   * Kernels:
     * power-law (Omori): k(j) ∝ (j + c)^−p;
     * exponential: k(j) ∝ e^−j/τ;
     * constant: μ only.
   * Fit by Bernoulli maximum likelihood on 1955–2007. Test out of sample on 2008-01-01 → 2026-11-05.
2. **Omori, mainshock-stacked.**
   * Aftershock rate at lag t = 1..120 sessions after each mainshock: b + K(t + c)^−p, vs b + K·e^−t/τ, vs b.
   * Fit on pre-2008 mainshocks. Test on 2008+ mainshocks.

## Hypotheses
* **H-SE1 (primary).** The power-law Hawkes beats the exponential Hawkes in out-of-sample log-likelihood on the S&P. Pass if the 90% CI of ΔLL (block bootstrap, 252-session blocks) is above 0.
* **H-SE2.** Both Hawkes models beat the constant rate out of sample. This is a sanity check: volatility clusters.
* **H-OM1.** In the mainshock-stacked data, the power law beats the exponential out of sample. Pass if the 90% CI of ΔLL (mainshock bootstrap) is above 0.
* **Descriptive:**
  * the branching ratio n and the Omori exponent p;
  * the NDX and SOX replications;
  * the share of big days attributed to triggering.

## Forward forecast (logged now, scored later)
* From the power-law Hawkes fitted on all data up to 2026-11-05, simulate forward 10,000 times.
* Report the expected number of S&P event days (|r| ≥ 3·s) over the next 5, 21 and 63 sessions, with 80% intervals.
* Score on 2026-11-13 (5 sessions), 2026-12-07 (21) and 2027-02-05 (63).

## My predictions (stated before running)
* H-SE1 passes: power law over exponential, because volatility has a long memory.
* n is about 0.85–0.95 (near-critical).
* p is about 0.7–1.0.
* H-SE2 passes.
* H-OM1 is a coin flip: there are few out-of-sample mainshocks.
