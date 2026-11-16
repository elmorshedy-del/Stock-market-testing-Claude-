# Barbon & Buraschi (2021). Gamma Fragility. Working paper, 18 March 2021 (University of St. Gallen School of Finance Research Paper 2020/05; SSRN 3725454)
**Read:** the full text (sections I–VI) and Table I; Tables II–IX were read through the text's description, not cell by cell. 2026-11-16. A working paper, not peer reviewed.
**Question it serves:** SIZE (how big), RISK (what breaks it). Mechanism tags: POS, FLOW.

## Claim
* **Negative dealer gamma goes with bigger daily moves and intraday momentum; positive dealer gamma goes with smaller moves and intraday reversal.**
* **The effect is larger where the stock is less liquid.** So it is a hedging-flow effect that needs limited liquidity, separate from informed trading and from margin spirals.
* Flash crashes are slightly more likely and clearly deeper when dealer gamma is negative.

## Data
* Opening and closing option volume by trader type from three Nasdaq exchanges (ISE, GEMX, PHLX), Jan 2010–May 2020. These carry 10–20% of U.S. equity-option dollar volume.
* OptionMetrics for prices, open interest and greeks; CRSP and TAQ for daily and intraday returns; RavenPack for news.
* 2,700 stocks (3.67 million stock-days) plus four indices (S&P 500, Dow, Nasdaq 100, Russell 2000).

## Method
* **Gamma imbalance** = dealers' gamma × price ÷ 21-day average daily volume: the hedging volume a 1% move forces, as a percentage of normal volume.
* **For the indices they have no positions.** They assume customers are short calls and long puts, so the proxy is call gamma minus put gamma, per unit of volume. (This is the same sign convention as the public "GEX".)
* Panel regressions with asset and month fixed effects, standard errors clustered by asset and month:
  1. next-day absolute return on lagged gamma imbalance, controlling for implied volatility;
  2. the same with an illiquidity interaction (Amihud ratio, top half vs bottom half);
  3. intraday autocorrelation of 5- to 60-minute returns on lagged gamma imbalance;
  4. high–low spread, a flash-crash dummy and flash-crash depth on lagged gamma imbalance. Flash crashes are found with the Christensen–Oomen–Renò drift-burst test (at least −1% in 30 minutes): 10,572 events in 1,849 stocks, 1997–2015.

## Results
* **Gamma imbalance across stocks:** mean 13.5, standard deviation 124.5, median 0.05, 10th percentile −14.6, 90th percentile 37.5 (percent of daily volume per 1% move). On almost every day some stocks are strongly negative and others strongly positive.
* **Stocks, next-day absolute return:** coefficient negative, t between −5.1 and −12.1 depending on fixed effects. One standard deviation ↔ 5 to 25 basis points, against a mean absolute return of 180. Negative in 70% of single-stock time-series regressions.
* **Indices (assumed signs):** coefficient −5.5 to −14.8, t from −3.3 to −4.4. One standard deviation ↔ more than 20 basis points of absolute index return, about 20% of a standard deviation.
* **Illiquidity:** the interaction is −8.88, t = −7.6. The rise in absolute return on negative-gamma days is about 9 basis points larger for the illiquid half.
* **Intraday autocorrelation:** negative coefficient at every horizon, strongest at 5 and 60 minutes. One standard deviation ↔ 1.5–2 percentage points of autocorrelation.
* **Flash crashes:** one standard deviation lower gamma ↔ about 5% higher crash probability relative to its base rate (small), and a 20–200 basis point deeper fall given a crash (large).
* **6 May 2010:** market-wide gamma imbalance went from about +$383m a week earlier to about −$431m on the day (−1.7 standard deviations).
* Leveraged-ETF size does not explain the pattern: it rose steadily while momentum and reversal both kept occurring.

## Caveats
* **The authors':** correlation is not causation; gamma is a friction that "may exacerbate" moves started by news or liquidity shocks; the three exchanges cover only 10–20% of volume.
* **Mine:**
  * The index result rests on an assumed sign (customers sell calls and buy puts). That assumption comes from 1996–2001 data. Later papers with real positions show it is often wrong for short-dated SPX options.
  * Implied volatility is used only as a control. The paper never asks whether option prices anticipate the effect.
  * Effect sizes are modest: 5–25 basis points per standard deviation in stocks.
  * The flash-crash sample (1997–2015) is longer than the positions data (2010–2020); the text does not say how the two were matched.

## What it means for us
* **Second, independent confirmation of our robust SIZE result, on 2010–2020 data** with partly real positions, and at the index level with the same proxy we use.
* **Liquidity is the multiplier.** The gamma effect is a flow divided by the market's capacity to absorb it. This is the cleanest statement in the literature of why our second state variable (liquidity) belongs next to positioning: the same gamma imbalance does more damage in a thin market.
* **The right unit for gamma is "percent of normal volume per 1% move".** That is comparable across stocks and over time, and it is the unit we should use for SPY against TSLA.
* **For the "is it priced?" derivation:** negative gamma raises the *tails* (crash depth) more than the average. Out-of-the-money options and at-the-money options may therefore be affected differently.

## How we would replicate or extend it on our data
* Recompute our SPY and TSLA gamma in their unit (gamma × price ÷ average daily volume) and check whether the size relation is tighter than with raw dollar gamma.

## Open questions
* Does the effect survive once lagged *realized* volatility, not only implied, is controlled? Their Table IV says yes for "alternative variables"; the specifics are not in the text.
