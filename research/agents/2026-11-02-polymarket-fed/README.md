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
