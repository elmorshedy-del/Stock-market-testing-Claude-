# Crash law (S4): what sets the size of a selloff, giant sellers or thin liquidity?

**Status:** pre-registered. This file is committed and pushed before any new number is computed. While designing, I checked by hand only that Kyle & Obizhaeva's published 1987 values reproduce: 16.7% (linear) and 1.3% (square root).
**Law:** FOUNDATION.md S4 (crash law), with F1 (impact shape), M1 (business time) and F4/M4 (liquidity).
**Owner's approval:** "Yes we can do four", given the papers were read in full first.
**Cards read in full before designing this** (memory/papers/):
* Kyle & Obizhaeva 2023 and 2016;
* Benzaquen, Donier & Bouchaud 2016;
* Bucci et al. 2019 and 2020;
* Donier & Bouchaud 2015;
* Donier & Bonart 2015.

## The question, as the reading sharpened it
Two explanations of crash size compete:
* **Giant sellers (KO).** A fall is linear in the net selling Q, amplified in big, fast markets: fall ∝ σ·(W/C)^(1/3)·Q/V. Crashes are just very big bets.
* **Thin liquidity (physics).** Impact is square root, fall = Y·σ·√(Q/V). That is far too small to make a crash at normal liquidity. Crashes need the market's liquidity to thin or break: after run-ups (Donier & Bouchaud 2015), or under sustained one-sided pressure (Donier & Bonart 2015).

KO's own data cannot decide this:
* the impact exponent is 0.57 ± 0.04, with linear supported only in one top bin;
* crash bets lie more than 10× beyond their calibration data.

**What we can do for free:** replicate the five documented crashes under each law, then ask, for every large S&P down day since 1955, **how much net selling each law needs to produce the fall, compared with all the volume that traded that day.** A law that needs more one-sided selling than the day's entire volume cannot be the mechanism.

## Impact laws (constants fixed from the papers, not fitted)
* **LIN (KO 2023, Eq. 15):**
  ΔlnP = (k/10⁴)·(P·V·g/40e6)^(1/3)·(σ/0.02)^(4/3)·Q/(0.01·V), with k = 5.00 (s.e. 0.38).
  * P·V = whole-market dollar volume per day; g converts to 2005 dollars; σ = daily volatility.
* **SQRT (KO 2023, Eq. 17, "Inv-SQRT"):** ΔP/P = (2 × 12.08/10⁴)·(σ/0.02)·√(Q/(0.01·V)), i.e. Y·σ·√(Q/V) with Y = 1.21.
  * Sensitivity: Y = 0.9 (Bitcoin; KO 2016 with the ramp factor 1.5).
* **SQRT-now (liquidity state):** SQRT with σ and V measured over the 5 sessions just before the event, instead of a normal month.

## Part A: the five documented crashes (replication and extension)
* **Inputs** (KO 2023 text and Tables I–VI):

  | Event | Sale Q | Market volume V | σ | g | Actual fall |
  |---|---|---|---|---|---|
  | 1929, Oct 24–30 | $1.181bn | $444.97m | 2.00% | 9.42 | 25% |
  | 1987, Oct 15–20 | $13.75bn | $20.57bn (futures 10.37 + NYSE 10.20) | 1.35% | 1.54 | 32% |
  | Soros, Oct 22 1987 | $309.6m | $13.52bn (futures only) | 8.63% | 1.54 | 22% |
  | Société Générale, Jan 21–23 2008 | €50bn | €180.49bn | 1.10% | ×1.4690 $/€ × 0.92 | 9.44% |
  | Flash crash, May 6 2010 | $4.37bn | $293bn (futures 132 + stocks 161) | 1.07% | 0.90 | 5.12% |

* **A1, replication.** Our LIN reproduces KO's 46.43 / 16.77 / 6.27 / 10.79 / 0.61% within 0.3 percentage points, and our SQRT gives 1987 ≈ 1.3%. If not, stop and find the error.
* **A2, liquidity state (new).** SQRT-now: σ_now = SD of daily log returns over the 5 sessions before the event window starts; V scaled by the ratio of the 5-day to the prior-month average volume.
  * Sources: ^GSPC for 1929 (closes only, V unchanged), 1987, Soros (window Oct 15–21, crash included) and 2010; ^STOXX50E closes for SocGen (V unchanged).
* **A3, selling needed.** Invert each law: the sale that would produce the actual fall, as a multiple of the documented sale.

## Part B: the volume bound on every large S&P down day
* **Days:** the S&P shocks of the M3 study (`2026-11-06-signature-test/out/shocks.csv`): a down day of at least 6× the trailing 5-year median |return|, with no ±6× day in the prior 21 sessions. That is 54 days, 1955–2026, including 2026-11-05. Keep those with ^GSPC volume > 0 over sessions −26…0.
* **Per day t:**
  * fall f = −ln(Cₜ/Cₜ₋₁);
  * σ_norm = SD of daily log returns over sessions t−26…t−6; σ_now = SD over t−5…t−1;
  * V_norm and V_now = mean ^GSPC share volume over the same windows; V_day = volume on day t.
* **Net selling each law needs,** and the share of the day's volume it represents (F):
  * SQRT: q = (f/(Y·σ_norm))² in units of V_norm; F_sqrt = q·V_norm/V_day.
  * SQRT-now: q = (f/(Y·σ_now))² in units of V_now; F_now = q·V_now/V_day.
  * LIN: q = 0.01·f/[(k/10⁴)·(PV·g/40e6)^(1/3)·(σ_norm/0.02)^(4/3)]; F_lin = q·V_norm/V_day.
* **Whole-market dollar volume PV (for LIN only; it enters as a cube root):**
  * ^GSPC share volume × ^GSPC close × c, with c set so that the April 2010 monthly average equals KO's $161.41bn stock-market volume;
  * × (1 + 0.82) after 21 Apr 1982 (S&P futures; KO's 2010 futures/stock ratio 132/161), × 1 before;
  * × g(t) = GDPDEF(2005)/GDPDEF(t) (FRED).
  * **Cross-check before results:** the proxy for Sep 15–Oct 14 1987 must give stock volume within 2× of KO's NYSE $10.20bn. If not, report it and use PV = KO's 1987 and 2010 anchors, interpolated in logs.
  * **Sensitivity:** PV × 3 and ÷ 3 (moves F_lin by ∓31% / +44%).
* **Hypotheses:**
  * **HB1.** SQRT needs F_sqrt > 1 (more net selling than the day's whole volume) on most days (> 50%). **This is close to guaranteed by the shock definition** (a 6× median day is about 3.5σ, and (3.5/1.21)² ≈ 8 days of normal volume). It is reported as the baseline, not as evidence.
  * **HB2 (the informative one).** SQRT-now still needs F_now > 1 on most days.
    * Also reported: medians for build-up vs abrupt shocks (M3 classes).
    * The liquidity-state theory predicts lower F_now after a build-up, because liquidity is already thin.
  * **HB3.** LIN needs F_lin ≤ 0.25 (net selling at most a quarter of the day's volume) on most days.
* **Interpretation rule, fixed now:**

  | Outcome | Reading |
  |---|---|
  | HB1, HB2 and HB3 all hold | Order flow can make index crashes only if the response at crash scale is about linear, or liquidity breaks during the day. The normal or pre-shock square-root law cannot. |
  | HB2 fails | The pre-shock liquidity state is enough; no linear regime is needed. |
  | HB3 fails | Even the linear law needs implausible selling, so news (moves without trading) must be part of crashes. |

* **Uncertainty:** report the 90% bootstrap interval of each share (resampling days). Also report Y = 0.9 and k ± 2 s.e.

## Part C: today's leveraged-ETF tipping point (descriptive)
* **Inputs:** from the forced-flows study (`2026-11-06-forced-flows/out/ff.json`): ψ = ΣL(L−1)·A/V, σ, and daily dollar volume per complex (SPX, NDX, SEMIS).
* **Calculation:** for an initial fall x ∈ {1%, 3%, 5%}, leveraged ETFs must sell ψ·x of a day's volume. Each law gives the extra fall that causes; gain G = extra fall ÷ x. Flag G ≥ 1 as runaway.
* **Two boundaries for "the market":**
  * the complex alone (its own volume and σ);
  * the whole US market (all complexes' selling summed against stocks + futures volume, market σ).
* **Check against 5 Nov 2026:** predicted vs actual 15:30→close move for each complex.

## Part D: the decisive measurement (proposed; needs the owner's approval to buy data)
* **Data:** ES and NQ trades with the aggressor side (Databento) on the selloff days (2024-08-05, 2025-04-03/04/07, 2026-11-05) and 6 matched calm days, about $2.82/day, about $34.
* **Measure:** price change per unit of signed volume, minute by minute.
* **How the outcomes map to the explanations:**

  | If, on selloff days… | Supports |
  |---|---|
  | the imbalance is huge and the response per unit is normal | giant sellers (KO) |
  | the response per unit jumps | liquidity breaking (physics) |
  | prices move with little imbalance | news |

* **Not run here.**

## My predictions (stated before running)
* **A1:** replicates.
* **A2:** SQRT-now raises the square-root predictions 1.5–4×, but they stay at least 3× below the actual falls for 1929 and 1987.
* **B:** HB1 true on 90% or more of days; HB2 true on about 70–80%; HB3 true on about 80%. Build-up shocks need less selling under SQRT-now than abrupt ones.
* **C:** LIN with the semis complex as its own market gives G > 1, which visibly does not happen. LIN on the whole market and SQRT give G < 1.

## Reproduce
```
python prep.py    # Yahoo ^GSPC (with volume) and ^STOXX50E, FRED GDPDEF -> data/ (gitignored)
python test.py    # Parts A-C -> out/crash.json, out/days.csv
python figure.py  # out/crash_law.png
```
