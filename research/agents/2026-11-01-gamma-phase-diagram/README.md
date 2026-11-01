# Is dealer gamma the control parameter of SPY's intraday dynamics? A phase-diagram test, and the first-15-minute signature

* **Owner, 2026-11-01:**
  * "maybe there are a signature for what is to come once the market opens by looking at … the first 5-15 mins";
  * "for spy we almost even predicted … the pocket and the flip … How can we turn this into strong predictive factors … like weather";
  * "/loop keep going till u find something … Be like a physicist … dealing with a chaotic system".
* **Protocol:** [METHOD.md](../METHOD.md). Written and pushed **before** any intraday data are pulled.

## Mechanism and derived predictions
* **The coupling:** dealer hedge flow is H = −Γ·ΔS. Price impact gives Δp = λ(u + H).
  * Dealers **long** gamma (engine total gamma > 0, price above the flip) sell rises and buy dips: **damped**.
  * Dealers **short** gamma (below the flip) chase: **amplified**.
* **Because dealers rebalance in discrete steps, three observables follow from one coupling:**
  * **H1, variance (the known law, calibrating the instrument):** the day's range, in units of the expected daily move σ_d = VIX(prior close)/√252, is **larger** when SPY opens below its pre-open flip than above it.
    * Dose–response: the further below the flip (in σ_d units), the larger the range.
    * Predicted ratio short/long ≈ 1.2–1.5. Confidence high; this is documented in the literature and in our dealer-sign study.
  * **H2, dynamics:** intraday 5-minute returns are **positively** autocorrelated (trending) below the flip and **negatively** autocorrelated (mean-reverting) above it, with lag-1 autocorrelation ρ ≈ −λ·Γ.
    * Predicted: ρ_short ≈ +0.02 to +0.08, ρ_long ≈ −0.02 to −0.08, difference 0.03–0.15.
    * Confidence medium: forced-flow A2 (last half hour) was weak in the predicted direction; Ni, Pearson, Poteshman & White (2021) found the effect in single stocks.
  * **H3, the signature (trading use):** the first 15 minutes' move (09:30 → 09:45) **continues** to the close more often below the flip, and **reverts** more often above it.
    * Predicted continuation 53–56% vs 44–48%. Under a bivariate-normal approximation P ≈ ½ + arcsin(ρ_eff)/π, so even a real effect gives only a few points of edge.
    * Confidence medium-low.
    * This is the "Simpson in phase space" hypothesis: the weak pooled 09:35 rule may be two opposite regimes mixed together.
* **Cross-check (METHOD 11):**
  * If H1 and H2 both hold, the variance amplification and the autocorrelation must be of consistent size. For returns with lag-1 autocorrelation ρ, the 30-minute variance ratio is VR(6) ≈ 1 + 2Σ_{j=1..5}(1 − j/6)ρ^j.
  * Reported, no pass bar.

## Design
* **Days:** SPY sessions 2020-01-03 to 2026-10-12, matching the pre-open map history ([flip-wicks](../2026-10-27-flip-wicks/) `out/preopen_levels.csv`: flip incl. 0DTE from day D's OI and day P's closing IVs, plus total gamma `gex_open`).
* **Intraday data:** SPY 1-minute bars, Databento XNAS.ITCH (Nasdaq prints), 09:30–16:00. Cost checked: ~$2.69 for SPY+QQQ+TSLA 2020–2026; QQQ and TSLA are for later iterations.
* **State (known at 09:30):**
  * **Primary:** short = 09:30 open below `flip_incl`; long = above.
  * **Dose:** d = (open − flip)/(σ_d·open).
* **Outcomes:**
  * **O1** = (RTH high − low)/open/σ_d.
  * **O2:** lag-1 autocorrelation of 5-minute log returns, pooled within state with the day mean removed. Also the per-day VR(6).
  * **O3:** r15 = ln(P09:45/P09:30), rest = ln(P16:00/P09:45). Continuation = same sign. Regression rest = a + b·r15 + c·r15·short.
* **Tests (primary family, Holm over three):**
  * **H1:** mean O1 short > long. Also Spearman(d, O1) < 0, reported with a quintile plot.
  * **H2:** ρ_short − ρ_long > 0.
  * **H3:** c > 0, and P(cont | short) − P(cont | long) > 0.
* **p-values:** day-block bootstrap (5,000) for differences, plus a **circular-shift null** of the state series across days (all offsets ≥ 20 days), which keeps regime persistence.
* **Multiverse (reported in full):** return interval {5, 10, 15 min} × opening window {5, 15, 30 min} × state definition {flip-based, sign of `gex_open`, `gex_open` percentile bottom vs top third (trailing 252 days)} = 27 cells. Joint p from the median z vs the circular-shift null.
* **Controls (reported):**
  * Within VIX terciles (trailing 252 days), each effect's sign.
  * Era split per OWNER_NOTES: R1 2020–21 vs R2 2022+ (the 0DTE era).
* **Pass:** H1, H2, H3 each Holm p < 0.05 with the predicted sign. H1 must pass for H2/H3 to be read: if the known law fails, the instrument is suspect.
* **Trading reading, if they pass:**
  * At 09:45 the state plus the opening move gives a continuation-or-reversion forecast for the rest of the day, and an expected range.
  * The forecast **updates** if price crosses the flip intraday, as a nowcast would.
  * In exit terms: on short-gamma continuation days, trail rather than take fixed targets; on long-gamma days, take profits into extensions.

## Iteration 1 results (`phase.py` → `out/phase.json`, `out/days.csv`; `figure1.py` → `out/phase_iter1.png`)
* **Data:**
  * 1,701 SPY sessions (2020-01-03 to 2026-10-12): 912 opened below the pre-open flip, 789 above.
  * Databento XNAS 1-minute bars ($2.69 for SPY+QQQ+TSLA).
  * The first run was interrupted before writing anything; the vectorized rewrite implements the same registered design.

![iteration 1](out/phase_iter1.png)

| | Prediction | Result | Verdict |
|---|---|---|---|
| **H1 range** | ×1.2–1.5 below vs above; dose–response | **×1.33** (1.026 vs 0.770 expected daily moves); quintiles 1.16 → 0.98 → 0.87 → 0.77 → 0.75; Spearman −0.42; circular-shift p < 0.002, Holm ≈ 0; multiverse median z **6.8** | **pass**, every year, both eras, every VIX third |
| **H2 persistence** | ρ_short +0.02…+0.08, ρ_long −0.02…−0.08 | ρ diff **+0.011** (p 0.20, Holm 0.40); multiverse median z 0.3 | **fail**: right sign, about 5–10× too small |
| **H3 first-15-min signature** | continuation 53–56% vs 44–48% | **50.5% vs 50.3%** (p 0.48); interaction c −0.13 (wrong sign, n.s.); multiverse median z −1.0 / 0.1 | **fail** |

* **Cross-check (METHOD 11):** VR(6) 0.92 below vs 0.88 above, both < 1. The variance difference (×1.33) is **not** accompanied by the persistence that a slow feedback loop would need.
  * The implied coupling λ_eff·|Γ| at 5–15-minute scales is about 0.01, a feedback multiplier of about 1.01.
* **Reading:**
  * Dealer gamma sets the **size** of SPY's day, strongly and monotonically. It does **not** make moves persist from one 5–15-minute interval to the next, and the opening move alone predicts nothing.
  * In weather terms, the pre-open map forecasts the storm's *intensity*, not its *direction*.

### Anomaly log (METHOD 13: exploratory until confirmed)
* **A. "Both regimes mean-revert" was partly an artefact (step b).**
  * Within-day demeaning biases lag-1 autocorrelation by about −1/n (−0.013 at 5 min, −0.04 at 15 min).
  * On raw returns: 1-minute +0.013 / +0.010, 5-minute −0.012 / −0.021, 15-minute **+0.008 / −0.008**.
  * The regime difference has the predicted sign at every horizon, growing with horizon (+0.002 → +0.010 → +0.016), but it is tiny.
  * The H2 difference test is unaffected, since the bias is common to both regimes.
* **B. Continuation depends on VIX × gamma (found in passing; continuation in the rest of the day):**

| | Above flip | Below flip |
|---|---|---|
| low VIX | 50% (n 450) | **45% (n 278)** |
| mid VIX | 50% (n 209) | **56% (n 203)** |
| high VIX | 44% (n 75) | 53% (n 367) |

  * Same direction in 2020–23 and 2024–26, and for the 5- and 15-minute opening windows; weaker for 30.
  * **Candidate mechanism:** feedback strength ∝ λ·|Γ|, and illiquidity λ rises with VIX. Short gamma trends only when liquidity is thin; long gamma damps harder when it is thin (44%).
  * The low-VIX/below-flip *reversion* (45%) is **not** explained by this mechanism: coupling should be about zero there, giving ~50%. It needs its own explanation, perhaps shallow dips in calm markets getting bought.
* **C. The H1 ratio drifted:** 1.5 in 2020–21, about 1.1–1.15 in 2022–24, 1.35 in 2025, 1.14 in 2026. In 2022 almost every day was below the flip (220 of 251).
* **D. The key open question about H1: is it dealer gamma or just "stress"?**
  * Opening below the flip usually follows a decline, and declines have high realized vol relative to VIX whatever dealers hold.
  * The dose–response is consistent with both. Iteration 2 separates them.

## Iteration 2 pre-registration (written before running)
* **I. Is H1 dealer gamma or stress? (separating the cause)**
  * **I-a Controls.** O1 ~ below-flip + |prior-day return| + prior-day range + |overnight gap| + prior-day ΔVIX + 5-day return, all in σ_d units. **Prediction:** the below-flip coefficient stays positive with p < 0.05 and keeps ≥ half its raw size.
  * **I-b Natural experiment (move the control parameter, not the system).**
    * Split the day-to-day change in distance-to-flip, Δd, into a **price part**, Δopen/(σS), and a **flip part**, −Δflip/(σS).
    * The flip part comes from open-interest changes (expiries, new positions) with price held fixed.
    * Regress ΔO1 (today's minus yesterday's range in σ units) on both parts.
    * **Prediction:** the flip-part coefficient is negative (the flip moving above price → bigger day), p < 0.05, and of the same order as the price part. If gamma is only a stress marker, the flip part is ~0.
  * **I-c Magnitude at fixed distance.** Among below-flip days, the partial correlation of O1 with −gex_open (more short gamma), controlling for d, is > 0.
* **II. Exploratory B, characterised (no pass bar; confirmation will be forward or on another instrument):**
  * Continuation and 15-minute raw autocorrelation by VIX tercile × state, with bootstrap CIs.
  * The same table on QQQ, using its own state (open vs the prior close's QQQ flip from `microstructure/out/td_gamma_QQQ.csv`). QQQ shares SPY's dates, so it is a weak, non-independent check, stated as such.
* **III. The practical forecast (the owner's "weather"): a 09:45 nowcast of the rest-of-day range.**
  * Target: rest-of-day high − low after 09:45, in σ_d units.
  * Predictors: state, d, first-15-minute range (σ units), |r15|, VIX percentile.
  * Fit on 2020–2023, test on 2024–2026.
  * Score:
    * out-of-sample R² vs a VIX-only baseline;
    * calibration of P(rest range > 1σ_d) by decile;
    * pinball loss of the 20/50/80% quantiles.
  * **Prediction:** state + first-15-min range beat the VIX-only baseline out of sample (R² gain > 0 with bootstrap CI excluding 0), and calibration stays within ±5 points per decile.

## Iteration 2 results (`iter2.py` → `out/iter2.json`)
| Test | Result | Verdict |
|---|---|---|
| **I-a** stress controls | Below-flip coefficient 0.255 → **0.146** with controls (keeps 57%), 90% CI [0.10, 0.19], p < 0.001. Yesterday's range (0.21) and the overnight gap (0.19) carry most of the rest | **pass** |
| **I-b** natural experiment | Flip-driven change in distance: **−0.051** (right sign), 90% CI [−0.10, +0.01], p 0.077. Price-driven part −0.007. The flip part correlates with ΔVIX (0.32), so it is not cleanly exogenous. Day after monthly opex (n 81): flip −0.12, price −0.10 | **fail (borderline)** |
| **I-c** amount of short gamma at a fixed distance | Partial Spearman **0.003** [−0.08, +0.07] | **fail** |
| **II** VIX × gamma continuation | SPY: low-VIX below-flip 45% [40, 50], mid 56% [50, 62], high 53% [49, 57]. **QQQ does not reproduce the low-VIX reversion** (52%) | exploratory B weakened |
| **III** 09:45 range nowcast | Out-of-sample R² gain over VIX-only **+0.124** [0.047, 0.205]. Almost all of it comes from the first-15-minute range (+0.118); the gamma state adds +0.006 [−0.045, +0.061]. The 20/50/80% quantiles are well calibrated (22/52/79%), but P(rest range > 1σ) is mis-calibrated (top quintile 56% forecast vs 42% observed) because I used a normal residual where the residuals are not normal | **fail on the registered calibration criterion**; the quantile forecast is usable |

* **Reading:**
  * The flip predicts the day's size beyond stress (I-a). But neither the *amount* of short gamma (I-c) nor clean day-to-day flip moves (I-b) confirm that dealer hedging is the cause.
  * The safest statement: the flip is a good **forecasting variable** for range; the mechanism is unproven. One possibility is that the flip marks where price sits relative to recently built positioning.
  * After 09:45 the opening range supersedes it.
  * **Practical:** before the open, use the flip distance to set the expected range. At 09:45, use the first 15 minutes' range: a calibrated 20/50/80% band for the rest of the day.

### Anomaly E (found in passing, 2026-11-01): the open's direction is more informative in QQQ than in SPY
* **On 1,717 common days (2020–2026), first-15-minute continuation:**
  * QQQ **53.7%** vs SPY **50.4%**. QQQ is higher in 6 of 7 years. TSLA 51.3%.
  * The gap comes from days when SPY and QQQ **open in opposite directions** (21.5%, n 370). There, SPY's own opening direction continues only **44.9%**, so the rest of the day follows **QQQ's** opening direction ~55% of the time. QQQ's own continues 54.1%.
  * When they agree: SPY 52.0%, QQQ 53.6%.
* **Artefact checks so far (b):**
  * The same pattern appears with 5-, 15-, 30- and 60-minute windows: QQQ ≥ SPY at every window.
  * The definitions are identical for both, and the effect is year-stable in sign.
* **Mechanism candidates (c):**
  1. **Information leadership:** news reaches tech first; SPY's open is diluted.
  2. **SPY opening-auction noise:** SPY's huge opening cross makes transient moves that revert.
  3. **Liquidity-led vs flow-led:** flow-physics found SPY liquidity-led and TSLA flow-led.
* **Independent predictions (d):**
  * (1) and (3): on disagreement days, QQQ's opening sign predicts SPY's rest-of-day sign.
  * (2): measuring SPY from 09:35 instead of 09:30 should raise its continuation.

## Pre-registration E (written before pulling the holdout): confirm on May 2018 – Dec 2019, data never used
* **Data:** SPY + QQQ 1-minute bars, Databento XNAS, 2018-05-01 to 2019-12-31 (cost **$0.35**). This is the smallest slice that can falsify (OWNER_NOTES data budget).
* **E1:** QQQ first-15-minute continuation > SPY's (paired by day). In-sample +3.3 pts.
* **E2 (the sharp claim):** on days when the SPY and QQQ first-15-minute moves disagree in sign, P(SPY's rest-of-day sign = QQQ's opening sign) > 50%. In-sample 55.1%.
* **E3 (mechanism 2):** SPY continuation measured from 09:35 (09:35 → 09:50 vs 09:50 → close) > from 09:30.
* **Power, stated honestly:** ~420 days and ~90 disagreement days give an SE of ~5 pts on E2. The holdout can **falsify** (e.g. ≤ 48%) but only weakly confirm.
* **Sequential rule, fixed now (METHOD 14):**
  * If E2 ≥ 52% in the holdout, extend with ES vs NQ futures (RTH, 2010–2017) **one year at a time** (~$2.4/yr), combining yearly z-scores by Stouffer.
  * **Confirm** when the combined z ≥ 3. **Abandon** if the running estimate is ≤ 50% after ≥ 400 disagreement days, or if the holdout itself is ≤ 48%.
* **One-sided p:** binomial for E2; paired day bootstrap for E1 and E3.

### Pre-registration E result: holdout May 2018 – Dec 2019 (`holdout_e.py` → `out/holdout_e.json`; 411 days; data cost $0.35)
| | In-sample (2020–26) | **Holdout (2018–19)** |
|---|---|---|
| E1: QQQ − SPY continuation | +3.3 pts | **+1.0 pt** (p 0.37) |
| E2: SPY rest follows QQQ's open on disagreement days | 55.1% (n 370) | **52.5%** (n 80, z 0.45, p 0.33) |
| E3: SPY from 09:35 − from 09:30 | — | **+1.4 pts** (p 0.29) |

* **Same direction, about half the size:** the usual shrinkage of an in-sample discovery (the winner's curse).
* **Decision: deviation from the registered sequential rule, stated openly.**
  * E2 ≥ 52% would trigger the futures extension, but a power calculation made before spending shows it cannot confirm.
  * At a true rate of 53%, a one-sided z = 3 with 80% power needs ≈ 4,100 disagreement days (≈ 19,000 sessions). At 55% it needs ≈ 1,500 (≈ 7,000 sessions).
  * All of ES/NQ 2010–2019 gives ≈ 480 disagreement days, for an expected z of ≈ 2.2 even if the effect were 55%.
  * An edge of 2–5 pts on 1 day in 5 is also of low trading value. Per the data-budget rule, **anomaly E stops here: unconfirmed, small, not worth more spend.**
  * Logged as a curiosity with the reason (METHOD 13).

## Iteration 3 pre-registration (written before running; free data already in hand): are gamma walls barriers?
* **Why:** iteration 1 showed the pre-open map forecasts the day's *size*. Can it also forecast *where* the day stops?
  * Thursday night's "realistic flush low 750–754 at the 750 put wall" was right.
  * flip-wicks H1 found the flip is a real stall level.
  * The next physical question: do the **largest open-interest strikes** act as barriers more than ordinary strikes at the same distance?
* **Mechanism:**
  * At a strike with very large open interest, dealer gamma is concentrated, and so is resting hedge liquidity and take-profit or monetisation flow.
  * Price approaching it meets the most offsetting flow, as at a reflecting barrier.
* **Confound to control (natural control group):** walls are usually round numbers, and round numbers already attract day highs and lows (positioning P4b). So the comparison is **wall vs other $5-multiple strikes at a similar distance**, which separates the open-interest effect from the round-number effect.
* **Data:**
  * SPY 1-minute bars 2020-01 → 2026-10 (in hand).
  * Call and put walls from `microstructure/out/td_gamma_SPY.csv`, using the **prior** session's walls (positions known before the open).
* **Event:** the day's high comes within 0.10% of the prior call wall (from below), or the day's low comes within 0.10% of the prior put wall (from above).
* **Outcome W1:** "stall", meaning the day's extreme ends within ±0.10% of the wall, i.e. price touched it and did not run through by more than 0.10%.
* **Comparison:** the same stall rate for every other $5-multiple strike reached on the same side within ±1% of the wall's distance from the open, on the same days.
  * A paired day-level difference (wall stall − mean control stall) with a day-block bootstrap.
* **Prediction:** wall stall rate exceeds the control rate by ≥ 5 pts, p < 0.05, for both walls. **Falsifier:** difference ≤ 0.
* **Era split:** R1 2020–21 vs R2 2022+.
* **Secondary W2:** after touching the wall, the close is back inside (below the call wall, above the put wall) more often than for the controls.
* **Design correction, written before running iteration 3:**
  * The registered "same-day" control is degenerate. If price reached the wall, it necessarily ran through every closer control strike on that day, so those controls can never stall.
  * The controls are therefore **all other $5-multiple strikes reached on any day, matched by distance from the open** (bins 0–0.5–1–1.5–2–3%) **and by roundness** ($10 multiples vs other $5 multiples).
  * The statistic is the Mantel–Haenszel-weighted difference in P(the day's extreme stops within ±0.10% of the strike | the strike was reached), wall vs non-wall. CIs come from a 20-day block bootstrap.
  * **Disclosure:** this correction was written to disk before the run but committed together with the results, not pushed before running (a process slip, logged).

### Iteration 3 result (`walls.py` → `out/walls.json`; 1,701 days, 2,224 strike-days reached, $0)
| | Wall stall rate | Non-wall (raw) | **MH difference (matched distance × roundness)** | 90% CI | n walls |
|---|---|---|---|---|---|
| **Call wall, day highs** | **42.8%** | 30.6% | **+15.3 pts** | +8.3 to +22.7 | 159 |
| **Put wall, day lows** | **6.9%** | 29.3% | **−22.1 pts** | −30.2 to −13.1 | 29 |
| W2 call wall: close back below | 59.1% | 54.2% | +5.9 pts (p 0.08) | −1.2 to +13.3 | 159 |
| W2 put wall: close back above | 37.9% | 59.1% | −22.5 pts | −36.9 to −9.1 | 29 |

* **Era split (stall MH difference):** call wall R1 +18.6 (n 56), R2 +15.0 (n 103); put wall R1 −0.2 (n 12), R2 −31.6 (n 17).
* **Round numbers alone do not stall here:** among non-walls, $10 strikes stall 27.4% / 27.7% (highs / lows) vs 33.1% / 30.7% for other $5 strikes. The round-number confound therefore biases *against* a wall effect.
* **Registered verdict: W1 fails as registered** ("both walls"). The call wall passes clearly (+15 pts, p < 0.001); the put wall reverses sign (falsifier hit).

**Reading it as a physicist: the reversal was predictable from our own prior result, and I missed it.**
* dealer-sign Part B (2026-10-16) found **call gamma damps and put gamma amplifies** SPY/QQQ ranges (classic convention, p < 0.001).
* At the strike level, that sign structure means:
  * a **call wall** is dealer *long* gamma, so hedges sell into the approach: a potential **well** (an attractor, a reflecting barrier);
  * a **put wall** is dealer *short* gamma, so hedges sell more as price falls into it: a potential **hill**, an unstable point that price runs through and overshoots.
* I registered the folklore ("put wall = support") instead of deriving the put-wall sign from the mechanism (METHOD 2). The data took the mechanism's side.
* It is still post hoc for this iteration, so it needs the checks below and an independent sample.
* **Known precedents for the attractor side:** strike pinning at expiry (Ni, Pearson & Poteshman 2005; Golez & Jackwerth 2012 for S&P futures), and the Avellaneda & Lipkin (2003) hedging model, in which long-gamma hedging creates a drift toward the strike.
* **What is new here:** the effect on *any* day, measured on the day's extreme, using the prior day's largest-OI strike.

## Iteration 3b pre-registration (written and pushed before running; free data in hand, $0)
Before trusting the call-wall barrier or the put-wall run-through, rule out the artefacts (METHOD 13b) and look for a second footprint (METHOD 11, 13d–e).
* **A1 — volatility / day-type confound.**
  * Walls may be reached on calmer days, when any overshoot is small.
  * Re-run with distance bins in σ units (σ = prior VIX/√252 × open; bins 0–0.5–1–1.5–2–3σ) and **prior-VIX tercile** added to the MH strata.
  * Pass: call-wall difference ≥ +5 pts, one-sided p < 0.05.
* **A2 — level-history confound.** Overwriters may sell calls at visible resistance, so the wall could mark a technical level rather than cause the stall.
  * (i) Drop wall cases within 0.25% of the prior day's high or the prior 5-day high (call) / low (put). Pass: call difference ≥ +5 pts.
  * (ii) **Stale walls:** the call wall from 10 sessions earlier, on days when it differs from the current wall. The gamma mechanism predicts a stale-wall difference **below** the current wall's and near 0.
  * A history mechanism predicts a stale-wall difference as large as the current wall's.
* **R — independent sample: QQQ** (its own chain and strikes; `td_gamma_QQQ.csv` walls, QQQ 1-minute bars 2020–26), same design as iteration 3 (MH, matched % distance × roundness).
  * Pass: call-wall difference > 0, one-sided p < 0.05.
  * Put wall: the difference is **< 0**, one-sided p < 0.05. The direction is now derived from the mechanism and stated before looking.
* **B — second observable: bunching** (the Saez/Chetty excess-mass estimator), SPY and QQQ.
  * Sample: days with the call wall 0.5–3σ above the open (so the high ≥ open bound sits away from the wall). Histogram x = (high − wall)/σ in 0.05σ bins over [−2.5, +1.5].
  * Counterfactual: a degree-5 polynomial fitted with [−0.15, +0.15] excluded.
  * Excess mass = (observed − counterfactual)/counterfactual inside that window. p = share of the 60 placebo window positions (same width, centres at −2.0…+1.0, |centre| ≥ 0.3) with excess ≥ observed.
  * Prediction: call wall excess > 0, p < 0.05. Put wall (x = (low − wall)/σ, wall 0.5–3σ below the open): excess ≤ 0, with the deficit or run-through sign.
* **M2 — pinning time (the attractor's footprint in time).**
  * After the first touch (within ±0.10%) of a reached strike, compute the share of the remaining session's minutes that close within ±0.10% of it.
  * MH difference, call wall vs controls (same strata as iteration 3). Prediction: > 0, one-sided p < 0.05.
* **Multiple tests:** 6 primary calls (A1, A2i, R-call, R-put, B-call, M2). The call-wall barrier counts as **established** only if A1, A2i and R-call pass and at least one of B-call or M2 passes.
  * The put-wall run-through counts as **supported** if R-put passes; with SPY's 29 events it stays provisional either way.
