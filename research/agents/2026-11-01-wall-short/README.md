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

## Results (`wall_short.py` → `out/wall_short.json`, trades in `out/trades_*_chosen.csv`, figure `out/wall_short.png`; $0)
**Chosen on 2020–23:** stop 0.25% above the wall, exit at the close, no filter. In-sample it was +0.060% per trade (n 72), and even that was not significant (p 0.20).

| Test | Result | Verdict |
|---|---|---|
| **T1** SPY 2024–26, untouched | +0.040% per trade, n 42, win 48%, p 0.24 | **fail** (positive, not distinguishable from 0) |
| **T2** QQQ 2020–26, same rules | −0.017% per trade, n 99, win 24% | **fail** |
| **T3** wall minus ordinary-strike short | +0.080 pts (ordinary short −0.027%, n 609), p 0.058 | **fail** (just short of 0.05) |
| **Persistence** | SPY 5 of 7 years positive, but R1 −0.011% per trade; **2022 alone is +5.0 of the +6.0% total** | **fail** (needs both eras) |

* **SPY full 2020–26:** +0.053% per trade (≈ $0.40 per share at 760), 114 trades (~17 a year).
  * Win rate 40%: average win +0.47%, average loss −0.23%.
  * Summed P&L +6.0% over 7 years at one share-unit per trade, max drawdown 3.8%.
* **Grid honesty:** only 9 of 32 configs were positive in-sample, but all 32 were positive in 2024–26 (+0.00 to +0.06% per trade, n 25–42).
  * That fits the stall effect being strong in 2024–26 (+15 pts), but the profits are too small to tell from 0 on 42 trades.
* **Verdict: not a tradeable candidate as a share short.** The wall stops the rise but does not push price down.
  * When SPY stalls there, the median close is only 0.07% below the wall; when it breaks, the stop is paid.
  * The edge is in the **missing upside tail** (big runs past the wall are half as common), not in a drop.
* **Mechanism-matched next test (GW5):** sell the upside instead of shorting the downside. That is a short 0DTE call or call spread struck at the wall, opened at the touch.
  * Call premium is priced off the normal upside tail, and the wall removes about half of that tail.
  * Needs 0DTE option quotes (ThetaData, not Databento). SPY has had daily expiries since late 2022 (~70 touches). Pre-register before running.
