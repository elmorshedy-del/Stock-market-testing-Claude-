# The breaking point: what is different on the day a TSLA rally tops, vs strong-rally days that keep going?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-02
**Type:** pre-registered event study (tops vs continuation days). Written and pushed before any top-day feature was computed.
**Owner's ask:** "The earlier put and call shows that traders pile into calls as the move goes higher, hoping for a higher move, and the opposite in a drop. So what makes 'the breaking point', when real demand flows exhaust and these options drop?"
**Note to the owner:** the call/put "chasing" readings in [tsla-options-signal](../2026-11-02-tsla-options-signal/) were leans, not passed tests. This study asks the sharper question: what changes *at the top*?

## The mechanism, in theory (what we test)
A call-driven rally is a feedback loop: customers buy calls → dealers short those calls hedge by buying stock → price rises → more call buying. It breaks when the fuel stops or the hedge reverses:
1. **Fuel exhaustion:** the *growth* of new call positions slows while price is still rising (the level stays high; the rate falls).
2. **Real-demand divergence:** stock buying aggression falls while price makes new highs.
3. **Complacency:** no one hedges, so put skew is flat.
4. **The hedge flips:**
   * dealers end up long gamma near big call strikes (the call wall), so hedging starts selling rallies;
   * time decay and expiry (charm, gamma roll-off near monthly opex) remove the dealer bid;
   * after the top, implied vol drops and call deltas shrink, so hedges unwind (vanna). That is "the options drop".

## Events (mechanical, so they cannot be picked to fit)
* **Data:** TSLA daily closes (split-adjusted), 2020-07 → 2026-10.
* **Tops:** peaks of a 15%-reversal zigzag on closes whose preceding up-leg is ≥ +30%.
* **Continuation controls:** days inside those same up-legs, at least 5 sessions before the top, whose prior 20-session return is ≥ +15% (strong-rally days that did not top).

## Features at day t (information available by t's close)
| | Feature | Source | Prediction at tops vs continuation days |
|---|---|---|---|
| F1 | Call-OI growth, 5 sessions | `td_gamma_TSLA.csv` call_oi | **lower** (fuel slowing) |
| F2 | Call share of option volume, 5 sessions | EOD chains | no prediction (level stays high) |
| F3 | Put skew, percentile vs trailing year | tsla-options-signal O2 | **lower** (complacency) |
| F4 | Stock buy aggression: last 5 sessions minus the prior 10 | 1-minute bars, bulk volume classification | **lower** (divergence) |
| F5 | Own-gamma (GEX z vs trailing year) | td_gamma | **higher** (dealers long gamma) |
| F6 | Spot vs the call wall, % | td_gamma | **closer to or above** the wall |
| F7 | Sessions to the next monthly opex | calendar | **fewer** (expiry near) |
| F8 | 30-day ATM IV change, 5 sessions | EOD chains | no prediction (spot-up/vol-up is common in squeezes) |

## Test
* **Statistic:** for each feature, the top-minus-control difference in medians. Mann–Whitney p; Holm across the 5 directional predictions (F1, F3, F4, F5, F7).
* **Post-top (descriptive), "the options drop":**
  * ATM IV, call share and call-OI growth over the 10 sessions after the top;
  * the same for the controls' following 10 sessions.
* **Power, stated now:** expect ~10–15 tops. Only large differences can pass; anything else is descriptive.
