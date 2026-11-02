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

## Results (`breaking.py` → `out/results.json`, `out/features.csv`, `out/daily.csv`; `figure.py` → `out/breaking_point.png`; $0)
**Events:** 16 tops (2020-08-31 → 2025-11-03; legs +32% to +128%) and 137 strong-rally control days.

| Feature | Tops (median) | Kept-going days (median) | p (registered direction) | Holm |
|---|---|---|---|---|
| F1 new call OI, 5-day growth | 1.8% | 2.6% | 0.52 | 0.57 |
| F2 call share of volume | 62% | 61% | 0.48 (two-sided) | — |
| F3 put-skew percentile | **11th** | 21st | 0.19 | 0.57 |
| F4 stock buying, last 5d − prior 10d | **−1.2%** | +0.4% | 0.25 | 0.57 |
| F5 dealer GEX z | 1.41 | 1.26 | 0.13 | 0.51 |
| F6 spot vs the call wall | −4.6% | −7.5% | 0.13 (two-sided) | — |
| F7 sessions to monthly opex | **10** | 12 | 0.10 | 0.51 |
| F8 ATM IV change, 5d | **+3.5 vol pts** | +1.2 | 0.11 (two-sided) | — |

* **No feature separates tops from strong-rally days that kept going** (Holm ≥ 0.51). Every directional prediction has the predicted sign; none is strong enough with 16 tops.
* **Counts at tops:**
  * skew at or below the 12th percentile at 9 of 14 tops;
  * buying fading at 11 of 16;
  * IV rising in the last 5 days at 13 of 15;
  * 6 of 16 tops within 4 sessions before monthly opex (about 24% of days are).
* **Event-time sequence (medians, descriptive):**
  * stock buying peaks ~9 sessions before the top;
  * new call OI growth (+7.5%) and call share peak ~5–7 sessions before;
  * put skew bottoms (~10th pct) from ~5 sessions before to the top;
  * implied vol rises into the top.
  * **Caveat:** buy aggression is classified from minute price changes, so part of its pre-top fade is simply the price slowing near a peak.
* **After the top ("the options drop"), 10 sessions, median:**
  * ATM IV −6.3 vol pts (vs +1.4 after kept-going days);
  * call share −2.6 pts (vs −1.3);
  * **call OI +6.9%** (traders keep buying calls into the fall);
  * TSLA −10.9%.
* **Now (Oct 30):** skew 88th pct (fear, not complacency), buying rising (+6.5%), IV +1.9 pts, Nov opex 15 sessions away, call share 54% (below typical tops). Only the price sitting at the 400 call wall looks top-like. **Not a breaking-point profile.**
* **Follow-up (TODO BP1):** a pre-registered composite top score (flat skew + rising IV + fading buying + near the wall + opex near), to be tested out of sample. The single gauges are too weak alone; a combination was not registered here and would be post hoc.
