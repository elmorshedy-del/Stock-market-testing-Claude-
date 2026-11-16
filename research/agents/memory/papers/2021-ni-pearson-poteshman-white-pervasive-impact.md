# Ni, Pearson, Poteshman & White (2021). Does Option Trading Have a Pervasive Impact on Underlying Stock Prices? Review of Financial Studies 34(4), 1952–1986. doi:10.1093/rfs/hhaa082
**Read:** the full text of the **2006 working-paper draft** (Pearson, Poteshman & White, 31 July 2006, marked preliminary; 47 pages with tables), 2026-11-16. The published 2021 version is behind a paywall and was **not** read; its numbers may differ. Everything below is from the draft.
**Question it serves:** SIZE (how big). Mechanism tag: POS.

## Claim
* **A stock moves less on days after its dealers are long gamma and more after they are short gamma.** The cause is hedge rebalancing, not informed volatility trading.
* The effect is present every week of the month, not only at expiry.

## Data
* CBOE open interest by trader type for every equity option series, daily, 1990–2001. Market-maker positions are the negative of public plus firm-proprietary positions.
* 2,308 underlying stocks with at least 200 days of data. CRSP returns, volume and shares outstanding.

## Method
* **Net gamma of likely hedgers,** scaled by price ÷ shares outstanding, (S/M)·Γ, so that it is dimensionless and comparable across stocks. Black–Scholes gammas with 60-day historical volatility; OptionMetrics gammas as a check.
* **Theory they test** (Frey–Stremme, Sircar–Papanicolaou, Platen–Schweizer, Frey): volatility = v·σ with v ≈ 1 ÷ (1 + λ·(S/M)·Γ). Positive hedger gamma lowers volatility; negative raises it.
* **Identification.** Net gamma today is split into three parts:
  1. the change in the gamma of positions held τ days ago that comes only from the stock price moving since then (cannot be new volatility bets);
  2. the gamma of those old positions at the old price;
  3. the gamma added by new positions.
  
  Part 1 is the clean test. Parts 2 and 3 could also reflect informed volatility trading.
* **Regression,** one per stock: next-day absolute return on the three parts plus the absolute returns of today and the last 10 days. Coefficients averaged across stocks; standard errors clustered by date. τ = 5 days (also 3 and 10).

## Results
* **Sorting by decile** of market-maker net gamma: mean next-day absolute return falls monotonically from about 3.4% (lowest gamma) to about 2.6% (highest), a gap of about 100 basis points.
* **Clean component (part 1), τ = 5:** average coefficient −0.000543, t = −7.6. With market makers plus firm proprietary traders: −0.000476, t = −6.9.
* **Size:** one standard deviation of net gamma (6.77) ↔ 37 basis points of daily absolute return, against a mean of 310. About 12% of daily absolute return.
* **Robust to:** dropping expiration week (−0.000535, t = −5.5); 1990–1995 and 1996–2001 separately (smaller in the first half); the 250 largest stocks (−0.000492, t = −3.7) and the rest; τ = 10 (−0.000484, t = −8.1); OptionMetrics gammas (−0.000507, t = −12.9).
* **Hedging volume:** one standard deviation of estimated hedge-rebalancing volume ↔ about 14% of average daily stock volume (coefficient 4.13, t = 26.7).
* **Mean market-maker gamma is positive** in single stocks (average 3.1 in scaled units), consistent with end-users being net sellers of stock options in 1990–2001.

## Caveats
* **The authors':** part 1 could still carry private volatility information if it is realised partly before and partly after day t; they argue this biases toward zero.
* **Mine:**
  * I read the 2006 draft, not the published paper.
  * 1990–2001, daily data, single stocks. No index, no 0DTE, no retail call buying on today's scale.
  * The dependent variable is the next-day absolute return. Nothing is said about option prices or implied volatility.
  * They show the effect is real. They do not ask whether the option market prices it.

## What it means for us
* **This is the academic version of our robust result** (dealer-sign and gamma-phase-diagram studies): the sign and size of dealer gamma forecast the size of the next move. Their estimate of the share explained is modest: about one-eighth of daily absolute return per standard deviation.
* **It uses true positions.** We use open interest with assumed signs. The decomposition (old positions revalued at the new price) is a clean idea we can copy with open interest alone, because it needs no new-position data.
* **For the "is it priced?" derivation:** the size of the effect is what the option market has to price. If one standard deviation of gamma moves realized volatility by about 12%, implied volatility has to move by about the same proportion for the state to be fully priced.

## How we would replicate or extend it on our data
* Compute for SPY and TSLA the change in gamma of yesterday's open interest caused only by today's price move, and use that as the regressor for the next day's range. This removes the "new positions carry information" objection from our own results.

## Open questions
* Is the 2021 published estimate the same size? (Not read.)
* Does the relation hold in the index, where dealer gamma was negative in this period and positive later?
