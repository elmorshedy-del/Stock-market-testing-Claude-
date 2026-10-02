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
python channels.py            # current MU channel
python backtest.py            # ~3-4 min on 4 cores -> out/backtest.json, out/events.csv
python report.py              # figures + out/report_numbers.json
```
