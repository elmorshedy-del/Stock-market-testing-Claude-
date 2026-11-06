# Liquidity landscape: price as motion through levels of liquidity (plan + first observations)

**Agent / session:** Claude, for the owner, 2026-11-06.
**Type:** observation first, then pre-registered tests. Nothing is tested yet.

## The owner's idea, restated
1. **Liquidity sits at price levels.** It comes from resting orders, old positions and their stops, and option hedging. Price moves fast through thin zones and slows in thick ones.
2. **A pause is absorption.** The aggressive side keeps hitting a level and passive liquidity soaks it up, so volatility compresses. The move resumes only when the absorbing liquidity is used up.
3. **A top or bottom is exhaustion.** The aggressive side runs out; it is not that a line holds.
4. **Each move has a volatility signature.** Its speed, or energy, sets how long its pauses last. Up bursts and down bursts follow the same rules.
5. **Open question:** can the signature be seen in advance, for example from options (implied-vol term structure, skew, dealer gamma)?

## Physics framing (the architect's version)
* **Price is a particle pushed by order-flow imbalance (the force) through a medium whose density is liquidity.**
  * Speed is roughly imbalance ÷ density. This is the same structure as the square-root impact law, Δp ≈ σ√(Q/V).
  * Absorption: passive density at a level is at least the incoming aggressive flow.
  * Exhaustion: the force goes to zero.
  * Option hedging changes the medium: negative dealer gamma thins it (faster legs); positive gamma thickens it (pauses and pins).
* **Measurable state variables:**
  * aggressive imbalance (delta);
  * passive depth near the price;
  * efficiency, i.e. the price change per unit of aggressive volume (low efficiency = absorption);
  * a liquidity map from history (volume or time at price) and from options (open interest and gamma by strike);
  * volatility measured in volume-time.
* **Candidate predictions (to be fixed and pre-registered after observation):**
  * P1: fast legs cross thin zones; pauses form in thick zones or at big option strikes.
  * P2: in pauses, efficiency collapses. Continuation comes after absorption volume reaches some fraction of the leg's aggressive volume (a volume-time clock).
  * P3: bottoms show exhaustion: aggressive selling dries up while price stops falling, or a climax of selling with no progress.
  * P4: the same rules hold for up moves.
  * P5: pause length scales with the leg's volatility signature.
  * P6: options (gamma regime, term-structure inversion) give the signature in advance.
* **Already known in this repo:**
  * Low gamma makes reactions bigger (macro-trigger A1, passed).
  * Lows run through put walls (2 of 29 stopped exactly there).
  * Fear is self-exciting (aftershocks).
  * Leveraged-ETF close flows are priced early (forced-flows).

## First observation: Nov 5, 2026 (price only, Yahoo 1-minute bars)
* **SPY:**
  * The first 90 minutes were impulsive, with 30-minute ranges of 1.4–1.8%.
  * From midday the range compressed to 0.25–0.7%, and price hovered at 734–740 for about 3 hours.
  * That is the strike where dealers were most short gamma (735), inside the dense put block (720–740).
  * SPY had not closed a 5-minute bar below 750 in the prior 20 sessions. So the stall was not at old traded liquidity; it was at the options level.
* **SOXX:**
  * The whole day traded below its prior-20-session range, with no recent liquidity memory there.
  * Morning 30-minute ranges were 3.5–4.3%, compressing to 0.8–1.7% at midday around 134–136.
  * The selling resumed in the last hour (2–2.6% ranges), when the leveraged-ETF close flow was due.
* **Yahoo volume can't be trusted for absorption.** The 1-minute bars sum to 497M SPY shares on Nov 5, with giant isolated 15-minute bars at near-zero price change. This matches the known Yahoo cumulative-volume glitch. Reading absorption needs real trade data.

## Data needed
* **Must have: footprint (trades with aggressor side, giving delta and volume at price).**
  * CME ES + NQ futures: $2.82 per day (quote for Nov 5).
  * Nasdaq SOXX / NVDA / QQQ: $0.42 per day.
* **Strongly useful: 10-level order book.**
  * ES + NQ: $16.20 per day.
  * SOXX / NVDA / QQQ: $6.29 per day.
* **Have already or free:**
  * per-strike open interest and gamma (ThetaData);
  * implied-vol term structure and skew indices (Yahoo: ^VIX9D, ^VIX, ^VIX3M, ^VVIX, ^SKEW);
  * closing-imbalance quotes from forced-flows.
* **Not now:** full tick history (ES + NQ 2024 to now: $726).
* **Proposed phase-1 purchase, awaiting the owner's approval:**
  * footprint for about 10 case days (ES + NQ about $28; stocks about $4);
  * order book for 3 key days (about $49).
  * Total about $80, with exact per-day quotes before buying.

## Self-prompt (the plan)
1. **Observe.** Write down what is seen at each leg, pause and turn, with no statistics, for 6–10 episodes in both directions:
   * Nov 5 and Oct 30, 2026;
   * Apr 3–9, 2025, including the Apr 9 up-burst;
   * Aug 5, 2024;
   * Mar 9–24, 2020;
   * a big up-burst such as Nov 10, 2022.
   * For each episode, use footprint, book depth, gamma levels and the prior volume profile.
2. **Formalize.** Turn the recurring observations into 3–5 measurable definitions (thin zone, absorption, exhaustion, volatility signature) and pre-register them.
3. **Test widely.** Run them on a broad sample, out of sample.
4. **Model.** Build a liquidity-landscape simulator: imbalance through a density field made of book depth plus option hedging. Test its predictions of where pauses form and how long they last.
