# Log-scale channels, from macrostructure to microstructure: MU case study

Data snapshot: close of **2026-10-01** (MU 1,097.39). Daily bars for 40 large caps
(10y), MU 5-minute (60 sessions) and 1-minute (7 sessions) bars, and the full MU
option chain (22 expiries, 3.49M contracts of open interest). All from Yahoo.
Everything below is reproducible with the scripts in this folder (see bottom).

---

## TL;DR

1. **Yes, the lines can be drawn by a computer.** Rotate a ruler in log space
   until the band holding 70% of wicks is as narrow as possible, and pick the
   anchor by scanning swing lows. Run blind on MU, the algorithm picks the
   **2025-04-07 low** (the same one you drew from) and returns a **591%/yr**
   channel, 39% wide, with R² 0.966. Today's lines: **lower 1,070 · mid 1,261 · upper 1,485**.
2. **Why log scale:** returns compound, so a constant growth rate is a straight line
   in log space. The *parallel* lines come from a moving-average identity: in a
   log-linear trend, an N-day SMA trails price by a **constant** log distance
   b·(N−1)/2. For MU that predicts the 50-day SMA sits 18.8% below the midline;
   the observed average is 16.2%, almost exactly the lower rail (16.4%). **The lower
   line is the 50-day SMA that dip buyers watch, drawn as a straight line.**
3. **Brute-force test: lines are mostly not magic.** Across 40 stocks and about 2,000
   fresh line touches (no look-ahead), rejection rates at lines are 4 pts higher than
   in random paths built from each stock's own returns. But the random-path rate sits
   **inside** the 95% confidence interval on both sides. Most of the "respect" you see
   is what any trending, volatile random walk looks like once you fit lines to it.
4. **Breakouts are partly predictable.** A walk-forward logistic model (trained before
   2021, tested 2021 onward) gets an out-of-sample **AUC of 0.62** and is well
   calibrated. Two things drive it. First, which line is touched: counter-trend lines
   break 62% of the time, with-trend lines 46%. Second, how fast price approaches the
   line, plus volatility expanding (not compressing). High volume at the touch
   slightly favors rejection (absorption).
5. **Microstructure right now (MU):** your channel has a deadline. The lower line rises
   0.77%/day, so **if MU goes flat it breaks the channel in about 3 trading days**,
   without any selloff. Options map:
   - Biggest dealer-gamma strike is **1,100**, right at spot; the next are 1,150, 1,200 and 1,300 (call open-interest wall).
   - Gamma flip is about **1,011** (classic sign convention), just under the lower line.
   - Put support is at 1,000.
   - Price just pushed above the 60-session value-area high (1,077).
   - Breakout up needs acceptance above 1,100 → 1,150. Breakdown means losing 1,070 and then 1,011, where hedging flips from dampening moves to amplifying them.

---

## 1. Computing the lines (`channels.py`)

Model: `log P(t) = a + b·t + e(t)`, with t as the trading-bar index (what a
TradingView log chart uses on its x-axis).

* **Slope:** choose b to minimise `q85(log high − b·t) − q15(log low − b·t)`. That
  is the narrowest strip containing 70% of the highs and lows. Using quantiles instead
  of max/min is what lets the June-2026 blow-off poke through, as it does in your
  drawing.
* **Lines:** upper and lower are those two quantiles; the mid is halfway.
* **Anchor:** test every 10-bar swing low 120–750 bars back. Score =
  `R² · log(length) · total trend move / width`, and keep the best.
* The tolerance `q` sets the style: 3% gives a 93% wide envelope, **15% gives 39%
  (closest to your picture)**, 25% gives 26%.

![channel](out/fig_channel.png)

Channel residual dynamics: AR(1) φ = 0.960 → **mean-reversion half-life about 17
trading days**. In theory the band acts like a spring (an Ornstein–Uhlenbeck
process around the trend). Section 3 tests whether that is real or just a
side effect of fitting the line.

## 2. Why price looks like it respects log channels: the thesis

| Mechanism | Prediction | Evidence here |
|---|---|---|
| Returns compound, so constant growth is linear in log | Straight trend line in log space only | R² 0.966 over 374 bars |
| **SMA-lag identity**: SMA_N trails a log-linear trend by b(N−1)/2 | 20/50/100-day SMAs are *parallel lines* at fixed offsets | Predicted −7.3% / −18.8% / −38.0% vs mid; observed −6.2% / −16.2% / −33.7%. Lower rail at −16.4% ≈ 50-day SMA |
| Dip buyers, CTAs and vol-targeters size in *percent* of NAV / ATR | Pullbacks are a constant % deep, so the channel width stays constant in log space | Width is stable while price went ×17 |
| Option strikes cluster at *% out of the money*, and as price rises the open interest gets rolled to higher strikes | The gamma "ceiling" travels with price at a roughly constant % above it | Call-OI strikes now sit 0–18% above spot (1,100/1,150/1,200/1,300) |
| Anchored VWAP from the low | A support level | **Rejected for this trend**: the AVWAP rises far more slowly and sits about 50% under price. It is not the rail |

**What breaks the channel:** the slope has to keep being paid for. Any month
where price grows slower than the slope (here 0.77%/day, about 17%/month)
mechanically walks price down through the lower line. That's why channels this
steep end in *time* (sideways), not necessarily in crashes. The 50-day SMA
(954 today) now sits **below** the lower line (1,070), because price has gone
sideways since June. The flow anchor has already separated from the geometric line.

## 3. Brute force: do lines matter beyond chance? (`backtest.py`)

Setup:

* **Universe and channels:** 40 stocks/ETFs, 10 years. Rolling channels (126 and 252 bars), refit every 5 bars on past data only, kept when R² ≥ 0.75.
* **Event:** a fresh touch, meaning a wick reaches a line after 5 bars without touching it.
* **Outcome (within 20 bars):** *break* = close 0.5 half-widths beyond the line; *reject* = close 0.5 half-widths back inside. The two thresholds are symmetric, so a coin-flip world gives about 50/50.
* **Null:** 12 stationary block-bootstrap paths per stock (mean block 10 days). This keeps drift, fat tails and volatility clustering but destroys any memory of price levels. The identical pipeline runs on the fake paths.

| | real reject | 95% CI (month-clustered) | null reject |
|---|---|---|---|
| lower-line touch (n = 1,194) | 39.2% | 34.9–43.4% | 35.6% |
| upper-line touch (n = 811) | 46.7% | 42.3–51.1% | 42.6% |

The real rate is higher on both sides, but neither difference is statistically
significant. In short: the channel helps you describe the trend, but it is not
yet an edge on its own.

Options-calendar tests (2018 onward, cross-sectional means per date, 105 monthly expiries):

* **Pinning:** distance of the opex-Friday close to the nearest strike = 0.247 strike units vs 0.249 on other Fridays (±0.002). **No measurable pin at the daily close.**
* **Vanna/charm drift:** week into opex −8 bp vs week after +51 bp (difference −60 ± 52 bp); realized volatility after opex / before = 1.06 vs 1.05 on other weeks. **Not significant.** The folklore exists, but you can't detect it on daily closes; it has to be measured intraday.

## 4. Predicting breakouts

Features at the touch:

* trend quality: R², slope (signed to the touched side)
* channel width in volatility units
* volatility ratio (10-day vs 60-day realized vol)
* 5-day vs 50-day volume
* 5-day close-location-value delta (a crude daily buy-vs-sell proxy)
* number of prior touches
* approach speed
* range vs ATR, gap size, extension above the 20-day SMA

One feature was removed: how far the touch bar closed through the line. Including it
pushes AUC to 0.71, but it is partly mechanical (that bar is already part way to the
break threshold).

![backtest](out/fig_backtest.png)

* Out-of-sample (2021 onward, n = 1,289): AUC **0.62**, calibrated. Predicted 41% → realised 40%; predicted 74% → realised 67%.
* **Which line, relative to trend:** the biggest single driver. Counter-trend lines (the lower line of an uptrend) break 62% of the time, with-trend lines 46%. Strong trends fail by *losing support*, not by pausing at the ceiling.
* **Approach speed:** fast approaches break more often, 62% in the top third vs 51% in the bottom third.
* **Volatility expanding:** helps (coefficient +0.39). The "squeeze" story, a compressed range before a breakout, does not show up at this horizon.
* **Volume at the touch:** high volume slightly favours rejection (−0.27). That is the absorption signature: big volume at the line without progress.

## 4b. Level hopping: do the lines predict which level is hit next? (`level_hits.py`)

Starting point: 351 moments in uptrend channels (39 stocks) where price sat at the lower line, like MU now. The benchmark is a driftless random walk with trailing 20-day realized vol; its barrier distances include the drift of the rising lines.

| Target within 20 bars | Hit | Random walk | Excess (95% CI, month-clustered) |
|---|---|---|---|
| Mid line | 23% | 24% | −1 pt (−7, +6) |
| Upper line | 6% | 7% | −1 pt (−4, +3) |
| Half a band below | 77% | 84% | −7 pt (−13, −1) |
| Next level down | 52% | 50% | +2 pt (−5, +9) |

**The levels carry almost no information beyond volatility.** Jumps between levels are just volatility measured in band-widths. For options, this moves the edge from *which level* to *realized vs implied volatility* and pin-vs-trend behaviour, where dealer gamma positioning is the candidate predictor (see §7).

## 4c. MSFT's two big up-weeks: what free data says (`week_forensics.py`)

There is no free historical open-interest data, so positioning *then* is inferred from the calendar, the VIX complex and price/volume. The current chain (2026-10-01) is a real snapshot.

| | Week of 13 Apr 2026 | Week of 27 Jul 2026 |
|---|---|---|
| MSFT / QQQ | +13.1% / +6.0% | +19.7% / +0.6% |
| Trigger | **Monthly opex week** (17 Apr), no event | **Earnings** (29 Jul after close): +11.4% gap, 3.3× volume |
| Shape | Five steady up days, small gaps, 1.0–1.4× volume (hedge unwinding) | Gap, then follow-through (+3.0%, +4.8% the next days) |
| MSFT drawdown before | −32% from high | −30% from high |
| VIX | 31 → 19 in prior 3 weeks, 17.5 by Friday | 18.6 → 16.0 |
| Read | Vanna/charm rally into opex: after the March shock, puts and hedges are crushed by falling IV and time, and dealers buy back short hedges. MSFT, the most washed-out mega-cap, rebounds most | Short squeeze after an under-owned print: low expectations, gap through the walls, dealers chase calls; IV crush releases put hedges |

Common pattern: a ~30% drawdown (under-owned, hedged), vol falling, and a forced-flow date (opex or earnings).

**Now (2026-10-01, MSFT 512.80):**

* **The setup is not the same.**
  - MSFT is up 38% from its June low, so it is not washed out.
  - VIX is 16 in contango, so there is little vol left to crush (little vanna fuel).
  - Positioning is already call-heavy (put/call OI 0.54).
* **The calendar does rhyme with July.** Oct 16 opex holds most of the near-term gamma: 62k 550 calls, 40k 510 calls, about $518M of the ~$1.16B per 1% across expiries ≤60d under the classic sign. Earnings are **Oct 28 after close**. After the 16th the pin falls away right before the event, so the **week of Oct 26 is the candidate "elevator" week**.
* **The upside case needs more than the options price.** Implied earnings move is ±6.0% (from the Oct 23 vs Oct 30 IV jump). Getting to the upper line (~585–600) is roughly a 2–2.5σ event move. MSFT moved ≥10% in two of its last four reports.

## 4d. What "frees" the market: S&P 500 dealer gamma (`release.py`)

Data: SqueezeMetrics' free daily S&P dealer-gamma estimate (GEX, from 2011) and DIX, plus the S&P 500 and the VIX complex from 1990. Outcome: the next 10-day S&P move. An "elevator" leg is a top-decile up move (base rate 10%).

**Calendar and VIX triggers alone barely matter.** Lift on P(elevator):

| Trigger | Lift |
|---|---|
| Day after monthly opex | 1.07× |
| Day after quarterly opex | 1.03× |
| VIX settlement | 0.82× |
| VIX crush | 1.13× |
| Term structure out of backwardation | 1.41× (n = 71, CI includes 1) |
| 2–3 triggers stacked | ~1.1× |

The first month of a quarter has the best 10-day returns (47–62 bp vs 8–24 bp), which fits earnings season and buyback windows reopening. That is about 2σ.

**Dealer gamma is the variable that matters.** GEX is ranked against its trailing year:

| GEX quintile | P(elevator) | P(top-decile move either way) | next-10d realized vol |
|---|---|---|---|
| 0 (lowest) | **24%** | 24% | 20.9% |
| 1 | 13% | 12% | 14.7% |
| 2 | 8% | 6% | 12.5% |
| 3 | 3% | 5% | 11.1% |
| 4 (highest) | **2%** | 3% | 9.8% |
| GEX < 0 | **33%** | 33% | 26.9% |

It survives three checks:

* **Controlling for VIX.** Within high-VIX days, P(elevator) runs 29% → 5% from low to high GEX. In low-VIX markets it is ~0 whatever GEX does: the index cannot sprint without vol.
* **Non-overlapping samples:** 22.5% → 4%.
* **2020 onward:** 28% → 3%.

For options, realized minus VIX is −2.4 vol pts at low GEX vs −7.9 at high GEX (high-VIX days). Index options are much closer to fairly priced when gamma is low. Selling vol earns most when gamma is high.

**The 2026 legs:**

* **April:**
  - GEX fell negative from the Mar 18 VIX settlement through the quarterly opex. It bottomed at **−$7.2B on Mar 27 (0th percentile)**, the low.
  - The rally began at that trough.
  - Gamma rebuilt as price rose, reaching the 99th percentile on Apr 16–17 opex, and the leg stalled.
* **July/August:**
  - GEX dropped to the 10th–20th percentile on Jul 23–28, after Jul 20 opex and around the Jul 22 VIX settlement.
  - The leg ran through earnings and stalled once GEX hit the 99th percentile on Aug 5.

**The mechanism:** a leg starts when dealer gamma is low or negative (price is "free") and ends when the rally rebuilds gamma to an extreme (price is pinned).

**Now (Oct 1):** GEX $5.6B, 44th percentile, down from $9.6B at Sep 18 opex. VIX is 16.4, mid tercile. The historical P(elevator) for this cell is ~4%. Not freed. Watch for GEX dropping into the bottom quintile around Oct 16 opex, the Oct 21 VIX settlement and earnings season.

## 4e. Earnings: does pre-event positioning decide how a surprise is priced? (`earnings.py`)

**Events:** 690 earnings reactions across 38 stocks, 2017–2026. Each is the highest-volume day of its quarter with ≥ 2.5× volume and a gap ≥ 2σ.

**What is measured:** each reaction is split into the day-0 move and a market-adjusted drift over days 1–10, signed in the day-0 direction:
* **D10 > 0** means under-priced on day 0: it kept going.
* **D10 < 0** means over-priced: it faded.

Overall: +50 bp, with 53% of reactions continuing.

| Positioning proxy | Result |
|---|---|
| **Surprise vs prior 40-day trend** (crowding proxy) | **Against a big trend** (beat after a drawdown, miss after a run-up): **+175 bp, 62% continue** [CI +44, +300]. **With a big trend:** −7 bp, 49%. Same direction under looser and stricter detectors, but the size is unstable (+46 to +131 bp) and the CI often includes zero. Strongest for the biggest surprises |
| Day-0 close location | Day 0 closing weak relative to the surprise → more later drift (regression t = −2.4). The day-0 under-reaction gets finished over the following week. Not robust to the detector threshold |
| Gap faded intraday | Gap 100–150% of the day's move: +128 bp continuation. Gap faded by more than half: −93 bp (reversal) |
| Days to monthly opex | **No effect** (+44 to +64 bp in every bucket) |
| S&P dealer gamma | Weak, and opposite to the index result (t = 1.5) |

**Reading:** your thesis survives at the one thing price data can see, how crowded the stock was going in.
* **Under-owned + surprise:** repricing is slow. Shorts and hedges unwind, and underweight holders chase for days. MSFT in July is the example: −30% drawdown, beat, +22% over five days.
* **Crowded + surprise:** it is priced on day 0 or sold on the news.

The options-specific parts cannot be tested with free data: implied move vs actual, call/put OI concentration at the strikes the gap jumps through, skew, and dealer gamma by strike. Testing them needs per-stock historical chains: ORATS / Cboe end-of-day, or start snapshotting chains before each report.

## 4f. A tradable rule: gamma release + vol crush (`strategy.py`)

**Rules** (fixed in advance; S&P 500 index, GEX from SqueezeMetrics):

* **ARMED:** GEX percentile ≤ 5% at some point in the last 15 days.
* **IGNITION:** VIX ≥ 25% below its 10-day max, first such day while armed.
* **ENTRY:** next day's close.
* **EXIT:** GEX percentile ≥ 95% (pinned) or 20 days.

Parameters were picked on 2012–2018 only, from a 72-point grid (`arm` × `k` × `pin` × `maxhold`), and tested untouched on 2019–2026.

| | Trades | Hit | S&P per trade | Same-length random hold | 30-day ATM call: mean / median / hit | Call vs random entries |
|---|---|---|---|---|---|---|
| In 2012–18 | 19 | 68% | +1.0% | +0.6% | +6% / +15% / 58% | 87th percentile |
| **Out 2019–26** | **15** | **73%** | **+2.9%** | +1.0% | **+17% / +0.5% / 53%** | 84th percentile |

**How robust it is:**

* Out of sample, 81% of the 72 grid configurations beat the same-length random hold (67% in sample).
* The `k = 0.25` (deep VIX crush) rows are a plateau out of sample: excess +0.2% to +1.9% in all 18 configurations.
* **In sample the same plateau averaged ~0**, so the edge is stronger in the 2019–2026 V-shaped-recovery regime and is not proven stable.
* Call returns are lumpy: 2020-03 +96%, 2025-04 +256%, but 2025-03-18 −104% (armed too early, before the April crash).
* Neither period clears the 95th percentile against random-entry calls.
* About 2.4 signals a year.
* IV is set to VIX; real ATM IV usually sits a bit below VIX, so the call numbers are conservative.

**Now (Oct 1):** GEX percentile 0.44 (15-day minimum 0.22). **Not armed.**

## 4g. Has the options market changed too much for old data? (`era_check.py`)

**What the sources say:**

* Commissions went to zero in Oct 2019.
* Retail's share of Cboe volume jumped from 35% to 47% in March 2020, and retail is ~25% of all US option contracts.
* SPX gained expiries every weekday in 2022. 0DTE went from ~20% of SPX volume in 2020 to 59% in 2025, and ~63% in early 2026; retail is 50–60% of it.
* Research on whether 0DTE positioning dampens or amplifies index vol is mixed.
* The data itself has a hole: **SqueezeMetrics-style GEX is built from end-of-day open interest, so it cannot see 0DTE positions.**

| Era | corr(GEX pct, next-10d RV) | P(elevator): lowest → highest GEX quintile |
|---|---|---|
| 2012 – 2019Q3 | −0.48 | 20% → 1% |
| 2019Q4 – 2022-05 (zero commission, retail boom) | −0.41 | 32% → 3% |
| 2022-05 → now (0DTE) | −0.48 | 25% → 2% |

**The core gamma → realized vol / up-leg relationship did not break.** It is equally strong in every era, even though GEX is blind to 0DTE. Multi-day open-interest gamma still drives multi-day legs.

The strategy is different. The edge from the VIX crush (`k = 0.25`) grows over time: mean excess −0.01% → +0.53% → +1.49% per trade. But the 0DTE era has only 5 trades (4 wins, calls +64% median), far too few to fit on. So old data is kept for the *relationship* and weighted toward recent eras for *expectations*. Parameters are never refit on the 0DTE era alone.

## 4h. Forecasting the gamma path from today (`forecast.py`)

**Setup:** today (Oct 1) is GEX pct 0.44, VIX 16.4, VIX/VIX3M 0.88, DIX pct 0.81, SPX at its 50-day average, 9 days after opex. I took the 80 closest historical days (de-clustered, 2012–2026) and tracked the next 30 trading days.

| | Analogs of today | Random day |
|---|---|---|
| GEX reaches bottom quintile within 30d | 66% (median **5 days**, IQR 2–13) | 72% |
| SPX on the way there | median **−1.1%**, 83% negative | |
| An up-leg starts within 30d | 60% (start day median **11**, IQR 4–18) | 64% |
| ...if GEX hit the bottom quintile first | 68% | |
| SPX 30d | median +3.0%, 71% up | +2.1%, 70% up |

**Opex cycle:** GEX percentile builds into monthly opex (0.52 → 0.63) and drops about 17 points on expiry day (0.46). The 0DTE era looks the same.

**Confirmations, measured on their own:**

* **DIX × GEX.** P(up-leg in the next 10 days), normally 10%:
  - mid GEX with DIX > 80th pct (**today's cell**): **15%** (n = 444)
  - mid GEX with DIX < 50th pct: 6%
  - low GEX: 22–26% for any DIX
* **Midterm-year Q4.** +5.0% mean vs +2.9% in other years since 1970, but the same 79% hit rate (n = 14; 2018 was −15%). Not a real edge.

**Reading:** today's state does **not** raise the odds of a leg beyond normal. The way a leg usually starts from here is a small dip (≈1%) that knocks gamma into the bottom quintile within about 1–2 weeks. Typical timing is Oct 7–27, centred on Oct 16 opex. The leg follows after that. High DIX (dark-pool buying) is the one live tilt in favour.

## 4i. Entry ladder: the earliest point where odds tilt (`ladder.py`)

Each rung is a condition, from today's state to the full signal. Events are the first day it turns on, at least 10 days apart. Outcomes are over the next 20 trading days.

| Rung | P(up-leg starts ≤20d), 2012–26 / 2019Q4–26 | Lead to leg (median days) | 60-DTE ATM call | 60-DTE ATM/105% call spread, 2012–26 / 2019Q4–26 |
|---|---|---|---|---|
| any day | 50% / 58% | 7 | −1% | +9.5% / +12.4% |
| R0 mid GEX + DIX > 0.8 (**today**) | 59% / 70% | 5–6 | −3% | +10% / +19% |
| R1 GEX ≤ 0.30 | 61% / 72% | 6 | −3% | +12% / +13% |
| **R2 GEX ≤ 0.30 + DIX > 0.5** | **65% / 79%** | 5 | −1% | **+15% / +16%** |
| R3 GEX ≤ 0.20 | 65% / 73% | 5 | −6% | +13% / +10% |
| R4 GEX ≤ 0.20 + S&P ≥ 2% off its 10-day high | 70% / 74% | 4–5 | −4% | +17% / +11% |
| R5 R4 + DIX > 0.5 | 74% / 83% | 3–5 | −3% | +18% / +11% |
| R7 low GEX + VIX ≥ 25% off its 10-day max | 46% / 52% | 6–8 | **+5% / +10%** | +17% / +21% |

**Reading:**

* P(leg) climbs steadily along the ladder, but **naked calls bought early do not pay more**. Low gamma comes with high VIX, so you buy expensive vol, and the leg arrives with a vol crush.
* The call spread neutralises most of that vega, and R2 onward beats "any day".
* Naked calls only win once the vol crush has happened (R7), which is later.
* **The earliest rung with a clear tilt is R2 (GEX ≤ 30th pct with DIX > 50th):** about 5 days of lead, with a spread rather than a naked call.
* Caveats:
  - Option prices use flat vol at VIX with no skew, so compare rungs with "any day", not with zero.
  - Most rung CIs overlap the base.
  - Events overlap across rungs.

## 4j. Multiverse test: is the gamma result real or a lucky choice? (`multiverse.py`)

**Setup:** 216 specifications, every combination of:

* GEX threshold: 0.1 / 0.2 / 0.3 / 0.4
* DIX filter: none / > 0.5 / > 0.8
* horizon: 10 / 20 / 30 days
* era: 2012+ / 2019Q4+ / 2022-05+
* outcome: excess S&P return / P(up-leg)

**Null:** circularly shift the GEX/DIX series in time (this keeps their persistence and destroys their timing), rerun all 216, and repeat 300×.

| Outcome | Specs positive | Specs p < 0.05 (luck ≈ 5%) |
|---|---|---|
| P(up-leg within H) | **99%** | **91%** |
| Excess S&P return | 65% | 6% (≈ luck) |

* Joint p-value < 0.003 (0 of 300 shifted multiverses matched); 105 of 216 specs survive FDR 10%.
* Lower GEX thresholds and a DIX filter strengthen the effect: P(leg) lift is +26 pts at GEX ≤ 0.1, +26 pts with DIX > 0.8, and +13 pts with no DIX filter.
* It holds in every era (+16 / +19 / +23 pts).

**Conclusion:** low gamma robustly predicts *that a big up-leg starts* (movement). It does **not** predict a higher *average* return, because the downside widens too. This is why structure (spreads) and confirmation (DIX, the VIX crush) matter for direction.

## 4k. Tesla: does the S&P gamma signal carry over? (`single_name.py TSLA`)

**Data:** single-stock gamma history is a premium Alpha Vantage endpoint (not on the connected key) and not free elsewhere. So the predictors stay market-wide (S&P GEX/DIX, VIX), and the target is Tesla's own top-decile 10-day up-leg.

* **No.** Multiverse with TSLA as the target: joint p = 0.74. 0% of 216 specs are significant; P(leg) effect +1 pt on average; excess return is negative in 86% of specs. P(TSLA up-leg) is flat at 9–13% across S&P GEX quintiles in every era.
* **What S&P gamma does do to Tesla:**
  - **Volatility:** next-10d realized vol is 65% at the lowest S&P GEX vs 49% at the highest.
  - **Coupling:** correlation with the S&P is 0.62 at low GEX vs 0.35 at high GEX. Beta falls (1.49 vs 1.98) as correlation rises, and idiosyncratic vol is 57% vs 47%.
  - Low S&P gamma turns Tesla into a market-beta instrument; high gamma leaves it trading on its own story.
* **Ladder:** no rung beats "any day" on P(leg) (38% / 44%).
  - Buying calls into a Tesla-specific dip during low S&P gamma (R4s/R5s) was the worst entry: −25% to −27% vs +12% / +22% any day.
  - Only the vol-crush rung (R7) helps option P&L (spread +33% vs +13% since 2019Q4, n = 27).
  - The "today-like" R0 row looks strong (n = 46), but the multiverse says S&P-gamma conditioning has no robust effect on TSLA, so treat it as noise.
* **Snapshot (Oct 8, TSLA 375):**
  - Earnings **Oct 21**; implied earnings move ±6.0% (ATM IV 39% → 49% across it).
  - Classic gamma flip ≈ 362; largest gamma strikes 372.5–400; the call OI wall is **400** (79k); put OI sits at 350/370; max pain 370 for every expiry through Nov.
  - TSLA is +13.5% over 40 days but 23.5% below its 52-week high (490, Dec 2025).
  - The auto log channel does not fit (R² 0.56, price below its lower line), so there is no channel to trade.

## 4l. Tesla burst check, event by event (`burst_check.py TSLA 2024-01-01`)

**Definitions.** Burst = +5% in 1 day or +9% over 2 days; 36 up-bursts and 35 down-bursts since 2024. A signal "catches" a burst if it first fired 1–10 days before.

**The windows asked about:**

* **Caught:** 2025-04-23 (R6/R7/R4s/R5s, the vol crush after the April crash), 2025-05-27, 2025-11-24, and late Jul 2024.
* **Missed:** 2024-07-01/02 (+15.6%), 2025-09-11/12 (+13%), 2025-10-06 and 2025-10-13. All of them came in calm, high-gamma markets: S&P GEX at the 69th–89th pct, VIX 12–17. These were Tesla-specific catalysts, which market-wide data cannot see.
* **Weak:** 2025-05-12 (only R0).

**Precision vs the base rate** (any day: 47% up / 45% down within 10 days):

| Signal | Fired | Up-burst followed | Down-burst followed |
|---|---|---|---|
| R7 (vol crush) | 11 | **82%** (p = 0.02) | 45% |
| R5s | 12 | 75% (p = 0.05) | 58% |
| R2 | 22 | 64% (p = 0.09) | 50% |
| others | | 42–61% | 36–55% |

Most signals precede down-bursts about as often as up-bursts: they flag Tesla *volatility*, not direction. R7 is the only directional one, and with 10 signals tested its p-value does not survive correction (≈0.2 Bonferroni).

## 4m. Tesla today and three trader observations (`stock_now.py TSLA`, data to Oct 8 2026)

**State:** TSLA 375; S&P GEX pct 0.62, DIX pct 0.91, VIX 15.4. **No ladder rung has fired in 10 days.** This is a calm, mid-to-high-gamma market, the regime where Tesla's bursts came from its own catalysts.

| Observation | Test | Result |
|---|---|---|
| Bursts come going **into** opex week | up-bursts by week vs monthly opex, 2012+ / 2019Q4+ | **Not supported.** Opex week lift 1.03 / 1.04; the week before is 0.87 / 0.83 (fewer); the week after is 1.08 / 1.19 (not significant) |
| Tesla makes its year in 1–2 bursts, often late | top-2 2-day bursts vs the full-year return | **Partly.** The top-2 bursts made ≥ half the gain in 8 of 12 up years, but that is the fat-tail norm for a 50%-vol stock (they sum to +18 to +53% every year, up or down). A Q4 burst is in the top 2 in 5 of 14 years (25% by chance) |
| Catches up with SPY by year end | Q4 relative return when TSLA lagged SPY by >10 pts at Sep 30 | **Supported, small n.** 5 of 5 lagging years beat SPY in Q4 (2012, 16, 18, 19, 24), mean +28.7 pts vs −10.3 in other years (base rate 53%; p ≈ 0.04). 2026 gap: **−30.8 pts** YTD |
| Grind-up like Jul–Aug 2025 → burst | 40 nearest analogs on 40d return, vol, vol ratio, drawdown, trend R², up-day share | The setup really is similar (ret40 +13.5% vs +11.3%; vol ratio 0.60 vs 0.51; drawdown −1.5% vs −1.1%). **But up-burst odds were not higher:** 38% vs 41% base. Down-bursts were rarer: 28% vs 41% |

**Earnings: the dominant burst source.**

* Within ±1 day of 39 reports: up-burst 31%, down-burst 51%, vs 13% for any 3-day window.
* The 11 detected October (Q3) reactions: five ≥ +5% (2014, 2018, 2019, 2021, 2024) and two ≤ −5%.
* Next report **Oct 21**; options price ±6.0% for the event.

**Oct 16 monthly expiry** (36% of ≤45d call OI):

* call OI: 400 (31k), 380, 420
* put OI: 380, 360, 340
* largest gamma strikes: 400, 385
* max pain: 370

The pin releases five days before earnings.

## 4n. Anatomy of Tesla's Q4 catch-ups (`q4_forensics.py TSLA`)

**Catch-up years** (TSLA lagging SPY by > 10 pts at Sep 30): 2012, 2016, 2018, 2019, 2024. For each Q4 up-burst and the year's best 10-day leg relative to SPY, the analysis records:

* calendar position: day of month, opex bucket, Q3 report (published dates), US election
* the burst itself: gap share, follow-through
* Tesla's own state
* the S&P state: GEX, DIX, VIX, term structure

Control group: Q4 bursts in other years. Full table: `out/q4_forensics_TSLA.csv`.

| Year | Main catch-up leg (best 10d vs SPY) | What drove it | S&P GEX pct at the bursts |
|---|---|---|---|
| 2012 | Oct 26 → early Nov, +16.9 | Nov 5 +8.6% on the eve of the Q3 report **and** the election (Nov 6) | 15–20 |
| 2016 | Dec 12 → Dec 23, +13.2 | Q3 report fizzled (−7.4 rel over 10d); a December grind into quad witching instead, no burst | 97 |
| 2018 | Oct 19 (opex day) → Nov 2, +30.3 | Oct 23 +12% two days before the Q3 report, then +8.7% on it | 1–5 (Oct 2018 selloff) |
| 2019 | Oct 11 → Oct 25, +26.3 | Q3 report Oct 24 +16.3%, 97% of it in the gap; Dec 16 burst in Dec opex week | 44–54; Dec 97 |
| 2024 | Dec 3 → Dec 17, +31.1 | Q3 report Oct 24 +19.8%, election Nov 6 +13.8% (+13.5% the next 5d), then a December leg into quad witching | 28–37; Dec 96–99 |

**Common factors:**

1. **The Q3 report is the anchor** in 4 of 5 years. 10-day return vs SPY after the Q3 report:
   - lagging years: +6.3, +13.1, +22.5, +27.8 (2016: −7.4); mean +12.5 pts
   - other years: mean −1.4 (range −35 to +31)
   - This is the earnings-crowding result (§4e): under-owned + surprise → multi-day drift.
2. **December continuation into quad witching** in 3 of 5 years (2016, 2019, 2024). It came at *high* S&P gamma (96–99th pct): a grind, not a burst.
3. **Opex:** the "week after October opex" is over-represented (39% vs 26%) only because that is where the Q3 report falls. With the report removed, there is no opex effect.
4. **S&P gamma is not the common factor.** October bursts came at low-to-mid GEX (1–54th pct); December legs at high GEX.
5. **Tesla was 19–35% below its 52-week high** before every October catch-up burst.
6. **Elections:** bursts at the 2012 and 2024 presidential elections; nothing in 2016 or 2018. n = 2.
7. Catch-up bursts **kept going**: median next-5d +5.1% vs +1.1% for other Q4 bursts. Earnings bursts were made **in the opening gap** (68–97%), so positioning has to be in place before.

**2026 vs the template:**

| Factor | Now | Template |
|---|---|---|
| Gap vs SPY | −30.8 pts | lagging > 10 pts |
| Below 52-week high | −23% | 19–35% below |
| Q3 report | Oct 21 (after close) | week after October opex |
| 40-day return | +14% | only 2019 (+17%) was this high going in; the others were flat or negative, so part of the move may already be priced |
| US midterm | Nov 3 | election bursts in 2012 and 2024 (n = 2) |
| Dec quad witching | Dec 18 | December continuation in 3 of 5 years |

## 4o. Tesla options regime: pre-2020 vs 2020+ (`tsla_eras.py`)

Tesla options changed character around 2020: retail inflows, the Aug 2020 split, heavy short-dated OTM call buying, then the 0DTE era. Every options-related Tesla test is re-run by era.

| Test | pre-2020 | 2020+ |
|---|---|---|
| Up / down bursts per year | 8.1 / 8.8 | **15.1 / 14.4** (vol 50% → 64%) |
| Up-bursts in opex week / week after (lift) | 1.05 / 0.95 | 1.02 / 1.16 (n.s.) |
| **Up-bursts on Monday** (lift, p) | 1.72, p = 0.007 | **1.95, p < 0.001** (2.02 excl. report days) |
| Up-bursts on Friday (weekly expiry) | 0.15 | **0.44** |
| Down-bursts Monday / Friday | 0.83 / 0.92 | 0.89 / 1.04 |
| Q3 report: mean abs move day 0 | 8.1% | 7.1% |
| Q3 report: day 0 ≥ +5% / ≤ −5% | 38% / 25% | 17% / 33% |
| Q3 report: drift after, signed by day 0 | +82 bp | **+706 bp** (n = 6) |
| All reports 2020+ (n = 24): continue in the day-0 direction | | 62.5%, mean +350 bp (t = 1.78, p ≈ 0.15) |
| Grind-up analogs: P(up-burst 10d) vs base | 38% vs 41% (full pool) | **32% vs 52%** (2020+ pool); down 24% vs 49% |
| Q4 catch-up years (lag > 10 at Sep 30) | 2012, 2016, 2018, 2019 (4 of 4 beat SPY) | **2024 only** (+41.3); mild lags 2021 (+20.8) and 2025 (−1.2) |

**Reading:**

* **The Monday effect is the most robust new finding.** It is up-only (Monday down-bursts are below average) and mostly made intraday (median gap share 0.37), so it is not simply weekend-news volatility. Friday up-bursts are suppressed. That fits weekly-expiry mechanics: Friday's expiring short-dated calls pin, and fresh weeklies bought on Monday put dealers short gamma. It replicates in both eras and survives correction for 20 tests.
* The Thursday down-burst excess (1.59) is mostly earnings reactions (8 of 31; 1.35 and p = 0.07 without them).
* Post-2020 reports reprice more slowly (continuation after day 0), consistent with options-driven hedging after the event; n is small.
* The grind-up state is a *low-burst* state in the 2020+ era: fewer bursts both ways.
* Catch-up evidence in the new regime is only 1–2 years.

## 4p. After the leg: topping, consolidation and the gamma "reset" (`reset.py`)

Definitions: leg = top-decile 10-day S&P return (≥ +3.5%); reset = GEX pct ≤ 0.30; consolidation = 20-day range in the bottom 30%. Each pair of numbers below is 2012+ / 2019Q4+.

| Question | Result |
|---|---|
| **Do legs need a reset first?** | **Yes.** 88% / 90% of legs had GEX ≤ 0.30 within the prior 20 days, vs 73% / 71% of random days (p = 0.001 / 0.002) |
| **Gamma ran up with no price** (GEX pct +0.5 from its 7-day low while the S&P 7d is −1% to +2.5%) | P(leg within 20d) **27% vs 44%** (p < 0.001) / 40% vs 51% (p = 0.07). Consolidation 36% vs 30% / 27% vs 19% |
| **Leg ends pinned** (GEX ≥ 0.90 at the leg end) | Next 20d: consolidation **55% vs 30%** / 36% vs 19%; new leg 35% / 36% vs 44% / 51%; shallow dips (median −0.2% / −0.1%); still drifts up (+1.6% / +3.2%). **A pause, not a top** |
| **Leg ends unpinned** (GEX < 0.90) | New leg 46% / 62%; consolidation 19% / 14%; deeper dips (−1.6% / −1.8%) |
| **Gamma built over 10d** (10d mean GEX ≥ 0.70, S&P 10d flat) | Reset within 40d in 80%, median **11 days** (IQR 6–19). When a leg followed, it came **after** a reset 72% / 74% of the time (median 18 / 15 days) |

**Now (Oct 8):**

* A reset happened Sep 28 (GEX 0.30, DIX 0.82; R2 was on that day).
* The S&P then rose only +1.8% to Oct 6 while GEX ran to 0.91. The "gamma ran with no price" signal fired on Oct 2, 5 and 6.
* Today GEX is 0.62 and fading, DIX is 0.91, VIX 15.4 in contango.
* Read: lower odds of a real leg through late October, chop or consolidation more likely. The next reset typically comes ~5–19 days after the build, roughly Oct 13–30, around Oct 16 opex and the Oct 21 VIX settlement. A leg typically follows it.
* High DIX is the one counterweight: in the matching state *with* DIX > 0.8, P(leg) was 47% (n = 17) vs 33% without the filter.

## 4q. Scorecard: calls since Oct 1 vs what happened (`dashboard_data.py`, dashboard "S&P gamma cycle")

Through the Oct 8 close: 6 calls held, 3 held partly, 1 missed, 3 are still open.

* **Held:** S&P had no up-leg from the Oct 1 state; DIX tilt up (S&P +1.3%); MU broke its rising channel line on Oct 2; MU never accepted above 1,100; MSFT stayed in or just above the 510–525 pin zone.
* **Partly:** gamma built into expiry and is fading ahead of Oct 16; MU chopped, a little lower than called (1,036–1,088); MU lost 1,070 but has not reached the 1,011 flip.
* **Missed:** the usual path, "a ~1% dip pushes gamma down within ~5 days". The S&P rose 2% instead, and gamma ran to its 91st percentile. That miss is what triggered the "gamma ran without price" signal in §4p.
* **Not yet:** R2 (56% by Oct 16).

The dashboard (`out/dashboard/index.html` + CSVs) charts the S&P cycle, the gamma and DIX percentiles with the reset and pinned zones, the next-20-day odds by state, the scorecard, and the MU and MSFT tracks.

## 5. MU microstructure snapshot (`options_flow.py`, `flow_intraday.py`)

![gex](out/fig_gex.png)

There is no free data on who is long or short each option, so dealer positioning is shown under two sign conventions.

**Classic convention (dealers long calls, short puts):**

| Item | Value |
|---|---|
| Net GEX | **+$1.31B per 1% move**, about 4.9% of MU's $26.8B average daily dollar volume, enough to dampen intraday moves |
| Gamma flip | **≈ 1,011** |
| Vanna | +$385M of dealer delta per +1 IV point |
| Charm | +$1.1B/day. Under this convention, time decay mechanically adds dealer buying into expiries while above the flip |

**If customers are net buyers of everything (likely in a parabolic name):**
net GEX is **−$3.25B per 1%**, so negative gamma everywhere. The 1,100 strike then
becomes the biggest *accelerator* rather than a pin. The truth sits between the two
conventions. Signed trade data (see §7) is what settles it.

| Level | Source |
|---|---|
| 1,485 | upper channel line |
| 1,300 | largest call OI (≤ 45 days), the call wall |
| 1,261 | mid channel line |
| 1,200 / 1,150 | next big gamma strikes |
| **1,100** | largest gamma strike, right at spot; today's 0DTE expiry |
| 1,077 | 60-session value-area high (price just accepted above it) |
| **1,070** | lower channel line (rises about 8 points/day) |
| 1,045–1,055 | max pain, 2/5/7 Oct expiries |
| **1,011** | gamma flip (classic) |
| 1,000 | large put + call open interest |
| 954 | 50-day SMA |
| 931 | 60-session point of control (POC) |

* Implied 1-standard-deviation move (straddle): ±3.4% today, ±7.9% by 9 Oct, ±15.4% by 30 Oct. ATM IV is about 53–55%, after the 30 Sep earnings.
* Put/call open-interest ratio for expiries ≤ 45 days: 1.12.

![flow](out/fig_flow.png)

* **Order flow** (bulk-volume classification on 5-minute bars, a proxy, not real tape):
  - Cumulative volume delta is **+45.6M shares** over 60 sessions, climbing steadily from Aug 6. That is accumulation while price chopped in a 750–1,100 range.
  - The daily delta-vs-return correlation is 0.91. That is largely by construction (the classifier assigns direction from the price change), so read the level and its divergences, not the correlation.
* **Block detection:** only 3 five-minute bars cleared a 4-sigma volume threshold. Real block, sweep and iceberg detection needs tick-level prints.

### Breakout / breakdown playbook (rules derived from the above, not a forecast)

* **Up:** hold above 1,100 into the close.
  - Watch for rising IV *and* rising price. That combination means dealers are short calls, which is the negative-gamma squeeze case.
  - CVD should make new highs alongside price.
  - Targets: 1,150 → 1,200 → mid line 1,261 → call wall 1,300.
  - **Speed is required:** a channel this steep needs about +0.8%/day just to stay inside.
* **Down:** close below the lower line (1,070, rising), then below 1,011 (gamma flip).
  - Below the flip, dealer hedging amplifies moves.
  - That is the "counter-trend line" break, which the backtest says happens 62% of the time once tested, and a fast approach raises the odds.
  - Next magnets: 1,000 (put open interest), 954 (50-day SMA), 931 (POC).
* **Most likely by base rates:** time decay. Price chops between 1,045 and 1,150, pinned around 1,100 by near-dated gamma. The rising lower line runs into it within 3–9 sessions, so the *channel* ends even if the *stock* doesn't fall.

## 6. Limitations (read before trading this)

* Yahoo has no signed options trades, no historical open interest and no Level-2 data, so the GEX/vanna/charm levels are a **single-day snapshot** and the dealer sign is assumed.
* IVs were re-solved from last-trade prices and smoothed per expiry.
* Bulk-volume classification and close-location-value delta are classification proxies, not aggressor-side prints.
* The universe has survivorship bias (all are current winners), so trend persistence is probably overstated.
* Events from the 126- and 252-bar windows overlap. The confidence intervals are clustered by calendar month to absorb some of this.

## 7. Next data to get a real microstructure answer

1. **Signed options trades** (OPRA trade-level: Cboe LiveVol, ORATS, Unusual Whales/Tradier) to fix the dealer sign, plus daily open-interest history so §5 can be backtested the way §3 was.
2. **Trade and quote data** (Polygon/Databento) for real aggressor delta, block/sweep detection, and absorption at the lines. Then rerun §4 with tape features.
3. Rerun `calendar_tests` on intraday data (last-hour moves into opex) to measure pinning and vanna/charm at the resolution where they actually operate.

## Reproduce

```bash
pip install -r requirements.txt
python fetch.py MU            # MU daily/5m/1m + full option chain
python fetch.py --universe    # daily bars for the 40-name universe
python fetch.py --index       # S&P/VIX history + SqueezeMetrics GEX/DIX
python release.py             # what frees the index (section 4d)
python earnings.py            # earnings repricing vs positioning proxies (section 4e)
python strategy.py            # gamma-release rule, walk-forward (section 4f); last line = live state
python forecast.py            # gamma path analogs from today + confirmations (section 4h)
python ladder.py              # entry ladder; last lines = which rungs are ON today (section 4i)
python multiverse.py          # 216-spec multiverse vs time-shifted nulls (section 4j)
python single_name.py TSLA    # S&P gamma studies with a stock as the target (section 4k)
python burst_check.py TSLA 2024-01-01   # event-by-event bursts vs signals, false positives (4l)
python stock_now.py TSLA      # today's state + opex-timing, catch-up, grind-analog, earnings tests (4m)
python q4_forensics.py TSLA   # anatomy of Q4 catch-up legs vs controls (4n)
python tsla_eras.py           # Tesla options-regime split pre-2020 vs 2020+ (4o)
python reset.py               # topping/consolidation after legs and the gamma reset (4p)
python channels.py            # current MU channel
python backtest.py            # ~3-4 min on 4 cores -> out/backtest.json, out/events.csv
python report.py              # figures + out/report_numbers.json
```
