# Polymarket's December-Fed odds: how do markets digest the shifts? A stress test on rate-sensitive assets

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02
**Type:** pre-registered test. Written and pushed after downloading the Polymarket odds (the exposure) and before any asset return was joined to them.
**Owner's ask:** "Polymarket on the December expected decision has shifted a lot lately, since September exactly. Can we establish any correlation in how the market behaves as these shifts get digested? It doesn't have to be up or down… any kind of aberration in how stocks behave, especially interest-sensitive ones. Get the extremely sensitive ones so it's a stress test, and also other market holdings that can reflect a relationship."

## The exposure (seen before writing this)
* **Market:** Polymarket "Fed Decision in December?" (2026; event created Jul 30, resolves Dec 10). Hourly prices of each outcome (−50, −25, 0, +25, +50 bps).
* **Expected change E[bps]** = Σ p_i × bps_i, with prices normalised to sum to 1, read at **16:00 ET** each trading day.
* **Path:**
  * P(hike) ~28–31% in mid-August → 61% by Sep 11 → 72% late September → 78% mid-October → 71% after the Oct 28 FOMC (held, two hawkish dissents).
  * E[bps] rose from about +5 to +20.
* **Replication markets:** December 2025 (Jul 31 → Dec 10 2025) and December 2024 (Aug 6 → Dec 18 2024), built the same way.

## Assets (Yahoo daily closes)
* **Stress panel (extremely rate-sensitive):** TLT (20y+ Treasuries), REM (mortgage REITs), ITB (homebuilders), XLRE (REITs), XLU (utilities), KRE (regional banks), IWM (small caps), ARKK (long-duration growth), XBI (biotech).
* **Rate gauges:** 3-month bill (^IRX), 5-year (^FVX), 10-year (^TNX) yields.
* **Cross-asset:** SPY, QQQ, XLF, GLD, the dollar index, BTC-USD, TSLA.

## Tests
* **H1 (primary), the same-day sensitivity:** each asset's daily return regressed on ΔE[bps] (16:00 to 16:00), scaled per +5bps hawkish shift. Day-block bootstrap (5-day blocks, 2,000).
  * Primary sample: the 2026 market, Jul 31 → Oct 30. Holm across the 9 stress assets.
  * **Predicted signs for a hawkish shift:** TLT, REM, ITB, XLRE, XLU, IWM, ARKK, XBI down; KRE ambiguous (margins vs funding and credit); yields up; dollar up; gold down.
  * **Replication:** the same slopes in the 2024 and 2025 markets. Same sign in both = replicated.
* **H2, digestion and lead-lag:**
  * (a) Does ΔE at t predict returns at t+1 and t+2 (slow digestion)? Prediction: no.
  * (b) Does the 5-year yield change at t predict ΔE at t+1 (Polymarket lags the bond market)? Prediction: yes.
* **H3, does Polymarket add anything beyond the bond market?** Asset returns regressed on ΔE *and* the 5-year yield change together. Prediction: the Polymarket coefficient ≈ 0 once yields are in.
  * Descriptive: "disagreement days" (top-decile |ΔE| while the 5-year yield moved the other way).
* **H4, is the market unusually rate-sensitive now? (the "aberration")**
  * The 40-session beta of each stress asset to the 5-year yield change, Sep–Oct 2026, vs its own 2020–2026 distribution of 40-session betas (percentile).
  * And SPY's beta: is "higher yields = lower stocks" stronger than usual?
* **H5, abnormal activity on big-shift days:** stress-asset volume vs the 20-day average, and |return| in σ units, on top-decile |ΔE| days vs other days (2026 market).

## Limits stated now
* About 65 trading days in 2026 (and ~90 in each replication market).
* Polymarket moves on the same macro news that moves markets, so same-day correlation is co-movement, not causation. H2 and H3 are there to separate "the market reacts to Polymarket" from "both react to news".
* Thin hours on Polymarket can create stale or jumpy prices. The odds are read on the hour at 16:00 ET.

## Results (`polyfed.py` → `out/results.json`, `out/daily_2026.csv`; `figure.py` → `out/polymarket_fed.png`; $0)
**Exposure:**
* 2026 market: 65 days, E[bps] +8.0 → +18.6, daily SD 1.0bp.
* 2025 market: 90 days, −17 → −25.
* 2024 market: 93 days, −29 → −24.
* Same-day correlation of ΔE with the 5-year yield change: 0.52 (2026), 0.39 (2025), 0.32 (2024).

### H1: same-day reaction per +5bp hawkish shift
| Asset | 2026 | p | 2025 | 2024 | Same sign in all 3? |
|---|---|---|---|---|---|
| **Utilities (XLU)** | **−1.71%** | **<0.001 (Holm 0.000)** | −0.52 | −0.01 | yes |
| REITs (XLRE) | −0.93% | 0.009 (Holm 0.07) | −1.05 | −0.94 | yes |
| Mortgage REITs (REM) | −1.25% | 0.012 (Holm 0.08) | −0.91 | −0.26 | yes |
| Long Treasuries (TLT) | −0.84% | 0.019 (Holm 0.11) | −0.62 | −0.52 | yes |
| Small caps (IWM) | −0.96% | 0.021 (Holm 0.11) | −1.35 | +0.57 | no |
| Homebuilders (ITB) | −2.19% | 0.10 | −2.21 | −0.90 | yes |
| Regional banks (KRE) | −0.75% | 0.13 | −1.09 | +1.68 | no |
| ARKK | −0.98% | 0.33 | −1.69 | +0.72 | no |
| Biotech (XBI) | −1.28% | 0.34 | −1.33 | −0.60 | yes |
| 5-year yield | **+13.5bp** | <0.001 | +5.0 | +5.4 | yes |
| 3-month bill | +4.4bp | <0.001 | +2.0 | +1.7 | yes |
| Dollar | +0.54% | 0.007 | +0.36 | +0.23 | yes |
| Gold | −2.19% | 0.010 | +0.03 | −0.50 | no |
| SPY / QQQ / TSLA | −0.15 / −0.05 / −1.24% | 0.48 / 0.67 / 0.39 | | | no |

* **The registered prediction holds for the bond proxies.** All 9 stress assets fell on hawkish shifts in 2026.
  * Utilities pass Holm; REITs and mortgage REITs are near it.
  * TLT, REM, ITB, XLRE, XLU, XBI, the yields and the dollar replicate in sign in both earlier markets.
  * Small caps, regional banks and ARKK flip sign in 2024, a cutting cycle in which hawkish days came with good growth news.
* **The broad market (SPY/QQQ) barely reacts.**

### H2: digestion and lead-lag
* **Lead-lag:** neither way at the daily level.
  * The 5-year yield does not predict tomorrow's Polymarket shift (−0.01, p 0.33), and Polymarket does not predict tomorrow's yield (+0.20, p 0.76).
  * The registered prediction that Polymarket lags bonds is **not supported** at daily resolution.
* **Continuation:**
  * At t+1, the stress-panel average is +0.61% (p 0.22).
  * **At t+2 it is −1.28% (p < 0.001) in 2026, but −0.37 (p 0.22) in 2025 and +0.57 (p 0.05, opposite) in 2024.**
  * Not replicated; logged as anomaly P1, not a rule.

### H3: beyond the bond market
* In 2026, once the 5-year yield is in, Polymarket adds nothing for equities (all p ≥ 0.16).
* The exception is **TLT +0.62% (p 0.011)**: for a given 5-year move, a hawkish Polymarket shift goes with long bonds doing *better*. That is a bear-flattening signature, with hikes priced at the front end and the long end anchored.
* In 2025, Polymarket did carry equity information beyond yields: ITB, XLRE, XLU, KRE, IWM, ARKK, XBI, SPY and TSLA all negative at p < 0.05.
* No disagreement days in 2026: every top-decile shift moved with the 5-year.

### H4: the aberration, rate sensitivity now vs 2020–26 (40-session beta to the 5-year yield, % per +10bp)
| Asset | Now | 2020–26 median | Percentile |
|---|---|---|---|
| Utilities | −1.06 | −0.42 | **5th (most sensitive since 2020)** |
| Mortgage REITs | −1.26 | −0.42 | 14th |
| Homebuilders | −2.18 | −0.98 | 14th |
| Regional banks | **−0.70** | **+0.35** | 24th (**sign flipped**) |
| REITs | −0.74 | −0.58 | 38th |
| Long Treasuries | −0.93 | −1.20 | 88th (less sensitive: curve flattening) |
| QQQ / ARKK / TSLA | **+0.59 / +0.72 / +0.64** | −0.13 / −0.47 / −0.27 | 81st / 74th / 71st (**sign flipped**) |
| SPY | +0.09 | −0.05 | 56th |

### H5: big-shift days (top decile |ΔE|, 7 days)
* Slightly more activity:
  * stress-asset volume 1.16× vs 1.06× normal; SPY 1.09× vs 0.97×;
  * |return| 0.89σ vs 0.85σ.
* Not a large effect.

### Verdict
1. **Established (replicated across three December markets):** a hawkish shift in December odds comes with same-day falls in the bond proxies (utilities, REITs, mortgage REITs, homebuilders, long Treasuries) and a stronger dollar. The broad index barely moves.
2. **The 2026 aberrations:**
   * The 5-year yield moves ~2.5× more per shift than in 2024/25: bonds are pricing a path, not one decision.
   * The bond proxies are 2–3× more rate-sensitive than normal; utilities are the most sensitive since 2020.
   * **Regional banks flipped:** they now fall when yields rise. Rate rises read as funding and credit stress, not a margin tailwind.
   * **Tech, ARKK and TSLA currently move *with* yields.** The recent driver is risk-on/risk-off (the late-October flight into bonds while tech sold off), not discount rates.
   * Gold turned rate-sensitive.
3. **Digestion:** markets and Polymarket move together on the day, with no daily lead either way. Polymarket adds nothing beyond the 5-year yield this year. The t+2 continuation (P1) is a curiosity, not a rule.
4. **Stress-test read for December:** if the odds swing further hawkish (or the Fed hikes), the most exposed are homebuilders, mortgage REITs, utilities, REITs and regional banks.
   * SPY and TSLA are not the rate victims in the current regime; their recent link to yields runs through risk appetite.
