# Dew-Becker & Giglio (2026). The decline of the S&P 500 variance risk premium. Working paper, version of 2 June 2026 (earlier version: Chicago Fed WP 2025-17)
**Read:** the full main text (sections 1–5) and the model-extension appendix B in outline; appendix figures A.1–A.3 and the external appendices not read. 2026-11-16. A working paper, not peer reviewed.
**Question it serves:** PRICE (is it priced?). Mechanism tag: POS.

## Claim
* **S&P 500 options stopped being overpriced around 2012.** From 1987 to about 2012, buying index options lost money after adjusting for the market. Since then the loss is statistically and economically zero, and in some cases a small gain.
* **The change came when dealers stopped being net short options.** Net dealer gamma was clearly negative until about the financial crisis and has been near zero or positive since.

## Data
* CME futures options 1987–1995 spliced with CBOE SPX options (OptionMetrics) 1996–2025. Monthly: buy on the third Friday, hold to the next third Friday. 457 months (301 before August 2012, 156 after).
* Five strategies: a 5% out-of-the-money put, an at-the-money straddle, each with and without daily delta hedging, and a variance swap built from the VIX: (realized variance − VIX²) ÷ VIX².
* Dealer gamma from Cboe open-close data, 1996–2025, options with 10–180 days. Dealers = traders that are neither customers nor firms.
* Synthetic straddles (delta-hedge replication with a volatility forecast) back to 1926.

## Method
* Mean returns, CAPM alphas and information ratios before and after August 2012. That date is the last month in which the centred 12-month average of dealer gamma was negative.
* Three break tests: a fixed-date Wald test; a Hodges–Lehmann median-based test with an unknown break date; the Andrews–Ploberger test. Simulations show the median-based test has the right size and much more power here.
* Regression of rolling straddle information ratios on lagged dealer net gamma and on the volatility of the index–futures basis (both smoothed), monthly 1996–2025, n = 356.
* A model: two kinds of retail investors with different beliefs, plus small dealers. When retail can buy options but not sell them, options are overpriced. When retail can also sell, the premium vanishes.

## Results
* **Break tests on market-adjusted returns** (change in the monthly mean; p-values for fixed date / median test / Andrews–Ploberger):

  | Strategy | Change | p-values | Break date (median test) |
  |---|---|---|---|
  | Straddle | +0.18 to +0.20 | 0.026 / 0.044 / 0.041 | Jan 2010 |
  | Delta-hedged straddle | +0.08 to +0.10 | <0.001 / 0.001 / 0.007 | Feb 2007 |
  | Delta-hedged 95% put | +0.20 to +0.25 | 0.059 / <0.001 / 0.071 | Mar 2007 |
  | Variance swap (unscaled) | +0.008 to +0.010 | 0.074 / 0.007 / 0.347 | Sep 2010 |
  | 95% put, unhedged | n/a | 0.337 / 0.076 / 0.352 | Apr 2009 |

* **Straddle Sharpe ratio:** −0.74 in 1987–2001; −0.09 after 2001; **+0.12 after 2012.**
* **VIX against realized volatility:** in the first 10-year window the VIX overstated realized volatility by about 25% (18.7 against 15). In the latest window by about 10% (16.4 against 15). On rolling 10-year averages the VIX has been close to an unbiased forecast "for 17 years now".
* **Dealer gamma and option returns:** the delta-hedged straddle information ratio loads on lagged dealer net gamma with coefficient 0.61 (s.e. 0.28, 5% level) and on basis volatility with −1.03 (s.e. 0.28). The unhedged straddle and the hedge leg alone do not load on gamma (0.44, s.e. 0.87; −0.31, s.e. 0.83).
* **The hedge leg never had an alpha,** from 1926 to 2025. So the old premium was in the traded option itself, not in the risk it carries.
* **Frictions fell:** bid-ask spreads and basis risk dropped by about an order of magnitude; jump risk and skewness did not fall (skewness became more negative). So the premium did not vanish because risk vanished.
* Value, momentum and currency carry flattened at about the same time.

## Caveats
* **The authors':** both the early and the late sample are short; "nothing here is about forecasting the future"; all results are unconditional averages; the unhedged put result is weak.
* **Mine:**
  * The gamma regression is slow. Both sides are smoothed (rolling ratios, moving averages), so it is close to a single trend break seen once. It does **not** show that this month's or this day's dealer gamma predicts option returns.
  * Dealer gamma uses options of 10–180 days. Weeklies and 0DTE, which now carry much of the gamma, are left out.
  * The break date was chosen from the gamma series; the tests that search for the date put it between 2006 and 2010.
  * Monthly options held to expiry. Nothing on shorter holding periods or on single stocks.

## What it means for us
* **The baseline for an index option buyer has changed.** The old headwind (implied about 25% above realized) is now about 10% or less on average. Our founding-report table (naked calls bought early lose, spreads gain) was built on rough estimates; the fair starting assumption for SPY today is that an option costs about what the move turns out to be worth, on average.
* **Sign of the link, slow version:** when dealers were short gamma, options were dear. As dealers moved to flat or long, options became fairly priced. So "dealers short gamma" is not a reason to buy options. It went with options being a bad buy.
* **This sharpens step 1.** Two effects pull in opposite directions when dealer gamma is low or negative:
  1. realized moves get bigger (Ni et al.; our own results);
  2. options get more expensive, because dealers charge for the risk (Gârleanu et al.; this paper).
  
  The question "is the state priced?" is which one wins, at the daily-to-monthly horizon, in today's regime. Nothing in this paper answers that; it only fixes the unconditional level near zero.
* **A regime warning for all our gamma history:** GEX series before about 2012 come from a market where dealers were structurally short. Pooling 2011–2026 mixes two regimes.

## How we would replicate or extend it on our data
* Check the baseline on our own data first: realized ÷ implied for SPY, monthly, 2012–2026, should average close to 0.9–1.0. If it does not, our implied-move measure is off, and that has to be fixed before any conditional test.

## Open questions
* Does the high-frequency version hold: within the post-2012 regime, do months that start with low dealer gamma have better or worse returns to buying options?
* Is the single-stock market (TSLA) in the "retail buys, dealers short" regime that the index left in 2012?
