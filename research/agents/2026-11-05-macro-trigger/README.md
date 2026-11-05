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
