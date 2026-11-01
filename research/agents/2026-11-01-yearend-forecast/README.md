# SPY from Nov 2 to year-end 2026: a scored, pre-registered forecast

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-01 (Sunday; the last close was Fri Oct 30)
**Type:** pre-registered forecast. The method is fixed and pushed before any forward-looking number is computed, and it is scored on fixed dates.
**Owner's ask (2026-11-01):** use the July↔October resemblance "for starting next week predictions to year end".
**Builds on:**
* [july-october-forensics](../2026-11-01-july-october-forensics/): same 13-week calendar and state; likeness not beyond chance.
* Ladder R4 (fired Oct 30).
* [forced-flow](../2026-10-24-forced-flow/): moves made in low dealer gamma fade.
* The midterm base rates in [2026-10-30-live-read](../2026-10-30-live-read/).

## Step 1 (test before use): does the 13-week analog predict anything?
* **A1:** across the S&P 500 1950–2026, for every month-end t, the correlation between:
  * the return over the next 20 sessions after t, and
  * the return over the 20 sessions after the month-end 3 months earlier.
  This is "what came after July predicts what comes after October".
  * Same for 40 sessions.
  * Also the sign-agreement rate vs 50%.
* **Use rule fixed now:** the analog enters the forecast only if A1's correlation > 0 with p < 0.05 (year-block bootstrap). Otherwise it is shown for reference only, labelled "no predictive value".

## Step 2: the forecast core (empirical base rates, no fitting)
* **Paths:** S&P 500 cumulative returns from the last October close to each session through Dec 31, for every year 1950–2025.
* **Vol scaling:** each year's path is scaled by (today's 20-day realized vol ÷ that year's 20-day realized vol at its October close), capped at 0.5×–2×. Calm years then do not understate today's risk, and wild years do not overstate it.
* **Three reference classes, reported side by side:**
  * **B-all:** every year.
  * **B-midterm:** midterm years (1950, 1954 … 2022; n 19).
  * **B-pullback:** years whose October close was 2–8% below the 52-week high (today: S&P ~4% below its high).
* **The headline forecast is B-all.** It is the largest sample. B-midterm and B-pullback are shown as tilts, because small n inflates confidence.
* **Output:**
  * the median and 10/25/75/90% bands of SPY on Nov 13 (10 sessions), Nov 30 and Dec 31;
  * P(SPY above the Oct 30 close) on each date;
  * translation to SPY at 755.69 (Oct 30 close).

## Step 3: the in-house signals now firing (documented numbers, not refit)
* **R4 (fired Oct 30):** up-leg odds 70–74% within ~20 sessions (ladder study). Scored on WR3 by ~Nov 27.
* **Forced-move fade:** moves made below the flip are given back ~18% within 10 sessions (forced-flow, p 0.002).
* **Election VIX release:** fit −3.8 VIX points in the 5 sessions after Nov 3.
* **Gamma map for the first week** (Monday's map): flip 774.06, put wall 750, deepest pocket ~740, call wall 800.

## Step 4: the volatility calendar (when, not which way)
* The scheduled days from Nov 2 to Dec 31: election, jobs, CPI, FOMC, opex and VIX expiries, NVDA earnings, Thanksgiving, the December quarterly expiry, year-end.
* Per the forensics, these mark *when* moves are likely to be released, not their direction.

## Scoring (fixed now)
* **On Nov 13, Nov 30 and Dec 31:**
  * the percentile of SPY's actual close within the B-all forecast distribution (PIT);
  * whether it fell inside the 25–75% and 10–90% bands.
* A calibrated forecast lands inside 25–75% half the time. **Three dates is far too few to judge.** This starts a running log of forecasts.

## Results (`forecast.py` → `out/forecast.json`, `figure.py` → `out/forecast.png`; $0)
### Step 1: the 13-week analog fails, so it does not enter the forecast
| | corr | 95% CI | p | sign agreement | Octobers only (after Oct vs after Jul) |
|---|---|---|---|---|---|
| next 20 sessions vs the 20 after the month-end 3 months earlier (n 918) | +0.05 | −0.04 to +0.13 | 0.13 | 52.6% | −0.00 (n 76) |
| next 40 sessions (n 917) | +0.03 | −0.09 to +0.14 | 0.33 | 56.8% | +0.10 (n 76) |

* What came after July (SPY +5.7% from the Jul 29 low into mid-August, then sideways) says nothing reliable about November.

### Step 2: base rates, vol-scaled (today: S&P 7,580, 3.05% below its 52-week high, 20-day realized vol 11.5%)
| Reference class | Nov 13: P(up), median SPY | Nov 30: P(up), median | Dec 31: P(up), median, 25–75%, 10–90% |
|---|---|---|---|
| **All years 1950–2025 (n 76), headline** | **63%, 764** | **70%, 769** | **78%, 783; 757–804; 740–820** |
| Midterm years (n 19) | 79%, 765 | 79%, 774 | 68%, 775; 753–804; 734–824 |
| Pullback years, Oct close 2–8% below the high (n 30) | 63%, 766 | 80%, 769 | 83%, 783; 766–797; 743–821 |

* **Caveat, fixed in the method but worth flagging:** the bands use realized vol (11.5%). VIX 19.4 prices wider swings; ±1σ to Dec 31 is about ±7.9% (SPY ≈ 696–815). Part of that is the election premium the fit expects to drain after Nov 3.
* The fan maps each year onto 2026's 42 sessions by fraction of the Oct-end → Dec-end span. Years have different session counts, e.g. the 1968 Wednesday closures.

### Step 3–4: signals and calendar (from earlier studies; not refit)
* **Signals:**
  * R4 fired Oct 30: 70–74% up-leg odds (WR3, scored ~Nov 27).
  * Forced-move fade: ~18% of below-flip moves given back in 10 sessions.
  * Election VIX fit: −3.8 points in the 5 sessions after Nov 3.
* **Calendar** (when moves are likely, not their direction):
  * election Tue Nov 3; jobs Fri Nov 6; CPI ~Nov 10–13 (date to confirm);
  * VIX expiry Wed Nov 18 (NVDA earnings about then; estimate); Nov opex Fri Nov 20; Thanksgiving Nov 26;
  * jobs Dec 4; FOMC Dec 8–9; VIX expiry Dec 16; quarterly opex Fri Dec 18 (the biggest gamma roll-off; calendar-mechanics A7: a weaker next week, ρ +0.17); year-end Dec 31.

### Scoring log (fill in on the dates; B-all distribution)
| Date | Forecast median | 25–75% | 10–90% | Actual SPY close | Percentile | Inside 25–75? |
|---|---|---|---|---|---|---|
| Fri Nov 13 | 764 | 751–778 | 734–794 | | | |
| Mon Nov 30 | 769 | 754–784 | 732–801 | | | |
| Thu Dec 31 | 783 | 757–804 | 740–820 | | | |
