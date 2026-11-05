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
