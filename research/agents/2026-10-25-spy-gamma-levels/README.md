# SPY dealer gamma: the flip and next levels into Fed week, and whether the flip mattered at channel dips

* **Owner, 2026-10-25:** "Wait we didn't use gamma to check spy flips and next levels."
* **Engine:** `research/microstructure/td_gamma.py` plus `hd_gamma.day_metrics` / `flip` (classic convention: dealers long calls, short puts; 81-point grid from 0.8 to 1.2 × spot), imported unchanged. It is the same code path as the exact TSLA flip of Oct 23.
* **Data:** ThetaData Value tier.
  * Stored SPY end-of-day chains and OI run to 2026-10-14 (git-ignored).
  * Oct 15–23 pulled into the scratchpad on 2026-10-25 (licensed; not in this repo).
  * Only computed levels are written here.

## Method (fixed before computing)
1. **Verify the code path** against the engine's stored rows for 2026-10-08 and 10-09 (flip, spot, GEX).
2. **Daily rows, Oct 12–23:** spot (put-call parity at the close), flip, GEX, call wall and put wall (largest OI within 45 days and ±25%).
3. **Map after Friday's close:**
   * Oct 23 closing chain (IVs and spot) with OI dated Oct 23. That is positions at the Oct 22 close; Monday's file is not published yet, so the OI is one day stale.
   * Oct 23 expiries excluded.
   * Reported:
     * dealer GEX by strike: the largest positive strikes (where dealers dampen moves: magnets and resistance) and the largest negative ones (where dealers amplify moves: accelerants), within ±5%;
     * the total-GEX profile across prices from −6% to +6%;
     * the share of gamma by expiry (Fed decision Wed Oct 28; Fri Oct 30; monthly Nov 20).
4. **Channel check:**
   * SPY's distance to its flip (spot/flip − 1) at the start of each of the 21 decided dips, from the engine's daily history plus the new rows.
   * AUC, corrections vs bounces.
   * Forced-flow prediction: corrections start closer to or below the flip (dealers less long gamma).
   * Descriptive only, because 21 dips is a small sample. Today's dip is placed on it.
