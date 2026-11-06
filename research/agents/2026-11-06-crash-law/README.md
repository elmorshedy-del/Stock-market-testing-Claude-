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

---

## Results (run 2026-11-06 on data to the 2026-11-05 close)
**Deviation from the pre-registration, reported:**
* The whole-market dollar-volume proxy (^GSPC share volume × index level) **failed its cross-check**. It gave $1.3bn for Sep–Oct 1987 against KO's NYSE $10.20bn (ratio 0.13).
* As pre-registered, LIN therefore uses KO's whole-market anchors: $20.57bn in Oct 1987 and $293bn in May 2010, log-linear in time and extended beyond the anchors.
* The proxy re-scaled at both anchors is reported as a sensitivity.
* Nothing else changed.

### Part A: the five crashes
* **A1: replicates.** Our LIN gives 46.51 / 16.73 / 6.27 / 10.78 / 0.61% against KO's 46.43 / 16.77 / 6.27 / 10.79 / 0.61%. SQRT gives 1987 = 1.33% (KO: 1.3%).

| Crash | Actual | LIN | SQRT | SQRT-now | Sale needed, LIN | Sale needed, SQRT-now | SQRT-now sale as % of a day's volume |
|---|---|---|---|---|---|---|---|
| 1929 | 25% | 46.5% | 3.9% | 6.9% | 0.46× | 13× | 3,492% |
| 1987 | 32% | 16.7% | 1.3% | 1.7% | 2.1× | 373× | 24,952% |
| Soros, Oct 22 1987 | 22% | 6.3% | 1.6% | 1.4% | 3.8× | 242× | 554% (in 6 minutes) |
| SocGen 2008 | 9.44% | 10.8% | 0.70% | 0.62% | 0.87× | 232× | 6,427% |
| Flash crash 2010 | 5.12% | 0.61% | 0.16% | 0.24% | 8.7× | 473× | 706% (in 20 minutes) |

"Sale needed" is the multiple of the documented sale that would produce the actual fall.

* **A2: the week-before liquidity state hardly helps.** σ in the 5 sessions before each event was 0.9–1.75× KO's σ, so SQRT-now is 0.9–1.8× SQRT.
  * My prediction (1.5–4× higher) was too optimistic.
  * The square-root law with the pre-event state still needs 13–473× the documented selling, i.e. 5.5 to 250 days of total volume squeezed into windows of minutes to days. That is physically impossible.
* **A3:** LIN needs 0.5–3.8× the documented sale for the four slower events. For the flash crash it needs 8.7×, i.e. 13% of a day's volume in 20 minutes, near the limit of what traded. KO also say speed is the problem there.

### Part B: the volume bound, 54 S&P shock days (1955-09-26 to 2026-11-05)
* **HB1 (baseline) holds, 54/54.** SQRT needs net selling of 1.7–60× the day's entire volume (median 8.3×). With Y = 0.9 it is worse (median 15×).
* **HB2 holds, 54/54.** With the week-before σ and volume, SQRT-now still needs 1.4–113× the day's volume (median 8.4×).
  * By M3 class, median: build-up 5.2×, mid 9.2×, abrupt 12.8×.
  * In the direction the liquidity-state theory predicts (stressed build-ups need less), but nowhere near feasible. My predicted 70–80% was too low; it is 100%.
* **HB3 holds.** LIN needs ≤ 25% of the day's volume on 80% of days (90% CI 70–89%); median 14%.

  | Sensitivity | Share of days ≤ 25% |
  |---|---|
  | k ± 2 s.e. | 76–80% |
  | volume ×3 / ÷3 | 87% / 63% |
  | proxy re-scaled at both anchors | 63% |

  * The worst days are the 1950s–60s (small market, so lower LIN sensitivity), up to 63% of the day's volume.
* **Nov 5, 2026:** SQRT needs 24× the day's volume, SQRT-now 7.0×, LIN 9.2%.
* **Caveat on HB1/HB2:** the bound treats the day's net selling as one aggregate flow. Donier & Bonart find the market responds to the square root of total imbalance, which supports this. If instead a day's selling came as k independent bursts with liquidity fully refilling between them, the bound loosens by √k: about 3× for 10 bursts, 10× for 100.

### Part C: leveraged-ETF tipping point (descriptive)
* **Feedback gain** (extra fall caused by leveraged-ETF rebalancing ÷ initial fall):

  | Market boundary | Linear law | Square root |
  |---|---|---|
  | S&P complex alone | 0.07 | 0.02–0.05 |
  | Nasdaq-100 complex alone | 0.60 | 0.08–0.19 |
  | Semis complex alone | **3.1–3.3: runaway** | 0.30–0.66 |
  | Whole market | 0.61 (amplifies any fall 2.6×) | 0.06–0.13 |

  * Whole-market leveraged-ETF selling is $15.7bn per 1% S&P fall: 1.7% of total stock + futures volume (about $923bn/day).
* **Nov 5 close check** (move predicted from the known rebalancing flow, 15:30 → close):

  | | Actual | Square root | Linear |
  |---|---|---|---|
  | Whole market (S&P) | −0.30% | −0.23% | −2.0% |
  | Nasdaq-100 | −0.66% | −0.43% | −3.3% |
  | Semis | −1.46% | −1.91% | −23.9% |

  * The known forced flow moved prices about as the square root predicts. Linear over-predicts by 5–16×.
  * Caveat: if swap dealers hedged during the day, the close is the wrong window. Linear on the whole market would then not be ruled out (it would be −2.0% of the day's −4.4%).
* **The linear law with semis as its own market predicts a runaway** (gain above 3, −24% at one close). Neither happened, so that version is ruled out. My Part C prediction was right.

### Verdict (by the pre-registered interpretation rule)
* **HB1, HB2 and HB3 all hold.** So order flow can make index crashes only if the price response at crash scale is about linear, or liquidity breaks during the day. The normal or week-before square-root law cannot. This is robust: 54/54 days, the 1955–2026 span, and both values of Y.
* **But "about linear" is not a fixed law either.** On the one forced flow we can compute exactly, the Nov 5 close, prices followed the square root and the linear law over-predicted 5–16×.
* **The reading that fits both:**
  * calm, deep markets (and the close) respond in the square-root way;
  * crash days need a response roughly 10× more sensitive than the week before showed. That is a regime change within the day, Donier & Bonart's "liquidity breakdown". KO's linear law describes that broken regime as an average.
  * The alternative this test cannot exclude: the falls are mostly news, with prices moving without trading.
* **S4 status:** still contested, but sharper. Crash size is not a fixed function of the selling. The decisive unknown is how the response per unit of selling changes inside a crash day.

### What this means for a trader
* **Normal-time liquidity math understates crash moves by about 10×.** That covers square-root impact, "it's only X% of volume", and the forced-flow sizes we computed. The week before does not reveal it: even build-up shocks needed 5× the day's volume under the square-root law.
* **Leveraged-ETF feedback is small while liquidity holds** (square-root gain about 0.1). If liquidity breaks and the linear law takes over, the same flows could amplify an S&P fall about 2.6× (whole-market gain 0.61).
  * The danger is regime-dependent, so the thing to watch is whether liquidity has broken: price moving far per unit of selling.
  * The size of the flow alone does not tell you.

### Next (Part D, needs approval to buy data)
* **Data:** ES and NQ trades with aggressor side on the selloff days (2024-08-05, 2025-04-03/04/07, 2026-11-05) and about 5 calm days. We already hold ES trades for one calm day (2026-10-27, `2026-11-04-deferred-days/data`). About $25–35 at the $2.82/day quote; I will get an exact quote first.
* **Measure:** price response per unit of signed volume, minute by minute.
* **What it decides:**
  * whether liquidity breaks (response jumps);
  * whether it is giant sellers (huge imbalance, normal response);
  * whether it is news (moves without imbalance);
  * and whether the break comes before the fall, which would be an early warning.

Files:
* `prep.py` → `data/` (gitignored);
* `test.py` → `out/crash.json`, `out/days.csv`;
* `figure.py` → `out/crash_law.png`.
