# Deferred days: Oct 27 into flow-physics (TODO D4) and TSLA Oct 28 into gap-teardown (TODO G1 / T4)

**Agent / session:** Claude, claude.ai session for the owner, Wed Nov 4.
**Owner (Nov 4):** "There were two tests tho we delayed cuz we said we can't be sure until tsla data released … just do it."

**Why now:** both studies froze their measurements and predictions before their data existed, and left these days for when Databento published them. They are published now. This folder applies the **original measurements unchanged** to the missing days.
* The original folders are not edited.
* Their scripts are imported, or their formulas copied with a pointer to the source line.

## Pre-registration (fixed before any data is pulled)

### D4: Oct 27 in flow-physics ([2026-10-27-flow-physics](../2026-10-27-flow-physics/), registered @ bdc698c)
Data (Databento; quotes checked before each pull; cap $3 for D4 + G1 together):
* ES front month (ESZ6) trades, 09:30–16:00 ET (GLBX.MDP3);
* ES order-by-order book (MBO) around the day's high;
* closing-auction imbalance messages (SPY: ARCX.PILLAR; TSLA, GOOGL, AMZN, NVDA, AVGO, MSFT, AAPL, META, QQQ: XNAS.ITCH), 15:45–16:00 ET;
* TSLA Nasdaq trades (XNAS.ITCH), 09:30–16:00 ET.

Measurements (each as defined in flow-physics):
* **A1/A2 (ES and TSLA):** session delta % of volume, Kyle λ (5-minute), Hawkes branching n median. Placed against the 16 ES and 26 TSLA baseline sessions in `out/a_daily.csv`. Descriptive.
* **A4 (ES, a flip-wick day):** the buy/min ratio (final 0.1% before the high vs the 30 minutes before) and the absorption ratio.
  * **Prediction, as registered:** exhaustion (buy/min ratio < 1), not absorption.
  * **MBO, as for Oct 20:** net new offers/min at the high vs 10 placebo swing highs that day.
* **A5 (closing auction):** the first imbalance message at or after 15:50:00 for each of the 10 symbols. Signed % of the day's dollar volume vs the 15:50→close return (Yahoo 5-minute bars).
  * **Question:** did SPY print a sell imbalance at 15:50 on Oct 27?
  * The 10 new symbol-days are added to the 260 and the pooled Spearman is recomputed (registered pass: ρ > 0, one-sided p < 0.05, bootstrap by day).
* **A6 (TSLA, the 400 break):** buy-aggressor events per second in the 60 s after the first print above 399.90 vs the 60 s before. Compared with the same measure at the day's other round-dollar crosses (stop-cascade signature: a burst right after the cross).

### G1: TSLA Oct 28 in gap-teardown ([2026-10-28-gap-teardown](../2026-10-28-gap-teardown/), registered T4)
Data (XNAS.ITCH, as `pull.py`):
* trades 04:00–10:35 ET;
* 10-level book 09:25–10:35;
* opening imbalance 09:20–09:31.

Measurements:
* `features.feats` unchanged: M1–M3, M6–M10, and the 09:35→10:30 return in σ.
* **T4 as registered:** place Oct 28 (and Oct 27, already in `out/features.csv`) on the T1 distributions (VF vs SC, TSLA and all names) and on T3 (within-TSLA ranks of M6–M10 vs the 09:35→10:30 outcome).
* Descriptive. Oct 28's gap (~0.3σ) sits below the 0.5σ setup, as noted in the original.

No new statistical test is added. Everything is a placement or the registered A5 recount.
