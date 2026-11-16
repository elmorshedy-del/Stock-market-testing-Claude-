# Gârleanu, Pedersen & Poteshman (2009). Demand-Based Option Pricing. Review of Financial Studies 22(10), 4259–4299. doi:10.1093/rfs/hhp005
**Read:** the full published text (sections 1–4; appendix proofs skimmed, not checked line by line), 2026-11-16.
**Question it serves:** PRICE (is the state priced?). Mechanism tag: POS.

## Claim
* **Option prices depend on who holds them.** Dealers cannot hedge options perfectly (they trade at discrete times, the price jumps, volatility moves). They are risk averse. So the price of an option rises with the amount end-users make dealers sell.
* **The size of the effect is set by the risk dealers cannot hedge.** Demand for option j moves the price of option i by an amount proportional to the covariance of their unhedgeable parts.

## Data
* CBOE open interest by trader type (public customers, firm proprietary traders; market-makers are the remainder), daily, 1996–2001, for SPX options and options on 303 stocks.
* OptionMetrics implied volatilities; CRSP returns.
* "Expensiveness" = implied volatility minus a reference volatility (Bates 2006 filtered volatility for SPX; a GARCH(1,1) forecast for stocks). ATM, 15–45 days to expiry.

## Method
* **Model:** competitive dealers with constant absolute risk aversion γ take the other side of an exogenous end-user demand d. Prices are "inverted from quantities".
* **Theorem 2:** ∂p_i/∂d_j = γ(R_f − 1)·Cov(p̄_i, p̄_j), where p̄ is the price change left after the best hedge with the underlying.
* **Three sources of unhedgeable risk, each with its own weighting of demand:**
  1. Discrete hedging: weight = gamma. Effect on implied volatility ∝ Γ_i·Γ_j/vega_i. It shifts the level of the smile, not the slope, and shrinks as hedging gets more frequent.
  2. Jumps: weight = "kappa", the loss on a hedged option in a large jump. Shifts level and slope.
  3. Stochastic volatility: weight = maturity-adjusted vega. Shifts the level.
* **Tests:** monthly time-series regression of SPX expensiveness on demand (four weightings); skew on demand skew; Fama–MacBeth cross-section for stocks.

## Results
* **Who holds what (1996–2001):**
  * SPX: end-users are net long in almost every strike and maturity bucket (about 103,000 contracts net; most in out-of-the-money puts; 39% with under 30 days). So dealers are net short index options.
  * Stocks: end-users are net short in almost every bucket. Dealers are net long stock options.
* **SPX level, Oct 1997–Dec 2001 (n = 50 months):**

  | Demand weighting | t-statistic | Adj. R² |
  |---|---|---|
  | Raw contracts | 1.55 | 7.0% |
  | Gamma (discrete hedging) | 3.85 | 18.5% |
  | Kappa (jumps) | 3.68 | 25.9% |
  | Vega (stochastic volatility) | 2.74 | 15.7% |

  * Jan–Oct 1996 (n = 10): positive, not significant.
  * A one-standard-deviation move in jump-weighted demand goes with half a standard deviation of expensiveness. Lowest to highest demand: about 5.6 volatility points.
  * Demand explains about 1.7 volatility points on average, "more than a third" of the average expensiveness.
* **Dealer losses matter:** after 20 days of dealer losses the price response to demand is about twice as large (coefficient 2.6e-5, t = 3.7, n = 330 days, against 1.1e-5, t = 6.1, n = 646).
* **Skew:** demand skew explains skew (t = 2.99, R² 26.7%; one s.d. → 0.53 s.d.).
* **Stocks:** more end-user demand → more expensive options (t = 7.66); weaker when option volume is high and after cross-listing in 1999.
* **Dealer P&L:** daily delta-hedged P&L swings between about +$100m and −$100m; about $800m over six years; Sharpe ratio 0.41 on daily P&L and 0.85 on monthly.

## Caveats
* **The authors':** over-the-counter demand is not in the data, so the estimate is a lower bound; other risk premia also make index options dear.
* **Mine:**
  * 50 monthly observations, one six-year period that includes 1998 and the dot-com peak.
  * The regressions are same-month levels on levels. They show co-movement, not that positions lead prices.
  * The reference volatility is a model output; "expensive" is relative to that model.
  * The 1996–2001 sign (dealers short index options) is not today's. Dew-Becker & Giglio show dealer gamma has been near zero or positive since about 2012.

## What it means for us
* **The price of an option already contains the dealers' position.** If dealers are short a lot of gamma, they charge for it. So "low dealer gamma → bigger moves" does not by itself make options cheap. The two forces work on both sides of the ratio we want to test: bigger realized moves and a higher price.
* **The sign matters, and it flips between products.** In the index dealers were sellers of options (dear). In single stocks dealers were buyers (cheap). TSLA today is a call-buying market, so its sign has to be measured, not assumed.
* **The mechanism is risk the dealer cannot hedge, weighted by gamma, jump loss or vega.** The effect is larger when dealers have just lost money. This gives the derivation its second state variable: dealer risk-bearing capacity.
* **Theorem 3:** expected future demand is priced today. A known expiry is known in advance, so its effect on demand should be in the price before it happens.

## How we would replicate or extend it on our data
* We do not have positions by trader type. We have open interest and assumed signs. So we cannot run their regression; we can only test consequences (realized ÷ implied by our gamma proxies).
* The Cboe open-close files would give true signs. Cost not yet checked.

## Open questions
* How much of the daily change in implied volatility is repricing of dealer inventory risk, and how much is the forecast of realized volatility?
* Does the demand effect still exist at all when dealer gamma is near zero or positive?
