# TSLA live read (Mon Nov 2, before the open): the next gamma wall, and was the Oct 26-27 burst's buying different?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02 (written Sunday evening ET; the last close is Fri Oct 30)
**Type:** live read, descriptive. No new pre-registered test; the flow comparison is exploratory and labelled as such. $0 (ThetaData plus Databento bars already in hand).
**Owner's ask:** "What is the next strongest gamma wall for TSLA? My TA shows around 430. And what has aggressive flow this burst compared to before? I want to see if this will be a quick snap up or a slower one."

## Walls (`walls.py` → `out/walls.json`; engine unchanged)
* **Inputs:** OI dated Oct 30 (the Oct 29 close; Friday's trades arrive in Monday's file); IVs from the Oct 30 close; spot 399.81.
* **Dealer gamma by strike above spot ($bn per 1%):**
  * **420: 0.044** (the strongest);
  * then 450 0.038, 440 0.037, 410 0.036, 425 0.021, 435 0.019;
  * **430 is not in the top 8.**
* **Largest call OI ≤ 45 days above spot:** 400 28.7k, **450 23.2k, 420 22.8k**, 455 20.4k, 410 20.3k, 425 16.0k, 440 13.8k, 430 13.3k.
* **Total dealer gamma** rises from +$0.32bn at 400 to +$0.68bn at 430 and **peaks at ~455 (+$0.90bn)**. Going up, dealer hedging leans harder against rallies (classic convention).
* **Call OI added during the burst** (Oct 23 → Oct 29 close): **440 +26.7k, 420 +20.4k, 410 +19.1k**, 415 +13.5k, 430 +12.6k, 450 +12.6k, 425 +12.5k.
* **Reading:**
  * The next wall is **420**.
  * The owner's 430 sits inside a 420–440 band of resistance; it is a minor strike itself.
  * Above that is the 440–455 cluster.
  * The Monday Nov 2 expiry holds 4.7k calls at 450 (gone after Monday).

## Flow: the Oct 26–27 burst vs 70 earlier 2-day bursts of +7% or more since 2020 (`flow.py` → `out/flow.json`, `out/bursts.csv`; exploratory)
* **Method:** aggressor proxy = bulk volume classification on 1-minute bars (Easley, López de Prado & O'Hara 2012). It is a proxy, not exchange aggressor flags.
| | This burst | Percentile among earlier |
|---|---|---|
| Move | +9.5% | 53rd |
| Net buy share (aggression) | **13.0%** | **90th** |
| Volume vs 20-day | 1.46× | 81st |
| Share of the move from overnight gaps | 51% | 69th |
| Pause Oct 28–30 | −1.9% | 40th |
| Pause net buy share | +2.5% (dips bought) | 71st |
| Pause volume | 0.91× (light) | 41st |
* **What followed earlier bursts:**
  * Only **24%** "snapped" (+5% within 3 sessions after the 3-session pause), whatever the aggression: high-aggression 23%, low 26%. Aggression does not predict speed.
  * Pauses held with net buying ended 10 sessions later at a median +3.1%, vs −1.3% after pauses with net selling.
  * **The 4 closest look-alikes** (pause −5% to 0% with net buying): 0 of 4 snapped; all 4 cleared the burst high +2% within 10 sessions, taking 4–9 sessions; median best gain +10.5%. n is tiny.
* **Combined read:**
  * The buying was strong and the pause was healthy (dips bought on light volume, not distribution).
  * But neither history nor the gamma map points to a snap. The map gets *more* damped going up (dealer long gamma doubles from 400 to 430).
  * The likelier path is a **stair-step**: a stall near 420, then a push toward 440–450 over 1–2 weeks.
* **Caveat:** the new 420/440 calls were added during a rally, which suggests customer buying.
  * If dealers are short those calls, approaching them could accelerate (a squeeze) rather than damp.
  * Our dealer-sign test supports the damping convention for TSLA overall, but more weakly since 2023 (p 0.10).
  * The call-wall ceiling result is SPY/QQQ-only so far (TSLA untested: TODO GW1).

## Addendum: against the owner's own named bursts (`named.py`, `figure_named.py` → `out/named.csv`, `out/named_paths.csv`, `out/named_bursts.png`; descriptive, n = 11)
**Owner:** "By snap I meant going up fast. And I was talking about the bursts I had identified by date." Those are the 11 dates in `microstructure/burst_compare.NAMED`.

| Burst | Buying (net buy share) | Volume | Day 3 | Day 10 | Day 20 |
|---|---|---|---|---|---|
| Sep '25 | 16% | 2.0× | +7.5% | +11% | +4% |
| Jul '24 (call-wall break) | 15% | 2.3× | +9.4% | +7% | +0% |
| Oct '24 report | 14% | 2.5× | **−4.2%** (−7.5% by day 5) | **+19%** | +31% |
| **NOW, Oct 26–27 '26** | **13%** | **1.5×** | **−1.9%** | ? | ? |
| Nov '24 election | 8% | 1.7× | +10.6% | +14% | +31% |
| May '25 | 8% | 1.2× | +4.8% | +7% | −2% |
| Jun '24 | 5% | 1.2× | **−1.2%** | **+34%** | +35% |
| Oct '25 b | 5% | 0.7× | +2.4% | +7% | +2% |
| Nov '25 | 4% | 0.9× | +2.6% | +8% | +16% |
| late May '25 | 4% | 1.0× | −4.0% | −9% | −9% |
| Apr '25 report | 1% | 0.8× | +12.5% | +10% | +31% |
| Oct '25 a | 1% | 0.9× | −4.5% | +2% | +3% |

* **Going up fast (≥ +5% by day 3):** 4 of 11 (Jul '24, Nov '24, Apr '25, Sep '25). All were already up by day 3. Now is −1.9%, so the immediate fast path has not shown up.
* **Dipped by day 3:** 4 of 11.
  * The 2 on above-normal volume ran: Jun '24 +34% and Oct '24 +19% by day 10, with the run starting between days 5 and 8.
  * The 2 on normal volume faded or went flat: late May '25 and Oct '25 a.
* **Now** has 13% buying (3rd-highest of the 12) on 1.5× volume. Its closest twin is **Oct '24**: similar buying, about half the move from gaps, an early dip.
* Across the 11, buying aggression vs the day-10 gain has Spearman ρ +0.49 (n 11, not significant).
* **Read (a lean, not proof):** not a fast snap from here. If it follows the dip-then-run twins, the up-leg comes after a few more sessions of pause or dip. The gamma map's first stop is 420, then 440–455.
