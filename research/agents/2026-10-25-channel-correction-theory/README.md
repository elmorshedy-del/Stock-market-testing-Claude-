# What lines up before this channel's corrections? A theory, not a statistic

* **Owner, 2026-10-25:** "It won't make sense to back that far. This is a certain type of trade and environment. Even if the statistics is not robust enough. It's enough if we just establish very reasonable explanations for what is happening. If we have enough things lining up together that all can fall in a nice 'theory' or explanation."
* **Scope:** only the post-2022 channel (2022-10-13 to 2026-10-23).
* **Events** (from [spy-channel-reversion](../2026-10-25-spy-channel-reversion/)):

  | Type | Top dates |
  |---|---|
  | Three main corrections | **2023-07-31, 2025-02-19, 2026-01-27** |
  | Three minor pullbacks | 2024-03-28, 2024-07-16, 2025-10-28 |

* **Not a significance test.** The filter is consistency plus mechanism: an indicator counts only if it lines up across events **and** fits a causal chain with the others.

## Method (fixed before computing)
**Indicators, daily**, known at that day's close. Percentiles are trailing 252 days.

| Group | Indicators |
|---|---|
| **Leadership / rotation** | semis vs SPY (20-day log change of SMH/SPY); AAPL stock-specific 20-day return (residual vs S&P ex-AAPL); AAPL–S&P 20-day correlation; equal weight vs cap weight (RSP/SPY, 20 days); small caps vs SPY (IWM/SPY); defensives vs SPY (XLP/SPY) |
| **Breadth** | share of a 41-stock large-cap panel above its 50-day average; average pairwise 20-day correlation of that panel |
| **Dealers / flows** | SqueezeMetrics GEX percentile; DIX percentile; SPY dealer gamma (`gex_classic`) percentile (through 2026-10-09) |
| **Volatility structure** | VIX percentile; VIX/VIX3M (term structure); VVIX percentile; SKEW percentile; 20-day correlation of daily VIX change with the S&P return (spot-vol; normally about −0.8, and rising toward 0 means "spot up, vol up") |
| **Cross-asset** | TLT, UUP, BTC and GLD 20-day returns; HYG vs IEF (credit); KRE vs SPY (banks) |
| **Stretch** | S&P vs its 50-day average; S&P 20-day return |

**Event reading:**
* Each indicator's average over the 10 sessions ending at each top.
* It is shown as a z-score against its distribution on channel days when the S&P is within 3% of its 252-day high, i.e. against normal "near the high" days.

**"Lines up":** |z| ≥ 0.5 in the same direction before all 3 main corrections **and** at least 5 of the 6 events.

**Theory step:** the indicators that line up are arranged into a causal chain, and any that fit no chain are reported as loose ends.

**Today:**
* The same reading for the 10 sessions ending 2026-10-23.
* A similarity score: cosine similarity of today's z-profile to the average pre-top profile, over the indicators that line up, compared with every other channel day near the high.

## Round 1 results (`dossier.py`, `posthoc_types.py`; `out/profile.csv`, `out/lineup.csv`, `out/dossier.json`, `out/types.json`)
**Nothing lines up by the rule. No indicator is |z| ≥ 0.5 in the same direction before all 3 main corrections:**
* not in the 10 sessions before the top;
* not in the earlier window (sessions t−30 to t−11; post hoc check).

| Near misses | Before the 3 main corrections | Before all 6 events |
|---|---|---|
| VVIX high | 3 of 3 | 4 of 6 |
| Gold up | 2 of 3 | 4 of 6 |
| SKEW high | 2 of 3 | 4 of 6 |

**The three corrections looked different beforehand.** Cosine similarity of their 23-indicator pre-top profiles:
* Jul 2023 vs Feb 2025: −0.16
* Jul 2023 vs Jan 2026: −0.02
* Feb 2025 vs Jan 2026: +0.31

What each top looked like:
* **Jul 2023, "exhaustion":**
  * S&P stretched above its 50-day average (+1.1), broad breadth (+1.4), low VIX (−1.2);
  * spot and vol rising together (spot-vol correlation +1.5);
  * strong credit and banks; high GEX.
* **Feb 2025, "rotation under the surface":**
  * semis already lagging (−1.1, after DeepSeek), AAPL decoupled (correlation −1.1), defensives leading (+0.9);
  * gold (+1.2) and bonds (+0.9) bid; VIX elevated (+0.6); credit weakening (−0.8);
  * S&P below its usual stretch (−0.8).
* **Jan 2026, "broadening on a thin cushion":**
  * semis (+1.2), equal weight (+1.2), small caps (+1.4), defensives (+1.4) and gold (+1.5) all up;
  * AAPL lagging (−1.6);
  * low dealer gamma: GEX −1.4, SPY gamma −0.9, DIX −0.9.

**Today** (10 sessions to Oct 23) is most similar to **Feb 2025 (+0.47)** and the opposite of Jul 2023 (−0.46):
* semis lagging (−1.3), AAPL decoupled (−1.5), defensives leading (+1.7), small caps lagging (−1.3);
* breadth weak (−1.5), credit weakening (−1.5), low GEX (−1.1), VIX term structure up (+0.9), SKEW high (+1.1);
* S&P below its usual stretch (−1.4).
* Unlike Feb 2025, gold (−1.3) and bonds (−0.3) are not bid.

## Amendment 1 (round 2, owner-aligned and still channel-only): dip anatomy. Written before computing.
* **Why:** no common setup precedes the tops. The question a trader faces right now (S&P −2.5% from its Oct 6 high) is different: **is this dip the start of a correction, or a dip the channel will buy?** The channel has many more dips than corrections, so both outcomes are well represented.
* **Episode:** the first close ≥ 2% below the running 252-day high (high made on or after 2022-10-13), outside an open episode.
  * Outcome: **correction** if a close ≥ 5% below that high comes before a new high; **bounce** if a new high comes first.
  * An episode ends when its outcome is decided.
* **Reading:** each indicator's mean over the 5 sessions ending on the episode's first day, as a z-score as before.
* **Separates:** at least 5 of the 6 corrections on the same side of the bounces' median, including all 3 main corrections, with the corrections' mean differing from the bounces' mean by ≥ 0.5 SD.
* **Theory step and today:** as before. Today's episode began on the first close ≥ 2% below the Oct 6 high.

**Added by the owner before the dip anatomy was computed:** "Also that margin and debt thing u said before that can drive moves." Two indicators join the list, and are also reported for the pre-top profiles:
* **margin debt growth:** FINRA margin debt, year on year, from the macro panel ([channel-reversion-macro](../2026-10-15-channel-reversion-macro/), which found margin-debt surges before reversions after 2010).
* **margin debt vs prices:** margin-debt year-on-year growth minus the S&P's year-on-year growth for the same month. Leverage growing faster than prices is the cleaner proxy that [forced-flow](../2026-10-24-forced-flow/) D suggested.
* Both use a 2-month lag (FINRA publishes about three weeks after month end), so each day sees only what was public.
