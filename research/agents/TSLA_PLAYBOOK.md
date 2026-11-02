# TSLA playbook: what we have tested, and what every TSLA read must include

*Owner (2026-11-02): "So what are the strong points here that we should keep integrated whenever we analyze TSLA?"*
*Built from INDEX.md and microstructure/REPORT.md. Each line links to its study. Update when a test changes the picture.*

## Tier 1: proven (passed a pre-registered test or replicated). Use every time
| # | Rule | Evidence | Study |
|---|---|---|---|
| 1 | **Freed = bigger moves, leaning up short-term.** Near-price OI (±5%, ≤ 45 days) in the bottom third of its trailing year gives 1.8× up-burst odds with vol/momentum/IV controlled (p < 0.01); down-bursts are not raised | §4s/4z | microstructure REPORT |
| 2 | **Full setup = freed + below own flip:** 39% up vs 17% down bursts within 3 sessions (reproduced). Over 10 sessions it is two-sided and volatile (worst dip median −9.4%) | §4w, pierce-and-reclaim | REPORT, 2026-10-16 |
| 3 | **Call gamma damps TSLA's next-day range** (classic dealer convention, p < 0.001). Above the flip and near big call strikes means smaller moves. Weaker since 2023 (p 0.10); put gamma inconclusive for TSLA | dealer-sign Part B | 2026-10-16-dealer-sign |
| 4 | **Forced moves fade, unforced moves stick:** moves made on low dealer-gamma days give back ~18% in 10 sessions; high-gamma moves extend (+8%) (p 0.002, 5/6 tickers) | forced-flow | 2026-10-24-forced-flow |
| 5 | **TSLA is flow-led** (return vs net aggressive flow ρ +0.48, p 0.013); SPY is liquidity-led. For TSLA, who is hitting the tape matters | flow-physics | 2026-10-27-flow-physics |
| 6 | **SPY drags TSLA about 2× on S&P down days ≤ −1%,** whatever TSLA's own gamma (no cushion). Always read SPY's state first | D1 | 2026-10-30-live-read |
| 7 | **Washed-out RSI leans up:** RSI in its bottom tenth → up-burst within 10 sessions 57% vs 40% (p 0.001, 115 episodes); RSI < 30: 74%. Mostly overlaps the options setup | technical-indicators A | 2026-10-16 |
| 8 | **A new 20-day closing low holds only 20% of the time** (usually goes lower); after a 1-ATR bounce it holds 66% | technical-indicators B | 2026-10-16 |
| 9 | **Earnings-reaction gap-ups fade more:** −0.31σ in the first hour; violent fades 25% vs 15% (passed out of sample, 12 stocks) | calendar-mechanics B2 | 2026-10-29 |
| 10 | **Gaps:** breakaway gaps fill less (55% vs 69%, p 0.04); ≥ 2% up-gaps fill same day 32%, within 5 sessions 59%. Up-gap open = day high only 11% | tsla-gap-states, open-fade | 2026-10-26, 10-28 |
| 11 | **Round numbers:** day highs stall just below round levels and lows just above (p 2e-15 / 5e-5) | positioning-tests P4 | 2026-10-26 |

## Tier 2: maps to compute every time (mechanics; they set levels and speed, not direction)
* **Own gamma map:**
  * flip and % to it; total gamma at spot and its slope above/below (a rising curve above = damping on the way up);
  * call/put walls; the top gamma strikes above and below; the short-gamma zone.
  * Now: walls 420, then 440–455; total gamma peaks ~455; flip ~375.
* **Freed percentile and the expiry schedule:** what share of gamma expires on each date; the next monthly opex. Deep-freed states rebuild above the 33rd pct in a median 4 sessions.
* **New call/put OI by strike** since the last burst: where the fuel sits.
* **Call-wall soft ceiling:** proven for SPY/QQQ (the high stops at the prior call wall ~1.4× as often; big runs past it half as common). **Untested for TSLA (GW1)**, so treat it as a lean.
* **SPY state:** flip, walls, GEX, ladder rungs, breadth. Then the TSLA ↔ SPY translator with bands (not points).
* **Calendar:**
  * TSLA reports Wednesday after the close, so the reaction is Thursday;
  * the VIX-expiry Wednesday, FOMC, month-end, monthly/quarterly opex.
  * These set *when* moves land, not their direction.

## Tier 3: leans (descriptive or near-miss). Mention with the caveat
* **Bursts vs the owner's 11 named bursts:**
  * fast continuations were already up 5%+ by day 3;
  * early dips on above-normal volume ran later (Jun '24, Oct '24); on normal volume they faded.
  * Buying aggression does not predict speed (snaps ~24%). [tsla-wall-flow]
* **Anatomy of a top** (16 tops, no single gauge passed):
  * stock buying peaks ~9 sessions before; new calls and call share ~5–7 before;
  * put skew bottoms (~10th pct) into the top; implied vol rises *with* price;
  * 6/16 tops ≤ 4 sessions before monthly opex.
  * After: IV −6 pts, call OI still rising, TSLA −11% in 10 sessions.
  * Composite score pending (BP1). [tsla-breaking-point]
* **Flat put skew at tops:** 9 of 14 mechanical tops ≤ 12th pct; 4 of 8 named tops ≤ 10th. Fear readings lean contrarian. [tsla-options-signal]
* **Call-skew richening during a run** means the run is less likely to hold (ρ −0.20, p 0.05). [permanence]
* **Deep freed above own flip:** up-burst 50% vs down 20% within 3 sessions (post hoc, 20 days). [tsla-freed-dpi]
* **High own gamma → next-day excess +1.1 pts vs low** (p 0.08). [D1 secondary]

## Tier 4: tested and failed. Do not use as signals
* Kimbal Musk's (or any single insider's) sales as top calls: 48 sales, no edge (memory keeps the hits). Other insiders: a −2-pt tilt, too small. [informed-flow]
* Option pricing or put/call ratios as forecasts beyond gamma + momentum (none pass, no OOS gain). [tsla-options-signal]
* "Smart money" flows: asset managers (they chase price), DIX, credit, the close-vs-open index. [informed-flow]
* Opens/highs/lows landing on top-OI strikes (1.04×, p 0.12). [gaps-and-walls]
* Hand-drawn channel lines as hold/break levels (touches hold 48–50% = placebo). [channel-microstructure]
* Up-gap fade predictors for TSLA (none pass). [open-fade]
* Weekday/calendar direction, the 13-week analog. [july-october-forensics, yearend-forecast]
* TSLA's own gamma cushioning an S&P selloff. [D1]
* "Lasting burst" confirmation and the first-passage formula. [flow-physics B]
* RSI at burst lows looking back. [technical-indicators A]

## The standard TSLA read (in this order)
1. **State:** price vs own flip (long/short gamma), freed percentile, full-setup flag, total gamma slope.
2. **Levels:** nearest walls above/below, top gamma strikes, new call/put OI by strike, the short-gamma zone. Round numbers nearby.
3. **Expiries and calendar:** what expires when; next opex; earnings (Wed after close → Thu); VIX expiry; FOMC.
4. **Market:** SPY's gamma state, walls, ladder, breadth. A ~2× drag on S&P down days.
5. **Flow:** aggression on the move (TSLA is flow-led); a forced (low-gamma) move means expect ~18% give-back in 10 sessions.
6. **Setups:** RSI bottom tenth; new 20-day low (holds 20%); 1-ATR bounce (holds 66%); gap type (earnings gap-ups fade, breakaway gaps fill less).
7. **Top watch (lean):** flat skew + IV rising with price + buying fading + near a wall + opex near.
8. **Tag every number** as proven / map / lean. State n, eras (R1 2020–21 / R2 2022+) and the data caveats:
   * the Databento single-venue close vs Yahoo;
   * open interest lags one session.
