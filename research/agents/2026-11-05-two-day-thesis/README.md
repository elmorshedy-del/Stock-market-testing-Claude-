# What drove Nov 4 (Day 1) and Nov 5 (Day 2)? Competing theses, tested

**Agent / session:** Claude, for the owner, 2026-11-05 ~14:50 ET. **Pre-registered at commit:** the commit that first adds this README.

**Owner:** "Create a thesis for yesterday and today's move and test them, till you reach something that's satisfactory and almost elegant."

**Method:** observe first, then competing theses with predictions only they make, then tests. Revisions are logged as amendments. Day 2 is evaluated at the 16:00 close; any earlier run is labelled a preview.

## 0. Observations (before any test)
Data: Yahoo daily and intraday bars, plus the Yahoo Finance, Reuters and CNBC timelines. Day 1 = Wed Nov 4, Day 2 = Thu Nov 5.

**O1. Day 1 was a split day.**
* AI suppliers fell: VST −13.8%, VRT −12.9%, ETN −9.9%, GEV −9.3%, CRWV −9.9%, DELL −8.8%, MU −7.0%, MRVL −7.1%, NVDA −3.2%.
* AI spenders and almost everything else rallied: MSFT +6.7%, AMZN +6.1%, AAPL +5.3%, homebuilders (ITB) +7.3%, airlines (JETS) +6.7%, retail (XRT) +5.5%, gold miners (GDX) +9.0%, solar (TAN) +5.7%, equal-weight S&P (RSP) +1.9%.
* SPY gained +1.65%, all at the open, then stayed flat all day while SMH bled −3.6% from its open.

**O2. A second channel: oil and the war.**
* Oil fell 7.4% on Monday and 8.3% on Day 1 (WTI $88, −15% in 3 days). Traders bet that a weakened Trump ends the Iran war, which began in February.
* Energy (XLE) −4.7%, 10-year yield −6bp, gold +3.7%, VIX −20%.

**O3. Day 2 had no gap.**
* SPY opened −0.2% and QQQ −1.3%. Nasdaq futures drifted only −1.5% overnight.
* The crash came in the US cash session: one-way selling 09:30–10:50 (QQQ low 647.4 at 10:50). The broad market made its lows later (13:00–14:05). After that, a light-volume hover at SPY 735 / QQQ 650.

**O4. Day 2 cross-asset.**
* AI suppliers −7% to −15%. AI spenders fell less than the market (AAPL −1.6%, GOOGL −1.6%, AMZN −2.3%).
* Defensives about flat: staples (XLP) −0.4%, utilities (XLU) −1.0%, communications (XLC) −0.8%.
* Gold +0.9%, yields −7bp, oil +2.7%, BTC −5.4%, VIX +56%. Korea and Taiwan ETFs −11%.

**O5. Day 2 press (13:20):** "dumping software's AI winners and mostly leaving the losers alone." PLTR, CRWD and NET fell 10%+ while CRM and ADBE barely moved.

**O6. Day 2 overnight headlines:** "Trump's midterm drubbing demonstrates the power of data center opponents"; Apple reportedly cutting internal AI budgets; the Bank of England hiked; JD Vance said "the reason we lost is the war."

## 1. Competing theses
* **T1. Policy repricing of the AI buildout.** The sweep raised the odds of a political brake on data centers. That transfers value from suppliers to spenders and is persistent news. Separately, oil and yields fell.
* **T2. A crowded-trade unwind.** The election was the trigger, not the cause. Day 1 was a momentum crash (winners down, losers up). Day 2 was de-grossing of crowded winners regardless of fundamentals. The non-fundamental part of Day 1 reverses.
* **T3. Macro relief, then a vol-regime break.** Day 1 was driven by oil and rates. Day 2's index size came from deleveraging in a calm, short-gamma market, so selling was proportional to market beta.

## 2. Tests
**Universe:** S&P 500 constituents (datasets/s-and-p-500-companies list) with ≥150 days of data. Day returns are winsorized at 1/99%.

**Exposures**, estimated 2025-11-03 → 2026-10-30 by one OLS per stock:
* daily return on SPY (MKT), SMH − SPY (AI), USO (OIL), TLT (RATE), GLD (GOLD);
* MOM = 12-1 month return (2025-10-31 → 2026-09-30);
* STR = October return.

**Cross-sectional regressions per day** (exposures z-scored; HC3 SEs):
* Model A = MKT, AI, OIL, RATE, GOLD.
* Model B = A + MOM + STR.

**Hypotheses** (one-sided tests; Holm across H1–H5; pass at adjusted p < 0.05):
* **H1 (T1/T3, Day 1):** Model A on Day 1 has AI < 0, OIL < 0 and RATE > 0. The p used is the largest of the three.
* **H2 (T2, Day 1 momentum crash):** MOM < 0 on Day 1 in Model B.
* **H3 (T2 vs T1, the key discriminator):** MOM < 0 on Day 2 in Model B, **within stocks with AI exposure below its 70th percentile.** T1 predicts no momentum effect outside AI suppliers.
* **H4 (T3, Day 2):** MKT < 0 on Day 2 in Model B.
* **H5 (T2 vs T1):** corr(Day-1 residual, Day-2 residual), both from Model A, < 0. Positioning reverses; news persists.
* **H6 (contagion timing, intraday, separate family):** on Day 2, the time of the intraday low is earlier for the top AI-exposure tercile than the bottom. Mann–Whitney, one-sided.

**Robustness:** Huber regression; within-sector (sector-demeaned) versions.

**Descriptive:**
* R² of A and B per day;
* sector and industry tables;
* the software winners-vs-losers check;
* spenders vs suppliers;
* history of "rotation days" (SMH − RSP ≤ −3% with RSP ≥ +1%) and what followed.

**Elegance yardstick (stated now):** the fewest mechanisms whose predictions pass while rivals' fail, that explain both days, including why the broad market flipped from up to down.

---

# Preview results (14:44 ET, Day 2 live) and Amendment A1 (pre-registered before running A1)
**Preview** (`out/tests_preview.json`):
* H1 passes: Day 1 AI −2.45%/SD (t −11.6), OIL −1.43 (t −9.6), RATE +0.81 (t +4.2); R² 0.46.
* H4 passes: Day 2 MKT −1.56 (t −13.4).
* **H2 fails:** Day 1 MOM +0.09 (t 0.3). There was no momentum crash. Instead, October's losers rose (STR −0.72, t −3.0).
* **H3 fails:** within low-AI stocks MOM −0.38 (t −1.5, Holm 0.20), though −3.7 on the full sample.
* **H5 fails:** residual corr +0.07, so Day 1's unexplained part did not reverse.
* **H6 fails:** median time of the low was the same for the high- and low-AI terciles. By sector, tech's low came at ~11:05 and utilities' at ~14:20.
* **Reading:** T2 as registered mostly fails. The AI loading was about equal on both days (−2.45 vs −2.21%/SD). The market loading went from ~0 on Day 1 to −1.5%/SD on Day 2.

## A1 thesis ("same shock, different offset")
* Both days carried the **same AI-buildout shock**.
* On Day 1 a **peace-trade offset** (oil −8%, yields −6bp) lifted everything else, so breadth **decoupled** from AI.
* On Day 2 the offset partly reversed (oil +2.7%). The decoupling ended, and normal co-movement plus the AI shock dragged the broad market down.
* Rival A1-R (contagion beyond normal): Day 2 broad-market selling exceeded normal co-movement with AI.

## A1 tests
* **B1 (time series):** fit the daily equal-weight S&P (RSP) return on SMH, USO, TLT and GLD, 2025-11-03 → 2026-10-30, OLS. Compute the prediction and the residual z for Day 1 and Day 2.
  * **A1 predicts** Day 1 residual z ≥ +2 (breadth rallied beyond normal) and Day 2 |z| < 2 (normal co-movement).
  * **A1-R predicts** Day 2 z ≤ −2.
  * Robustness: the same fit for the equal-weighted mean of S&P stocks with AI exposure below its 70th percentile (no AI names inside).
* **B2 (intraday lead-lag, Day 2, 5-min):** equal-weight returns of the top AI-exposure decile vs stocks below the 70th percentile.
  * Lead-lag statistic L = Σ_{k=1..3} corr(AI_t, rest_{t+k}) − Σ_{k=1..3} corr(rest_t, AI_{t+k}).
  * Contagion predicts L > 0, with a block bootstrap 90% CI.
  * Descriptive: when each group completed half of its day's decline.
* **B3 (history, descriptive):** "rotation days" since 2004 (SMH − RSP ≤ −3% and RSP ≥ +1%). Next-day and next-3-day RSP returns, with the share negative vs the base rate.
* **Final:** all tests rerun on the 16:00 close (`label = final`).

---

# A1 preview results and Amendment A2 (pre-registered before running A2)
**A1 preview** (`out/a1_preview.json`):
* **B1:** A1's Day-2 prediction fails.
  * RSP Day 2: actual −2.64% vs predicted −0.47%, z −3.72.
  * Non-AI EW stocks: −1.81% vs +0.97%, z −3.97.
  * Day 1 was also abnormal: RSP z +1.95; non-AI z +2.54.
* **B2 (descriptive):**
  * Top AI decile: half its decline by 10:10, low at 11:00 (−7.5%).
  * Rest: half by 11:10, low at 13:00 (−3.1%).
  * The rest fell −1.0% from 11:00 to 12:00 while the AI decile bounced +1.1%.
  * The lead-lag L returned NaN (a NaN bar) and is fixed below.
* **B3:** 15 rotation days since 2003. Next-day RSP was negative 33% of the time (base 45%); next 3 days negative 60% (base 43%). Day 2's contagion is unusual for the day after a rotation.

## A2: is Day 2 "abnormal contagion" or "normal tail co-movement"?
* **B4 (tail co-movement):** piecewise regression of RSP on SMH, with separate slopes above and below SMH = −4%, plus USO, TLT and GLD.
  * Fit 2004-01-01 → 2026-10-30, with 2023-01 → 2026-10 as robustness.
  * Report both slopes, then the Day 1 and Day 2 predictions and residual z.
  * "Tail-normal" (Day 2 is the rule) predicts Day 2 |z| < 2.
  * "Abnormal contagion" predicts Day 2 z ≤ −2 even with the tail slope.
* **B5 (basket-selling signature):** average pairwise correlation of 5-min returns among 150 non-AI S&P stocks (AI exposure below its 70th percentile, seeded random sample).
  * Compare Day 1 and Day 2 with the prior ~55 sessions (Yahoo 60-day 5-min). Report each day's percentile and z.
  * "Portfolio problem" predicts Day 2 ≥ 95th percentile of baseline days. "Rotation" predicts Day 1 below the baseline median.
* **B2 fix:** drop NaN bars before computing L.

---

# A2 preview results and Amendment A3 (pre-registered before running A3)
**A2 preview** (`out/a2_preview.json`):
* **B4 tail model.** The extra slope below SMH −4% is +0.57 (t 4.7) over 2004–26, and +0.21 (t 1.3) over 2023–26.
  * **Day 2 is not abnormal once tail co-movement is allowed:** z +2.07 (full sample; RSP fell *less* than predicted) and −1.12 (recent).
  * **Day 1 is abnormal under every model:** z +4.62 (full), +3.46 (recent), +1.95 (linear).
  * The 5 recent days with SMH within 1.5pt of −8.7% had a median RSP move of −1.42% (mean −2.6%).
* **B5:** Day 1 pairwise correlation among non-AI stocks was 0.149 (median, 52nd percentile). Day 2 came back missing: the 60-day 5-min pull had no Nov 5 bars, so it is recomputed from the 5-day pull below.
* **B2 fixed:** L = −0.40 (90% CI −0.66 to +0.26). No 5-min lead-lag; the ordering is at the hour scale only.
* **Revised reading:** "Day 1 was the anomaly; Day 2 was the rule."

## A3: is there a rotation zone and a coupling zone?
* **B6:** bin SMH daily returns (≤ −6, −6..−4, −4..−2, −2..0, 0..+2, > +2%) over 2023-01 → 2026-10 and over 2004 → 2026-10. Per bin, report mean RSP, share of RSP < 0, and the coupling ratio = mean RSP ÷ mean SMH.
  * **Prediction:** the coupling ratio in the ≤ −4% bins is at least twice that of the −4..−2 bin.
  * In the recent regime, the −4..−2 bin's mean RSP is ≥ −0.3% (a rotation zone).
* **B5 fix:** compute Day 2's pairwise correlation for the same 150 names from the 5-day 5-min pull, against the same baseline.

---

# A3 preview results and Amendment A4 (pre-registered before running A4)
**A3 preview** (`out/a3_preview.json`):
* **B6 fails.** No rotation-then-coupling threshold.
  * Recent coupling ≈ 0.18–0.24 in every bin; tail 0.184 vs mid 0.194 (ratio 0.95). The mid bin's mean RSP is −0.56% (not ≥ −0.3%).
  * Full sample: ratio 1.11.
* What stands: on days with SMH −2..−4%, RSP is down 75% of the time (mean −0.56%). Day 1's +1.86% is a rare decoupling.
* B5 Day-2 correlation is still NaN (irregular live timestamps); fixed in the final run by flooring to 5-min bars.

## New observation (from §0 data, previously unused)
* **Monday Nov 2, the day before the election, already showed the Day-1 pattern** on an Iran peace-talk headline: oil −7.4%, SMH −2.71% vs RSP +0.76%, CRWV −8.6%, ORCL −8.8%, AMD −7.5%, ITB +4.6%, JETS +4.2%, XLY +2.4%.

## T4 ("war-shelter eviction")
* During the Iran war (since end-Feb 2026), AI was the growth shelter from oil. When oil spikes, money hides in AI; on peace news it rotates into oil-sensitive cyclicals.
* The election added peace odds (oil −8.3%) on top of the data-center politics. T4 explains Day 1 mostly through oil.
* Day 2 (oil +2.7%) cannot be oil-driven, so T4 needs a non-oil driver on Day 2.

## A4 tests
* **C1:** corr(USO, SMH − RSP) over the war period 2026-03-02 → 2026-10-30 is > 0, and higher than pre-war (2025-06-02 → 2026-02-27). Fisher z-test, one-sided.
* **C2:** the Monday Nov 2 cross-section (Model A, same exposures) has AI < 0 and OIL < 0, each with t ≤ −3. If so, the rotation existed before the election result.
* **C3:** war-period OLS of (SMH − RSP) on USO, used to predict the Nov 2 and Nov 4 spreads. Report the share of each actual spread explained by oil.
* **C4 (descriptive):** the same prediction for Day 2 (oil up), to size the non-oil driver.
