# Working memory (overwrite at the end of every task)
**Updated:** 2026-11-06 (after the crash-law test).
Read this first, then LESSONS.md.
* Theory: [FOUNDATION.md](../FOUNDATION.md)
* Plan: [PROGRAM.md](../PROGRAM.md)
* Study log: [INDEX.md](../INDEX.md)

## Where we are
* **Program:** laws-first (PROGRAM.md, revision 2026-11-06). The theory is FOUNDATION.md: 16 laws in three layers.
* **Last task done:** test #4, the crash law (`2026-11-06-crash-law/`, pre-registered @ 77fea8a). The owner approved it once the papers were read in full.
  * All seven crash-law papers read in full, with cards.
  * **Results:**
    * Kyle–Obizhaeva's five crashes replicate.
    * Volume bound: the square-root law needs more one-sided selling than the day's whole volume on 54/54 S&P shock days (median 8.3×; 8.4× with the week-before state). The linear law needs ≤ 25% on 80%.
    * But the Nov 5 close (known leveraged-ETF flow) followed the square root, and linear over-predicted 5–16×.
    * Verdict: crash days are a liquidity regime change (sensitivity about 10× higher), or news.
  * **Next, needs approval:** Part D, ES/NQ trades with aggressor side on 5 selloff days (2024-08-05, 2025-04-03/04/07, 2026-11-05) plus calm days, about $25–35. Get an exact Databento quote first. We already hold ES trades for 2026-10-27 (calm).
* **Before that:** the M3 signature test (`2026-11-06-signature-test/`).
  * H1 (fade) passes narrowly: p 0.049, corrected joint p 0.08.
  * H2 (memory condition) not established, but in the predicted direction.
  * H3 (second legs) fails.
  * Live forecast logged: the Nov 5 shock is build-up in all three indices; score around 2027-03-16.
* **Papers read in full** (cards in memory/papers/):
  * Marcaccioli 2021; Sornette–Malevergne–Muzy 2002; Sornette–Helmstetter 2003; Patzelt–Bouchaud 2018; Muhle-Karbe 2026;
  * the crash set: KO2023, KO2016, Benzaquen 2016, Bucci 2019, Bucci 2020, Donier–Bouchaud 2015, Donier–Bonart 2015.
* **Reading queue:** Tóth 2011; Sato–Kanazawa 2024; Maitrier 2025; Cont–Kukanov–Stoikov 2014; Hartzmark–Solomon 2025; Gabaix–Koijen; Farmer–Gillemot–Lillo 2004 ("What really causes large price changes?"); Joulin 2008. Get the text from arxiv.org/pdf/<id> with pdftotext.
  * **Before M1, read:** Ané–Geman 2000 (KO2016 and Benzaquen 2016 are done).
* **Agenda proposed to the owner on 2026-11-06 (waiting for their reaction). Literature-led, laws first:**
  1. **How mechanical is the market?** The share of ES/NQ price moves explained by order flow through the impact law, vs news. This is the order-driven vs fundamental debate (Maitrier & Bouchaud 2025; Joulin 2008).
  2. **Did 0DTE options and dealer gamma change the physics?** Impact constant, depth, pinning and liquidity feedback, by year and by gamma sign. No paper measures this.
  3. **Cross-impact in an AI-concentrated market:** how selling in NVDA and the AI names moves QQQ and SMH (Hey et al. 2025).
  4. **Crash law** (Kyle & Obizhaeva 2023): can business time plus estimated forced flows predict selloff size (Aug 2024, Apr 2025, Jun 2026, Nov 2026)? Mostly free.
  5. **Distance to instability:** liquidity feedback (Fosset 2020) and branching ratio, intraday, and whether negative gamma moves the market closer to the edge.
  * The owner's ideas sit inside these as applications: absorption (1, 5), exhaustion (1), levels (5), close and forced flows (4 and S2).
  * Items 1–3 and 5 need tick data. Get a quote before spending.

## Waiting on the owner
1. **Approval for crash-law Part D:** ES/NQ signed trades, about $25–35. Quote first.
2. About $100 of order-flow data, for the fast-layer laws and the close.
3. Which agenda item comes next: 1 (how mechanical), 2 (0DTE/gamma), 3 (AI cross-impact) or 5 (distance to instability). The crash result points to 5 and 1.

## Scheduled scoring
* M3 live forecast (Nov 5 shock): score after day 89, around 2027-03-16.
* Aftershock forecasts: 2026-11-13, 2026-12-07, 2027-02-05.
* Year-end forecast: 2026-11-13.
* Overdue: EV1 and TP1 (due Nov 5); live-read LR1 (due Nov 6 close).
* CPI on Nov 10.

## Reminders
* The owner should rotate the ThetaData key.
* The Scite citation tool needs a paid plan. Verify papers through Crossref or arXiv instead (scripts in `2026-11-06-literature-laws/`).

## Local data (gitignored; lost when the container resets)
* `2026-11-04-deferred-days/data`: ES trades for 2026-10-27; TSLA trades for 10-27 and 10-28; TSLA 10-level book for 10-28.
* `2026-11-02-orb-gamma/data`: Databento 1-minute bars for SPY, QQQ and TSLA, 2020–26.

## Repositories
* **Research:** this repo; push to `origin main`.
* **Figures for the owner:** the genovy repo, folder `today/`, branch `claude/price-lines-order-flow-bjaulu`.
