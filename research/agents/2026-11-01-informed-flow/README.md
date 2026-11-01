# Follow the informed money: which flows forecast the market, and can we piggyback on them?

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-01
**Type:** pre-registered test. Written and pushed before any flow data was downloaded.
**Owner's ask (2026-11-01):** "What flow is the biggest predictor, meaning sellers or buyers who are forecasting moves… not acting reflexively on price but either accumulating or genuinely offloading… instead of building our own model, piggyback on those who are trustworthy. Can we test this?"

## What the literature already says (prior, from published work)
| Who | Evidence | Level | Timeliness |
|---|---|---|---|
| **Short sellers (aggregate short interest)** | Rapach, Ringgenberg & Zhou (2016, *JFE*): the strongest known monthly predictor of market returns, in and out of sample (high short interest → low returns) | market | twice a month, ~1-week lag |
| **Corporate insiders, opportunistic trades** | Lakonishok & Lee (2001, *RFS*): aggregate insider buying predicts the market. Cohen, Malloy & Pomorski (2012, *JF*): only **non-routine** insider trades carry information; routine ones carry none | market and stock | Form 4 within 2 business days |
| **Firms themselves** | Baker & Wurgler (2000, *JF*): heavy equity issuance → low market returns. Ikenberry, Lakonishok & Vermaelen (1995): drift after buyback announcements | market (annual) / stock | slow |
| **Informed option buyers** | Pan & Poteshman (2006, *RFS*): put/call ratios from *opening, buyer-initiated* volume predict next-week stock returns | stock | needs signed open/close data (paid; our minute signing failed) |
| **Institutional shorts** | Boehmer, Jones & Zhang (2008, *JF*): institutional non-program short sales are the most informed | stock | needs proprietary flags |
| **Activists (13D)** | Brav, Jiang, Partnoy & Thomas (2008, *JF*): positive abnormal returns after 13D filings | stock | 10 days |
| Dealers hedging, vol-targeters, CTAs, stop-losses | Reflexive by construction: they trade *because* price moved | — | — |

## Candidates testable on free data now (market level, S&P 500)
1. **I — corporate insiders** (SEC Form 3/4/5 structured data sets, 2006Q1 → 2026Q3).
   * Open-market purchases (code P) and sales (code S), dated by **filing date**, counted as distinct insider–issuer pairs.
   * **I-opp (primary):** the net buy ratio buys/(buys+sells) over the trailing 21 sessions, opportunistic trades only.
     * Cohen–Malloy–Pomorski routine rule: an insider-month is *routine* if the same insider traded in the same calendar month in each of the 3 prior years.
     * The classification needs 3 years of history, so the series starts 2009.
   * **I-all (secondary):** the same ratio for all trades.
2. **A — asset managers in E-mini S&P 500 futures** (CFTC Traders in Financial Futures, weekly, 2006 →).
   * The 4-week change in net long as % of open interest (accumulating vs offloading).
   * Usable from the Friday release (Tuesday positions).
   * **L — leveraged funds** (hedge funds/CTAs): the same, secondary.
3. **D — SqueezeMetrics DIX** (dark-pool buy share, daily, 2011 →): the level z-scored against the trailing 252 sessions, usable the next session.

## Two properties measured for each candidate
* **Reflexivity:** the correlation of the signal with the *past* 20-session S&P return.
  * Trend-chasing = positive; buying weakness = negative; independent of price ≈ 0.
  * "Trustworthy" in the owner's sense means not trend-chasing.
* **Predictiveness:**
  * the slope of the forward S&P log return (h = 20 and 60 sessions) on the standardised signal, controlling for the past 20-session return;
  * inference by a 6-month block bootstrap (2,000);
  * Holm across the 3 primaries × 2 horizons (I-opp, A, D).

## Out-of-sample and "can we follow them?"
* **OOS R²** (Campbell–Thompson): an expanding-window regression starting after the first 5 years of each series, vs the historical mean.
* **Follow rule:** long the S&P when the signal is in the top third of its trailing 3-year range, flat otherwise.
  * Compare: mean 20-session forward return, top third minus bottom third; the share of years positive.
* **Era split:** R0 (before 2020) / R1 (2020–21) / R2 (2022+).

## Predictions written now
* **I-opp:** positive slope at 60 sessions (insiders buy before rises), mildly contrarian reflexivity (they buy dips). The strongest candidate.
* **I-all** weaker than I-opp, because routine and plan sales dilute it.
* **A:** no reliable prediction. Asset-manager futures largely reflect cash equitisation, and they follow flows.
* **L:** trend-chasing reflexivity (positive), little or contrarian predictive value.
* **D:** weak positive at 60 sessions. Our ladder found DIX helps time up-leg starts, not mean returns.

## Limits stated now
* Monthly-horizon market predictors have OOS R² of ~1–3% at best. With 15–20 years of data, a real effect can still fail the test (low power).
* Aggregate short interest, the literature's top candidate, has only ~2020+ free data via FINRA's API. That is too short to test here; logged as a follow-up.
* Insider classification is a simplified Cohen–Malloy–Pomorski rule; the 10b5-1 plan flag only exists from 2023.

## Amendment 1 (owner, 2026-11-01, written before any result was computed; the first run was stopped before producing output)
**Owner:** "SEC aren't reliable and they are really lagging indicators. I meant more like ones we can say: ok, these people know this will bounce in November to EOY, or these know it will sell."
* **Dropped:** I-opp and I-all (SEC Form 4). No insider numbers were computed or seen.
* **Kept:** A and L (CFTC asset managers / leveraged funds, weekly, Friday release) and D (DIX, daily).
* **Added, all timely and free:**
  * **C — credit investors:** the 20-session log change of HYG/IEF (high-yield vs Treasuries, daily, 2007 →). This is the "bond investors see it first" hypothesis.
  * **SMI — the "smart money index" (Hays):** SPY's last-60-minute return minus its first-30-minute return, summed over the trailing 20 sessions, from 1-minute bars (2018-05 → 2026-10).
    * The folklore: the open is emotional retail, the close is institutions.
* **Horizons:** 20, **40** (≈ Nov → year-end) and 60 sessions. **Primary = the 40-session horizon** for A, D, C, SMI (Holm across 4). The others are secondary.
* **"What they say now":** each signal's Oct 30 reading and tercile is reported. It is read as "positioned for a bounce" or "offloading" only if that signal passes.
* **Predictions:**
  * C: positive (credit improving → stocks rise), weak.
  * SMI: no reliable effect (folklore; our forced-flow study found last-half-hour momentum died after 2023).
  * A, L, D: as above.

## Amendment 2 (owner, 2026-11-01): one insider's timing. Written before any of the individual's trades was looked at
**Owner:** "We can also do an individual SEC test… like Elon's brother has been known to sell at intermediate tops."
* **Who:**
  * Kimbal Musk (SEC filer CIK 0001494731, a Tesla director): open-market sales (code S) of TSLA (issuer CIK 0001318605) on Form 4, from the SEC data sets 2006Q1–2026Q1 (2026Q2/Q3 not yet published).
  * Comparison groups: Elon Musk (CIK 0001494730) and all other TSLA insiders.
* **Sale episodes:** filings whose trade dates are within 10 sessions of each other are merged. The episode date is the first trade date; the actionable date is the session after the first filing date.
* **Outcomes** (TSLA daily close, split-adjusted, Yahoo):
  * **O1:** TSLA return from the episode date to +20 and +60 sessions.
  * **O2 (actionable, primary):** the same from the session after the filing.
  * **O3 "sold near a top":**
    * (a) the sale-day close is within 10% of the highest close from −20 to +60 sessions;
    * (b) TSLA falls ≥ 20% below the sale-day close at some point within the next 60 sessions.
* **Null:** for each episode, random TSLA sessions from the same calendar year with past-60-session return in the same tercile. Insiders sell after rallies, so this match removes "sold after a run-up" as an explanation. 10,000 permutation draws; one-sided p.
* **Prediction (owner's hypothesis):** Kimbal's O2 at 60 sessions is below the matched baseline, and his O3 shares are above it.
* **Power:** expected to be small (likely fewer than 20 episodes), so CIs will be wide.
  * A famous pattern can also be memory selection: we remember the sales before drops.
  * The test counts every sale.

## Results (`informed.py` → `out/informed.json`, `out/signals.csv`; `insider_tsla.py` → `out/insider_tsla.json`, `out/kimbal_episodes.csv`; figure `out/informed.png`; $0)
**Process notes:**
* The first run (with SEC insiders) was stopped by the owner before it produced output; it was replaced by Amendment 1.
* HYG/IEF was first fetched only from 2020 by mistake; it was re-fetched from 2007 as registered and C re-run. Only C changed.
* SEC 2026Q2/Q3 data sets are not yet published, so insider data ends 2026-03-31.
* The insider permutation null used 2,000 draws, not the 10,000 registered (the sample sizes make this immaterial).

### Timely flows (Amendment 1): **none passes** (primary = 40 sessions, Holm across 4)
| Flow | Reflexivity (corr with past 20-day S&P move) | Next 40 sessions, % per 1 sd [95% CI] | p | Holm | OOS R² (40) | Follow rule: top vs bottom third, next 40 sessions |
|---|---|---|---|---|---|---|
| **A** asset managers (E-mini, 4-week change) | **+0.39 (chase price)** | −0.72 [−1.48, −0.02] | 0.04 | 0.16 | +3.6% | **+0.90% vs +2.35%** (contrarian; 5 of 19 years) |
| **D** dark-pool buying (DIX z) | −0.07 (independent) | +0.11 [−0.59, +0.86] | 0.71 | 1.0 | +0.1% | +2.08% vs +2.18% |
| **C** credit (HYG/IEF 20-day change) | **+0.74 (moves with stocks)** | +0.02 [−1.21, +1.67] | 0.99 | 1.0 | −0.4% | +1.63% vs +2.19% |
| **SMI** close vs open (2018 →) | −0.14 | +0.63 [−0.71, +1.79] | 0.39 | 1.0 | +3.3% (40 points) | +1.84% vs +2.36% |
| L leveraged funds (secondary) | −0.30 (buy weakness) | −0.29 [−1.13, +0.41] | 0.45 | — | −2.1% | +1.89% vs +1.44% |

* **Asset managers are the closest to a signal, and it runs the wrong way for "follow them".**
  * They add after rallies (+0.39) and the market does *worse* after they add (−0.72% per sd, Holm 0.16).
  * Strongest in R1 (−2.9); **gone in R2 (+0.04)**.
* **DIX is genuinely price-independent but carries no forecast** (and its R2 sign is negative).
* **Credit simply moves with stocks** (+0.74); there is no lead.
* **SMI** was strong before 2020 (+2.7 per sd) and is ~0 since 2022.

### Kimbal Musk (Amendment 2): **no edge across all his sales**
| | Kimbal (48 sale episodes with follow-up) | Matched random days | p (owner's hypothesis) |
|---|---|---|---|
| TSLA 60 sessions after the filing (O2_60) | **+11.2%** | +7.7% | 0.87 (wrong direction) |
| TSLA 60 sessions after the trade (O1_60) | +9.7% | +7.7% | 0.75 |
| Sold within 10% of the local top (O3a) | 31% | 31% | 0.57 |
| A 20% drop within 60 sessions (O3b) | 27% | 24% | 0.33 |

* **The famous sales were real top-ticks:** Feb 2021 ($26M) −22%, Nov 2021 ($109M) −26%, Feb 2025 ($28M) −25%, May 2025 −12%, Dec 2025 −10%.
* **The forgotten ones were before big rallies:** Nov 2019 ($23M) +120%, Jun 2020 +125%, Apr 2023 ($20M) +32%, Nov 2024 ($15M) +63%.
* Most of his 2014–2018 sales were small monthly (plan-like) sales.
* **Memory keeps the hits.** The full record is a coin flip vs matched days.
* **Elon Musk** (7 episodes): 20 sessions after the trade −17% vs −6% (p 0.04). With n 7, dominated by 2021–22 tax/Twitter sales, this is not usable.
* **Other TSLA insiders** (336 episodes): TSLA 2.1 pts weaker over 60 sessions after the filing (+7.5% vs +9.6%, p 0.04); 20% drops 38% vs 34% (p 0.03). A small, real-looking tilt; too small to trade on a stock that moves ±30% in 60 sessions.

### Verdict
* **No visible, timely group "knows" the next two months.** The flows we can see in real time either react to price or carry no forecast. The one with a hint (asset managers) is a mild *contrarian* signal that has vanished since 2022.
* **The groups with published forecasting power are slow:** aggregate short interest, non-routine insider buying, net equity issuance. They work over months to years, are released with a lag, and are not the "they know November" kind.
* **Single famous insiders look prescient because we remember the hits.** Kimbal's full record shows no edge.
* **What we keep using instead** is our own tested structure: dealer gamma (call wall, flip), the ladder rungs, the forced-move fade. Their edges are in timing and size, not in someone else's knowledge.
