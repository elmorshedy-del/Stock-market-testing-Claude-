# Violent fade vs violent continuation after a gap-up following a big move: a microstructure teardown (pre-registration)

* **Owner, 2026-10-28:**
  * "This move isn't inherent to TSLA. It happens a lot after big moves (TSLA, AAPL, NVDA)… filter to violent fades like today's and big moves up, so kinda mirror TSLA this week… positioning, options gamma… also liquidity flow footprint."
  * The owner has a theory and asked me **not** to be biased by it. The metrics below come from the standard microstructure toolkit (auction imbalance, aggressor flow, book depth and imbalance, absorption, spreads, trade-size mix, dealer gamma), fixed before any data is pulled.
* **Focal pair (out of sample):** TSLA Oct 27 (gap +1.6% → ran +2.7%) and Oct 28 (gap +0.7% → −3.2% by 10:12). Oct 26 (news gap, held) is context.

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
