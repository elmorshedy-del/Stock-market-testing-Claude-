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

---

## Deviation note
* The first run's Holm set included SPX by mistake; the plan says NDX and SOX only. Fixed in `extremes.py`.
* Holm over NDX and SOX: SOX p 0.050 → adj 0.10; NDX p 0.18 → adj 0.18. Both fail H1.

# Amendment A1 (pre-registered before computing outcomes): per name, not pooled
**Owner:** "It's not just today. But past weeks too and different stock … Stop lumping stats. Also include today individually."

* **Dashboard** (`dashboard.py`, descriptive, done): 26 AI-complex names plus SOX, SMH, QQQ, SPY and RSP. For each: today's 1-day z, 5-day z, 20-day z, the drop from the 60-day high in σ√t, and daily and weekly RSI, each ranked against **its own** history.
* **Per-name episodes** (`per_name.py`):
  * **Weeks:** for each name with today's 20-day z ≤ −1.5, the past days when its 20-day z was ≤ today's value (its own threshold). Declustered 20 sessions.
  * **Today:** for each name with today's 1-day z ≤ −2.5, the past days when its 1-day z was ≤ today's value. Declustered 20 sessions.
  * **Per episode:** 20- and 60-session forward return; whether a lower close came within 20 sessions; the best bounce within 20 sessions.
  * Every episode is reported individually, with counts per name. Nothing is averaged across names.
* **Today's index-level signature** (`per_name.py`): every past day with S&P 1-day z ≤ −4.0 and SOX 1-day z ≤ −3.0 (since 1994), listed one by one with its next 1/5/20/60-session moves.
* **Caveats:**
  * The names are today's survivors (no Nortel or Lucent).
  * Today's values are live intraday.
