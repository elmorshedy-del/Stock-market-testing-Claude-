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

---

# Results (run ~12:00 ET; today's row live)

## H1 (index level, declustered fast-drop episodes)
* **Fails.** SOX: 12 episodes, p 0.050 (adj 0.10). NDX: 18 episodes, p 0.18. SPX (context): 23 episodes, p 0.47.
* Descriptive: after fast drops, **the low held for 20 sessions in SOX 2/12 and NDX 7/18 cases.** That is a bit more often than random days for NDX (base 18%) and about the same for SOX (base 15%).
* 60 sessions later: SOX up 10/12, NDX 14/18.

## A1-1 Dashboard: each name vs its own history (`out/dashboard.json`)
**Today (1-day, live)**
* TSM −4.2σ (0.1st pct), TSLA −3.9σ, QCOM −3.8σ, AMD −3.6σ, MU −3.3σ, PLTR −3.2σ, LRCX −3.3σ, NVDA −3.1σ, AMAT −3.1σ, VRT −3.0σ.
* Indices: QQQ −4.3σ, SPY −4.8σ, RSP −3.3σ.
* Not extreme today: MSFT, AMZN, AAPL, GOOGL, INTC.

**4 weeks (20-day)**
* LRCX −2.4σ (0.0 pct), AMAT −2.4σ, TSM −2.3σ, QQQ −2.4σ, SOX −2.3σ, MRVL −2.2σ, KLAC −2.2σ, MU −2.0σ, INTC −2.0σ.
* Not extreme: MSFT, AMZN, AAPL.

**Weekly RSI**
* Bottom 5% of own history: AVGO (3.7th pct), CRWV (1.3), GOOGL (1.9).
* Most others sit around the 15th–30th pct. The weekly frame is not washed out the way the daily is.

## A1-2 Per name (`out/per_name.json`, `out/speed_extremes.png`)
Each name's own past days or months as extreme as now, one episode at a time. Low held = no lower close within 20 sessions.

**Today-type days**

| Name | Past days this bad | Bounced ≥5% within 20 sessions | Low held |
|---|---|---|---|
| TSLA | 13 | 11 | 2 |
| TSM | 10 | 5 | **0** |
| NVDA | 30 | 18 | 5 |
| AMD | 32 | 20 | 3 |
| MU | 25 | 14 | 3 |
| QQQ | 11 | 5 | 2 |
| SPY | 11 | 6 | 3 |
| RSP | 21 | **3** | **1** |

**4-week-type moves**

| Name | Past months this bad | Bounced ≥5% within 20 sessions | Low held |
|---|---|---|---|
| QQQ | 5 | **5** | 1 |
| SOX | 12 | 10 | 2 |
| MU | 17 | 14 | 3 |
| NVDA | 12 | **6** | 2 |
| AMD | 26 | 12 | 2 |
| DELL | 10 | **10** | 3 |

## A1-3 Today's index signature (S&P ≤ −4σ and SOX ≤ −3σ), 16 days since 1994, each listed in `out/per_name.json`
* S&P higher 20 sessions later in 12/16.
* The 4 lower ones:
  * Lehman / TARP (2008-09-29): −23%.
  * COVID start (2020-02-24): −31%.
  * 2020-03-09: −3%.
  * 2018-10-24: −0.2%.
* The five most similar in shape (chips hit 2–3× the S&P), with the S&P's next day and 20 sessions:

| Day | Event | S&P next day | S&P 20 sessions | SOX 20 sessions |
|---|---|---|---|---|
| 1997-10-27 | Asian crisis | +5.1% | +7.9% | +2.8% |
| 2016-06-24 | Brexit | −1.8% | +6.4% | +10.5% |
| 2018-10-24 | Q4 2018 selloff | +1.9% | −0.2% | +2.9% |
| 2025-04-03 | tariff shock | −6.0% | +5.4% | +12.9% |
| 2025-10-10 | China tariff threat | +1.6% | +2.7% | +8.4% |

## Reading
* **Extreme:** yes, today and over 4 weeks, in most AI names, each vs its own history.
* **Indicative:** of a **bounce** within about a month, in most names. **Not of the low:** in nearly every name a lower close came first in most past cases (TSM 10/10, AMD 29/32, RSP 20/21).
* The tested entry filter remains the 1-ATR bounce ([technical-indicators](../2026-10-16-technical-indicators/)). Triggers off today's live lows: QQQ close ≥ 673.3, SMH ≥ 484.2, TSLA ≥ 361.5, NVDA ≥ 193.8, SPY ≥ 752.6.
* **Intraday breadth at 11:55:** RSP −2.3% and IWM −3.5% at new lows while QQQ bounced from 647.4 (10:50). The average stock is joining in, which is the 2000-lens watch item.

---

# 13:10 ET update (live; descriptive)
* The noon outputs are preserved as `out/*_1200.*`. `out/per_name.json` and `out/dashboard.json` are now the 13:10 rerun.
* **Correction:** the dashboard rounded percentiles to 0.1, so "never before" was printed for cases with a few precedents. Exact counts are in `out/exact_counts_1310.json`.

**Today, 1-day (σ = prior 60-day stdev)**
* SPY −6.0σ: 4 past days since 1994 (1997-10-27, 2007-02-27, 2018-02-05, 2018-10-10).
* QQQ −5.2σ: 4 past days since 1999 (2007-02-27, 2017-05-17, 2018-02-05, 2018-10-10).
* TSM −4.9σ: 4. TSLA −4.7σ: 7 (mostly earnings days).

**Past weeks**
* QQQ 20-day −2.6σ: 3 past days (2008-10-09, 2008-10-10, 2020-03-12).
* SMH 20-day −2.5σ: 3 (2016-01-15, 2018-10-24, 2020-03-12).
* SMH 5-day −3.7σ: 2 (2014-10-10, 2018-10-10).
* TSM 5-day −3.9σ: **0 since 1997**.
* LRCX 20-day: 2. AMAT 20-day: 3.

**After SPY's 4 days, one by one** (next day / 20 days / 60 days; deepest close in the next 20 days)

| Day | Event | Next day | 20 days | 60 days | Deepest close, next 20 |
|---|---|---|---|---|---|
| 1997-10-27 | Asian crisis | +5.8% | +9.0% | +10.0% | none lower |
| 2007-02-27 | Shanghai crash | +1.0% | +2.4% | +9.3% | −1.5% |
| 2018-02-05 | Volmageddon | +2.0% | +3.4% | −0.3% | −2.4% |
| 2018-10-10 | Fed hiking, yields up | −2.2% | +1.0% | **−7.7%** | −5.2% |

**Reading**
* At once-a-decade 1-day extremes after a calm stretch, the S&P was higher 20 days later every time (4/4).
* The lower lows came within 1–3 weeks and were small (−1.5% to −5.2%).
* The macro twin, Oct 2018 (a hiking Fed, rising yields, chips leading down), bounced and then broke lower into December.
* QQQ's 4-week move matches only crash months (2008, 2020).

`figure_1310.py` → `out/extremes_1310.png`.
