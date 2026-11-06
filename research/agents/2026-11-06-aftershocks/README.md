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

## Results (run 2026-11-06, before the open)
Files: `hawkes.py` → `out/hawkes.json`.

### H-SE2: self-excitation is real (PASSES, by a lot)
Out-of-sample log-likelihood gain over a constant rate, 2008–2026:

| | power-law Hawkes vs constant | exponential Hawkes vs constant | branching ratio n (fit on data before 2008) | share of out-of-sample big days attributed to triggering |
|---|---|---|---|---|
| S&P 500 | +387 [222, 583] | +384 [225, 574] | 0.87 | 90% |
| Nasdaq-100 | +274 [160, 414] | +264 [150, 404] | 0.95 | 96% |
| SOX | +269 [133, 410] | +256 [118, 397] | 0.90 | 97% |

* All three markets are near-critical. Each big day (|r| ≥ 3 × the 5-year median, about 1.7% for the S&P now) triggers 0.87–0.95 more big days on average.
* About 9 in 10 big days are aftershocks of earlier big days rather than shocks out of calm.

### H-SE1: power-law vs exponential memory (FAILS on the primary S&P; PASSES in both replications)
* **S&P:** ΔLL +2.5, 90% CI [−2.5, +7.2]. This is the primary test, and it fails.
* **Nasdaq-100:** +10.5 [2.6, 19.5]. **SOX:** +12.7 [2.2, 26.4]. Long-memory triggering beats short memory for tech and chips.
* **Kernel exponents:**
  * S&P: p = 2.13, c = 14.7 days;
  * Nasdaq-100: p = 1.67, c = 14.1;
  * SOX: p = 1.46, c = 7.1.
* Chips have the longest memory of fear. My predicted p of 0.7–1.0 was wrong: the bare kernel decays faster.

### H-OM1: Omori law after mainshocks (not supported; underpowered)
* **S&P, 21 in-sample and 11 out-of-sample mainshocks:** ΔLL +0.1, CI [0.00, 0.21].
  * The power-law fit collapsed into an exponential (c = 1,614, p = 13.7, which is about e^(−t/118)), so the two models are the same curve. This is not support for a power law.
* **Nasdaq-100 and SOX:** only 5 and 1 in-sample mainshocks, so the fits are meaningless.
* **Descriptive:** after an S&P mainshock, the extra big-day rate decays with a time constant of about 120 sessions. Fear lingers for months.
* **Consistency check.** A linear Hawkes process with kernel time τ and branching ratio n decays after a shock with time constant τ/(1 − n).
  * The all-days exponential fit gives 16.0/(1 − 0.821) ≈ 89 sessions.
  * The mainshock stacking gives about 122.
  * Two separate analyses agree in order of magnitude.

### Forward forecast (logged 2026-11-06 before the open; to be scored)
* **Status of the latest move:** the S&P's event threshold is now 1.71%. Nov 5 (−4.45%) just missed the mainshock bar (4.55%). Recent event days are Oct 30 and Nov 5 only, so this is not yet a cluster.
* **Probability today (Nov 6) is a big day:** 13.4%, against 10.1% unconditional.
* **Expected S&P big days (80% interval in brackets):**

| window | Hawkes forecast | constant rate | score on |
|---|---|---|---|
| next 5 sessions | 0.63 [0–2] | 0.55 | 2026-11-13 |
| next 21 sessions | 2.36 [0–6] | 2.31 | 2026-12-07 |
| next 63 sessions | 6.44 [1–14] | 6.92 | 2027-02-05 |

* **Read:** the model sees one shock, not a storm. The storm signature would be more big days within the next two weeks, because each one raises the odds of the next.

## Addendum (exploratory, after the results; logged before the outcome)
**Shock size matters.** This is seismology's productivity law, which the unmarked Hawkes model ignores because it treats a 4.5% day like a 1.7% day. Below are S&P shocks of 6–10 times the 5-year median (Nov 5 was 7.8×) with no shock of 6× or more in the prior 21 sessions. Big-day rate per session; the normal rate is 11%:

| era | n | next session | sessions 2–5 | sessions 6–21 | sessions 22–63 |
|---|---|---|---|---|---|
| 1955–2007 | 52 | 35% | 26% | 23% | 17% |
| 2008–2026 | 23 | 30% | 44% | 29% | 24% |

* **Mainshock aftershock curves by era:**
  * before 2008 (21 mainshocks): 43% at lag 1, falling to 13% at lags 64–120;
  * 2008 on (11): 64%, falling to 19%.
  * Fear has lingered more strongly since 2008.
* **Second forecast, logged now and scored with the first on 2026-12-07.** The size-conditioned analog expects 5.0 (pre-2008 rates) to 6.7 (post-2008 rates) S&P big days in the next 21 sessions. That compares with 2.4 [0–6] from the pre-registered Hawkes model and 2.3 at the constant rate.
* **Next model:** ETAS (epidemic-type aftershock sequence), the standard earthquake model, in which the triggering grows with shock size.
