# Patzelt & Bouchaud (2018). Universal scaling and nonlinearity of aggregate price impact in financial markets. Phys. Rev. E 97, 012304. arXiv:1706.04163
**Read:** full text, including Appendices A–C, on 2026-11-06. **Verified:** Crossref and arXiv. **Laws:** F4 (absorption and pinning), F1, F3.

## Claim
**Impact of net volume.** The price impact of the net signed volume over N trades has one universal S-shaped curve once rescaled. It is linear for small imbalances and saturates for large ones. The curve is the same at every intraday scale and across instruments.

**Impact of the sign imbalance.** The impact of the imbalance in trade signs (buys minus sells) goes back toward zero at the extremes.

**The pinned-price effect.** Extreme one-sided flow happens when the price is pinned at a level. The chance that a trade moves the mid-price falls to zero as flow becomes one-sided.

## Data
* **Nasdaq:** 12 tech stocks, 2011–2016, primary market only: AAPL, MSFT, ADBE, AMZN, CMCSA, CSCO, EBAY, GOOG, INTC, NFLX, PCLN, QCOM.
* **Nordic:** 13 OMX stocks, Oct 2011 – Sep 2015.
* **Futures:** 6 EUREX contracts (BOBL, BUND, DAX, EUROSTOXX, SCHATZ, SMI), Oct 2014 – Dec 2015.
* **Trade signs:** a trade above the mid is a buy, below is a sell; trades at the mid are dropped. Exchange signs give near-identical results.
* **Exclusions:** the first and last 30 minutes, and short days.
* **Volume:** normalised by the day's volume relative to its average.

## Method
* **Net-volume impact:** R_N(Q) = average log mid-price change over N trades, conditional on the net signed volume Q.
* **Sign impact:** R_N(E) is the same, conditional on the sign imbalance E.
* **Rescaling:** R_N(Q) ≈ R_N · F(Q/Q_N), with Q_N ∝ N^ξ and R_N ∝ N^ψ.
  * Shape: F(x) = x / (1 + |x|^α)^(β/α).
  * β = 1 means saturation; β > 1 means reversal.
  * Fit by alternating the shape and scale fits, with robust regression.
* **Trend measure:** Hurst exponents from the growth of sums: Var(Σx) ∝ N^(2H).
* **Pinning measure:** the probability that the mid changes between consecutive trades, as a function of the mean sign in the bin.

## Results
* **Shape:** α = 1.2 ± 0.6 and β = 1.3 ± 0.7 across instruments.
* **Scaling exponents:**
  * curve width ξ ≈ 0.75 (AAPL 0.84);
  * curve height ψ ≈ 0.5 (AAPL 0.53);
  * the slope of the linear part falls as N^(−0.23 ± 0.10).
* **Saturation is common:** about 100 events per day for AAPL at N = 100 sit in the saturation zone. Not anecdotal.
* **Sign impact:** it saturates sharply near a 50% sign imbalance, then goes back toward zero.
* **Persistence:** returns are nearly diffusive (slight mean reversion for large-tick names). Trade signs are persistent (H > 0.7, with autocorrelation decaying with exponent γ ≈ 0.5). The impact-curve scaling follows the sign persistence, not the volume persistence.
* **Pinned-price example.** AAPL "May 1, 2016" (a Sunday, so a date slip in the paper):
  * more than 100 market sells arrive, yet the mid moves only half a tick;
  * buy limit orders are refilled at the best price or inside the spread.
* **Tent-shaped curve.** P(mid changes) against the mean sign is tent-shaped. It does not change with N for N ≥ 50, and it goes to zero for strongly one-sided flow. The same holds across all 30 instruments.
* **Interpretation (the authors'):**
  * prices move on surprise, as in the Madhavan–Richardson–Roomans model;
  * takers size their orders to visible liquidity;
  * makers refill to match the incoming bias.
  * This is two-sided adaptation, with predictable flow counterbalanced on all intraday scales.

## Caveats (mine)
* **Intraday only:** from 10 trades up to one day; overnight is excluded.
* **Not consolidated:** primary-market data only for the Nasdaq names.
* **The key open point for the owner:** the paper does not measure what happens after a pinned episode ends.
  * Does price break in the aggressor's direction once the passive side is used up (the owner's "absorption must complete, then the move continues")?
  * Or does it reverse when the aggressor gives up?
* **Old data:** 2011–2016, before 0DTE options.

## What it means for us
* **Absorption is real, common and measurable.** One-sided aggressive flow plus a refilling passive side pins the price. The fingerprint is a high sign imbalance with a low chance of a price change.
* **This is the owner's "level that absorbs", measured.** What remains open is the "must complete" part, i.e. the direction and timing of the break.

## How we would replicate or extend it on our data
1. **Free pilot on data we hold:**
   * TSLA trades for Oct 27–28 and the 10-level book for Oct 28; ES trades for Oct 27.
   * Rebuild the tent curve P(mid change) against the mean sign for N = 50–500.
   * Flag pinned episodes: mean sign magnitude ≥ 0.6 with P(change) in the bottom decile.
2. **Paid extension (ES/NQ trades and book, about 10 days):**
   * Classify how each pinned episode ends: depth at the pinned level runs out, or the aggressors stop.
   * Measure the next move: continuation vs reversal, and its size relative to the √-impact scale.
   * Pre-register the owner's prediction: once the passive side is exhausted, price continues in the aggressor's direction; if the aggressors stop first, it reverts.

## Open questions
* Do the S-shaped curve and the exponents (ξ ≈ 0.75, ψ ≈ 0.5) hold on ES/NQ in 2024–26, with 0DTE hedging flows?
* Are pinned episodes more frequent near dealer-gamma strikes (S2 × F4)?
