# Does a 5-minute opening-range breakout make money in SPY, and mainly when dealers are short gamma?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02 (intraday, after the close data for Oct 30)
**Started:** 2026-11-02   **Pre-registered at commit:** (the commit that first adds this README)
**Type:** replication (practitioner ORB) + new question (gamma conditioning) + exploratory features and ML with a held-out test
**Verdict:** (filled in at the end)

**Owner's ask (2026-11-02):** "Let's run it, make it simple first, then add any related variables that could sharpen it or tilt the odds, and do ML. Start small so you don't use a lot of quota. The data has to be sorted, audited and diagnosed. A failed test doesn't mean the strategy is wrong; it could be the parameters, the regime or the conditions, so analyze what worked and why, and improvise."

## Question
* Does the opening-range breakout (ORB) of Zarattini & Aziz (SSRN 4416622, 2023: QQQ 2016-23, claimed 33% annual alpha) make money on SPY in 2024-26 after costs?
* Is the edge concentrated where our gamma work says dealers amplify moves, with SPY below its pre-open gamma flip or S&P GEX low?
* Which conditions (gap, opening-range width, opening volume, VIX, 0DTE share, calendar) tilt the odds, and can a small ML model, tested on held-out months, beat the simple rule?

## Prior work
* REPORT §4z at 26a8bce: below the flip, SPY up-bursts are 2.8× as likely (p < 0.001); down-bursts are not raised (0.7×). This is the basis for H2's direction. A long-side tilt below the flip is possible, so long and short results are reported separately.
* flip-wicks at 26a8bce: `out/preopen_levels.csv` gives the daily pre-open SPY flip (including and excluding same-day expiries), GEX and 0DTE share, from prior-close open interest. That makes it known before the open. Used as is, not edited.
* intraday-hours B1 and forced-flow A2 at 26a8bce: no intraday momentum into the US close in 2023-26. That is a prior against the ORB working overall.
* open-fade at 26a8bce: "sell at the open" is not supported; the routine first-hour dip is not a signal.
* hft-papers at fd8ede0 (C1): the source of this idea.

## Hypotheses and pass/fail criteria (frozen before any strategy result)

### Data audit (must pass before any strategy number is computed)
* **D1 completeness:** a regular session has 390 one-minute bars, 09:30-15:59 ET. Days missing more than 5 bars in 09:30-10:00, or more than 20 bars in total, are dropped and counted.
* **D2 accuracy:** daily open, high, low and close rebuilt from the bars vs Yahoo SPY daily (unadjusted). A day is flagged if any of the four differs by more than 0.05%.
* **D3 timestamps:** UTC to ET with DST. The first bar must be 09:30.
* **D4 calendar:** half days (13:00 close) are excluded.
* **Pass:** at least 95% of sessions clean on D1 and D2. If the audit fails, switch the source (ARCX.PILLAR, SPY's primary listing) and log it as an amendment before any strategy run.

### Strategies (frozen)
* **S0, the paper's ORB (primary):**
  * The first 5-minute candle is the 09:30-09:34 bars. Close > open: go long at the 09:35 bar's open. Close < open: go short. Equal: no trade.
  * Stop = the first candle's low for a long, its high for a short. Target = 10R, where R = |entry − stop|. Otherwise exit at the 15:59 bar's close.
  * Stops are checked on each bar's high and low. If a bar opens through the stop, the fill is that bar's open. If the stop and the target are both touched in one bar, the stop is assumed.
* **S1, classic breakout (secondary):**
  * The opening range is the high and low of 09:30-09:34.
  * Enter long on the first trade above the range high + $0.01 (fill at the larger of that level and the bar's open), or short on the first trade below the range low − $0.01. Only the first break counts, and there are no entries after 15:00.
  * Stop at the opposite side of the range; exit at the close.
* **Costs:** $0.01 a share a side, plus $0.01 extra on stop fills. Results are in basis points of the entry price, and in R.
  * Day P&L is 0 on no-trade days.
  * The paper's sizing (1% risk per trade, leverage capped at 4×) is reported as secondary, for comparability only.

### H1 (replication)
* **Statistic:** S0 mean net P&L per day.
* **Null:** a circular shift of the daily direction signal against the days' price paths. Each day's long and short outcomes are both computed, so a shifted signal picks the other outcome. Shifts k run from 20 to N−20; p = the share of shifts with a mean ≥ the actual.
* **Pass:** mean > 0 and p < 0.05. S1 is reported the same way, but S0 decides H1.

### H2 (gamma regime, this study's main question)
* **Regime:** below the flip = SPY's 09:35 price < `flip_incl`. That flip includes the day's expiring options, which are live during the session.
* **Statistic:** mean S0 P&L on below-flip days minus above-flip days, over sessions covered by `preopen_levels.csv` (through 2026-10-12).
* **Null:** a circular shift of the regime series, which keeps how persistent regimes are.
* **Prediction:** the difference is positive. **Pass:** p < 0.05.
* **Secondary regime definitions,** with Holm correction across the three:
  * `flip_excl`;
  * SqueezeMetrics S&P GEX at the prior close in the bottom tercile of its trailing 252 days, vs the top tercile.
* **Falsified if** above-flip days do as well or better.
* Long and short trades are also reported separately, because of the 2.8× long-side prior.

### H3 (exploratory: parameters, the multiverse)
* **Grid:** opening range ∈ {1, 5, 15, 30} minutes × exit ∈ {close, 10R, 2R} × {S0, S1} = 24 variants.
* **Joint p:** the max-t across the grid under the same circular shift.
* Report which variants work and in which regimes. Nothing here is a confirmatory claim.

### Conditioning variables (exploratory; all known by 09:35)
* the overnight gap, its size and direction, and whether the first candle agrees with it;
* opening-range width vs 14-day ATR (Crabel: narrow ranges break better);
* first-5-minute volume vs its 14-day average ("in play");
* VIX at the prior close and its overnight change (Breaking-VIX-at-open);
* the 0DTE share; distance to the flip, scaled;
* day of week; OPEX week; scheduled CPI, FOMC and NFP days;
* the prior day's return; DIX (prior close).

### ML (exploratory, with an untouched test)
* **Target:** an S0 win (net P&L > 0).
* **Features:** the list above.
* **Split by time:**
  * train 2024-01-02 to 2025-06-30;
  * validate 2025-07-01 to 2025-12-31, where the probability threshold is chosen;
  * test 2026-01-02 to 2026-10-30, touched once.
* **Models:** L2 logistic regression; shallow gradient boosting (depth ≤ 3, ≤ 200 trees).
* **Rule:** take S0 only when the predicted P(win) is above the threshold.
* **Compare on test** with unfiltered S0 and with the best simple regime filter from H2.
* **ML "pass":** test-period Sharpe above the unfiltered S0, with a 10-day block-bootstrap 90% CI that excludes 0.
* About 200 test days is small. The result is a lean, not a rule.

### Scope and cost (start small)
* **Stage 1 (this registration):** SPY only, Databento EQUS.MINI `ohlcv-1m`, 2024-01-01 to 2026-10-31. The quote is **$0.227** (20.3 MB). Gamma state from flip-wicks; GEX and DIX from SqueezeMetrics (free); VIX from Yahoo (free).
* **Stage 2 (pre-planned; logged as an amendment before it runs):**
  * extend SPY to 2020-2023 (ARCX.PILLAR, about $0.55) as an out-of-sample check of any Stage-1 regime finding;
  * QQQ, and TSLA on its own flip.

### Amendment A1 (logged after the Stage-1 SPY results, before any new data was pulled)
* **Stage-1 outcome:**
  * H1 fails: S0 −1.40 bp/day, shift p 0.79.
  * H2 fails, and points the wrong way: below the flip −2.20 vs above −0.95, p 0.69.
  * The 24-variant grid is flat (best t 0.5; joint p 0.97 to follow, 0.55 to fade).
  * The opening move carries no information: corr(first 5 minutes, rest of day) = 0.008.
* **Three post-hoc patterns from the Stage-1 exploration,** frozen now for confirmation:
  * **E1 regime-aligned ORB:** take S0 (5-min, 10R) longs only when the 09:35 price < `flip_incl`, and shorts only when it is ≥ `flip_incl`. SPY 2024-26: +0.46 bp/day on 293 trades (shift p 0.029). Prediction: mean > 0.
  * **E2 Monday:** S0 on Mondays minus other days. SPY 2024-26: +7.35 bp (shift p 0.016). Prediction: > 0.
  * **E3 high VIX hurts:** S0 on days with prior-close VIX > 17.86 (the Stage-1 top-tercile cutoff, now fixed) minus other days. SPY 2024-26: about −4.9 bp. Prediction: < 0.
* **Confirmation sets:**
  * **(i) SPY 2020-01-02 to 2023-12-29** (ARCX.PILLAR `ohlcv-1m`, quoted about $0.45-0.95; same audit D1-D4; flip from `preopen_levels.csv`). This is the **primary confirmation**: an independent period.
  * **(ii) QQQ 2024-26** (EQUS.MINI, $0.233): H1 on the paper's own instrument. E1 uses SPY's flip, a cross-asset proxy. Not independent of SPY.
  * **(iii) TSLA 2024-26** (EQUS.MINI, $0.260): H1, E2 and E3. E1 can't be tested, because there is no daily TSLA flip series in hand.
* **Pass for each E:** one-sided p < 0.05 under the circular-shift null in set (i). Sets (ii) and (iii) are supporting evidence only.
* The ML step stays as registered, on SPY 2024-26.

### Amendment A2 (logged after the H1 runs on all sets, before E1-E3, the TSLA exploration or any ML)
* **Fetch overrun:** the SPY ARCX pull ran from 2020 to 2026-10-31 (the fetch end date was hard-coded), so it cost about $0.96, not the quoted $0.45. Total Databento spend for this study is about $1.68. The extra 2024-26 ARCX bars serve as a cross-venue check of Stage 1.
* **The D2 flags are definitional, not bad bars:**
  * Yahoo's high or low is the more extreme one on 91-100% of flagged days. That points to consolidated-tape outlier prints.
  * For TSLA, the flags are mostly the open and the close (66 and 56 days). Yahoo uses the opening and closing auction prices; our first and last 1-minute bars use the first and last trades.
  * The audit's 95% bar fails for SPY 2020-23 (89% clean) and TSLA (78%) only on this tolerance. The bars themselves are complete.
  * So every set is reported **twice**: clean days (as registered) and all complete days (`_d2`). Neither is chosen after the fact.
  * For TSLA the dropped days (22%) are not random. They are days with large auction moves.
* **TSLA exploration** (H1 S0 is positive but not significant):
  * the same 24-variant grid with a joint max-t null;
  * the same conditioning variables, using the S&P GEX percentile and SPY's flip state as cross-asset regimes;
  * the registered ML pipeline re-run on TSLA with the same time split (train 2024-01 to 2025-06, validate 2025-07 to 2025-12, test 2026).
  * All of it exploratory, and labelled as such.

### Amendment A3 (logged after the results above, before any new data or screen was computed). Owner: "test more, and see what other stocks can be good candidates and test them too."
* **C1, TSLA out of sample:** 2020-01-02 to 2023-12-29, XNAS.ITCH `ohlcv-1m` (Nasdaq is TSLA's primary venue).
  * Frozen rule: **S1_5_close** (the first break of the 09:30-09:34 range, stop at the other side, exit at the close; same costs).
  * **Pass:** mean > 0 and shift p < 0.05 on clean days. All complete days are reported too.
  * **Splits to confirm,** with the prediction in brackets:
    * Mon+Fri minus Tue-Thu [> 0];
    * longs minus shorts [> 0];
    * the top tercile of first-5-minute relative volume minus the other two [> 0];
    * auction-gap days (|Yahoo open vs the first bar's open| > 5 bp) minus other days [> 0].
  * One-sided, circular-shift null on the label. A split is supported at p < 0.05.
  * The audit's Yahoo comparison is split-adjusted, because TSLA split 5:1 in 2020 and 3:1 in 2022 (factors come from Yahoo's split events).
* **C2, which other stocks?** A candidate screen fixed now, computed only on **2023** daily data, before the 2024-26 test window.
  * **Universe (fixed list):** NVDA, AMD, AVGO, MU, TSM, SMCI, PLTR, COIN, MSTR, HOOD, RIVN, SOFI, MARA, RIOT, AFRM, UPST, RBLX, SHOP, ARM, MRVL, INTC, CRWD, SNOW, NFLX, UBER, ABNB, BA, AAPL, MSFT, GOOGL, AMZN, META, ORCL, JPM, XOM, UNH, LLY, COST, WMT. (ARM listed in Sep 2023; it is screened on its available days.)
  * **Liquidity filter:** 2023 average daily dollar volume ≥ $1.5bn.
  * **Score:** 2023 mean ATR% (14-day average true range / close). This follows the mechanism: flow-driven, high-idiosyncratic-movement names.
  * **Picks:** the **5 highest-scoring** liquid names (the "in play" group) and the **2 lowest-scoring** liquid names (controls).
* **C2 test:** S1_5_close on each pick, 2024-26 (EQUS.MINI), same audit.
  * **Predictions:**
    * (a) the mean S1 P&L across the 5 high-score names > 0 (shift null applied to every name at once, using the pooled average);
    * (b) high-score names beat the controls (permutation of group labels across the 7 names is too coarse to test, so (b) is reported descriptively).
* **Cost:** all quotes are taken before any pull. Total cap for A3 is about $2.5, and stocks are dropped from the bottom of the ranking if the quote exceeds it.

### Amendment A4 (logged before any exit-rule or option run). Owner: "Can I reduce the frequency or size of losses with an exit rule, or by spotting a loser early? I can use calls instead of stock."
* **Base:** TSLA S1_5_close on every tradable day (`_d2` sets).
* **Exit variants, frozen.** All decisions use bars that are already closed. Stops fill like the base (bar open if gapped, plus 2c); close-based exits fill at that bar's close less 1c.
  * **T15 / T30 / T60, time stop:** if the trade is not in profit at the close of the bar T minutes after entry, exit there.
  * **BE1R:** after +1R in favour, move the stop to entry.
  * **MID:** the initial stop at the opening-range midpoint, not the far side. That halves the risk.
  * **REIN30, failed breakout:** within 30 minutes of entry, a 1-minute close back inside the range exits.
  * **TRAIL1R:** after +1R, trail the stop 1R behind the best price.
  * **REIN30+BE1R:** the two combined.
* **Design / confirm:** variants are compared on TSLA 2024-26, and the best by Sharpe is named there. **It is confirmed on TSLA 2020-23** if its Sharpe beats the base there, its mean bp/day is at least 80% of the base's, and the 10-day block-bootstrap 90% CI of the daily difference in mean P&L is not entirely below 0. All variants are reported for both periods.
* **Early-loss diagnostics** (descriptive): P(trade ends a winner | its P&L at +15, +30 and +60 minutes); how far eventual winners first go against you (MAE in R).
* **Options (stage A5, run only after A4):**
  * Same entries.
  * Buy the nearest-expiry **at-the-money call** (long breaks) or **put** (short breaks): the expiry at least 1 day out, plus a 0DTE variant where one exists.
  * Price = the option's 1-minute bar, with half the quoted spread paid on each side (ThetaData 1-minute quotes). Exit on the underlying's stop or at 15:55.
  * Report the return on premium per trade and per day, and compare with shares on the same days.
  * Start with 2024-26 to check coverage. The data is included in the plan.

## Method
* `fetch.py` pulls the bars into `data/`, which is gitignored.
* `audit.py` writes `out/audit.json`.
* `orb.py` holds the S0/S1 engine plus H1 and H2.
* `explore.py` runs H3 and the features.
* `ml.py` runs the ML step.
* `figure.py` makes the figures.

## Results

**Bottom line:**
* The ORB does not work on SPY. In 2020-23 and 2024-26, on two venues, all 24 variants lose or are flat.
* The gamma regime does not rescue it. Below the flip, SPY breakouts do **worse**.
* ML adds nothing.
* The one place the breakout has life is **TSLA**: the classic 5-minute breakout held to the close made +12 to +18 bp/day in 2024-26, positive in each year. That is a single-asset, single-period exploratory result, not yet confirmed.

Figure: `out/orb_gamma.png`. Data cost about $1.68 (Databento).

### Data audit (D1-D4)
* **Pass:** SPY EQUS.MINI 2024-26 (96.1% clean, 683 sessions), SPY ARCX 2024-26 (96.5%), QQQ (95.9%).
* **Fail on the 5 bp D2 tolerance:** SPY ARCX 2020-23 (89.4%) and TSLA (77.8%). The flags are definitional (amendment A2):
  * Yahoo's high or low is the more extreme one on 91-100% of flagged days;
  * TSLA's open and close come from auctions on Yahoo but from first and last trades in our bars.
* Bars are complete (median 390 a session). Half days are dropped. Every result is shown on clean days and on all complete days (`_d2`).
* **Engine hand-check:** Oct 30 2026 short +55.9 bp and Aug 5 2024 long +101.7 bp, both matching manual fills.

### H1 (replication), S0 = the paper's 5-min rule with a 10R target. **FAILS** on SPY.

| Set | Sessions | S0 bp/day | Shift p | S1 classic breakout bp/day (shift p) | Long 09:35 → close |
|---|---|---|---|---|---|
| SPY 2024-26 (EQUS) | 683 | **−1.40** | 0.79 | −1.18 (0.87) | −0.71 |
| SPY 2024-26 (ARCX) | 686 | −0.66 | 0.44 | −1.40 | −0.15 |
| SPY 2020-23 (ARCX) | 899 | −0.46 | 0.73 | +0.72 (0.32) | +1.68 |
| QQQ 2024-26 | 682 | +1.02 | 0.28 | +1.83 (0.10) | −1.69 |
| **TSLA 2024-26** | 553 | **+6.10** | 0.47 | **+12.39 (0.049)** | +0.92 |
| TSLA, all complete days | 705 | +13.02 | 0.18 | **+18.48 (0.021)** | +0.50 |

* **Why SPY fails:** the opening move carries no information. Corr(first-5-min return, rest of day) = 0.008 (2024 −0.06, 2025 +0.01, 2026 +0.06).
  * 81% of S0 trades are stopped out and 2% reach 10R.
  * Costs are not the issue (about 0.36 bp a trade); it loses before costs too.
* **H3 grid (24 variants):**
  * SPY: best t = 0.5, joint p 0.97 (2024-26) and 0.67 (2020-23). No parameter choice rescues it, and fading it doesn't work either (joint p 0.55).
  * TSLA: best t = 1.9-2.75, joint p 0.28 (clean) and 0.086 (all days). Positive, but it does not survive the 24-variant multiple-testing bar.

### H2 (gamma regime, the main question). **FAILS, in the opposite direction**, in both SPY periods.

| SPY S0 bp/day | Below `flip_incl` | Above | Diff | Shift p (predicted below > above) |
|---|---|---|---|---|
| 2024-26 | −2.20 (345) | −0.95 (324) | −1.25 | 0.69 |
| 2020-23 | −2.2 | +1.7 | −3.88 | 0.91 |

* **Secondary definitions** (`flip_excl`; S&P GEX bottom vs top tercile, 2024-26): diffs −0.47 and −1.41, Holm p 1.0.
* **The one consistent cell:** shorting SPY's opening breakdown **while SPY is below its flip** is the worst trade in both periods: −4.4 bp a trade (2024-26, n 186) and −6.9 (2020-23, n 249). Longs below the flip are slightly positive (+0.4 and +2.7).
* That is the intraday face of REPORT §4z: below the flip, down-moves do not extend, and up-bursts are 2.8× as likely. **Practical lean:** below the flip, don't short the open breakdown in SPY.

### A1 confirmations: E1-E3, frozen on SPY 2024-26, tested on SPY 2020-23. **None confirm.**

| Test | SPY 2024-26 (found) | **SPY 2020-23 (confirm)** | QQQ | TSLA |
|---|---|---|---|---|
| E1 regime-aligned (longs below the flip, shorts above) | +0.46 bp/day, p 0.029 | **+1.37, p 0.19** (all days +1.46, p 0.10) | −0.78, p 0.88 | +10.0, p 0.028 |
| E2 Monday minus other days | +7.35, p 0.016 | **−5.07, p 0.87** | +0.53, p 0.45 | **+34.4, p 0.039** |
| E3 VIX > 17.86 minus other days | −4.3, p 0.033 | **−2.37, p 0.17** | **−6.2, p 0.022** | −10.8, p 0.20 |

* E1 has the right sign in 3 of 4 sets but is not significant out of sample. E2 for SPY was a fluke.
* For TSLA, Monday agrees with the proven TSLA Monday up-burst rule (REPORT §4o, 1.95×). That is an independent prior, but this test is still exploratory.

### ML (registered on SPY; exploratory on TSLA). **FAILS** everywhere.
* Gradient boosting: train AUC 0.99-1.00 (memorised), validation 0.47-0.53, test 0.51-0.56. Logistic regression: test AUC 0.50-0.58.
* No ML filter beat the unfiltered rule on test (2026), and every Sharpe-difference CI includes 0.
* Top features (unstable) were the regime-alignment flag, VIX, the 0DTE share and opening volume. With about 300 training days the conditioning variables don't generalise.

### TSLA: what worked (exploratory; all complete days, classic 5-min breakout)
* **By year:** +5.1 (2024), +34.9 (2025), +15.0 (2026) bp/day. Sharpe 1.37 (clean set: 0.99).
* **Win/loss:** 43% wins; average win +206 bp vs average loss −123 bp. A trend-following payoff.
* **Longs beat shorts:** +24 vs +13 bp a trade.
* **Weekday:** Mon +43 and Fri +42 (TSLA's weekly expiry); Tue −2, Wed −3, Thu +14.
* **Opening volume vs its 14-day norm:** high tercile +48, mid −5, low +17. Not monotone.
* **Auction-gap days** (large open-auction move, the D2-flagged days): +41 vs +12 on other days.

### Why (the mechanism, tied to proven rules)
* **SPY is liquidity-driven** (playbook rule 5; order-flow study: day net flow vs move ρ −0.12). A deep book and dealer hedging absorb the opening imbalance, so the first 5 minutes don't tell you where SPY closes. Breakouts get faded and stops get run.
* **TSLA is flow-driven** (ρ +0.48). When the opening crowd pushes it, the push tends to persist. A breakout is a bet on persistence, so it works where persistence exists.
* QQQ sits in between, and so does its result.
* **The flip** predicts multi-day burst asymmetry (§4z), not intraday continuation. Below the flip, SPY's intraday path is more two-sided (V-shapes), which kills stop-based breakouts, especially on the short side.

### A3 results (TSLA out of sample + screened candidates; `python a3.py`, `python robust.py`; `out/a3.json`, `out/robust.json`, `out/orb_a3.png`)

**C1: TSLA 2020-23, out of sample. PASS.**

The frozen S1_5_close rule:

| Set | Sessions | bp/day | Shift p | Sharpe | Hit | Average win / loss | By year |
|---|---|---|---|---|---|---|---|
| Clean days (primary) | 715 | **+29.5** | **0.018** | 1.94 | 41.5% | +253 / −129 | 2020 +37, 2021 +27, 2022 +45, 2023 +14 |
| All complete days | 994 | +24.6 | 0.046 | 1.59 | 40.9% | +259 / −137 | +16, +24, +41, +17 |

* **The four splits are not confirmed** (all complete days):
  * Mon+Fri +12.1 (p 0.24);
  * longs over shorts +13.2 (p 0.20);
  * high opening volume +5.5 (p 0.38; +29 on clean days, p 0.058);
  * auction-gap days **reversed**: −3.6 vs +30.0 (p 0.93).
* **So the base rule is what carries over;** the 2024-26 conditions were noise.
* **Robustness (exploratory)** on 2020-23 clean days:
  * extra cost +10c/share/side → +24.0;
  * without the 10 best days → +16.1;
  * excluding the top-decile |gap| (news) days → +28.0;
  * max drawdown −24% at 1×, 62% of months positive, worst month −6.3%;
  * median trade −76 bp. It is a trend-following payoff: many small losses, few big wins.
* **The 2024-26 TSLA result is more fragile:** without its 10 best days it is −1.4 (clean) or +5.2 (all days). Most of it came from big-gap days: +50 to +63 bp/day vs +8 to +14 on other days.

**C2: screened candidates 2024-26.** The 2023 ATR% screen with the $1.5bn liquidity filter picked AMD, NVDA, NFLX, META, AMZN, with UNH and JPM as controls (`out/screen_2023.json`).
* **The answer depends on the day set:**
  * clean days: high group −1.04 bp/day (pooled p 0.58), controls −7.3;
  * all complete days: high group **+6.1 (pooled p 0.007)**, controls +8.0.
* **Why the two sets differ:** for single stocks the D2 flag is mostly the opening auction (70-78% of days for the NYSE names UNH and JPM). Flagged days are big opening-imbalance days and much better for the breakout (for example AMD +30 flagged vs −7.7 clean). The clean set is a biased, quiet-open subsample for single stocks, so the all-complete-days set is the fair one. This judgement is made after seeing the data and is flagged as such.
* **Stress tests** (all complete days; bp/day, then with +5c a side, then without the 10 best days):

  | Name | bp/day | +5c a side | Without 10 best days |
  |---|---|---|---|
  | NFLX | +12.8 | +7.5 | +6.2 |
  | UNH | +10.3 | +7.7 | +3.3 |
  | NVDA | +8.9 | +3.3 | −1.3 |
  | AMD | +6.8 | +1.1 | −6.6 |
  | JPM | +5.7 | +1.7 | +0.6 |
  | META | +1.5 | −0.2 | −5.7 |
  | AMZN | +0.5 | −4.3 | −4.9 |
  | QQQ | +3.8 | +2.0 | −0.8 |
  | SPY | −0.7 | −2.4 | −3.2 |

* **The screen does not discriminate:** the low-volatility controls did as well as the high group. What separates winners from losers is **single stock vs index**, and **news-gap days.** On the top-decile |gap| days the breakout made +42 (NVDA), +32 (AMD), +36 (NFLX), +19 (JPM), against +4 to +10 on other days.

**Money translation (TSLA, S1_5_close, every tradable day; `out/tsla_money.json`; descriptive):**

| | 1×, the whole account in shares, intraday | Paper sizing (1% risk a trade, ≤ 4×; median 0.75×) |
|---|---|---|
| 2020-23 (out of sample) | about +62%/yr simple (CAGR 72%); max drawdown −30%; worst day −5.3%; by year +33 / +75 / +154 / +45%; with +5c costs about +56%/yr | CAGR 66%, max drawdown −19% |
| 2024-26 | about +47%/yr simple (CAGR 51%); max drawdown −23%; by year +8 / +119 / +33% (2026 to Oct 30) | CAGR 28%, max drawdown −18% |

* The longest losing streak is 10-12 sessions.
* Returns scale with TSLA's daily range: 2022 was the extreme.
* The backtest fills at 1-minute granularity. Margin, the PDT rule and taxes are not modelled.

### A4 results: exit rules and early-loss diagnostics (`python exits.py`, `out/exits.json`; post-hoc cut in `posthoc_cut.py`)
* **Bug caught and fixed before reading any result.** The first run divided short-trade P&L by a negative mirrored price, which flipped the sign of every short. The base then read +5 bp/day instead of the engine's +18.5 / +24.6. After the fix, the base matches `orb.py` exactly.
* **Named best on 2024-26:** TRAIL1R (Sharpe 1.50 vs 1.37).
* **Not confirmed on 2020-23:** Sharpe 1.43 vs 1.59, mean 17.8 vs 24.6 bp/day, CI of the difference [−13.5, −0.6].
* **No exit rule improves the base in both periods.** Rules that cut losses shrink them, but cut the winners about as much. Sharpe stays about the same or falls; it is the same as trading smaller.

  | Rule (2024-26 / 2020-23) | bp/day | Win % | Average loss bp | Worst day bp | Max drawdown bp | Sharpe |
  |---|---|---|---|---|---|---|
  | Base | 18.5 / 24.6 | 43 / 41 | −123 / −137 | −328 / −534 | −2,423 / −3,502 | 1.37 / 1.59 |
  | MID stop (half the risk) | 10.8 / 20.3 | 28 / 26 | −70 / −75 | **−165 / −302** | −2,569 / −2,107 | 1.06 / 1.59 |
  | REIN30 (failed-breakout exit) | 10.6 / 12.5 | 13 / 12 | **−27 / −29** | −240 / −254 | **−1,612 / −2,361** | 1.29 / 1.37 |
  | Time stop T30 | 14.0 / 23.3 | 34 / 34 | −95 / −107 | −312 / −569 | −2,381 / −3,791 | 1.09 / 1.59 |
  | BE1R | 16.0 / 21.9 | 34 / 30 | −91 / −95 | −328 / −534 | −1,981 / −3,820 | 1.31 / 1.51 |

* **Early-loss diagnostics** (base rule, both periods agree):
  * At +30 minutes, a trade **in profit** ends a winner 69% of the time; one **not in profit**, 29-31%.
  * One down **−0.5R or more**: only 10-15%.
  * But winners also dip: the median winner first goes −0.27R against you, the 75th percentile −0.5R, the 90th −0.7R.
* **Post-hoc rule** "exit at +30 minutes only if ≤ −0.5R": 2024-26 +19.6 (vs 18.5; max drawdown −1,959 vs −2,423); 2020-23 +23.3 (vs 24.6). That is neutral. The deep losers would mostly hit the −1R stop anyway, and the 10-15% that recover are big winners.
* **Daily return on capital at 1×** (`out/tsla_daily_returns.json`): see the owner summary.

### A5 results: the TSLA breakout with options, 2024-26 (`python opts.py`, `opts_itm.py`, `opts_diag.py`; `out/opts*.json`, `out/orb_opts.png`)
* **Data:** ThetaData 1-minute option bars and quotes, 921 option-days (nearest expiry plus 0DTE), included in the plan.
* **Fills:** buy at the ask of the next-minute quote; sell at the bid after the underlying stop, or at 15:55. Hand-checked: Apr 9 2025, ask $10.40 → bid $42.50 = +309%.
* **Pre-registered (ATM, nearest expiry ≥ 1 day; median 3 days to expiry, held a median 5.8 h):**
  * 702 trades: **mean +0.4% on premium (t ≈ 0), median −20%**, 35.5% wins, average win +58%, average loss −31%.
  * Shares on the same days: +16.8 bp a trade. **The share edge does not carry over.**
* **0DTE ATM** (217 expiry days): mean +13.9%, median −53%, worst −100%. Not significant (t ≈ 1.3), and driven by 2025 (+32%; 2024 −2%).
* **Exploratory in-the-money versions** (2 and 4 strikes ITM): next expiry −0.4% and −0.8%; 0DTE +7.4% and +4.2% (t 1.1-1.3). No improvement.
* **Why (decomposition; mid-to-mid regression):**
  * Leverage is about 26× per 1% stock move.
  * The breakout's directional move is worth **+3.7%** of premium.
  * Convexity costs −0.8%: implied volatility falls on big moves.
  * Time decay and IV drift cost −0.3%.
  * **The bid-ask spread costs −2.2%** per round trip.
  * That leaves +0.4%.
* **Verdict for A5:** don't use short-dated TSLA options for this rule. Shares, or a delta-equivalent stock position, keep the edge; options give it back to the spread.

**What this adds to the mechanism:**
* The breakout is a bet on a **trend day**. It pays when information or one-sided flow arrives and persists: single stocks, news days, and TSLA most days.
* It fails where liquidity and index arbitrage absorb the push (SPY).
* TSLA is special because its trend days are not only news days: in 2020-23, excluding gap days barely changed the result.

## Threats to validity
* **Venue:** EQUS.MINI is not the full consolidated tape. Highs and lows can differ slightly, which D2 checks.
* **Fill realism:** stop fills at bar granularity; there is no queue position.
* **Period:** 2024-26 is mostly a bull market. The regime split shrinks the samples.
* **The flip** is a model level that depends on our convention (classic dealer sign).

## Verdict
* **Contradicts** the practitioner ORB claim for SPY (two periods, two venues, 24 variants).
* **Contradicts** our own H2 prediction: the gamma regime does not make SPY breakouts work, and below the flip they are worse.
* **A3 update:** the TSLA 5-minute breakout **passed out of sample on 2020-23** (+29.5 bp/day, p 0.018, every year positive). It is now a tested TSLA rule, with a −24% max drawdown at 1× and a trend-following payoff. Other single stocks are positive but fragile, mostly a few news days; indices fail.
* **Extends** the playbook with leans only:
  * (1) Below the flip, don't short SPY's opening breakdown (consistent in both periods, untested as a single cell).
  * (2) TSLA's 5-minute breakout is the only live version: +12 to +18 bp/day, p 0.02-0.05 alone, joint p 0.09-0.28. **Next:** confirm on TSLA 2020-23 (Nasdaq bars, about $0.3-0.5, owner's OK) and forward-test from Nov 3 with the rule frozen.
* No change to the originals.

## Reproduce
```bash
python fetch.py   # needs DATABENTO_API_KEY in the environment
python audit.py && python orb.py && python explore.py && python ml.py && python figure.py
```
