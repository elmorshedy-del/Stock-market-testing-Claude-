# Which past years has the S&P's 2026 rhymed with, and what came next?

**Agent / session:** Claude, claude.ai session for the owner, 2026-10-24
**Type:** analog study plus a pre-registered skill test. Pre-registered here before any analog was computed. The only thing looked at beforehand was 2026's own path.
**Builds on:**
* microstructure §4x (state analogs for the S&P: neutral; the Oct–Dec season is the tailwind);
* spy-channel (the Q4 record since 1971).

**Verdict:** (after the run)

## The owner's question
* Based on what the S&P has done this year and this month, what will next month look like?
* Is there a past year that rhymes with this one?
* Show it in a way that is neat, not only averages.

## 2026 so far (^GSPC, through the Oct 23 close)
* **Year to date:** +11.4%.
* **Spring correction:** −5.1% in March, low 6,344 on Mar 30.
* **V rebound:** +10.4% in April, +5.1% in May.
* **Summer plateau:** Jun −1.1%, Jul −0.1%, Aug +2.6%, Sep −0.5%.
* **October:** +2.2% to a new high of 7,819 on Oct 6, then a fade to −0.4% month to date.

## Design
* **Data:** ^GSPC daily from Yahoo, 1928 to 2026-10-23.
* **Path:** each year's log close relative to the prior year's last close, indexed by trading day. Today is trading day n0 = 204.
* **Similarity (primary, shape):** Pearson correlation between 2026's path and year Y's path over trading days 1..n0.
* **Also reported:**
  * the correlation over the last 21 sessions (this month's shape), each re-based to its start;
  * the RMSE of the raw paths (shape plus size).
* **Analogs:** the top K = 5 years by the primary score. A year needs at least n0 + 30 sessions.
* **Outcomes from day n0 in year Y:**
  * (a) to Y's last November close (**"next month"**);
  * (b) to Y's year end.
* **Picture:** 2026's path with the analog years overlaid, each scaled to 2026's level at day n0 and continued to year end.

## Pre-registered skill test: do analogs say anything about the next month beyond the season?
* **Walk-forward over Y = 1950 to 2025:**
  * Pick the top 5 analogs for Y among years before Y only, by the same primary score at Y's day n0.
  * Prediction: the mean of the analogs' outcome (a).
  * Naive prediction: the mean outcome (a) of all prior years (the season).
* **Scores (76 test years):**
  * the correlation of the analog prediction with the realized outcome;
  * the sign hit rate vs the naive hit rate;
  * the realized outcome when the prediction is in its top vs bottom third.
* **Null:** permute predictions across test years, 5,000 draws. One-sided p for the correlation.
* **Pass:** correlation > 0 with p < 0.05 **and** a sign hit rate above naive.
* **Secondary:**
  * outcome (b), to year end;
  * K = 3 and K = 10;
  * the recent-month score as the selector instead of the year-to-date shape.
* **Prediction (written before the run):** analogs add little beyond the season. November is up in most years, so the naive hit rate is hard to beat.

## Threats to validity
* With 76 test years the test has low power: it can detect a strong signal, not a subtle one.
* Choosing the shape metric is itself a degree of freedom. It is fixed above, and the alternatives are reported as secondary.
* Markets before 1950 differ (volatility, the role of index investing). They serve only as candidate analogs, never as test years.
