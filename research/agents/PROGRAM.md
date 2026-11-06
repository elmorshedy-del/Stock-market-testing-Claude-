# Research program: how a decline unfolds and where it stops (one model, three layers)

**Owner's question, the thread through every study since Oct 25:** is this a correction inside the uptrend or the start of something deeper? How do moves unfold (legs, pauses, follow-through), and where do they stop?

**One model:** price moves through a liquidity landscape. Order-flow imbalance pushes it; fear (volatility) feeds on itself; and a slow fundamental drift decides whether there is a reason to keep going. The three parts work on three time scales.

| Layer | Time scale | What it decides | Established (study) | Failed or dropped (study) | Open |
|---|---|---|---|---|---|
| **Slow: cause** | weeks to months | whether there is a reason to keep falling | today: no inflation spiral, credit calm, AI suppliers' estimates rising; but hikes are priced and stocks yield less than TIPS (regime-compare) | channels as a force (channel-physics: no pull back to the trend); bear-market calendar (channels-deep P3) | monitor 10y, oil, credit, AI capex and estimate revisions; no new tests |
| **Medium: energy and rhythm** | days to weeks | how violent, how many legs, how long the pauses last | fear is self-exciting, about 90% of big days are aftershocks, n ≈ 0.9 (aftershocks); continuations pause first: next leg a median 12 sessions after the first low; odds fade 48% → 28% → 10% at 1, 10 and 20 sessions held (aftershocks addendum 2) | power-law memory for the S&P (aftershocks H-SE1, but it holds for NDX and SOX); the VIX first-passage model has thin skill (channel-physics A1) | size-dependent aftershocks (ETAS); score the logged forecasts (Nov 13, Dec 7) |
| **Fast: mechanics** | minutes to hours | where legs accelerate and where they pause; absorption; exhaustion | low dealer gamma amplifies reactions (macro-trigger A1); Nov 5 stalled at the 735 options level (liquidity-landscape, one case) | predictable leveraged-ETF close flow moving the last 30 minutes (forced-flows: priced early); put walls stopping lows (2 of 29) | needs order-flow data: footprint, book, closing imbalances |

## How the layers link (the hypothesis to build toward)
* **Slow** sets the direction and whether follow-through has fuel.
* **Medium** sets the energy, which is the size and speed of legs and the length of pauses.
* **Fast** sets where each leg runs out of road (thick liquidity, option strikes) and when a bottom forms: the aggressive side exhausts while absorption completes.
* **A bottom is the moment all three agree:** fast-layer exhaustion, medium-layer pause lengthening, and no new slow-layer cause.

## Order of work (no new side tests until each step finishes)
1. **Now (free):** one daily three-layer reading for the owner.
   * Slow gauges.
   * Hawkes state plus the leg clock: sessions held above the first-leg low.
   * Gamma map and liquidity levels.
2. **Observe the fast layer (data, about $100 with owner approval):**
   * footprint for about 10 case days, both directions;
   * order book for 3 key days;
   * closing-auction imbalances, Jan 2024 to now, which also answers the forced-flow question directly.
   * Write observations only.
3. **Formalize and pre-register** 3–5 fast-layer measures (thin zone, absorption, exhaustion, signature) and ETAS for the medium layer. Test widely.
4. **Integrate:** forecasts of the next-leg probability, likely pause zones and pause length, scored live.

## Scheduled scoring (already logged)
* Aftershock forecasts: 2026-11-13, 12-07, 2027-02-05.
* Year-end forecast: 2026-11-13.
* Overdue follow-ups EV1 and TP1 (due Nov 5) and live-read LR1 (due Nov 6 close).

## Literature read (as outside work, not a guide)
**Muhle-Karbe, Ouazzani Chahdi, Rosenbaum, Szymanski (2026), "A unified theory of order flow, market impact, and volatility", arXiv:2601.23172 (preprint).**
Read: the main text (Sections 1–5) and the data appendix. The reference list and the proof appendices were not read.

* **Claim.** Order flow = slow "core" orders (fundamental investors, split metaorders, trend followers) + "reaction" orders (market makers, HFT), each a near-critical Hawkes process with power-law memory.
  * One parameter, the core-flow persistence H0, fixes all of these:
    * signed flow: mixed fractional, Brownian at high frequency and persistent at coarse scales;
    * volume roughness: H0 − 1/2;
    * impact exponent: 2 − 2H0;
    * volatility roughness: 2H0 − 3/2.
  * The estimate H0 ≈ 0.75 gives square-root impact and very rough volatility.
  * Data: BMLL trades, 2021–2024, 40 large caps (20 Paris, 20 NYSE).
* **Strengths.** It unifies four known laws from one mechanism. It explains why Hurst estimates of order flow rise with the sampling interval, and the mixed-fractional estimate is stable across scales.
* **Problems.**
  * The key number is inconsistent: the introduction says H0 is 0.75–0.80, but Section 3.3 says it "stabilizes around 0.65". That matters, because Section 4 needs H0 > 3/4.
  * The impact and volatility links rest on stated approximations, at the H0 = 3/4 boundary.
  * Impact and volatility are not estimated on the same data. The paper compares them with published values, so this is not a joint or out-of-sample test.
  * No index futures, ETFs, tech names or stress episodes.
  * The model has no price levels. Liquidity is the same at every price.
* **Fit with our program.**
  * Agrees with the medium layer: markets near criticality (our branching ratio is 0.87–0.95 on daily big moves).
  * Explains the forced-flows failure through its price rule: price = today's expectation of all future signed flow. Predictable flow is priced when it becomes predictable, not when it trades.
  * Does not cover the owner's liquidity landscape (price-level-dependent liquidity, absorption, exhaustion). That idea stays our own, open, contribution.
* **Plan changes (no new tests):**
  * In step 2, measure signed-flow persistence in legs vs pauses (core flow dominating vs reaction flow absorbing).
  * If the auction data is bought, split the closing imbalance into its predictable part and its surprise part. Only the surprise part should move the close.

**Correction to the review above (same day, after checking the paper's figure files and stock table).** Three of the "Problems" bullets were wrong or overstated. The lines above stay as written.
1. **"The key number is inconsistent" is resolved; it was a text slip.**
   * Values read from Figure 4's vector file: the mixed-fractional H0 averages 0.741–0.785 across 25 bin sizes (10 s to 80 min), mean 0.762.
   * The "0.65" in Section 3.3 matches the naive estimator in Figure 3 (0.657 at 1 h, 0.666 at 80 min). It is not the value Figure 4 shows.
   * The real weakness is different: the average is only about one standard error above 3/4. The median z is 1.2 assuming independent stocks, and less once stocks are correlated.
   * The 5–95% band across stocks runs from 0.56–0.69 at the low edge to 0.84–0.93 at the high edge. With a normal approximation, about 43% of stock-level estimates fall below 3/4 (26–54% depending on bin size).
   * Below 3/4 the price link in Section 4 does not apply. The data show H0 ≈ 3/4, not clearly above it. The paper does not test H0 > 3/4 and does not separate estimation noise from real differences between stocks.
2. **"No tech names" is wrong.** The sample includes STMicroelectronics (a chipmaker), Uber, Shopify, Alibaba and Visa. What is missing is Nasdaq-listed names (the AI megacaps), index ETFs and futures.
3. **"No stress episodes" is wrong.** 2021–2024 includes the 2022 bear market, the March 2023 bank stress and the August 2024 volatility spike. What is missing is a regime split: every estimate pools the whole four years.

**Additions.**
* **Strength.** Volume roughness, measured at 5–12 s bins (mean 0.239–0.293), implies H0 = 0.739–0.793. This matches the signed-flow estimate: a genuine cross-check on the paper's own data.
* **Scope.** All the evidence sits between 5 seconds and 80 minutes. Nothing is shown at daily or weekly scales, which is where our medium layer works.
