# Three positioning claims, tested: TSLA's strike crossing, correlation × gamma, put monetization

* **Owner, 2026-10-26:**
  * "was this particular level it opened at some kind of resistance by some positioning and once it opened above it it caused a forced buy";
  * "we want to formalize this correlation thing mentioned in the letter by testing and also that large put sell since these can be confusing or just noise."
* **The letter** (a SpotGamma-style newsletter the owner pasted):
  * "if COR1M starts to creep higher with SPX < 7,700, then we want to start positioning for a broader selloff";
  * "One trader bought nearly 110K QQQ October 30 $700 puts for an estimated $111 million… closed for a 193% gain."
* **Prior evidence that matters:** [dealer-sign](../2026-10-16-dealer-sign/) Part B. **Dealers are net long calls in TSLA:** call gamma damps the next-day range (−0.070, p < 0.001). Put gamma is inconclusive in TSLA.

## P1. Did TSLA's gap cross a positioning level, and does crossing one force buying?
* **Today, descriptive:**
  * the call open interest at the strikes TSLA gapped over (375, 380), from OI dated Oct 26 (positions at Friday's close);
  * the dealer delta change from $372.22 to $391.62 under the classic convention (dealers long calls, short puts) and under the all-short convention, in shares, compared with Monday's TSLA volume.
* **Historical test (TSLA, 2020 to 2026-10-14):**
  * For each day, find the largest call-OI strike within 0–10% above the prior close, expiring within 45 days, from OI dated that day (known before the open).
  * Events: up-gaps ≥ 2% whose **open is above that strike** (crossed overnight), vs up-gaps ≥ 2% that did not cross it.
  * Outcomes: open-to-close return (does the day continue?); the next 5 sessions' return from the close; the same-day gap-fill rate.
* **Competing predictions:**
  * owner: crossing forces buying, so continuation is **higher**;
  * dealer-sign (dealers long calls): dealers sell above the strike, so continuation is **lower**.
* Two-sided; bootstrap by event.

## P2. Correlation × gamma: does rising correlation while dealers are short gamma lead to a broader selloff?
* **Correlation:** realized 10-day average pairwise correlation of daily returns.
  * 41 large caps from 1990; 81 from 2020.
  * The letter's COR1M (implied) is not available here, which is a stated limitation.
* **"Rising":** the 5-session change in correlation is in the top third of its trailing-252 distribution.
* **Gamma state:**
  * **primary:** SqueezeMetrics GEX < 0 (2011–2026);
  * secondary: SPY below its flip, from the engine (2020–2026).
* **Outcomes:** the S&P's next-10-session return, and P(a close ≥ 5% below the 252-day high within the next 20 sessions, given the S&P was within 5% at the signal).
* **Primary contrast:** (GEX < 0 and rising) minus (GEX < 0 and not rising): next-10-day return **< 0** and drawdown probability **> 0**. 20-day block bootstrap, one-sided.
* All four cells are reported, plus the same contrast when GEX > 0.

## P3. Large put closes: a bottom signal or noise?
* **Verify the letter's trade:** OI of QQQ 2026-10-30 $700 puts, Oct 1–23 (ThetaData; licensed, only aggregates written).
* **Systematic, SPY and QQQ 2020 to 2026-10-14:**
  * **Large put close:** a single put contract (expiring in 3–60 days, strike within 15% of spot) whose OI falls by ≥ 40,000 contracts from the prior day.
  * Same-day expiries are excluded, so expiry roll-off is not counted.
  * **In a selloff:** the ETF is down ≥ 3% over the prior 10 sessions.
  * **Statistic:** mean next 5/10/20-session ETF return after selloff days **with** a large put close minus selloff days **without** one. Events are de-duplicated: one per 5 sessions per ETF.
  * Bootstrap by event; two-sided (the letter implies > 0).
* **Reading:** a positive difference means monetization marks short-term lows; otherwise it is noise.

## Verification of the letter's QQQ trade (`spyg/QQQ_oi_exp20261030.csv.gz`, licensed; aggregates only)
QQQ 2026-10-30 **$700 put** OI by file date (each file is positions at the prior close):

| File date | OI (contracts) |
|---|---|
| Oct 6 | 38.6k |
| **Oct 7** | **88.1k (+49.5k)** |
| Oct 13 | 91.3k |
| Oct 16 | 95.6k |
| **Oct 19** | **103.9k (peak)** |
| Oct 20 | 89.8k |
| Oct 22 | 82.5k |
| Oct 23 | 88.3k |
| **Oct 26** | **72.0k** |

* **The build is confirmed:** about +65k contracts from Oct 6 to Oct 16.
* **The close is only partly visible:** −32k from the peak by Friday's close.
* OI falls only when both sides close. A holder selling to a new buyer leaves OI unchanged, so the letter's "closed" cannot be fully verified from OI, nor refuted.

## Amendment 1 (owner: "It's also about positioning as orders and order book. It can force shorts covering… levels that have orders sitting that we didn't even explore"). Written before computing P1–P4.
* **No order-book depth is available:** Databento market-by-price would need the owner's approval to spend. We test the **footprints** that resting orders leave in prices, following the literature:
  * Osler (2003, *JF*; 2005, *JIMF*): take-profit and limit orders cluster **at** round numbers, so trends tend to stall there. Stop-loss orders cluster **just beyond** round numbers and beyond prior extremes, so moves **accelerate** once these are crossed: price cascades and forced short covering.
  * Kavajecz & Odders-White (2004, *JF*): support and resistance levels coincide with peaks in limit-order depth.

**P4a. Stop-cascade footprint at prior highs** (daily data, 81 large caps; 41 from 1990, 81 from 2020):
* **Event:** the day's high crosses the prior **20-day high** for the first time in at least 5 sessions.
* **Statistic:** next-day and next-5-day return (z, by trailing 20-day volatility), **crossed and closed above** vs a **near miss** (high within 0.5% below the prior 20-day high without crossing).
* The day's own z-return is a control, via regression of the outcome on the crossing dummy plus that z-return.
* **Predictions:** crossings continue (coefficient > 0, stops and short covering); near misses reverse (limit orders at the level).
* Split by market volatility third and by the stock's 50-day trend.

**P4b. Round-number clustering** (Osler's test): daily highs and lows of TSLA, SPY and the 81 stocks, 2015–2026.
* **Round levels:** multiples of $10 for prices above $100, $5 for $20–100, $1 below $20; SPY uses multiples of $5.
* **Statistic:** the share of daily highs that end in the band just **below** a round level (within 0.5% under it) vs just **above** it (within 0.5% over it).
  * Take-profit and limit orders at the level should make highs stall just below it: share below > share above.
  * Lows are mirrored.
* **Also:** the next-day return after a close that crossed a round level vs one that stopped just short of it.
* Binomial test on below vs above; bootstrap by day for the returns.

**P1 additions:**
* TSLA's **opening auction and first 30 minutes on Oct 26** (5-minute bars): volume relative to its recent first-bar average, and the price path.
* **Short interest,** if a free source can serve it (FINRA bi-monthly short interest or the Yahoo key statistics), as context only.

## P1 results (`p1_tsla.py`; `out/p1.json`, `out/p1_events.csv`)
**Historical: TSLA up-gaps ≥ 2% with a call strike within +10%, 2020–2026 (228 events).**

| | Crossed the largest call-OI strike (60) | Did not cross (168) | Difference, p |
|---|---|---|---|
| Open → close | **−0.58%** (median −0.82%) | +0.28% (median +0.03%) | −0.86 points, p 0.17 |
| Next 5 days from the close | −0.09% | −0.08% | ≈ 0 |
| Filled the same day | 35% | 31% | p 0.57 |

* After crossing a big call strike, gaps tend to **fade** intraday: the dealer-lid direction (dealers long calls sell into the rise).
* Not significant. **The forced-buy-by-dealers idea gets no support.**

**Monday Oct 26 (descriptive):**
* **Call OI within 45 days** (positions at Friday's close): 375 → 21.2k, **380 → 27.1k**, 385 → 18.9k, 390 → 15.9k, 395 → 17.5k, **400 → 42.4k**.
* **Dealer hedge flow from $372.22 to $391.62:**
  * classic convention (supported for TSLA calls by dealer-sign): dealers had to **sell about 5.9M shares**;
  * all-short convention: they would have had to buy about 20M.
  * Dealers were **not** the forced buyers; they leaned against the move, toward the 400 lid.
* **Levels where shorts' stops sit:** Friday's high $377.32, gapped over at the open. The **triple top $388.56 / $388.84 / $388.86** (the Oct 9, 21 and 22 highs; Oct 22 was the earnings-spike high).
* **Price path:** open $383.97; **the first 5-minute bar closed $389.49, through the triple top within 5 minutes**; $393.82 by 10:00; high $397.27, just under the 400 round number and call wall. The day's low was the opening print.
* **Opening volume:** first 30 minutes about **2.5×** the prior 4 days' first-30-minute average (Yahoo 5-minute bars).
* **Short positioning:**
  * FINRA short interest 70.9M shares at the Sep 30 settlement (68.9M Sep 15), **about 1.9 days to cover**: modest, around 2% of shares.
  * Off-exchange short-sale ratio: Oct 21 0.60, Oct 22 0.52, Oct 23 0.58, vs a 60-day mean of 0.50 (10th–90th percentile 0.41–0.61). Upper range, not extreme.
  * The Oct 15 settlement isn't published yet; **the Oct 30 settlement (published around Nov 10) will show whether shorts covered.**
* **Reading:**
  * The **gap (+3.2%) was news**: the Barclays upgrade and SpaceX merger talk.
  * The **open-to-close +2.0%** has the footprint of a **stop run above the $389 triple top**: an immediate break, heavy opening volume, no pullback. That fits short covering by shorts who sold the earnings spike, plus momentum buyers.
  * It was a burst, not a squeeze: short interest is modest (about 2 days to cover), and dealers were selling into it.
  * Historically, gaps over big call strikes fade intraday, so Monday bucked that tendency. That is consistent with an extra, non-dealer buyer.
