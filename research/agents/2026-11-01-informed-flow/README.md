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
