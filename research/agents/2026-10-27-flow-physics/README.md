# Order-flow physics of the last weeks (SPY via ES, TSLA) and a tested trajectory for the next days

* **Owner, 2026-10-27:**
  * "use Databento for the best useful tests to explain the last few days' price action on weekly and daily frames, and to put a statistical trajectory on the next few days, with explanations we can reuse (strengthen our grasp of market mechanics)";
  * "I want to make an entry for the possible November rally on SPY and TSLA, if we can confirm a lasting burst and it drops a bit to a favourable price";
  * "rigorous quant, elegant physics-like stuff"; budget about $15.
* **Why this design:** the last three studies tested patterns without a mechanism ([flip-wicks](../2026-10-27-flip-wicks/) correction). Here every measurement is a named mechanism from the microstructure literature, measured on the actual order flow, against each instrument's own baseline weeks.
* **Data (Databento, licensed, kept in `data/`, gitignored):**
  * ES (CME, ESZ6) trades with aggressor side, regular hours, Oct 5–26 (16 sessions). ES is SPY's single central book.
  * One ES order-by-order (MBO) session (Oct 20).
  * TSLA Nasdaq trades with aggressor side, Sep 21 – Oct 26 (Nasdaq is part of TSLA's volume; stated limit).
  * Closing-auction imbalances: SPY (NYSE Arca), and TSLA, GOOGL, AMZN, NVDA, AVGO, MSFT, AAPL, META, QQQ (Nasdaq), Sep 21 – Oct 26.
  * Oct 27 is added when Databento publishes it.
  * Quoted cost about $9.3 now, plus about $5 for Oct 27.
  * Not bought: the SPY 0DTE options tape ($16–21 per day).
* **Free data:** ThetaData Value chains, SqueezeMetrics, Yahoo bars, and our engine.

## Part A — mechanics of the last weeks (each is a named mechanism; baseline = the instrument's own other sessions)
**A1. Who drove each day: signed flow and Kyle's lambda** (Kyle 1985; Hasbrouck 1991).
* Per session: aggressor-signed volume ("delta", buy − sell) and its running sum, daily and weekly.
* Kyle's λ: per session, regress 5-minute price changes on 5-minute signed volume. λ = price move per contract of net aggression, i.e. 1 / market depth.
* **Reading:**
  * A move with large delta and normal λ is *driven* (aggressors paid up).
  * A move with small delta and high λ is *liquidity-led*: the book thinned, so little flow moved price far.
* **Prediction:** the down legs (Oct 16, Oct 22–23) were driven by sell aggression with λ above the baseline median. The Oct 26 rally was driven by buy aggression.

**A2. How self-exciting the tape was: Hawkes branching ratio** (Filimonov & Sornette 2012; Hardiman, Bercot & Bouchaud 2013).
* Market-order arrivals (trades with the same timestamp and side merged into one event) are fit with an exponential-kernel Hawkes process by maximum likelihood, in 30-minute windows.
* The branching ratio n is the share of activity triggered by earlier activity (endogenous) rather than by outside news. n → 1 is a "critical" market where cascades run.
* Daily median n for ES and TSLA.
* **Prediction:** n is higher on the trend days (Oct 16, 22, 26) than on drift days.

**A3. How long a trade's push lasts: the propagator** (Bouchaud, Gefen, Potters & Wyart 2004; Lillo & Farmer 2004).
* Sign autocorrelation of merged market orders, C(ℓ) ~ ℓ^(−γ): long memory, from order splitting.
* Response R(ℓ) = ⟨ε_n (p_{n+ℓ} − p_n)⟩.
* Physics consistency check: prices stay diffusive only if the impact kernel decays as ℓ^(−β) with **β = (1 − γ)/2**. We estimate γ and β separately and test whether β ≈ (1 − γ)/2 (within ±0.1).
* Per regime: the persistence ratio R(1000)/R(10) on up days vs down days.

**A4. The flip wicks in the footprint (ES).**
* Days whose SPY high came within ±0.15% of the pre-open flip (incl. 0DTE; flip-wicks `recent.json`): Oct 14, 15, 16, 19, 20 (Oct 27 later).
* SPY → ES via the open's ES/SPY ratio.
* In the last 0.10% of the run into the day's high vs the prior 30 minutes:
  * buy-aggressor volume per minute;
  * price progress per 1,000 contracts bought (absorption ratio).
* **Absorption** (a passive seller): buying holds or rises, progress collapses. **Exhaustion** (the chase stops): buying falls.
* Placebo: the same measures at the highs of the other sessions in the window.
* **Prediction from the H1 mechanism** (dealers' chase stops at the flip): exhaustion, not absorption.
* MBO on Oct 20: whether the offers at the high refilled (iceberg / passive seller).

**A5. Closing auction: does the published imbalance push the close?** (Cushing & Madhavan 2000; Bogousslavsky & Muravyev 2023).
* For each symbol-day: the first imbalance message at or after 15:50:00 ET, signed by side; dollars = paired-off imbalance quantity × reference price.
* Outcome: the 15:50 → close return (Yahoo 5-minute bars).
* **Test:** Spearman correlation of signed imbalance (as % of the day's dollar volume) with the outcome, pooled over about 10 symbols × 25 days, bootstrap by day. **Passes if > 0 with p < 0.05 (one-sided).**

**A6. TSLA's Oct 26–27 composition.**
* TSLA daily delta, λ and Hawkes n vs its 5-week baseline.
* Retail-size share (trades < 100 shares).
* Around the $389 cross on Oct 26: buy-aggressor events per second in the 60 s after the first print above 388.90 vs the 60 s before, and vs the same at the day's other round-dollar crosses (stop-cascade signature: a burst right after the cross).

## Part B — a trajectory for the next days, and an entry rule (free data; methods fixed here)
**B1. Risk-neutral distribution** (Breeden & Litzenberger 1978).
* From the latest ThetaData closing chains: SPY and TSLA, Oct 30, Nov 6 and Nov 20 expiries.
* Smoothed IV smile → density → quantiles, and P(below / above key levels).

**B2. Conditional ensemble (real-world distribution).**
* **SPY:** analog days, S&P 2012–2026, matching today's state, defined now:
  * R2 fired within the last 10 sessions;
  * S&P within 2% of its 252-day high;
  * VIX 15–20.
  * Fan of 1–20-day forward returns (5/25/50/75/95%), and P(+3% before −3%).
* **TSLA:** 2021 – Oct 14 2026: freed (near-price OI ≤ 1/3 pctile) and above its own flip by > 5%. Forward 1–10-day fan vs all days.

**B3. November base rate:** S&P November returns 1950–2025, all years and years where the S&P ended October within 3% of its 52-week high. Descriptive.

**B4. Entry physics: first-passage probabilities (reflection principle / gambler's ruin for drifted Brownian motion).**
* P(touch a pullback level L within T days) and P(L before target U), from σ (implied vol) and μ (= 0 as the null; B2's conditional drift as the alternative).
* **Validation test (must pass before use):**
  * SPY daily paths 2012 – Oct 12 2026. Each day, with σ from that day's VIX, predict P(touch −1%, −2%, −3% within 5 and 10 sessions).
  * Compare with what happened: calibration slope (realized on predicted, binned) and Brier skill vs the unconditional rate.
  * **Usable if the slope is within 0.8–1.2 and Brier skill > 0.**
  * Same for TSLA with its 30-day ATM IV (engine history).

**B5. "Lasting burst" confirmation rule** (from earlier results, not tuned here).
* For SPY 2020 – Oct 12 2026 (pre-open flips from flip-wicks), the confirmation = **a close above the pre-open flip AND SqueezeMetrics GEX < 90th pctile (not pinned)**.
* Prediction: forward 10-day return and P(new 20-day high before −3%) are higher on confirmed days than on other days within 2% of the high.
* Circular-shift null on the confirmation series. **Passes if p < 0.05.**
* Descriptive add-on: whether breadth (50-day participation rising over 5 days) strengthens it.

**Reporting:** every result with its denominator. Part A is mechanism measurement on a few weeks, so it explains, it does not forecast. Only B4 and B5 (tested on years) may be used for the entry.
