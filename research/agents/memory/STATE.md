# Working memory (overwrite at the end of every task)
**Updated:** 2026-11-16, later (the owner rejected the step-1 direction; a model of the price from the mechanism is written and sent; no data touched).
**Entry point for the work: [MAP.md](../MAP.md).** It replaces PROGRAM.md's order of work.
Read this first, then LESSONS.md.
* Theory: [FOUNDATION.md](../FOUNDATION.md)
* Plan: [PROGRAM.md](../PROGRAM.md)
* Study log: [INDEX.md](../INDEX.md)

## Where we are
* **2026-11-22, LATEST: the vulnerability study, done the scientist's way** (`2026-11-22-vulnerability/`).
  * **The owner's strongest feedback yet:** "For the million time stop this wide scope that you do without any clear reasoning"; "U always go back to a century and you don't know why"; "Stop being a computer that just computes and be a scientist". Then a full research brief: combine economic reasoning with data-driven exploration; linear, nonlinear, conditional and interaction effects; stability across regimes; diagnose failures; iterate.
  * **Their actual question:** inside the post-2009 bull market, when do rates, Fed expectations, inflation, valuation, corporate debt and breadth **together** make the market vulnerable to a correction? Would it have flagged October 2026?
  * **Steps so far (each small, reasoned, frozen before testing):**
    1. cases since 2010, including the non-events;
    2. conditional frequencies 2010–26;
    3. the frozen rule on 1976–2009: **failed**, diagnosed (2y − Fed funds changes meaning at the zero bound);
    4. regime-consistent measures: **only "2-year up 50bp+ in 6 months" holds in both eras** (lifts 1.9 and 1.7; weak p).
  * **2026:** that signal was on from May, +109bp by September (most since 2022, NOT the most since 2010; my message erred, corrected); the cushion was −0.09 (thinnest since 2010).
  * **Proposed step 5 (not run):** inside months when the vulnerable state is on, what separates the times it cracked from the false alarms (2016–17, 2023)? Case-based first, then a frozen test. Alternative: a small cross-era model (fit on one era, test on the other).
* **2026-11-22, latest: THE DISCOVERY SYSTEM** (`DISCOVERY.md`; passes 1–2 in `2026-11-22-discovery/`).
  * **The owner's words, in order:**
    1. "this is u zooming in too much maybe the state of how things get triggered are on bigger scales. I think how things correlate here needs more careful statistical analysis";
    2. "I meant it could be how fast they moved or how certain variables moved together in certain environments... How do mathematicians and scientists and ml experts surface relationships... You should work like them";
    3. "There must a rigorous system we follow to surface relationships. And predictors".
  * **System:** eight stages (fix the question; point-in-time data; sealed lockbox; a systematic feature library; several lenses; chance from time-shifted reruns, purged walk-forward, FDR; stability; mechanism then confirmation).
  * **Result:** one dependable predictor, current stress (VIX + recent realized vol). Nothing among 182 clean weekly variables adds to it; returns unpredictable; weekly lead–lag unstable. NFCI excluded (not point-in-time).
  * **Lockbox 2020+ still sealed.** Candidate list = the stress model only. Ask the owner before opening.
  * **Tools:** the scratchpad venv312 now has lightgbm 4.7, shap 0.54, dcor 0.7 and tigramite (PCMCI). A container reset loses them: reinstall with pip.
  * **Proposed next passes (owner's choice):**
    1. the same system on daily data with positioning (GEX, DIX 2011+) and TSLA, where our only robust results live;
    2. intraday ES/NQ data around extreme days (about $4.60 for Nov 5 and 20);
    3. symbolic regression for the compact law linking stress to danger.
* **Interrupted and superseded:** `2026-11-22-correlation-regimes/` (descriptive; README written).
* **2026-11-22: CROSS-ASSET STUDY DONE AND SENT** (`2026-11-22-cross-asset/`). The owner pasted an Arabic newsletter article (stocks, gold and bitcoin falling together; yields, yen carry, tech borrowing, deleveraging, no Fed rescue) and wrote "We never rly had these variables studied and integrated in our research."
  * **Market:** S&P 6,910 on Nov 20 (−8.6% from Nov 13; −11.6% from the Oct 6 peak). VIX 35.9 (highest close of the episode). Gold 3,515, bitcoin about 59k, NVDA 125.5 (−47.5% from peak), SOX −36%. 10y 4.91%.
  * **Findings:** phase 1 (Sep 3–Oct 5) = real-rate shock (10y +54bp; 2y +50; term premium +22; breakevens flat). Phase 2 (Oct 6–Nov 20) = dollar-funded forced selling of everything except Treasuries. Yen carry not visible. Gold's fall unexplained by yields in phase 2 (−16.3% vs +2.0%). Nov 5 = sector shock (gold up); Nov 20 = forced selling (gold −4.6%).
  * **Model added:** flow into asset j from a leveraged common holder = w_j(λ−1)λE·r_p → r_j = news_j + k_j·r_p.
  * **Forecast F-XA1:** gold outperforms SOX from the Nov 20 close to the Dec 22 close, 60%. Watch W-XA1: yen +2% in 3 sessions with the Nikkei −5%.
  * **Waiting for approval:** ES/NQ trades for Nov 5 and Nov 20, about $4.60 (quote 2026-11-22; top of book for Nov 4, 5, 19, 20 about $29). This answers the owner's Nov 16 question ("explain Nov 5 on a microstructure level"), which was interrupted.
* **REDIRECT 2026-11-16: the owner wants a model of what moves the price, built from the mechanism.**
  * Their words on the step-1 derivation: "This isn't really the kind of research I want." Asked what missed (four options, several allowed), they chose **"Not from first principles"** and **"Wrong subject"**. They did not choose "effects too small" or "too much reading".
  * My reading (mine, not theirs): the product must be a model, with equations and one formula tested across calm days, selloffs and expiries. Papers are inputs. Option pricing and trade structure is not the subject.
  * **Sent:** `2026-11-16-price-law/` (README and `out/price_law.png`). Three postulates → one equation.
    * Law A (linear impact): move = push ÷ (liquidity + G); constant multiplier 1/(1 − n), n = −G/L; runaway at L + G = 0.
    * Law B (square-root impact, my algebra): move = ½[√(m\*² + 4m₀²) − s·m\*], m\* = Y²σ²|G|/V, controlled by γ = |G|σ/V. Fixed amount, floor at m\* under negative gamma, pinning under positive gamma, no runaway unless capacity collapses. Checked numerically.
    * First estimate: γ ≈ 1% for the S&P, so the mechanical effect is a few percent at most. Inputs are rough; one paper's level would make it 100× larger if read literally (unit to check).
  * **Waiting for the owner's challenge.** If they agree, the first steps are: measure γ for SPY and TSLA; look at ten days (quiet and large, low and high gamma); then register the test that separates Law A from Law B.
  * **Not yet in the model:** time (hedging delay → momentum or reversal), G as a function of price (levels), and capacity that responds to the move (the crash equation).
  * **The MAP's queue steps 1 and 2 are on hold** (a note is in MAP.md). The step-1 pricing derivation below is kept as a record only.
* **QUEUE STEP 1, 2026-11-16: the derivation is written and sent; waiting for the owner's challenge** (`2026-11-16-is-it-priced/`). The owner said "Do it" to: read the papers in full, then send a one-page derivation **before any data is touched**. Nothing is pre-registered and nothing has been run.
  * **Seven papers read in full, with cards:** Gârleanu–Pedersen–Poteshman 2009; Ni–Pearson–Poteshman–White (2006 draft); Barbon–Buraschi 2021; Amaya et al. 2025; Adams et al. 2026; Dew-Becker–Giglio 2026; Garcia-Ares–Muravyev 2025.
  * **The derived judgement:** an option is cheap or dear mainly because of who is on the other side. The dealer whose hedging makes moves bigger in low gamma also sets the price and charges for it. So options should be **dearer** in low gamma (after a selloff) and fair or cheap in high gamma. The founding ladder table (§4i) already showed this.
  * **Predictions fixed before data:**
    * P1: realized ÷ implied is higher in high gamma than low, within a VIX band; gap 0.05–0.15.
    * P2: where customers write options, a fixed 30–60 day option gets about 3% cheaper from the Thursday before monthly expiry to the Monday after, and stays cheaper.
    * P3: where customers buy calls, the same days push the price up. TSLA's sign is unknown.
  * **Proposed order (not yet approved):** calibrate (realized ÷ implied should average 0.9–1.0 since 2012; signed vs unsigned gamma) → look at ten cases → the expiry test on SPY (47 expiries held) and TSLA (chains to be pulled again) → P1 goes into the structure table (queue step 2), because as a ratio test it can only detect a gap of 0.14–0.21.
  * **What I had wrong in the map:** I wrote that options are cheapest after expiry "because positioning clears". The papers say writers selling again is the cause, and the sign flips where customers are buyers.
  * **Facts to carry into all gamma work:** S&P market makers are long gamma 88% of the time; customers sell short-dated at-the-money options on both sides, so the public GEX sign is wrong at the short end; regime dates are about 2012 and May 2022; never pool across them.
  * **When the owner replies:** answer their challenges first. Only then write the pre-registration for the first approved test, push it, and run.
* **NEW ARCHITECTURE 2026-11-15** (the owner asked for it after the audit): `MAP.md` + `CATALOG.md` (generated by `2026-11-15-architecture/catalog.py`).
  * All 116 pieces of work are filed under seven questions: how big, where, which way, when, is it priced, when to get out, what breaks it.
  * **Key finding:** 33 items asked "which way?", 4 asked "is it priced?". The pricing question is the gap.
  * **Queue:**
    1. is the state priced (realized vs implied move by gamma state; free);
    2. structure and exit table in real option prices;
    3. daily state card and scoreboard;
    4. the owner's own fills (optional);
    5. liquidity pilot (about $35, quote first);
    6. earnings straddle by positioning.
  * **Waiting for the owner's go on step 1.** Before pre-registering it: read in full the papers on dealer gamma and option pricing, and write cards.
* **AUDIT DONE 2026-11-15** (`2026-11-15-audit/`). Its proposal was accepted in substance: the owner then asked for the recategorization above.
  * **Scope:** this thread began 2026-10-02 (the founding report `research/microstructure/REPORT.md`, then 81 studies). `Market_Data` main holds our option data; its `analysis/*` branches are another session's. `TeslaQuant` has no commits from this thread.
  * **Tally:** 55 tests → 7 robust, 19 leans, 29 nulls; 26 studies with no test. Every robust result is in dealer positioning, forced flows, or big-move physics.
  * **Forward record:** my adjusted calls 0.279 vs the options-implied odds 0.256 (12 forecasts, week of Nov 2). Level calls did better.
  * **Proposed purpose:** each day know the market's state and what it makes likely (how big, where, how fast); turn it into entry and exit rules for SPY and TSLA calls; score live against the options market's odds.
  * **Proposed theory:** three state variables: positioning (measured), liquidity (not measured), forced flow (partly).
  * **Proposed path:**
    * step 0: consolidate (purpose page, SPY playbook, scoreboard, to-do list from 79 to about 10);
    * step 1: prove or drop the traded rules in real option prices, and start a daily forward log;
    * step 2: measure liquidity from ES/NQ signed trades (about $35 first, quote first);
    * step 3: forced-flow calendar.
    * Parked: channels, indicators, analogs, politics, quirks, law replications that change no decision.
  * **Proposed method:** seven operating rules (three lanes; a gate before every test; look first; pre-register in the owner's units; one home for conclusions; a scoreboard; a weekly review). They are in the audit README.
* **Program on file (until the owner decides):** laws-first (PROGRAM.md, revision 2026-11-06). The theory is FOUNDATION.md: 16 laws in three layers.
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
  * the option-pricing set (2026-11-16): Gârleanu–Pedersen–Poteshman 2009, Ni et al. (2006 draft), Barbon–Buraschi 2021, Amaya et al. 2025, Adams et al. 2026, Dew-Becker–Giglio 2026, Garcia-Ares–Muravyev 2025.
  * **Not read in full, do not build on:** Baltussen et al. 2021; Chen–Joslin–Ni 2019; Lipson–Tomio–Zhang 2023; the published Ni et al. 2021.
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
0. **The owner's reaction to the price-law model** (`2026-11-16-price-law/`): is this the kind of research they want, and may I measure γ and look at ten days? The earlier step-1 pricing work is set aside.
0b. **Optional:** the owner's broker export of fills (queue step 4).
0c. Still open from the audit: the purpose sentence (accept or edit); the liquidity-pilot budget (about $35); whether to cross-check the other thread's SPY work in `Market_Data`.
1. **Approval for crash-law Part D:** ES/NQ signed trades, about $25–35. Quote first. (This is now step 2 of the proposed path.)
2. About $100 of order-flow data, for the fast-layer laws and the close.
3. Which agenda item comes next: 1 (how mechanical), 2 (0DTE/gamma), 3 (AI cross-impact) or 5 (distance to instability). The crash result points to 5 and 1.

## Scheduled scoring
* **F-XA1** (gold vs SOX, Nov 20 → Dec 22 close, 60%): score on 2026-12-22.
* M3 live forecast (Nov 5 shock): score after day 89, around 2027-03-16.
* Aftershock forecasts: 2026-11-13 scored (1 big day vs 0.63 forecast); next 2026-12-07, 2027-02-05.
* Year-end forecast: Nov 13 scored (754.37, inside 25–75%); next Nov 30, Dec 31.
* LR1 scored 2026-11-15. **Still overdue: EV1 and TP1.** Open: F2–F6. The ladder call (R2 on Oct 20) is due about Nov 17. A reminder is scheduled in this session for 2026-11-17 after the close to score EV1, TP1 and the ladder call together (desk lane, no new test).

## Reminders
* The owner should rotate the ThetaData key.
* The Scite citation tool needs a paid plan. Verify papers through Crossref or arXiv instead (scripts in `2026-11-06-literature-laws/`).

## Local data (gitignored; lost when the container resets)
* Scratchpad `fullread/pdfs2` and `fullread/txt2`: the seven option-pricing papers as PDF and text (lost on reset; links are in the cards).
* `2026-11-04-deferred-days/data`: ES trades for 2026-10-27; TSLA trades for 10-27 and 10-28; TSLA 10-level book for 10-28.
* `2026-11-02-orb-gamma/data`: Databento 1-minute bars for SPY, QQQ and TSLA, 2020–26.

## Repositories
* **Research:** this repo; push to `origin main`.
* **Figures for the owner:** the genovy repo, folder `today/`, branch `claude/price-lines-order-flow-bjaulu`.
