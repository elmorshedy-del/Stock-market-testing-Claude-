# July vs October 2026: is the same machine running, and will it produce the same rebound?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-01
**Type:** mechanism ledger (descriptive) plus conditional forecasts scored later. Gauges and rules fixed and pushed before any gauge was computed.
**Owner's framing (2026-11-01):** "Not historical forensics… this special case: whether the down forces were similar, and whether what softened it and caused the rebound should also hold in October. Are these two machines under the hood operating similarly, and will the product be the same?"
**Builds on:** [july-october-forensics](../2026-11-01-july-october-forensics/) (same calendar and state), dealer-sign, forced-flow, ladder R2/R4 (DIX/GEX), rsi-gamma-precedents (Oct 30 hedge decomposition).

## Phases (fixed)
* **July:**
  * down leg Jul 10 close (high) → Jul 29 close (low);
  * turn Jul 29 → Aug 4 close;
  * after: Aug 4 → Aug 14.
* **October:** down leg Oct 9 close → Oct 30 close (now). The turn has not happened.

## Gauges (daily, free data, same for both months)
| # | Force | Gauge | Down-force sign |
|---|---|---|---|
| G1 | Dealer gamma (amplifier vs damper) | SqueezeMetrics GEX; our engine's spot vs flip (July: `td_gamma_SPY.csv`; October: live maps) | GEX falling / below the flip |
| G2 | Institutional dip buying | SqueezeMetrics DIX (dark-pool buy share) | low DIX = no dip buyers |
| G3 | Fear and event premium | VIX; VIX9D/VIX (near-term event kink); VIX/VIX3M (term-structure inversion) | VIX rising, term structure inverting |
| G4 | Rotation out of megacap tech | QQQ/IWM, SMH/SPY, RSP/SPY | tech underperforming |
| G5 | Credit stress | HYG/IEF | falling |
| G6 | Rates / dollar | 10-year yield, DXY | rising yields / dollar |
| G7 | Systematic de-risking | SPY 20-day realized vol (vol-control); SPY vs its 50-day MA (trend/CTA proxy) | vol up, price under the 50-day |
| G8 | Fundamental news | megacap EPS surprises in the window (Alpha Vantage) | misses |
| G9 | Corporate bid | buyback blackout ends ~2 sessions after each megacap report (mechanical, independent of beat or miss) | blackout on |
| G10 | Calendar flows | turn-of-month (last session + first 3), scheduled vol events | — |

## Rules (fixed)
* **"Similar down force":** the gauge moved in the down-force direction in both down legs.
* **"July turn force":** the gauge moved in the rebound direction from Jul 29 to Aug 4 by more than one standard deviation of its own 4-session changes, 2020–2026 (|z| > 1). Discrete items G8–G10 are judged by whether they occurred.
* **October status of each July turn force:** present now / scheduled (with date) / absent.
* **Conditional forecasts written into the results before anything after Oct 30 is known.** They are scored on Nov 6, Nov 13 and Nov 20, e.g. "if the election VIX crush happens, SPY reclaims the flip by …".
* **Limits:**
  * one July episode; the ledger shows mechanism, not proof;
  * GEX/DIX are SqueezeMetrics' models;
  * October's engine flip comes from the live maps, not the full daily engine (`td_gamma` ends Oct 9).
