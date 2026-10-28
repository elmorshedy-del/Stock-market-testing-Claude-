# Violent fade vs violent continuation after a gap-up following a big move: a microstructure teardown (pre-registration)

* **Owner, 2026-10-28:**
  * "This move isn't inherent to TSLA. It happens a lot after big moves (TSLA, AAPL, NVDA)… filter to violent fades like today's and big moves up, so kinda mirror TSLA this week… positioning, options gamma… also liquidity flow footprint."
  * The owner has a theory and asked me **not** to be biased by it. The metrics below come from the standard microstructure toolkit (auction imbalance, aggressor flow, book depth and imbalance, absorption, spreads, trade-size mix, dealer gamma), fixed before any data is pulled.
* **Focal pair (out of sample):** TSLA Oct 27 (gap +1.6% → ran +2.7%) and Oct 28 (gap +0.7% → −3.2% by 10:12). Oct 26 (news gap, held) is context.

## Amendment 3 (owner, during labeling: "narrow the fetch for big names for now"; written before any class label or microstructure data was viewed)
* **Why:** Databento was slow (~15 s per small request) and returned repeated 500 errors on 2018–2019 dates; the 13-symbol labeling fetch would have taken over an hour.
* **Universe:** TSLA, AAPL, NVDA (the names the owner flagged) plus QQQ for the market-wide label. 1,512 candidates on 814 dates.
* **Market-wide label:** the same rule. QQQ shares the class, or at least 2 of the 3 stocks do.
* **Labeling fetch:** `fetch_bars.py`, one request per date for all gapped symbols. Same XNAS 09:30–10:35 1-minute bars; results are cached per date.
* **Options (M5):** TSLA, NVDA and QQQ have local chains; AAPL has none (stated gap).
* **Sample:**
  * Every VF and SC event if the quoted pull fits $32. Otherwise a stratified draw (class × year, seed 0).
  * Plus 120 middle days for T3, drawn the same way.
  * Plus the focal days: 2020-09-02 for each of the 4 that gapped, and TSLA 2026-10-26/27.
* **Unchanged:** the classes, the metrics M0–M10, tests T1–T4, the Holm rules, and the $40 cap.
* **The other 9 symbols** are left for later. No claim is made about them.

## Amendment 2 (owner: "September 2 [2020] is a good example… market-wide, especially tech"; written before any microstructure data was pulled)
* **Period:** May 2018 – Oct 27 2026, the full XNAS.ITCH history, so 2020 is in. **QQQ is added** (13 symbols).
* **Classification source:** Databento XNAS 1-minute bars for 09:30–10:35 ET on each candidate day. Candidates are gap ≥ 0.5σ on Yahoo daily bars. The VF/SC rules are unchanged.
* **Market-wide label:**
  * a VF (SC) day is *market-wide* if QQQ is VF (SC) that day, or ≥ 1/3 of the 12 stocks with a qualifying gap share the class;
  * otherwise it is *single-name*.
  * T2 and T3 are reported for all events and split by this label.
* **Sampling:** if all VF + SC events exceed the budget, a stratified random sample (seed 0; by class × year) is drawn.
  * Focal days are always included: **2020-09-02, all 13 symbols**, and TSLA 2026-10-26/27/28.
* **Budget cap raised to $40** (owner: "consume any data if you need to").

## Amendment 1 (owner, before any data was pulled: "it doesn't have to be after certain days, use your own brain")
* **Setup:** a gap-up of at least **0.5σ** (open vs prior close, in units of the stock's 20-day daily σ). This scales the gap to each stock's volatility instead of a flat 0.5%.
* **No prior-run filter.** The prior 2-day return becomes a measured covariate (**M0**, added to T2, so T2 covers 8 measures).
* **Classes (VF, SC) are unchanged.**
* **Cost control:** if the full VF + SC set exceeds the $25 cap, events are drawn at random within class and stock (seed 0) until the cap. Stated before pulling.

## Events (original definition, superseded by Amendment 1)
* **Universe:** 12 Nasdaq-listed mega caps: TSLA, AAPL, NVDA, AMD, META, MSFT, AMZN, GOOGL, AVGO, NFLX, MU, ORCL.
  * Days Nov 2023 – Oct 2026 (Yahoo hourly bars give the first hour).
* **Setup:**
  * gap ≥ +0.5% (open vs prior close);
  * after a big move: the prior 2-day return in the top fifth of the stock's trailing year.
* **Classes, from the first hour (09:30–10:30), in units of the stock's 20-day daily σ:**
  * **VF, violent fade:** first-hour low ≤ open − 0.75σ AND first-hour high ≤ open + 0.25σ.
  * **SC, violent continuation:** first-hour high ≥ open + 0.75σ AND first-hour low ≥ open − 0.25σ.
* **Counts:** **91 VF, 91 SC** (all other setup days form the "middle" group, used only for T3).

## Data (Databento XNAS.ITCH, Nasdaq = primary listing venue; licensed, `data/` gitignored)
* Per event day:
  * trades with aggressor side 04:00–10:35 ET (premarket + first hour);
  * the 10-level book (mbp-10) 09:25–10:35;
  * the opening-cross imbalance (NOII) 09:20–09:31.
* **Options:** engine chains (ThetaData, local) for TSLA, NVDA, MU, MSFT events up to Oct 14 2026: the gamma map at the prior close.
* **Stated limit:** Nasdaq's book and trades are a share, not all, of each stock's volume.

## Metrics (fixed)
**Before the open (could act on them at 09:30):**
* **M1 premarket drift:** last premarket price vs the premarket high, in σ; and the premarket high's time.
* **M2 premarket flow:** buy-aggressor share of premarket volume; retail-size share (trades < 100 shares) of premarket volume.
* **M3 opening-cross imbalance:** the last NOII before 09:30, signed (buy +) imbalance shares / paired shares.
* **M4 gap size in σ.**
* **M5 options** (where available):
  * open above vs below the largest positive dealer-gamma strike within ±5%;
  * dealer total gamma at the open price (sign);
  * the distance from the open down to the next strike with large positive gamma (a gamma "gap" below), in σ.

**First 5 minutes (could act on them at 09:35):**
* **M6** aggressor delta, % of volume.
* **M7** book imbalance (bid − ask depth within 0.5% of mid) / total, time-averaged; plus ask depth and bid depth, each ranked within the stock.
* **M8 absorption:** price progress per 1,000 shares bought aggressively, ranked within the stock.
* **M9** quoted spread (bp).
* **M10** trade-size mix: retail-size share of volume.

## Tests (fixed)
* **T1 Anatomy (descriptive):** average VF vs SC paths, 04:00–10:30, of price, cumulative delta, depth imbalance, spread and trade-size mix.
* **T2 Before-the-open separation:**
  * M1–M5 (7 measures), VF vs SC, rank-sum with bootstrap by event.
  * **Holm across the 7. A measure passes at Holm p < 0.05.** AUC reported.
* **T3 Early-warning value (at 09:35):**
  * Across all setup days (VF + SC + middle), Spearman of M6–M10 (6 measures) with the 09:35 → 10:30 return in σ (outcome window excludes the measurement window).
  * Within-stock ranks.
  * **Holm across the 6. Passes at Holm p < 0.05.**
* **T4 Focal pair:** TSLA Oct 27 vs Oct 28 placed on the T1 and T3 distributions (Oct 28 data when Databento publishes it).
* **Budget:** capped at $25 of Databento credit.

---

# Results (written after the run; everything above was fixed before the data was viewed)

**Data:**
* 1,512 gap-ups of at least 0.5σ in TSLA, AAPL, NVDA and QQQ, May 2018 – Oct 27 2026, labeled from Nasdaq 1-minute bars: **196 VF, 203 SC, 1,113 middle**.
* Sample: 305 drawn (stratified, seed 0). The pull stopped at the cap after **270 events: 83 VF, 79 SC, 109 middle**. The order was shuffled first, so the 35 dropped are a random cut.
* Per event: Nasdaq trades 04:00–10:35, the 10-level book 09:25–10:35, and the opening-cross messages.
* Options maps for 166 TSLA/NVDA/QQQ events; AAPL has none.
* Databento: $39.00 for the pull plus about $0.3 for labeling, inside the $40 cap.

**Deviations, stated:**
* T2 is Holm-corrected over 10 measures and T3 over 7. Both are more than the pre-registered 8 and 6, so stricter.
* M3x (the average opening imbalance 09:25–09:30), the weighted and price-controlled T3, and the first-5-minute table are **exploratory**. I added them after seeing that the last pre-open imbalance message is usually exactly balanced, and that VF/SC are over-sampled.
* σ = each stock's 20-day daily σ. For TSLA now about 2.35%, so 0.25σ ≈ 0.6% ≈ $2.40.

## T2: before the open, nothing separates a violent fade from a violent continuation (null)
* **No measure passes.** Holm p ≥ 0.42 for all 10:
  * the prior 2-day run (M0);
  * premarket drift from its high and the high's time (M1);
  * premarket aggressor share and retail-size share (M2);
  * the opening-cross imbalance (M3);
  * gap size (M4);
  * the three options measures (M5).
* **The nearest misses:**
  * VF gaps are slightly bigger (AUC 0.60, raw p 0.04).
  * The VF premarket high comes earlier (median 274 vs 300 minutes after 4am, raw p 0.07).
* **Same null within the market-wide and single-name splits.**
* **The premarket looks the same.** Both classes drift up into the open from about −0.3σ below it at 04:00. Premarket buy share is 0.50 vs 0.52. The last opening-cross message is balanced on most days.
* **Gamma doesn't separate them either.** Both open 1.7σ above the pre-open flip (medians), in long dealer gamma (86% of events), with similar gamma 1σ below the open ($0.16bn vs $0.14bn).

## T3: at 09:35 the first 5 minutes carry the signal, and it lives in the price
* **Pre-registered (unweighted), three pass:**
  * first-5-minute aggressor delta (M6): ρ +0.40;
  * price progress per 1k bought (M8): ρ +0.46;
  * book imbalance (M7): ρ −0.18, Holm p 0.014.
* **Weighted back to the population of all gap-ups** (VF and SC are over-sampled and defined on the same hour, which inflates ρ):
  * M6 +0.20 (95% CI 0.08–0.34, date-block bootstrap);
  * M8 +0.22;
  * M7 −0.06 (CI −0.19 to +0.06, no longer distinguishable);
  * the first-5-minute return itself +0.24 (CI 0.11–0.35).
* **After removing the first 5 minutes' price move, no flow or book measure adds anything:**
  * M6 +0.08 (CI −0.06 to +0.22), M8 0.00, depth and spread within ±0.08;
  * M6's price-controlled ρ stays near zero in 2018–21 (+0.09) and 2022–26 (+0.07), and in each symbol (−0.05 to +0.15, every CI spans 0).
* **Mechanism:**
  * Aggressive flow moves price at once (Kyle-style), so by 09:35 the price already shows what the delta shows.
  * VF first-5-minute delta is **−9%** vs **+25%** for SC; price −0.30σ vs +0.30σ.
  * Cumulative delta keeps diverging to 10:30: −4% vs +7% of first-hour volume.

## The book: liquidity leans against the move, then builds behind it (descriptive)
* **In the first 5 minutes, the resting book leans against the move:**
  * VF bids within 0.5% are deeper than asks ($0.76M vs $0.59M median);
  * SC asks are deeper than bids ($1.03M vs $0.51M).
  * Passive orders are contrarian: the fade runs *through* a deeper bid, and the continuation lifts *through* a thicker offer.
  * Example, AAPL 2020-09-02: $6.0M of bids vs $0.48M of asks, yet −0.77σ in 5 minutes on −52% delta.
* **Over the hour, depth builds behind the move:** SC bids rise to about 1.2× their first-5-minute level; VF offers rise to about 1.1×, mostly in the second half hour.
  * On Nasdaq's lit book, a "sell wall" on fade days is a *result* of the turn (sellers re-offering above a falling price), not something visible at 09:30.
  * Hidden or off-exchange orders are not seen here (stated limit).
* **Spreads are the same in both classes:** first-5-minute median 2.2bp (VF) vs 2.6bp (SC), decaying to about 1.2bp by 10:00.

## Practical table (exploratory, weighted to all gap-ups ≥ 0.5σ)
| 09:30–09:35 move | share of days | next 55 min mean | P(down) | P(down > 0.5σ) | P(up > 0.5σ) |
|---|---|---|---|---|---|
| ≤ −0.25σ | 16% | −0.08σ | 58% | 20% | 18% |
| −0.25 to 0 | 36% | −0.04σ | 51% | 14% | 7% |
| 0 to +0.25 | 33% | +0.13σ | 42% | 4% | 16% |
| ≥ +0.25σ | 16% | +0.27σ | 28% | 4% | 27% |
* **A strong first 5 minutes protects:** only 4% fall more than 0.5σ afterwards.
* **A weak first 5 minutes is a warning, not a verdict:** the rest of the hour turns two-sided with a down tilt (20% further drop vs 18% rebound).

## T4: focal days
* **2020-09-02 was market-wide VF** for AAPL (first-hour low −3.6σ), NVDA (−2.3σ) and QQQ (−1.4σ).
  * TSLA's gap that day was under 0.5σ, so it is not in the setup.
  * QQQ's first 5 minutes were −0.26σ on −11% delta; it fell another −0.39σ to 10:30.
* **TSLA Oct 26 (SC):** first 5 minutes +0.63σ, delta +51%, ask depth twice the bid; next 55 minutes +0.66σ. Textbook SC.
* **TSLA Oct 27 (middle):** +0.16σ / +30% delta; next +0.32σ. The big run came after 10:30.
* **TSLA Oct 28 (Yahoo consolidated bars; Databento not yet published):**
  * first 5 minutes −0.33σ (410.21 → 407.02), then −0.83σ more to 399.09 by 10:29;
  * first hour +0.07σ / −1.35σ, a VF by shape;
  * the gap (about 0.3σ) was below the 0.5σ setup, so it sits just outside the tested population.
  * It fits the table's bottom row and the pattern: the move was visible by 09:35, not at 09:30.

## Verdict
* **For the owner's question** ("can I tell at the open to sell held calls?"): none of the pre-open tape, auction, book or gamma measures does it on these four names.
* **The earliest usable read is 09:35:** the sign and size of the first 5 minutes.
  * Flow and book add nothing beyond it; they matter because they move the price at once.
* **On the owner's theory** (sell wall plus a pocket underneath):
  * No visible wall at the open. On fade days asks are thinner than on continuation days.
  * No gamma pocket difference.
  * Offers do stack up above the price *after* a fade starts, which may be the wall seen on the tape.
  * Whether hidden or iceberg selling sits at the high is untested (needs MBO; see TODO G4).
* **Limits:**
  * Nasdaq is a share of volume.
  * Four symbols only (the other 9 were parked by Amendment 3).
  * The table is exploratory and needs the forward check (TODO F6).
