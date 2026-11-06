# Kyle & Obizhaeva (2023). Large bets and stock market crashes. Review of Finance 27(6), 2163–2203. doi:10.1093/rof/rfad008
**Read:** the full published text (41 pages), including Appendices A–D and the references, on 2026-11-06. Source: the authors' PDF at pages.nes.ru/aobizhaeva/Kyle-Obizhaeva-crashes.pdf.
**Laws:** S4 (crash law), M1 (business time), F1 (impact; tension with the square-root law).

## Claim
Crashes can be explained quantitatively by the price impact of large forced or one-sided bets, provided impact is computed in **business time**. "Conventional wisdom" says selling 1% of market capitalization moves prices about 1%. That predicts tiny impacts for every one of the five crashes studied. Invariance plus linear impact predicts declines of the right size.

## The framework (from Kyle & Obizhaeva 2016, restated in the paper)
* **Trading activity:** W = P·V·σ, in dollars per day^(3/2). Two invariance assumptions:
  1. the dollar risk of a bet per unit of business time is the same across markets: Q·P·σ/√γ = C ≈ $2,000;
  2. equivalent bets cost the same.
* **Consequences:**
  * bet arrival rate γ = (W/C)^(2/3);
  * mean dollar bet P·Q = C·(W/C)^(1/3)/σ;
  * business-time unit H = (W/C)^(−2/3).
* **Bet sizes:** ln(Q/V) ~ N(−5.71 − (2/3)·ln(W/W*), 2.53), with W* = $40m × 0.02 (the benchmark stock: $40/share, 1m shares/day, σ = 2%/day). Bets per day: ln γ = ln 85 + (2/3)·ln(W/W*).
* **Impact (Eq. 15), log-linear form:**
  ΔlnP = −(k/1e4) · (P·V·g/40e6)^(1/3) · (σ/0.02)^(4/3) · Q/(0.01·V)
  * k = 5.00 (s.e. 0.38): an order of 1% of ADV in the benchmark stock moves price 5 bp.
  * k was calibrated on about 400,000 portfolio-transition orders, 2001–05 (median 0.57% of ADV, mean 4.20%).
  * g converts to 2005 dollars.
  * Equivalent to ΔP/P = a·σ·(W/C)^(1/3)·Q/V.
* **Scaling:** for a given fraction of ADV, impact grows with (dollar volume)^(1/3)·σ^(4/3). The whole US market (stocks + futures) runs about 225× faster in business time than the benchmark stock.
  * A 25% of ADV sale (≈ $70bn) → about 9.4% decline. Market elasticity about 0.01.
  * A $200bn fund or ETF liquidation over a few days → about 30%.
* **Linear, not square-root, for crashes.** The paper's invariant square-root version predicts much smaller declines (e.g. 1987: 1.3% against 32% actual). In KO2016, the square root fits individual stocks slightly better and linear fits the largest 1% of bets slightly better. **This conflicts with the econophysics square-root law (F1) for very large bets,** and is unresolved.

## Results: five crashes
| Event | Bet size | % of ADV | Predicted (window range) | Actual |
|---|---|---|---|---|
| 1929 margin selling, last week of Oct | $1.181bn | 265% | 46.4% (26.8–46.4%) | 25% |
| 1987 portfolio insurance, Oct 15–20 | $13.75bn gross | 67% | 16.8% (11.9–16.8%); net-sales variants 9.7–13.8% | 32% (Dow); 40% (futures) |
| Soros, Oct 22 1987 | 2,400 contracts, $310m | 2.3% | 6.3% (1.7–13.9% with additional sellers) | 22% |
| Société Générale, Jan 2008 | €50bn | 27.7% | 10.8% (10.6–12.9%) | 9.44% |
| Flash crash, May 2010 | 75,000 E-minis, $4.37bn, in 20 minutes | 1.49% | 0.61% (0.44–2.91%) | 5.12%, then a V-shaped rebound |

* **Model choices:**
  * Volume is the whole market (cash plus futures) for 1987, SocGen and 2010; futures only for Soros (before the cash open).
  * Volatility and volume are historical windows of 1–12 months before the event.
* **Biggest misses:**
  * the two flash events: executed 15× faster than normal; temporary impact is linear in speed in their smooth-trading model, so a V shape;
  * 1929: smaller fall than predicted. Selling was spread over 5 weeks, a ~$750m bankers' fund bought, the Fed eased, and markets were less integrated ("silos").
* **SocGen losses** predicted at €5.0–8.0bn vs €6.3bn reported.

## Frequency (Appendix D)
* **Typical bets in the whole market** ($270bn/day, σ = 1%):
  * 19,125 bets/day;
  * median bet about $4m, mean $14m;
  * a 4-standard-deviation bet is about $2.3bn (0.86% of ADV);
  * the standard deviation of the daily order imbalance is about 2.55% of ADV.
* **The crash bets were extreme:** 1929, 1987 and SocGen were 6.0–6.2 standard-deviation bets. Under a log-normal, those come once in 600–5,500 years. So the tails are fatter than log-normal, or the variance is underestimated. Soros and 2010 were about 4.5 standard deviations, which happen several times a year; executed slowly, such bets do not crash markets.

## Lessons the authors draw
* **Impact is big in liquid markets.** The "under 5–10% of ADV per day" rule is unsafe in index futures.
* **Speed** turns impact into a V shape.
* **Support must match the shock in size,** e.g. the 1929 bankers' fund.
* **Integrated markets spread impact.** Where the boundary of "the market" sits is an open question.
* **Early warning:**
  * Tuzun (2012): leveraged ETFs in financial stocks were near a tipping point in 2008–09. A 1% fall forced about $1bn of selling, which by invariance means about another 1%.
  * Leland's 1987 projection ($4bn of sales after a 4% fall) implied about another 4% fall: a tipping point, visible beforehand.

## Caveats (mine)
* **n = 5, all selected for known selling sizes.** The fit is loose: two predictions are off by 3–8× (the flash events); 1929 is off by 1.9×.
* **Calibrated on 2001–05 transitions,** then extrapolated 1929–2010 and across 6 orders of magnitude of trading activity. Its own argument puts the whole market at ln(W/W*) ≈ 8.2, far outside the calibration range of individual stocks (−12 to 2).
* **Linear vs square root** is a choice that decides the conclusion. The square-root law is strongly established for normal-sized metaorders (Sato & Kanazawa 2024), so what large bets do is a live empirical question.
* **Timing:** the formula ignores execution speed and how fragile the market was at the time (e.g. dealer gamma).
* **Unknowns in each crash:** information content and other traders' flows.

## What it means for us
* **This is the "how far can forced selling push the market" law.** It has inputs we can estimate:
  * the size of forced flows (leveraged-ETF rebalancing, volatility-target and CTA deleveraging, margin calls);
  * market-wide dollar volume (SPY + ES + all stocks, or futures + cash);
  * volatility.
* **Tipping-point test (the Tuzun/Leland logic):** does a 1% fall force enough selling to cause about a 1% fall? This is a feedback-gain number (M4) we can compute for leveraged ETFs today, and as a function of dealer gamma (S2).
* **Linear vs square root at crash scale** is a test our data could contribute to.

## How we would replicate or extend it on our data (test #4)
1. **Rebuild Eq. 15** with our inputs: whole-market dollar volume (US equities + ES/NQ futures) and the prior-month volatility.
2. **Out-of-sample events with estimable forced selling:**
   * Aug 5, 2024 (yen carry and volatility-target unwind);
   * Apr 3–8, 2025 (tariffs);
   * Jun 5, 2026;
   * Nov 4–5, 2026.
   * Flow estimates: leveraged-ETF rebalancing (we have the identity L(L−1)·A·r), volatility-target and CTA (published estimates only, marked as such), margin.
3. **Compare** linear invariance, square-root invariance, and conventional predictions against actual declines, out of sample. Pre-register which flows count.
4. **Live tipping-point gain:** dollars of forced selling per 1% fall, from leveraged-ETF assets today, then fed through Eq. 15 → the % fall it causes. A gain near 1 is the danger zone.

## Open questions
* Where is the market boundary today: SPY + ES + single stocks + 0DTE hedges?
* Do 0DTE hedging flows act like portfolio insurance (short gamma) or the opposite?
