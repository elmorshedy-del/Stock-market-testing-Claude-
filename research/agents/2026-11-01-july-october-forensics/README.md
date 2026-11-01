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
