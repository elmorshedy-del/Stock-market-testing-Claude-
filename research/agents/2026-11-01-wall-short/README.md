# Shorting SPY at the prior day's call wall: is there a persistently profitable day trade?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-01
**Type:** pre-registered strategy test (this file pushed before any strategy P&L was computed)
**Builds on:** [gamma-phase-diagram](../2026-11-01-gamma-phase-diagram/) iterations 3/3b. The prior call wall stops the day's high 43% vs 28–31% at matched ordinary strikes; QQQ replicates; the effect is smaller since 2022 after a VIX adjustment.
**Owner's ask (2026-11-01):** "A better day trade would be to short at that level. Can u optimize a strategy where this is a persistently profitable one."

## Why not just optimise
* There are ~23 call-wall touches a year (159 in 2020–26). A free search over stops, targets and filters on 159 trades will always find a config that looks great in-sample.
* **The design is therefore:**
  * a small grid fixed now;
  * selection on 2020–2023 only;
  * one chosen config tested untouched on 2024–2026, on QQQ, and against a placebo level;
  * every config's result reported, not just the winner.

## Trade rules (all fixed now)
* **Universe:** SPY, regular session 09:30–16:00, 1-minute bars. Days 2020-01-03 → 2026-10-09, the last prior wall on file.
* **Setup (known before the open):** the prior session's call wall K (`td_gamma_SPY.csv`, largest call OI ≤ 45 days) sits above today's open by 0 < (K − open)/open ≤ 1%. That is where 92% of the touches happened.
* **Entry:** a sell limit at K, filled at the first minute whose high ≥ K + $0.01 (it must trade through, to be conservative on fills).
  * No entry after 15:30. At most one trade per day.
* **Stop:** a buy stop at K × (1 + s), filled at max(stop, that bar's open) + $0.01.
* **Exit:** whichever comes first:
  * the stop;
  * the target, a buy limit at K × (1 − t), filled when the low ≤ target − $0.01;
  * the exit time.
* **Bar ambiguity (conservative):**
  * if a bar touches both the stop and the target, the stop counts first;
  * on the entry bar, a high ≥ the stop counts as stopped.
* **Costs:** 1 bp round trip (spread + fees), plus the $0.01 stop slippage above. Intraday short: no borrow cost.
* **Return:** per trade, in % of K. A no-trade day is 0.

## Grid (32 configs)
| Parameter | Values |
|---|---|
| Stop s above K | 0.15%, 0.25%, 0.40%, 0.60% |
| Exit | target 0.25%; target 0.50%; no target, exit at 15:59; no target, exit 60 minutes after entry |
| Filter | all setups; only if the prior session's spot was above its gamma flip (dealers net long gamma, where hedging damps moves) |

## Selection and tests
* **Selection (in-sample 2020-01 → 2023-12):** the config with the highest mean net return per trade among configs with ≥ 30 trades.
* **T1 out-of-sample, time:** the chosen config on SPY 2024-01 → 2026-10. Pass: mean net > 0, one-sided p < 0.05 (bootstrap over trades).
* **T2 out-of-sample, asset:** the same config, unchanged, on QQQ 2020–2026 (QQQ's own walls). Pass: mean net > 0, p < 0.05.
* **T3 placebo:** the same config shorting the nearest ordinary $5 strike above the open (not the wall, same ≤ 1% band), SPY 2020–26.
  * Pass: wall mean − placebo mean > 0, p < 0.05.
  * This separates "the wall" from "fading any intraday push into a round number".
* **Persistence:** SPY net P&L positive in ≥ 5 of the 7 calendar years (2026 partial), and in both R1 (2020–21) and R2 (2022+).
* **Verdict:** **tradeable candidate** only if T1, T2 and T3 all pass and persistence holds. Otherwise report what fails.
  * Even then it goes to a live forward log before any real size.
* **Power, stated now:**
  * ~65 out-of-sample SPY trades with a per-trade SD of ~0.35% give an SE of ~0.045%. T1 can only detect a mean of ≳ 0.08% per trade.
  * QQQ adds ~140 trades.
  * A true edge smaller than that can pass in-sample and still fail T1. That would be "not proven", not "disproven".
* **Not tested here:** options (0DTE puts at the wall), which would need option-price data. That comes only if the share version passes.
