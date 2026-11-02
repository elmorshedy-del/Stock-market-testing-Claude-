# July vs October 2026: why the two selloffs look alike (forensics)

**Agent / session:** Claude, claude.ai session for the owner, 2026-11-01
**Type:** forensic comparison. Descriptive alignment plus two pre-registered tests (F1, F2), written and pushed before the tests were run.
**Owner's question (2026-11-01):** "October selling looks so much like July… same sell then drift then big gap down like Friday's. Does microstructure… macro or micro… validate or offer some explanation why that similarity is happening so it's not just a visual coincidence… like doing forensics where all pieces fall in place."

## What was seen before writing this (stated so nothing below is presented as a prediction)
* **The two windows sit exactly 13 weeks (91 days) apart,** with the same weekdays:
  * Fri Jul 17 / Fri Oct 16: monthly opex, −1.02% / −1.09%;
  * Mon–Wed after: a drift up;
  * Thu Jul 23 / Thu Oct 22: gaps of −1.07% / −0.87%, days of −1.22% / −1.18%.
* **The endings differ:**
  * July: FOMC day Wed Jul 29 −1.51%, then +1.67% / +0.69% into month-end and an August breakout.
  * October: FOMC Wed Oct 28 +0.34%, then a Friday month-end gap of −1.05% and a day of −1.80%.
* **Scheduled events on the matching days, checked from Alpha Vantage report dates and the Fed / Cboe calendars:**
  * TSLA and IBM reported after the close on Wed Jul 22 and Wed Oct 21, both VIX-expiry Wednesdays (the 3rd Friday of the next month minus 30 days).
  * NFLX reported Thu Jul 16 (the night before July opex) but Tue Oct 20.
  * GOOGL reported Jul 22 but Oct 28; AMZN reported Thu Jul 30 / Thu Oct 29.
  * FOMC decided Wed Jul 29 / Wed Oct 28.
  * Both months end on a Friday (Jul 31 / Oct 30).

## Pre-registered tests
* **F1: is the similarity unusual, or what any two selloffs look like?**
  * Statistic: the Pearson correlation of daily close-to-close returns, aligned weekday by weekday, over the 15 sessions Jul 13–31 vs Oct 12–30.
  * Null: the correlation of the October window with every other 15-session window of the S&P 500, 1993-01 → 2026-06 (excluding windows that overlap October).
  * Report the percentile, and a look-elsewhere version: the best match among the 24 month-end-aligned windows before October. A person comparing recent months would naturally pick the most similar one.
  * Also report the first 9 aligned sessions (to the Thursday gap) separately, labelled as chosen after looking.
* **F2: does the event calendar impose a rhythm** (the mechanism the alignment suggests)?
  * S&P 500 daily returns, 1993-01 → 2026-10, in units of the prior day's VIX/√252. VIX from 1990 via Yahoo.
  * **F2a, opex rhythm:** mean standardized return on each session from 5 before to 10 after the monthly 3rd Friday.
    * Earnings-season months (Jan/Apr/Jul/Oct) vs others.
    * Prediction from our calendar study (gamma roll-off → weaker next week; weaker second half of the month): sessions +1…+10 below the all-session mean.
  * **F2b, the day after VIX expiry** (2004-04 → 2026-10; expiry = the next month's 3rd Friday − 30 days, moved to the prior business day on holidays): mean standardized return vs all other sessions.
    * Prediction: below average (the "vanna/charm support ends after VIX expiry" story).
  * **F2c, the overlap that hit both Thursdays:** the day after a VIX expiry that is also in the week after a 5-week-cycle opex (as in July and October).
    * Descriptive (few events), mean and count.
  * Inference: a 1-year block bootstrap (10,000); two-sided p; Holm across F2a (pooled +1…+10), F2b.
* **Descriptive "pieces" table:**
  * the same pieces for both months: gamma state (spot vs flip, from `td_gamma_SPY.csv` where available and the live maps), VIX path, breadth (RSP/SPY), 10-year yield, the megacap earnings surprises;
  * which matched and which did not.

## Limits stated now
* **Two episodes cannot prove a mechanism.** The tests ask whether (1) the resemblance is beyond chance and (2) the scheduled calendar that both months share produces systematic moves on those days.
* **News sets direction; the calendar sets timing.** If F2 shows only small mean effects, the honest reading is "same scaffold, similar timing of volatility, direction from the news".

## Results (`forensics.py` → `out/forensics.json`, `figure.py` → `out/forensics.png`; $0, free data)
**Disclosure:** the first run computed October's VIX expiry wrongly. For future expiry dates, the helper returned the last date on file, giving Sep 30 instead of Oct 21; this affected one event. Fixed and re-run; F2b moved from −0.075 to −0.081σ.

### F1: is the resemblance beyond chance? **No.**
* **Whole 15 aligned sessions:** correlation of daily returns **−0.02**, the 47th percentile of all 8,415 windows since 1993.
  * July ranks only #13 of the 24 month-end windows before October. The closest was Oct 2024 (+0.74; best-of-24 look-elsewhere p 0.03).
* **First 9 sessions only** (to the Thursday gap; chosen after looking): +0.41, 85th percentile. Mildly alike, not exceptional.

### F2: does the shared calendar push prices on those days? **Barely.**
| Test (S&P, returns in σ = prior VIX/√252) | Estimate | p | Holm |
|---|---|---|---|
| F2a sessions 1–10 after the monthly opex vs others (1993–2026) | +0.004σ (CI −0.02 to +0.03) | 0.75 | 0.75 |
| F2b day after VIX expiry vs others (2004–2026, n 271) | **−0.081σ** (CI −0.155 to −0.011) ≈ −0.09% at VIX 17; 49% down vs 45% | 0.026 | **0.052** (misses) |
| F2c day after a VIX expiry in the week after opex (the July/October layout, n 95) | −0.03σ, 48% down | — | descriptive |

* 2026 has had four F2c days: Jan 22 +0.51σ, May 20 +0.94σ, **Jul 23 −1.16σ, Oct 22 −1.16σ**. Same layout, opposite signs earlier in the year.
* **Exploratory (not registered):** scheduled days do not carry bigger moves either. Mean |z| vs all days: opex 0.91×, day after VIX expiry 1.03×, month-end 0.98×.

### The pieces (descriptive)
| | July (Jul 10 → 31) | October (Oct 9 → 30) | Match? |
|---|---|---|---|
| Weekday calendar | opex Fri 17, VIX-exp Wed 22 + TSLA/IBM/GOOGL night, FOMC Wed 29, AAPL/AMZN Thu 30, month-end Fri 31 | opex Fri 16, VIX-exp Wed 21 + TSLA/IBM night, FOMC Wed 28 (+GOOGL/MSFT night), AAPL/AMZN Thu 29, month-end Fri 30 | ✓ exactly +91 days |
| Start | VIX 15.0 at a fresh high after an early-month rally | VIX 14.8, same | ✓ |
| Gamma | below flip 81% of days, median GEX −$5.2bn | below flip from Oct 14 (live maps: GEX −$12 to −14bn per 1%) | ✓ (short gamma both) |
| VIX peak | 20.7 | 20.0 | ✓ |
| Rotation out of tech | QQQ−IWM −3.6 pts; RSP−S&P +1.5 | −8.2; +5.4 | ✓ (October 2× stronger) |
| Rates / dollar | 10y **+18bp**; DXY −1.2% | **−32bp**; −0.3% | ✗ (corrected: October was a flight into bonds) |
| End-of-month earnings | GOOGL EPS surprise +216%, AMZN +2.7% | GOOGL −28%, AMZN −6.0% | ✗ (opposite) |
| FOMC day | −1.5% | +0.3% | ✗ |
| Window result | −1.1% (then the August breakout) | −2.9% (Friday gap −1.05%, day −1.8%) | ✗ |

### Verdict
* **The likeness has a real structural cause, but it is a cause of timing, not of a pattern.**
  * The Q3 calendar was the Q2 calendar shifted exactly 13 weeks, so the same scheduled shocks (opex, the VIX-expiry/earnings night, FOMC plus the megacap week, a Friday month-end) landed on the same weekdays.
  * Both selloffs also began from the same state: VIX ~15 at a high, then short gamma, money rotating out of megacap tech. That makes the same kind of shock produce a similar-sized move.
* **The calendar does not set direction.** In 33 years of data, those days are not systematically down and do not carry bigger moves; the day after VIX expiry is a near-miss at −0.09%.
  * The endings split on the earnings news (beats in July, misses in October). Over the full three weeks, the two paths are no more alike than random windows.
* **"Sell, drift, gap down" is what most multi-week declines look like.** The eye matches the shape; the statistics match only the timing of the scheduled days.
* **Forward use (timing only):** Q4 replays the scaffold 13 weeks on: Jan opex Fri Jan 15 2027, VIX expiry Wed Jan 20, month-end Fri Jan 29.
  * Expect volatility to be released on those days if the state is fragile again. Do not expect a direction from the calendar.

### Erratum (2026-11-01, found while building the mechanism ledger)
* **The 10-year yield change was mis-scaled by 10×** (Yahoo `^TNX` is quoted in percent; the code multiplied by 10 instead of 100).
* **Corrected:** July window +18bp, October window −32bp.
* **Consequence:** the "not rates" row was wrong. Rates *differ* between the two months: July's selloff came with yields rising, October's with a flight into bonds (yields falling, credit softer). That points to a growth or risk-off tone in October that July did not have.
* The figure and table are corrected. No other number changes.

### Erratum 2 (2026-11-02): Apple's report date
* The calendar row "AAPL/AMZN Thu Oct 29" was wrong: only AMZN reported Oct 29. **AAPL reports Mon Nov 2** (Alpha Vantage: last report Jul 30 2026; confirmed by a third-party note, see [note-check](../2026-11-02-note-check/)).
* July's AAPL report (Thu Jul 30, +7.4% surprise) was part of July's turn. In October, AAPL is a pending catalyst: its reaction lands Tue Nov 3, election day.
* The machine ledger's "megacap tech retakes the lead: absent" becomes "pending: AAPL Nov 2, then NVDA ~Nov 18–19". Forecasts C1–C4 are unchanged (written before this was known).
