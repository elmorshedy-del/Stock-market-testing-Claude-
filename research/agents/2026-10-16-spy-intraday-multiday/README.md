# Does SPY trade options levels and options flow "deterministically"? A multi-day test, 2023–2026

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-16
**Pre-registered at commit:** (this commit; pushed before any multi-day data was pulled)
**Type:** pre-registered test of the owner's hypothesis that day traders and algos trade option levels and flow almost deterministically, so the edge must be strong
**Builds on:** spy-intraday-levels Parts A–B (one day: levels no, flow yes, modestly), dealer-sign Part B (the classic convention holds for SPY on both legs)
**Verdict:** (after the run)

## Data
* **Option minute data:** ThetaData Value tier, SPY options expiring the **same day (0DTE)**, the 15 strikes either side of the money, 1-minute OHLC (volume, VWAP) and 1-minute NBBO quotes.
* **Period:** every trading day from **2023-01-03 to 2026-10-15**, excluding early closes. Oct 16 is excluded: it was the exploratory day.
* **0DTE only:** today 89% of the signed flow was 0DTE, and the next expiry would double the pull.
* **SPY's own minute price:** not on our tier (checked: permission denied). It is rebuilt from put-call parity each minute: S = K + C_mid − P_mid, the median over the 3 strikes nearest the previous minute's S.
  * **Check before use:** against Yahoo 1-minute closes on the days Yahoo still serves. Pass if the median absolute gap is under $0.05.
* **Morning map (known before the open):**
  * open interest dated day d (positions at the prior close) for every expiry on file;
  * implied vols from the prior day's end-of-day chain;
  * spot = the prior close;
  * the classic convention, which the dealer-sign Part B test supports for SPY.

## Definitions
* **Signed flow:** as in spy-intraday-levels Part B.
  * s = clip((VWAP − average of the start-of-minute and next-minute mid) ÷ half-spread, −1, 1).
  * Flow = Σ s × volume × delta × 100, with delta from the minute's mid-implied vol.
* **Live dealer gamma map at minute m:** per contract, dealer position = classic sign × morning OI − cumulative customer signed volume up to m.
  * Customers buying a call leaves dealers shorter calls. The classic sign is +1 for calls and −1 for puts.
  * Gamma uses the minute spot S_m. 0DTE contracts use the minute's mid-implied vol; other expiries use the prior day's end-of-day vol.
  * Dealer GEX per strike = Σ position × γ × 100 × S² × 0.01.
* **Day type (known at the open):** **long-gamma day** if total classic dealer GEX at the prior close (morning map) is > 0, otherwise **short-gamma day**.
* **Turns:** a minute whose spot is the highest (or lowest) of the 10 minutes either side, on the parity-spot series.

## Test FL: does flow lead SPY? (primary 1)
* **Buckets:** 5 minutes. Flow is z-scored within each day. Returns are in bp, from parity spot at bucket ends.
* **Statistic:** the coefficient on z(flow_b) in the pooled OLS ret_{b+1} = a + β·z(flow_b) + γ·ret_b.
* **Null:** each day's flow series circularly shifted by its own random offset (at least 6 buckets), 1,000 draws. One-sided p for β > 0.
* **Pass:** p < 0.025.
* **Reported with it:**
  * a sign strategy: hold sign(flow_b) in SPY for bucket b+1, gross and net of a 0.3 bp round-trip cost (SPY's one-cent spread is about 0.15–0.25 bp); all buckets, and only the top fifth of |z(flow)|;
  * long- and short-gamma days separately;
  * 2023, 2024, 2025 and 2026 separately.

## Test LG: do turns land on live gamma levels? (primary 2)
* **Levels at a turn at minute i:** from the live map as of minute i−1.
  * **Positive levels:** the 3 strikes with the largest positive dealer GEX within ±1.5% of S_{i−1}.
  * **Absolute levels:** the 3 largest |dealer GEX|.
* **Statistic:** the mean $ distance from the turn's spot to the nearest level, pooled over all turns.
* **Null:** each level in each turn replaced by a random strike within ±1.5% of S_{i−1}, of the same roundness class ($10, $5, $1) and in the same distance decile. 1,000 draws. One-sided p (observed ≤ null).
* **Primary:** **long-gamma days, positive levels.** This is the pinning hypothesis: dealers long gamma at a strike sell above it and buy below it.
* **Pass:** p < 0.025.
* **Secondary:**
  * short-gamma days (prediction: no pinning, run-through);
  * all days;
  * absolute levels;
  * **live map vs the static morning map:** does adding intraday 0DTE flow move the levels closer to the turns?

## Prediction written now
* **FL passes gross** (β > 0, p < 0.025). Net of the 0.3 bp cost, the all-bucket sign strategy is about zero; the top-fifth buckets keep a small positive edge.
* **LG does not pass** on long-gamma days, but the live map beats the static map slightly.
* **This is not a strong deterministic edge.** If there is one, it is small and short-horizon.

## Threats to validity
* **Minute-level signing** has a level bias on trending days (seen on Oct 16). The tests use within-day variation.
* **Parity spot** is quote-based, so a stale or locked minute adds noise to turns.
* **No sub-minute data,** so anything that lives in seconds is invisible here.
* **The dealer side of intraday flow is assumed** to be the opposite of customer signed volume.

## Reproduce
```bash
THETADATA_API_KEY=... python pull_days.py 2023-01-03 2026-10-15   # resumable; about 20 s per day
OMP_NUM_THREADS=1 python multiday.py
```
