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
