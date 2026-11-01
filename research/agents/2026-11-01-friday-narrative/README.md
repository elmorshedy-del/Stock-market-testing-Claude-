# Friday Oct 30 from the open to the close: a narrative built from pre-registered evidence

* **Owner, 2026-11-01:** "Days like this offer windows in the world of microstructure. Can we make a 'narrative' for it from start to end based on evidence. Not post hoc."
  * Also open from the owner: "How did u know it's election hedges", the time-decay question, and "why did the bounce start … was it a highly liquid level so selling through it became harder".
* **How this avoids post hoc:**
  * Each chapter below states a claim, a measure, a baseline and a falsifier. All of it was written and pushed **before** pulling the microstructure data: Databento ES and SPY trades, Arca book and closing imbalance, OPRA put trades, and the SPY IV term structure.
  * A chapter is told as written only if its evidence passes. A chapter that fails is reported as failed, and the narrative changes.
* **Already seen before this pre-registration (cannot count as confirmation):**
  * SPY 1-minute path: open 761.40, low 750.36 at 14:52, close 755.71.
  * VIX 5-minute path: high ~23.5 around 14:30.
  * The engine's dealer-flow model (2026-11-01-rsi-gamma-precedents).
  * The 750 put wall and the pocket.
  * Thursday night's ex-ante calls (2026-10-30-live-read).
  * ES daily volume.
* **Baseline days:** the 5 prior sessions, Oct 23–29, same clock windows.
* **Cap:** Databento spend ≤ $15 (costs checked first: ES trades ~$0.67/day, Arca book ~$1.05, Arca imbalance ~$0.01; OPRA limited to named contracts).

## Chapters, claims and falsifiers
* **C1. The open, 09:30–10:30: was the drop aggressive selling, with futures leading?**
  * Measure: ES aggressor-signed volume (buy − sell, front month), cumulative over the window, as a z-score vs the baseline days' same window. Also the lead-lag: correlation of 1-minute ES signed flow with the **next** minute's SPY return vs the reverse.
  * Claim: z ≤ −1 and ES leads.
  * **Falsifier:** z > −1, which would make it a gap with no aggressive selling.
* **C2. The grind, 10:30–14:30: persistent, mechanical-looking selling in thin liquidity?**
  * Measure (a): lag-1 autocorrelation of 5-minute ES signed flow vs the baseline days.
  * Measure (b): price impact per signed contract (Kyle's λ, a 1-minute regression of ES return on signed flow) vs the baseline days.
  * Claim: (a) above the baseline median and (b) above the baseline median.
  * **Falsifier:** both at or below the median.
* **C3. The low, 14:30–14:55: did resting liquidity at 750 and fading selling stop the fall?**
  * (a) **Arca bid depth** within $0.50 above 750.00 during 14:40–14:55 vs bid depth at the same distance from price in other windows of the day. Claim: larger (top quartile of the day). **Falsifier:** not in the top half.
  * (b) **Exhaustion:** ES signed flow per minute in the 15 minutes before the 14:52 low vs the 30 minutes before that. Claim: less negative. **Falsifier:** selling at its most intense into the low.
  * (c) VIX peaking before the price low: already seen, reported only.
* **C4. The rebound and close, 14:55–16:00: buyers arriving, or sellers stepping away?**
  * (a) ES signed flow in the 10 minutes after the low. Claim: positive, so buyers arrived. **Falsifier:** at or below zero, meaning the rebound came from absent sellers.
  * (b) **Month-end closing auction** (Arca imbalance feed). Claim: buy-side imbalance into the close. This is pre-stated from pension rebalancing: in October stocks −0.9% vs long bonds +5.6%, so rebalancers buy equities. **Falsifier:** sell-side imbalance.
* **C5. Was there an election premium? (owner's question)**
  * Measure: SPY implied variance for the single-day interval covering election night (Nov 3 → Nov 4 expiry), from ATM implied vols per expiry on the Oct 30 close, vs the neighbouring single-day intervals.
  * Claim (as I implied last week): ≥ 1.5× the neighbours.
  * **Falsifier:** below 1.5×, in which case the VIX rise was not specifically election hedging.
* **C6. Put monetization at the low (owner's bounce question)**
  * Measure: OPRA trades in near-money SPY puts (Oct 30 expiry 745–760; Nov 20 expiry 740–760). Share of put volume traded at or below the mid (customer selling) in 14:30–15:00 vs 13:30–14:30, and volume per minute.
  * Claim: more selling-to-close and higher volume at the low.
  * **Falsifier:** put trades skew to buying at the low.
* **Answer kept separate from the evidence: time decay.**
  * Dealers short puts hedge by holding short stock.
  * Over time an out-of-the-money put's delta shrinks, so dealers **buy back** stock. The model said time decay was a small net *buyer* on Friday (+$1.2bn).
  * This is mechanics, not tested here.
