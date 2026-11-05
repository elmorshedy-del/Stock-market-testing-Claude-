# Do jobs and CPI days trigger bounces after sharp drops in low gamma?

**Agent / session:** Claude, for the owner, 2026-11-05 ~11:15 ET. **Pre-registered at commit:** the commit that first adds this README.

**Owner:** "Many times job and inflation surge the market especially on these low gamma environment and after sharp drops."

**Why now:** the jobs report is Fri Nov 6 and CPI is Tue Nov 10 (FRED release calendar).

## Data
* **Release dates:** FRED release-dates API (release 50 = Employment Situation, 10 = CPI), 2011–2026.
  * Jobs: the earliest date in each month (later same-month dates are benchmark or revision releases).
  * CPI: the latest date in each month (earlier February dates are seasonal-factor revisions).
* **Prices:** S&P (^GSPC) and NDX daily closes, from Yahoo.
* **Gamma:** SqueezeMetrics GEX, as a trailing 252-session percentile. Usable from about May 2012.

## Conditions, at the prior close (t−1)
* **DROP:** S&P ≥ 3% below its 10-session closing high.
* **LOWG:** GEX percentile ≤ 0.30.
* **SETUP:** DROP and LOWG together (the owner's claim).

## Outcomes
* The S&P close-to-close return on release day t (releases come out at 08:30 ET, before the open).
* Secondary: NDX day-t return; S&P return from t−1 to t+5; |day-t return| (size).

## Tests
* **H1 (primary, SETUP):** release days beat non-release SETUP days on the day-t S&P return.
  * One-sided permutation: shuffle release labels within SETUP days, 10,000 draws.
* **H2 (DROP only)** and **H3 (LOWG only):** the same test.
* **Holm across H1–H3.** Pass: adjusted p < 0.05 **and ≥ 15 release days in the condition**. Otherwise "can't say."
* **Descriptive:**
  * Share up and mean, jobs vs CPI separately.
  * Size: |return| on release vs non-release days.
  * Unconditional release-day returns.
  * The list of SETUP release days.

## Today (descriptive)
* DROP status at the Nov 5 close.
* LOWG status: Nov 5's GEX is not published until tonight, so report Nov 4's value and say so.

## Reproduce
`python trigger.py <DIX.csv>` → `out/trigger.json`. Release dates are saved in `out/release_dates.csv` (public FRED data).

---

# Results (run ~11:30 ET)
Span: 2012-05 → 2026-11-04. 340 release days (169 jobs, 171 CPI).

**H1–H3 all fail (Holm adj 1.0).** The sign is the opposite of the claim.

**H1, SETUP (drop ≥ 3% and GEX ≤ 30th pct):** 33 release days.
* S&P −0.56% on average, 42% up. Non-release SETUP days: +0.21%, 58% up. Permutation p 0.98.
* Jobs days: −1.14%, 3 of 12 up. CPI days: −0.22%, 11 of 21 up.
* NDX: −0.62% vs +0.28%.
* S&P t−1 → t+5: −0.52% vs +0.81%.
* Size: release |r| 1.58% vs 1.41%. Bigger moves, in either direction.
  * Big up days (≥ +1%): 9. Big down days (≤ −1%): 14.

**H2, DROP only:** 36 days, −0.34%, 44% up; jobs days 4 of 14 up (p 0.94).

**H3, LOWG only:** 90 days, −0.19%, 46% up (p 0.96).

**All days, unconditional:** release days +0.075% vs +0.05%, 57% vs 54% up. Normal-sized moves on average (|r| 0.79% vs 0.69%).

**Robustness (exploratory):** without the COVID (Mar 2020) and tariff-crash (Apr 2025) days, SETUP release days are flat.
* −0.08%, 48% up, n 29.
* Jobs days 3 of 10 up; CPI days 11 of 19 up (+0.19%).
* The negative tilt partly comes from shock days, but the claim ("surge") still fails.

**Memorable surges exist but are not the norm:** 2022-10 CPI +2.6%, 2014-12 CPI +2.0%, 2021-03 jobs +1.95%, 2023-03 CPI +1.65%.

**Today (live):**
* DROP is met: S&P −3.4% from its 10-day high.
* LOWG is not met on the last published GEX: Nov 4, 45th pct. Nov 5's value comes tonight.

**Verdict**
* Release days in this setup are a trigger for a *big* move, not a reliably *up* one.
* After drops, jobs days have leaned down (n small). CPI days are close to a coin flip, slightly up without the shock days.
