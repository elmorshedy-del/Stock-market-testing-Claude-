# Benzaquen, Donier & Bouchaud (2016). Unravelling the trading invariance hypothesis. Market Microstructure and Liquidity. doi:10.1142/s238262661650009x (arXiv:1602.03011v2)
**Read:** the full arXiv text (12 pages, Tables I–IV, all figures' captions), 2026-11-06. Verified: Crossref (2026-11-06-literature-laws/out/crossref*.json).
**Laws:** M1 (business time, the 3/2 law), S4 (crash law: the constant C enters the crash formula), F7 (spread ∝ volatility per trade).

## Claim
* **The 3/2 law is real and broad.** Traded risk W = P·V·σ scales as N^(3/2), where N is the number of trades in a time bin. It holds in 12 futures and 300 US stocks, at every bin size from 1 minute to a day.
* **The "invariant" is not invariant.** KO's I = W/N^(3/2) differs by more than 10× across futures, and is about 10× smaller for stocks than for futures.
* **What is closer to invariant is I/C,** where C = ⟨S·Q⟩ is the spread cost of a typical trade (spread in $/share × trade size).

## Data
* **Futures:** 12 front-month contracts (index, energy, agriculture, bond, FX, metal), Jan 2012–Dec 2014, best bid and offer tick data, 1-minute bins. Trades with the same timestamp are merged into one market order.
* **Stocks:** 300 US stocks chosen to span market cap and tick size, 2012 only, primary-exchange trades and quotes, 5-minute bins. Auctions and the first and last 30 minutes are removed.
* **Note:** N counts trades, not bets (metaorders). This follows Andersen, Bondarenko, Kyle & Obizhaeva (2015), who moved the test from bets to trades. The authors say that downscaling is "far from obvious".

## Method
* Averages are log-averages: ⟨X⟩ = exp(E log X). Power laws come from regressing log W on log N.
* Futures: average each 1-minute bin across days, so intraday seasonality (Asia, Europe, US) gives about two decades of range in N. Stocks: regress bin by bin, no averaging across days.
* Volatility: 10-second squared returns, then the Rogers–Satchell estimator, because the simple estimator biased the slope down at 30-minute to 2-hour bins.
* Tail exponents of the distribution of I: Hill estimator above the 1% tail.
* Decomposition: fit σ ∝ N^β and V ∝ N^γ separately, so that W ∝ N^(β+γ).

## Results
* **Slopes of log W on log N:**
  * futures 1.46–1.66 (SPMINI 1.50, TBOND 1.58, NSDQMINI 1.56);
  * stocks 1.54 ± 0.11 (cross-sectional spread), unchanged at daily bins.
* **The level I (dollars) is not universal:**
  * futures: TBOND 98, SPMINI 30.5, NSDQMINI 7.0, DJMINI 6.7, crude 12.0, gold 12.5;
  * stocks: 0.5–2.4 (sample of 12);
  * year-to-year change for one contract about 20%. Across contracts the change is more than 10×. Within a contract, I hardly depends on the bin size.
* **I/C is much tighter:** futures 0.30 ± 0.09, stocks 0.86 ± 0.54 (dimensionless, order 1).
* **Tails of I are power laws:** μ ≈ 2.5 (large-tick futures) to 1.5 (small-tick futures); stocks about 4.
* **Why 3/2 appears (the "naive argument"):**
  * Trades arrive at rate φ with average size Q₀, so V ∝ N.
  * Price is a random walk in trade time, σ ∝ √N, with a per-trade volatility proportional to the spread (Wyart et al. 2008).
  * So W ∝ Q₀·S·N^(3/2): the 3/2 law follows almost automatically, with the spread cost setting the level.
  * Stocks behave this way: β = 0.51 ± 0.06 and γ = 1.04 ± 0.07 at 5 minutes; 0.54 ± 0.10 and 1.02 ± 0.12 daily.
* **Large-tick futures are subtler.** Prices are sub-diffusive at small N (β < 1/2), and trade size grows with N (γ > 1), yet β + γ ≈ 3/2 still holds.
  * Two master curves fit all 12 contracts: Eq. 6 for σ(N) with a crossover at N₀ trades (about one tick of movement), and Eq. 7 for Q(N) with ν ≈ 0.54.
  * The authors cannot say whether β + γ ≈ 3/2 is a coincidence or a deeper principle.
* **Generalized law (Eq. 10):** P·Q/C = f_asset(Q·σ²/V, P·σ·√τ/s). For large τ or small tick s this reduces to KO's form.

## Caveats
* **The authors':**
  * trades are not bets;
  * stocks are one year only;
  * the NYSE/NASDAQ split in I for large-tick stocks is only partly understood (NASDAQ has smaller trades and hidden trades inside the spread);
  * whether I/C's weak tick dependence is real is left open.
* **Mine:**
  * This paper tests the 3/2 law, not impact. It says nothing about how far a bet moves price.
  * It also shows that the 3/2 law on trades is weak evidence for KO's bet-level invariance. Diffusion plus additive volume plus spread ∝ volatility per trade give 3/2 without any invariance of bets.

## What it means for us
* **For the crash law (S4, test #4). This is the important point.** In KO's formula the bet cost C enters as C^(−1/3):
  ΔP/P = a·σ·(W/C)^(1/3)·Q/V.
  * KO use one C (≈ $2,000) for the whole market, futures and stocks pooled.
  * This paper finds the trade-level analogue of C differs by about 10× between futures and stocks. If the bet-level C differs by 10× too, the predicted crash size changes by 10^(1/3) ≈ 2.2×.
  * **So any crash-law prediction carries at least a factor of about 2 of uncertainty from C alone,** before the linear vs square-root question. Test #4 must report this band, not a point.
  * **Direction:** the whole market is dominated by futures volume, and futures show the larger invariant. So pooling them at the stock-calibrated C probably overstates the predicted fall.
* **For M1 (business time):**
  * The 3/2 law is safe to use as a scaling rule.
  * The absolute level of the invariant is not, unless measured per market.
  * The cleanest version of business time is "per-trade volatility ∝ spread" (F7), which this paper supports.
* **For the owner's "volatility signature sets the speed" idea:** the clock runs at a rate set by trade count, and the scale of each tick of that clock is set by the spread. Both can be measured live.

## How we would replicate or extend it on our data
1. **3/2 law on our 1-minute bars** (SPY and QQQ 2020–26; ES/NQ if bought). Regress log(P·V·σ) on log N per 5-minute bin with the Rogers–Satchell σ. Expect a slope of 1.5 ± 0.1. A failure on our data would be news.
2. **I and I/C per instrument:** SPY vs QQQ vs ES vs NQ. This needs the spread and trade counts (Databento trades or mbp-1). It gives us the per-market C that the crash law needs, instead of KO's single $2,000.
3. **In test #4,** carry C as an uncertainty: report predictions at the KO C and at C × 10^(±1) (a factor of 2.2 either way on the predicted fall).

## Open questions
* Does the bet-level invariant (metaorders, not trades) also vary across markets? Bucci, Lillo, Bouchaud & Benzaquen (2020), "Are trading invariants really invariant? Trading costs matter", tests that on metaorder data. **Read it before test #4.**
* How do trade-level and bet-level business time relate in a crash, when bets are split into many more trades than usual?
