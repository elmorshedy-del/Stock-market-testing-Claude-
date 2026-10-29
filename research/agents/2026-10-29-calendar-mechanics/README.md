# Calendar mechanics: tracing seasonal weakness to the forced flow behind it (pre-registration)

* **Owner, 2026-10-29:**
  * "There is underlying weakness (and strength) that patterns with particular times or conditions… September wouldn't be consistently one of the weakest months… somewhere out there is able to trace it back to its origin… the generalized rule that controls the mechanics."
  * Then: "Do it, and if there are any earlier tests we delayed that go well with these, do them too."
* **The working rule:**
  * Equity markets are inelastic (Gabaix-Koijen 2021). So prices drift when a large, scheduled, price-insensitive flow meets a temporary absence of the marginal buyer. The calendar schedules both.
  * Related: Hartzmark-Solomon (predictable price pressure from dividend reinvestment), Etula et al. 2020 (month-end cash needs), Lou 2012 (flow-induced trading).
* **The motivating fact** (descriptive, written up before this pre-registration, S&P 500 1950–2025):
  * September's weakness is all after the third Friday: +0.24% before vs −0.97% after (t −3.3, 38% of years up).
  * The 5 sessions after a quarterly expiry average −0.14% (39% up) vs +0.11% (58% up) after monthly expiries.
  * This came from trading lore, so it may be data-mined. **The 1950–2025 S&P late-September result is not re-tested here.** Every test below uses other years, other markets, or the timing differences between candidate causes.
* **Builds on:** [forced-flow](../2026-10-24-forced-flow/) (month-end and Russell moves are given back; the expiry-size *volatility* law failed), [gap-context](../2026-10-29-gap-context/) (the earnings-gap fade lead), and TODO items E1, E2, N4.

## Candidate mechanisms and their clocks
| Mechanism | Clock | Exists since |
|---|---|---|
| Index-option expiry hedges (support into expiry, released after; quarterly is largest) | 3rd Friday (moves between the 15th and 21st) | US index futures 1982, options 1983 |
| Buyback blackout (the largest net buyer steps away) | about 2 weeks before quarter-end, a fixed date about the 16th | SEC Rule 10b-18, Nov 1982 |
| Corporate tax date (cash drained from the system) | the 15th of Mar/Apr/Jun/Sep/Dec | always |
| Pension and balanced-fund quarter-end rebalancing | last days of the quarter | grows after 1980s |
| Japan's index expiry (SQ) | 2nd Friday | Nikkei futures 1988 |

## Part A: index tests (daily log returns; Holm across A1–A8; date-block or year-block bootstrap, 10,000; two-sided p; pass at Holm p < 0.05)
* **A1, pre-1950 out of sample** (S&P 500, 1928–1949; no derivatives, no buybacks):
  * Mean daily return in September sessions after the 3rd Friday, minus all other sessions.
  * Prediction: none for the sign. If negative, the late-September weakness predates expiry and buybacks.
* **A2, other markets** (DAX 1988–2025, FTSE 1984–2025, Nikkei 1970–2025; pooled, year-block bootstrap):
  * The same late-September contrast.
  * Prediction: negative (replication of existence).
* **A3, the era test** (S&P):
  * The late-September contrast in 1983–2025 minus the same in 1950–1982.
  * Prediction: negative if expiry or buybacks (both born 1982–83) are the origin.
* **A4, quarterly vs monthly expiry × era** (S&P):
  * (Mean of the 5 sessions after a quarterly 3rd Friday − mean after a monthly one), in 1983–2025 minus in 1950–1982 (placebo era, when the 3rd Friday meant nothing).
  * Prediction: negative.
* **A5, the clock race** (S&P 1983–2025, quarterly months):
  * Sessions on or after the 16th but on or before the 3rd Friday ("blackout and tax date have started, expiry has not") vs sessions after the 3rd Friday to quarter-end.
  * Statistic: mean(between) − mean(after). Expiry origin predicts > 0 (support persists until expiry); fixed-date origins predict ≈ 0.
* **A6, Japan's clock** (Nikkei 225, 1989–2025, quarterly months):
  * The mean of the 5 Tokyo sessions after the US 3rd Friday, minus the 5 after Japan's own SQ (2nd Friday).
  * Local-expiry origin predicts > 0 (weakness after the local SQ); US-flow origin predicts < 0.
  * Two-sided; the sign tells which.
* **A7, dose** (SqueezeMetrics, 2011–2025, all monthly expiries):
  * Spearman of the GEX change from the session before expiry to the session after (gamma rolled off) with the next-5-session S&P return.
  * Prediction: ρ > 0 (a bigger roll-off means a weaker week). Note: the forced-flow study's volatility version of this failed.
* **A8, liquidity drain** (Treasury daily cash balance, 2009–2025):
  * Spearman of the weekly change in the Treasury General Account with the same week's S&P return, non-overlapping Wednesday-to-Wednesday weeks.
  * Prediction: ρ < 0 (cash pulled out of the banking system weakens stocks).

## Part B: back to single names (Holm across B1–B5)
* **Events:** gap-ups ≥ 0.5σ (gap-teardown definitions, labels and outcomes Y1/Y2), extended to all 13 names by fetching the 9 parked names' first-hour bars (Databento, about $0.2). AVGO and ORCL earnings dates permitting.
* **B1, post-quarterly-expiry window:**
  * Gap-ups in the 5 sessions after a quarterly 3rd Friday vs all others.
  * Prediction: Y1 lower. All 13 names.
* **B2, the earnings-gap fade, out of sample:**
  * The gap-context C7 contrast (earnings-reaction gap-up vs other gap-ups) on the 9 parked names only.
  * Prediction: Y1 lower (now directional, from the 4-name lead).
* **B3, the call-wall cap, out of sample:**
  * Gap-context C1 on MSFT and MU (the parked names with local chains).
  * Prediction: Y1 lower. Low power, stated.
* **B4, the earnings fade mechanism (E1):**
  * Earnings-reaction gap-ups with local chains (TSLA, NVDA, MSFT, MU, 2020–2026).
  * Spearman of "unwind pressure" with Y1. Unwind pressure = near-the-money call OI (strikes from the prior close to +10%, ≤ 45 days, OI dated the reaction day) per 20-day average share volume × the ATM implied-vol drop (report-day close to reaction-day close).
  * Prediction: ρ < 0. Explanatory, not predictive (the vol drop is known only after).
* **B5, pre-earnings selling into the close (N4):**
  * Stocks with a report after that day's close: the 15:30–16:00 return on the report day vs the same stock's other days (stock-demeaned). 12 stocks, Yahoo 60-minute bars, Nov 2023 – Oct 2026.
  * Prediction: lower.

## Amendment 1, Part C: the hemisphere test (owner: "do it"; written after Part A's results, before any southern-hemisphere return was computed)
* **Why:** Part A found late-September weakness of the same size before 1983 (−16bp/day) as after (−16), and in the DAX, Nikkei and FTSE. So index expiries and buybacks are not its origin. Two old, global candidates remain, and they predict opposite things for the southern hemisphere:
  * **Seasonal risk aversion** (Kamstra-Kramer-Levi 2003; disputed by Kelly-Meschke 2010): weakness starts as nights lengthen after the *local* autumn equinox. Southern markets should be weak in late **March**.
  * **A global calendar or flow origin** (fiscal half-years, post-summer issuance, global funds): southern markets are weak in late **September** too.
* **Windows:** the 10 sessions starting on or after the equinox date (Mar 20, Sep 22).
* **Statistic:** mean daily log return in the local-autumn window minus the local-spring window. Year-block bootstrap (10,000), two-sided. **Holm across C1–C4.**
  * **C1, Australia** (All Ordinaries, 1985–2025): late-March window minus late-September window. Mood predicts < 0; a global calendar predicts > 0.
  * **C2, Australia's local component:** the same, on All Ordinaries returns after removing the prior US session's S&P return (full-sample OLS beta). Australia trades after the US close, so this strips the imported US move. Mood predicts < 0.
  * **C3, southern pooled:** Australia 1985–2025, New Zealand 2003–2025, South Africa (All Share) 2012–2025. Same statistic as C1.
  * **C4, northern control:** S&P, DAX, FTSE, Nikkei (late-September window minus late-March window). Both views predict < 0; this checks that the equinox window captures the northern effect.
* **Excluded in advance:** Brazil and Argentina (low latitude, where the mood theory predicts little; Argentina's inflation distorts index returns).
* **Reading, fixed now:**
  * C1 or C3 < 0 supports a seasonal-mood origin.
  * C1 or C3 > 0 supports a global calendar or flow origin.
  * Near 0 with C4 < 0 means the northern effect is not mirrored (inconclusive for mood).

## Data
* **Indices:** S&P 500 daily from 1927 (Yahoo); DAX, FTSE and Nikkei daily (Yahoo).
* **Positioning and cash:** SqueezeMetrics DIX.csv; Treasury Daily Treasury Statement operating cash balance (fiscaldata.treasury.gov). The account was called "Federal Reserve Account" until 2021-09, then "TGA".
* **Earnings:** dates and timing from Alpha Vantage.
  * Every company here reports after the close. Alpha Vantage's few "pre-market" flags for these names (for example MSFT July 2021/22/23) are treated as after the close.
* **Gaps and chains:** gap labels from the Databento first-hour bars; local ThetaData chains.
* **Spend:** about $0.2 of Databento.

## Limits stated in advance
* Calendar windows overlap (quarter-end, expiry, blackout, tax date), so A5 and A6 are the discriminating tests and A1–A4 establish existence and era.
* There are about 76 Septembers per index, so power is modest.
* Japan's SQ also aligns with Japan's own fiscal calendar, so A6 separates local from US timing, not expiry from every local factor.

---

# Results (written after the run; Parts A and B pre-registered @ 89dcdd6, Part C @ 8d8be48)

**Deviations, stated:**
* **A7:** the outcome window is sessions 2–6 after expiry, because session 1 holds the "after" GEX reading and GEX moves with spot. The pre-registered wording was ambiguous; this is the uncontaminated reading.
* **B3:** "next 3 trading days" used weekdays.
* **B4:** Yahoo volume is split-adjusted, so it was divided back by later splits to match pre-split option contracts.
* **Labels:** 4,583 gap-up events across the 13 names, from Databento first-hour bars ($0.2).

## Part A: where late-September weakness comes from (Holm across A1–A8; units bp per day)
| test | estimate [95% CI] | raw p | Holm | reading |
|---|---|---|---|---|
| A1 S&P 1928–49, late Sep vs other days | −17.7 [−47.0, +8.2] | 0.20 | 1.0 | same sign and size before derivatives or buybacks existed (noisy) |
| A2 DAX + FTSE + Nikkei, late Sep | −14.3 [−25.0, −3.1] | 0.014 | 0.10 | exists abroad: DAX −24, Nikkei −13, FTSE −7 |
| A3 era: 1983–2025 minus 1950–82 | +0.0 [−13.3, +13.9] | 1.00 | 1.0 | **−16.0 in both eras: not born with expiry or buybacks** |
| A4 (quarterly − monthly) post-expiry week, era change | −2.4 [−11.9, +7.4] | 0.63 | 1.0 | no expiry-era signature |
| A5 clock race: 16th→3rd Friday minus after 3rd Friday | +6.2 [−10.1, +20.3] | 0.41 | 1.0 | +6.7 vs +0.5 (ordinary days +4.4): leans "support until expiry", not resolved |
| A6 Nikkei: after US 3rd Friday minus after own expiry | +6.0 [−8.5, +22.8] | 0.47 | 1.0 | no clock wins |
| A7 dose: GEX roll-off vs the following week (ρ) | +0.17 [+0.04, +0.31] | 0.013 | 0.10 | bigger gamma roll-off → weaker next week (near-pass) |
| A8 Treasury cash drain vs same-week S&P (ρ) | +0.03 [−0.02, +0.09] | 0.22 | 1.0 | no cash-drain effect |

## Part C: the hemisphere test (Holm across C1–C4)
| test | estimate [95% CI] | raw p | Holm |
|---|---|---|---|
| C1 Australia, late-Mar (local autumn) minus late-Sep | +1.3 [−11.5, +14.5] | 0.87 | 1.0 |
| C2 Australia, local component (US move removed, β 0.29) | +0.1 [−11.3, +11.9] | 0.98 | 1.0 |
| C3 southern pooled (AU +1.3, NZ +15.5, ZA +10.8) | +7.2 [−5.6, +20.0] | 0.28 | 0.84 |
| C4 northern control, late-Sep minus late-Mar (DAX −18, Nikkei −15, S&P −4, FTSE −3) | −9.4 [−21.3, +1.7] | 0.10 | 0.39 |

* **Southern autumns are not weak.** If anything, the southern late-September window is the weaker one (pooled +7, n.s.), the sign a *global* calendar predicts.
* **Seasonal mood (Kamstra-Kramer-Levi) is not the origin.**
* Australia's late September (after the US 3rd Friday) is −5.9bp/day vs other days (descriptive), which is imported, not local.

## Part B: single names (Holm across B1–B5)
| test | n | estimate [95% CI] | raw p | Holm | VF / SC in context vs rest |
|---|---|---|---|---|---|
| B1 gap-up in the 5 sessions after a quarterly expiry (Y1, σ) | 291 | +0.08 [−0.05, +0.21] | 0.22 | 0.66 | VF 16% vs 15%, SC 21% vs 15% |
| **B2 earnings-reaction gap-up, 9 new names (Y1, σ)** | 146 | **−0.31 [−0.51, −0.10]** | 0.006 | **0.031 PASS** | **VF 25% vs 15%**, SC 14% vs 16% |
| B3 call-wall cap, MSFT + MU (Y1, σ) | 72 | +0.08 [−0.08, +0.25] | 0.33 | 0.66 | |
| B4 options-unwind pressure vs Y1 (ρ) | 52 | −0.12 [−0.40, +0.17] | 0.43 | 0.66 | call OI part −0.02, IV-drop part −0.08 |
| B5 last 30 minutes on a report day (%) | 138 | −0.14 [−0.26, −0.01] | 0.033 | 0.13 | |

## Descriptive: the half-month rhythm (Ariel 1987), S&P bp/day
| | days 1–15 | days 16–end | September 1–15 | September 16–end |
|---|---|---|---|---|
| 1950–1986 | +4.8 | +1.0 | −1.6 | −5.1 |
| 1987–2025 | +4.2 | +2.6 | +3.4 | −10.1 |

* Second halves of months are weaker in general: inflows (pay, contributions, dividends) cluster around the month turn.
* September's second half is far weaker than an ordinary second half, so the monthly rhythm explains part of the September effect, not all of it.

## Verdict
1. **What September's weakness is not:**
   * It is not index-option expiry and not buybacks: it is the same size before 1983 as after.
   * It is not Treasury cash drains (A8) and not seasonal mood (no southern mirror).
   * It is old (1928+), northern-hemisphere-wide, and imported by Australia.
   * What fits is a *global institutional calendar*: the weak second half of every month (inflows cluster at the turn), made much worse in September. Candidates for the extra: post-summer issuance supply, fiscal half-year and quarter ends, and global fund flows.
2. **Expiry mechanics are real at the weekly scale:** the more dealer gamma rolls off, the weaker the next week (ρ +0.17, Holm 0.10).
3. **The earnings-morning fade is confirmed out of sample** and passes:
   * 9 new names, −0.31σ in the first hour, violent fades 25% vs 15%. That matches the 4-name estimate (−0.31σ).
   * Across all 12 stocks, about 1 in 4 earnings gap-ups is a violent fade, vs about 1 in 7 normally.
   * The option-unwind measure does not explain it (B4), so the mechanism is still open.
4. **Pre-report selling into the close** leans the predicted way (−0.14% in the last 30 minutes, raw p 0.03) but does not pass.
