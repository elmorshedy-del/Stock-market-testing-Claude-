# Why that day? The calendar, flow and positioning context of violent gap fades and continuations (pre-registration)

* **Owner, 2026-10-29:**
  * "We didn't view these dates in the lens of funds' scheduled flows or monthly or weekly expirations… even if you view the option flow you still didn't answer why that day or that period or why at that part of the trend and prices and why that gap up. You're going too convex and not concave."
* **Builds on:**
  * [gap-teardown](../2026-10-28-gap-teardown/): nothing pre-open in the tape, auction, book or gamma *levels* separated VF from SC; the first 5 minutes did.
  * [open-fade](../2026-10-28-open-fade/): the extended-run fade died after 2020.
  * [flip-wicks](../2026-10-27-flip-wicks/): expiry-cluster drift and release; [tsla-freed-dpi](../2026-10-28-tsla-freed-dpi/); [ladder-status](../2026-10-26-ladder-status/).
* **This study asks the other question:** what *kind of day* the gap lands on.
  * The calendar of expiries and scheduled fund flows.
  * Where the stock sits in its trend.
  * Whether the gap is news or attention.
  * Whether it is the stock's own move or the market's.
  * The dealer and market regime.
* **Everything below is fixed before any context variable is joined to an outcome.**

## Amendment 1, fragility (owner: "what led to the vulnerability… was there an underlying structural weakness"; written before any test was run or any context was joined to an outcome)
* **Idea:**
  * The calendar and news contexts (C1–C12) are the *trigger*. Fragility is the *loaded spring*: a state built over days that raises how far price moves per unit of selling.
  * In physics terms, the susceptibility of the system.
  * Each measure uses only the sessions before D.
* **Family F, Holm across these 7**, same outcome handling and date-block bootstrap as C1–C12:
  * **F1, clientele tug-of-war** (Lou-Polk-Skouras 2019):
    * Over the prior 20 sessions, Σ overnight log returns − Σ intraday log returns, in σ√20, top tercile within stock.
    * Mechanism: overnight buyers keep lifting the opens and intraday sellers keep selling them, a persistent supply waiting at the open.
    * Prediction: Y1 lower.
  * **F2, thinning liquidity:**
    * Amihud illiquidity (|return| / $ volume), 5-day mean over 60-day mean, top tercile.
    * Mechanism: the same flow moves price further.
    * Prediction: Y2 larger.
  * **F3, air pocket below** (the owner's original "pocket underneath"):
    * The share of the prior 20 sessions' volume (each day's volume spread evenly over its range) that traded within 1σ below the open, bottom tercile.
    * Mechanism: few resting interests and little memory of value below.
    * Prediction: Y1 lower.
  * **F4, no dealer cushion** ("freed"):
    * The near-price OI share (±5% of the prior close, expiries ≤ 45 days, over all OI ≤ 120 days), bottom tercile within stock.
    * Prediction: Y2 larger. TSLA, NVDA, QQQ.
  * **F5, fresh call crowding:**
    * The 5-session change in call OI struck from the prior close to +10%, expiries ≤ 45 days, top tercile.
    * Mechanism: when the gap lets new call holders take profit, the dealers' hedges unwind as stock sales.
    * Prediction: Y1 lower. TSLA, NVDA, QQQ.
  * **F6, off-exchange short share** (FINRA daily, 5-session):
    * Top tercile.
    * Mechanism: wholesalers short-selling into customer buying (the SqueezeMetrics reading: demand absorbed).
    * Prediction: Y1 higher.
  * **F7, narrow market:**
    * The share of the ~50-stock panel above its 50-day average in the bottom tercile while QQQ is within 3% of its 252-day high.
    * Mechanism: leadership is thin, so index gains rest on few names.
    * Prediction: Y1 lower.
* **Not in this run (needs a Databento quote and the owner's OK):**
  * the microstructure precursors over the 3 sessions before each sampled gap;
  * the Hawkes branching ratio drifting toward 1 (criticality, Filimonov-Sornette);
  * Kyle's λ rising;
  * lit depth shrinking;
  * closing-auction sell imbalances (distribution into the close).

## Events and outcomes
* **Events:** the 1,512 labeled gap-ups (gap ≥ 0.5σ) in TSLA, AAPL, NVDA and QQQ, May 2018 – Oct 27 2026, from the gap teardown: 196 VF, 203 SC, 1,113 middle. Labels and bars are unchanged.
* **Y1, the first hour's direction:** the 09:30 open → 10:30 (close of the 10:29 bar) return, in σ (Nasdaq 1-minute bars).
* **Y2, the first hour's violence:** (first-hour high − low) / open, in σ.
* **Also reported:** the VF and SC rates and the fade share VF / (VF + SC).
* **Stock effects:** outcomes are demeaned within stock before each contrast, so a context is not credited for its stock mix.

## Context variables (all known before 09:30) and hypotheses
Each hypothesis names a mechanism and a direction. The test is the difference in mean (stock-demeaned) outcome, context vs the rest, or the stated correlation. Inference: date-block bootstrap (5,000), two-sided p. **Holm across the 12 below; pass at Holm p < 0.05.**

**Expiry clock (positioning that expires)**
* **C1, pin pull:**
  * The gap-up opens above the largest call-OI strike among expiries in the next 3 trading days (OI dated D), with that strike within 1.5σ below the open.
  * Mechanism: dealers long those calls hedge by selling into strength, and the pull grows as expiry nears.
  * Prediction: Y1 lower. TSLA, NVDA, QQQ, 2020-01 to 2026-10-14.
* **C2, gamma release:**
  * The 5 trading days after the monthly expiry (3rd Friday, or the day before it if a holiday) vs the 5 days up to and including it.
  * Mechanism: the dampening long gamma of the monthly expiry is gone.
  * Prediction: Y2 larger after.

**Scheduled fund flows**
* **C3, turn of the month:**
  * The last trading day of the month and the first 3 trading days of the next.
  * Mechanism: payroll, 401k and institutional month-start inflows (turn-of-month effect: Ariel 1987, Lakonishok-Smidt 1988, Etula et al. 2020).
  * Prediction: Y1 higher.
* **C4, month-end rebalancing:**
  * Within the last 4 trading days of the month, Spearman of the month-to-date SPY − TLT return (through the prior close) with Y1.
  * Mechanism: balanced funds and pensions sell the asset that outperformed.
  * Prediction: ρ < 0.

**Trend position**
* **C5, extended:**
  * The prior close vs its 20-day average, in σ, in the stock's top tercile.
  * Mechanism: short-term holders use the gap's liquidity to take profit.
  * Prediction: Y1 lower.
* **C6, breakout from a base:**
  * The open is above the prior 20-day high, and the prior 10-day range (in σ) is in the stock's bottom tercile.
  * Mechanism: buy-stops above the range and breakout systems.
  * Prediction: Y1 higher.

**Why that gap (news vs attention; own vs market)**
* **C7, own earnings:**
  * The first session after a post-market report (or the day of a pre-market one). AAPL, NVDA, TSLA.
  * Mechanism: information gaps continue; attention gaps revert (Berkman et al. 2012).
  * Prediction: Y1 higher.
* **C8, scheduled macro news:**
  * A CPI or jobs-report morning (8:30 ET release that day), or the session after an FOMC decision.
  * Prediction: Y1 higher (information).
* **C9, the stock's own gap:**
  * Gap minus β × the QQQ gap (β from 60 prior daily returns), as a share of the gap, in the top tercile. Stocks only.
  * Mechanism: relative-value algorithms sell a stock that gapped beyond its market.
  * Prediction: Y1 lower.

**Dealer and market regime**
* **C10, market gamma:**
  * SqueezeMetrics GEX (prior close) in the top tercile of its trailing 252 days, vs the bottom tercile.
  * Mechanism: long-gamma dealers dampen moves.
  * Prediction: Y2 smaller.
* **C11, own-dealer hedge pressure:**
  * Dealer gamma at the open price (engine pre-open map) × the gap, as a share of 20-day average dollar volume. Signed: long gamma means dealers sell into a gap-up. Spearman with Y1. TSLA, NVDA, QQQ, 2020-01 to 2026-10-14.
  * Prediction: ρ < 0.
* **C12, buyback blackout:**
  * From 14 calendar days before the fiscal quarter end to 1 trading day after the report. AAPL, NVDA.
  * Mechanism: the corporate bid is absent.
  * Prediction: Y1 lower.
  * TSLA does not buy back stock and is reported as a placebo, outside the Holm family.

## Also reported (descriptive, no test)
* Quarterly expiry and index-rebalance days, and the S&P ladder rung on each day.
* The rates for each context crossed with VF/SC.
* A context profile of the focal days: 2020-09-02; TSLA Oct 26, 27 and 28 (Oct 28 is outside the setup, gap about 0.3σ).

## Data
* Labels and bars: the gap teardown.
* Daily prices: Yahoo (stocks, QQQ, SPY, TLT).
* SqueezeMetrics DIX.csv.
* Option OI: ThetaData engine files, local.
* Earnings dates and pre/post-market timing: Alpha Vantage.
* CPI and jobs-report release dates: BLS archive pages.
* FOMC decision dates: Federal Reserve calendar, 2018–2026.
* $0 new spend.

## Limits stated in advance
* Four symbols, so context cells are small. A real but modest effect (about 0.1σ) may not pass Holm across 12.
* The 9 parked names can be labeled for about $0.2 to re-test.
* C1, C11 and the AAPL options gaps: chains for TSLA/NVDA/QQQ only.
