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
