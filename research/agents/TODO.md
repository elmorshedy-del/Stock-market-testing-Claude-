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

- [x] **D5. Opening cross and first-30-minute flow.** Done: [gap-teardown](2026-10-28-gap-teardown/), INDEX 2026-10-28 (opening cross balanced, flow adds nothing beyond the 5-min price move). Nasdaq opening imbalance (`imbalance` schema, auction type O) and TSLA aggressor flow in the first 30 minutes on gap days: buying exhaustion vs active selling. About $0.05 a day.
- [ ] **T4. Call profit-taking at the open.** Near-money call OI change (next-morning OI) plus signed option trades on gap days: do customers selling calls force dealers to sell stock hedges? (ThetaData Standard.)

### Sierra Chart Package 11 or 12 + Denali CME feed (about $57–67/mo)
- [ ] **S1. ES futures footprint at SPY gamma levels.** Measure absorption (large volume, little price progress) and delta divergence at the flip, the walls and the pockets, vs equally round placebo levels. ES has one central order book, so this is the cleanest order-flow test of the gamma map.

### Cboe COR1M history (implied correlation; Yahoo serves no history)
- [ ] **C1. The letter's correlation rule with its real variable.** Re-run P2 with COR1M in place of realized 10-day correlation, plus a channel-era check (only 42 GEX < 0 days since 2023).
  - Source: [positioning-tests](2026-10-26-positioning-tests/) P2.

### Databento, reserved (~$5.8 left of the owner's $15)
- [x] **D4 done** ([deferred-days](2026-11-04-deferred-days/), $1.25 with G1): sell imbalance at 15:50 confirmed; A4 exhaustion fails again. ~~D4. Add Oct 27 to flow-physics~~ once published: ES trades + MBO (the 771 wicks and the 15:50 drop), SPY/Nasdaq closing imbalances (did a sell imbalance print at 15:50?), TSLA trades (the 400 break). About $1.6.

## Can run now (data in hand)
- [ ] **N1. SqueezeMetrics GEX vs our engine when they disagree.** Example: on Oct 23 SqueezeMetrics showed +$4.0bn while our engine showed −$8.8bn. Only SqueezeMetrics carries P2; our flip carries the rally-hold result. Test which measure predicts better on the days they disagree.
- [ ] **N3. Who is long the 0DTE calls? A last-30-minute convention test.** On 711 days, does the 15:30 → close move continue the day's move more when the 0DTE strikes near the price are put-heavy (classic: dealers short gamma) than call-heavy (classic: dealers long gamma)? Classic predicts a difference by call/put mix; all-short predicts momentum scales with total 0DTE gamma regardless of mix. Prompted by Oct 27's last-10-minute drop through the 770 calls. [flip-wicks](2026-10-27-flip-wicks/).
- [x] **N4. Pre-earnings de-risking into the close.** Run in [calendar-mechanics](2026-10-29-calendar-mechanics/) B5: −0.14% in the last 30 minutes (raw p 0.03, Holm 0.13). Do mega caps underperform in the last 30 minutes of the day before their report, more so after an up day? Oct 27: GOOGL −0.66%, AMZN −0.36% in the last 10 minutes. Hourly bars in hand (51 tickers, Nov 2023 →); earnings dates needed.
- [ ] **N2. Breakaway-gap rule beyond TSLA.** TSLA breakaway gaps fill less (p 0.04). Pre-register the same rule on the 81-stock panel and SPY/QQQ.

- [ ] **N5. Liquidity regime test.** Does ES Kyle lambda (book depth) track dealer gamma over a long sample? Flow-physics found rho -0.37 on 16 days. Needs more ES trade days, or a cheaper depth proxy (ohlcv range / volume).
- [ ] **N6. A calibrated pullback model.** The reflection principle fails with VIX (B4). Test a VIX × (realized/implied ratio) scaling or a GARCH sigma, walk-forward, with the same calibration rule.

- [ ] **N7. Premarket drift and overnight-high timing** as an open-fade predictor (Oct 28: the 4am print was the high). Needs premarket bar history.
- [ ] **N8. The 3-of-4 open-fade state** (extended run + long gamma + open above the call wall): first hour −0.83%, median dip −2.1% on 25 events. Re-test as events accrue.

## Needs time (more events), re-test on schedule
- [ ] **R1. TSLA RSI divergence after a 1-ATR bounce:** 86% vs 69% held (21 cases, p 0.21). [technical-indicators](2026-10-16-technical-indicators/) B.
- [ ] **R2. MSFT stretched-release lead:** 28% vs 62% (p 0.053). Weekly ADX in trends: +23 points (raw p 0.046).
- [ ] **R3. TSLA R7 (S&P vol crush):** 82% up-burst (11 events, raw p 0.02, about 0.2 after correction). REPORT §4l.
- [ ] **R4. SPCX–TSLA lead-lag:** retest around Feb 2027. [spcx-tsla-lead-lag](2026-10-16-spcx-tsla-lead-lag/).

## Gap-teardown follow-ups (2026-10-28)
- [x] **G1 done** ([deferred-days](2026-11-04-deferred-days/)): Oct 28 flagged at 09:35 only. ~~G1. TSLA Oct 28 on Databento~~ (publishes about Oct 29): trades, book and cross; place on the T1/T3 distributions. About $0.2.
- [ ] **G2. The other 9 names** (AMD, META as FB before 2022-06-09, MSFT, AMZN, GOOGL, AVGO, NFLX, MU, ORCL with no Nasdaq cross). Labels already fetched for about 170 dates. About $40+ for the book pull.
- [ ] **G3. "Depth builds behind the move"** as a pre-registered test: do offers stacking above a falling price within 30 minutes cap rebounds (and bids under a rising one stop pullbacks)?
- [ ] **G4. Hidden selling at the high:** MBO executions vs displayed size (iceberg refills) at the first-hour high on VF days vs SC days. Needs mbo, about $0.3 an event.

## Gap-context follow-ups (2026-10-29)
- [ ] **E1. Earnings-morning fade mechanism:** the IV drop across the report (EOD chains) × pre-report call OI near the price vs the first-hour fade. TSLA/NVDA in hand (small n). OPRA signed flow at 09:30 on earnings mornings (Databento quote first) doubles as gap-teardown H4.
- [x] **E2 (partly). 13 names labeled** (4,583 gap-ups); the earnings-gap fade replicates out of sample, Holm 0.031 ([calendar-mechanics](2026-10-29-calendar-mechanics/) B2). Still to do: re-run the rest of C and F on all 13. (labels about $0.2) to triple n. Pre-register C7 (earnings fade) and C1 (wall caps continuation) as directional confirmations.
- [ ] **E3. Microstructure precursors** (Amendment 1): Hawkes branching, Kyle lambda, depth and closing imbalances over the 3 sessions before each sampled gap. Databento quote first.

## Calendar-mechanics follow-ups (2026-10-29)
- [ ] **K1. What makes September's second half extra weak:** post-summer equity issuance (IPO and secondary counts by month, for example Ritter's IPO data), fiscal half-year and quarter ends abroad, global fund flows. Pre-register on data after 1987.
- [ ] **K2. Earnings-fade mechanism, round 2:** after-hours headline overshoot vs the conference call (after-hours price at 16:30 vs 18:00 vs the open), and pre-report positioning (the B5 close drift) as the predictor.
- [ ] **K3. GEX roll-off dose** (A7, Holm 0.10): re-test forward on 2026–27 expiries, and with SPY's own expiring-gamma share.

## House-of-cards follow-ups (2026-10-29)
- [ ] **HC1. Forward log:** for every gap-up in the 5 chain names, record the forced/genuine signature at the prior close and the open→close outcome. This is the out-of-sample check of the exit tilt.
- [ ] **HC2. Market-level signature for all 13 names** (VIX/VXN instead of own IV, much larger n). Pre-register before running.
- [ ] **HC3. Earnings morning × forced run:** do the two fade mechanisms stack?

## Permanence follow-ups (2026-10-30)
- [ ] **PM1. Call-skew footprint at scale:** 25-delta risk-reversal change over runs for more names and years (ThetaData history), pre-registered directional (ρ < 0).
- [ ] **PM2. Low-volume runs cliff more** (35% vs 28%) and **thin-liquidity runs' gap days fade**: pre-register as directional and test on the 83-name breadth panel names not in the 42.
- [ ] **PM3. Forward log:** call-skew change and volume tercile at each run end, for TSLA/NVDA/QQQ/SPY.

## Options-regime follow-ups (2026-10-30)
- [ ] **T5. Pre-2020 single-stock options (ThetaData Standard):** call skew, ATM IV and gamma footprints in R0, so every option-linked result gets a three-era comparison.
- [ ] **RG1. The 0DTE-era call-skew rule** (ρ −0.33, n 100): pre-register as directional and confirm forward, plus on more names once chains allow.
- [ ] **RG2. The earnings-morning fade by era and by pre-report option positioning** (call OI and skew going into the report), 2020+.

## Live forward checks (calls already made)
- [ ] **F6. First-5-minute table** (gap-teardown, exploratory): log every TSLA/NVDA/AAPL/QQQ gap-up ≥ 0.5σ from Oct 29: the 09:30–09:35 bin and the 09:35–10:30 outcome.
- [ ] **F1. Channel call:** the S&P makes a new high above 7,818.93 before closing at or below 7,427.98 ([channel-correction-theory](2026-10-25-channel-correction-theory/)).
- [ ] **F2. S&P ladder:** whether an up-leg starts within 20 sessions of R2 turning on (Oct 20). History: 78% since 2019Q4, 64% since 2012. Watch R4/R5 (S&P ≤ 7,602 with GEX ≤ 20th) and R6/R7 (VIX ≤ 16.5 / ≤ 14.6 from Oct 30).
- [ ] **F3. TSLA "freed only" state after the Oct 30 expiry** (near-price OI at the 0.4th percentile): do bigger moves follow (20% up / 23% down within 3 sessions historically)? Is $400 the lid and $389 the support?
- [ ] **F4. TSLA short covering:** FINRA short interest for the Oct 30 settlement, published around Nov 10. Sep 30 was 70.9M shares.
- [ ] **F5. AAPL residual Oct 26 – Nov 2** (R3d, [aapl-decoupling](2026-10-25-aapl-decoupling/)).

## Week-review follow-ups (2026-10-31)
*Context: Fri Oct 30 S&P −1.8% month-end flush to SPY 750.36 (the put wall); R4 fired; TSLA held 400 on its expiry; third-party "stealth bear market" note checked.*
- [ ] **WR1. Expiry-day pin vs market selloff:** on S&P down days that are also big single-name expiries, does price hold the top-gamma strike? TSLA Oct 30 held 400 on S&P -1.8% (one case). [week-review](2026-10-31-week-review/).
- [ ] **WR2. Translator bands:** report D1-style beta translations with the excess-return spread (TSLA SD 3.4 pts), never a point range. [week-review](2026-10-31-week-review/).
- [ ] **WR3. Score R4 (fired Oct 30):** up-leg (10-day S&P rise >= ~3.5%) by about Nov 27? And the election VIX release (fit -3.8 pts in the 5 sessions after Nov 3).

## Friday-narrative follow-ups (2026-11-01)
*Context: the Fri Oct 30 low at 14:52 (SPY 750.38) was a retest. Price made a slightly lower low than at 14:35 (750.54) while VIX made a lower high (22.8 vs 23.9), and the hedge model's vanna term had flipped to dealer buying at 14:40. The rule below comes from the hedge equation H = −Γ·ΔS − Vanna·Δσ − Charm·Δt. Owner asked (2026-11-01) whether it "would usually work": untested.*
- [ ] **ND1 (added 2026-11-01, from the Fri Oct 30 14:52 low). Vol-divergence turn rule (derived from the vanna hedge term):** in short gamma, a price low that is not confirmed by a new implied-vol high marks the end of forced selling. Daily version on free data since 1990 (S&P new 10-day low with VIX below its high at the prior low, SPY below flip where known); intraday version needs SPY ATM IV from OPRA. Pre-register before running. [friday-narrative](2026-11-01-friday-narrative/).
  * Plan: (a) daily version first (free data since 1990); (b) intraday version only after checking the OPRA cost.
  * Outcome to test: next 1–10 day S&P return and P(up-leg) after a divergence low vs other new lows. Report era splits per OWNER_NOTES (pre-2020 / 2020–21 / 2022+).

## Gamma-wall follow-ups (2026-11-01)
*Context: iteration 3/3b of the gamma phase diagram found that the prior day's SPY call wall stops the day's high ~1.4x as often as ordinary $5 strikes (+11 to +15 pts, replicated in QQQ, survives VIX and prior-high controls; smaller since 2022). The put wall did not act as a floor.*
- [ ] **GW1. TSLA as a third asset (same design):** mechanism-derived prediction. Classic convention (dealer-sign Part B) implies a stall at TSLA's call wall, but weaker since 2023 (call damping p 0.10). Owner's 400 intuition: TSLA closed 399.81 on its 400 call wall Oct 30. Pre-register before running. [gamma-phase-diagram](2026-11-01-gamma-phase-diagram/).
- [ ] **GW2. Dose-response with per-strike OI** (ThetaData EOD OI, not Databento): does the stall gap scale with the wall's OI dominance (wall OI / next-largest)? Separates gamma dose from level memory (anomaly G).
- [ ] **GW3. Live forward log of the exit rule:** each SPY day whose high tags the prior call wall, record stall (±0.1%) and the run past it; compare with the 43% / 18% (> 0.5%) base rates.
- [ ] **GW4. Put wall (anomaly F) parked:** SPY lows ran through the put wall (2/29 stopped) but QQQ did not repeat it. Revisit once >= 60 SPY put-wall touches exist.
- [ ] **GW5. Sell the upside at the wall (owner's day-trade ask, 2026-11-01):** short 0DTE call / call spread at the prior call wall, opened at the first touch, held to expiry; SPY daily expiries since late 2022 (~70 touches). ThetaData 0DTE quotes (not Databento). Share-short version failed ([wall-short](2026-11-01-wall-short/)). Pre-register before running.
- [ ] **YF1. Score the year-end forecast** on Nov 13, Nov 30, Dec 31 (percentile of the SPY close in the B-all distribution; fill the log in [yearend-forecast](2026-11-01-yearend-forecast/)).
- [ ] **MC1. Score the July/October machine forecasts C1-C4** on Nov 13 and Nov 20 ([july-october-machine](2026-11-01-july-october-machine/)).
- [ ] **OS1. Flat-skew top warning (TSLA):** put skew <= 10th pct after a >= 30% run at 4 of 8 named tops; pre-register a test on all run-tops (and SPY/QQQ). [tsla-options-signal](2026-11-02-tsla-options-signal/).
- [ ] **EV1. Score the election-vol read on Nov 5:** realised SPY Nov 4 move vs implied 1.08%; TSLA Nov 3-4 move vs implied ~4.6% (two-day); TSLA IV30 Nov 2 close -> Nov 5 close (expect ~-1 pt, all else equal); ICLN/TLT results-day direction vs the Senate outcome ([election-vol](2026-11-02-election-vol/)).
- [ ] **TP1. Score the TSLA politics read on Nov 5:** TSLA residual (vs 1.56x QQQ) on Nov 4 vs the Texas Senate and House results (Paxton slope implies ~+14% if Paxton wins, ~-5% if Talarico wins; CI wide); realised Nov 3-6 move vs the priced 3.4% excess ([tsla-politics](2026-11-02-tsla-politics/)).
- [ ] **LR1. Score the Nov 2 live-read forecasts** (S1-S8 SPY, T1-T6 TSLA): S1/S2/T1/T2 after Mon close, the rest Fri Nov 6; Brier for my calls vs the options-implied map ([2026-11-02-live-read](2026-11-02-live-read/)).
- [ ] **BP1. Composite top score (TSLA, then SPY/QQQ):** flat skew + IV rising with price + fading buy aggression + near the call wall + opex within ~5 sessions; pre-register weights/thresholds before testing on tops vs kept-going days (16 tops in-sample; extend to other high-option stocks for out-of-sample). [tsla-breaking-point](2026-11-02-tsla-breaking-point/).

## HFT-papers follow-ups (2026-11-02)
- [x] **HP1 done** ([orb-gamma](2026-11-02-orb-gamma/)): SPY fails, gamma doesn't rescue it, TSLA lives. Follow-ups OG1-OG2.
- [x] **OG1 done:** TSLA 5-min breakout passed on 2020-23 (+29.5 bp/day, p 0.018).
- [ ] **OG3. News-gap / in-play filter, pre-registered:** trade the 5-min breakout on single stocks only on days with |gap| above a fixed ex-ante threshold (e.g. > 1x the 14-day ATR%), test on 2020-23 for NVDA/AMD/NFLX (XNAS, about $1.5; ask the owner).
- [ ] ~~OG1. Confirm TSLA 5-min breakout on 2020-23~~ (XNAS bars, about $0.3-0.5; ask the owner), with the rule frozen as S1_5_close plus Monday/Friday and long-side splits.
- [ ] **OG2. Forward-test TSLA S1_5_close from Nov 3 2026** (paper; log each day's trade before 09:40).
- [ ] ~~HP1. ORB replication conditioned on gamma regime~~ (SPY/QQQ/TSLA 1-min, out-of-sample 2024-26, realistic costs): ORB profit should sit in short-gamma or freed days and vanish in long-gamma or pinned days ([hft-papers](2026-11-02-hft-papers/)).
- [ ] **HP3. Non-news vs news extreme AI-basket days:** do no-news forced shocks revert over 1-5 sessions (Knight-glitch logic)? Data in hand (LQ) ([hft-papers](2026-11-02-hft-papers/)).
- [ ] **HP4. VIX overnight vs intraday split by weekday;** rung hits on open vs close; post-event Wednesday pattern (Yahoo VIX OHLC) ([hft-papers](2026-11-02-hft-papers/)).
- [ ] **HP5. TSLA aggressor imbalance near round $10 levels** (Databento trades; cost quote first) ([hft-papers](2026-11-02-hft-papers/)).
- [ ] **HP6. BJZZ retail-flow measure for TSLA and 1-15 day volatility** (Databento/TAQ prints) ([hft-papers](2026-11-02-hft-papers/)).
- [ ] **HP2. First-30-min signed option flow -> TSLA rest-of-day return** (blocked: ThetaData Options Standard trades) ([hft-papers](2026-11-02-hft-papers/)).

## Earnings-mechanics follow-ups (2026-11-04, from the MSFT July-vs-now comparison)
*Owner: "This gives us tests to do for this kind of vanna and charm unwind … think what will be high value tests that we can do that can be used to trade earnings."*

**Background.** [msft-read](2026-11-04-msft-read/) found four reasons July's walls didn't slow MSFT while today's do:
1. The options were far from the price (freed: near-price OI 11th pct, dealer gamma $0.45bn per 1%, call wall 18% away).
2. An overnight gap skips dealer hedging.
3. The IV crush (45% IV) releases put hedges (vanna), on top of time decay (charm).
4. Customers chase new calls, which flips the dealer sign.

These come from **one case**; each needs a test.

**Data and rules.**
* ThetaData Value (2020+, EOD chains + daily OI). It costs only pull time, at about 1 minute per symbol-day, so pull days −1, +1 and +5 only.
* Events: the 690 in `microstructure/out/earnings_events.csv` (40+ names), plus the six `td_gamma_*.csv` series, which already carry daily vanna/charm for TSLA, MSFT, NVDA and MU.
* Report R1 (2020–21) and R2 (2022+) separately.
* Pre-register each test in its own folder before it runs.
* Related open items: E1, RG2, HC3, K2.

- [ ] **EQ0. Data step (first).**
  * Build one row per event with the pre-report state at the report-day close (OI dated that day, the report day's chain):
    * near-price OI percentile;
    * own dealer gamma, vanna and charm;
    * the call/put walls and the biggest call pile within the implied move;
    * put/call OI;
    * the implied move (front-expiry ATM straddle / spot);
    * the IV term kink;
    * drawdown from the 52-week high and distance from the 200-day average.
  * Add the outcomes:
    * the gap;
    * the close→close returns on days 1, 2–5 and 2–10;
    * the IV crush (day +1);
    * the new OI by strike on day +1.
- [ ] **EQ1. Earnings straddle by positioning state (highest value: a direct trade).**
  * **Trade:** buy the front-expiry ATM straddle at the ask at the report-day close; sell at the bid at the day +1 close, and separately at day +5.
  * **Prediction:** freed + low own gamma → realized move > implied, straddle P&L > 0. Pinned (high gamma, a big call pile inside the implied move) → realized < implied, so selling it (or an iron fly) pays.
  * **Null:** circular shift of the state across events within each name; the bootstrap is blocked by quarter.
- [ ] **EQ2. Vanna/charm-unwind fuel (the July MSFT mechanism).**
  * **Fuel:** pre-report dealer vanna exposure × the realized IV crush (IV day −1 minus IV day +1), with charm to the next expiry as a second term.
  * **Prediction:** after **up**-gaps, the day 1→5 continuation rises with fuel. Down-gaps get no help (the effect is asymmetric).
  * **Controls:** gap size, surprise size, the market's move (beta-adjusted).
  * **Tension to resolve:** this is the case where the tested earnings-morning fade (calendar-mechanics B2) should **not** happen.
- [ ] **EQ3. Where the gap lands relative to the call pile.**
  * **Classes:** (a) the gap open lands below the biggest call pile within +5%; (b) it jumps through the call wall.
  * **Prediction:** (a) a smaller day 2–5 range, pinned toward the pile; (b) continuation.
  * **Dose:** wall OI ÷ next-largest strike (like GW2).
- [ ] **EQ4. Call chase after the gap (Value-tier OI version).**
  * **Measure:** new call OI on day +1 at strikes above the gap open, as a multiple of prior OI, plus the day-1 call/put volume ratio.
  * **Prediction:** a big chase → day 2–5 continuation (dealers short gamma).
  * The signed version (who opened) needs ThetaData Standard (see T4).
- [ ] **EQ5. Charm into the first monthly expiry after the report.**
  * **Measure:** post-report drift by sessions to that expiry and by the expiring share of put gamma that is OTM after the gap.
  * **Prediction:** when the expiry falls 3–8 sessions after the report and large OTM put OI expires, the drift into the expiry is up.
- [ ] **EQ6. Under-owned + surprise.**
  * **Classes:** a pre-report drawdown ≥ 20% and below the 200-day (MSFT July), vs at-highs stretched (MSFT now).
  * **Prediction:** larger, longer post-beat drift for the under-owned class (the conditioned version of post-earnings drift). Links to R2 (the MSFT stretched release).
- [ ] **EQ7. Shares vs calls for the follow-through.**
  * **Trade:** buy at the day +1 close, after the crush, either an ATM call (30–45 DTE) or the shares; exit at day 5 and day 10. Bid/ask both sides.
  * **Prediction:** in the EQ2/EQ3 continuation states, calls beat shares per dollar risked. Elsewhere the spread eats the edge (as in orb-gamma A5).

## Liquidity-cycle follow-ups (2026-11-05; owner: "hold to these tests and results for now. We will go back to them.")
- [ ] **LC1. What separates a real THINNING from a false alarm?** 29% of THINNING episodes reach THIN and 58% return to CALM ([liquidity-cycle](2026-11-05-liquidity-cycle/)). Candidate early-warning features: speed of the gamma drop, VIX rising with it, breadth, the expiry calendar. Pre-register before running.
- [ ] **LC2. TSLA flow persistence at scale** (does multi-day net aggression predict the next days?). Needs aggressor-signed trades (Databento); BVC from bars would build the answer in.
- [ ] **LC3. Claims ledger + harness refresh** (offered 2026-11-05, owner deferred): refetch bars for `rule_checks.py`, add CLAIMS.md with evidence grades, downgrade "SPY liquidity-led" in the playbook.

## Done
- (none yet)
