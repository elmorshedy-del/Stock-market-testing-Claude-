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

---

# A4 preview results and Amendment A5 (pre-registered before running A5)
**A4 preview** (`out/a4_preview.json`):
* **C1 fails, opposite sign.**
  * War-period corr(USO, SMH − RSP) = −0.193, vs +0.004 pre-war. AI *outperformed* on oil-down days during the war.
  * On 16 war-period peace days (USO ≤ −4%), SMH − RSP averaged **+1.2%** (negative on only 31% of them). AI was not a war shelter.
* **C3, the sign flipped.** The war-period relation predicted SMH − RSP of +1.22% on Nov 2 and +1.36% on Nov 4. The actual spreads were **−3.48% and −4.60%**. From Nov 2, peace news coincided with AI *under*performance.
* **C2 passes.** Monday Nov 2's cross-section matches Day 1: AI −1.43%/SD (t −11.5), OIL −1.32 (t −11.9), RATE +0.45 (t 2.6), R² 0.53. Stock returns correlate 0.54 between Monday and Day 1. The rotation predates the election result.
* Election day (Tue) partly reversed it: AI +0.92 (t 8.7).

## T5 ("AI became the funding leg")
* Since the October peak, the AI suppliers are where money is *taken from* when risk appetite improves. Good news for the economy now means AI is sold to buy the rest.
* Earlier in 2026, the rest of the market and the AI spread rose together.

## A5 test
* **D1:** corr(RSP return, SMH − RSP spread), 2026-03-02 → 2026-10-02 (war, before the AI peak) vs 2026-10-05 → 2026-11-03 (after the peak, before Day 1). Fisher z, one-sided.
  * **T5 predicts:** the post-peak correlation is negative and lower than before.
  * Also reported: the same on war-period peace days vs Nov peace days (descriptive), and a rolling 20-day correlation.
* All tests are then rerun on the 16:00 close with `label = final`.

---

# A5 preview result and synthesis (PREVIEW: Day 2 data to 14:44 ET; the automatic rerun on the 16:00 close follows below)
**A5 fails:**
* corr(RSP, SMH − RSP) was +0.188 (Mar 2 – Oct 2, n 150) and −0.177 after the peak (n 22). Fisher z −1.51, p 0.065.
* Rolling 20-day: +0.63 in March, +0.43 to +0.46 in May–Jun, −0.35 in July, −0.1 to −0.3 in Oct–Nov.
* Suggestive only.

**Exploratory, not pre-registered:**
* 12-1 momentum correlates 0.64 with AI exposure. AI + OIL explains each day better than MOM alone (Day 1 R² 0.42 vs 0.15).
* Only the top momentum decile moves differently (Day 1 −3.7%, Day 2 −7.7%; deciles 0–8 alike). Crowding is the AI exposure, not a separate force.
* Post-peak days with SMH − RSP ≤ −3% (n 7): RSP rose on 4, each with a macro cushion (oil −7/−8%, or TLT +0.9/+1.9). It fell on the 3 without one, Day 2 included.

## Thesis v4, "same AI shock twice; only the cushion changed"
1. **One shock both days.** The data-defined AI basket (top 10% by AI exposure) is the **data-center build-out supply chain**: chips, memory and storage, networking and optics, servers, power and electrical equipment.
   * It was repriced at the same intensity both days: −2.45 vs −2.21%/SD, t −12 and −18 (H1, C2).
2. **Day 1 had a cushion.** The election lifted Iran-war-ending odds: oil −8.1%, 10-year −6bp. Oil exposure −1.43%/SD (t −9.6), rate exposure +0.81 (t +4.2).
   * The rest of the S&P rose **+3.2%** (equal weight), a rare decoupling for a −2.75% chip day. RSP z +3.5 (recent tail model), +4.6 (full sample).
3. **Day 2 had none.** Oil rose 2%, so the rest did what it normally does on a −9% chip day: −1.8% (RSP z −1.1 in the recent tail model; the 5 recent analogs had a median of −1.4%).
   * Selling was proportional to market beta (H4, t −13).
   * Intraday, the AI basket front-loaded (low 11:00) and the rest kept falling to 13:00.
4. **Not new.** Monday Nov 2 (Iran talks) had the same pattern (AI −1.43/SD, OIL −1.32/SD; corr 0.54 with Day 1), and Tuesday mirrored it.
   * A **seesaw** ran Mon–Wed: AI and oil moved together, the rest opposite. Thursday broke it.
5. **Net:** over the two days the AI basket fell **−14.2%** and the rest of the S&P rose **+1.4%**. Over four days: −14.5% vs +2.1%. A rotation that, on Day 2, briefly dragged everything.

**Rejected:**
* momentum crash (H2);
* crowding outside AI (H3);
* Day-1 reversal (H5);
* AI-first timing at 5-minute resolution (H6, L);
* a "rotation zone" threshold (A3);
* AI as a war shelter (C1).
* The linear 1-year model (B1) flags Day 2 as abnormal; the tail model does not.

**Open:**
* Why AI started *falling* on peace news in November after *rising* on it all war (C3: predicted +1.2–1.4%, actual −3.5/−4.6%). It fits an AI trade that peaked Oct 6 and an election that made data centers political. A5 (p 0.065) only hints at it. Not tested causally.

**TSLA:** about −8% stock-specific over the two days (Day 1 −4.2%, Day 2 −3.9% beyond exposures; Musk/Texas/SpaceX-merger news). The rest is its market beta (z +2.0).

**What it implies (a map, not a forecast):**
* While the AI build-out keeps being repriced, the rest of the market's direction depends on whether a cushion shows up (oil or yields falling).
* Friday's payrolls is the next test: a weak print means lower yields, a cushion. A hot print removes it.

---

# FINAL results (16:00 close; rerun 16:06–16:07 ET). These supersede the preview where they differ.
Files: `out/*_final.*`, figure `out/two_day_thesis_final.png`.

**Closes, Day 2:** SPY 733.11 (−4.39%), QQQ 647.05 (−6.49%), RSP −2.89%, IWM −4.58%, **SMH −11.21%** (preview −8.69%). AI basket EW −11.39%, rest EW −1.73%, TSLA 343.69.

| Test | Preview | **Final** |
|---|---|---|
| H1 Day-1 AI/OIL/RATE | pass | **pass** (t −11.6 / −9.6 / +4.2) |
| H2 Day-1 momentum crash | fail | **fail** (t +0.3) |
| H3 Day-2 crowding outside AI | fail (Holm 0.20) | **pass**: −0.83%/SD, t −3.1, Holm p 0.0009; Huber −5.2, sector-demeaned −2.8 |
| H4 Day-2 beta selling | pass | **pass** (t −14.2) |
| H5 Day-1 residual reverses | fail | **fail** (corr +0.11) |
| H6 AI lows earlier | fail | **fail, reversed**: high-AI median low 14:25 vs low-AI 13:00 |
| B1 Day 2 vs linear model | z −3.7 / −4.0 | z −3.72 (RSP) / −4.08 (non-AI) |
| B4 Day 2 vs recent tail model | z −1.1 | **z −0.85** (normal). Full-sample z +3.33: RSP fell *less* than the 2004–26 tail implies. The 2 SMH-within-1.5pt analogs were 2020-03-12 (−10.1%) and 2025-01-27 (+0.1%). |
| B4 Day 1 | z +3.5 / +4.6 | z +3.46 / +4.62 |
| B5 non-AI co-movement | Day 2 missing | **Day 2 0.253 = 98th pct of 58 days (z +2.5)**; Day 1 0.149 (52nd pct) |
| B2 5-min lead-lag | L −0.40 | L −0.31 (CI −0.59..+0.28): none |
| C2 Day-2 cross-section | — | AI −2.93 (t −22.4), MKT −1.68, OIL −0.05 (n.s.) |

**Intraday Day 2** (EW from the open):
* AI basket −7.2% at 11:00, recovered to −4.6% at 14:45, then fell to **−7.3% at 15:55, its low, at the close**.
* Rest: low −3.0% at 13:00, then flat (−2.6% at the close). The final hour's selling was AI-only.

**AI basket minus the rest:** Mon −5.0, Tue +3.9, **Wed −9.0, Thu −9.7**.
**Net:** two days AI basket **−16.5%**, rest **+1.4%**. Four days −16.8% vs +2.2%.
**TSLA:** stock-specific −4.2% (Day 1) and −2.9% (Day 2) beyond its exposures.

## Final thesis (v5): "same relative shock, different level"
1. **The relative shock was the same both days.** The data-defined AI build-out basket (chips, memory and storage, networking and optics, servers, power and electrical equipment) lost **9–10% against the rest of the S&P on each day** (−9.0%, −9.7%).
   * In cross-sectional loadings, Day 2 was about 20% larger (−2.93 vs −2.45%/SD).
2. **Only the level of the rest changed.**
   * **Day 1 was cushioned:** the election's Iran-peace odds sent oil −8.1% and yields −6bp, and the rest rose **+3.2%**. That is a rare decoupling (z +2.5 to +4.6); normally a −2.75% chip day drags the broad market down.
   * **Day 2 had no cushion:** the rest fell **−1.7%**. The size is ordinary for an −11% chip day in the 2023–26 regime (z −0.85).
3. **Day 2's broad selling had the signature of portfolio de-risking, not news about those companies.**
   * Non-AI stocks moved as one basket (98th-percentile co-movement).
   * Selling was in proportion to market beta (t −14), with crowded winners outside AI sold too (t −3.1).
   * Yields fell and defensives held.
   * It ran 10:00–13:00 and stopped as SPY reached its 735 gamma trough and put block. The AI leg alone kept falling into the close.
4. **Not new.** Monday (Iran talks) had the same pattern and Tuesday mirrored it: a Mon–Wed seesaw (AI and oil together, the rest opposite) that Thursday broke.

**Corrections to the v4 preview text:**
* "same intensity" holds for the AI-minus-rest spread, not the loadings (Day 2 about 20% larger);
* "crowding outside AI rejected" is reversed: H3 passes at the close;
* "AI front-loaded" is wrong for the full day: AI had two legs and its low came at the close.

**Open:**
* Why AI began falling on peace news in November after rising on it during the war (C3).
* The funding-leg hypothesis (A5, p 0.065).
* What drove the AI-only final hour. Leveraged-ETF rebalancing or closing-auction imbalances could test it, using Databento closing-imbalance data (cost to be quoted first).
