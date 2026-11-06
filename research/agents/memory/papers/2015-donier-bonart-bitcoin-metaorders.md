# Donier & Bonart (2015). A million metaorder analysis of market impact on the Bitcoin. Market Microstructure and Liquidity 1(2), 1550008 (arXiv:1412.4503v3)
**Read:** the full arXiv text (18 pages, Figures 1–12), 2026-11-06. Venue as cited in Bucci et al. 2019; DOI not checked against Crossref.
**Laws:** F1 (the square-root law, its constant and its limits), F6 (impact decay), S4 (liquidity breakdown under sustained pressure), F4.

## Claim
* **The square-root law holds on Bitcoin over 4 decades of order size, along the whole execution path,** even though fees (0.6%) shut out market makers and arbitrage. So the law does not come from equilibrium or arbitrage. It is how supply and demand absorb a local excess.
* **The market responds to total order flow, not to individual metaorders.** Metaorder impacts do not add linearly.
* **Isolated (uninformed) metaorders leave about zero permanent impact.**

## Data
* MtGox BTC/USD, Aug 2011–Nov 2013: all ~13–14 million trades with anonymized trader IDs. So every metaorder is identifiable, with no broker conditioning.
* Over 1 million metaorders: 61% single trades, 3.5% with 10 or more trades. They start after about an hour of inactivity and end at the next pause or a reversal of direction.
* About 5 metaorders are active at a time. Signs are autocorrelated (power-law exponent about 0.4).

## Method
* Peak impact I(Q) at the end of the metaorder; the impact path I_path(r, Q, μ) along it; the average execution price; the long-run price.
* A daily constant Ỹ compared with σ_D/√V_D.
* Impact against execution rate.
* "Isolated" metaorders: those that make up over 75% of the market's net imbalance over 10× their duration (about 3% of all).

## Results
* **Square-root law:** I ≈ Ỹ·Q^δ with δ ≈ 0.5 from the smallest sizes up, over 4 decades.
  * Y-ratio (I = Y·σ·√(Q/V_D)) ≈ 0.9. The daily Y is about N(0.9, 0.35), i.e. mostly between 0 and 2.
  * The path follows the same law: I_path(r, Q) = I(rQ).
* **Liquidity varies with σ_D/√V_D,** "particularly during extreme market events (e.g. April 10, 2013 crash)".
* **Liquidity breakdown** (Fig. 6; a qualitative statement, no fit):
  * at high trading rates (10 BTC/s) and large sizes, "a liquidity breakdown leading to an asymptotically linear impact when important pressures are maintained for too long on the same side of the order book";
  * near-100% participation makes impact "unusually high": "the market breaks down in this regime". On financial markets participation "rarely exceed[s] 20–30% for this very reason".
* **Total order flow:** during a metaorder, impact is "a very nice square root of global market imbalance". Execution cost even rose for slower execution (∝ Q^0.5/μ^0.4) because slow orders overlap correlated flow. Isolated orders show the expected opposite (slower is cheaper), but the data are too noisy to fit.
* **Decay:** isolated metaorders revert far below 2/3 of peak, probably to zero. The apparent permanent impact is correlation with later flow, not information about value.

## Caveats
* **The authors':** an unusual market (high fees, wide spread, little HFT, one asset); the data come from an anonymous source, though checked against public prints.
* **Mine:**
  * the liquidity-breakdown statement rests on one figure with no fitted threshold;
  * the metaorder definition (one hour of inactivity) is a free choice, though the authors say it barely matters.

## What it means for us
* **It reconciles the two crash-law camps.**
  * Under normal pressure: square root, Y ≈ 1, independent of execution time.
  * Under sustained one-sided pressure near full participation: liquidity breaks and impact steepens toward linear.
  * So KO's "linear at crash size" and the physics "square root" can both hold, in different regimes. **The crash question becomes: at what pressure does liquidity break, and can we see it coming?**
* **Aggregate flow is what matters,** so the crash law should be applied to net market-wide selling, not to one seller's bet (KO's framing). That supports summing forced flows (leveraged ETFs + volatility targeting + margin) into one Q.
* **For F1:** Y ≈ 0.9 on a market with no market makers, consistent with KO2016's square-root calibration (12.08 bp × 1.5 at 1% of volume → Y ≈ 0.9).
* **For F6:** uninformed impact decays to about zero. A forced-selling dip should fully revert, unless the selling coincides with information.

## How we would replicate or extend it on our data
* **Breakdown test (paid):** in ES/NQ trades with aggressor side (Databento), measure the price move per unit of signed volume, minute by minute, on selloff days vs normal days. If the response per unit of selling jumps on selloff days, liquidity broke. This is the decisive measurement for test #4.
* **Free:** daily σ_D/√V_D for SPY/QQQ/SOXX as the liquidity state before each selloff (Donier & Bouchaud's proxy).

## Open questions
* Is there a measurable participation threshold where equity-futures liquidity breaks (e.g. 20–30%)?
* Does the breakdown reverse fully once the pressure stops (a V shape), as KO say the flash crashes did?
