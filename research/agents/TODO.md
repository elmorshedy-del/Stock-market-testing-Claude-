# Agent research to-do (owner, 2026-10-27: "write these as to do until I get the data")

Open leads, grouped by what unblocks them. Source: [2026-10-26-ladder-status](2026-10-26-ladder-status/) §4.
When a lead is run, move it to **Done** with a link to its folder and INDEX row.
Every test is pre-registered in its own folder before it runs.

## Blocked on data the owner is getting

### ThetaData Options Standard ($80/mo; tick trades + every NBBO quote)
- [ ] **T1. Signed 0DTE and option flow.** Re-run order-flow A1–A4, which were void because minute-bar signing came out backwards. Does signed customer flow lead SPY over the next 5–30 minutes and over the next day? Does it add to breadth at the start of channel dips?
  - Hint so far: Oct 16 single day, next-5-minute correlation +0.23 (p 0.027).
  - Source: [order-flow](2026-10-25-order-flow/), [spy-intraday-levels](2026-10-16-spy-intraday-levels/).
- [ ] **T2. TSLA put-side dealer sign.** Use open/close trade flags to measure who is long or short TSLA puts. This decides whether "below the flip" is a real hedging state for TSLA.
  - Current evidence: put gamma inconclusive, +0.026, p 0.24.
  - Source: [dealer-sign](2026-10-16-dealer-sign/).
- [ ] **T3. Large put closes: tell real closes from transfers.** P3 found 9 events, in the right direction but at noise level. Use signed trades to confirm each event was a buyer closing, and extend to IWM, XLK and single names to get more events.
  - Source: [positioning-tests](2026-10-26-positioning-tests/) P3.

### Databento (equities order book and trades; spend the $125 free credit first, get a cost quote, ask the owner before spending)
- [ ] **D1. Intraday stop cascades.**
  - Events: crossings of the prior 20-day high, prior highs (like TSLA's $389 triple top), and round numbers.
  - Measure: whether order flow and the speed of price jump in the first minutes after the crossing, vs near misses.
  - Daily bars showed no follow-through (P4a). The mechanism is intraday.
  - Source: [positioning-tests](2026-10-26-positioning-tests/) P1, P4a.
- [ ] **D2. Order-book depth at round numbers and gamma strikes.** Does resting depth peak at round numbers (Kavajecz & Odders-White) and at the call and put walls? P4b proved highs and lows cluster there; D2 would show the orders themselves.

- [ ] **D3. Closing-auction imbalances.** Use NYSE/Nasdaq imbalance messages (Databento imbalance schema). Does the 15:50 published imbalance explain the last-10-minute move, and does it interact with the 0DTE map? Oct 27's drop began at 15:50.

### Sierra Chart Package 11 or 12 + Denali CME feed (about $57–67/mo)
- [ ] **S1. ES futures footprint at SPY gamma levels.** Measure absorption (large volume, little price progress) and delta divergence at the flip, the walls and the pockets, vs equally round placebo levels. ES has one central order book, so this is the cleanest order-flow test of the gamma map.

### Cboe COR1M history (implied correlation; Yahoo serves no history)
- [ ] **C1. The letter's correlation rule with its real variable.** Re-run P2 with COR1M in place of realized 10-day correlation, plus a channel-era check (only 42 GEX < 0 days since 2023).
  - Source: [positioning-tests](2026-10-26-positioning-tests/) P2.

### Databento, reserved (~$5.8 left of the owner's $15)
- [ ] **D4. Add Oct 27 to flow-physics** once published: ES trades + MBO (the 771 wicks and the 15:50 drop), SPY/Nasdaq closing imbalances (did a sell imbalance print at 15:50?), TSLA trades (the 400 break). About $1.6.

## Can run now (data in hand)
- [ ] **N1. SqueezeMetrics GEX vs our engine when they disagree.** Example: on Oct 23 SqueezeMetrics showed +$4.0bn while our engine showed −$8.8bn. Only SqueezeMetrics carries P2; our flip carries the rally-hold result. Test which measure predicts better on the days they disagree.
- [ ] **N3. Who is long the 0DTE calls? A last-30-minute convention test.** On 711 days, does the 15:30 → close move continue the day's move more when the 0DTE strikes near the price are put-heavy (classic: dealers short gamma) than call-heavy (classic: dealers long gamma)? Classic predicts a difference by call/put mix; all-short predicts momentum scales with total 0DTE gamma regardless of mix. Prompted by Oct 27's last-10-minute drop through the 770 calls. [flip-wicks](2026-10-27-flip-wicks/).
- [ ] **N4. Pre-earnings de-risking into the close.** Do mega caps underperform in the last 30 minutes of the day before their report, more so after an up day? Oct 27: GOOGL −0.66%, AMZN −0.36% in the last 10 minutes. Hourly bars in hand (51 tickers, Nov 2023 →); earnings dates needed.
- [ ] **N2. Breakaway-gap rule beyond TSLA.** TSLA breakaway gaps fill less (p 0.04). Pre-register the same rule on the 81-stock panel and SPY/QQQ.

- [ ] **N5. Liquidity regime test.** Does ES Kyle lambda (book depth) track dealer gamma over a long sample? Flow-physics found rho -0.37 on 16 days. Needs more ES trade days, or a cheaper depth proxy (ohlcv range / volume).
- [ ] **N6. A calibrated pullback model.** The reflection principle fails with VIX (B4). Test a VIX × (realized/implied ratio) scaling or a GARCH sigma, walk-forward, with the same calibration rule.

## Needs time (more events), re-test on schedule
- [ ] **R1. TSLA RSI divergence after a 1-ATR bounce:** 86% vs 69% held (21 cases, p 0.21). [technical-indicators](2026-10-16-technical-indicators/) B.
- [ ] **R2. MSFT stretched-release lead:** 28% vs 62% (p 0.053). Weekly ADX in trends: +23 points (raw p 0.046).
- [ ] **R3. TSLA R7 (S&P vol crush):** 82% up-burst (11 events, raw p 0.02, about 0.2 after correction). REPORT §4l.
- [ ] **R4. SPCX–TSLA lead-lag:** retest around Feb 2027. [spcx-tsla-lead-lag](2026-10-16-spcx-tsla-lead-lag/).

## Live forward checks (calls already made)
- [ ] **F1. Channel call:** the S&P makes a new high above 7,818.93 before closing at or below 7,427.98 ([channel-correction-theory](2026-10-25-channel-correction-theory/)).
- [ ] **F2. S&P ladder:** whether an up-leg starts within 20 sessions of R2 turning on (Oct 20). History: 78% since 2019Q4, 64% since 2012. Watch R4/R5 (S&P ≤ 7,602 with GEX ≤ 20th) and R6/R7 (VIX ≤ 16.5 / ≤ 14.6 from Oct 30).
- [ ] **F3. TSLA "freed only" state after the Oct 30 expiry** (near-price OI at the 0.4th percentile): do bigger moves follow (20% up / 23% down within 3 sessions historically)? Is $400 the lid and $389 the support?
- [ ] **F4. TSLA short covering:** FINRA short interest for the Oct 30 settlement, published around Nov 10. Sep 30 was 70.9M shares.
- [ ] **F5. AAPL residual Oct 26 – Nov 2** (R3d, [aapl-decoupling](2026-10-25-aapl-decoupling/)).

## Done
- (none yet)
