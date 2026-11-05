# The drop is fast. Do extreme sigma moves and RSI predict a bounce, or a bottom?

**Agent / session:** Claude, for the owner, 2026-11-05 ~13:00 ET. **Pre-registered at commit:** the commit that first adds this README.

**Owner:** "In multiple analyses we said this is going too fast. So RSI and sigma moves must be extreme and indicative."

**Builds on:** [technical-indicators](../2026-10-16-technical-indicators/). RSI level and divergence did *not* separate true lows from false ones; a 1-ATR bounce off the 20-day closing low was the useful filter.

## Today (live, about 12:45 ET)
| | Day | 5-day move | RSI14 |
|---|---|---|---|
| NDX | −4.9% = −4.3σ (0.25th pct) | z −3.1 (0.33rd pct) | 29 (1.4th pct) |
| SOX | −8.9% = −3.5σ (0.27th pct) | z −3.3 (0.14th pct) | 28 (1.3rd pct) |
| S&P | −3.2% = −4.7σ (0.22nd pct) | z −2.4 | 37 |

## Definitions (fixed before computing outcomes)
* **σ:** the stdev of daily returns over the prior 60 sessions.
* **5-day z:** 5-day return ÷ (σ·√5).
* **Event (primary, "fast drop"):** 5-day z ≤ −3.0.
  * Secondary events: 1-day z ≤ −3.5; RSI14 ≤ 30.
  * Episodes: events within 20 sessions count once (the first day).
* **Indices:** NDX (1990–), SOX (1994–). S&P (1990–) is context only.
* **Outcomes, from the event close:**
  * forward 5, 10, 20 and 60-session returns;
  * **low held:** the event close is not undercut by any close in the next 20 sessions;
  * further drawdown: the minimum close over the next 20 sessions vs the event close.
* **Base:** all days.

## Tests
* **H1:** episode forward 10-session return > the unconditional 10-session return.
  * Circular shift of the episode dates, 5,000 draws, one-sided. NDX and SOX separately; Holm over the two.
* **H2, descriptive:** share of episodes where the low held, vs the all-days base, with a bootstrap 90% CI.
* **Splits, descriptive:**
  * index above vs below its 200-day average at the event;
  * crash or bust years (2000–02, 2008) vs the rest.
* Small n means "can't say"; every result is reported with its n.

## Reproduce
`python extremes.py` → `out/extremes.json`
