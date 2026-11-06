# Donier & Bouchaud (2015). Why do markets crash? Bitcoin data offers unprecedented insights. PLoS ONE 10(10): e0139356 (arXiv:1503.06704v2)
**Read:** the full arXiv text (13 pages, Figures 1–6), 2026-11-06. Venue from the arXiv record (v2, Oct 2015); DOI not yet checked against Crossref.
**Laws:** S4 (crash law, physics version), F4 (liquidity geometry, latent liquidity), F1 (the square-root law as a liquidity measure).

## Claim
* **Crash size is set by the sell imbalance relative to the liquidity on the buy side, not by the selling alone.**
  * In the 10 April 2013 Bitcoin crash (−50% in hours), the selling in BTC was not unusual.
  * What was unusual was how few buyers remained below the price after a bubble.
* **A public measure tracks that liquidity:** σ_d/√V_d (the square-root-law illiquidity). It anticipates how big a crash a given sell-off would cause, but not when.

## Data
* MtGox, the dominant exchange then (over 80% of BTC/USD spot): every trade from Dec 2011 to Jan 2014, plus the full order book they collected.
* Bitcoin is special: 30–40% of a day's volume is already visible in the order book in the morning, against under 1% for stocks. So "latent" liquidity is mostly visible here.

## Method
* Aggressive imbalance in 4-hour windows, in BTC and in USD.
* "Support price": the price reached if 40,000 BTC were sold at once into the visible book.
* Three liquidity measures:
  * L_OB, the order book;
  * L_I, the measured impact of metaorders (from Donier & Bonart's million-metaorder study);
  * L_TH, the square-root law, I = Y·σ_d·√(Q/V_d), using daily σ (Garman–Klass) and daily volume.
* Compare them day by day, Nov 2012–Nov 2013.
* For the 14 largest falls (Jan–Apr 2013), compare the actual fall with the imbalance alone and with the imbalance adjusted by liquidity.

## Results
* **The selling was ordinary.** In BTC terms the 10 April sell-off (about 30,000 BTC in 4 hours) was no larger than several others; in USD it was an outlier. During the bubble ($13 → $260):
  * buy-side liquidity in USD roughly doubled;
  * in BTC it fell by 2–3×;
  * the support price was about 50% below the market just before the crash, the size of the actual fall.
* **14 largest falls:** the liquidity-adjusted imbalance L_OB⁻¹(O) "nearly perfectly matches" the fall sizes; the raw imbalance does not. The match is only shown visually; no statistic is reported.
* **The measures agree:**
  * L_OB⁻¹ vs L_TH⁻¹: R² ≈ 0.86 on the same day and 0.83 with a one-day lag (slopes 0.87–0.95).
  * Amihud σ/V does worse: R² 0.74 and 0.71.
  * L_I and L_TH were rescaled by one constant (6.104) to match the order-book level.

## Caveats
* **The authors':**
  * Bitcoin's visible book is unusual;
  * the amplitude can be anticipated, not the timing;
  * they call for a study across many stocks.
* **Mine:**
  * one exchange and one bubble; 14 events picked after the fact; the key result (Fig. 4) has no statistic;
  * the cross-measure R² is day-level co-movement over one year, partly shared volatility;
  * the square-root measure is only checked against the order book, not used to predict crash sizes. That step is untested even here.

## What it means for us
* **This is the physics side of the crash law,** and it disagrees with KO on mechanism:
  * **KO:** a giant bet × linear impact amplified by business time.
  * **Donier & Bouchaud:** a sell imbalance against *current* latent liquidity. Liquidity thins after a run-up, because demand does not keep up with the price, so an ordinary sell-off then causes a big fall.
* **For the owner's "liquidity landscape" and "distance to the edge" (agenda #5):** this is the clearest statement of the idea. The danger is a large gap between the price and where real demand sits, not the size of the selling. On equity markets the only public proxy offered is σ_d/√V_d.
* **For test #4:** add a liquidity-state version of the square-root prediction. Fit it two ways:
  1. normal-time σ and V (prior month, as KO do);
  2. the current state (the prior 5 days).
  
  If version 2 explains the falls and version 1 does not, liquidity collapse before the event is the amplifier.

## How we would replicate or extend it on our data
* **Daily L_TH⁻¹ = σ_d/√(dollar V_d)** for SPY, QQQ and SOXX from our daily data. Check whether its level before each selloff predicts the size of the fall per unit of forced selling.
* **Order-book depth** (Databento mbp-10 for ES/NQ) would let us test L_OB vs L_TH on equity futures, as here. Not bought.

## Open questions
* In equities most liquidity is latent, so is σ/√V still a good proxy? Donier and Bouchaud assume yes.
* After a run-up, is equity buy-side liquidity thinner in share terms, as in Bitcoin? That is the "price above support" condition, a possible signature for agenda #5.
